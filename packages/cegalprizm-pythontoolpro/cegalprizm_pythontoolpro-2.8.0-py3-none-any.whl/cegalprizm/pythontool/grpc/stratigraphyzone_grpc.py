# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc import petrelinterface_pb2
from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
import cegalprizm.pythontool.grpc.markerstratigraphy_grpc as markerstratigraphy_grpc
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.markercollection_hub import MarkerCollectionHub
    from cegalprizm.pythontool.grpc.markerstratigraphy_grpc import MarkerStratigraphyGrpc

class StratigraphyZoneGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection", unique_name: str = ""):
        super(StratigraphyZoneGrpc, self).__init__(WellKnownObjectDescription.MarkerStratigraphyZone, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("MarkerCollectionHub", petrel_connection._service_markercollection)
        self._unique_name = self.GetUniqueName() if unique_name == "" else unique_name

    def GetUniqueName(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.MarkerCollection_GetStratigraphyZoneUniqueName(request)
        return response.value

    def GetStratigraphyParent(self):
        from cegalprizm.pythontool.markercollection import MarkerCollection
        from cegalprizm.pythontool.grpc.markercollection_grpc import MarkerCollectionGrpc
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.MarkerCollection_GetStratigraphyZoneParent(request)
        grpc = MarkerCollectionGrpc(response.guid, self._plink)
        mc = MarkerCollection(grpc)
        return mc
    
    def GetStratigraphyZoneParentZone(self, parent_droid: str) -> "StratigraphyZoneGrpc":
        self._plink._opened_test()
        request0 = petrelinterface_pb2.PetrelObjectGuid(guid = parent_droid)
        request1 = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        request = petrelinterface_pb2.PetrelObjectGuids(
            guids = [request0, request1]
        )
        response = self._channel.MarkerCollection_GetStratigraphyZoneParentZone(request)
        if response.guid:
            return StratigraphyZoneGrpc(response.guid, self._plink, response.petrel_name)
        else:
            return None

    def GetStratigraphyZoneChildren(self, parent_droid: str) -> typing.Iterable[typing.Union["StratigraphyZoneGrpc", "MarkerStratigraphyGrpc"]]:
        self._plink._opened_test()
        request0 = petrelinterface_pb2.PetrelObjectGuid(guid = parent_droid)
        request1 = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        request = petrelinterface_pb2.PetrelObjectGuids(
            guids = [request0, request1]
        )
        response = self._channel.MarkerCollection_GetStratigraphyZoneChildren(request)
        refs = [r for r in response]
        grpcs = []
        for ref in refs:
            if ref.guid and ref.sub_type == WellKnownObjectDescription.MarkerStratigraphyZone:
                grpcs.append(StratigraphyZoneGrpc(ref.guid, self._plink, ref.petrel_name))
            elif ref.guid and ref.sub_type == WellKnownObjectDescription.MarkerStratigraphyHorizon:
                grpcs.append(markerstratigraphy_grpc.MarkerStratigraphyGrpc(ref.guid, self._plink, ref.sub_type, ref.petrel_name))
        return grpcs