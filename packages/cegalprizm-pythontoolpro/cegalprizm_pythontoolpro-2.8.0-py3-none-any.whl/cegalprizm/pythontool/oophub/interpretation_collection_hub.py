# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .base_hub import BaseHub
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef

class InterpretationCollectionHub(BaseHub):
    def InterpretationCollection_CreateFolder(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.InterpretationCollection_CreateFolder", PetrelObjectRef, msg)