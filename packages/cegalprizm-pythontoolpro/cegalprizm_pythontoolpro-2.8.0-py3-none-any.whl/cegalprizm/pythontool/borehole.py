# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import typing
from cegalprizm.pythontool.grpc import petrelinterface_pb2, utils
from cegalprizm.pythontool.parameter_validation import validate_name
import pandas as pd
from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion
from cegalprizm.pythontool import welllog, _docstring_utils, _utils
from cegalprizm.pythontool.observeddata import ObservedDataSet, ObservedDataSets
from cegalprizm.pythontool.wellsurvey import WellSurvey, WellSurveys
from cegalprizm.pythontool.wellsymboldescription import WellSymbolDescription
from cegalprizm.pythontool import petrellink
from cegalprizm.pythontool.completionsset import CompletionsSet
from cegalprizm.pythontool.exceptions import PythonToolException
from cegalprizm.pythontool.experimental import experimental_class, experimental_property
from cegalprizm.pythontool.grpc.completionsset_grpc import CompletionsSetGrpc
from cegalprizm.pythontool.wellattribute import WellAttribute, WellAttributeFilterEnum, WellAttributeInstance
import collections
import datetime
from typing import List, Union

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.borehole_grpc import BoreholeGrpc
    from cegalprizm.pythontool import WellFolder

class Well(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion):
    """A class holding information about a well.

    Trajectory information can be derived via a :class:`cegalprizm.pythontool.LogSamples` 
    - no direct trajectory information is maintained here."""

    def __init__(self, petrel_object_link: "BoreholeGrpc"):
        super(Well, self).__init__(petrel_object_link)
        self._borehole_object_link = petrel_object_link
    
    def __str__(self) -> str:
        """A readable representation"""
        return 'Well(petrel_name="{0}")'.format(self.petrel_name)

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="Well")
    def crs_wkt(self):
        return self._borehole_object_link.GetCrs()

    @property
    def completions_set(self):
        """The currently active completions set for the well as a :class:`cegalprizm.pythontool.CompletionsSet` object.

        Note:
            Even if there are multiple completions sets for the well in Petrel, only the currently active one will be returned. If no completions sets are available, None will be returned.

        Returns:
            cegalprizm.pythontool.CompletionsSet: the completions set for the well.
        """
        completionsSetExists = self._borehole_object_link.CheckCompletionsSetExists()
        if(not completionsSetExists):
            return None
        grpc = CompletionsSetGrpc(self)
        return CompletionsSet(grpc)
    
    @property
    def well_datum(self) -> typing.Tuple[str, float, str]:
        """The well datum (working reference level) for the well as a tuple.
        
        The tuple has the format (name[str], offset[float], description[str])
        When setting the well datum, the description is optional.

        Args:
            well_datum (tuple): The well datum as a tuple of (name[str], offset[float], [optional]description[str])

        Raises:
            PythonToolException: If the well is read-only
            PythonToolException: If the well is a sidetrack borehole
            TypeError: If trying to set the value with an input that is not a tuple
            ValueError: If the tuple is not of length 2 or 3
        
        **Example**:

        Set the well datum for a well:

        .. code-block:: python

            well = petrel.wells["Input/Wells/Other Wells/Well 1"]
            well.readonly = False
            well.well_datum = ("KB", 25, "Kelly Bushing")

        **Example**:

        Set the well datum for a well using the value from another well:

        .. code-block:: python

            well1 = petrel.wells["Input/Wells/Other Wells/Well 1"]
            well2 = petrel.wells["Input/Wells/Other Wells/Well 2"]
            shared_datum = well1.well_datum
            well2.well_datum = shared_datum
        """
        return self._borehole_object_link.GetWellDatum()
    
    @well_datum.setter
    def well_datum(self, value: typing.Tuple[str, float, str]):
        if not isinstance(value, tuple):
            raise TypeError("well_datum must be a tuple of (name[str], offset[float], [optional]description[str])")
        if len(value) < 2 or len(value) > 3:
            raise ValueError("well_datum must be a tuple of (name[str], offset[float], [optional]description[str])")
        if len(value) == 2:
            value = (value[0], value[1], "")
        if (self.readonly):
            raise PythonToolException("The well is read-only")
        if self.is_sidetrack:
            raise PythonToolException("Cannot set WorkingReferenceLevel for a sidetrack borehole")
        self._borehole_object_link.SetWellDatum(value[0], value[1], value[2])

    @property
    def logs(self) -> "welllog.Logs":
        """A readonly iterable collection of the logs for the well

        Returns:
            cegalprizm.pythontool.Logs: the logs for the well

        **Example**:

        .. code-block:: python

            well = petrel.wells.get_by_name("Well 1")

            ## Get a specific log by name
            gamma_log = well.logs["GR"]

            ## Iterate over all logs
            for log in well.logs:
                print(log)

        """
        return welllog.Logs(self)

    @property
    def observed_data_sets(self) -> ObservedDataSets:
        """A readonly iterable collection of the observed data sets for the well
        
        Returns:
            cegalprizm.pythontool.ObservedDataSets: the observed data sets for the well"""
        return ObservedDataSets(self)

    @property
    def surveys(self) -> WellSurveys:
        """A readonly iterable collection of the well surveys for the well.
        Surveys can be accessed by index or name. In case of duplicate names, a list of surveys will be returned.

        **Example**:

        Get a well survey by index:

        well = petrel.wells["Input/Wells/Other Wells/Well 1"]
        first_survey = well.surveys[0]

        **Example**:

        Get a well survey by name:

        well = petrel.wells["Input/Wells/Other Wells/Well 1"]
        survey = well.surveys["Survey 1"]
        
        Returns:
            cegalprizm.pythontool.WellSurveys: the well surveys for the well"""
        return WellSurveys(self)
    
    @property
    def uwi(self) -> str:
        """The unique well identifier (UWI) for the well
        Note that uniqueness is not enforced by either PTP or Petrel, so multiple wells may have the same UWI.
        Note that if the Petrel Project setting is UWI, attempting to set an empty string will throw an exception.

        Args:
            uwi (str): The unique well identifier for the well

        Raises:
            PythonToolException: If the well is read-only

        **Example**:

        Set the unique well identifier for a well:

        .. code-block:: python

            well = petrel.wells["Input/Wells/Other Wells/Well 1"]
            well.uwi = "abc123"
        
        Returns:
            str: the UWI for the well"""
        return self._borehole_object_link.GetUwi()
    
    @uwi.setter
    def uwi(self, value: str) -> None:
        if (self.readonly):
            raise PythonToolException("The well is read-only")
        self._borehole_object_link.SetUwi(str(value))

    @property
    def spud_date(self) -> datetime.datetime:
        """The spud date for the well.

        Args:
            spud_date (datetime.datetime): The spud date for the well as a datetime.datetime object

        Raises:
            TypeError: If trying to set the value with an input that is not a datetime.datetime object
            PythonToolException: If the well is read-only

        **Example**:

        Set the spud date for a well:

        .. code-block:: python

            well = petrel.wells["Input/Wells/Other Wells/Well 1"]
            well.spud_date = datetime.datetime(2020, 1, 1)

        Returns:
            datetime.datetime: the spud date for the well
        """
        return self._borehole_object_link.GetSpudDate()

    @spud_date.setter
    def spud_date(self, value: datetime.datetime) -> None:
        if (self.readonly):
            raise PythonToolException("The well is read-only")
        if not isinstance(value, datetime.datetime):
            raise TypeError("The new date must be a datetime.datetime object")
        self._borehole_object_link.SetSpudDate(value)

    @property
    def well_symbol(self) -> "WellSymbolDescription":
        """The well symbol description for the well. Corresponds to the "Well symbol" drop-down selection in Petrel.

        **Example**:

        Set the well symbol for a well:

        .. code-block:: python

            well_symbol = [desc for desc in petrel.available_well_symbols() if desc.id == 23][0]
            well.well_symbol = well_symbol
        
        Args:
            well_symbol (WellSymbolDescription): The well symbol description for the well

        Raises:
            TypeError: If trying to set the value with an input that is not a WellSymbolDescription object
            PythonToolException: If the well is read-only

        Returns:
            WellSymbolDescription: the well symbol description for the well"""
        (index, name, desription) = self._borehole_object_link.GetWellSymbolDescription()
        return WellSymbolDescription(index, name, desription)
    
    @well_symbol.setter
    def well_symbol(self, value: "WellSymbolDescription") -> None:
        if not isinstance(value, WellSymbolDescription):
            raise TypeError("Well symbol must be a WellSymbolDescription object")
        if (self.readonly):
            raise PythonToolException("The well is read-only")
        self._borehole_object_link.SetWellSymbolDescription(value)
    
    @property
    def wellhead_coordinates(self) -> typing.Tuple[float, float]:
        """The x and y coordinates of the wellhead as a tuple of (x-coordinate[float], y-coordinate[float])

        Args:
            wellhead_coordinates (tuple): The x and y coordinates of the wellhead as a tuple of (x-coordinate[float], y-coordinate[float])

        Raises:
            PythonToolException: If the well is read-only
            PythonToolException: If the method used on sidetrack well
            TypeError: If trying to set the coordinates with an input that is not a tuple
            ValueError: If the coordinates tuple is not of length 2
        
        **Example**:

        Set the wellhead coordinates for a well:

        .. code-block:: python

            well = petrel.wells["Input/Wells/Other Wells/Well 1"]
            well.wellhead_coordinates = (1234.56, 9876.54)

        **Example**:

        Set the wellhead coordinates for a well using the value from another well:

        .. code-block:: python

            well1 = petrel.wells["Input/Wells/Other Wells/Well 1"]
            well2 = petrel.wells["Input/Wells/Other Wells/Well 2"]
            shared_coordinates = well1.wellhead_coordinates
            well2.wellhead_coordinates = shared_coordinates
        """
        return self._borehole_object_link.GetWellHeadCoordinates()
    
    @wellhead_coordinates.setter
    def wellhead_coordinates(self, coordinates: typing.Tuple[float, float]) -> None:
        if not isinstance(coordinates, tuple):
            raise TypeError("Coordinates must be a tuple of (x-coordinate[float], y-coordinate[float])")
        if len(coordinates) != 2:
            raise ValueError("Coordinates must be a tuple of (x-coordinate[float], y-coordinate[float])")
        if (self.readonly):
            raise PythonToolException("The well is read-only")
        if self.is_sidetrack:
            raise PythonToolException("Cannot set WellHead for a sidetrack borehole")
        self._borehole_object_link.SetWellHeadCoordinates(coordinates)

    @property
    def is_sidetrack(self) -> bool:
        """A boolean value indicating whether the well is a sidetrack or not.

        Returns:
            bool: True if the well is a sidetrack, False if the well is a main well.
        """
        return self._borehole_object_link.IsSidetrack()
    
    @experimental_property
    def attributes(self) -> typing.Iterable[WellAttributeInstance]:
        """
        Python iterator with the WellAttributeInstance objects for the Well.
        The WellAttributeInstance objects can be accessed by index or name.
        In case of duplicate names, a list of WellAttributeInstance objects will be returned.

        Returns: An iterable collection of :class:`cegalprizm.pythontool.WellAttributeInstance` objects for the Well.

        Raises:
            KeyError: If the attribute name is not found
            KeyError: If the index is not an int or str
            IndexError: If the index is out of range

        **Example**:

        Print all well attributes for a well:

        .. code-block:: python

            well = petrel.wells["path/to/well"]
            for attribute in well.attributes:
                print(attribute)

        **Example**:

        Retrieve a well attribute by index:

        .. code-block:: python

            well = petrel.wells["path/to/well"]
            attribute_by_index = well.attributes[0]
        
        **Example**:

        Retrieve a well attribute by name:

        .. code-block:: python

            well = petrel.wells["path/to/well"]
            attribute_by_name = well.attributes["Ambient temperature"]
        
        **Example**:

        Retrieve a well attribute by name that has duplicates, returns a list of WellAttribute objects:

        .. code-block:: python

            well = petrel.wells["path/to/well"]
            duplicate_attributes = well.attributes["Duplicate Attribute"]
            attribute_1 = duplicate_attributes[0]
            attribute_2 = duplicate_attributes[1]
        """
        return Attributes(self)

    @validate_name(param_name="sidetrack_name")
    def create_sidetrack(self, sidetrack_name: str) -> "Well":
        """Create a new sidetrack wellbore from the current well. 
        After creation the sidetrack well survey should be created using :func:`create_sidetrack_well_survey` and values should be set using :func:`set`.
        The sidetrack well will have the same wellhead coordinates and well datum as the parent well, so these can not be set.
        Note that if an empty string is passed as the name argument, Petrel will automatically assign a name to the created sidetrack well.

        Args:
            sidetrack_name (str): The name of the new sidetrack well.

        Returns:
            Well: The new sidetrack well as a :class:`Well` object

        Raises:
            TypeError: If the sidetrack_name argument is not a string.
            ValueError: If the sidetrack_name argument is not a valid string.
            PythonToolException: If the well is read-only

        **Example**:

        Create a new sidetrack wellbore from an existing well, create a sidetrack well survey and set values for the survey:

        .. code-block:: python

            my_well = petrel.wells["Input/Wells/My Well"]
            main_survey = my_well.surveys[0]
            my_sidetrack = my_well.create_sidetrack("My Well T2")
            sidetrack_survey = my_sidetrack.create_sidetrack_well_survey("T2 Survey", "X Y Z survey", main_survey, 1234.56)
            sidetrack_survey.set(xs=[458000, 458001], ys=[6785818, 6785819], zs=[-1234, -1235])

        """
        if (self.readonly):
            raise PythonToolException("The well is read-only")
        well_grpc = self._borehole_object_link.CreateSidetrack(sidetrack_name)
        return Well(well_grpc)

    @validate_name(param_name="name", can_be_empty=False)
    def create_well_survey(self, name: str, well_survey_type: str) -> WellSurvey:
        """Create a new well survey (trajectory) for the well.
        Note that this method only works on a main well and will throw an exception if called on a sidetrack well.
        Use the `is_sidetrack` property to check if the well is a sidetrack or not.
        Use :func:`create_sidetrack_well_survey` to create a new well survey for a sidetrack well.

        Args:
            name (str): The name of the new well survey
            well_survey_type (str): One of the following well survey types as a string:
                'X Y Z survey', 'X Y TVD survey', 'DX DY TVD survey', 'MD inclination azimuth survey'

        Returns:
            WellSurvey: The new well survey as a :class:`WellSurvey` object

        Raises:
            TypeError: If the name argument is not a string.
            ValueError: If the name argument is not a valid string.
            ValueError: If the name argument is an empty string or None.
            PythonToolException: If the well is read-only
            PythonToolException: If the method used on a borehole that is not a main borehole
            ValueError: If the well survey type is not one of the allowed types

        **Example**:

        Create a new well survey for a well and set values for the survey:

        .. code-block:: python

            well = petrelconnection.wells["Input/Path/To/Well"]
            survey = well.create_well_survey("New survey", "DX DY TVD survey")
            survey.set(dxs=[0,0], dys=[0,0], tvds=[0,1000])
        
        """
        if (self.readonly):
            raise PythonToolException("The well is read-only")
        if self.is_sidetrack:
            raise PythonToolException("The borehole is not a main borehole.")
        petrel_object = self._borehole_object_link.CreateWellSurvey(name, well_survey_type)
        well_survey = WellSurvey(petrel_object)
        well_survey.readonly = False
        return well_survey

    @validate_name(param_name="name", can_be_empty=False)
    def create_sidetrack_well_survey(self, name: str, well_survey_type: str, tie_in_survey: WellSurvey, tie_in_md: float) -> WellSurvey:
        """Create a new sidetrack well survey (trajectory) for the sidetrack well.
        Note that this method only works on a sidetrack well and will throw an exception if called on a main well.
        Use the `is_sidetrack` property to check if the well is a sidetrack well or not.
        Use :func:`create_well_survey` to create a new well survey for a main well.

        Args:
            name (str): The name of the new well survey
            well_survey_type (str): One of the following well survey types as a string:
                'X Y Z survey', 'X Y TVD survey', 'DX DY TVD survey', 'MD inclination azimuth survey'
            tie_in_survey (WellSurvey): The survey to tie the sidetrack well to (e.g. the WellSurvey of the parent Well)
            tie_in_md (float): The measured depth of the tie-in point in the parent well

        Returns:
            WellSurvey: The new well survey as a :class:`WellSurvey` object

        Raises:
            TypeError: If the name argument is not a string.
            ValueError: If the name argument is not a valid string.
            ValueError: If the name argument is an empty string or None.
            PythonToolException: If the sidetrack well is read-only
            PythonToolException: If the method used on a well that is not a sidetrack well
            ValueError: If the well survey type is not one of the allowed types

        **Example**:

        Create a new sidetrack well survey for a sidetrack well and set values for the survey:

        .. code-block:: python

            well = petrelconnection.wells["Input/Path/To/Well"]
            parent_well_survey = well.surveys[0]
            my_sidetrack = well.create_sidetrack("Well T2")
            sidetrack_survey = my_sidetrack.create_sidetrack_well_survey("New survey", "DX DY TVD survey", parent_well_survey, 500.55)
            sidetrack_survey.set(dxs=[2,3], dys=[2,3], tvds=[1000, 1500])
        
        """
        if not isinstance(tie_in_survey, WellSurvey):
            raise TypeError("tie_in_survey must be a WellSurvey object.")
        if (self.readonly):
            raise PythonToolException("The well is read-only")
        if not self.is_sidetrack:
            raise PythonToolException("The borehole is not a sidetrack borehole.")
        tie_in_guid = ""
        tie_in_sub_type = ""
        if tie_in_survey is not None:
            tie_in_guid = tie_in_survey._petrel_object_link._guid
            tie_in_sub_type = tie_in_survey._petrel_object_link._sub_type
        petrel_object = self._borehole_object_link.CreateWellSurvey(name, well_survey_type, tie_in_guid, tie_in_sub_type, tie_in_md)
        well_survey = WellSurvey(petrel_object)
        well_survey.readonly = False
        return well_survey

    def logs_dataframe(self, 
            global_well_logs: typing.Union[typing.Union["welllog.WellLog", "welllog.DiscreteWellLog", "welllog.GlobalWellLog", "petrellink.DiscreteGlobalWellLogs", "petrellink.GlobalWellLogs"], typing.Iterable[typing.Union["welllog.WellLog", "welllog.DiscreteWellLog", "welllog.GlobalWellLog", "petrellink.DiscreteGlobalWellLogs", "petrellink.GlobalWellLogs"]]], 
            discrete_data_as: typing.Union[str, int] = "string")\
            -> pd.DataFrame:
            
        """Log data for the passed well logs or global well logs as a Pandas dataframe. 

        Returns the log data for the passed global well logs resampled onto consistent MDs.
        You can pass a list of well logs or global well logs as input.

        Note that due to the resampling the returned dataframe may have more rows than the original logs.
        To retrieve the actual log data for a single log, use the as_dataframe() method on the individual :class:`cegalprizm.pythontool.WellLog` or :class:`cegalprizm.pythontool.DiscreteWellLog` object.

        Args:
            global_well_logs: a list of WellLogs, DiscreteWellLogs, GlobalWellLogs or DiscreteGlobalWellLogs
            discrete_data_as: A flag to change how discrete data is displayed. 
                'string' will cause discrete data tag to be returned as name
                or 'value' will cause discrete data tag to be returned as int. Defaults to 'string'

        Returns:
            pandas.DataFrame: a dataframe of the resampled continuous logs

        Raises:
            ValueError: if the supplied objects are not WellLog, DiscreteWellLog, GlobalWellLog, or DiscreteGlobalWellLog
        """
        from cegalprizm.pythontool import WellLog, GlobalWellLog, DiscreteWellLog, DiscreteGlobalWellLog

        if not isinstance(global_well_logs, collections.abc.Iterable):
            global_well_logs = [global_well_logs]
        
        if any(
            o
            for o in global_well_logs
            if not (isinstance(o, WellLog) or isinstance(o, GlobalWellLog) or isinstance(o, DiscreteWellLog) or isinstance(o, DiscreteGlobalWellLog))
        ):
            raise ValueError(
                "You can only pass in GlobalWellLogs, DiscreteGlobalWellLogs, WellLogs or DiscreteWellLogs"
            )

        df = self._borehole_object_link.GetLogs(tuple([gwl for gwl in global_well_logs]), discrete_data_as)
                 
        return df

    def md_to_xytime(self, md: typing.List[float])\
            -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:            
        """Converts a list of MD values to X, Y and Z (time)

        Args:
            md: List with MD values

        Returns:
            Returns a tuple([x], [y], [z]), where x is a list of x positions, 
                y is a list of y positions and z is a list of z (time) positions.
                Wells without time will return NaN values.
        """               
        lst_xs = []
        lst_ys = []
        lst_zs = []
        n = 1000
        for i in range(0, len(md), n):
            data = self._borehole_object_link.GetElevationTimePosition(md[i:i+n])
            lst_xs.append(data[0])
            lst_ys.append(data[1])
            lst_zs.append(data[2])
        d = ([x for xs in lst_xs for x in xs ], 
            [y for ys in lst_ys for y in ys ], 
            [z for zs in lst_zs for z in zs ])
        return d

    def md_to_xydepth(self, md: typing.List[float])\
            -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        """Converts a list of MD values to X, Y and Z (depth)

        Args:
            md: List with MD values

        Returns:
            Returns a tuple([x], [y], [z]), where x is a list of x positions, 
                y is a list of y positions and z is a list of z (depth) positions of the md values.
        """         
        lst_xs = []
        lst_ys = []
        lst_zs = []
        n = 1000
        for i in range(0, len(md), n):
            data = self._borehole_object_link.GetTvdPosition(md[i:i+n])
            lst_xs.append(data[0])
            lst_ys.append(data[1])
            lst_zs.append(data[2])
        d = ([x for xs in lst_xs for x in xs ], 
            [y for ys in lst_ys for y in ys ], 
            [z for zs in lst_zs for z in zs ])
        return d

    @property
    def parent_folder(self) -> typing.Union["WellFolder"]:
        """Returns the parent WellFolder of this Well in Petrel.

        Returns:
            :class:`WellFolder`: The parent WellFolder of the Well.

        **Example**:

        .. code-block:: python

            well = petrel_connection.wells["Input/Wells/Well 1"]
            well.parent_folder
            >> WellFolder(petrel_name="Wells")
        """
        return self._parent_folder

    def __get_compatible_logs(self, existing_droids, global_logs):
        compatible_logs = []
        if (len(global_logs) > 0):
            for log in global_logs:
                droid = log._petrel_object_link.GetDroidString()
                if droid in existing_droids:
                    compatible_logs.append(log)
        return compatible_logs

    def _get_observed_data_sets(self) -> typing.Iterator[ObservedDataSet]:
        for odset in self._borehole_object_link.GetObservedDataSets():
            if odset is None:
                continue
            ods = ObservedDataSet(odset)
            yield ods

    def _get_number_of_observed_data_sets(self) -> int:
        return self._borehole_object_link.GetNumberOfObservedDataSets()

    def _get_well_surveys(self):
        return self._borehole_object_link.GetWellSurveys()

    def _get_number_of_well_surveys(self) -> int:
        return self._borehole_object_link.GetNumberOfWellSurveys()
    
    def _as_dataframe_for_attributes(self, attribute_filter: List[str], attribute_guids) -> pd.DataFrame:
        return self._borehole_object_link.GetDataFrameValues(attribute_filter, attribute_guids)

    def _set_values_from_dataframe(self, data_to_write) -> None:
        return self._borehole_object_link.SetDataFrameValues(data_to_write)

@experimental_class
class Attributes(object):
    """
    An iterable collection of :class:`cegalprizm.pythontool.WellAttributeInstance` objects for the Attributes in the Well
    """

    def __init__(self, well: Well):
        self._well = well
        if isinstance(well, Well):
            petrel_connection = well._borehole_object_link._plink
            attributes = petrel_connection.well_attributes
            flattened_attributes = utils.deep_flatten_list(attributes)
            self._well_attributes = [
                WellAttributeInstance(attr, well) 
                for attr in flattened_attributes
            ]
        else:
            raise TypeError("Parent must be a Well")
    
    def __len__(self) -> int:
        return len(self._well_attributes)
    
    def __iter__(self) -> typing.Iterator[WellAttributeInstance]:
        return iter(self._well_attributes)
    
    def __getitem__(self, key):
        attribute = _utils.get_item_from_collection_petrel_name(self._well_attributes, key)
        if attribute is not None:
            return attribute
        if isinstance(key, str):
            raise KeyError(f"The attribute with Petrel name '{key}' was not found. Please verify the attribute name and ensure it is present in the project.")
        else:
            raise KeyError("Attributes can only be indexed by int or str")

    def __str__(self) -> str:
        return 'Attributes(Well="{0}")'.format(self._well.petrel_name)
    
    def __repr__(self) -> str:
        return str(self)

    def as_dataframe(self, attribute_filter: List[Union[WellAttributeFilterEnum, WellAttribute, str]] = [WellAttributeFilterEnum.All]) -> pd.DataFrame:
        """
        Gets a dataframe with information about the Attributes in the Well.

        Args:
            attribute_filter: A list of WellAttributeFilterEnum, WellAttribute or strings to filter the attributes to include in the dataframe. Defaults to [WellAttributeFilterEnum.All].
                Available filters are:
                - 'All': All attributes (Default + User)
                - 'Default': Only the default attributes
                - 'User': Only the user defined attributes
                - Any number of WellAttribute objects to include in the dataframe

        Returns:
            Dataframe: A dataframe with WellAttribute information about the Attributes in the Well.
        
        Raises:
            ValueError: If an unknown attribute filter string is passed.
            ValueError: If the attribute_filter argument is not a list of WellAttributeFilterEnum, WellAttribute or strings.
            TypeError: If an individual entry the attribute_filter argument is not a WellAttributeFilterEnum, WellAttribute or strings.

        **Example**:

        Get a dataframe with attribute information for all Attributes in the Well

        .. code-block:: python

                well = petrelconnection.wells["Input/Path/To/Well"]
                df = well.attributes.as_dataframe()

        **Example**:

        Get a dataframe with attribute information for a specific set of attributes in the Well using WellAttributeFilterEnum or string

        .. code-block:: python

                well = petrelconnection.wells["Input/Path/To/Well"]
                df_user_enum = well.attributes.as_dataframe([WellAttributeFilterEnum.User])
                df_user_str = well.attributes.as_dataframe(['User'])

        **Example**:

        Get a dataframe with attribute information for a specific set of attributes in the Well,
        using a combination of WellAttributeFilterEnum or string and WellAttribute.

        .. code-block:: python

                well_attributes = petrelconnection.well_attributes
                surfacey_attribute = attributes['Input/Wells/Well Attributes/Surface Y']
                z_attribute = attributes['Input/Wells/Well Attributes/Z']
                uwi_attribute = attributes['Input/Wells/Well Attributes/UWI']
                well = petrelconnection.wells["Input/Path/To/Well"]
                df_filtered = well.attributes.as_dataframe([z_attribute, surfacey_attribute, uwi_attribute])
                df_filtered_user_enum = well.attributes.as_dataframe([WellAttributeFilterEnum.User, z_attribute, surfacey_attribute, uwi_attribute])
                df_filtered_user_str = well.attributes.as_dataframe(['User', z_attribute, surfacey_attribute, uwi_attribute])
        """
        attribute_filter_str = []
        attribute_guids = []
        all_enum_values = [e.value for e in WellAttributeFilterEnum]
        if attribute_filter is None or len(attribute_filter) == 0:
            raise ValueError("attribute_filter must be a list of WellAttributeFilterEnum, WellAttribute or strings")
        if all(isinstance(attr, WellAttribute) for attr in attribute_filter):
            attribute_filter_str = ["All"]
        for attr in attribute_filter:
            if isinstance(attr, WellAttributeFilterEnum):
                attribute_filter_str.append(attr.value)
            elif isinstance(attr, WellAttribute):
                attribute_guids.append(petrelinterface_pb2.PetrelObjectGuid(
                    guid = attr.droid,
                    sub_type = attr._petrel_object_link._sub_type))
            elif isinstance(attr, str):
                if attr not in all_enum_values:
                    raise ValueError(f"Unknown attribute filter string: {attr}")
                attribute_filter_str.append(attr)
            else:
                raise TypeError("attribute_filter must be a list of WellAttributeFilterEnum, WellAttribute or str")
        df = self._well._as_dataframe_for_attributes(attribute_filter=attribute_filter_str, attribute_guids=attribute_guids)
        if "Name" in df.columns:
            df.insert(0, "Name", df.pop("Name"))
        return df

    def set_values(self, df: pd.DataFrame, ignore_duplicates:bool=False) -> None:
        """
        Sets the values for the Attributes for the Well using a dataframe.

        The dataframe must have exactly one row and the column names must match the WellAttribute names.
        The values will be set for all Attributes that are writable and have a matching column in the dataframe.

        If the WellAttribute is not writable, it will be skipped.

        Args:
            df (pd.DataFrame): A pandas dataframe of attributes with format as returned by the as_dataframe() method.
            ignore_duplicates (bool): If False, all attributes with the same Petrel name will be updated with the same attribute values. Defaults to False.

        **Example**:

        Get the dataframe for the Well and edit some values and set values using the updated dataframe.

        .. code-block:: python
            well = petrel.wells["Input/Path/To/Well"]
            df = well.attributes.as_dataframe()
            df["Surface X"] = 123456.55
            df["Surface Y"] = 654321.55
            df["UWI"] = "abc123"
            df["Boolean"] = True
            well.attributes.set_values(df)
        
        Raises:
            TypeError: If df is not a pandas DataFrame
            TypeError: If ignore_duplicates is not a boolean
            ValueError: If the dataframe has more than one row or no rows
            PythonToolException: If the value for an attribute could not be set
        """
        
        data_to_write = []
        attributes = self._well_attributes.copy()

        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        if not isinstance(ignore_duplicates, bool):
            raise TypeError("ignore_duplicates must be a boolean")
        if df.index.empty:
            return
        if len(df) != 1:
            raise ValueError("df must have exactly one row")

        valid_attributes = _utils.get_valid_well_attributes(attributes, df, ignore_duplicates)
        
        attr_column_map = _utils.map_well_attributes_to_columns(valid_attributes, df)

        for _, row in df.iterrows():
            data_to_write = [
                [attr.droid, [row[attr_column_map[attr]]]]
                for attr in valid_attributes
            ]
        if data_to_write:
            self._well._set_values_from_dataframe(data_to_write)