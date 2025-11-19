# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, ProtoString, Primitives, Subchunk, Report
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import Date, IntStringTuples, ProtoBool, IndicesArray
from .base_hub import BaseHub
import typing

class GridPropertyHub(BaseHub):
    def GetGridPropertyGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetGridPropertyGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetGridProperty(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetGridProperty", PetrelObjectRef, msg) # type: ignore
    
    def GridProperty_GetUpscaledCells(self, msg) -> IndicesArray:
        return self._unary_wrapper("cegal.pythontool.GridProperty_GetUpscaledCells", IndicesArray, msg) # type: ignore
    
    def GridProperty_SetUpscaledCells(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.GridProperty_SetUpscaledCells", ProtoBool, msg) # type: ignore
    
    def GridProperty_DisplayUnitSymbol(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.GridProperty_DisplayUnitSymbol", ProtoString, msg) # type: ignore
    
    def GridProperty_GetChunk(self, msg) -> typing.Iterable[Subchunk]:
        return self._server_streaming_wrapper("cegal.pythontool.GridProperty_GetChunk", Subchunk, msg) # type: ignore
    
    def GridProperty_Extent(self, msg) -> Primitives:
        return self._unary_wrapper("cegal.pythontool.GridProperty_Extent", Primitives.Indices3, msg) # type: ignore
    
    def GridProperty_ParentGrid(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.GridProperty_ParentGrid", ProtoString, msg) # type: ignore
    
    def GridProperty_StreamSetChunk(self, iterable_requests) -> Report:
        return self._client_streaming_wrapper("cegal.pythontool.GridProperty_StreamSetChunk", Report, iterable_requests) # type: ignore
    
    def GridProperty_GetDate(self, msg) -> Date:
        return self._unary_wrapper("cegal.pythontool.GridProperty_GetDate", Date, msg) # type: ignore

    def GridProperty_SetDate(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.GridProperty_SetDate", ProtoBool, msg)

    def GridProperty_GetUseDate(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.GridProperty_GetUseDate", ProtoBool, msg)

    def GridProperty_SetUseDate(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.GridProperty_SetUseDate", ProtoBool, msg)
    
    def GridDictionaryProperty_GetAllDictionaryCodes(self, msg) -> IntStringTuples:
        return self._unary_wrapper("cegal.pythontool.GridDictionaryProperty_GetAllDictionaryCodes", IntStringTuples, msg) # type: ignore
    
    def GridProperty_GetParentPropertyCollection(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.GridProperty_GetParentPropertyCollection", ProtoString, msg) # type: ignore
    
    def GridProperty_GetPropertyCollection(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GridProperty_GetPropertyCollection", PetrelObjectRef, msg) # type: ignore