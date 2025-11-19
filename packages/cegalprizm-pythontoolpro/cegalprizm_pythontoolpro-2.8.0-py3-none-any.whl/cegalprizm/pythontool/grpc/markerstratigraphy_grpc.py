# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc import petrelinterface_pb2
from cegalprizm.pythontool.exceptions import PythonToolException
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from .petrelobject_grpc import PetrelObjectGrpc
from .stratigraphyzone_grpc import StratigraphyZoneGrpc
import typing
import warnings
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.markercollection_hub import MarkerCollectionHub

class MarkerStratigraphyGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection", stratigraphy_type: str, unique_name: str = ""):
        super(MarkerStratigraphyGrpc, self).__init__(stratigraphy_type, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("MarkerCollectionHub", petrel_connection._service_markercollection)
        self._unique_name = self.GetUniqueName() if unique_name == "" else unique_name
        self._is_horizon = True if stratigraphy_type == WellKnownObjectDescription.MarkerStratigraphyHorizon else False

    def GetUniqueName(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.MarkerCollection_GetStratigraphyUniqueName(request)
        return response.value

    def GetStratigraphyParent(self):
        from cegalprizm.pythontool.markercollection import MarkerCollection
        from cegalprizm.pythontool.grpc.markercollection_grpc import MarkerCollectionGrpc
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.MarkerCollection_GetStratigraphyParent(request)
        grpc = MarkerCollectionGrpc(response.guid, self._plink)
        mc = MarkerCollection(grpc)
        return mc

    def IsHorizon(self):
        return self._is_horizon

    def GetHorizonType(self) -> str:
        if not self.IsHorizon():
            warnings.warn("Unable to get horizon type for MarkerStratigraphy object with name {0}. Object is not a Horizon.".format(self._unique_name), UserWarning, 2)
            return ""
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.MarkerCollection_MarkerStratigraphy_GetHorizonType(request)
        return response.value

    def SetHorizonType(self, horizon_type: str) -> bool:
        if not self.IsHorizon():
            warnings.warn("Unable to set horizon type for MarkerStratigraphy object with name {0}. Object is not a Horizon.".format(self._unique_name), UserWarning, 2)
            return False
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuidAndString(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            value = horizon_type
        )
        response = self._channel.MarkerCollection_MarkerStratigraphy_SetHorizonType(request)
        if len(response.error.message) > 0:
            raise PythonToolException(response.error.message)
        return response.value

    def GetStratigraphyHorizonParentZone(self, parent_droid: str) -> "StratigraphyZoneGrpc":
        if not self.IsHorizon():
            warnings.warn("Unable to get parent zone for MarkerStratigraphy object with name {0}. Object is not a Horizon.".format(self._unique_name), UserWarning, 2)
            return None
        self._plink._opened_test()
        request0 = petrelinterface_pb2.PetrelObjectGuid(guid = parent_droid)
        request1 = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        request = petrelinterface_pb2.PetrelObjectGuids(
            guids = [request0, request1]
        )
        response = self._channel.MarkerCollection_GetStratigraphyHorizonParentZone(request)
        if response.guid:
            return StratigraphyZoneGrpc(response.guid, self._plink, response.petrel_name)
        else:
            return None