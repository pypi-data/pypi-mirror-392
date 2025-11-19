# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc import petrelinterface_pb2
from cegalprizm.pythontool.grpc.points_grpc import PropertyRangeHandler
from .petrelobject_grpc import PetrelObjectGrpc
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.wellattribute_hub import WellAttributeHub

class WellAttributeGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection", unique_name: str = ""):
        super(WellAttributeGrpc, self).__init__('well attribute', guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("WellAttributeHub", petrel_connection._service_wellattribute)
        self._unique_name = self.GetUniqueName() if unique_name == "" else unique_name
        self._property_range_handler = PropertyRangeHandler()

    def GetUniqueName(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.WellAttribute_GetAttributeUniqueName(request)
        return response.value

    def GetAttributeIsWritable(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.WellAttribute_GetAttributeIsWritable(request)
        return response.value

    def GetAttributeIsSupported(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.WellAttribute_GetAttributeIsSupported(request)
        return response.value

    def GetAttribute(self, well_guid):
        self._plink._opened_test()
        request = petrelinterface_pb2.Borehole_Attribute_Request(
            attributeGuid = petrelinterface_pb2.PetrelObjectGuid( guid = self._guid ),
            wellGuid = petrelinterface_pb2.PetrelObjectGuid( guid = well_guid )
        )
        response = self._channel.WellAttribute_GetAttribute(request)
        return response

    def SetAttributeValue(self, well_guid, value):
        self._plink._opened_test()
        prd = self._property_range_handler.get_property_range_datas("", [0], value, attribute_droid = self._guid)
        request = petrelinterface_pb2.Borehole_SetAttributeValue_Request(
            attributeGuid = petrelinterface_pb2.PetrelObjectGuid( guid = self._guid ),
            wellGuid = petrelinterface_pb2.PetrelObjectGuid( guid = well_guid ),
            data = next(iter(prd))
        )
        ok = self._channel.WellAttribute_SetAttributeValue(request)
        return ok.value