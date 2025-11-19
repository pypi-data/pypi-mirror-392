# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from cegalprizm.pythontool.grpc import petrelinterface_pb2, utils
import datetime
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.completionsset_hub import CompletionsSetHub

class PerforationGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(PerforationGrpc, self).__init__(WellKnownObjectDescription.CompletionsPerforation, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._invariant_content = {}
        self._channel = typing.cast("CompletionsSetHub", petrel_connection._service_completionsset)

    def GetTopMd(self) -> float:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(
            guid = self._guid
        )
        response = self._channel.GetPerforationTopMd(request)
        return response.Md

    def SetTopMd(self, new_top_md: float) -> bool:
        self._plink._opened_test()
        request = petrelinterface_pb2.CompletionsSet_SetDepth_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            NewMd = new_top_md
        )
        response = self._channel.SetPerforationTopMd(request)
        return response.value

    def GetBottomMd(self) -> float:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(
            guid = self._guid
        )
        response = self._channel.GetPerforationBottomMd(request)
        return response.Md

    def SetBottomMd(self, new_bottom_md: float) -> bool:
        self._plink._opened_test()
        request = petrelinterface_pb2.CompletionsSet_SetDepth_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            NewMd = new_bottom_md
        )
        response = self._channel.SetPerforationBottomMd(request)
        return response.value

    def GetDate(self) -> datetime.datetime:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(
            guid = self._guid
        )
        response = self._channel.GetPerforationDate(request)
        grpcDate: petrelinterface_pb2.Date = response.Date
        date = datetime.datetime(grpcDate.year, grpcDate.month, grpcDate.day, grpcDate.hour, grpcDate.minute, grpcDate.second)
        return date

    def SetDate(self, new_date: datetime.datetime) -> bool:
        self._plink._opened_test()
        grpcDate = utils.datetime_to_pb_date(new_date)
        request = petrelinterface_pb2.PetrelObject_SetDate_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            NewDate = grpcDate
        )
        response = self._channel.SetPerforationDate(request)
        return response.value

    def GetSkinFactor(self) -> float:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(
            guid = self._guid
        )
        response = self._channel.GetPerforationSkinFactor(request)
        return response.SkinFactor

    def SetSkinFactor(self, new_skin_factor: float) -> bool:
        self._plink._opened_test()
        request = petrelinterface_pb2.CompletionsSet_Perforations_SetSkinFactor_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            NewSkinFactor = new_skin_factor
        )
        response = self._channel.SetPerforationSkinFactor(request)
        return response.value