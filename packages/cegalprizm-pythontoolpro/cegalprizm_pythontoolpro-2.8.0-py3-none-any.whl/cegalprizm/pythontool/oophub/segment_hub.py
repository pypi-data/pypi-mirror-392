# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuid, Indices2Array, ProtoBool
from .base_hub import BaseHub


class SegmentHub(BaseHub):
    def GetSegment(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetSegment", PetrelObjectRef, msg) # type: ignore

    def Segment_GetParentGrid(self, msg) -> PetrelObjectGuid:
        return self._wrapper("cegal.pythontool.Segment_GetParentGrid", PetrelObjectGuid, msg) # type: ignore

    def Segment_GetCells(self, msg) -> Indices2Array:
        return self._wrapper("cegal.pythontool.Segment_GetCells", Indices2Array, msg) # type: ignore
    
    def Segment_IsCellInside(self, msg) -> ProtoBool:
        return self._wrapper("cegal.pythontool.Segment_IsCellInside", ProtoBool, msg) # type: ignore