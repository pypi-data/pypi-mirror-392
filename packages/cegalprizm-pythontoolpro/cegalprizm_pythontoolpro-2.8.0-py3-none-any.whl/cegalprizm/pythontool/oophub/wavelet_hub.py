# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, ProtoBool, ProtoDouble, ProtoDoubles, ProtoInt, ProtoString
from .base_hub import BaseHub
import typing

class WaveletHub(BaseHub):
    def GetWaveletGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetWaveletGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetWavelet(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetWavelet", PetrelObjectRef, msg) # type: ignore
    
    def Wavelet_Amplitudes(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.Wavelet_Amplitudes", ProtoDoubles, msg) # type: ignore
    
    def Wavelet_SampleCount(self, msg) -> ProtoInt:
        return self._unary_wrapper("cegal.pythontool.Wavelet_SampleCount", ProtoInt, msg) # type: ignore
    
    def Wavelet_SamplingInterval(self, msg) -> ProtoDouble:
        return self._unary_wrapper("cegal.pythontool.Wavelet_SamplingInterval", ProtoDouble, msg) # type: ignore
    
    def Wavelet_SamplingStart(self, msg) -> ProtoDouble:
        return self._unary_wrapper("cegal.pythontool.Wavelet_SamplingStart", ProtoDouble, msg) # type: ignore
    
    def Wavelet_SamplePoints(self, msg) -> typing.Iterable[ProtoDoubles]:
        return self._server_streaming_wrapper("cegal.pythontool.Wavelet_SamplePoints", ProtoDoubles, msg) # type: ignore
    
    def Wavelet_TimeUnitSymbol(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.Wavelet_TimeUnitSymbol", ProtoString, msg) # type: ignore
    
    def Wavelet_SetAmplitudes(self, iterable_requests) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.Wavelet_SetAmplitudes", ProtoBool, iterable_requests) # type: ignore
    
    def Wavelet_SetSamplingStart(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.Wavelet_SetSamplingStart", ProtoBool, msg) # type: ignore
    
    def Wavelet_SetSamplingInterval(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.Wavelet_SetSamplingInterval", ProtoBool, msg) # type: ignore
    