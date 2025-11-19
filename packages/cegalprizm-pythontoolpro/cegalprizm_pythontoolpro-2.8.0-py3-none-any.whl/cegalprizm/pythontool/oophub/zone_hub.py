# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuid, PetrelObjectGuids
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import ProtoInt
from .base_hub import BaseHub


class ZoneHub(BaseHub):
    def GetZone(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetZone", PetrelObjectRef, msg) # type: ignore

    def Zone_GetParentGrid(self, msg) -> PetrelObjectGuid:
        return self._wrapper("cegal.pythontool.Zone_GetParentGrid", PetrelObjectGuid, msg) # type: ignore

    def Zone_GetBaseK(self, msg) -> ProtoInt:
        return self._wrapper("cegal.pythontool.Zone_GetBaseK", ProtoInt, msg) # type: ignore

    def Zone_GetTopK(self, msg) -> ProtoInt:
        return self._wrapper("cegal.pythontool.Zone_GetTopK", ProtoInt, msg) # type: ignore

    def Zone_GetNumberOfZones(self, msg) -> ProtoInt:
        return self._wrapper("cegal.pythontool.Zone_GetNumberOfZones", ProtoInt, msg) # type: ignore

    def Zone_GetZones(self, msg) -> PetrelObjectGuids:
        return self._wrapper("cegal.pythontool.Zone_GetZones", PetrelObjectGuids, msg) # type: ignore

    def Zone_GetParentZone(self, msg) -> PetrelObjectGuid:
        return self._wrapper("cegal.pythontool.Zone_GetParentZone", PetrelObjectGuid, msg) # type: ignore