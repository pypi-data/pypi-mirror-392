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
    from cegalprizm.pythontool.grpc.borehole_grpc import GlobalWellLogGrpc

class GlobalWellLogFolderGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(GlobalWellLogFolderGrpc, self).__init__(WellKnownObjectDescription.WellLogFolderGlobal, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = petrel_connection._service_globalwelllogfolder

    def CreateGlobalWellLog(self, name: str, discrete: bool, template = None) -> "GlobalWellLogGrpc":
        self._plink._opened_test()

        template_guid = petrelinterface_pb2.PetrelObjectGuid(guid = template._petrel_object_link._guid) if template else petrelinterface_pb2.PetrelObjectGuid()

        request = petrelinterface_pb2.CreateObjectWithTemplate_Request(
            ParentGuid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            TemplateGuid = template_guid,
            Name = name,
            Discrete = discrete
        )

        response = self._channel.CreateGlobalWellLog(request)
        return grpc_utils.pb_PetrelObjectRef_to_grpcobj(response, self._plink) if response.guid else None

    def CreateGlobalWellLogFolder(self, name: str) -> "GlobalWellLogFolderGrpc":
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuidAndString(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            value = name
        )
        response = self._channel.CreateGlobalWellLogFolder(request)
        return grpc_utils.pb_PetrelObjectRef_to_grpcobj(response, self._plink) if response.guid else None

    def GetGlobalWellLogs(self, recursive: bool, log_type: str = None):
        self._plink._opened_test()

        request = petrelinterface_pb2.GlobalWellLogFolder_GetLogs_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            recursive = recursive,
            logType = log_type
        )

        responses = self._channel.GetLogs(request)
        return [grpc_utils.pb_PetrelObjectRef_to_grpcobj(response, self._plink) if response.guid else None for response in responses]