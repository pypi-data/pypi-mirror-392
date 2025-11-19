# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuids, ProtoString, ProtoBool, ProtoInt, StringsMap, VersionAccepted
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import Project_GetAvailableWellSymbolDescriptions_Response
from .base_hub import BaseHub
import typing

class ProjectHub(BaseHub):
    def GetProjectGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetProjectGrpc", PetrelObjectRef, msg)
    
    def VerifyClientVersion(self, msg) -> VersionAccepted:
        return self._unary_wrapper("cegal.pythontool.VerifyClientVersion", VersionAccepted, msg)
    
    def Ping(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.Ping", ProtoInt, msg)
    
    def GetCurrentProjectName(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.GetCurrentProjectName", ProtoString, msg)

    def GetCurrentProjectPath(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.GetCurrentProjectPath", ProtoString, msg)
    
    def AProjectIsActive(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.AProjectIsActive", ProtoBool, msg)
    
    def EnableHistory(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.EnableHistory", ProtoBool, msg)
    
    def SetScriptName(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.SetScriptName", ProtoString, msg)
    
    def GetStringsMap(self, msg) -> typing.Iterable[StringsMap]:
        return self._server_streaming_wrapper("cegal.pythontool.GetStringsMap", StringsMap, msg)
    
    def Project_ImportWorkflow(self, msg) -> PetrelObjectGuids:
        return self._unary_wrapper("cegal.pythontool.Project_ImportWorkflow", PetrelObjectGuids, msg)
    
    def Project_GetRegisteredObservedDataVersions(self, msg) -> StringsMap:
        return self._unary_wrapper("cegal.pythontool.Project_GetRegisteredObservedDataVersions", StringsMap, msg)
    
    def Project_GetPetrelObjectsByGuids(self, msg) -> PetrelObjectRef:
        return self._server_streaming_wrapper("cegal.pythontool.Project_GetPetrelObjectsByGuids", PetrelObjectRef, msg)

    def Project_GetPetrelProjectUnits(self, msg) -> StringsMap:
        return self._unary_wrapper("cegal.pythontool.Project_GetPetrelProjectUnits", StringsMap, msg)

    def GetServerVersion(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.GetServerVersion", ProtoString, msg)
    
    def GetCrs(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.GetCrs", ProtoString, msg)
    
    def Project_ClearCache(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.Project_ClearCache", ProtoBool, msg)
    
    def Project_GetPetrelObjectsByType(self, msg) -> PetrelObjectRef:
        return self._server_streaming_wrapper("cegal.pythontool.Project_GetPetrelObjectsByType", PetrelObjectRef, msg)

    def Project_GetAvailableWellSymbolDescriptions(self, msg) -> Project_GetAvailableWellSymbolDescriptions_Response:
        return self._server_streaming_wrapper("cegal.pythontool.Project_GetAvailableWellSymbolDescriptions", Project_GetAvailableWellSymbolDescriptions_Response, msg)

    def Project_CreateMarkerCollection(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.Project_CreateMarkerCollection", PetrelObjectRef, msg)

    def Project_GetPetrelObjectsByName(self, msg) -> PetrelObjectRef:
        return self._server_streaming_wrapper("cegal.pythontool.Project_GetPetrelObjectsByName", PetrelObjectRef, msg)

    def Project_CreateFolder(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.Project_CreateFolder", PetrelObjectRef, msg)

    def Project_DeletePetrelObjects(self, msg) -> PetrelObjectGuids:
        return self._unary_wrapper("cegal.pythontool.Project_DeletePetrelObjects", PetrelObjectGuids, msg)

    def Project_CreateBoreholeCollection(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.Project_CreateBoreholeCollection", PetrelObjectRef, msg)

    def Project_GetDefaultSeismicDirectory(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.Project_GetDefaultSeismicDirectory", ProtoString, msg)

    def Project_CreateGlobalWellLog(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.Project_CreateGlobalWellLog", PetrelObjectRef, msg)