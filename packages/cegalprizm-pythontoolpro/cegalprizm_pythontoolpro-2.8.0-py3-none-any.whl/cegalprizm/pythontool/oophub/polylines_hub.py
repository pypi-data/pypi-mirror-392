# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuid, ProtoInt, ProtoBool, Primitives, ProtoString
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PolylineSet_GetPointsDataframe_Response
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PolylineSet_GetAttributesDataframe_Response, PolylineSet_GetIndividualAttributeValues_Response
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PolylineSet_GetPolylineType_Response
from .base_hub import BaseHub
import typing

class PolylinesHub(BaseHub):
    def GetPolylinesGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetPolylinesGrpc", PetrelObjectRef, msg) # type: ignore
    
    def CreatePolylineSet(self, msg) -> PetrelObjectGuid: # type: ignore
        return self._unary_wrapper("cegal.pythontool.CreatePolylineSet", PetrelObjectGuid, msg)
    
    def PolylineSet_GetCrs(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.PolylineSet_GetCrs", ProtoString, msg) # type: ignore

    def GetPolylineSet(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetPolylineSet", PetrelObjectRef, msg) # type: ignore
    
    def PolylineSet_GetNumPolylines(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.PolylineSet_GetNumPolylines", ProtoInt, msg) # type: ignore
    
    def PolylineSet_IsClosed(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.PolylineSet_IsClosed", ProtoBool, msg) # type: ignore
    
    def PolylineSet_GetPoints(self, msg) -> typing.Iterable[Primitives.Double3]:
        return self._server_streaming_wrapper("cegal.pythontool.PolylineSet_GetPoints", Primitives.Double3, msg) # type: ignore
    
    def PolylineSet_SetPolylinePoints(self, iterable_requests) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.PolylineSet_SetPolylinePoints", ProtoBool, iterable_requests) # type: ignore
    
    def PolylineSet_AddPolyline(self, iterable_requests) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.PolylineSet_AddPolyline", ProtoBool, iterable_requests) # type: ignore
    
    def PolylineSet_AddMultiplePolylines(self, iterable_requests) -> ProtoBool: # type: ignore
        return self._client_streaming_wrapper("cegal.pythontool.PolylineSet_AddMultiplePolylines", ProtoBool, iterable_requests)
    
    def PolylineSet_DeletePolyline(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.PolylineSet_DeletePolyline", ProtoBool, msg) # type: ignore
    
    def PolylineSet_DeleteAll(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.PolylineSet_DeleteAll", ProtoBool, msg) # type: ignore
    
    def PolylineSet_GetPointsDataframe(self, msg) -> typing.Iterable[PolylineSet_GetPointsDataframe_Response]:
        return self._server_streaming_wrapper("cegal.pythontool.PolylineSet_GetPointsDataframe", PolylineSet_GetPointsDataframe_Response, msg)
    
    def PolylineSet_GetAttributesDataframe(self, msg) -> typing.Iterable[PolylineSet_GetAttributesDataframe_Response]:
        return self._server_streaming_wrapper("cegal.pythontool.PolylineSet_GetAttributesDataframe", PolylineSet_GetAttributesDataframe_Response, msg)
    
    def PolylineSet_GetAttributeParent(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.PolylineSet_GetAttributeParent", PetrelObjectGuid, msg)
    
    def PolylineSet_AddAttribute(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.PolylineSet_AddAttribute", PetrelObjectRef, msg)
    
    def PolylineSet_DeleteAttribute(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.PolylineSet_DeleteAttribute", ProtoBool, msg)
    
    def PolylineSet_GetAllAttributes(self, msg) -> typing.Iterable[PetrelObjectRef]:
        return self._server_streaming_wrapper("cegal.pythontool.PolylineSet_GetAllAttributes", PetrelObjectRef, msg)
    
    def PolylineSet_IsWellKnownAttribute(self, msg) -> ProtoBool: # type: ignore
        return self._unary_wrapper("cegal.pythontool.PolylineSet_IsWellKnownAttribute", ProtoBool, msg)
    
    def PolylineSet_GetIndividualAttributeValues(self, msg) -> PolylineSet_GetIndividualAttributeValues_Response: # type: ignore
        return self._server_streaming_wrapper("cegal.pythontool.PolylineSet_GetIndividualAttributeValues", PolylineSet_GetIndividualAttributeValues_Response, msg)
    
    def PolylineSet_SetIndividualAttributeValues(self, iterable_requests) -> ProtoBool: # type: ignore
        return self._client_streaming_wrapper("cegal.pythontool.PolylineSet_SetIndividualAttributeValues", ProtoBool, iterable_requests)
    
    def PolylineSet_GetPolylineType(self, msg) -> PolylineSet_GetPolylineType_Response: # type: ignore
        return self._unary_wrapper("cegal.pythontool.PolylineSet_GetPolylineType", PolylineSet_GetPolylineType_Response, msg)
    
    def PolylineSet_GetAttributeUniqueName(self, msg) -> ProtoString: # type: ignore
        return self._unary_wrapper("cegal.pythontool.PolylineSet_GetAttributeUniqueName", ProtoString, msg)

    def PolylineSet_SetPolylineType(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.PolylineSet_SetPolylineType", ProtoBool, msg)