# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .base_hub import BaseHub
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef
import typing

class FolderHub(BaseHub):
    def Folder_CreateFolder(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.Folder_CreateFolder", PetrelObjectRef, msg)

    def Folder_GetObjects(self, msg) -> typing.Iterable[PetrelObjectRef]:
        return self._server_streaming_wrapper("cegal.pythontool.Folder_GetObjects", PetrelObjectRef, msg)