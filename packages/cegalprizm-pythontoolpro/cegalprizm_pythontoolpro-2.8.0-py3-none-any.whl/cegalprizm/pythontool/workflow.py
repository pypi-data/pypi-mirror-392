# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.completions_casingstring import CasingString
from cegalprizm.pythontool.completions_perforation import Perforation
from cegalprizm.pythontool.completions_plugback import Plugback
from cegalprizm.pythontool.completions_squeeze import Squeeze
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistoryToBeDeprecated, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion
import datetime

from cegalprizm.pythontool.checkshot import CheckShot
from cegalprizm.pythontool.grid import Grid
from cegalprizm.pythontool.gridproperty import GridProperty, GridDiscreteProperty
from cegalprizm.pythontool.gridpropertycollection import PropertyCollection, PropertyFolder
from cegalprizm.pythontool.surface import Surface, SurfaceAttribute, SurfaceDiscreteAttribute, Surfaces
from cegalprizm.pythontool.markerattribute import MarkerAttribute
from cegalprizm.pythontool.markercollection import MarkerCollection
from cegalprizm.pythontool.markerstratigraphy import MarkerStratigraphy
from cegalprizm.pythontool.stratigraphyzone import StratigraphyZone
from cegalprizm.pythontool.borehole import Well
from cegalprizm.pythontool.folder import Folder
from cegalprizm.pythontool.globalwelllogfolder import GlobalWellLogFolder
from cegalprizm.pythontool.wellattribute import WellAttribute
from cegalprizm.pythontool.wellfolder import WellFolder
from cegalprizm.pythontool.welllog import WellLog, DiscreteWellLog, GlobalWellLog, DiscreteGlobalWellLog
from cegalprizm.pythontool.observeddata import ObservedData, ObservedDataSet, GlobalObservedDataSet
from cegalprizm.pythontool.points import PointSet
from cegalprizm.pythontool.polylineattribute import PolylineAttribute
from cegalprizm.pythontool.polylines import PolylineSet
from cegalprizm.pythontool.faultinterpretation import FaultInterpretation
from cegalprizm.pythontool.interpretationfolder import InterpretationFolder
from cegalprizm.pythontool.horizoninterpretation import HorizonInterpretation3d, HorizonProperty3d, HorizonInterpretation
from cegalprizm.pythontool.savedsearch import SavedSearch
from cegalprizm.pythontool.seismic import SeismicCube, SeismicLine
from cegalprizm.pythontool.wavelet import Wavelet
from cegalprizm.pythontool.wellsurvey import WellSurvey
from cegalprizm.pythontool.template import Template, DiscreteTemplate
from cegalprizm.pythontool.zone import Zone
from cegalprizm.pythontool.segment import Segment
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
import typing
from warnings import warn

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.workflow_grpc import WorkflowGrpc

class ReferenceVariable(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistoryToBeDeprecated, PetrelObjectWithPetrelNameSetter):
    def __hash__(self):
        return hash((self.droid, self.path))

    def __eq__(self, other) -> bool:
        try:
            return (self.droid, self.petrel_name) == (other.droid, other.petrel_name)
        except Exception:
            return False

    def __init__(self, python_reference_variable_object):
        super(ReferenceVariable, self).__init__(python_reference_variable_object)

    def __str__(self) -> str:
        return 'ReferenceVariable(petrel_name="{0}")'.format(self.petrel_name)

def _pb_grpcobj_to_pyobj(pol):
    if pol is None:
        return None
    if pol._sub_type == WellKnownObjectDescription.Grid:
        return Grid(pol)
    elif pol._sub_type == WellKnownObjectDescription.GridProperty:
        return GridProperty(pol)
    elif pol._sub_type == WellKnownObjectDescription.GridDiscreteProperty:
        return GridDiscreteProperty(pol)
    elif pol._sub_type == WellKnownObjectDescription.Surface:
        return Surface(pol)
    elif pol._sub_type == WellKnownObjectDescription.SurfaceProperty:
        return SurfaceAttribute(pol)
    elif pol._sub_type == WellKnownObjectDescription.SurfaceDiscreteProperty:
        return SurfaceDiscreteAttribute(pol)
    elif pol._sub_type == WellKnownObjectDescription.SurfaceCollection:
        return Surfaces(pol)
    elif pol._sub_type == WellKnownObjectDescription.MarkerCollection:
        return MarkerCollection(pol)
    elif pol._sub_type == WellKnownObjectDescription.FaultInterpretation:
        return FaultInterpretation(pol)
    elif pol._sub_type == WellKnownObjectDescription.InterpretationCollection:
        return InterpretationFolder(pol)
    elif pol._sub_type == WellKnownObjectDescription.Borehole:
        return Well(pol)
    elif pol._sub_type == WellKnownObjectDescription.BoreholeCollection:
        return WellFolder(pol)
    elif pol._sub_type == WellKnownObjectDescription.WellLog:
        return WellLog(pol)
    elif pol._sub_type == WellKnownObjectDescription.WellLogDiscrete:
        return DiscreteWellLog(pol)
    elif pol._sub_type == WellKnownObjectDescription.WellLogGlobal:
        return GlobalWellLog(pol)
    elif pol._sub_type == WellKnownObjectDescription.WellLogGlobalDiscrete:
        return DiscreteGlobalWellLog(pol)
    elif pol._sub_type == WellKnownObjectDescription.WellLogFolderGlobal:
        return GlobalWellLogFolder(pol)
    elif pol._sub_type == WellKnownObjectDescription.SeismicCube:
        return SeismicCube(pol)
    elif pol._sub_type == WellKnownObjectDescription.SeismicLine:
        return SeismicLine(pol)
    elif pol._sub_type == WellKnownObjectDescription.ObservedDataSetGlobal:
        return GlobalObservedDataSet(pol)
    elif pol._sub_type == WellKnownObjectDescription.ObservedDataSet:
        return ObservedDataSet(pol)
    elif pol._sub_type == WellKnownObjectDescription.ObservedData:
        return ObservedData(pol)
    elif pol._sub_type == WellKnownObjectDescription.PropertyCollection:
        return PropertyCollection(pol)
    elif pol._sub_type == WellKnownObjectDescription.PropertyFolder:
        return PropertyFolder(pol)
    elif pol._sub_type == WellKnownObjectDescription.PointSet:
        return PointSet(pol)
    elif pol._sub_type == WellKnownObjectDescription.PolylineSet:
        return PolylineSet(pol)
    elif pol._sub_type == WellKnownObjectDescription.PolylineAttribute:
        return PolylineAttribute(pol)
    elif pol._sub_type == WellKnownObjectDescription.HorizonProperty3D:
        return HorizonProperty3d(pol)
    elif pol._sub_type == WellKnownObjectDescription.HorizonInterpretation3D:
        return HorizonInterpretation3d(pol)
    elif pol._sub_type == WellKnownObjectDescription.HorizonInterpretation:
        return HorizonInterpretation(pol)
    elif pol._sub_type == WellKnownObjectDescription.Wavelet:
        return Wavelet(pol)
    elif pol._sub_type == WellKnownObjectDescription.WellSurveyXYZ:
        return WellSurvey(pol)
    elif pol._sub_type == WellKnownObjectDescription.WellSurveyXYTVD:
        return WellSurvey(pol)
    elif pol._sub_type == WellKnownObjectDescription.WellSurveyDxDyTVD:
        return WellSurvey(pol)
    elif pol._sub_type == WellKnownObjectDescription.WellSurveyMdInclAzim:
        return WellSurvey(pol)
    elif pol._sub_type == WellKnownObjectDescription.WellSurveyExplicit:
        return WellSurvey(pol)
    elif pol._sub_type == WellKnownObjectDescription.Template:
        return Template(pol)
    elif pol._sub_type == WellKnownObjectDescription.TemplateDiscrete:
        return DiscreteTemplate(pol)
    elif pol._sub_type == WellKnownObjectDescription.ReferenceVariable:
        return ReferenceVariable(pol)
    elif pol._sub_type == WellKnownObjectDescription.Workflow:
        return Workflow(pol)
    elif pol._sub_type == WellKnownObjectDescription.CheckShot:
        return CheckShot(pol)
    elif pol._sub_type == WellKnownObjectDescription.MarkerAttribute:
        return MarkerAttribute(pol)
    elif pol._sub_type == WellKnownObjectDescription.MarkerStratigraphy:
        return MarkerStratigraphy(pol)
    elif pol._sub_type == WellKnownObjectDescription.MarkerStratigraphyHorizon:
        return MarkerStratigraphy(pol)
    elif pol._sub_type == WellKnownObjectDescription.MarkerStratigraphyZone:
        return StratigraphyZone(pol)
    elif pol._sub_type == WellKnownObjectDescription.CompletionsCasingString:
        return CasingString(pol)
    elif pol._sub_type == WellKnownObjectDescription.CompletionsPerforation:
        return Perforation(pol)
    elif pol._sub_type == WellKnownObjectDescription.CompletionsSqueeze:
        return Squeeze(pol)
    elif pol._sub_type == WellKnownObjectDescription.CompletionsPlugback:
        return Plugback(pol)
    elif pol._sub_type == WellKnownObjectDescription.Zone:
        return Zone(pol)
    elif pol._sub_type == WellKnownObjectDescription.Segment:
        return Segment(pol)
    elif pol._sub_type == WellKnownObjectDescription.SavedSearch:
        return SavedSearch(pol)
    elif pol._sub_type == WellKnownObjectDescription.WellAttribute or pol._sub_type == WellKnownObjectDescription.WellAttributeDiscrete:
        return WellAttribute(pol)
    elif pol._sub_type == WellKnownObjectDescription.Folder:
        return Folder(pol)

class Workflow(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    """A class holding information about a Petrel workflow"""

    def __init__(self, python_workflow_object: "WorkflowGrpc"):
        super(Workflow, self).__init__(python_workflow_object)
        self._workflow_object_link = python_workflow_object

    @property
    def input(self) -> typing.Dict[str, ReferenceVariable]:
        """The input variables for the workflow

        Returns:
            cegalprizm.pythontool.workflow.ReferenceVariable: the input variables for the workflow
        """        
        ref_vars = [ReferenceVariable(obj) for obj in self._workflow_object_link.GetWorkflowInputReferences()]
        return dict([(r.petrel_name, r) for r in ref_vars])

    @property
    def output(self) -> typing.Dict[str, ReferenceVariable]:
        """The output variables for the workflow

        Returns:
            cegalprizm.pythontool.workflow.ReferenceVariable: the output variables for the workflow
        """        
        ref_vars = [ReferenceVariable(obj) for obj in self._workflow_object_link.GetWorkflowOutputReferences()]
        return dict([(r.petrel_name, r) for r in ref_vars])

    def __str__(self) -> str:
        return 'Workflow(petrel_name="{0}")'.format(self.petrel_name)

    def run(self, 
            args: typing.Optional[typing.Dict[typing.Union[str,ReferenceVariable], typing.Union[str, float, int, bool, datetime.datetime, PetrelObject]]] = None,
            return_strings: typing.List[str] = [],
            return_numerics: typing.List[str] = [],
            return_dates: typing.List[str] = []
        )\
            -> typing.Dict[ReferenceVariable, typing.Union[PetrelObject, None]]:
        """Executes the workflow in Petrel.

        Args:
            args: A dictionary with input variables as keys and input as values. It is possible to define additional input variables in this dictionary.
            return_strings: A list of string variable names to be returned from the workflow. Defaults to an empty list.
            return_numerics: A list of numeric variable names to be returned from the workflow. Defaults to an empty list.
            return_dates: A list of date variable names to be returned from the workflow. Defaults to an empty list.

        Returns:
            A dictionary with output variables as keys and output as values. Defaults to None.

        Raises:
            ValueError: If a ReferenceVariable is not paired with a PetrelObject.
        
        **Example**:

        A workflow with folder input variable.

        .. code-block:: python

            workflow = petrel.workflows['Workflows/Path/To/Workflow']
            obj = workflow.input['input_object']
            folder = pet.folders.get_by_name("NameOfFolder")
            workflow.run({obj: folder})

        **Example**:

        A workflow returning numeric, string and date expressions values.

        .. code-block:: python

            workflow = petrel.workflows['Workflows/Path/To/Workflow']
            return_dict = workflow.run(return_strings=["$string"], return_dates=["$date"], return_numerics=["$number"])
            return_dict
            >> {'$string': 'AString', '$number': 42.22, '$date': datetime.datetime(2015, 6, 29, 0, 0)}
        """

        if args is None:
            args = {}
        referenceVars = []
        referenceTargets = [] 
        doubleNames = [] 
        doubleVals = [] 
        intNames = [] 
        intVals = [] 
        boolNames = [] 
        boolVals = [] 
        dateNames = [] 
        dateVals = [] 
        stringNames = [] 
        stringVals = [] 

        for key, val in args.items():
            if isinstance(key, ReferenceVariable) and isinstance(val, PetrelObject):
                referenceVars.append(key._petrel_object_link)
                referenceTargets.append(val._petrel_object_link)
            elif isinstance(key, ReferenceVariable) and (isinstance(val, Template) or isinstance(val, DiscreteTemplate)):
                referenceVars.append(key._petrel_object_link)
                referenceTargets.append(val._petrel_object_link)
            elif isinstance(key, ReferenceVariable) and not isinstance(val, PetrelObject):
                raise ValueError("Reference variables must be paired with PetrelObjects")
            elif isinstance(key, str):
                if isinstance(val, float):
                    doubleNames.append(key)
                    doubleVals.append(val)
                if isinstance(val, int):
                    intNames.append(key)
                    intVals.append(val)
                if isinstance(val, bool):
                    boolNames.append(key)
                    boolVals.append(val)
                if isinstance(val, datetime.datetime):
                    dateNames.append(key)
                    dateVals.append(val)
                if isinstance(val, str):
                    stringNames.append(key)
                    stringVals.append(val)

        obj_dict, value_dict = self._workflow_object_link.RunSingle(
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
            return_strings,
            return_numerics,
            return_dates
        )

        results = {}
        for variable_ref, val in obj_dict.items():
            key = _pb_grpcobj_to_pyobj(variable_ref)
            value = _pb_grpcobj_to_pyobj(val)
            results[key] = value

        results.update(value_dict)

        return results # type: ignore

    def retrieve_history(self):
        """DeprecationWarning: retrieve_history() not available for Workflow objects. This method will be removed in Python Tool Pro 3.0.
        """
        warn("retrieve_history() not available for Workflow objects. This method will be removed in Python Tool Pro 3.0.", DeprecationWarning, stacklevel=2)
        print("History not available for this object type.")