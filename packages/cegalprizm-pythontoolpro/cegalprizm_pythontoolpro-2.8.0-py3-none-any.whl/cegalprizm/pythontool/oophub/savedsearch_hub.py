# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuid, ProtoBool
from .base_hub import BaseHub
import typing

class SavedSearchHub(BaseHub):
    def GetSavedSearch(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetSavedSearch", PetrelObjectRef, msg)

    def SavedSearch_GetWells(self, msg) -> typing.Iterable[PetrelObjectGuid]:
        return self._server_streaming_wrapper("cegal.pythontool.SavedSearch_GetWells", PetrelObjectGuid, msg)

    def SavedSearch_IsDynamic(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.SavedSearch_IsDynamic", ProtoBool, msg)
