# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, ProtoString, ProtoStrings, StringsMap, ProtoBool, PetrelObjectGuid
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObject_GetTemplate_Response
from .base_hub import BaseHub
import typing

class PetrelObjectHub(BaseHub):
    def GetPetrelObjectGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetPetrelObjectGrpc", PetrelObjectRef, msg) # type: ignore
    
    def PetrelObject_GetPetrelName(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_GetPetrelName", ProtoString, msg) # type: ignore

    def PetrelObject_SetPetrelName(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_SetPetrelName", ProtoBool, msg)
    
    def PetrelObject_GetPath(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_GetPath", ProtoString, msg) # type: ignore
    
    def PetrelObject_GetDroidString(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_GetDroidString", ProtoString, msg) # type: ignore
    
    def PetrelObject_RetrieveStats(self, msg) -> StringsMap:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_RetrieveStats", StringsMap, msg) # type: ignore
    
    def PetrelObject_GetReadOnly(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_GetReadOnly", ProtoBool, msg) # type: ignore
    
    def PetrelObject_Clone(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_Clone", PetrelObjectGuid, msg) # type: ignore
    
    def PetrelObject_IsAlwaysReadonly(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_IsAlwaysReadonly", ProtoString, msg) # type: ignore
    
    def PetrelObject_GetOceanType(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_GetOceanType", ProtoString, msg) # type: ignore
    
    def PetrelObject_RetrieveHistory(self, msg) -> typing.Iterable[ProtoStrings]:
        return self._server_streaming_wrapper("cegal.pythontool.PetrelObject_RetrieveHistory", ProtoStrings, msg) # type: ignore
    
    def PetrelObject_GetTemplate(self, msg) -> PetrelObject_GetTemplate_Response:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_GetTemplate", PetrelObject_GetTemplate_Response, msg) # type: ignore

    def PetrelObject_GetComments(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_GetComments", ProtoString, msg) # type: ignore

    def PetrelObject_AddComment(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_AddComment", ProtoBool, msg) # type: ignore
    
    def PetrelObject_GetColorTableInfo(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_GetColorTableInfo", ProtoString, msg) # type: ignore
    
    def PetrelObject_GetDomain(self, msg) -> ProtoString: # type: ignore
        return self._unary_wrapper("cegal.pythontool.PetrelObject_GetDomain", ProtoString, msg)

    def PetrelObject_Move(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_Move", ProtoBool, msg)

    def PetrelObject_Delete(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_Delete", ProtoBool, msg)


    def PetrelObject_GetParentFolder(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.PetrelObject_GetParentFolder", PetrelObjectRef, msg)