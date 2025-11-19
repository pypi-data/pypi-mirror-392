# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc import petrelinterface_pb2
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from .petrelobject_grpc import PetrelObjectGrpc
import datetime
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.completionsset_hub import CompletionsSetHub

class CasingStringGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(CasingStringGrpc, self).__init__(WellKnownObjectDescription.CompletionsCasingString, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._invariant_content = {}
        self._channel = typing.cast("CompletionsSetHub", petrel_connection._service_completionsset)

    def GetEndDepth(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(
            guid = self._guid
        )
        response = self._channel.GetCasingStringEndDepth(request)
        return response.Md
    
    def SetEndDepth(self, new_depth: float) -> bool:
        self._plink._opened_test()
        request = petrelinterface_pb2.CompletionsSet_SetDepth_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            NewMd = new_depth,
        )
        response = self._channel.SetCasingStringEndDepth(request)
        return response.value
    
    def GetStartDate(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(
            guid = self._guid
        )
        response = self._channel.GetCasingStringStartDate(request)
       
        grpcDate: petrelinterface_pb2.Date = response.Date
        date = datetime.datetime(grpcDate.year, grpcDate.month, grpcDate.day, grpcDate.hour, grpcDate.minute, grpcDate.second)
        return date
    
    def SetStartDate(self, new_date: datetime.datetime) -> bool:
        self._plink._opened_test()
        grpcDate = petrelinterface_pb2.Date(
            year = new_date.year,
            month = new_date.month,
            day = new_date.day,
            hour = new_date.hour,
            minute = new_date.minute,
            second = new_date.second
        )
        request = petrelinterface_pb2.PetrelObject_SetDate_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            NewDate = grpcDate,
        )
        response = self._channel.SetCasingStringStartDate(request)
        return response.value

    def GetCasingStringParts(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid)
        responses = self._channel.GetCasingStringParts(request)
        container = []
        for response in responses:
            container.append(response.Name)
            container.append(response.StartDepth)
            container.append(response.EndDepth)
        return container
    
    def AddCasingStringPart(self, split_md, equipment_name):
        self._plink._opened_test()
        request = petrelinterface_pb2.CompletionsSet_AddCasingStringPart_Request(
            Guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            SplitMd = split_md,
            EquipmentName = equipment_name
        )
        response = self._channel.AddCasingStringPart(request)
        name = response.Name
        start_depth  = response.StartDepth
        end_depth = response.EndDepth
        return name, start_depth, end_depth

    def RemoveCasingStringPart(self, start_depth, end_depth):
        self._plink._opened_test()
        request = petrelinterface_pb2.CompletionsSet_RemoveCasingStringPart_Request(
            Guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            StartDepth = start_depth,
            EndDepth = end_depth
        )
        response = self._channel.RemoveCasingStringPart(request)
        return response

    def SetCasingPartDepth(self, start_depth, old_end_depth, new_end_depth) -> bool:
        self._plink._opened_test()
        request = petrelinterface_pb2.CompletionsSet_CasingStrings_SetPartDepth_Request(
            Guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            StartDepth = start_depth,
            OldEndDepth = old_end_depth,
            NewEndDepth = new_end_depth
        )
        response = self._channel.SetCasingStringPartDepth(request)
        return response.NewEndDepth