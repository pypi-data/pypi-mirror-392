# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuid
from .base_hub import BaseHub
import typing

class BoreholeCollectionHub(BaseHub):
    def GetBoreholeCollectionGrpc(self, msg) -> PetrelObjectRef: # type: ignore
        return self._wrapper("cegal.pythontool.GetBoreholeCollectionGrpc", PetrelObjectRef, msg)
    
    def BoreholeCollection_GetWells(self, msg) -> typing.Iterable[PetrelObjectGuid]:
        return self._server_streaming_wrapper("cegal.pythontool.BoreholeCollection_GetWells", PetrelObjectGuid, msg) # type: ignore
    
    def BoreholeCollection_GetBoreholeCollections(self, msg) -> typing.Iterable[PetrelObjectGuid]:
        return self._server_streaming_wrapper("cegal.pythontool.BoreholeCollection_GetBoreholeCollections", PetrelObjectGuid, msg)

    def BoreholeCollection_CreateBoreholeCollection(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.BoreholeCollection_CreateBoreholeCollection", PetrelObjectRef, msg)