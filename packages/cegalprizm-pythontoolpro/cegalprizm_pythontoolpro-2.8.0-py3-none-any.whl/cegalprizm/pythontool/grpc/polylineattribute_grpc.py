# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc import petrelinterface_pb2, utils
from cegalprizm.pythontool.grpc.polylines_grpc import PolylineSetGrpc
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from .petrelobject_grpc import PetrelObjectGrpc
from .points_grpc import PropertyRangeHandler
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.polylines_hub import PolylinesHub

class PolylineAttributeGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection", unique_name: str = ""):
        super(PolylineAttributeGrpc, self).__init__(WellKnownObjectDescription.PolylineAttribute, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("PolylinesHub", petrel_connection._service_polylines)
        self._property_range_handler = PropertyRangeHandler()
        self._unique_name = self.GetUniqueName() if unique_name == "" else unique_name

    def GetAttributeParent(self):
        from cegalprizm.pythontool import PolylineSet
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.PolylineSet_GetAttributeParent(request)
        grpc = PolylineSetGrpc(response.guid, self._plink)
        ps = PolylineSet(grpc)
        return ps
    
    def IsWellKnownAttribute(self):
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.PolylineSet_IsWellKnownAttribute(request)
        return response.value
    
    def GetIndividualAttributeValues(self, parent_guid: str) -> typing.Any:
        self._plink._opened_test()
        request = petrelinterface_pb2.PolylineSet_GetIndividualAttributeValues_Request(
            PolylineSetGuid = petrelinterface_pb2.PetrelObjectGuid(guid = parent_guid),
            AttributeGuid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
            )
        responses = self._channel.PolylineSet_GetIndividualAttributeValues(request)
        values = []

        for response in responses:
            values.append(response.value)
            dataType = response.data_type

        converter = utils.get_from_grpc_converter(dataType)
        converted_values = [converter(v) for v in values]
        arr = utils.getNumpyArrayFromPropertyType(converted_values, dataType)
        return arr
    
    def SetIndividualAttributeValues(self, parent_guid, values):
        self._plink._opened_test()

        indices = utils.create_indices(values)

        iterable_requests = [petrelinterface_pb2.PolylineSet_SetIndividualAttributeValues_Request(
            PolylineSetGuid = petrelinterface_pb2.PetrelObjectGuid(guid = parent_guid),
            Data = prd) for prd in self._property_range_handler.get_property_range_datas("", indices, values, attribute_droid = self._guid)
        ]
        response = self._channel.PolylineSet_SetIndividualAttributeValues(r for r in iterable_requests)
        return response.value
    
    def GetUniqueName(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.PolylineSet_GetAttributeUniqueName(request)
        return response.value
