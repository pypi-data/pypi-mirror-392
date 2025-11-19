# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import pandas as pd
import numpy as np
from datetime import datetime
from distutils.util import strtobool
from cegalprizm.pythontool import _config
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription

from cegalprizm.pythontool.grpc import completions_casingstring_grpc, completions_perforation_grpc, completions_plugback_grpc, completions_squeeze_grpc, grid_grpc, gridpropertycollection_grpc, wellattribute_grpc, zone_grpc #GridGrpc
from cegalprizm.pythontool.grpc import gridproperty_grpc #GridPropertyGrpc, GridDiscretePropertyGrpc
from cegalprizm.pythontool.grpc import surface_grpc #SurfaceGrpc, SurfacePropertyGrpc, SurfaceDiscretePropertyGrpc
from cegalprizm.pythontool.grpc import seismic_grpc #Seismic2DGrpc, SeismicCubeGrpc 
from cegalprizm.pythontool.grpc import borehole_grpc #BoreholeGrpc, WellLogGrpc, DiscreteWellLogGrpc, GlobalWellLogGrpc, DiscreteGlobalWellLogGrpc
from cegalprizm.pythontool.grpc import globalwelllogfolder_grpc #GlobalWellLogFolderGrpc
from cegalprizm.pythontool.grpc import borehole_collection_grpc #BoreholeCollectionGrpc
from cegalprizm.pythontool.grpc import markerattribute_grpc #MarkerAttributeGrpc
from cegalprizm.pythontool.grpc import markerstratigraphy_grpc #MarkerStratigraphyGrpc
from cegalprizm.pythontool.grpc import markercollection_grpc #MarkerCollectionGrpc
from cegalprizm.pythontool.grpc import stratigraphyzone_grpc #StratigraphyZoneGrpc
from cegalprizm.pythontool.grpc import faultinterpretation_grpc, interpretation_collection_grpc #FaultInterpretationGrpc
from cegalprizm.pythontool.grpc import points_grpc #PointSetGrpc
from cegalprizm.pythontool.grpc import polylines_grpc, polylineattribute_grpc
from cegalprizm.pythontool.grpc import wavelet_grpc #WaveletGrpc
from cegalprizm.pythontool.grpc import wellsurvey_grpc #XyzWellSurveyGrpc, XytvdWellSurveyGrpc, DxdytvdWellSurveyGrpc, MdinclazimWellSurveyGrpc, ExplicitWellSurveyGrpc
from cegalprizm.pythontool.grpc import horizoninterpretation_grpc #HorizonInterpretation3dGrpc, HorizonProperty3dGrpc, HorizonInterpretationGrpc
from cegalprizm.pythontool.grpc import workflow_grpc #ReferenceVariableGrpc, WorkflowGrpc
from cegalprizm.pythontool.grpc import observeddata_grpc #ObservedDataSetGrpc, ObservedDataGrpc
from cegalprizm.pythontool.grpc import template_grpc #TemplateGrpc, DiscreteTemplateGrpc
from cegalprizm.pythontool.grpc import checkshot_grpc
from cegalprizm.pythontool.grpc import savedsearch_grpc
from cegalprizm.pythontool.grpc import segment_grpc
from cegalprizm.pythontool.grpc import folder_grpc
from cegalprizm.pythontool.grpc import petrelinterface_pb2

def pb_PetrelObjectRef_to_grpcobj(pog, plink):
    if pog is None:
        return None
    elif pog.sub_type == WellKnownObjectDescription.Grid:
        pol = grid_grpc.GridGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.GridProperty:
        pol = gridproperty_grpc.GridPropertyGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.GridDiscreteProperty:
        pol = gridproperty_grpc.GridDiscretePropertyGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.Surface:
        pol = surface_grpc.SurfaceGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.SurfaceProperty:
        pol = surface_grpc.SurfacePropertyGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.SurfaceDiscreteProperty:
        pol = surface_grpc.SurfaceDiscretePropertyGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.SurfaceCollection:
        pol = surface_grpc.SurfaceCollectionGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.MarkerCollection:
        pol = markercollection_grpc.MarkerCollectionGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.FaultInterpretation:
        pol = faultinterpretation_grpc.FaultInterpretationGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.InterpretationCollection:
        pol = interpretation_collection_grpc.InterpretationCollectionGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.MarkerAttribute:
        pol = markerattribute_grpc.MarkerAttributeGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.MarkerStratigraphy:
        pol = markerstratigraphy_grpc.MarkerStratigraphyGrpc(pog.guid, plink, pog.sub_type)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.MarkerStratigraphyHorizon:
        pol = markerstratigraphy_grpc.MarkerStratigraphyGrpc(pog.guid, plink, pog.sub_type)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.MarkerStratigraphyZone:
        pol = stratigraphyzone_grpc.StratigraphyZoneGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.Borehole:
        pol = borehole_grpc.BoreholeGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.BoreholeCollection:
        pol = borehole_collection_grpc.BoreholeCollectionGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.WellLog:
        pol = borehole_grpc.WellLogGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.WellLogDiscrete:
        pol = borehole_grpc.DiscreteWellLogGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.WellLogGlobal:
        pol = borehole_grpc.GlobalWellLogGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.WellLogGlobalDiscrete:
        pol = borehole_grpc.DiscreteGlobalWellLogGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.WellLogFolderGlobal:
        pol = globalwelllogfolder_grpc.GlobalWellLogFolderGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.SeismicCube:
        pol = seismic_grpc.SeismicCubeGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.SeismicLine:
        pol = seismic_grpc.Seismic2DGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.ObservedDataSetGlobal:
        pol = observeddata_grpc.GlobalObservedDataSetsGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.ObservedDataSet:
        pol = observeddata_grpc.ObservedDataSetGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.ObservedData:
        pol = observeddata_grpc.ObservedDataGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.PropertyCollection:
        pol = gridpropertycollection_grpc.PropertyCollectionGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.PropertyFolder:
        pol = gridpropertycollection_grpc.PropertyFolderGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.PointSet:
        pol = points_grpc.PointSetGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.PolylineSet:
        pol = polylines_grpc.PolylineSetGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.PolylineAttribute:
        pol = polylineattribute_grpc.PolylineAttributeGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.HorizonProperty3D:
        pol = horizoninterpretation_grpc.HorizonProperty3dGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.HorizonInterpretation3D:
        pol = horizoninterpretation_grpc.HorizonInterpretation3dGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.HorizonInterpretation:
        pol = horizoninterpretation_grpc.HorizonInterpretationGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.Wavelet:
        pol = wavelet_grpc.WaveletGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.WellSurveyXYZ:
        pol = wellsurvey_grpc.XyzWellSurveyGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.WellSurveyXYTVD:
        pol = wellsurvey_grpc.XytvdWellSurveyGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.WellSurveyDxDyTVD:
        pol = wellsurvey_grpc.DxdytvdWellSurveyGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.WellSurveyMdInclAzim:
        pol = wellsurvey_grpc.MdinclazimWellSurveyGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.WellSurveyExplicit:
        pol = wellsurvey_grpc.ExplicitWellSurveyGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.ReferenceVariable:
        pol = workflow_grpc.ReferenceVariableGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.Workflow:
        pol = workflow_grpc.WorkflowGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.Template:
        pol = template_grpc.TemplateGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.TemplateDiscrete:
        pol = template_grpc.DiscreteTemplateGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.CheckShot:
        pol = checkshot_grpc.CheckShotGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.CompletionsCasingString:
        pol = completions_casingstring_grpc.CasingStringGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.CompletionsPerforation:
        pol = completions_perforation_grpc.PerforationGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.CompletionsSqueeze:
        pol = completions_squeeze_grpc.SqueezeGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.CompletionsPlugback:
        pol = completions_plugback_grpc.PlugbackGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.Zone:
        pol = zone_grpc.ZoneGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.Segment:
        pol = segment_grpc.SegmentGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.SavedSearch:
        pol = savedsearch_grpc.SavedSearchGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.WellAttribute or pog.sub_type == WellKnownObjectDescription.WellAttributeDiscrete:
        pol = wellattribute_grpc.WellAttributeGrpc(pog.guid, plink)
        return pol
    elif pog.sub_type == WellKnownObjectDescription.Folder:
        pol = folder_grpc.FolderGrpc(pog.guid, plink)
        return pol

def datetime_to_pb_date(datetime: datetime):
    grpcDate = petrelinterface_pb2.Date(
            year = datetime.year,
            month = datetime.month,
            day = datetime.day,
            hour = datetime.hour,
            minute = datetime.minute,
            second = datetime.second
        )
    return grpcDate

def get_from_grpc_converter(value_type):
    if value_type == petrelinterface_pb2.STRING:
        return lambda x: x
    if value_type == petrelinterface_pb2.SINGLE_FLOAT or value_type == petrelinterface_pb2.DOUBLE_FLOAT:
        return  lambda x: float(x)
    if value_type == petrelinterface_pb2.INT:
        def intnoneconverter(x):
            if int(x) ==  _config._INT32MAXVALUE:
                return None
            else:
                return int(x)
        return intnoneconverter
    if value_type == petrelinterface_pb2.BOOL:
        return lambda x: bool(strtobool(x))
    if value_type == petrelinterface_pb2.DATETIME:
        def datetimeconverter(date_string):
            if date_string == "1/1/1/0/0/0":
                return None
            date_ints = [int(v) for v in date_string.split("/")]
            year, month, day, hour, minute, second = date_ints
            return datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
        return datetimeconverter

def isFloat(value) -> bool:
    if 'float' in str(type(value)).lower():
        return True
    return False

def create_indices(data: np.array) -> list:
    indices = []
    for i in range(len(data)):
        indices.append(i)
    return indices

def getNumpyArrayFromPropertyType(values, datatype: petrelinterface_pb2.PointPropertyType) -> pd.Series:
    if datatype == petrelinterface_pb2.STRING:
        df = pd.DataFrame(values).astype(str)
        return df.iloc[:,0].array
    if datatype == petrelinterface_pb2.SINGLE_FLOAT or datatype == petrelinterface_pb2.DOUBLE_FLOAT:
        return np.array(values).astype(np.float64)
    if datatype == petrelinterface_pb2.INT:
        df = pd.DataFrame(values).astype(pd.Int64Dtype())
        return df.iloc[:,0].array
    if datatype == petrelinterface_pb2.BOOL:
        return np.array(values).astype(bool)
    if datatype == petrelinterface_pb2.DATETIME:
        return np.array(pd.to_datetime(values))
    
def check_input_contains_data(data: np.array) -> None:
    if len(data) < 1: # No data
        raise ValueError("Input array does not contain any values")
    
def check_input_has_expected_data_type(data: np.array, expectedPropType) -> None:
    for i in range(len(data)):
        value = data[i]
        if value is None:
            continue
        propType = GetPropTypeForValue(value)
        # Prop type is an int
        if propType != expectedPropType:
            raise ValueError(f"Input data type {type(value)} for value '{value}' does not match expected data type")
    
def GetPropTypeForValue(value) -> int:
    prop_handler = points_grpc.PropertyRangeHandler()
    prop_type = prop_handler._point_property_type(value)
    return prop_type

def GetWellGuid(borehole) -> petrelinterface_pb2.PetrelObjectGuid:
    well_guid = None
    if borehole is not None:
        well_guid = petrelinterface_pb2.PetrelObjectGuid(guid = borehole._borehole_object_link._guid, sub_type = borehole._borehole_object_link._sub_type)
    return well_guid
    
def GetWellGuids(boreholes) -> petrelinterface_pb2.PetrelObjectGuid:
    well_guids = []
    for borehole in boreholes:
        if borehole is not None:
            well_guids.append(GetWellGuid(borehole))
    return well_guids

## Handle user defined properties for Checkshots / Polylinesets

def HandleUserDefinedProperties(data: dict,  userDefinedNames: list, userDefinedValues: list,
                                userDefinedTypes: list) -> dict:
    for i in range(len(userDefinedNames[0])):
        dataForProperty = []
        if len(userDefinedValues[0]) > 0:
            for j in range(len(userDefinedNames)):
                dataForProperty.append(userDefinedValues[j][i])
        definedType = str(userDefinedTypes[0][i])
        columnName = userDefinedNames[0][i]
        if definedType == "System.Single" or definedType == "System.Double":
            data[columnName] = pd.Series(dataForProperty, dtype=float)
        elif "Int" in definedType:
            data[columnName] = HandleAttributeIntegerValues(dataForProperty)
        elif "Boolean" in definedType:
            data[columnName] = HandleAttributeBoolValues(dataForProperty)
        elif "String" in definedType:
            data[columnName] = pd.Series(dataForProperty, dtype=str)
        elif "DateTime" in definedType:
            data[columnName] = HandleAttributeDateTimeValues(dataForProperty)
    return data


def HandleAttributeIntegerValues(dataForProperty: list) -> pd.Series:
    dataAsNullableInt = []
    for value in dataForProperty:
        if int(value) ==  _config._INT32MAXVALUE:
            dataAsNullableInt.append(None)
        else:
            dataAsNullableInt.append(int(value))
    
    return pd.Series(dataAsNullableInt, dtype = pd.Int64Dtype())

def HandleAttributeBoolValues(dataForProperty: list) -> pd.Series:
    dataAsBool = []
    for value in dataForProperty:
        if value == "True":
            dataAsBool.append(True)
        else:
            dataAsBool.append(False)
    return pd.Series(dataAsBool, dtype=bool)

def HandleAttributeDateTimeValues(dataForProperty: list) -> pd.Series:
        datesWithNone = []
        for value in dataForProperty:
            if value == "01/01/0001 00:00:00":
                datesWithNone.append(None)
            else:
                datesWithNone.append(value)
        return pd.Series(datesWithNone, dtype = "datetime64[ns]")

def GetPropTypeFromString(type_as_string: str) -> petrelinterface_pb2.PointPropertyType:
        datatype = None
        if  type_as_string.lower() == "string":
            datatype = petrelinterface_pb2.PointPropertyType.STRING
        elif type_as_string.lower() == "bool":
            datatype = petrelinterface_pb2.PointPropertyType.BOOL
        elif type_as_string.lower() == "continuous": 
            datatype = petrelinterface_pb2.PointPropertyType.DOUBLE_FLOAT
        elif type_as_string.lower() == "discrete":
            datatype = petrelinterface_pb2.PointPropertyType.INT 
        
        return datatype

def GetDepthIndexFromString(depth_index: str) -> petrelinterface_pb2.DepthIndexType:
    if (str(depth_index).upper() == "MD"):
        depth_enum = petrelinterface_pb2.DepthIndexType.MD
    elif str(depth_index).upper() == "TWT":
        depth_enum = petrelinterface_pb2.DepthIndexType.TWT
    elif str(depth_index).upper() == "TVD":
        depth_enum = petrelinterface_pb2.DepthIndexType.TVD
    elif str(depth_index).upper() == "TVDSS":
        depth_enum = petrelinterface_pb2.DepthIndexType.TVDSS
    else:
        raise ValueError("Invalid depth index type: " + depth_index + ". Valid values are: 'MD', 'TWT', 'TVD', 'TVDSS'.")

    return depth_enum

def deep_flatten_list(nested_list: list):
    return [item for sub in nested_list for item in (deep_flatten_list(sub) if isinstance(sub, list) else [sub])]
