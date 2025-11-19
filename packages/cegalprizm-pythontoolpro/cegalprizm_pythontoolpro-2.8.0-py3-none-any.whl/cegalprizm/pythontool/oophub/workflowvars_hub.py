# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import ProtoDouble, ProtoString, Date, ProtoEmpty, ProtoInt, ProtoBool
from .base_hub import BaseHub

class WorkflowvarsHub(BaseHub):
    def GetVarDouble(self, msg) -> ProtoDouble:
        return self._unary_wrapper("cegal.pythontool.GetVarDouble", ProtoDouble, msg) # type: ignore
    
    def GetVarString(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.GetVarString", ProtoString, msg) # type: ignore
    
    def GetVarDate(self, msg) -> Date:
        return self._unary_wrapper("cegal.pythontool.GetVarDate", Date, msg) # type: ignore
    
    def SetVarDouble(self, msg) -> ProtoEmpty:
        return self._unary_wrapper("cegal.pythontool.SetVarDouble", ProtoEmpty, msg) # type: ignore
    
    def SetVarString(self, msg) -> ProtoEmpty:
        return self._unary_wrapper("cegal.pythontool.SetVarString", ProtoEmpty, msg) # type: ignore
    
    def SetVarDate(self, msg) -> ProtoEmpty:
        return self._unary_wrapper("cegal.pythontool.SetVarDate", ProtoEmpty, msg) # type: ignore
    
    def GetVarType(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.GetVarType", ProtoInt, msg) # type: ignore
    
    def VarExists(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.VarExists", ProtoBool, msg) # type: ignore