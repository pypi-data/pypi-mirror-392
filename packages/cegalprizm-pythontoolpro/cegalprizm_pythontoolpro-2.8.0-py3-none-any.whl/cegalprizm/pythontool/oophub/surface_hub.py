# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuid, PetrelObjectGuids, Primitives, ProtoDoubles, ProtoString
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import AxesRange, Surface_GetIjk_Response, Surface_GetPositions_Response
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import Surface_GetPositionsDataframe_Response
from .base_hub import BaseHub


class SurfaceHub(BaseHub):
    def GetSurfaceGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetSurfaceGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetSurface(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetSurface", PetrelObjectRef, msg) # type: ignore

    def CreateSurface(self, iterable_requests) -> PetrelObjectGuid:
        return self._client_streaming_wrapper("cegal.pythontool.CreateSurface", PetrelObjectGuid, iterable_requests) # type: ignore
    
    def RegularHeightField_GetCrs(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.RegularHeightField_GetCrs", ProtoString, msg) # type: ignore
    
    def RegularHeightField_GetAffineTransform(self, msg) -> ProtoDoubles:
        return self._server_streaming_wrapper("cegal.pythontool.RegularHeightField_GetAffineTransform", ProtoDoubles, msg) # type: ignore
    
    def Surface_Extent(self, msg) -> Primitives.Indices2:
        return self._unary_wrapper("cegal.pythontool.Surface_Extent", Primitives.Indices2, msg) # type: ignore
    
    def Surface_AxesRange(self, msg) -> AxesRange:
        return self._unary_wrapper("cegal.pythontool.Surface_AxesRange", AxesRange, msg) # type: ignore
    
    def Surface_IndexAtPosition(self, msg) -> Primitives.ExtIndices2:
        return self._unary_wrapper("cegal.pythontool.Surface_IndexAtPosition", Primitives.ExtIndices2, msg) # type: ignore
    
    def Surface_PositionAtIndex(self, msg) -> Primitives.ExtDouble3:
        return self._unary_wrapper("cegal.pythontool.Surface_PositionAtIndex", Primitives.ExtDouble3, msg) # type: ignore
    
    def Surface_ParentSurfaceCollection(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.Surface_ParentSurfaceCollection", PetrelObjectGuid, msg) # type: ignore
    
    def Surface_Properties(self, msg) -> PetrelObjectGuids:
        return self._unary_wrapper("cegal.pythontool.Surface_Properties", PetrelObjectGuids, msg) # type: ignore
    
    def Surface_GetIjk(self, msg) -> Surface_GetIjk_Response:
        return self._unary_wrapper("cegal.pythontool.Surface_GetIjk", Surface_GetIjk_Response, msg) # type: ignore
    
    def Surface_GetPositions(self, msg) -> Surface_GetPositions_Response:
        return self._unary_wrapper("cegal.pythontool.Surface_GetPositions", Surface_GetPositions_Response, msg) # type: ignore

    def Surface_GetPositionsDataframe(self, msg) -> Surface_GetPositionsDataframe_Response: # type: ignore
        return self._server_streaming_wrapper("cegal.pythontool.Surface_GetPositionsDataframe", Surface_GetPositionsDataframe_Response, msg)

    def Surface_CreateAttribute(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.Surface_CreateAttribute", PetrelObjectRef, msg)