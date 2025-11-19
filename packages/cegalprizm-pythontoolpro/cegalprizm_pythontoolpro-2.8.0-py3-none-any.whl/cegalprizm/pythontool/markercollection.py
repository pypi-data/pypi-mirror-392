# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import typing
from cegalprizm.pythontool.parameter_validation import validate_name
import numpy as np
import pandas as pd
from cegalprizm.pythontool import exceptions, PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, _utils
from cegalprizm.pythontool import PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion
from cegalprizm.pythontool import _docstring_utils
from cegalprizm.pythontool.exceptions import PythonToolException
from cegalprizm.pythontool.borehole import Well
from cegalprizm.pythontool.grpc import utils
from cegalprizm.pythontool.grpc.markerattribute_grpc import MarkerAttributeGrpc
from cegalprizm.pythontool.grpc.markerstratigraphy_grpc import MarkerStratigraphyGrpc
from cegalprizm.pythontool.grpc.stratigraphyzone_grpc import StratigraphyZoneGrpc
from cegalprizm.pythontool.markerattribute import MarkerAttribute
from cegalprizm.pythontool.markerstratigraphy import MarkerStratigraphy, HorizonTypeEnum
from cegalprizm.pythontool.stratigraphyzone import StratigraphyZone
from cegalprizm.pythontool.exceptions import UserErrorException
from cegalprizm.pythontool.experimental import experimental_method
from typing import List
from warnings import warn

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.markercollection_grpc import MarkerCollectionGrpc
    from cegalprizm.pythontool import Folder

class MarkerCollection(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion):
    """A class holding information about a MarkerCollection."""

    def __init__(self, petrel_object_link: "MarkerCollectionGrpc"):
        super(MarkerCollection, self).__init__(petrel_object_link)
        self._markercollection_object_link = petrel_object_link
        
    def __str__(self) -> str:
        """A readable representation"""
        return 'MarkerCollection(petrel_name="{0}")'.format(self.petrel_name)

    @property
    def name(self):
        """
        .. warning::
            **Deprecated** - This property will be removed in Python Tool Pro 3.0. Use :attr:`petrel_name` instead.

        The name of the MarkerCollection.
        
        Returns:
            string: Name of the MarkerCollection as a string.
        """
        warn("name property will be removed in Python Tool Pro 3.0. Use petrel_name instead.", DeprecationWarning, stacklevel=2)
        return self._markercollection_object_link.GetName()
 
    @name.setter
    def name(self, value: str) -> None:
        warn("name property will be removed in Python Tool Pro 3.0. Use set_petrel_name() instead.", DeprecationWarning, stacklevel=2)
        self._markercollection_object_link.SetName(value)

    @_docstring_utils.move_docstring_decorator(object_type="MarkerCollection")
    def move(self, destination: "Folder"):
        if self.readonly:
            raise PythonToolException("MarkerCollection is readonly")
        _utils.verify_folder(destination)
        self._move(destination)

    def as_dataframe(self, 
                     include_unconnected_markers: bool = True, 
                     marker_stratigraphy: MarkerStratigraphy = None, 
                     well: Well = None,
                     include_petrel_index: bool = True,
                     wells_filter: List[Well] = None,
                     marker_stratigraphies_filter: List[MarkerStratigraphy] = None,
                     marker_attributes_filter: List[MarkerAttribute] = None) -> pd.DataFrame:
        """Gets a dataframe with information about Markers in the MarkerCollection.
        
        Args:
            include_unconnected_markers: Flag to include markers where the borehole does not exist in the project. Defaults to True.
            marker_stratigraphy: WARNING: This argument will be removed in the future. Use marker_stratigraphies_filter instead. Limit dataframe to include only markers for one specified MarkerStratigraphy (as returned by markercollection.stratigraphies). Defaults to None.
            well: WARNING: This argument will be removed in the future. Use wells_filter instead. Limit dataframe to include only markers for a specified Well (as returned by petrelconnection.wells). Defaults to None.
            include_petrel_index: Flag to include Petrel index (from Petrel spreadsheet) in the DataFrame. Defaults to True. Setting it to False may improve performance for a large MarkerCollection.
            wells_filter: Limit dataframe to include a subset of some Wells by supplying a list of :class:`Well`. By default this is None which will return data for all Wells.
            marker_stratigraphies_filter: Limit dataframe to include a subset of some MarkerStratigraphies by supplying a list of :class:`MarkerStratigraphy`. By default this is None which will return data for all MarkerStratigraphies.
            marker_attributes_filter: Limit dataframe to include a subset of some Attributes by supplying a list of :class:`MarkerAttribute`. By default this is None which will return all Attributes. Use an empty list to not include Attributes.

        Returns:
            Dataframe: A dataframe with Marker information, similar to the Well tops spreadsheet in Petrel.

        **Example**:

        Get a dataframe with information about all attributes for all Markers in the MarkerCollection

        .. code-block:: python

            mc = petrelconnection.markercollections["Input/Path/To/MarkerCollection"]
            df = mc.as_dataframe()

        **Example**:

        Get a dataframe with only basic information about all attributes for all Markers in the MarkerCollection. Use the marker_attributes_filter and pass a empty list.

        .. code-block:: python

            mc = petrelconnection.markercollections["Input/Path/To/MarkerCollection"]
            df = mc.as_dataframe(marker_attributes_filter=[])

        **Example**:

        Get a dataframe with information about specific wells. Supply a list of well objects to the wells_filter argument.

        .. code-block:: python

            my_well = petrelconnection.wells["Input/Path/To/Well"]
            my_well2 = petrelconnection.wells["Input/Path/To/Well2"]
            mc = petrelconnection.markercollections["Input/Path/To/MarkerCollection"]
            df = mc.as_dataframe(wells_filter=[my_well,my_well2])

        **Example**:

        Get a dataframe with only basic information for a specific well and two stratigraphies while skipping the Petrel index

        .. code-block:: python

            my_well = petrelconnection.wells["Input/Path/To/Well"]
            mc = petrelconnection.markercollections["Input/Path/To/MarkerCollection"]
            strat1 = mc.stratigraphies["First Stratigraphy"]
            strat2 = mc.stratigraphies["Second Stratigraphy"]
            df = mc.as_dataframe(include_petrel_index=False, 
                                 wells_filter=[my_well], 
                                 marker_stratigraphies_filter=[strat1, strat2],
                                 marker_attributes_filter=[])

        **Example**:

        Get a dataframe with basic information and the selected attributes for all Markers connected to a borehole that exists in the project

        .. code-block:: python

            mc = petrelconnection.markercollections["Input/Path/To/MarkerCollection"]
            attributes = []
            attributes.append(mc.attributes["Interpreter"])
            attributes.append(mc.attributes["Observation number"])
            df = mc.as_dataframe(include_unconnected_markers=False, marker_attributes_filter=attributes)
        """
        if marker_stratigraphy is not None:
            warn("The 'marker_stratigraphy' argument is deprecated and will be removed in Python Tool Pro version 3.0. Use 'marker_stratigraphies_filter' instead.", DeprecationWarning, stacklevel=2)
        if well is not None:
            warn("The 'well' argument is deprecated and will be removed in Python Tool Pro version 3.0. Use 'wells_filter' instead.", DeprecationWarning, stacklevel=2)
        if marker_stratigraphy is not None and marker_stratigraphies_filter is not None:
            raise ValueError("The marker_stratigraphy and marker_stratigraphies_filter arguments cannot be used at the same time")
        if well is not None and wells_filter is not None:
            raise ValueError("The well and wells_filter arguments cannot be used at the same time")
        stratigraphy_droids = self._get_stratigraphy_droids(marker_stratigraphy, marker_stratigraphies_filter)
        wells = _utils.get_wells(well, wells_filter)
        attribute_droids = self._get_attribute_droids(marker_attributes_filter)
        
        df = self._markercollection_object_link.GetDataFrameValues(include_unconnected_markers, stratigraphy_droids, wells, include_petrel_index, attribute_droids)
        return df
    
    def _as_dataframe_for_attribute(self, 
                                    attribute_droid: str, 
                                    include_unconnected_markers: bool = True, 
                                    marker_stratigraphies_filter: List[MarkerStratigraphy] = None,
                                    wells_filter: List[Well] = None) -> pd.DataFrame:
        
        stratigraphy_droids = self._get_stratigraphy_droids(marker_stratigraphies_filter=marker_stratigraphies_filter)
        wells = _utils.get_wells(wells_filter=wells_filter)
        df = self._markercollection_object_link.GetDataFrameValuesForAttribute(attribute_droid, include_unconnected_markers, stratigraphy_droids, wells)
        return df

    def _as_array_for_attribute(self, attribute_droid: str, include_unconnected_markers: bool = True, marker_stratigraphy: MarkerStratigraphy = None, well: Well = None) -> np.array:
        stratigraphy_droid = self._get_stratigraphy_droid(marker_stratigraphy)
        _utils.check_well(well)
        array = self._markercollection_object_link.GetArrayValuesForAttribute(attribute_droid, include_unconnected_markers, stratigraphy_droid, well)
        return array

    def _set_values_for_attribute(self, attribute_droid: str, data: np.array, include_unconnected_markers: bool, marker_stratigraphy: MarkerStratigraphy = None, well: Well = None) -> None:
        utils.check_input_contains_data(data)

        currentArray = self._as_array_for_attribute(attribute_droid, include_unconnected_markers, marker_stratigraphy, well)
        self._check_input_data_has_correct_length(data, len(currentArray))
        
        currentPropType = utils.GetPropTypeForValue(currentArray[0])
        utils.check_input_has_expected_data_type(data, currentPropType)

        indices = utils.create_indices(data)

        stratigraphy_droid = self._get_stratigraphy_droid(marker_stratigraphy)
        _utils.check_well(well)

        self._markercollection_object_link.SetPropertyValues(attribute_droid, indices, data, include_unconnected_markers, stratigraphy_droid, well)

    def add_marker(self, well: Well, marker_stratigraphy: MarkerStratigraphy, measured_depth: float):
        """Add a new Marker to the MarkerCollection. 
        For adding more than a few markers, it is recommended to use add_multiple_markers() which performs better on large amounts of data.
        
        Args:
            well: A Well object as returned from petrelconnection.wells.
            marker_stratigraphy: A MarkerStratigraphy object as returned by markercollection.stratigraphies.
            measured_depth: A float value as the measured depth of the new Marker

        Raises:
            PythonToolException: if the MarkerCollection is read-only
            TypeError: if the well parameter is not a Well object or marker_stratigraphy parameter is not a MarkerStratigraphy object
        """

        self._check_readonly()

        if marker_stratigraphy is None:
            raise TypeError("marker_stratigraphy must be a MarkerStratigraphy object as returned from markercollection.stratigraphies")

        stratigraphy_droid = self._get_stratigraphy_droid(marker_stratigraphy)

        if not isinstance(well, Well):
            raise TypeError("well argument must be a Well object as returned from petrelconnection.wells")
        
        self._markercollection_object_link.AddMarker(well, stratigraphy_droid, measured_depth)

    def add_multiple_markers(self, wells: 'np.array[Well]', marker_stratigraphies: 'np.array[MarkerStratigraphy]', measured_depths: 'np.array[float]'):
        """Add multiple new Markers to the MarkerCollection. This method performs better than add_marker() when adding larger amounts of data.
        Data input is supplied as numpy arrays. The array must all have the same length, and the data in the arrays must match by index.
        This means that the first marker added will be (wells[0], marker_stratigraphies[0], measured_depths[0]), and so on.
        
        Args:
            wells: A numpy array of Well objects, where each Well is an object as returned by petrelconnection.wells.
            marker_stratigraphies: A numpy array of MarkerStratigraphy objects, where each MarkerStratigraphy is an object as returned by markercollection.stratigraphies.
            measured_depths: A numpy array of float values as the measured depth of the new Markers.

        Raises:
            PythonToolException: if the MarkerCollection is read-only
            TypeError: If the input arrays are not numpy arrays
            ValueError: If the input arrays are not all of the same length, or if indivudal elements in the arrays are not of the correct type.
        
        **Example**:

        Add multiple markers to a MarkerCollection

        .. code-block:: python

            mc = petrelconnection.markercollections["Input/Path/To/MarkerCollection"]
            well1 = petrelconnection.wells["Input/Path/To/Well1"]
            well2 = petrelconnection.wells["Input/Path/To/Well2"]
            stratigraphy1 = mc.stratigraphies["Stratigraphy1"]
            stratigraphy2 = mc.stratigraphies["Stratigraphy2"]
            wells = np.array([well1, well2, well1, well2])
            stratigraphies = np.array([stratigraphy1, stratigraphy1, stratigraphy2, stratigraphy2])
            depths = np.array([1111.11, 1115.55, 2222.22, 2226.66])
            mc.add_multiple_markers(wells, stratigraphies, depths) 
        """
        self._check_readonly()
        if len(wells) != len(marker_stratigraphies) or len(wells) != len(measured_depths):
            raise ValueError("The input arrays must all be of the same length")
        if not isinstance(wells, np.ndarray) or not isinstance(marker_stratigraphies, np.ndarray) or not isinstance(measured_depths, np.ndarray):
            raise TypeError("The input arrays must all be numpy arrays")
        for well in wells:
            if not isinstance(well, Well):
                raise ValueError("The input array for wells must contain only Well objects as returned from petrelconnection.wells")
        strat_droids = []
        for strat in marker_stratigraphies:
            strat_droids.append(self._get_stratigraphy_droid(strat))

        self._markercollection_object_link.AddManyMarkers(wells, strat_droids, measured_depths)

    def add_attribute(self, data: 'np.array', name: str, data_type: str, include_unconnected_markers: bool = True, marker_stratigraphy: MarkerStratigraphy = None, well: Well = None) -> None:
        """Add a new MarkerAttribute to a MarkerCollection by specifying the data as a numpy array and the name and data_type of the attribute as strings.
           The include_unconnected_markers flag is used for verifying that the length of the provided array matches the expected amount of data. 
           If set to False the attribute will still be added to all markers, but with default values for all unconnected markers.
           If an empty array is passed in the attribute will be added to all markers with default values. For boolean attributes the default value is False.

        Args:
            data: A numpy array of attributes with format as returned by MarkerAttribute.as_array() 
            name: A string specifying the name of the new attribute
            data_type: A string specifying the data_type. Supported strings are: string | bool | continuous | discrete
            include_unconnected_markers: A boolean flag to include markers where the borehole does not exist in the project. Defaults to True.
            marker_stratigraphy: Limit array to include only markers for one specified MarkerStratigraphy (as returned by markercollection.stratigraphies). Defaults to None.
            well: Limit array to include only markers for a specified Well (as returned by petrelconnection.wells). Defaults to None.

        Raises:
            PythonToolException: if the MarkerCollection is read-only
            ValueError: if the data_type is not 'string | bool | continuous | discrete'
            UserErrorException: if column already exist

        **Example**:

        Add a new continuous attribute to a markercollection and set values only for the connected markers.

        .. code-block:: python

          import numpy as np
          new_attribute_values = np.array([1.1, 2.2, 3.3])
          markercollection.add_attribute(new_attribute_values, 'MyNewAttribute', 'continuous', False)
        """
        self._check_readonly()

        expectedPropType = utils.GetPropTypeFromString(data_type)
        if expectedPropType is None:
            raise ValueError("Unsupported data_type, supported values are: string | bool | continuous | discrete")

        if len(data) > 0:
            stratigraphy_droid = self._get_stratigraphy_droid(marker_stratigraphy)
            _utils.check_well(well)
            firstAttribute = next(iter(self.attributes))
            firstAttributeArray = self._as_array_for_attribute(firstAttribute._droid, include_unconnected_markers, marker_stratigraphy, well)
            self._check_input_data_has_correct_length(data, len(firstAttributeArray))
            utils.check_input_has_expected_data_type(data, expectedPropType)
            indices = utils.create_indices(data)
            ok = self._markercollection_object_link.AddAttribute(name, indices, data, include_unconnected_markers, stratigraphy_droid, well)
        else:
            ok = self._markercollection_object_link.AddEmptyAttribute(name, expectedPropType)
      
        if not ok:
            raise UserErrorException("Something went wrong while adding the attribute.")

    @validate_name(param_name="zone_name")
    @validate_name(param_name="horizon_name")
    def create_zone_and_horizon_above(self, reference_object: typing.Union[StratigraphyZone, MarkerStratigraphy],
                                            zone_name: str = "", 
                                            horizon_name: str = "",
                                            horizon_type: typing.Union[str, HorizonTypeEnum] = "Conformable") -> typing.Tuple[StratigraphyZone, MarkerStratigraphy]:
        """Create a new zone and horizon above the given reference object. The reference object can be either a StratigraphyZone or a MarkerStratigraphy where is_horizon is True.
        If the reference object is a StratigraphyZone, the new horizon will be created directly above the reference zone, and the new zone will be created above the newly created horizon.
        If the reference object is a horizon MarkerStratigraphy the new zone will be created above the reference horizon, and the new horizon will be created above the newly created zone.
        The names of the new objects can be set using the optional zone_name and horizon_name arguments. If not provided, default names will be used.
        The type of the horizon can be set using the optional horizon_type argument. If not provided, the type will be set to "Conformable".
        The new zone and horizon are returned as a tuple of (StratigraphyZone, MarkerStratigraphy) objects.

        Note:
            Only MarkerStratigraphy objects representing horizons can be used as reference objects. Providing a MarkerStratigraphy object representing a fault or other surface type will raise an exception.

        Args:
            reference_object: A StratigraphyZone object representing a zone or a MarkerStratigraphy object representing a horizon. The new zone and horizon will be created above this object.
            zone_name (optional): A string specifying the name of the new zone. If not provided, a default name will be used.
            horizon_name (optional): A string specifying the name of the new horizon. If not provided, a default name will be used.
            horizon_type (optional): A string or HorizonTypeEnum specifying the type of the new horizon. Valid inputs are "Conformable", "Erosional", "Base", "Discontinuous". Defaults to "Conformable".

        Returns:
            The newly created zone and horizon as a tuple of :class:`StratigraphyZone` and :class:`MarkerStratigraphy` objects.

        Raises:
            TypeError: If the zone_name or horizon_name arguments are not string objects.
            ValueError: If the zone_name or horizon_name arguments are not valid string objects.
            PythonToolException: If the MarkerCollection is read-only.
            PythonToolException: If the reference object is a MarkerStratigraphy object not representing a horizon.
            TypeError: If the reference object is not a StratigraphyZone or MarkerStratigraphy object.
            TypeError: If the horizon_type argument is not a string or HorizonTypeEnum object.
            ValueError: If the horizon_type argument is not one of the valid types.

        **Example**:

        Create a zone and horizon above a reference zone using default names

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            reference_zone = mc.zones["ReferenceZone"]
            new_zone, new_horizon = mc.create_zone_and_horizon_above(reference_zone)

        **Example**:

        Create a zone and horizon above a reference horizon using custom names and horizon type

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            reference_horizon = mc.stratigraphies["ReferenceHorizon"]
            new_zone, new_horizon = mc.create_zone_and_horizon_above(reference_horizon, zone_name="NewZone", horizon_name="NewHorizon", horizon_type="Erosional")

        """
        self._check_readonly()
        self._check_reference_object(reference_object)
        horizon_type = self._check_horizon_type(horizon_type)

        zone_grpc, horizon_grpc = self._markercollection_object_link.CreateZoneAndHorizonAboveOrBelow(True, reference_object, zone_name, horizon_name, horizon_type)

        if zone_grpc is not None:
            zone = StratigraphyZone(zone_grpc, self)
        if horizon_grpc is not None:
            horizon = MarkerStratigraphy(horizon_grpc, self)
        return zone, horizon

    @validate_name(param_name="zone_name")
    @validate_name(param_name="horizon_name")
    def create_zone_and_horizon_below(self, reference_object: typing.Union[StratigraphyZone, MarkerStratigraphy],
                                            zone_name: str = "", 
                                            horizon_name: str = "",
                                            horizon_type: typing.Union[str, HorizonTypeEnum] = "Conformable") -> typing.Tuple[StratigraphyZone, MarkerStratigraphy]:
        """Create a new zone and horizon below the given reference object. The reference object can be either a StratigraphyZone or a MarkerStratigraphy where is_horizon is True.
        If the reference object is a StratigraphyZone, the new horizon will be created directly below the reference zone, and the new zone will be created below the newly created horizon.
        If the reference object is a horizon MarkerStratigraphy the new zone will be created below the reference horizon, and the new horizon will be created below the newly created zone.
        The names of the new objects can be set using the optional zone_name and horizon_name arguments. If not provided, default names will be used.
        The type of the horizon can be set using the optional horizon_type argument. If not provided, the type will be set to "Conformable".
        The new zone and horizon are returned as a tuple of (StratigraphyZone, MarkerStratigraphy) objects.

        Note:
            Only MarkerStratigraphy objects representing horizons can be used as reference objects. Providing a MarkerStratigraphy object representing a fault or other surface type will raise an exception.

        Args:
            reference_object: A StratigraphyZone object representing a zone or a MarkerStratigraphy object representing a horizon. The new zone and horizon will be created below this object.
            zone_name (optional): A string specifying the name of the new zone. If not provided, a default name will be used.
            horizon_name (optional): A string specifying the name of the new horizon. If not provided, a default name will be used.
            horizon_type (optional): A string or HorizonTypeEnum specifying the type of the new horizon. Valid inputs are "Conformable", "Erosional", "Base", "Discontinuous". Defaults to "Conformable".

        Returns:
            The newly created zone and horizon as a tuple of :class:`StratigraphyZone` and :class:`MarkerStratigraphy` objects.

        Raises:
            TypeError: If the zone_name or horizon_name arguments are not string objects.
            ValueError: If the zone_name or horizon_name arguments are not valid string objects.
            PythonToolException: If the MarkerCollection is read-only.
            PythonToolException: If the reference object is a MarkerStratigraphy object not representing a horizon.
            TypeError: If the reference object is not a StratigraphyZone or MarkerStratigraphy object.
            TypeError: If the horizon_type argument is not a string or HorizonTypeEnum object.
            ValueError: If the horizon_type argument is not one of the valid types.

        **Example**:

        Create a zone and horizon below a reference zone using default names

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            reference_zone = mc.zones["ReferenceZone"]
            new_zone, new_horizon = mc.create_zone_and_horizon_below(reference_zone)

        **Example**:

        Create a zone and horizon below a reference horizon using custom names and horizon type

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            reference_horizon = mc.stratigraphies["ReferenceHorizon"]
            new_zone, new_horizon = mc.create_zone_and_horizon_below(reference_horizon, zone_name="NewZone", horizon_name="NewHorizon", horizon_type="Erosional")

        """
        self._check_readonly()
        self._check_reference_object(reference_object)
        horizon_type = self._check_horizon_type(horizon_type)

        zone_grpc, horizon_grpc = self._markercollection_object_link.CreateZoneAndHorizonAboveOrBelow(False, reference_object, zone_name, horizon_name, horizon_type)

        if zone_grpc is not None:
            zone = StratigraphyZone(zone_grpc, self)
        if horizon_grpc is not None:
            horizon = MarkerStratigraphy(horizon_grpc, self)
        return zone, horizon

    @validate_name(param_name="zone_name_bottom")
    @validate_name(param_name="horizon_name")
    @validate_name(param_name="zone_name_top")
    def create_zones_and_horizon_inside(self, reference_zone: StratigraphyZone,
                                         zone_name_bottom: str = "",
                                         horizon_name: str = "",
                                         zone_name_top: str = "",
                                         horizon_type: typing.Union[str, HorizonTypeEnum] = "Conformable") -> typing.Tuple[StratigraphyZone, MarkerStratigraphy, StratigraphyZone]:
        """Create two new zones and a new horizon inside the given reference zone. The new zones will be created above and below the new horizon. The reference zone must be a StratigraphyZone object.
        The names of the new objects can be set using the optional zone_name_bottom, horizon_name and zone_name_top arguments. If not provided, default names will be used.
        The type of the horizon can be set using the optional horizon_type argument. If not provided, the type will be set to "Conformable".
        The new zones and horizon are returned as a tuple of (StratigraphyZone, MarkerStratigraphy, StratigraphyZone) objects, with the bottom zone first and the top zone last.

        Note:
            Calling this method on a zone that already contains subzones is not supported and will raise an exception. In this case use either create_zone_and_horizon_above() or create_zone_and_horizon_below() instead.

        Args:
            reference_zone: A StratigraphyZone object representing the reference zone. The new zones and horizon will be created inside this zone.
            zone_name_bottom (optional): A string specifying the name of the new bottom zone. If not provided, a default name will be used.
            horizon_name (optional): A string specifying the name of the new horizon. If not provided, a default name will be used.
            zone_name_top (optional): A string specifying the name of the new top zone. If not provided, a default name will be used.
            horizon_type (optional): A string or HorizonTypeEnum specifying the type of the new horizon. Valid inputs are "Conformable", "Erosional", "Base", "Discontinuous". Defaults to "Conformable".

        Returns:
            The newly created bottom zone, horizon and top zone as a tuple of :class:`StratigraphyZone`, :class:`MarkerStratigraphy` and :class:`StratigraphyZone` objects.

        Raises:
            TypeError: If the zone_name_bottom, horizon_name or zone_name_top arguments are not string objects.
            ValueError: If the zone_name_bottom, horizon_name or zone_name_top arguments are not valid string objects.
            PythonToolException: If the MarkerCollection is read-only.
            TypeError: If the reference_zone argument is not a StratigraphyZone object.
            TypeError: If the horizon_type argument is not a string or HorizonTypeEnum object.
            ValueError: If the horizon_type argument is not one of the valid types.
            UserErrorException: If the reference zone already contains subzones.

        **Example**:

        Create two zones and a horizon inside a reference zone using default names

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            reference_zone = mc.zones["ReferenceZone"]
            zone_bottom, horizon, zone_top = mc.create_zones_and_horizon_inside(reference_zone)

        **Example**:

        Create two zones and a horizon inside a reference zone using custom names and horizon type

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            reference_zone = mc.zones["ReferenceZone"]
            zone_bottom, horizon, zone_top = mc.create_zones_and_horizon_inside(reference_zone, zone_name_bottom="NewBottomZoneInside", horizon_name="NewHorizonInside", zone_name_top="NewTopZoneInside", horizon_type="Erosional")

        """
        self._check_readonly()
        if not isinstance(reference_zone, StratigraphyZone):
            raise TypeError("reference_zone must be a StratigraphyZone object")
        horizon_type = self._check_horizon_type(horizon_type)

        zone_bottom_grpc, horizon_grpc, zone_top_grpc = self._markercollection_object_link.CreateZonesAndHorizonInside(reference_zone, zone_name_bottom, horizon_name, zone_name_top, horizon_type)

        if zone_bottom_grpc is not None:
            zone_bottom = StratigraphyZone(zone_bottom_grpc, self)
        if horizon_grpc is not None:
            horizon = MarkerStratigraphy(horizon_grpc, self)
        if zone_top_grpc is not None:
            zone_top = StratigraphyZone(zone_top_grpc, self)
        return zone_bottom, horizon, zone_top

    @validate_name(param_name="zone_name")
    @validate_name(param_name="horizon_name")
    def create_zone_and_horizon(self, zone_name: str = "",
                                      horizon_name: str = "",
                                      horizon_type: typing.Union[str, HorizonTypeEnum] = "Conformable") -> typing.Union[MarkerStratigraphy, typing.Tuple[StratigraphyZone, MarkerStratigraphy]]:
        """Create either the first horizon in a MarkerCollection or, if a horizon already exists, create a new zone and horizon at the bottom of the stratigraphy.
        The names of the new objects can be set using the optional zone_name and horizon_name arguments. If not provided, default names will be used.
        The type of the horizon can be set using the optional horizon_type argument. If not provided, the type will be set to "Conformable".
        If the markercollection did not contain any stratigraphy only the newly created horizon will be returned.
        If the markercollection already contained stratigraphy, the new zone and horizon will be returned as a tuple of (StratigraphyZone, MarkerStratigraphy) objects.

        Args:
            zone_name (optional): A string specifying the name of the new zone. If not provided, a default name will be used. If creating the first horizon, this argument is ignored.
            horizon_name (optional): A string specifying the name of the new horizon. If not provided, a default name will be used.
            horizon_type (optional): A string or HorizonTypeEnum specifying the type of the new horizon. Valid inputs are "Conformable", "Erosional", "Base", "Discontinuous". Defaults to "Conformable".

        Returns:
            The newly created horizon as a :class:`MarkerStratigraphy` object if the markercollection did not contain any stratigraphy.
            A tuple of :class:`StratigraphyZone` and :class:`MarkerStratigraphy` objects if the markercollection already contained stratigraphy.

        Raises:
            TypeError: If the zone_name or horizon_name arguments are not string objects.
            ValueError: If the zone_name or horizon_name arguments are not valid string objects.
            PythonToolException: If the MarkerCollection is read-only.
            TypeError: If the horizon_type argument is not a string or HorizonTypeEnum object.
            ValueError: If the horizon_type argument is not one of the valid types.
        
        **Example**:

        Create a named horizon of type "Erosional" in a MarkerCollection that does not contain any stratigraphy

        .. code-block:: python

            from cegalprizm.pythontool import HorizonTypeEnum
            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            horizon = mc.create_zone_and_horizon(horizon_name="FirstHorizon", horizon_type=HorizonTypeEnum.Erosional)

        **Example**:

        Create two horizons and a zone with default names and type in a MarkerCollection that does not contain any stratigraphy

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            first_horizon = mc.create_zone_and_horizon()
            zone, second_horizon = mc.create_zone_and_horizon()

        """
        
        self._check_readonly()
        horizon_type = self._check_horizon_type(horizon_type)

        zone_grpc, horizon_grpc = self._markercollection_object_link.CreateZoneAndHorizon(zone_name, horizon_name, horizon_type)

        if horizon_grpc is not None:
            horizon = MarkerStratigraphy(horizon_grpc, self)
        if zone_grpc is not None:
            zone = StratigraphyZone(zone_grpc, self)
            return zone, horizon
        return horizon

    def stratigraphy_hierarchy(self, include_subzones: bool = True, print_hierarchy: bool = False) -> typing.List[typing.Union[MarkerStratigraphy, StratigraphyZone]]:
        """Retrieve the stratigraphy hierarchy of the MarkerCollection as a list of MarkerStratigraphy horizons and StratigraphyZone objects.
        The order of the list will reflect the order seen in the Stratigraphy folder in Petrel. By default, child objects are included in the list, and the order is the same as with all nodes expanded in the Petrel UI.
        If include_subzones is set to False, only the top-level objects will be included in the list. The structure can be explored further by using the 'children' property of the StratigraphyZone objects.
        For a quick overview of the hierarchy, the print_hierarchy arugument can be set to True. This will print the hierarchy to the console before returning the list.

        **Example**:
        
        Get the stratigraphy hierarchy of a MarkerCollection inlcuding subzones and print the structure to the console.

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            hierarchy = mc.stratigraphy_hierarchy(include_subzones=True, print_hierarchy=True)
            >> ├── TopHorizon
            >> ├── TopZone
            >> │   ├── SubzoneTop
            >> │   ├── SubHorizon
            >> |   └── SubZoneBottom
            >> └── BottomHorizon

            print(hierarchy)
            >> [MarkerStratigraphy("TopHorizon"),
            >>  StratigraphyZone("TopZone"),
            >>  StratigraphyZone("SubzoneTop"),
            >>  MarkerStratigraphy("SubHorizon"),
            >>  StratigraphyZone("SubZoneBottom"),
            >>  MarkerStratigraphy("BottomHorizon")]

        **Example**:

        Get the stratigraphy hierarchy of a MarkerCollection excluding subzones and print the structure to the console. Then use the StratigraphyZone.children property to explore the structure further.

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            hierarchy = mc.stratigraphy_hierarchy(include_subzones=False, print_hierarchy=True)
            >> ├── TopHorizon
            >> ├── TopZone
            >> └── BottomHorizon

            print(hierarchy)
            >> [MarkerStratigraphy("TopHorizon"),
            >>  StratigraphyZone("TopZone"),
            >>  MarkerStratigraphy("BottomHorizon")]

            zone = hierarchy[1]
            print(zone.children)
            >> [StratigraphyZone("SubzoneTop"),
            >>  MarkerStratigraphy("SubHorizon"),
            >>  StratigraphyZone("SubZoneBottom")]

        Args:
            include_subzones (optional): A boolean flag to include subzones in the hierarchy. Defaults to True.
            print_hierarchy (optional): A boolean flag to print the hierarchy structure to the console. Defaults to False.

        Returns:
            A list of :class:`MarkerStratigraphy` and :class:`StratigraphyZone` objects representing the stratigraphy hierarchy of the MarkerCollection.
        """
        return self._markercollection_object_link.GetHorizonsAndZonesInOrder(self, include_subzones, print_hierarchy)


    def _check_horizon_type(self, horizon_type: typing.Union[str, HorizonTypeEnum]) -> str:
        """Check if the horizon_type is a valid type and return it as a string."""
        if not isinstance(horizon_type, (str, HorizonTypeEnum)):
            raise TypeError("horizon_type must be a string or HorizonTypeEnum")
        if isinstance(horizon_type, HorizonTypeEnum):
            horizon_type = horizon_type.value
        if horizon_type.lower() not in ["conformable", "erosional", "base", "discontinuous"]:
            raise ValueError("horizon_type must be one of the following: 'Conformable', 'Erosional', 'Base', 'Discontinuous'")
        return horizon_type

    def _check_readonly(self) -> None:
        """Check if the MarkerCollection is read-only."""
        if self.readonly:
            raise exceptions.PythonToolException("MarkerCollection is readonly")

    def _check_reference_object(self, reference_object: typing.Union[StratigraphyZone, MarkerStratigraphy]) -> None:
        if not isinstance(reference_object, (StratigraphyZone, MarkerStratigraphy)):
            raise TypeError("reference_object must be a StratigraphyZone or MarkerStratigraphy object")
        if isinstance(reference_object, MarkerStratigraphy) and not reference_object.is_horizon:
            raise exceptions.PythonToolException("reference_object must be a MarkerStratigraphy object representing a horizon")

    @property
    def attributes(self) -> typing.Iterable[MarkerAttribute]:
        """Python iterator with the MarkerAttribute objects for the MarkerCollection.

        Use to retrieve the attributes :class:`cegalprizm.pythontool.MarkerAttribute` from the MarkerCollection.
        Attributes can be iterated over, or accessed by index or name.
        Note that in the case of duplicate names, the unique name must be used to retrieve the attribute by name. (See example below)
        
        **Example**:

        Retrieve the first attribute from the MarkerCollection

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            first_attribute = mc.attributes[0]

        **Example**:

        Retrieve a named attribute from the MarkerCollection

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            my_attribute = mc.attributes["MyAttribute"]

        **Example**:

        Retrieve a named attribute from the MarkerCollection where multiple attributes have the same name

        .. code-block:: python

            # As an example, imagine Petrel has two attributes named "Custom". 
            # In PTP they will get a suffix added as a unique name, "Custom (1) and "Custom (2)"
            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]

            custom1 = mc.attributes["Custom (1)"]
            print(custom1) 
            >> 'MarkerAttribute(unique_name="Custom (1)")'
            print(custom1.petrel_name)
            >> 'Custom'

            custom2 = mc.attributes["Custom (2)"]
            print(custom2)
            >> 'MarkerAttribute(unique_name="Custom (2)")'
            print(custom2.petrel_name)
            >> 'Custom'

            # In this example, the line below will raise a KeyError
            custom = mc.attributes["Custom"]
        
        Returns:
            An iterable collection of :class:`cegalprizm.pythontool.MarkerAttribute` objects for the MarkerCollection.
        """
        return MarkerAttributes(self)

    @property
    def stratigraphies(self) -> dict:
        """ Gets an iterator with the MarkerStratigraphy objects for the MarkerCollection.

        Use to retrieve the stratigraphies :class:`MarkerStratigraphy` from the MarkerCollection.
        MarkerStratigraphies can be iterated over, or accessed by index or name.
        Note that in the case of duplicate names, the unique name must be used to retrieve the MarkerStratigraphy by name.

        **Example**:

        Retrieve MarkerStratigraphy objects from the MarkerCollection

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]

            # Retrieve all MarkerStratigraphies
            all_stratigraphies = [stratigraphy for stratigraphy in mc.stratigraphies]

            # Retrieve the first MarkerStratigraphy
            first_stratigraphy = mc.stratigraphies[0]
            
            # Retrieve a named MarkerStratigraphy
            my_stratigraphy = mc.stratigraphies["MyStratigraphy"]
        
        Returns:
            An iterable collection of :class:`MarkerStratigraphy` objects for a markercollection.
        """
        return MarkerStratigraphies(self)

    @property
    def zones(self) -> dict:
        """ Gets an iterator with the StratigraphyZone objects for the MarkerCollection.

        Use to retrieve the zones :class:`StratigraphyZone` from the MarkerCollection.
        StratigraphyZones can be iterated over, or accessed by index or name.
        Note that in the case of duplicate names, the unique name must be used to retrieve the StratigraphyZone by name.

        **Example**:

        Retrieve StratigraphyZone objects from the MarkerCollection

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            
            # Retrieve all StratigraphyZones
            all_zones = [zone for zone in mc.zones]

            # Retrieve the first StratigraphyZone
            first_zone = mc.zones[0]

            # Retrieve a named StratigraphyZone
            my_zone = mc.zones["MyZone"]

        Returns:
            An iterable collection of :class:`StratigraphyZone` objects for a markercollection.
        """
        return StratigraphyZones(self)

    @property
    def horizons(self) -> typing.Iterable[MarkerStratigraphy]:
        """Gets an iterable collection of the horizons in the MarkerCollection as :class:`MarkerStratigraphy` objects.

        Use to retrieve the :class:`MarkerStratigraphy` objects with horizons from the MarkerCollection, skipping any non-horizons.
        Horizons can be iterated over, or accessed by index or name.
        Note that in the case of duplicate names, the unique name must be used to retrieve the MarkerStratigraphy horizon by name.

        **Example**:

        Retrieve all horizons from the MarkerCollection

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Path/To/MarkerCollection"]
            all_horizons = [horizon for horizon in mc.horizons]

        Returns:
            An iterable collection of :class:`MarkerStratigraphy` objects that are horizons in the MarkerCollection.
        """
        return StratigraphyHorizons(self)

    @property
    def parent_folder(self) -> typing.Union["Folder", None]:
        """Returns the parent folder of this MarkerCollection in Petrel. Returns None if the object is the Input root.

        Returns:
            :class:`Folder` or None: The parent folder of the MarkerCollection, or None if the object is located at the root level.

        **Example**:

        .. code-block:: python

            mc = petrel_connection.markercollections["Input/Folder/Markers"]
            mc.parent_folder
            >> Folder(petrel_name="Folder")
        """
        return self._parent_folder

    ## Private methods
    @experimental_method
    def _get_marker_droid(self, well: Well, marker_stratigraphy: MarkerStratigraphy, measured_depth: float) -> str:
        """
        Get the droid as a string for a specified marker. If multiple matches the first droid is returned.
        """
        stratigraphy_droid = self._get_stratigraphy_droid(marker_stratigraphy)
        return self._markercollection_object_link.GetMarkerDroid(well, stratigraphy_droid, measured_depth)
    
    @experimental_method
    def _delete_marker(self, marker_droid: str):
        """
        Delete a marker from the MarkerCollection by supplying the droid as a string.
        """
        self._markercollection_object_link.DeleteMarker(marker_droid)

    @experimental_method
    def _delete_multiple_markers(self, wells: 'np.array[Well]', marker_stratigraphies: 'np.array[MarkerStratigraphy]', measured_depths: 'np.array[float]'):
        """
        Delete multiple markers from the MarkerCollection by supplying lists of Wells, MarkerStratigraphes and depths.
        The numpy arrays must all be of the same length.
        """
        if len(wells) != len(marker_stratigraphies) or len(wells) != len(measured_depths):
            raise ValueError("The input arrays must all be of the same length")
        if not isinstance(wells, np.ndarray) or not isinstance(marker_stratigraphies, np.ndarray) or not isinstance(measured_depths, np.ndarray):
            raise TypeError("The input arrays must all be numpy arrays")
        strat_droids = []
        for strat in marker_stratigraphies:
            strat_droids.append(self._get_stratigraphy_droid(strat))
        self._markercollection_object_link.DeleteManyMarkers(wells, strat_droids, measured_depths)

    ## Helper methods
    def _check_input_data_has_correct_length(self, data: np.array, requiredLength) -> None:
        if len(data) != requiredLength:
            raise ValueError("Number of elements in array must match number of markers in markercollection")
    
    def _get_stratigraphy_droid(self, marker_stratigraphy: MarkerStratigraphy) -> str:
        stratigraphy_droid = ""
        if marker_stratigraphy is not None:
            if not isinstance(marker_stratigraphy, MarkerStratigraphy):
                raise ValueError("Each marker_stratigraphy must be a MarkerStratigraphy object as returned from markercollection.stratigraphies")
            stratigraphy_droid = marker_stratigraphy._droid
        return stratigraphy_droid
    
    def _get_stratigraphy_droids(self, marker_stratigraphy: MarkerStratigraphy = None, marker_stratigraphies_filter: list = None) -> list:
        if marker_stratigraphy is None and marker_stratigraphies_filter is None:
            return [""]
        if marker_stratigraphies_filter is not None:
            if not isinstance(marker_stratigraphies_filter, list):
                raise TypeError("marker_stratigraphies_filter must be a list of MarkerStratigraphy objects as returned from markercollection.stratigraphies")
            droids = []
            for stratigraphy in marker_stratigraphies_filter:
                droids.append(self._get_stratigraphy_droid(stratigraphy))
            return droids
        if marker_stratigraphy is not None:
            return [self._get_stratigraphy_droid(marker_stratigraphy)]
    
    def _get_attribute_droids(self, marker_attributes: list) -> list:
        if marker_attributes is None:
            return ["GetAllAttributes"]
        droids = []
        for attribute in marker_attributes:
            if not isinstance(attribute, MarkerAttribute):
                raise TypeError("All entries in marker_attributes_filter must be a MarkerAttribute object as returned from markercollection.attributes")
            droids.append(attribute._droid)
        return droids

class MarkerStratigraphies(object):
    """An iterable collection of :class:`MarkerStratigraphy` objects for the MarkerStratigraphies in the MarkerCollection"""

    def __init__(self, parent):
        self._parent = parent
        if isinstance(parent, MarkerCollection):
            mc = parent
            petrel_connection = parent._petrel_object_link._plink
            grpcs = [
                MarkerStratigraphyGrpc(petrelObjectRef.guid, petrel_connection, petrelObjectRef.sub_type, petrelObjectRef.petrel_name)
                for petrelObjectRef in mc._markercollection_object_link.GetStratigraphies()
            ]
            self._marker_stratigraphies = [
                MarkerStratigraphy(grpc, mc) for grpc in grpcs
            ]
        else:
            raise TypeError("Parent must be MarkerCollection")

    def __len__(self) -> int:
        return len(self._marker_stratigraphies)

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self._marker_stratigraphies)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._marker_stratigraphies[key]
        elif isinstance(key, str):
            stratigraphies = []
            for strat in self._marker_stratigraphies:
                if strat._get_name() == key:
                    stratigraphies.append(strat)
            
            if len(stratigraphies) == 1:
                return stratigraphies[0]
            else:
                raise KeyError("Cannot find unique stratigraphy name " + key)

    def __str__(self) -> str:
        return 'MarkerStratigraphies({0}="{1}")'.format(self._parent._petrel_object_link._sub_type, self._parent)

    def __repr__(self) -> str:
        return str(self)

class StratigraphyHorizons(MarkerStratigraphies):
    """An iterable collection of :class:`MarkerStratigraphy` objects for the StratigraphyHorizons in the MarkerCollection"""

    def __init__(self, parent):
        super(StratigraphyHorizons, self).__init__(parent)
        if not isinstance(parent, MarkerCollection):
            raise TypeError("Parent must be MarkerCollection")
        self._marker_stratigraphies = [strat for strat in self._marker_stratigraphies if strat.is_horizon]
    
    def __str__(self) -> str:
        return 'StratigraphyHorizons({0}="{1}")'.format(self._parent._petrel_object_link._sub_type, self._parent)

    def __getitem__(self, key):
        try:
            return super(StratigraphyHorizons, self).__getitem__(key)
        except KeyError:
            raise KeyError("Cannot find unique horizon name " + key)


class MarkerAttributes(object):
    """An iterable collection of :class:`MarkerAttribute` objects for the MarkerAttributes in the MarkerCollection"""

    def __init__(self, parent):
        self._parent = parent
        if isinstance(parent, MarkerCollection):
            mc = parent
            petrel_connection = parent._petrel_object_link._plink
            grpcs = [
                MarkerAttributeGrpc(petrelObjectRef.guid, petrel_connection, petrelObjectRef.petrel_name)
                for petrelObjectRef in mc._markercollection_object_link.GetAttributes()
            ]
            self._marker_attributes = [
                MarkerAttribute(grpc, mc)
                for grpc in grpcs
            ]
            self._marker_attributes_dict = {attr._get_name(): attr for attr in self._marker_attributes}
        else:
            raise TypeError("Parent must be MarkerCollection")

    def __len__(self) -> int:
        return len(self._marker_attributes)

    def __iter__(self) -> typing.Iterable[MarkerAttribute]:
        return iter(self._marker_attributes)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._marker_attributes[key]
        elif isinstance(key, str):
            return self._marker_attributes_dict[key]

    def __str__(self) -> str:
        return 'MarkerAttributes({0}="{1}")'.format(self._parent._petrel_object_link._sub_type, self._parent)

    def __repr__(self) -> str:
        return str(self)

class StratigraphyZones(object):
    """An iterable collection of :class:`StratigraphyZone` objects for the Stratigraphy Zones in the MarkerCollection"""

    def __init__(self, parent):
        self._parent = parent
        if isinstance(parent, MarkerCollection):
            mc = parent
            petrel_connection = parent._petrel_object_link._plink
            grpcs = [
                StratigraphyZoneGrpc(petrelObjectRef.guid, petrel_connection, petrelObjectRef.petrel_name)
                for petrelObjectRef in mc._markercollection_object_link.GetStratigraphyZones()
            ]
            self._stratigraphy_zones = [StratigraphyZone(grpc, mc) for grpc in grpcs]
            self._stratigraphy_zones_dict = {zone._get_name(): zone for zone in self._stratigraphy_zones}
        else:
            raise TypeError("Parent must be MarkerCollection")

    def __len__(self) -> int:
        return len(self._stratigraphy_zones)

    def __iter__(self) -> typing.Iterable[StratigraphyZone]:
        return iter(self._stratigraphy_zones)
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self._stratigraphy_zones[key]
        elif isinstance(key, str):
            return self._stratigraphy_zones_dict[key]
        raise KeyError("StratigraphyZones can only be indexed by int or str")
    
    def __str__(self) -> str:
        return 'StratigraphyZones({0}="{1}")'.format(self._parent._petrel_object_link._sub_type, self._parent)

    def __repr__(self) -> str:
        return str(self)