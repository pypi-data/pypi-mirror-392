# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc import petrelinterface_pb2
import datetime
import typing
import os
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.oophub.workflowvars_hub import WorkflowvarsHub


class WorkflowVars():
    """A class holding information about a Petrel workflow variables. Only available if used within a Petrel workflow."""

    def __init__(self, petrel_object_link: "WorkflowvarsHub"):
        self._workflowvars_hub = petrel_object_link
        self._workflow_context_id = os.environ.get("workflow_context_id", None)

    def __getitem__(self, key: str) -> typing.Union[float, str, datetime.date]:
        if self._workflow_context_id is None:
            raise ValueError("workflow_context_id is not set")
        
        msg = petrelinterface_pb2.GetDollarVariable(
            id = key,
            context_id = self._workflow_context_id
        )
        vartype = self._workflowvars_hub.GetVarType(msg).value
        if vartype == 0:
            return self._get_double(key)
        elif vartype == 1:
            return self._get_string(key)
        elif vartype == 2:
            return self._get_date(key)
        else:
            raise ValueError(f"Unknown type {vartype}")
        
    def __setitem__(self, key: str, value: typing.Union[float, str, datetime.date]) -> None:
        if isinstance(value, float):
            self._set_double(key, value)
        elif isinstance(value, str):
            self._set_string(key, value)
        elif isinstance(value, datetime.datetime):
            self._set_date(key, value)
        else:
            raise ValueError(f"Unknown type {type(value)}")

    def _get_double(self, name: str) -> float:
        if self._workflow_context_id is None:
            raise ValueError("workflow_context_id is not set")
        
        msg = petrelinterface_pb2.GetDollarVariable(
            id = name,
            context_id = self._workflow_context_id
        )
        response = self._workflowvars_hub.GetVarDouble(msg)
        return response.value
    
    def _get_string(self, name: str) -> str:
        if self._workflow_context_id is None:
            raise ValueError("workflow_context_id is not set")
        
        msg = petrelinterface_pb2.GetDollarVariable(
            id = name,
            context_id = self._workflow_context_id
        )
        response = self._workflowvars_hub.GetVarString(msg)
        return response.value
    
    def _get_date(self, name: str) -> str:
        if self._workflow_context_id is None:
            raise ValueError("workflow_context_id is not set")
        
        msg = petrelinterface_pb2.GetDollarVariable(
            id = name,
            context_id = self._workflow_context_id
        )
        response = self._workflowvars_hub.GetVarDate(msg)
        date = datetime.datetime(response.year, response.month, response.day, response.hour, response.minute, response.second)
        return date
    
    def _set_double(self, name: str, value: float) -> None:
        if self._workflow_context_id is None:
            raise ValueError("workflow_context_id is not set")
        
        msg = petrelinterface_pb2.SetDollarVariableDouble(
            id = name,
            context_id = self._workflow_context_id,
            value = value
        )
        self._workflowvars_hub.SetVarDouble(msg)

    def _set_string(self, name: str, value: str) -> None:
        if self._workflow_context_id is None:
            raise ValueError("workflow_context_id is not set")

        msg = petrelinterface_pb2.SetDollarVariableString(
            id = name,
            context_id = self._workflow_context_id,
            value = value
        )
        self._workflowvars_hub.SetVarString(msg)

    def _set_date(self, name: str, value: datetime.date) -> None:
        if self._workflow_context_id is None:
            raise ValueError("workflow_context_id is not set")
        
        grpcDate = petrelinterface_pb2.Date(
            year = value.year,
            month = value.month,
            day = value.day,
            hour = value.hour,
            minute = value.minute,
            second = value.second
        )

        msg = petrelinterface_pb2.SetDollarVariableDate(
            id = name,
            context_id = self._workflow_context_id,
            date = grpcDate
        )
        self._workflowvars_hub.SetVarDate(msg)