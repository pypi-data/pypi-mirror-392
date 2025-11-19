# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




from enum import Enum
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription

class NumericDataTypeEnum(Enum):
    Continuous = "continuous"
    Discrete = "discrete"

class DataTypeEnum(Enum):
    Continuous = "continuous"
    Discrete = "discrete"
    String = "string"
    DateTime = "datetime"
    Boolean = "boolean"

## Note that this enum is used for filtering in Folder.get_objects, it should not be added to unless the added object is also an object that can be stored in a folder in Petrel.
class FolderObjectTypeEnum(Enum):
    Folder = WellKnownObjectDescription.Folder.value
    MarkerCollection = WellKnownObjectDescription.MarkerCollection.value.replace(" ", "") ## WellKnownString has space, but the class name doe not.
    PointSet = WellKnownObjectDescription.PointSet.value
    PolylineSet = WellKnownObjectDescription.PolylineSet.value
    Surface = WellKnownObjectDescription.Surface.value
    Wavelet = WellKnownObjectDescription.Wavelet.value

class DomainObjectsEnum(Enum):
    CasingString = WellKnownObjectDescription.CompletionsCasingString.value
    CheckShot = WellKnownObjectDescription.CheckShot.value
    Completion = f"{WellKnownObjectDescription.CompletionsCasingString.value};{WellKnownObjectDescription.CompletionsPerforation.value};{WellKnownObjectDescription.CompletionsPlugback.value};{WellKnownObjectDescription.CompletionsSqueeze.value}"
    DiscreteGlobalWellLog = WellKnownObjectDescription.WellLogGlobalDiscrete.value
    DiscreteTemplate = WellKnownObjectDescription.TemplateDiscrete.value
    DiscreteWellLog = WellKnownObjectDescription.WellLogDiscrete.value
    FaultInterpretation = WellKnownObjectDescription.FaultInterpretation.value
    Folder = WellKnownObjectDescription.Folder.value
    GlobalObservedDataSet = WellKnownObjectDescription.ObservedDataSetGlobal.value
    GlobalWellLog = WellKnownObjectDescription.WellLogGlobal.value
    GlobalWellLogFolder = WellKnownObjectDescription.WellLogFolderGlobal.value
    Grid = WellKnownObjectDescription.Grid.value
    GridDiscreteProperty = WellKnownObjectDescription.GridDiscreteProperty.value
    GridProperty = WellKnownObjectDescription.GridProperty.value
    HorizonInterpretation = WellKnownObjectDescription.HorizonInterpretation.value
    HorizonInterpretation3D = WellKnownObjectDescription.HorizonInterpretation3D.value
    HorizonProperty3D = WellKnownObjectDescription.HorizonProperty3D.value
    InterpretationFolder = WellKnownObjectDescription.InterpretationCollection.value
    MarkerAttribute = f"{WellKnownObjectDescription.MarkerAttribute.value};{WellKnownObjectDescription.MarkerAttributeDiscrete.value}"
    MarkerCollection = WellKnownObjectDescription.MarkerCollection.value
    MarkerStratigraphy = WellKnownObjectDescription.MarkerStratigraphy.value
    ObservedData = WellKnownObjectDescription.ObservedData.value
    ObservedDataSet = WellKnownObjectDescription.ObservedDataSet.value
    Perforation = WellKnownObjectDescription.CompletionsPerforation.value
    Plugback = WellKnownObjectDescription.CompletionsPlugback.value
    PointSet = WellKnownObjectDescription.PointSet.value
    PolylineAttribute = f"{WellKnownObjectDescription.PolylineAttribute.value};{WellKnownObjectDescription.PolylineAttributeDiscrete.value}"
    PolylineSet = WellKnownObjectDescription.PolylineSet.value
    PropertyFolder = WellKnownObjectDescription.PropertyFolder.value
    SavedSearch = WellKnownObjectDescription.SavedSearch.value
    Segment = WellKnownObjectDescription.Segment.value
    SeismicCube = WellKnownObjectDescription.SeismicCube.value
    SeismicLine = WellKnownObjectDescription.SeismicLine.value
    Squeeze = WellKnownObjectDescription.CompletionsSqueeze.value
    Surface = WellKnownObjectDescription.Surface.value
    SurfaceAttribute = WellKnownObjectDescription.SurfaceProperty.value
    SurfaceDiscreteAttribute = WellKnownObjectDescription.SurfaceDiscreteProperty.value
    Template = WellKnownObjectDescription.Template.value
    Wavelet = WellKnownObjectDescription.Wavelet.value
    Well = WellKnownObjectDescription.Borehole.value
    WellAttribute = f"{WellKnownObjectDescription.WellAttribute.value};{WellKnownObjectDescription.WellAttributeDiscrete.value}"
    WellFolder = WellKnownObjectDescription.BoreholeCollection.value
    WellLog = WellKnownObjectDescription.WellLog.value
    WellSurvey = f"{WellKnownObjectDescription.WellSurveyDxDyTVD.value};{WellKnownObjectDescription.WellSurveyExplicit.value};{WellKnownObjectDescription.WellSurveyMdInclAzim.value};{WellKnownObjectDescription.WellSurveyXYTVD.value};{WellKnownObjectDescription.WellSurveyXYZ.value}"
    Zone = WellKnownObjectDescription.Zone.value