# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from cegalprizm.pythontool.grpc import petrelinterface_pb2
from cegalprizm.pythontool.ooponly.ip_oop_transition import Tuple2
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.template_hub import TemplateHub, DiscreteTemplateHub

class TemplateGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection", sub_type: str = WellKnownObjectDescription.Template):
        super(TemplateGrpc, self).__init__(sub_type, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast('TemplateHub', petrel_connection._service_template)

    def UnitSymbol(self) -> str:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._channel.Template_DisplayUnitSymbol(request)
        return response.value

    def Units(self) -> "list[str]":
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._channel.Template_Units(request)
        return response.values

class DiscreteTemplateGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection", sub_type: str = WellKnownObjectDescription.TemplateDiscrete):
        super(DiscreteTemplateGrpc, self).__init__(sub_type, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast('DiscreteTemplateHub', petrel_connection._service_discrete_template)

    def GetAllDictionaryCodes(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        values = self._channel.DiscreteTemplate_GetAllDictionaryCodes(request).values
        collection = []
        for pair in values:
            collection.append(Tuple2(Item1 = pair.item1, Item2 = pair.item2))
        return tuple(collection)