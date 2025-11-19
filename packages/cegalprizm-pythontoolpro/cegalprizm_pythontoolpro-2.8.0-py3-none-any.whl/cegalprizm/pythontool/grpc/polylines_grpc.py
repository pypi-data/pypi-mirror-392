# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool import _docstring_utils
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from cegalprizm.pythontool.grpc import petrelinterface_pb2, utils
from .petrelinterface_pb2 import Primitives, PolylineType
from .points_grpc import PropertyTableHandler


import pandas as pd
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.polylines_hub import PolylinesHub

class PolylineSetGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(PolylineSetGrpc, self).__init__(WellKnownObjectDescription.PolylineSet.value, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("PolylinesHub", petrel_connection._service_polylines)
        self._table_handler = PropertyTableHandler(self._guid, self._plink, self._channel, WellKnownObjectDescription.PolylineSet)

    def GetCrs(self):
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._channel.PolylineSet_GetCrs(request)
             
        return response.value

    def GetNumPolylines(self) -> int:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)        
        return self._channel.PolylineSet_GetNumPolylines(request).value 

    def IsClosed(self, idx) -> bool:
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        request = petrelinterface_pb2.PetrelObjectGuidAndIndex(
            guid = po_guid,
            index = idx
        )
        return self._channel.PolylineSet_IsClosed(request).value 

    def GetPoints(self, idx):
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        request = petrelinterface_pb2.PetrelObjectGuidAndIndex(guid = po_guid, index = idx)        
        responses = self._channel.PolylineSet_GetPoints(request)
        points = []
        for response in responses:
            point = Primitives.Double3(x = response.x, y = response.y, z = response.z)
            points.append(point)

        point_array = [None] * 3
        point_array[0] = []
        point_array[1] = []
        point_array[2] = []
        
        for p in points:
            point_array[0].append(p.x) 
            point_array[1].append(p.y) 
            point_array[2].append(p.z) 
        
        return point_array

    def SetPolylinePoints(self, idx, xs, ys, zs, closed = False):
        if not xs or len(xs) == 0:
            return

        self.write_test()
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        no_points_per_streamed_unit = self._table_handler.no_points_per_streamed_unit(len(xs), self._plink._preferred_streamed_unit_bytes)
        no_points = len(xs)
        start_inds = range(0, no_points, no_points_per_streamed_unit)
        
        iterable_requests = map(
            lambda start_ind : self._table_handler.setpoints_request(start_ind, po_guid, xs, ys, zs, no_points_per_streamed_unit, idx = idx, closed = closed),
            start_inds
        )

        ok = self._channel.PolylineSet_SetPolylinePoints(iterable_requests)
        return ok.value

    def AddPolyline(self, arrayx, arrayy, arrayz, closed):
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        point_inds = range(len(arrayx))
        iterable_requests = map(
            lambda point_ind : self._add_polyline_request(po_guid, arrayx[point_ind], arrayy[point_ind], arrayz[point_ind], closed),
            point_inds
        )

        return self._channel.PolylineSet_AddPolyline(iterable_requests).value

    def _add_polyline_request(self, po_guid, x, y, z, closed):
        point = petrelinterface_pb2.Primitives.Double3(x = x, y = y, z = z)
        return petrelinterface_pb2.AddPolyline_Request(
            guid = po_guid,
            point = point,
            closed = closed
        )
    
    def AddMultiplePolylines(self, polylines_dict: dict, contains_closed: bool = False):
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        iterable_requests = []
        for poly_index, values in polylines_dict.items():
            request = petrelinterface_pb2.AddMultiplePolylines_Request(
                Guid = po_guid,
                PolyIndex = poly_index,
                VertIndex = [vi for vi in values[0]],
                Xs = [x for x in values[1]],
                Ys = [y for y in values[2]],
                Zs = [z for z in values[3]],
                ## If no column provided, we assume all polylines are closed
                IsClosed = bool(values[4][0]) if contains_closed else True
            )
            iterable_requests.append(request)

        self._channel.PolylineSet_AddMultiplePolylines(r for r in iterable_requests)

    def DeletePolyline(self, polyline_index):
        self.write_test()
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        request = petrelinterface_pb2.PetrelObjectGuidAndIndex(guid = po_guid, index = polyline_index)        
        return self._channel.PolylineSet_DeletePolyline(request).value

    def DeleteAll(self):
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._channel.PolylineSet_DeleteAll(request)
             
        return response.value
    
    def GetPointsDataFrame(self) -> pd.DataFrame:
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.PolylineSet_GetPointsDataframe(request)

        poly_indices = []
        vertice_indices = []
        xs = []
        ys = []
        zs = []
        for response in responses:
            poly_indices.append(response.PolyIndex)
            vertice_indices.append(response.VerticeIndex)
            xs.append(round(response.X, 2))
            ys.append(round(response.Y, 2))
            zs.append(round(response.Z, 2))

        data = {}
        data["Poly"] = pd.Series(poly_indices, dtype = pd.Int64Dtype())
        data["Vert"] = pd.Series(vertice_indices, dtype = pd.Int64Dtype())
        data["X"] = pd.Series(xs, dtype = float)
        data["Y"] = pd.Series(ys, dtype = float)
        data["Z"] = pd.Series(zs, dtype = float)

        df = pd.DataFrame(data)
        return df
    
    def GetAttributesDataFrame(self) -> pd.DataFrame:
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.PolylineSet_GetAttributesDataframe(request)

        poly_indices, att_names, att_values, att_types = [], [], [], []

        for response in responses:
            poly_indices.append(response.PolyIndex)
            att_names.append(response.AttributeNames)
            att_values.append(response.AttributeValues)
            att_types.append(response.AttributeTypes)

        unordered_data = {}
        unordered_data["Poly"] = pd.Series(poly_indices, dtype = pd.Int64Dtype())

        if(len(att_names) > 0):
            unordered_data = utils.HandleUserDefinedProperties(unordered_data, att_names, att_values, att_types)

        ordered_data = self._get_ordered_dictionary(unordered_data)

        df = pd.DataFrame(ordered_data)
        ## Handle edge-case with no polylines, in this case polyindex is 0
        if len(df) == 1 and df['Poly'][0] == 0:
            df = df.drop(df.index[0])

        return df

    def _get_ordered_dictionary(self, unordered_data):
        ordered_data = {}
        if "Poly" in unordered_data:
            ordered_data["Poly"] = unordered_data.pop("Poly")
        if "Show polygon" in unordered_data:
            ordered_data["Show polygon"] = unordered_data.pop("Show polygon")
        if "Show polygon (1)" in unordered_data:
            ordered_data["Show polygon (1)"] = unordered_data.pop("Show polygon (1)")
        if "Label X" in unordered_data:
            ordered_data["Label X"] = unordered_data.pop("Label X").round(2)
        if "Label X (1)" in unordered_data:
            ordered_data["Label X (1)"] = unordered_data.pop("Label X (1)").round(2)
        if "Label Y" in unordered_data:
            ordered_data["Label Y"] = unordered_data.pop("Label Y").round(2)
        if "Label Y (1)" in unordered_data:
            ordered_data["Label Y (1)"] = unordered_data.pop("Label Y (1)").round(2)
        if "Label Z" in unordered_data:
            ordered_data["Label Z"] = unordered_data.pop("Label Z").round(2)
        if "Label Z (1)" in unordered_data:
            ordered_data["Label Z (1)"] = unordered_data.pop("Label Z (1)").round(2)
        if "Label angle" in unordered_data:
            ordered_data["Label angle"] = unordered_data.pop("Label angle").round(2)
        if "Label angle (1)" in unordered_data:
            ordered_data["Label angle (1)"] = unordered_data.pop("Label angle (1)").round(2)

        for key in unordered_data:
            ordered_data[key] = unordered_data[key]
        return ordered_data
    
    def AddAttribute(self, name: str, prop_type: petrelinterface_pb2.PointPropertyType, template_guid: str):
        self._plink._opened_test()
        request = petrelinterface_pb2.PolylineSet_AddAttribute_Request(
            Guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            AttributeName = name,
            AttributeType = prop_type,
            TemplateGuid = petrelinterface_pb2.PetrelObjectGuid(guid = template_guid)
        )
        response = self._channel.PolylineSet_AddAttribute(request)
        return response
    
    def DeleteAttribute(self, polylineset_guid: str, attribute_guid: str) -> bool:
        self._plink._opened_test()
        request = petrelinterface_pb2.PolylineSet_DeleteAttribute_Request(
            PolylineSetGuid = petrelinterface_pb2.PetrelObjectGuid(guid = polylineset_guid),
            AttributeGuid = petrelinterface_pb2.PetrelObjectGuid(guid = attribute_guid)
        )
        response = self._channel.PolylineSet_DeleteAttribute(request)
        return response.value
    
    def GetAllAttributes(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.PolylineSet_GetAllAttributes(request)
        object_refs = []
        for response in responses:
            object_refs.append(response)
        return object_refs
    
    def GetPolylineType(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._channel.PolylineSet_GetPolylineType(request)
        polyline_type_string = self.GetPolylineTypeStringFromGrpcEnum(response.EnumPolylineType)
        return polyline_type_string

    def SetPolylineType(self, polyline_type: str):
        self._plink._opened_test()
        grpc_type = self.GetGrpcPolylineTypeFromString(polyline_type)
        request = petrelinterface_pb2.PolylineSet_SetPolylineType_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            PolylineType = grpc_type
        )
        self._channel.PolylineSet_SetPolylineType(request)

    def GetPolylineTypeStringFromGrpcEnum(self, polyline_type: PolylineType):
        if polyline_type == PolylineType.FaultSticks:
            return 'Fault sticks'
        elif polyline_type == PolylineType.FaultLines:
            return 'Fault lines'
        elif polyline_type == PolylineType.FaultCenterline:
            return 'Fault centerline'
        elif polyline_type == PolylineType.FaultPolygons:
            return 'Fault polygons'
        elif polyline_type == PolylineType.Contours:
            return 'Horizon contours'
        elif polyline_type == PolylineType.ErosionLine:
            return 'Horizon erosion line'
        elif polyline_type == PolylineType.BoundaryPolygon:
            return 'Generic boundary polygon'
        elif polyline_type == PolylineType.Seismic2DLines:
            return 'Generic seismic 2D lines'
        elif polyline_type == PolylineType.Seismic3DLines:
            return 'Generic seismic 3D lines'
        elif polyline_type == PolylineType.ZeroLine:
            return 'Generic zero lines'
        elif polyline_type == PolylineType.TrendLines:
            return 'Trend lines'
        elif polyline_type == PolylineType.FlowLines:
            return 'Flow lines'
        elif polyline_type == PolylineType.SinglePolygon:
            return 'Generic single line'
        elif polyline_type == PolylineType.PointMany:
            return 'Many points'
        elif polyline_type == PolylineType.PointFew:
            return 'Few points'
        elif polyline_type == PolylineType.MultiZInterpretation:
            return 'Multi-Z horizon'
        elif polyline_type == PolylineType.Other:
            return 'Other'
        else:
            raise ValueError(f"Polyline type {polyline_type} not supported")

    def GetGrpcPolylineTypeFromString(self, polyline_type: str):
        if polyline_type.lower() == 'fault sticks':
            return PolylineType.FaultSticks
        elif polyline_type.lower() == 'fault lines':
            return PolylineType.FaultLines
        elif polyline_type.lower() == 'fault centerline':
            return PolylineType.FaultCenterline
        elif polyline_type.lower() == 'fault polygons':
            return PolylineType.FaultPolygons
        elif polyline_type.lower() == 'horizon contours':
            return PolylineType.Contours
        elif polyline_type.lower() == 'horizon erosion line':
            return PolylineType.ErosionLine
        elif polyline_type.lower() == 'generic boundary polygon':
            return PolylineType.BoundaryPolygon
        elif polyline_type.lower() == 'generic seismic 2d lines':
            return PolylineType.Seismic2DLines
        elif polyline_type.lower() == 'generic seismic 3d lines':
            return PolylineType.Seismic3DLines
        elif polyline_type.lower() == 'generic zero lines':
            return PolylineType.ZeroLine
        elif polyline_type.lower() == 'trend lines':
            return PolylineType.TrendLines
        elif polyline_type.lower() == 'flow lines':
            return PolylineType.FlowLines
        elif polyline_type.lower() == 'generic single line':
            return PolylineType.SinglePolygon
        elif polyline_type.lower() == 'many points':
            return PolylineType.PointMany
        elif polyline_type.lower() == 'few points':
            return PolylineType.PointFew
        elif polyline_type.lower() == 'multi-z horizon':
            return PolylineType.MultiZInterpretation
        elif polyline_type.lower() == 'other':
            return PolylineType.Other
        else:
            raise ValueError(f"Polyline type '{polyline_type}' not supported. Supported types are: {_docstring_utils.get_supported_polyline_types()}")
