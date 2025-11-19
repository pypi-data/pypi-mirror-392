# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef
from .base_hub import BaseHub
import typing

class GlobalWellLogFolderHub(BaseHub):
    def CreateGlobalWellLog(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GlobalWellLogFolder_CreateGlobalWellLog", PetrelObjectRef, msg)

    def CreateGlobalWellLogFolder(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GlobalWellLogFolder_CreateGlobalWellLogFolder", PetrelObjectRef, msg)

    def GetLogs(self, msg) -> typing.Iterable[PetrelObjectRef]:
        return self._server_streaming_wrapper("cegal.pythontool.GlobalWellLogFolder_GetLogs", PetrelObjectRef, msg)