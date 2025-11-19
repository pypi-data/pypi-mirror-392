# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuids
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import Workflow_RunSingle_Response
from .base_hub import BaseHub
import typing

class ReferenceVariableHub(BaseHub):
    def GetReferenceVariableGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetReferenceVariableGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetReferenceVariable(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetReferenceVariable", PetrelObjectRef, msg) # type: ignore

class WorkflowHub(BaseHub):
    def GetWorkflowGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetWorkflowGrpc", PetrelObjectRef, msg) # type: ignore
    
    def GetWorkflow(self, msg) -> "PetrelObjectRef":
        return self._unary_wrapper("cegal.pythontool.GetWorkflow", PetrelObjectRef, msg) # type: ignore
    
    def Workflow_GetWorkflowInputReferences(self, msg) -> typing.Iterable[PetrelObjectGuids]:
        return self._server_streaming_wrapper("cegal.pythontool.Workflow_GetWorkflowInputReferences", PetrelObjectGuids, msg) # type: ignore
    
    def Workflow_GetWorkflowOutputReferences(self, msg) -> typing.Iterable[PetrelObjectGuids]:
        return self._server_streaming_wrapper("cegal.pythontool.Workflow_GetWorkflowOutputReferences", PetrelObjectGuids, msg) # type: ignore
    
    def Workflow_RunSingle(self, msg) -> Workflow_RunSingle_Response:
        return self._unary_wrapper("cegal.pythontool.Workflow_RunSingle", Workflow_RunSingle_Response, msg) # type: ignore
    