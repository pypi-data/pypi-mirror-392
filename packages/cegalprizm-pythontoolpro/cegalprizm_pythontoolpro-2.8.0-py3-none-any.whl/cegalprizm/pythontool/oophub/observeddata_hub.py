# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuid, ProtoString, ProtoDoubles
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import ProtoInt, ProtoBool
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import ObservedDataSet_GetDates_Response
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import ObservedDataSet_GetDataFrame_Response
from .base_hub import BaseHub
import typing

class ObservedDataHub(BaseHub):
    def GetObservedDataGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetObservedDataGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetObservedData(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetObservedData", PetrelObjectRef, msg) # type: ignore
    
    def ObservedData_SetValues(self, iterable_requests) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.ObservedData_SetValues", ProtoBool, iterable_requests) # type: ignore
    
    def ObservedData_GetValues(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.ObservedData_GetValues", ProtoDoubles, msg) # type: ignore

    def ObservedData_DisplayUnitSymbol(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.ObservedData_DisplayUnitSymbol", ProtoString, msg) # type: ignore

    def ObservedData_GetParentObservedDataSet(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.ObservedData_GetParentObservedDataSet", PetrelObjectGuid, msg) # type: ignore

class ObservedDataSetHub(BaseHub):
    def GetObservedDataSetGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetObservedDataSetGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetObservedDataSet(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetObservedDataSet", PetrelObjectRef, msg) # type: ignore
    
    def ObservedDataSet_GetObservedDataObjects(self, msg) -> typing.Iterable[PetrelObjectGuid]:
        return self._server_streaming_wrapper("cegal.pythontool.ObservedDataSet_GetObservedDataObjects", PetrelObjectGuid, msg) # type: ignore

    def ObservedDataSet_GetNumberOfObservedDataObjects(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.ObservedDataSet_GetNumberOfObservedDataObjects", ProtoInt, msg) # type: ignore
    
    def ObservedDataSet_GetDates(self, msg) -> typing.Iterable[ObservedDataSet_GetDates_Response]:
        return self._server_streaming_wrapper("cegal.pythontool.ObservedDataSet_GetDates", ObservedDataSet_GetDates_Response, msg) # type: ignore
    
    def ObservedDataSet_Append(self, iterable_requests) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.ObservedDataSet_Append", ProtoBool, iterable_requests) # type: ignore
    
    def ObservedDataSet_CreateObservedData(self, iterable_requests) -> PetrelObjectGuid:
        return self._client_streaming_wrapper("cegal.pythontool.ObservedDataSet_CreateObservedData", PetrelObjectGuid, iterable_requests) # type: ignore

    def ObservedDataSet_GetParentPythonBoreholeObject(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.ObservedDataSet_GetParentPythonBoreholeObject", PetrelObjectGuid, msg) # type: ignore
    
    def ObservedDataSet_GetDataFrame(self, msg) -> typing.Iterable[ObservedDataSet_GetDataFrame_Response]:
        return self._server_streaming_wrapper("cegal.pythontool.ObservedDataSet_GetDataFrame", ObservedDataSet_GetDataFrame_Response, msg)
        