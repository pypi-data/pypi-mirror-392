# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectRefs, ProtoBool, ProtoString, PropertyRangeData, PetrelObjectGuid, StratigraphyInfo
from .base_hub import BaseHub
import typing
class MarkerCollectionHub(BaseHub):
    def GetMarkerCollection(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.GetMarkerCollection", PetrelObjectRef, msg) # type: ignore

    def MarkerCollection_GetName(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_GetName", ProtoString, msg) # type: ignore

    def MarkerCollection_SetName(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_SetName", ProtoBool, msg) # type: ignore

    def MarkerCollection_GetValues(self, msg) -> typing.Iterable[PropertyRangeData]:
        return self._server_streaming_wrapper("cegal.pythontool.MarkerCollection_GetValues", PropertyRangeData, msg) # type: ignore

    def MarkerCollection_SetPropertyValues(self, iterable_requests) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.MarkerCollection_SetPropertyValues", ProtoBool, iterable_requests) # type: ignore

    def MarkerCollection_GetAttributes(self, msg) -> PetrelObjectRef:
        return self._server_streaming_wrapper("cegal.pythontool.MarkerCollection_GetAttributes", PetrelObjectRef, msg) # type: ignore

    def MarkerCollection_AddAttribute(self, msg) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.MarkerCollection_AddAttribute", ProtoBool, msg) # type: ignore

    def MarkerCollection_AddEmptyAttribute(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_AddEmptyAttribute", ProtoBool, msg) # type: ignore

    def MarkerCollection_GetStratigraphies(self, msg) -> PetrelObjectRef:
        return self._server_streaming_wrapper("cegal.pythontool.MarkerCollection_GetStratigraphies", PetrelObjectRef, msg) # type: ignore

    def MarkerCollection_AddMarker(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_AddMarker", ProtoBool, msg) # type: ignore

    def MarkerCollection_AddManyMarkers(self, msg) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.MarkerCollection_AddManyMarkers", ProtoBool, msg)
    
    def MarkerCollection_GetMarkerDroid(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_GetMarkerDroid", ProtoString, msg)
    
    def MarkerCollection_DeleteMarker(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_DeleteMarker", ProtoBool, msg)
    
    def MarkerCollection_DeleteManyMarkers(self, msg) -> ProtoBool:
        return self._client_streaming_wrapper("cegal.pythontool.MarkerCollection_DeleteManyMarkers", ProtoBool, msg)
    
    def MarkerCollection_GetAttributeParent(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_GetAttributeParent", PetrelObjectGuid, msg)
    
    def MarkerCollection_GetAttributeUniqueName(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_GetAttributeUniqueName", ProtoString, msg)

    def MarkerCollection_GetStratigraphyUniqueName(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_GetStratigraphyUniqueName", ProtoString, msg)

    def MarkerCollection_GetStratigraphyParent(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_GetStratigraphyParent", PetrelObjectGuid, msg)

    def MarkerCollection_GetStratigraphyZones(self, msg) -> PetrelObjectRef:
        return self._server_streaming_wrapper("cegal.pythontool.MarkerCollection_GetStratigraphyZones", PetrelObjectRef, msg)

    def MarkerCollection_GetStratigraphyZoneUniqueName(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_GetStratigraphyZoneUniqueName", ProtoString, msg)

    def MarkerCollection_GetStratigraphyZoneParent(self, msg) -> PetrelObjectGuid:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_GetStratigraphyZoneParent", PetrelObjectGuid, msg)

    def MarkerCollection_MarkerStratigraphy_GetHorizonType(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_MarkerStratigraphy_GetHorizonType", ProtoString, msg)

    def MarkerCollection_MarkerStratigraphy_SetHorizonType(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_MarkerStratigraphy_SetHorizonType", ProtoBool, msg)

    def MarkerCollection_CreateZoneAndHorizonAboveOrBelow(self, msg) -> PetrelObjectRefs:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_CreateZoneAndHorizonAboveOrBelow", PetrelObjectRefs, msg)

    def MarkerCollection_CreateZonesAndHorizonInside(self, msg) -> PetrelObjectRefs:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_CreateZonesAndHorizonInside", PetrelObjectRefs, msg)

    def MarkerCollection_CreateFirstHorizon(self, msg) -> PetrelObjectRefs:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_CreateFirstHorizon", PetrelObjectRefs, msg)

    def MarkerCollection_GetStratigraphyZoneParentZone(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_GetStratigraphyZoneParentZone", PetrelObjectRef, msg)

    def MarkerCollection_GetStratigraphyZoneChildren(self, msg) -> PetrelObjectRef:
        return self._server_streaming_wrapper("cegal.pythontool.MarkerCollection_GetStratigraphyZoneChildren", PetrelObjectRef, msg)

    def MarkerCollection_GetStratigraphyHorizonParentZone(self, msg) -> PetrelObjectRef:
        return self._unary_wrapper("cegal.pythontool.MarkerCollection_GetStratigraphyHorizonParentZone", PetrelObjectRef, msg)

    def MarkerCollection_GetHorizonsAndZonesInOrder(self, msg) -> StratigraphyInfo:
        return self._server_streaming_wrapper("cegal.pythontool.MarkerCollection_GetHorizonsAndZonesInOrder", StratigraphyInfo, msg)