# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from . import utils
from cegalprizm.pythontool import _docstring_utils
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription

class PetrelObjectStoreBase(dict):
    """Base class of read-only collections storing Petrel objects by their path.
    When iterated over, the objects are returned, not their paths (unlike a standard
    Python dictionary which returns the keys).
    """

    def __init__(self, petrelconnection):
        self._petrelconnection = petrelconnection
        self._objects = self._query_objects(petrelconnection)

    def _query_objects(self, petrelconnection):
        # Virtual method to be implemented in sub class
        return {}

    def get_petrel_objects(self, objects_info, find_object_by_guid_func):
        objects = {}
        for guid, path in objects_info.items():
            obj = find_object_by_guid_func(guid)

            if path in objects.keys():
                # duplicate paths!
                existing = objects[path]
                # create or append to a list of petrel objects
                if isinstance(existing, list):
                    existing.append(obj)
                else:
                    objects[path] = [existing, obj]
            else:
                # unique path
                objects[path] = obj
        return objects

    def get_petrel_object_from_ref(self, object_refs, find_object_by_obj_ref_func):
        objects = {}
        for objref in object_refs:
            path = objref.path # fetch path from objref instead of from obj below
            obj = find_object_by_obj_ref_func(objref) # do not fetch any properties from this obj as we do not want to trigger more grpc calls

            if path in objects.keys():
                # duplicate paths!
                existing = objects[path]
                # create or append to a list of petrel objects
                if isinstance(existing, list):
                    existing.append(obj)
                else:
                    objects[path] = [existing, obj]
            else:
                # unique path
                objects[path] = obj
        return objects

    def _get_by_name_generic(self, name: str, object_type: str, case_sensitive: bool):
        result =  self._petrelconnection._get_objects_by_name(name, object_type, case_sensitive)

        if len(result) == 0:
            return None
        elif len(result) == 1:
            return result[0]
        else:
            return result

    def __getitem__(self, key):
        try:
            return self._objects[key]   
        except KeyError:
            self._objects = self._query_objects(self._petrelconnection)
            return self._objects[key] 

    def __setitem__(self, key, value):
        raise Exception("This collection is read-only")

    def __len__(self):
        return len(self._objects)

    def __iter__(self):
        # This is not dict-like behaviour!
        return iter(self._objects.values())

    def keys(self):
        """The paths of the Petrel objects

        Returns:
            A list of the paths of the Petrel objects
        """
        return self._objects.keys()

    def values(self):
        """The Petrel objects

        Returns:
            A list of the Petrel objects"""
        return self._objects.values()

    def items(self):
        """The (`path`, `Petrel object`) pairs available.  If multiple objects
        have the same path, a list of Petrel objects is returned.

        Returns:
            A list of (`path`, `objects`) tuples (pairs) available

        """
        return self._objects.items()

    def __str__(self):
        return str(self._objects)

    def __repr__(self):
        return f"{self.__class__.__name__}({str(self)})"

class Properties(PetrelObjectStoreBase):
    """A read-only collection of GridProperty objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_grid_properties(),
            lambda guid: petrelconnection._get_grid_property_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="GridProperty")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.GridProperty, case_sensitive)

class DiscreteProperties(PetrelObjectStoreBase):
    """A read-only collection of GridDiscreteProperty objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_grid_properties(discrete = True),
            lambda guid: petrelconnection._get_grid_property_by_guid(guid, discrete = True)
        )

    @_docstring_utils.get_by_name_decorator(object_type="GridDiscreteProperty")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.GridDiscreteProperty, case_sensitive)

class Grids(PetrelObjectStoreBase):
    """A read-only collection of Grid objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_grids(),
            lambda guid: petrelconnection._get_grid_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="Grid")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.Grid, case_sensitive)

class SeismicCubes(PetrelObjectStoreBase):
    """A read-only collection of Seismic Cube objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_seismic_cubes(),
            lambda guid: petrelconnection._get_seismic_cube_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="SeismicCube")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.SeismicCube, case_sensitive)

class HorizonProperties(PetrelObjectStoreBase):
    """A collection of HorizonProperty objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_horizon_properties(),
            lambda guid: petrelconnection._get_horizon_property_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="HorizonProperty3d")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.HorizonProperty3D, case_sensitive)

class PropertyCollections(PetrelObjectStoreBase):
    """
    .. warning::
        **Deprecated** - This Class will be removed in Python Tool Pro 3.0. Use :attr:`PropertyFolders` instead.
    A collection of PropertyCollection objects.
    """
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_property_collections(),
            lambda guid: petrelconnection._get_property_collection_by_guid(guid)
        )

class PropertyFolders(PetrelObjectStoreBase):
    """A collection of PropertyFolder objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_property_folders(),
            lambda guid: petrelconnection._get_property_folder_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="PropertyFolder")
    def get_by_name(self, name: str, ignore_case: bool = True):
        return self._get_by_name_generic(name, WellKnownObjectDescription.PropertyFolder, ignore_case)

class HorizonInterpretation3Ds(PetrelObjectStoreBase):
    """ A collection of HorizonInterpretation3D objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_horizon_interpretation_3ds(),
            lambda guid: petrelconnection._get_horizon_interpretation_3d_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="HorizonInterpretation3d")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.HorizonInterpretation3D, case_sensitive)

class HorizonInterpretations(PetrelObjectStoreBase):
    """ A collection of HorizonInterpretation3D objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_horizon_interpretations(),
            lambda guid: petrelconnection._get_horizon_interpretation_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="HorizonInterpretation")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.HorizonInterpretation, case_sensitive)

class Seismic2Ds(PetrelObjectStoreBase):
    """ A collection of Seismic2D objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_seismic_2ds(),
            lambda guid: petrelconnection._get_seismic_2d_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="Seismic2D")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.SeismicLine, case_sensitive)

class Surfaces(PetrelObjectStoreBase):
    """A read-only collection of Surface objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_surfaces(),
            lambda guid: petrelconnection._get_surface_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="Surface")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.Surface, case_sensitive)

class SurfaceAttributes(PetrelObjectStoreBase):
    """A read-only collection of SurfaceAttribute objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_surface_attributes(),
            lambda guid: petrelconnection._get_surface_attribute_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="SurfaceAttribute")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.SurfaceProperty, case_sensitive)

class SurfaceDiscreteAttributes(PetrelObjectStoreBase):
    """A read-only collection of SurfaceDiscreteAttribute objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_surface_attributes(discrete = True),
            lambda guid: petrelconnection._get_surface_attribute_by_guid(guid, discrete = True)
        )

    @_docstring_utils.get_by_name_decorator(object_type="SurfaceDiscreteAttribute")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.SurfaceDiscreteProperty, case_sensitive)

class WellLogs(PetrelObjectStoreBase):
    """A read-only collection of WellLog objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_well_logs(),
            lambda guid: petrelconnection._get_well_log_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="WellLog")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.WellLog, case_sensitive)

class DiscreteWellLogs(PetrelObjectStoreBase):
    """A read-only collection of DiscreteWellLog objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_well_logs(discrete = True),
            lambda guid: petrelconnection._get_well_log_by_guid(guid, discrete = True)
        )
    
    @_docstring_utils.get_by_name_decorator(object_type="DiscreteWellLog")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.WellLogDiscrete, case_sensitive)

class GlobalWellLogs(PetrelObjectStoreBase):
    """A read-only collection GlobalWellLog objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_global_well_logs(), 
            lambda guid: petrelconnection._get_global_well_log_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="GlobalWellLog")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.WellLogGlobal, case_sensitive)

class GlobalObservedDataSets(PetrelObjectStoreBase):
    """A read-only collection GlobalObservedDataSet objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_global_observed_data_sets(),
            lambda guid: petrelconnection._get_global_observed_data_set(guid)
        )
    
    @_docstring_utils.get_by_name_decorator(object_type="GlobalObservedDataSet")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.ObservedDataSetGlobal, case_sensitive)

class DiscreteGlobalWellLogs(PetrelObjectStoreBase):
    """A read-only collection of DiscreteWellLog objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_global_well_logs(discrete = True),
            lambda guid: petrelconnection._get_global_well_log_by_guid(guid, discrete = True)
        )

    @_docstring_utils.get_by_name_decorator(object_type="DiscreteGlobalWellLog")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.WellLogGlobalDiscrete, case_sensitive)

class Wells(PetrelObjectStoreBase):
    """A read-only collection of Well objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_wells(),
            lambda guid: petrelconnection._get_well_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="Well")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.Borehole, case_sensitive)

class WellAttributes(PetrelObjectStoreBase):
    """A read-only collection of WellAttribute objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_well_attributes(),
            lambda guid: petrelconnection._get_well_attribute_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="WellAttribute")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.WellAttribute, case_sensitive)

class WellFolders(PetrelObjectStoreBase):
    """A read-only collection of WellFolder objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_well_folders(),
            lambda guid: petrelconnection._get_well_folder_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="WellFolder")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.BoreholeCollection, case_sensitive)

class GlobalWellLogFolders(PetrelObjectStoreBase):
    """A read-only collection of GlobalWellLogFolder objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_global_well_log_folders(),
            lambda guid: petrelconnection._get_globalwelllogfolder_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="GlobalWellLogFolder")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.WellLogFolderGlobal, case_sensitive)

class Folders(PetrelObjectStoreBase):
    """A read-only collection of Folder objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_folders(),
            lambda guid: petrelconnection._get_folder_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="Folder")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.Folder, case_sensitive)

class MarkerCollections(PetrelObjectStoreBase):
    """A read-only collection of MarkerCollection objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_markercollections(),
            lambda guid: petrelconnection._get_markercollection_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="MarkerCollection")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.MarkerCollection, case_sensitive)

class PointSets(PetrelObjectStoreBase):
    """A read-only collection of PointSet objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_pointsets(),
            lambda guid: petrelconnection._get_pointset_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="PointSet")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.PointSet, case_sensitive)
    
class FaultInterpretations(PetrelObjectStoreBase):
    """A read-only collection of FaultInterpretation objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_fault_interpretations(),
            lambda guid: petrelconnection._get_fault_interpretation_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="FaultInterpretation")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.FaultInterpretation, case_sensitive)
    
class InterpretationFolders(PetrelObjectStoreBase):
    """A read-only collection of InterpretationFolder objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_interpretation_folders(),
            lambda guid: petrelconnection._get_interpretation_folder_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="InterpretationFolder")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.InterpretationCollection, case_sensitive)

class PolylineSets(PetrelObjectStoreBase):
    """A read-only collection of PolylineSets objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_polylinesets(),
            lambda guid: petrelconnection._get_polylineset_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="PolylineSet")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.PolylineSet, case_sensitive)

class Wavelets(PetrelObjectStoreBase):
    """A read-only collection of Wavelet objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_wavelets(),
            lambda guid: petrelconnection._get_wavelet_by_guid(guid)
        )
    
    @_docstring_utils.get_by_name_decorator(object_type="Wavelet")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.Wavelet, case_sensitive)

class Workflows(PetrelObjectStoreBase):
    """A read-only collection of Workflow objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_workflows(),
            lambda guid: petrelconnection._get_workflow_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="Workflow")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.Workflow, case_sensitive)

class ReferenceVariables(PetrelObjectStoreBase):
    """A read-only collection of ReferenceVariable objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_reference_variables(),
            lambda guid: petrelconnection._get_reference_variable_by_guid(guid)
        )

class WellSurveys(PetrelObjectStoreBase):
    """A read-only collection of WellSurvey objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_object_from_ref(
            petrelconnection._find_well_surveys(),
            lambda obj: petrelconnection._pb_PetrelObjectGuid_to_pyobj_wrapper(
                utils.pb_PetrelObjectRef_to_grpcobj(obj, petrelconnection)
            )
        )

    @_docstring_utils.get_by_name_decorator(object_type="WellSurvey")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.WellSurvey, case_sensitive)


class ObservedDataObjects(PetrelObjectStoreBase):
    """A read-only collection of ObservedData objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_observed_data(),
            lambda guid: petrelconnection._get_observed_data_by_guid(guid)
        )

class ObservedDataSets(PetrelObjectStoreBase):
    """A read-only collection of ObservedDataSets objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_observed_data_sets(),
            lambda guid: petrelconnection._get_observed_data_set_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="ObservedDataSet")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.ObservedDataSet, case_sensitive)

class Zones(PetrelObjectStoreBase):
    """A read-only collection of Zone objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_zones(),
            lambda guid: petrelconnection._get_zone_by_guid(guid)
        )

class Segments(PetrelObjectStoreBase):
    """A read-only collection of Segment objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_segments(),
            lambda guid: petrelconnection._get_segment_by_guid(guid)
        )

class Templates(PetrelObjectStoreBase):
    """A read-only collection of Template objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_templates(),
            lambda guid: petrelconnection._get_template_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="Template")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.Template, case_sensitive)

class DiscreteTemplates(PetrelObjectStoreBase):
    """A read-only collection of DiscreteTemplate objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_discrete_templates(),
            lambda guid: petrelconnection._get_discrete_template_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="DiscreteTemplate")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.TemplateDiscrete, case_sensitive)

class CheckShots(PetrelObjectStoreBase):
    """A read-only collection of CheckShot objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_checkshots(),
            lambda guid: petrelconnection._get_checkshot_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="CheckShot")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.CheckShot, case_sensitive)

class SavedSearches(PetrelObjectStoreBase):
    """A read-only collection of SavedSearch objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_saved_searches(),
            lambda guid: petrelconnection._get_saved_search_by_guid(guid)
        )

    @_docstring_utils.get_by_name_decorator(object_type="SavedSearch")
    def get_by_name(self, name: str, case_sensitive: bool = False):
        return self._get_by_name_generic(name, WellKnownObjectDescription.SavedSearch, case_sensitive)