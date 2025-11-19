# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from .borehole_grpc import BoreholeGrpc
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from cegalprizm.pythontool.grpc import petrelinterface_pb2, utils
import typing
import pandas as pd
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.checkshot_hub import CheckShotHub

class CheckShotGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection", sub_type: str = WellKnownObjectDescription.CheckShot):
        super(CheckShotGrpc, self).__init__(sub_type, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("CheckShotHub", petrel_connection._service_checkshot)

    def GetCheckShotDataFrame(self, include_unconnected_checkshots: bool, boreholes: list, include_user_properties: bool) -> pd.DataFrame:
        self._plink._opened_test()

        well_guids = utils.GetWellGuids(boreholes)
        request = petrelinterface_pb2.CheckShot_GetValues_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            includeUnconnectedCheckShots = include_unconnected_checkshots,
            wellGuids = [guid for guid in well_guids],
            includeUserDefinedProperties = include_user_properties
        )
        responses = self._channel.GetCheckShotData(request)
        return self.CreateCheckShotDataFrame(responses)
    
    def CreateCheckShotDataFrame(self, responses) -> pd.DataFrame:
        data = {}
        mds, petrelIndices, twts, wellNames, averageVelocities, intervalVelocities, zs = [], [], [], [], [], [], []
        userDefinedNames, userDefinedValues, userDefinedTypes = [], [], []
        
        for response in responses:
            mds.append(response.md)
            petrelIndices.append(response.nativeIndex+1)
            twts.append(response.twt)
            averageVelocities.append(round(response.averageVelocity, 2))
            intervalVelocities.append(round(response.intervalVelocity, 2))
            zs.append(response.z)
            wellNames.append(response.wellName)
            userDefinedNames.append(response.userDefinedPropertyName)
            userDefinedValues.append(response.userDefinedPropertyValue)
            userDefinedTypes.append(response.userDefinedPropertyType)

        data['Petrel Index'] = pd.Series(petrelIndices)
        data['MD'] = pd.Series(mds)
        data['TWT'] = pd.Series(twts)
        data['Average Velocity'] = pd.Series(averageVelocities)
        data['Interval Velocity'] = pd.Series(intervalVelocities)
        data['Z'] = pd.Series(zs)
        data['Well'] = pd.Series(wellNames)

        if len(userDefinedNames[0]) > 0:
            data = utils.HandleUserDefinedProperties(data, userDefinedNames, userDefinedValues, userDefinedTypes)
        return  pd.DataFrame(data)
    
    def GetWells(self, saved_search = None):
        self._plink._opened_test()
        guids = []
        guids.append(petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type))
        
        if saved_search is not None:
            guids.append(petrelinterface_pb2.PetrelObjectGuid(guid = saved_search._savedsearch_object_link._guid, sub_type = saved_search._savedsearch_object_link._sub_type))
        
        request = petrelinterface_pb2.PetrelObjectGuids(guids = guids)
        responses = self._channel.CheckShot_GetWells(request)
        return [BoreholeGrpc(response.guid, self._plink) for response in responses]
