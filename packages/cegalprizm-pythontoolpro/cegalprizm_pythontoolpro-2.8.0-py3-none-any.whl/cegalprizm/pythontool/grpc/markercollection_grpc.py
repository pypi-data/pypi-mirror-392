# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from cegalprizm.pythontool.grpc import petrelinterface_pb2, utils
from cegalprizm.pythontool.grpc.stratigraphyzone_grpc import StratigraphyZoneGrpc
from cegalprizm.pythontool.grpc.markerstratigraphy_grpc import MarkerStratigraphyGrpc
from .points_grpc import PropertyRangeHandler
import cegalprizm.pythontool.grpc
import numpy as np
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.markercollection_hub import MarkerCollectionHub

class MarkerCollectionGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(MarkerCollectionGrpc, self).__init__(WellKnownObjectDescription.MarkerCollection.value, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._invariant_content = {}
        self._channel = typing.cast("MarkerCollectionHub", petrel_connection._service_markercollection)
        self._property_range_handler = PropertyRangeHandler()
    
    def AddMarker(self, borehole, stratigraphy_droid, measured_depth):
        self._plink._opened_test()

        request = petrelinterface_pb2.MarkerCollection_AddMarker_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            wellGuid = petrelinterface_pb2.PetrelObjectGuid(guid = borehole._borehole_object_link._guid, sub_type = borehole._borehole_object_link._sub_type),
            stratigraphyDroid = stratigraphy_droid,
            measuredDepth = measured_depth
        )

        response = self._channel.MarkerCollection_AddMarker(request)

        ok = response.value
        return ok
    
    def AddManyMarkers(self, boreholes: np.array, strat_droids: np.array, depths: np.array):
        self._plink._opened_test()
        iterable_requests = []
        wells = list(boreholes)
        strats = list(strat_droids)
        mds = list(depths)
        for borehole, strat_droid, depth in zip(wells, strats, mds):
            request = petrelinterface_pb2.MarkerCollection_AddMarker_Request(
                guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
                wellGuid = petrelinterface_pb2.PetrelObjectGuid(guid = borehole._borehole_object_link._guid, sub_type = borehole._borehole_object_link._sub_type),
                stratigraphyDroid = strat_droid,
                measuredDepth = depth
            )
            iterable_requests.append(request)
        ok = self._channel.MarkerCollection_AddManyMarkers(value for value in iterable_requests)
        return ok.value
    
    def DeleteManyMarkers(self, boreholes: np.array, strat_droids: np.array, depths: np.array):
        self._plink._opened_test()
        iterable_requests = []
        wells = list(boreholes)
        strats = list(strat_droids)
        mds = list(depths)
        for well, strat_droid, depth in zip(wells, strats, mds):
            request = petrelinterface_pb2.MarkerCollection_GetMarkerDroid_Request(
                Guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
                WellGuid = petrelinterface_pb2.PetrelObjectGuid(guid = well._borehole_object_link._guid),
                StratigraphyDroid = strat_droid,
                MeasuredDepth = depth
            )
            iterable_requests.append(request)
        ok = self._channel.MarkerCollection_DeleteManyMarkers(value for value in iterable_requests)
        return ok.value

    def GetMarkerDroid(self, well, stratigraphy_droid, measured_depth):
        self._plink._opened_test()

        request = petrelinterface_pb2.MarkerCollection_GetMarkerDroid_Request(
            Guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            WellGuid = petrelinterface_pb2.PetrelObjectGuid(guid = well._borehole_object_link._guid),
            StratigraphyDroid = stratigraphy_droid,
            MeasuredDepth = measured_depth
        )
        response = self._channel.MarkerCollection_GetMarkerDroid(request)
        return response.value
    
    def DeleteMarker(self, marker_droid):
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuidAndString(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            value = marker_droid,
        )
        self._channel.MarkerCollection_DeleteMarker(request)

    def GetName(self):
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._channel.MarkerCollection_GetName(request)

        return response.value
    
    def SetName(self, name):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuidAndString(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            value = name
        )

        response = self._channel.MarkerCollection_SetName(request)

        return response.value

    def GetDataFrameValues(self, 
                           include_unconnected_markers: bool, 
                           stratigraphy_droids: list, 
                           boreholes: list,
                           include_petrel_index: bool,
                           marker_attribute_list: list):
        self._plink._opened_test()

        well_guids = utils.GetWellGuids(boreholes)

        request = petrelinterface_pb2.MarkerCollection_GetValues_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            includeUnconnectedMarkers = include_unconnected_markers,
            includePetrelIndex = include_petrel_index,
            attributeDroid = "",
            dataFrame = True,
            stratigraphyDroids = [s_droid for s_droid in stratigraphy_droids],
            wellGuids = [w_guid for w_guid in well_guids],
            attributeFilterDroids = [a_droid for a_droid in marker_attribute_list]
        )
        responses = self._channel.MarkerCollection_GetValues(request)
        return self._property_range_handler.get_dataframe(responses)

    def GetDataFrameValuesForAttribute(self, attribute_droid: str, include_unconnected_markers: bool, stratigraphy_droids: list, boreholes: list):
        self._plink._opened_test()

        well_guids = utils.GetWellGuids(boreholes)

        request = petrelinterface_pb2.MarkerCollection_GetValues_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            includeUnconnectedMarkers = include_unconnected_markers,
            dataFrame = True,
            attributeDroid = attribute_droid,
            stratigraphyDroids = [s_droid for s_droid in stratigraphy_droids],
            wellGuids = [w_guid for w_guid in well_guids],
        )
        responses = self._channel.MarkerCollection_GetValues(request)
        return self._property_range_handler.get_dataframe(responses)

    def GetArrayValuesForAttribute(self, attribute_droid: str, include_unconnected_markers: bool, stratigraphy_droid: str, borehole):
        self._plink._opened_test()

        well_guids = utils.GetWellGuids([borehole])

        request = petrelinterface_pb2.MarkerCollection_GetValues_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            includeUnconnectedMarkers = include_unconnected_markers,
            dataFrame = False,
            attributeDroid = attribute_droid,
            stratigraphyDroids = [stratigraphy_droid],
            wellGuids = well_guids,
        )
        responses = self._channel.MarkerCollection_GetValues(request)
        df = self._property_range_handler.get_dataframe(responses)
        array = df.iloc[:,0].array
        return array

    def SetPropertyValues(self, attribute_droid, indexes, values, include_unconnected_markers: bool, stratigraphy_droid: str, borehole):
        self._plink._opened_test()

        well_guid = utils.GetWellGuid(borehole)

        iterable_requests = [
            petrelinterface_pb2.MarkerCollection_SetValues_Request(
                guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
                includeUnconnectedMarkers = include_unconnected_markers,
                stratigraphyDroid = stratigraphy_droid,
                wellGuid = well_guid,
                data = prd)
                for prd in self._property_range_handler.get_property_range_datas("", indexes, values, attribute_droid = attribute_droid)
        ]
        ok = self._channel.MarkerCollection_SetPropertyValues(value for value in iterable_requests)
        return ok.value

    def AddAttribute(self, uniquePropertyName, indexes, values, include_unconnected_markers: bool, stratigraphy_droid: str, borehole) -> bool:
        self._plink._opened_test()
        well_guid = utils.GetWellGuid(borehole)
        request = [petrelinterface_pb2.MarkerCollection_SetValues_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            includeUnconnectedMarkers = include_unconnected_markers,
            stratigraphyDroid = stratigraphy_droid,
            wellGuid = well_guid,
            data = property_range_data)
            for property_range_data in self._property_range_handler.get_property_range_datas(uniquePropertyName, indexes, values)
        ]
        ok = self._channel.MarkerCollection_AddAttribute(request)
        return ok.value

    def AddEmptyAttribute(self, property_name, data_type) -> bool:
        self._plink._opened_test()
        request = petrelinterface_pb2.MarkerCollection_AddEmptyAttribute_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            attributeName = property_name,
            dataType = data_type
        )
        ok = self._channel.MarkerCollection_AddEmptyAttribute(request)
        return ok.value

    def GetAttributes(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.MarkerCollection_GetAttributes(request)
        collection = []
        for response in responses:
            collection.append(response)
        return collection

    def GetStratigraphies(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.MarkerCollection_GetStratigraphies(request)
        stratigraphies = []
        for response in responses:
            stratigraphies.append(response)
        return stratigraphies

    def GetStratigraphyZones(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.MarkerCollection_GetStratigraphyZones(request)
        stratigraphy_zones = []
        for response in responses:
            stratigraphy_zones.append(response)
        return stratigraphy_zones

    def CreateZoneAndHorizonAboveOrBelow(self, createAbove: bool, reference_object, zone_name, horizon_name, horizon_type):
        self._plink._opened_test()
        request = petrelinterface_pb2.MarkerCollection_CreateZoneAndHorizon_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            referenceGuid = petrelinterface_pb2.PetrelObjectGuid(guid = reference_object._droid),
            createAbove = createAbove,
            zoneName = zone_name,
            horizonName = horizon_name,
            horizonType = horizon_type
        )
        
        response = self._channel.MarkerCollection_CreateZoneAndHorizonAboveOrBelow(request)

        refs = [ref for ref in response.refs]
        
        zone_petrelobjectref = refs[0]
        if zone_petrelobjectref.guid:
            zone_grpc_object = StratigraphyZoneGrpc(zone_petrelobjectref.guid, self._plink, zone_petrelobjectref.petrel_name)

        horizon_petrelobjectref = refs[1]
        if horizon_petrelobjectref.guid:
            horizon_grpc_object = MarkerStratigraphyGrpc(horizon_petrelobjectref.guid, self._plink, horizon_petrelobjectref.sub_type, horizon_petrelobjectref.petrel_name)
        
        return (zone_grpc_object, horizon_grpc_object)

    def CreateZonesAndHorizonInside(self, reference_zone, zone_name_1, horizon_name, zone_name_2, horizon_type):
        self._plink._opened_test()
        request = petrelinterface_pb2.MarkerCollection_CreateZoneAndHorizon_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            referenceGuid = petrelinterface_pb2.PetrelObjectGuid(guid = reference_zone._droid),
            zoneName = zone_name_1,
            horizonName = horizon_name,
            zoneName2 = zone_name_2,
            horizonType = horizon_type
        )

        response = self._channel.MarkerCollection_CreateZonesAndHorizonInside(request)
        refs = [ref for ref in response.refs]
        zone_bottom_ref = refs[0]
        if zone_bottom_ref.guid:
            zone_bottom_grpc_object = StratigraphyZoneGrpc(zone_bottom_ref.guid, self._plink, zone_bottom_ref.petrel_name)
        horizon_ref = refs[1]
        if horizon_ref.guid:
            horizon_grpc_object = MarkerStratigraphyGrpc(horizon_ref.guid, self._plink, horizon_ref.sub_type, horizon_ref.petrel_name)
        zone_top_ref = refs[2]
        if zone_top_ref.guid:
            zone_top_grpc_object = StratigraphyZoneGrpc(zone_top_ref.guid, self._plink, zone_top_ref.petrel_name)
        return (zone_bottom_grpc_object, horizon_grpc_object, zone_top_grpc_object)

    def CreateZoneAndHorizon(self, zone_name, horizon_name, horizon_type):
        self._plink._opened_test()
        request = petrelinterface_pb2.MarkerCollection_CreateZoneAndHorizon_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            zoneName = zone_name,
            horizonName = horizon_name,
            horizonType = horizon_type
        )

        response = self._channel.MarkerCollection_CreateFirstHorizon(request)
        refs = [ref for ref in response.refs]

        if len(refs) == 1:
            ## only horizon
            horizon_ref = refs[0]
            if horizon_ref.guid:
                horizon_grpc_object = MarkerStratigraphyGrpc(horizon_ref.guid, self._plink, horizon_ref.sub_type, horizon_ref.petrel_name)
            return (None, horizon_grpc_object)
        if len(refs) == 2:
            ## horizon and zone
            zone_ref = refs[0]
            if zone_ref.guid:
                zone_grpc_object = StratigraphyZoneGrpc(zone_ref.guid, self._plink, zone_ref.petrel_name)
            horizon_ref = refs[1]
            if horizon_ref.guid:
                horizon_grpc_object = MarkerStratigraphyGrpc(horizon_ref.guid, self._plink, horizon_ref.sub_type, horizon_ref.petrel_name)
            return (zone_grpc_object, horizon_grpc_object)

    def GetHorizonsAndZonesInOrder(self, parent_markercollection, include_subzones, print_hierarchy):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.MarkerCollection_GetHorizonsAndZonesInOrder(request)
        stratigraphy_infos = [r for r in responses]

        if print_hierarchy:
            self._print_stratigraphy_structure(stratigraphy_infos, include_subzones)

        if include_subzones:
            return self._construct_flattened_structure(stratigraphy_infos, parent_markercollection)
        else:
            return self._construct_top_level_structure(stratigraphy_infos, parent_markercollection)

    def _create_python_object(self, stratigraphy_info, parent_markercollection):
        if stratigraphy_info.sub_type == WellKnownObjectDescription.MarkerStratigraphyHorizon:
            grpc = cegalprizm.pythontool.grpc.markerstratigraphy_grpc.MarkerStratigraphyGrpc(stratigraphy_info.guid, self._plink, stratigraphy_info.sub_type, stratigraphy_info.petrel_name)
            return cegalprizm.pythontool.markerstratigraphy.MarkerStratigraphy(grpc, parent_markercollection)
        elif stratigraphy_info.sub_type == WellKnownObjectDescription.MarkerStratigraphyZone:
            grpc = cegalprizm.pythontool.grpc.stratigraphyzone_grpc.StratigraphyZoneGrpc(stratigraphy_info.guid, self._plink, stratigraphy_info.petrel_name)
            return cegalprizm.pythontool.stratigraphyzone.StratigraphyZone(grpc, parent_markercollection)

    def _construct_flattened_structure(self, stratigraphy_infos, parent_markercollection):
        stratigraphies = []
        for stratigraphy_info in stratigraphy_infos:
            stratigraphies.append(self._create_python_object(stratigraphy_info, parent_markercollection))
        return stratigraphies

    def _construct_top_level_structure(self, stratigraphy_infos, parent_markercollection):
        top_level_stratigraphy_infos = [s_info for s_info in stratigraphy_infos if not s_info.parent_guid]
        return [self._create_python_object(s_info, parent_markercollection) for s_info in top_level_stratigraphy_infos]

    def _print_stratigraphy_structure(self, stratigraphy_infos, include_subzones):
        # Build a dictionary of children for each parent
        childrens_dict = {}
        for s_info in stratigraphy_infos:
            if s_info.parent_guid not in childrens_dict:
                childrens_dict[s_info.parent_guid] = []
            childrens_dict[s_info.parent_guid].append(s_info)

        def traverse_entries(stratigraphy_info, depth, parent_last_entries):
            # Determine if this is the last entry at the current level
            siblings = childrens_dict.get(stratigraphy_info.parent_guid, [])
            is_last_entry = stratigraphy_info == siblings[-1]

            # Print the current entry
            self._print_stratigraphy_info_structured(stratigraphy_info, depth, parent_last_entries + [is_last_entry])

            # Recursively loop through children
            if include_subzones and stratigraphy_info.guid in childrens_dict:
                for child in childrens_dict[stratigraphy_info.guid]:
                    traverse_entries(child, depth + 1, parent_last_entries + [is_last_entry])
        
        # Find top-level entries (entries without a parent)
        top_level_entries = [s_info for s_info in stratigraphy_infos if not s_info.parent_guid]
        for i in range(len(top_level_entries)):
            traverse_entries(top_level_entries[i], 0, [])


    def _print_stratigraphy_info_structured(self, stratigraphy_info, depth, parent_last_entries):
        space = '    '
        tee = '├── '
        branch = '│   '
        last = '└── '

        # Build the prefix dynamically based on parent_last_entries
        prefix = ''
        for is_last in parent_last_entries[:-1]:  # Skip the last level
            prefix += space if is_last else branch
        if parent_last_entries:
            prefix += last if parent_last_entries[-1] else tee

        # Print the entry with the correct prefix
        print(prefix + stratigraphy_info.petrel_name)

