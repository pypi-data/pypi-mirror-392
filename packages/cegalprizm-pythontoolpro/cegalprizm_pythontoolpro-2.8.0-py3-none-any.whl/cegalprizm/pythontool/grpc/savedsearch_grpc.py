# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from .borehole_grpc import BoreholeGrpc
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from cegalprizm.pythontool.grpc import petrelinterface_pb2
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.savedsearch_hub import SavedSearchHub

class SavedSearchGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(SavedSearchGrpc, self).__init__(WellKnownObjectDescription.SavedSearch, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("SavedSearchHub", petrel_connection._service_savedsearch)
        self._is_dynamic = None

    def GetWells(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.SavedSearch_GetWells(request)
        return [BoreholeGrpc(response.guid, self._plink) for response in responses]

    def IsDynamic(self) -> bool:
        if self._is_dynamic is not None:
            return self._is_dynamic
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._channel.SavedSearch_IsDynamic(request)
        self._is_dynamic = response.value
        return self._is_dynamic