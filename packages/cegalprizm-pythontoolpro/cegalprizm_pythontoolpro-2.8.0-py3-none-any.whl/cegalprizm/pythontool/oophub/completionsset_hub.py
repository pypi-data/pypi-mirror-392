# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectGuid, ProtoBool, ProtoStrings
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import CompletionsSet_GetData_Response, CompletionsSet_GetDepth_Response
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObject_GetDate_Response
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import CompletionsSet_CasingStrings_GetParts_Response, CompletionsSet_AddCasingStringPart_Response
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import CompletionsSet_CasingStrings_SetPartDepth_Response, CompletionsSet_Perforations_GetSkinFactor_Response
from .base_hub import BaseHub

class CompletionsSetHub(BaseHub):
    def GetCompletionsSetDataFrame(self, msg) -> CompletionsSet_GetData_Response:
        return self._server_streaming_wrapper("cegal.pythontool.CompletionsSet_GetCompletionsData", CompletionsSet_GetData_Response, msg) # type: ignore
    
    def GetCasingStrings(self, msg) -> PetrelObjectGuid:
        return self._server_streaming_wrapper("cegal.pythontool.CompletionsSet_GetCasingStrings", PetrelObjectGuid, msg) # type: ignore
    
    def GetPerforations(self, msg) -> PetrelObjectGuid:
        return self._server_streaming_wrapper("cegal.pythontool.CompletionsSet_GetPerforations", PetrelObjectGuid, msg)
    
    def GetPlugbacks(self, msg) -> PetrelObjectGuid:
        return self._server_streaming_wrapper("cegal.pythontool.CompletionsSet_GetPlugbacks", PetrelObjectGuid, msg)
    
    def GetSqueezes(self, msg) -> PetrelObjectGuid:
        return self._server_streaming_wrapper("cegal.pythontool.CompletionsSet_GetSqueezes", PetrelObjectGuid, msg)

    def AddPerforation(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_AddPerforation", PetrelObjectGuid, msg)
    
    def AddCasingString(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_AddCasingString", PetrelObjectGuid, msg)
    
    def AddPlugback(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_AddPlugback", PetrelObjectGuid, msg)
    
    def AddSqueeze(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_AddSqueeze", PetrelObjectGuid, msg)
    
    # CasingStrings
    
    def GetCasingStringEndDepth(self, msg) -> CompletionsSet_GetDepth_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_GetCasingStringEndDepth", CompletionsSet_GetDepth_Response, msg) # type: ignore
    
    def SetCasingStringEndDepth(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_SetCasingStringEndDepth", ProtoBool, msg)
    
    def GetCasingStringStartDate(self, msg) -> PetrelObject_GetDate_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_GetCasingStringStartDate", PetrelObject_GetDate_Response, msg) # type: ignore
    
    def SetCasingStringStartDate(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_SetCasingStringStartDate", ProtoBool, msg)

    def GetCasingStringEquipment(self, msg) -> ProtoStrings:
        return self._server_streaming_wrapper("cegal.pythontool.CompletionsSet_GetAvailableCasingEquipment", ProtoStrings, msg)

    def GetCasingStringParts(self, msg) -> CompletionsSet_CasingStrings_GetParts_Response:
        return self._server_streaming_wrapper("cegal.pythontool.CompletionsSet_GetCasingStringParts", CompletionsSet_CasingStrings_GetParts_Response, msg)
    
    def AddCasingStringPart(self, msg) -> CompletionsSet_AddCasingStringPart_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_AddCasingStringPart", CompletionsSet_AddCasingStringPart_Response, msg)
    
    def RemoveCasingStringPart(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_RemoveCasingStringPart", ProtoBool, msg)

    def SetCasingStringPartDepth(self, msg) -> CompletionsSet_CasingStrings_SetPartDepth_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_SetCasingPartDepth", CompletionsSet_CasingStrings_SetPartDepth_Response, msg)

    # Perforations

    def GetPerforationTopMd(self, msg) -> CompletionsSet_GetDepth_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_GetPerforationTopMd", CompletionsSet_GetDepth_Response, msg)
    
    def SetPerforationTopMd(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_SetPerforationTopMd", ProtoBool, msg)

    def GetPerforationBottomMd(self, msg) -> CompletionsSet_GetDepth_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_GetPerforationBottomMd", CompletionsSet_GetDepth_Response, msg)

    def SetPerforationBottomMd(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_SetPerforationBottomMd", ProtoBool, msg)

    def GetPerforationDate(self, msg) -> PetrelObject_GetDate_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_GetPerforationDate", PetrelObject_GetDate_Response, msg)

    def SetPerforationDate(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_SetPerforationDate", ProtoBool, msg)

    def GetPerforationSkinFactor(self, msg) -> CompletionsSet_Perforations_GetSkinFactor_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_GetPerforationSkinFactor", CompletionsSet_Perforations_GetSkinFactor_Response, msg)

    def SetPerforationSkinFactor(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_SetPerforationSkinFactor", ProtoBool, msg)
    
    # Plugbacks

    def GetPlugbackTopMd(self, msg) -> CompletionsSet_GetDepth_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_GetPlugbackTopMd", CompletionsSet_GetDepth_Response, msg)
    
    def SetPlugbackTopMd(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_SetPlugbackTopMd", ProtoBool, msg)
    
    def GetPlugbackBottomMd(self, msg) -> CompletionsSet_GetDepth_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_GetPlugbackBottomMd", CompletionsSet_GetDepth_Response, msg)
    
    def GetPlugbackStartDate(self, msg) -> PetrelObject_GetDate_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_GetPlugbackStartDate", PetrelObject_GetDate_Response, msg)
    
    def SetPlugbackStartDate(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_SetPlugbackStartDate", ProtoBool, msg)
    
    # Squeezes

    def GetSqueezeTopMd(self, msg) -> CompletionsSet_GetDepth_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_GetSqueezeTopMd", CompletionsSet_GetDepth_Response, msg)
    
    def SetSqueezeTopMd(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_SetSqueezeTopMd", ProtoBool, msg)
    
    def GetSqueezeBottomMd(self, msg) -> CompletionsSet_GetDepth_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_GetSqueezeBottomMd", CompletionsSet_GetDepth_Response, msg)
    
    def SetSqueezeBottomMd(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_SetSqueezeBottomMd", ProtoBool, msg)
    
    def GetSqueezeStartDate(self, msg) -> PetrelObject_GetDate_Response:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_GetSqueezeStartDate", PetrelObject_GetDate_Response, msg)
    
    def SetSqueezeStartDate(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CompletionsSet_SetSqueezeStartDate", ProtoBool, msg)