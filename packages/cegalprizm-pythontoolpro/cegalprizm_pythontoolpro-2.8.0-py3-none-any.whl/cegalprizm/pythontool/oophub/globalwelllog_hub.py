# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuids, ProtoString, IntStringTuples
from .base_hub import BaseHub


class GlobalWellLogHub(BaseHub):
    def GetGlobalWellLogGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetGlobalWellLogGrpc", PetrelObjectRef, msg)
    
    def GetGlobalWellLog(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetGlobalWellLog", PetrelObjectRef, msg)
    
    def GlobalWellLog_GetAllLogs(self, msg) -> PetrelObjectGuids:
        return self._unary_wrapper("cegal.pythontool.GlobalWellLog_GetAllLogs", PetrelObjectGuids, msg)
    
    def GlobalWellLog_GetWellLogByBoreholeNameOrGuid(self, msg) -> PetrelObjectGuids:
        return self._unary_wrapper("cegal.pythontool.GlobalWellLog_GetWellLogByBoreholeNameOrGuid", PetrelObjectGuids, msg)

    def GlobalWellLog_DisplayUnitSymbol(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.GlobalWellLog_DisplayUnitSymbol", ProtoString, msg)

    def GlobalWellLog_CreateWellLog(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GlobalWellLog_CreateWellLog", PetrelObjectRef, msg)
    
    def GlobalWellLog_CreateDictionaryWellLog(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GlobalWellLog_CreateDictionaryWellLog", PetrelObjectRef, msg)

    def GlobalWellLog_GetAllDictionaryCodes(self, msg) -> IntStringTuples:
        return self._unary_wrapper("cegal.pythontool.GlobalWellLog_GetAllDictionaryCodes", IntStringTuples, msg)