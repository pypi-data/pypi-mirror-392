# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc import petrelinterface_pb2
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from .petrelobject_grpc import PetrelObjectGrpc
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.markercollection_hub import MarkerCollectionHub

class MarkerAttributeGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection", unique_name: str = ""):
        super(MarkerAttributeGrpc, self).__init__(WellKnownObjectDescription.MarkerAttribute, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("MarkerCollectionHub", petrel_connection._service_markercollection)
        self._unique_name = self.GetUniqueName() if unique_name == "" else unique_name

    def GetAttributeParent(self):
        from cegalprizm.pythontool.markercollection import MarkerCollection
        from cegalprizm.pythontool.grpc.markercollection_grpc import MarkerCollectionGrpc
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.MarkerCollection_GetAttributeParent(request)
        grpc = MarkerCollectionGrpc(response.guid, self._plink)
        mc = MarkerCollection(grpc)
        return mc
    
    def GetUniqueName(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        response = self._channel.MarkerCollection_GetAttributeUniqueName(request)
        return response.value