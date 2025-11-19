# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import ProtoString, PetrelObjectGuid, PetrelObjectGuids, ProtoInt, PetrelObjectRef
from .base_hub import BaseHub

class GridPropertyCollectionHub(BaseHub):
    def PropertyCollection_GetPropertyObjects(self, msg) -> PetrelObjectGuids: # type: ignore
        return self._unary_wrapper("cegal.pythontool.PropertyCollection_GetPropertyObjects", PetrelObjectGuids, msg)

    def PropertyCollection_GetPropertyCollections(self, msg) -> PetrelObjectGuid: # type: ignore
        return self._server_streaming_wrapper("cegal.pythontool.PropertyCollection_GetPropertyCollections", PetrelObjectGuid, msg)

    def PropertyCollection_GetParentPropertyCollection(self, msg) -> ProtoString: # type: ignore
        return self._unary_wrapper("cegal.pythontool.PropertyCollection_GetParentPropertyCollection", ProtoString, msg)

    def PropertyCollection_CreatePropertyCollection(self, msg) -> PetrelObjectGuid: # type: ignore
        return self._unary_wrapper("cegal.pythontool.PropertyCollection_CreatePropertyCollection", PetrelObjectGuid, msg)

    def PropertyCollection_GetNumberOfProperties(self, msg) -> ProtoInt: # type: ignore
        return self._unary_wrapper("cegal.pythontool.PropertyCollection_GetNumberOfProperties", ProtoInt, msg)

    def PropertyCollection_GetParentGrid(self, msg) -> ProtoString: # type: ignore
        return self._unary_wrapper("cegal.pythontool.PropertyCollection_GetParentGrid", ProtoString, msg)

    def PropertyCollection_CreateProperty(self, msg) -> PetrelObjectRef: # type: ignore
        return self._unary_wrapper("cegal.pythontool.PropertyCollection_CreateProperty", PetrelObjectRef, msg)