# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool.grpc import petrelinterface_pb2
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
import pandas as pd
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.faultinterpretation_hub import FaultInterpretationHub

class FaultInterpretationGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(FaultInterpretationGrpc, self).__init__(WellKnownObjectDescription.FaultInterpretation, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._invariant_content = {}
        self._channel = typing.cast("FaultInterpretationHub", petrel_connection._service_faultinterpretation)

    def GetFaultSticksDataframe(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.FaultInterpretation_GetFaultSticksDataframe(request)
        ids = []
        xs, ys, zs = [], [], []
        for response in responses:
            for x in response.PointX:
                ids.append(response.FaultStickId)
                xs.append(x)
            for y in response.PointY:
                ys.append(y)
            for z in response.PointZ:
                zs.append(z)
        data = {}
        data["Fault Stick ID"] = pd.Series(ids, dtype = pd.Int64Dtype())
        data["X"] = pd.Series(xs, dtype = float)
        data["Y"] = pd.Series(ys, dtype = float)
        data["Z"] = pd.Series(zs, dtype = float)
        return pd.DataFrame(data)
    
    def ClearAllPolylines(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        self._channel.FaultInterpretation_ClearAllPolylines(request)

    def SetPolylines(self, polylines_dict: dict, seismic_context = None):
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)

        if seismic_context is not None:
            from cegalprizm.pythontool import SeismicLine, SeismicCube
            if isinstance(seismic_context, SeismicLine):
                context_guid = petrelinterface_pb2.PetrelObjectGuid(guid = seismic_context._seismicline_object_link._guid, sub_type = seismic_context._seismicline_object_link._sub_type)
            elif isinstance(seismic_context, SeismicCube):
                context_guid = petrelinterface_pb2.PetrelObjectGuid(guid = seismic_context._seismiccube_object_link._guid, sub_type = seismic_context._seismiccube_object_link._sub_type)
            else:
                raise ValueError("The connected_seismic context must be a SeismicLine or a SeismicCube")
        else:
            context_guid = petrelinterface_pb2.PetrelObjectGuid()

        iterable_requests = []
        for index, values in polylines_dict.items():
            request = petrelinterface_pb2.AddMultiplePolylines_Request(
                Guid = po_guid,
                PolyIndex = index,
                Xs = [x for x in values[0]],
                Ys = [y for y in values[1]],
                Zs = [z for z in values[2]],
                ContextGuid = context_guid
            )
            iterable_requests.append(request)
        self._channel.FaultInterpretation_SetPolylines(r for r in iterable_requests)