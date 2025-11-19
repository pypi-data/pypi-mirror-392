# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PropertyRangeData, ProtoBool, ProtoString, ProtoStrings
from cegalprizm.pythontool.oophub.base_hub import BaseHub
import typing


class WellAttributeHub(BaseHub):
    def CreateWellAttribute(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.CreateWellAttribute", ProtoBool, msg)

    def CreateWellAttributeIfMissing(self, msg) -> ProtoStrings:
        return self._client_streaming_wrapper("cegal.pythontool.CreateWellAttributeIfMissing", ProtoStrings, msg)

    def WellAttribute_GetAttributeIsWritable(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.WellAttribute_GetAttributeIsWritable", ProtoBool, msg)

    def WellAttribute_GetAttributeIsSupported(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.WellAttribute_GetAttributeIsSupported", ProtoBool, msg)

    def WellAttribute_GetAttributeUniqueName(self, msg) -> ProtoString:
        return self._unary_wrapper("cegal.pythontool.WellAttribute_GetAttributeUniqueName", ProtoString, msg)

    def WellAttribute_GetAttribute(self, msg) -> PropertyRangeData:
        return self._unary_wrapper("cegal.pythontool.WellAttribute_GetAttribute", PropertyRangeData, msg)
    
    def WellAttribute_SetAttributeValue(self, msg) -> ProtoBool:
        return self._unary_wrapper("cegal.pythontool.WellAttribute_SetAttributeValue", ProtoBool, msg)

    def GetProjectWellAttributes(self, msg) -> typing.Iterable[PropertyRangeData]:
        return self._server_streaming_wrapper("cegal.pythontool.GetProjectWellAttributes", PropertyRangeData, msg)