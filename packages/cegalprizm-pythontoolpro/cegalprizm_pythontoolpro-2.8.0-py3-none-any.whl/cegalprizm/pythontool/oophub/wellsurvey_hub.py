# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuid, ProtoBool, ProtoDouble, ProtoInt, ProtoDoubles

from .base_hub import BaseHub
import typing

class XyzWellSurveyHub(BaseHub):
    def GetXyzWellSurveyGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetXyzWellSurveyGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetXyzWellSurvey(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetXyzWellSurvey", PetrelObjectRef, msg) # type: ignore
    
    def XyzWellSurvey_RecordCount(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.XyzWellSurvey_RecordCount", ProtoInt, msg) # type: ignore
    
    def XyzWellSurvey_GetXs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XyzWellSurvey_GetXs", ProtoDoubles, msg) # type: ignore
    
    def XyzWellSurvey_GetYs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XyzWellSurvey_GetYs", ProtoDoubles, msg) # type: ignore
    
    def XyzWellSurvey_GetZs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XyzWellSurvey_GetZs", ProtoDoubles, msg) # type: ignore
    
    def XyzWellSurvey_GetMds(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XyzWellSurvey_GetMds", ProtoDoubles, msg) # type: ignore
    
    def XyzWellSurvey_GetIncls(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XyzWellSurvey_GetIncls", ProtoDoubles, msg) # type: ignore
    
    def XyzWellSurvey_GetAzims(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XyzWellSurvey_GetAzims", ProtoDoubles, msg) # type: ignore
    
    def XyzWellSurvey_SetRecords(self, iterable_requests) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.XyzWellSurvey_SetRecords", ProtoBool, iterable_requests) # type: ignore
    
    def XyzWellSurvey_SetSurveyAsDefinitive(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.XyzWellSurvey_SetSurveyAsDefinitive", ProtoBool, msg) # type: ignore
    
    def XyzWellSurvey_TieInMd(self, msg) -> ProtoDouble:
        return self._unary_wrapper("cegal.pythontool.XyzWellSurvey_TieInMd", ProtoDouble, msg) # type: ignore
    
    def XyzWellSurvey_SetTieInMd(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.XyzWellSurvey_SetTieInMd", ProtoBool, msg) # type: ignore
    
    def XyzWellSurvey_IsSidetrack(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.XyzWellSurvey_IsSidetrack", ProtoBool, msg) # type: ignore

    def XyzWellSurvey_IsDefinitive(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.XyzWellSurvey_IsDefinitive", ProtoBool, msg) # type: ignore

    def XyzWellSurvey_GetParentPythonBoreholeObject(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.XyzWellSurvey_GetParentPythonBoreholeObject", PetrelObjectGuid, msg) # type: ignore

    def XyzWellSurvey_IsAlgorithmMinimumCurvature(self, msg) -> ProtoBool: 
        return self._unary_wrapper("cegal.pythontool.XyzWellSurvey_IsAlgorithmMinimumCurvature", ProtoBool, msg) # type: ignore

    def XyzWellSurvey_SetAlgorithmToMinimumCurvature(self, msg) -> ProtoBool: 
        return self._unary_wrapper("cegal.pythontool.XyzWellSurvey_SetAlgorithmToMinimumCurvature", ProtoBool, msg) # type: ignore
    
    def XyzWellSurvey_IsCalculationValid(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.XyzWellSurvey_IsCalculationValid", ProtoBool, msg) # type: ignore

class XytvdWellSurveyHub(BaseHub):
    def GetXytvdWellSurveyGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetXytvdWellSurveyGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetXytvdWellSurvey(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetXytvdWellSurvey", PetrelObjectRef, msg) # type: ignore
    
    def XytvdWellSurvey_RecordCount(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.XytvdWellSurvey_RecordCount", ProtoInt, msg) # type: ignore
    
    def XytvdWellSurvey_GetXs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XytvdWellSurvey_GetXs", ProtoDoubles, msg) # type: ignore
    
    def XytvdWellSurvey_GetYs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XytvdWellSurvey_GetYs", ProtoDoubles, msg) # type: ignore
    
    def XytvdWellSurvey_GetTvds(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XytvdWellSurvey_GetTvds", ProtoDoubles, msg) # type: ignore
    
    def XytvdWellSurvey_GetZs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XytvdWellSurvey_GetZs", ProtoDoubles, msg) # type: ignore
    
    def XytvdWellSurvey_GetMds(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XytvdWellSurvey_GetMds", ProtoDoubles, msg) # type: ignore
    
    def XytvdWellSurvey_GetIncls(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XytvdWellSurvey_GetIncls", ProtoDoubles, msg) # type: ignore
    
    def XytvdWellSurvey_GetAzims(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.XytvdWellSurvey_GetAzims", ProtoDoubles, msg) # type: ignore
    
    def XytvdWellSurvey_SetRecords(self, iterable_requests) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.XytvdWellSurvey_SetRecords", ProtoBool, iterable_requests) # type: ignore
    
    def XytvdWellSurvey_SetSurveyAsDefinitive(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.XytvdWellSurvey_SetSurveyAsDefinitive", ProtoBool, msg) # type: ignore
    
    def XytvdWellSurvey_TieInMd(self, msg) -> ProtoDouble:
        return self._unary_wrapper("cegal.pythontool.XytvdWellSurvey_TieInMd", ProtoDouble, msg) # type: ignore
    
    def XytvdWellSurvey_SetTieInMd(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.XytvdWellSurvey_SetTieInMd", ProtoBool, msg) # type: ignore
    
    def XytvdWellSurvey_IsSidetrack(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.XytvdWellSurvey_IsSidetrack", ProtoBool, msg) # type: ignore

    def XytvdWellSurvey_IsDefinitive(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.XytvdWellSurvey_IsDefinitive", ProtoBool, msg) # type: ignore

    def XytvdWellSurvey_GetParentPythonBoreholeObject(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.XytvdWellSurvey_GetParentPythonBoreholeObject", PetrelObjectGuid, msg) # type: ignore

    def XytvdWellSurvey_IsAlgorithmMinimumCurvature(self, msg) -> ProtoBool: 
        return self._unary_wrapper("cegal.pythontool.XytvdWellSurvey_IsAlgorithmMinimumCurvature", ProtoBool, msg) # type: ignore

    def XytvdWellSurvey_SetAlgorithmToMinimumCurvature(self, msg) -> ProtoBool: 
        return self._unary_wrapper("cegal.pythontool.XytvdWellSurvey_SetAlgorithmToMinimumCurvature", ProtoBool, msg) # type: ignore

    def XytvdWellSurvey_IsCalculationValid(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.XytvdWellSurvey_IsCalculationValid", ProtoBool, msg) # type: ignore

class DxdytvdWellSurveyHub(BaseHub):
    def GetDxdytvdWellSurveyGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetDxdytvdWellSurveyGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetDxdytvdWellSurvey(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetDxdytvdWellSurvey", PetrelObjectRef, msg) # type: ignore
    
    def DxdytvdWellSurvey_RecordCount(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.DxdytvdWellSurvey_RecordCount", ProtoInt, msg) # type: ignore
    
    def DxdytvdWellSurvey_AzimuthReferenceIsGridNorth(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.DxdytvdWellSurvey_AzimuthReferenceIsGridNorth", ProtoBool, msg) # type: ignore
    
    def DxdytvdWellSurvey_SetAzimuthReference(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.DxdytvdWellSurvey_SetAzimuthReference", ProtoBool, msg)

    def DxdytvdWellSurvey_GetDxs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.DxdytvdWellSurvey_GetDxs", ProtoDoubles, msg) # type: ignore
    
    def DxdytvdWellSurvey_GetDys(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.DxdytvdWellSurvey_GetDys", ProtoDoubles, msg) # type: ignore
    
    def DxdytvdWellSurvey_GetTvds(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.DxdytvdWellSurvey_GetTvds", ProtoDoubles, msg) # type: ignore
    
    def DxdytvdWellSurvey_GetXs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.DxdytvdWellSurvey_GetXs", ProtoDoubles, msg) # type: ignore
    
    def DxdytvdWellSurvey_GetYs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.DxdytvdWellSurvey_GetYs", ProtoDoubles, msg) # type: ignore
    
    def DxdytvdWellSurvey_GetZs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.DxdytvdWellSurvey_GetZs", ProtoDoubles, msg) # type: ignore
    
    def DxdytvdWellSurvey_GetMds(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.DxdytvdWellSurvey_GetMds", ProtoDoubles, msg) # type: ignore
    
    def DxdytvdWellSurvey_GetIncls(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.DxdytvdWellSurvey_GetIncls", ProtoDoubles, msg) # type: ignore
    
    def DxdytvdWellSurvey_GetAzims(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.DxdytvdWellSurvey_GetAzims", ProtoDoubles, msg) # type: ignore
    
    def DxdytvdWellSurvey_SetRecords(self, iterable_requests) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.DxdytvdWellSurvey_SetRecords", ProtoBool, iterable_requests) # type: ignore
    
    def DxdytvdWellSurvey_SetSurveyAsDefinitive(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.DxdytvdWellSurvey_SetSurveyAsDefinitive", ProtoBool, msg) # type: ignore
    
    def DxdytvdWellSurvey_TieInMd(self, msg) -> ProtoDouble:
        return self._unary_wrapper("cegal.pythontool.DxdytvdWellSurvey_TieInMd", ProtoDouble, msg) # type: ignore
    
    def DxdytvdWellSurvey_SetTieInMd(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.DxdytvdWellSurvey_SetTieInMd", ProtoBool, msg) # type: ignore
    
    def DxdytvdWellSurvey_IsSidetrack(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.DxdytvdWellSurvey_IsSidetrack", ProtoBool, msg) # type: ignore

    def DxdytvdWellSurvey_IsDefinitive(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.DxdytvdWellSurvey_IsDefinitive", ProtoBool, msg) # type: ignore

    def DxdytvdWellSurvey_GetParentPythonBoreholeObject(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.DxdytvdWellSurvey_GetParentPythonBoreholeObject", PetrelObjectGuid, msg) # type: ignore

    def DxdytvdWellSurvey_IsAlgorithmMinimumCurvature(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.DxdytvdWellSurvey_IsAlgorithmMinimumCurvature", ProtoBool, msg) # type: ignore

    def DxdytvdWellSurvey_SetAlgorithmToMinimumCurvature(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.DxdytvdWellSurvey_SetAlgorithmToMinimumCurvature", ProtoBool, msg) # type: ignore

    def DxdytvdWellSurvey_IsCalculationValid(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.DxdytvdWellSurvey_IsCalculationValid", ProtoBool, msg) # type: ignore

class MdinclazimWellSurveyHub(BaseHub):
    def GetMdinclazimWellSurveyGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetMdinclazimWellSurveyGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetMdinclazimWellSurvey(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetMdinclazimWellSurvey", PetrelObjectRef, msg) # type: ignore
    
    def MdinclazimWellSurvey_RecordCount(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.MdinclazimWellSurvey_RecordCount", ProtoInt, msg) # type: ignore
    
    def MdinclazimWellSurvey_AzimuthReferenceIsGridNorth(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MdinclazimWellSurvey_AzimuthReferenceIsGridNorth", ProtoBool, msg) # type: ignore
    
    def MdinclazimWellSurvey_GetMds(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.MdinclazimWellSurvey_GetMds", ProtoDoubles, msg) # type: ignore
    
    def MdinclazimWellSurvey_GetIncls(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.MdinclazimWellSurvey_GetIncls", ProtoDoubles, msg) # type: ignore
    
    def MdinclazimWellSurvey_GetAzims(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.MdinclazimWellSurvey_GetAzims", ProtoDoubles, msg) # type: ignore
    
    def MdinclazimWellSurvey_GetXs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.MdinclazimWellSurvey_GetXs", ProtoDoubles, msg) # type: ignore
    
    def MdinclazimWellSurvey_GetYs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.MdinclazimWellSurvey_GetYs", ProtoDoubles, msg) # type: ignore
    
    def MdinclazimWellSurvey_GetZs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.MdinclazimWellSurvey_GetZs", ProtoDoubles, msg) # type: ignore
    
    def MdinclazimWellSurvey_IsAzimuthReferenceGridNorth(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MdinclazimWellSurvey_IsAzimuthReferenceGridNorth", ProtoBool, msg) # type: ignore
    
    def MdinclazimWellSurvey_SetAzimuthReference(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MdinclazimWellSurvey_SetAzimuthReference", ProtoBool, msg)
    
    def MdinclazimWellSurvey_SetRecords(self, iterable_requests) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.MdinclazimWellSurvey_SetRecords", ProtoBool, iterable_requests) # type: ignore
    
    def MdinclazimWellSurvey_SetSurveyAsDefinitive(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MdinclazimWellSurvey_SetSurveyAsDefinitive", ProtoBool, msg) # type: ignore
    
    def MdinclazimWellSurvey_TieInMd(self, msg) -> ProtoDouble:
        return self._unary_wrapper("cegal.pythontool.MdinclazimWellSurvey_TieInMd", ProtoDouble, msg) # type: ignore
    
    def MdinclazimWellSurvey_SetTieInMd(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MdinclazimWellSurvey_SetTieInMd", ProtoBool, msg) # type: ignore
    
    def MdinclazimWellSurvey_IsSidetrack(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MdinclazimWellSurvey_IsSidetrack", ProtoBool, msg) # type: ignore

    def MdinclazimWellSurvey_IsDefinitive(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MdinclazimWellSurvey_IsDefinitive", ProtoBool, msg) # type: ignore

    def MdinclazimWellSurvey_GetParentPythonBoreholeObject(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.MdinclazimWellSurvey_GetParentPythonBoreholeObject", PetrelObjectGuid, msg) # type: ignore

    def MdinclazimWellSurvey_IsCalculationValid(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MdinclazimWellSurvey_IsCalculationValid", ProtoBool, msg) # type: ignore

class ExplicitWellSurveyHub(BaseHub):
    def GetExplicitWellSurveyGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetExplicitWellSurveyGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetExplicitWellSurvey(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetExplicitWellSurvey", PetrelObjectRef, msg) # type: ignore
    
    def ExplicitWellSurvey_RecordCount(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.ExplicitWellSurvey_RecordCount", ProtoInt, msg) # type: ignore
    
    def ExplicitWellSurvey_GetXs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.ExplicitWellSurvey_GetXs", ProtoDoubles, msg) # type: ignore
    
    def ExplicitWellSurvey_GetYs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.ExplicitWellSurvey_GetYs", ProtoDoubles, msg) # type: ignore
    
    def ExplicitWellSurvey_GetZs(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.ExplicitWellSurvey_GetZs", ProtoDoubles, msg) # type: ignore
    
    def ExplicitWellSurvey_GetMds(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.ExplicitWellSurvey_GetMds", ProtoDoubles, msg) # type: ignore
    
    def ExplicitWellSurvey_GetIncls(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.ExplicitWellSurvey_GetIncls", ProtoDoubles, msg) # type: ignore
    
    def ExplicitWellSurvey_GetAzims(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.ExplicitWellSurvey_GetAzims", ProtoDoubles, msg) # type: ignore
    
    def ExplicitWellSurvey_SetSurveyAsDefinitive(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.ExplicitWellSurvey_SetSurveyAsDefinitive", ProtoBool, msg) # type: ignore
    
    def ExplicitWellSurvey_TieInMd(self, msg) -> ProtoDouble:
        return self._unary_wrapper("cegal.pythontool.ExplicitWellSurvey_TieInMd", ProtoDouble, msg) # type: ignore
    
    def ExplicitWellSurvey_SetTieInMd(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.ExplicitWellSurvey_SetTieInMd", ProtoBool, msg) # type: ignore
    
    def ExplicitWellSurvey_IsSidetrack(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.ExplicitWellSurvey_IsSidetrack", ProtoBool, msg) # type: ignore

    def ExplicitWellSurvey_IsDefinitive(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.ExplicitWellSurvey_IsDefinitive", ProtoBool, msg) # type: ignore

    def ExplicitWellSurvey_GetParentPythonBoreholeObject(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.ExplicitWellSurvey_GetParentPythonBoreholeObject", PetrelObjectGuid, msg)  # type: ignore
    
    def ExplicitWellSurvey_IsCalculationValid(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.ExplicitWellSurvey_IsCalculationValid", ProtoBool, msg) # type: ignore