# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuid, ProtoString, ProtoInt, ProtoBool, Primitives
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PropertyRangeData
from .base_hub import BaseHub
import typing

class PointsHub(BaseHub):
    def GetPointsGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetPointsGrpc", PetrelObjectRef, msg) # type: ignore
    
    def CreatePointSet(self, msg) -> PetrelObjectGuid: # type: ignore
        return self._unary_wrapper("cegal.pythontool.CreatePointSet", PetrelObjectGuid, msg)

    def PointSet_GetCrs(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.PointSet_GetCrs", ProtoString, msg) # type: ignore
    
    def GetPointSet(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetPointSet", PetrelObjectRef, msg) # type: ignore
    
    def PointSet_GetPropertyCount(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.PointSet_GetPropertyCount", ProtoInt, msg) # type: ignore
    
    def PointSet_GetPointCount(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.PointSet_GetPointCount", ProtoInt, msg) # type: ignore
    
    def PointSet_AddPoints(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.PointSet_AddPoints", ProtoBool, msg) # type: ignore
    
    def PointSet_AddProperties(self, iterable_requests) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.PointSet_AddProperties", ProtoBool, iterable_requests) # type: ignore
    
    def PointSet_AttributesInfo(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.PointSet_AttributesInfo", ProtoString, msg) # type: ignore
    
    def PointSet_DeletePoints(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.PointSet_DeletePoints", ProtoBool, msg) # type: ignore
    
    def PointSet_GetPositionValuesByInds(self, msg) -> typing.Iterable[PropertyRangeData]:
        return self._server_streaming_wrapper("cegal.pythontool.PointSet_GetPositionValuesByInds", PropertyRangeData, msg) # type: ignore
    
    def PointSet_GetPositionValuesByRange(self, msg) -> typing.Iterable[PropertyRangeData]:
        return self._server_streaming_wrapper("cegal.pythontool.PointSet_GetPositionValuesByRange", PropertyRangeData, msg) # type: ignore
    
    def PointSet_GetPropertiesValuesByInds(self, msg) -> typing.Iterable[PropertyRangeData]:
        return self._server_streaming_wrapper("cegal.pythontool.PointSet_GetPropertiesValuesByInds", PropertyRangeData, msg) # type: ignore
    
    def PointSet_OrderedUniquePropertyNames(self, msg) -> Primitives.StringArray:
        return self._unary_wrapper("cegal.pythontool.PointSet_OrderedUniquePropertyNames", Primitives.StringArray, msg) # type: ignore
    
    def PointSet_SetPropertyValues(self, iterable_requests) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.PointSet_SetPropertyValues", ProtoBool, iterable_requests) # type: ignore
    