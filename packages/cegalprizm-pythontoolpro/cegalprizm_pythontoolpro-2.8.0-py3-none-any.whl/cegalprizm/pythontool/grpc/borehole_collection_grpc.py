# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from .borehole_grpc import BoreholeGrpc
from cegalprizm.pythontool.grpc import petrelinterface_pb2
from cegalprizm.pythontool.grpc import utils as grpc_utils
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.borehole_collection_hub import BoreholeCollectionHub

class BoreholeCollectionGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(BoreholeCollectionGrpc, self).__init__(WellKnownObjectDescription.BoreholeCollection, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._invariant_content = {}
        self._channel = typing.cast("BoreholeCollectionHub", petrel_connection._service_boreholecollection)

    def GetWells(self, recursive, saved_search):
        self._plink._opened_test()
        saved_search_guid = None
        if saved_search is not None:
            saved_search_guid = petrelinterface_pb2.PetrelObjectGuid(guid = saved_search._savedsearch_object_link._guid, sub_type = saved_search._savedsearch_object_link._sub_type)
        request = petrelinterface_pb2.BoreholeCollection_GetWells_Request(
            Guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            Recursive = recursive,
            SavedSearchGuid = saved_search_guid
        )
        responses = self._channel.BoreholeCollection_GetWells(request)
        return [BoreholeGrpc(response.guid, self._plink) for response in responses]
    
    def GetBoreholeCollections(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.BoreholeCollection_GetBoreholeCollections(request)
        return [BoreholeCollectionGrpc(response.guid, self._plink) for response in responses]

    def CreateBoreholeCollection(self, name: str) -> "BoreholeCollectionGrpc":
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuidAndString(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            value = name
        )

        response = self._channel.BoreholeCollection_CreateBoreholeCollection(request)
        return grpc_utils.pb_PetrelObjectRef_to_grpcobj(response, self._plink) if response.guid else None