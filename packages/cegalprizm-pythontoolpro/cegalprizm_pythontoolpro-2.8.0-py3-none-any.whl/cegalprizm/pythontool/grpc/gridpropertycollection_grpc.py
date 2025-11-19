# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import typing

from . import petrelobject_grpc
from . import gridproperty_grpc

from cegalprizm.pythontool.grpc import grid_grpc, petrelinterface_pb2
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from cegalprizm.pythontool.grpc import utils as grpc_utils
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.gridpropertycollection_hub import GridPropertyCollectionHub

class PropertyFolderGrpc(petrelobject_grpc.PetrelObjectGrpc):

    def __init__(self, guid, petrel_connection: "PetrelConnection"):
        super(PropertyFolderGrpc, self).__init__(WellKnownObjectDescription.PropertyFolder.value, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("GridPropertyCollectionHub", petrel_connection._service_grid_property_collection)

    def GetPropertyObjects(self, recursive: bool = False):
        return self._get_property_objects(False, recursive)
    
    def GetDictionaryPropertyObjects(self, recursive: bool = False):
        return self._get_property_objects(True, recursive)

    def _get_property_objects(self, discrete, recursive=False):
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        request = petrelinterface_pb2.Properties_Request(
            guid = po_guid,
            discrete = discrete,
            recursive = recursive
        )
        reply_properties = self._channel.PropertyCollection_GetPropertyObjects(request)
        property_guids = [guid.guid for guid in reply_properties.guids]
        
        properties = []
        for guid in property_guids:
            if discrete:
                properties.append(gridproperty_grpc.GridDiscretePropertyGrpc(guid, self._plink))
            else:
                properties.append(gridproperty_grpc.GridPropertyGrpc(guid, self._plink))

        return properties

    def GetPropertyCollections(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.PropertyCollection_GetPropertyCollections(request)
        return [PropertyFolderGrpc(item.guid, self._plink) for item in responses]

    def GetParentPropertyCollection(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        parent_guid = self._channel.PropertyCollection_GetParentPropertyCollection(request).value
        if not parent_guid:
            return None
        return PropertyFolderGrpc(parent_guid, self._plink)

    def CreatePropertyFolder(self, name: str):
        from cegalprizm.pythontool.gridpropertycollection import PropertyFolder
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuidAndString(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            value = name
        )
        response = self._channel.PropertyCollection_CreatePropertyCollection(request)
        grpc = PropertyFolderGrpc(response.guid, self._plink)
        return PropertyFolder(grpc)

    def CreateProperty(self, name, template, discrete):
        self._plink._opened_test()
        template_guid = petrelinterface_pb2.PetrelObjectGuid(guid = template._petrel_object_link._guid) if template else petrelinterface_pb2.PetrelObjectGuid()
        request = petrelinterface_pb2.CreateObjectWithTemplate_Request(
            ParentGuid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            TemplateGuid = template_guid,
            Name = name,
            Discrete = discrete
        )
        response = self._channel.PropertyCollection_CreateProperty(request)
        return grpc_utils.pb_PetrelObjectRef_to_grpcobj(response, self._plink) if response.guid else None

    def GetNumberOfProperties(self, recursive: bool) -> int:
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        request = petrelinterface_pb2.Properties_Request(guid = po_guid, recursive = recursive)
        response = self._channel.PropertyCollection_GetNumberOfProperties(request)
        return response.value
    
    def GetParentGrid(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        parent_grid_guid = self._channel.PropertyCollection_GetParentGrid(request).value
        if not parent_grid_guid:
            return None
        return grid_grpc.GridGrpc(parent_grid_guid, self._plink)

class PropertyCollectionGrpc(petrelobject_grpc.PetrelObjectGrpc):

    def __init__(self, guid, petrel_connection):
        super(PropertyCollectionGrpc, self).__init__(WellKnownObjectDescription.PropertyCollection.value, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("GridPropertyCollectionHub", petrel_connection._service_grid_property_collection)

    def GetPropertyObjects(self):
        return self._get_property_objects(False)
    
    def GetDictionaryPropertyObjects(self):
        return self._get_property_objects(True)

    def _get_property_objects(self, discrete):
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        request = petrelinterface_pb2.Properties_Request(
            guid = po_guid,
            discrete = discrete
        )
        reply_properties = self._channel.PropertyCollection_GetPropertyObjects(request)
        property_guids = [guid.guid for guid in reply_properties.guids]
        
        properties = []
        for guid in property_guids:
            if discrete:
                properties.append(gridproperty_grpc.GridDiscretePropertyGrpc(guid, self._plink))
            else:
                properties.append(gridproperty_grpc.GridPropertyGrpc(guid, self._plink))
            
        return properties