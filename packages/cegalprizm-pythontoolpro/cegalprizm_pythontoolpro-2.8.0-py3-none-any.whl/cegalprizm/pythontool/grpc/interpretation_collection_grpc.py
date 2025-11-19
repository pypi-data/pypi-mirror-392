# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from cegalprizm.pythontool.grpc import petrelinterface_pb2
from cegalprizm.pythontool.grpc import utils as grpc_utils
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.interpretation_collection_hub import InterpretationCollectionHub

class InterpretationCollectionGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(InterpretationCollectionGrpc, self).__init__(WellKnownObjectDescription.InterpretationCollection, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._invariant_content = {}
        self._channel = typing.cast("InterpretationCollectionHub", petrel_connection._service_interpretationcollection)

    def CreateFolder(self, name: str) -> "InterpretationCollectionGrpc":
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuidAndString(
            guid=petrelinterface_pb2.PetrelObjectGuid(guid=self._guid, sub_type=self._sub_type),
            value=name
        )

        response = self._channel.InterpretationCollection_CreateFolder(request)
        return grpc_utils.pb_PetrelObjectRef_to_grpcobj(response, self._plink) if response.guid else None