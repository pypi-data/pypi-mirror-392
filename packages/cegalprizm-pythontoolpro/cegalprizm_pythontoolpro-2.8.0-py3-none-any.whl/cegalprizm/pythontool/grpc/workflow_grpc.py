# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import datetime
from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from cegalprizm.pythontool.grpc import petrelinterface_pb2
from cegalprizm.pythontool.grpc import utils as grpc_utils

import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.workflow_hub import WorkflowHub, ReferenceVariableHub
    
class ReferenceVariableGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(ReferenceVariableGrpc, self).__init__(WellKnownObjectDescription.ReferenceVariable, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("ReferenceVariableHub", petrel_connection._service_referencevariable)

    def __str__(self):
        return 'ReferenceVariable(petrel_name="{}")'.format(self.GetPetrelName())

class WorkflowGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(WorkflowGrpc, self).__init__(WellKnownObjectDescription.Workflow, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("WorkflowHub", petrel_connection._service_workflow)

    def __str__(self):
        return 'Workflow(petrel_name="{}")'.format(self.GetPetrelName())

    def GetWorkflowInputReferences(self):
        self._plink._opened_test()
    
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.Workflow_GetWorkflowInputReferences(request)
        
        return [ReferenceVariableGrpc(item.guid, self._plink) if item.guid else None for sublist in responses for item in sublist.guids] 
    
    def GetWorkflowOutputReferences(self):
        self._plink._opened_test()
    
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.Workflow_GetWorkflowOutputReferences(request)
        
        return [ReferenceVariableGrpc(item.guid, self._plink) if item.guid else None for sublist in responses for item in sublist.guids]
    
    def RunSingle(
                    self, 
                    referenceVars, 
                    referenceTargets, 
                    doubleNames, 
                    doubleVals, 
                    intNames, 
                    intVals, 
                    boolNames, 
                    boolVals, 
                    dateNames, 
                    dateVals, 
                    stringNames, 
                    stringVals,
                    returnStrings,
                    returnDoubles,
                    returnDates
                ):
        self._plink._opened_test()

        request = petrelinterface_pb2.Workflow_RunSingle_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
            , referenceVars = [petrelinterface_pb2.PetrelObjectGuid(guid = v._guid, sub_type = v._sub_type) for v in referenceVars]
            , referenceTargets = [petrelinterface_pb2.PetrelObjectGuid(guid = v._guid, sub_type = v._sub_type) for v in referenceTargets]
            , doubleNames = [v for v in doubleNames]
            , doubleVals = [v for v in doubleVals]
            , intNames = [v for v in intNames]
            , intVals = [v for v in intVals]
            , boolNames = [v for v in boolNames]
            , boolVals = [v for v in boolVals]
            , dateNames = [v for v in dateNames]
            , dateVals = [petrelinterface_pb2.Date(year=v.year, month=v.month, day=v.day, hour=v.hour, minute=v.minute, second=v.second) for v in dateVals]
            , stringNames = [v for v in stringNames]
            , stringVals = [v for v in stringVals]
            , returnVals = petrelinterface_pb2.Workflow_RunSingle_ReturnVals(
                stringVals = [v for v in returnStrings]
                , doubleVals = [v for v in returnDoubles]
                , dateVals = [v for v in returnDates]
            )
        )

        response = self._channel.Workflow_RunSingle(request)
        objs = [grpc_utils.pb_PetrelObjectRef_to_grpcobj(val, self._plink) for val in response.RunSingle]
        two_split = (objs[i:i+2] for i in range(0, len(objs), 2))
        obj_dict = {}
        for variable_ref, val in two_split:
            obj_dict[variable_ref] = val

        value_dict = {}
        for k, v in response.DoubleValueVariable.items():
            value_dict[k] = v

        for k, v in response.StringValueVariable.items():
            value_dict[k] = v
            
        for k, v in response.DateValueVariable.items():
            value_dict[k] = datetime.datetime(v.year, v.month, v.day, v.hour, v.minute, v.second)

        return obj_dict, value_dict
