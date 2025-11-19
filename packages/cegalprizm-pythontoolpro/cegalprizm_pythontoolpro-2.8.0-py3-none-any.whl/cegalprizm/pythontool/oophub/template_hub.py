# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, ProtoString, IntStringTuples, Primitives
from .base_hub import BaseHub

class TemplateHub(BaseHub):
    def GetTemplate(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetTemplate", PetrelObjectRef, msg) # type: ignore
    
    def Template_DisplayUnitSymbol(self, msg) -> ProtoString:
        return self._wrapper("cegal.pythontool.Template_DisplayUnitSymbol", ProtoString, msg) # type: ignore
    
    def Template_Units(self, msg) -> Primitives.StringArray:
        return self._wrapper("cegal.pythontool.Template_Units", Primitives.StringArray, msg) # type: ignore

class DiscreteTemplateHub(BaseHub):
    def GetTemplate(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetDiscreteTemplate", PetrelObjectRef, msg) # type: ignore
    
    def DiscreteTemplate_GetAllDictionaryCodes(self, msg) -> IntStringTuples:
        return self._wrapper("cegal.pythontool.DiscreteTemplate_GetAllDictionaryCodes", IntStringTuples, msg) # type: ignore