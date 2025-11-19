# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.ooponly.ptutils import Utils
from cegalprizm.pythontool.grpc import petrelinterface_pb2
from cegalprizm.pythontool.exceptions import PythonToolException
from cegalprizm.pythontool.template import Template, DiscreteTemplate

import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.petrelobject import PetrelObject
    from cegalprizm.pythontool.oophub.petrelobject_hub import PetrelObjectHub
    from cegalprizm.pythontool import GlobalWellLogFolder, Folder, PropertyCollection
class PetrelObjectGrpc:

    def __init__(self, sub_type: str, guid: str, petrel_connection: "PetrelConnection"):
        self._sub_type = sub_type
        self._guid = guid
        self._plink = petrel_connection
        self._invariant_content: typing.Dict[str, typing.Any] = {}
        self._base_channel = typing.cast("PetrelObjectHub", petrel_connection._service_petrel_object)
        self._domain_object: typing.Optional["PetrelObject"] = None
        
    @property
    def domain_object(self):
        return self._domain_object # Is set by constructor of associated PetrelObject

    @property
    def readonly(self):
        return self.domain_object.readonly

    def IsAlwaysReadonly(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        return self._base_channel.PetrelObject_IsAlwaysReadonly(request).value

    def write_test(self):
        if self.domain_object.readonly:
            raise PythonToolException(f"{self.domain_object.path} is readonly")
    
    def GetPetrelName(self) -> str:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        return self._base_channel.PetrelObject_GetPetrelName(request).value 

    def SetPetrelName(self, newName: str) -> bool:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuidAndString(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            value = newName
        )
        response = self._base_channel.PetrelObject_SetPetrelName(request)
        return response.value

    def GetParentFolder(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._base_channel.PetrelObject_GetParentFolder(request)
        return response
    
    def GetPath(self) -> str:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        return self._base_channel.PetrelObject_GetPath(request).value 
    
    def GetDroidString(self) -> str:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        return self._base_channel.PetrelObject_GetDroidString(request).value

    def RetrieveStats(self) -> typing.Dict[str, str]:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        reply = self._base_channel.PetrelObject_RetrieveStats(request)
        return Utils.protobuf_map_to_dict(reply.string_to_string_map, {})

    def GetOceanType(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        return self._base_channel.PetrelObject_GetOceanType(request).value  

    def ClonePetrelObject(self, path_of_clone, 
                                copy_values, 
                                template: typing.Union["Template", "DiscreteTemplate"] = None, 
                                destination: typing.Union["Folder", "GlobalWellLogFolder", "PropertyCollection"] = None,
                                realize_path: str = ""):
        name = path_of_clone.split('/')[-1]
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        template_guid = petrelinterface_pb2.PetrelObjectGuid() if (template is None) else petrelinterface_pb2.PetrelObjectGuid(guid = template._petrel_object_link._guid, sub_type = template._petrel_object_link._sub_type)
        destination_guid = petrelinterface_pb2.PetrelObjectGuid() if (destination is None) else petrelinterface_pb2.PetrelObjectGuid(guid = destination._object_link._guid, sub_type = destination._object_link._sub_type)
        request = petrelinterface_pb2.Clone_Request(
            guid = po_guid,
            name = name,
            sub_type = self._sub_type,
            copy_values = copy_values,
            templateguid = template_guid,
            destinationguid = destination_guid,
            realize_path = realize_path
        )
        reply = self._base_channel.PetrelObject_Clone(request)
        clone_guid = reply.guid
        if not clone_guid:
            return None

        clone = self._plink._get(self._sub_type, clone_guid)
        clone.readonly = False

        return clone

    def MovePetrelObject(self, destination: "Folder"):
        self._plink._opened_test()
        object_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        destination_guid = petrelinterface_pb2.PetrelObjectGuid(guid = destination._object_link._guid, sub_type = destination._object_link._sub_type)
        request = petrelinterface_pb2.PetrelObject_Move_Request(
            guid = object_guid,
            destinationGuid = destination_guid
        )
        response = self._base_channel.PetrelObject_Move(request)
        return response.value
        
    def RetrieveHistory(self):
        self._plink._opened_test()
    
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._base_channel.PetrelObject_RetrieveHistory(request)
        
        merged_list = [item for sublist in responses for item in sublist.values]
        n = len(merged_list) // 4
        if n > 0:
            return [merged_list[i:i + n] for i in range(0, len(merged_list), n)]
        else:
            return 4*[[]]

    def GetTemplateString(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        return self._base_channel.PetrelObject_GetTemplate(request).GetTemplate

    def GetTemplate(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        return self._base_channel.PetrelObject_GetTemplate(request).Template

    def GetDomainString(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuidAndBool(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            value = True
        )
        return self._plink._service_petrel_object.PetrelObject_GetDomain(request).value

    def GetComments(self):
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._base_channel.PetrelObject_GetComments(request)

        return response.value

    def AddComments(self, comment: str, overwrite: bool) -> bool:
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObject_AddComment_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            NewComment = comment,
            OverWrite = overwrite
        )

        response = self._base_channel.PetrelObject_AddComment(request)

        return response.value
    
    def GetColorTableDroid(self) -> str:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._base_channel.PetrelObject_GetColorTableInfo(request)
        return str(response.value)

    def DeletePetrelObject(self) -> bool:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._base_channel.PetrelObject_Delete(request)
        return response.value
