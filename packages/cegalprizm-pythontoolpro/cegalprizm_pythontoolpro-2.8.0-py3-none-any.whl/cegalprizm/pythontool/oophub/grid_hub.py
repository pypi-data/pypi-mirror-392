# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuid, PetrelObjectGuids, ProtoBool, ProtoInt, AxesRange, Primitives
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import Grid_VerticesPositions_Reply, Grid_GetIjk_Response
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import Grid_GetPositions_Response
from .base_hub import BaseHub
import typing

class GridHub(BaseHub):
    def GetGridGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetGridGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetGrid(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetGrid", PetrelObjectRef, msg) # type: ignore
    
    def Grid_Extent(self, msg) -> Primitives.Indices3:
        return self._unary_wrapper("cegal.pythontool.Grid_Extent", Primitives.Indices3, msg) # type: ignore
    
    def Grid_AxesRange(self, msg) -> AxesRange:
        return self._unary_wrapper("cegal.pythontool.Grid_AxesRange", AxesRange, msg) # type: ignore
    
    def Grid_IndicesOfCell(self, msg) -> Primitives.ExtIndices3:
        return self._unary_wrapper("cegal.pythontool.Grid_IndicesOfCell", Primitives.ExtIndices3, msg) # type: ignore
    
    def Grid_PositionOfCellCenter(self, msg) -> Primitives.ExtDouble3:
        return self._unary_wrapper("cegal.pythontool.Grid_PositionOfCellCenter", Primitives.ExtDouble3, msg) # type: ignore
    
    def Grid_VerticesPositions(self, msg) -> Grid_VerticesPositions_Reply:
        return self._unary_wrapper("cegal.pythontool.Grid_VerticesPositions", Grid_VerticesPositions_Reply, msg) # type: ignore
    
    def Grid_IsCellDefined(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.Grid_IsCellDefined", ProtoBool, msg) # type: ignore
    
    def Grid_GetIjk(self, msg) -> Grid_GetIjk_Response:
        return self._unary_wrapper("cegal.pythontool.Grid_GetIjk", Grid_GetIjk_Response, msg) # type: ignore
    
    def Grid_GetPositions(self, msg) -> Grid_GetPositions_Response:
        return self._unary_wrapper("cegal.pythontool.Grid_GetPositions", Grid_GetPositions_Response, msg) # type: ignore
    
    def Grid_GetProperties(self, msg) -> typing.Iterable[PetrelObjectGuid]:
        return self._server_streaming_wrapper("cegal.pythontool.Grid_GetProperties", PetrelObjectGuid, msg) # type: ignore

    def Grid_GetDictionaryProperties(self, msg) -> typing.Iterable[PetrelObjectGuid]:
        return self._server_streaming_wrapper("cegal.pythontool.Grid_GetDictionaryProperties", PetrelObjectGuid, msg) # type: ignore

    def Grid_GetZones(self, msg) -> PetrelObjectGuids:
        return self._unary_wrapper("cegal.pythontool.Grid_GetZones", PetrelObjectGuids, msg) # type: ignore

    def Grid_GetNumberOfZones(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.Grid_GetNumberOfZones", ProtoInt, msg) # type: ignore

    def Grid_GetSegments(self, msg) -> PetrelObjectGuids:
        return self._unary_wrapper("cegal.pythontool.Grid_GetSegments", PetrelObjectGuids, msg) # type: ignore

    def Grid_GetNumberOfSegments(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.Grid_GetNumberOfSegments", ProtoInt, msg) # type: ignore

    def Grid_GetPropertyCollection(self, msg) -> PetrelObjectGuid: # type: ignore
        return self._unary_wrapper("cegal.pythontool.Grid_GetPropertyCollection", PetrelObjectGuid, msg)