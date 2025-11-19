# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from cegalprizm.pythontool.grpc import grid_grpc, petrelinterface_pb2

import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.zone_hub import ZoneHub

class ZoneGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection", sub_type: str = WellKnownObjectDescription.Zone):
        super(ZoneGrpc, self).__init__(sub_type, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast('ZoneHub', petrel_connection._service_zone)

    def GetParentGrid(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.Zone_GetParentGrid(request)
        return grid_grpc.GridGrpc(response.guid, self._plink)
    
    def GetBaseK(self) -> int:
        self._plink._opened_test
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.Zone_GetBaseK(request)
        return response.value
    
    def GetTopK(self) -> int:
        self._plink._opened_test
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.Zone_GetTopK(request)
        return response.value
    
    def GetNumberOfZones(self) -> int:
        self._plink._opened_test
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.Zone_GetNumberOfZones(request)
        return response.value
    
    def GetZones(self):
        self._plink._opened_test
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.Zone_GetZones(request)
        guids = [item.guid for item in response.guids]
        return [ZoneGrpc(guid, self._plink) for guid in guids]
    
    def GetParentZone(self) -> 'ZoneGrpc':
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.Zone_GetParentZone(request)
        if not response.guid:
            return None
        return ZoneGrpc(response.guid, self._plink)