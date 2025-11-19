# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, ProtoBool, PetrelObjectGuid
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import FaultInterpretation_GetAllFaultSticks_Response
from .base_hub import BaseHub
import typing

class FaultInterpretationHub(BaseHub):
    def GetFaultInterpretation(self, msg) -> PetrelObjectRef: # type: ignore
        return self._wrapper("cegal.pythontool.GetFaultInterpretation", PetrelObjectRef, msg)

    def CreateFaultInterpretation(self, msg) -> PetrelObjectGuid: # type: ignore
        return self._wrapper("cegal.pythontool.CreateFaultInterpretation", PetrelObjectGuid, msg)

    def FaultInterpretation_GetFaultSticksDataframe(self, msg) -> typing.Iterable[FaultInterpretation_GetAllFaultSticks_Response]: # type: ignore
        return self._server_streaming_wrapper("cegal.pythontool.FaultInterpretation_GetAllFaultSticks", FaultInterpretation_GetAllFaultSticks_Response, msg)
    
    def FaultInterpretation_ClearAllPolylines(self, msg) -> ProtoBool: # type: ignore
        return self._wrapper("cegal.pythontool.FaultInterpretation_ClearAllPolylines", ProtoBool, msg)
    
    def FaultInterpretation_SetPolylines(self, iterable_requests) -> ProtoBool: # type: ignore
        return self._client_streaming_wrapper("cegal.pythontool.FaultInterpretation_SetPolylines", ProtoBool, iterable_requests)