# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuid, ProtoBool, ProtoString, IntStringTuples
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import WellLog_GetSamples_Response
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import WellLog_GetTuple_Response, WellLog_GetValues_Response
from .base_hub import BaseHub

class WellLogHub(BaseHub):
    def GetWellLogGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetWellLogGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetWellLog(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetWellLog", PetrelObjectRef, msg) # type: ignore
    
    def WellLog_DisplayUnitSymbol(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.WellLog_DisplayUnitSymbol", ProtoString, msg) # type: ignore
    
    def WellLog_GetParentPythonBoreholeObject(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.WellLog_GetParentPythonBoreholeObject", PetrelObjectGuid, msg) # type: ignore
    
    def WellLog_SetSamples(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.WellLog_SetSamples", ProtoBool, msg) # type: ignore
    
    def WellLog_GetSamples(self, msg) -> WellLog_GetSamples_Response:
        return self._unary_wrapper("cegal.pythontool.WellLog_GetSamples", WellLog_GetSamples_Response, msg) # type: ignore
    
    def WellLog_GetGlobalWellLog(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.WellLog_GetGlobalWellLog", PetrelObjectGuid, msg) # type: ignore
    
    def DiscreteWellLog_GetAllDictionaryCodes(self, msg) -> IntStringTuples:
        return self._unary_wrapper("cegal.pythontool.DiscreteWellLog_GetAllDictionaryCodes", IntStringTuples, msg) # type: ignore

    def WellLog_GetTupleValues(self, msg) -> WellLog_GetTuple_Response:
        return self._server_streaming_wrapper("cegal.pythontool.WellLog_GetTupleValues", WellLog_GetTuple_Response, msg)

    def WellLog_GetLogValues(self, msg) -> WellLog_GetValues_Response:
        return self._server_streaming_wrapper("cegal.pythontool.WellLog_GetLogValues", WellLog_GetValues_Response, msg)
    