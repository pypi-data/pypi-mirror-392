# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool.grpc import petrelinterface_pb2
from cegalprizm.pythontool.grpc import utils as grpc_utils
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection

class FolderGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(FolderGrpc, self).__init__(WellKnownObjectDescription.Folder, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = petrel_connection._service_folder

    def CreateFolder(self, name: str) -> "FolderGrpc":
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuidAndString(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            value = name
        )

        response = self._channel.Folder_CreateFolder(request)
        return grpc_utils.pb_PetrelObjectRef_to_grpcobj(response, self._plink) if response.guid else None

    def GetObjects(self, recursive: bool = False, object_types: typing.List[str] = None):
        self._plink._opened_test()

        request = petrelinterface_pb2.GetObjectsRequest(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            recursive = recursive,
            filterTypes = object_types if object_types else []
        )

        responses = self._channel.Folder_GetObjects(request)
        return [grpc_utils.pb_PetrelObjectRef_to_grpcobj(r, self._plink) if r.guid else None for r in responses]