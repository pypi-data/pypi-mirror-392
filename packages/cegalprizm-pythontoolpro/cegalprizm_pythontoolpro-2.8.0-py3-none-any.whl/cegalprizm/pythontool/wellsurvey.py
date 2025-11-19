# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




import typing
import pandas as pd
from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion
from cegalprizm.pythontool import borehole, exceptions, _docstring_utils
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.wellsurvey_grpc import DxdytvdWellSurveyGrpc, ExplicitWellSurveyGrpc, MdinclazimWellSurveyGrpc, XyzWellSurveyGrpc, XytvdWellSurveyGrpc
    from cegalprizm.pythontool.borehole import Well

class WellSurvey(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    """A class holding information about a well survey"""

    def __init__(self, petrel_object_link:  typing.Union["DxdytvdWellSurveyGrpc", "ExplicitWellSurveyGrpc", "MdinclazimWellSurveyGrpc", "XyzWellSurveyGrpc", "XytvdWellSurveyGrpc"]):
        super(WellSurvey, self).__init__(petrel_object_link)
        self._wellsurvey_object_link = petrel_object_link
        self.__well_survey_type = None

    @property
    def _well_survey_type(self) -> str:
        if self.__well_survey_type is None:
            self.__well_survey_type = self._wellsurvey_object_link.GetOceanType()
        return self.__well_survey_type

    @property
    def record_count(self) -> int:
        """The number of records in this well survey"""
        return self._wellsurvey_object_link.RecordCount() # int

    def __str__(self) -> str:
        """A readable representation of the well survey"""
        return 'WellSurvey(petrel_name="{0}")'.format(self.petrel_name)

    @property
    def well(self) -> "Well":
        """The well to which this well survey belongs to

        Returns:
            cegalprizm.pythontool.Well: the well for this well survey"""
        well = self._wellsurvey_object_link.GetParentPythonBoreholeObject()
        return borehole.Well(well)

    @property
    def well_survey_type(self) -> str:
        """Returns the type of well survey
        
        Returns:
            'X Y Z survey' 
                or 'X Y TVD survey' 
                or 'DX DY TVD survey' 
                or 'MD inclination azimuth survey'
                or 'Explicit survey'
        """
        if (self._well_survey_type == "XyzTrajectory"):
            return "X Y Z survey"
        elif (self._well_survey_type == "XyTvdTrajectory"):
            return "X Y TVD survey"
        elif (self._well_survey_type == "DxDyTvdTrajectory"):
            return "DX DY TVD survey"
        elif (self._well_survey_type == "MDInclinationAzimuthTrajectory"):
            return "MD inclination azimuth survey"
        elif (self._well_survey_type == "ExplicitTrajectory"):
            return "Explicit survey"
        else: 
            raise NotImplementedError("Cannot return the well_survey-type for this WellSurvey object")

    @property
    def azimuth_reference(self) -> str:
        """Gets or sets the azimuth reference for well survey types MD inclination azimuth survey and DX DY TVD survey 

        Can only be set to string: 'Grid north' or 'True north'
        Changing the azimuth reference will not alter the values themselves but will change the reference point from which these values were measured.

        Returns:
            string: 'Grid north' or 'True north'

        Raises:
            PythonToolException: If the well survey is X Y Z well survey, X Y TVD well survey or Explicit survey
            ValueError: If the set value is not 'Grid north' or 'True north'
        """
        if (self._well_survey_type == "ExplicitTrajectory" or self._well_survey_type == "XyzTrajectory" or self._well_survey_type == "XyTvdTrajectory"):
            raise exceptions.PythonToolException("X Y Z well survey, X Y TVD well survey and Explicit survey have no azimuth reference.")
        return "Grid north" if self._wellsurvey_object_link.AzimuthReferenceIsGridNorth() else "True north" # type: ignore

    @azimuth_reference.setter
    def azimuth_reference(self, value: str) -> None:
        invalid_survey_types = {"ExplicitTrajectory", "XyzTrajectory", "XyTvdTrajectory"}
        if self._well_survey_type in invalid_survey_types:
            raise exceptions.PythonToolException("X Y Z well survey, X Y TVD well survey and Explicit survey have no azimuth reference.")
        if self.readonly:
            raise exceptions.PythonToolException("WellSurvey is readonly")
        valid_references = {'grid north': True, 'true north': False}
        value_lower = value.lower()
        if value_lower not in valid_references:
            raise ValueError("Azimuth reference must be set to either 'Grid north' or 'True north'")
        self._wellsurvey_object_link.SetAzimuthReference(valid_references[value_lower])

    @property
    def algorithm(self) -> str:
        """Gets or sets the algorithm for well survey types X Y Z, X Y TVD and DX DY TVD surveys

        Can only be set to string: 'Minimum curvature' or 'Linearization'
    
        Returns:
            string: 'Minimum curvature' or 'Linearization'

        Raises:
            PythonToolException: If well survey is MD inclination azimuth survey or Explicit survey
            ValueError: If the set value is not 'Minimum curvature' or 'Linearization'
        """
        if (self._well_survey_type == "MDInclinationAzimuthTrajectory" or self._well_survey_type == "ExplicitTrajectory"):
            raise exceptions.PythonToolException("Algorithm can only be retrieved for X Y Z, X Y TVD and DX DY TVD surveys")
        return 'Minimum curvature' if self._wellsurvey_object_link.IsAlgorithmMinimumCurvature() else 'Linearization'

    @algorithm.setter
    def algorithm(self, value) -> None:
        if (self._well_survey_type == "MDInclinationAzimuthTrajectory" or self._well_survey_type == "ExplicitTrajectory"):
            raise exceptions.PythonToolException("Algorithm can only be modified for X Y Z, X Y TVD and DX DY TVD surveys")
        if (not (value == 'Minimum curvature' or value == 'Linearization')):
            raise ValueError("Algorithm must be set to either 'Minimum curvature' or 'Linearization'")
        self._wellsurvey_object_link.SetAlgorithmToMinimumCurvature(True if value == 'Minimum curvature' else False)

    def set_survey_as_definitive(self):
        """Set well survey as definitive"""
        self._wellsurvey_object_link.SetSurveyAsDefinitive()

    def __is_sidetrack(self):
        return self._wellsurvey_object_link.IsSidetrack() # bool

    @property
    def is_definitive(self) -> bool:
        """Check if survey is definitive.
        
        Returns:
            bool: True if survey is definitive, False otherwise
        """
        return self._wellsurvey_object_link.IsDefinitive()

    @property
    def tie_in_md(self) -> float:
        """Returns the tie-in MD point
        
        Raises:
            PythonToolException: If the well survey is not a sidetrack trajectory
        """
        if (not self.__is_sidetrack()):
            raise exceptions.PythonToolException("WellSurvey is not a sidetrack trajectory and therefore has no tie-in MD")

        tie_in_md = self._wellsurvey_object_link.TieInMd() # float
        return tie_in_md
    
    @tie_in_md.setter
    def tie_in_md(self, value: float):
        """Sets the tie-in MD for this well survey
        
        Raises:
            PythonToolException: If the well survey is not a sidetrack trajectory
        """
        if (not self.__is_sidetrack()):
            raise exceptions.PythonToolException("WellSurvey is not a sidetrack trajectory and therefore cannot set tie-in MD")

        self._wellsurvey_object_link.SetTieInMd(value)

    def is_calculation_valid(self) -> bool:
        """Returns True if the calculation is valid, False otherwise.
        
        This method checks if the polyline records can be calculated for the well survey.
        The polyline records are calculated using the survey records and the settings of the survey.
        If there are no polyline records, the calculation is not valid.

        Reasons for this may be: 
            - No well head defined
            - No well datum defined
            - If project CRS is set, the well survey cannot be spatially converted
            - If a sidetrack well survey: tie-in well survey calculation fails or tie-in-md is outside range of the tie-in well survey
            - A main well survey requires at least two records
            - A sidetrack well survey requires at least one record
            - For survey types with algorithm: if using minimum curvature algorithm, the algorithm may not accept the supplied records
        """
        return self._wellsurvey_object_link.IsCalculationValid()

    def as_dataframe(self, get_calculated_trajectory: bool = False) -> pd.DataFrame:
        """The well survey records OR the calculated well survey polyline records of the well survey as a pandas dataframe.
        
        For X Y Z well survey - X, Y, and Z records will be returned in the dataframe.
        For X Y TVD well survey - X, Y and TVD records will be returned in the dataframe.
        For DX DY TVD well survey - DX, DY, and TVD will be returned in the dataframe.
        For MD inclination azimuth well survey - MD, Inclination, Azimuth GN/TN will be returned in the dataframe.
        
        For X Y Z, X Y TVD, DX DY TVD and MD inclination azimuth well survey: 
        - If setting get_calculated_trajectory=True, dataframe will contain X, Y, Z, MD, Inclination, Azimuth GN columns.
        - If setting get_calculated_trajectory=True and well survey calculation is not valid - an empty dataframe will be returned.

        For Explicit well survey:
        -  X, Y, Z, MD, Inclincation, Azimuth GN columns will be returned in the dataframe. Using flag get_calculated_trajectory will not affect columns in dataframe.

        The API for well surveys is limited to either get the editable survey records or the calculated well survey polyline records.
        It is therefore not possible to return a dataframe matching what is shown in the Petrel well survey spreadsheet.

        Args:
            get_calculated_trajectory: Flag to get the calculated well survey polyline records instead of the type specific editable records. Defaults to False.
        
        Returns:
            A pandas dataframe containing records of the well survey
        """
        import pandas as pd
        if (self._well_survey_type == "XyzTrajectory"):
            xs = [x for x in self._wellsurvey_object_link.GetXs(get_calculated_trajectory)]
            ys = [y for y in self._wellsurvey_object_link.GetYs(get_calculated_trajectory)]
            zs = [z for z in self._wellsurvey_object_link.GetZs(get_calculated_trajectory)]
            data = {"X": xs, "Y": ys, "Z": zs}
            if get_calculated_trajectory:
                mds = [md for md in self._wellsurvey_object_link.GetMds()]
                incls = [incl for incl in self._wellsurvey_object_link.GetIncls()]
                azims = [azim for azim in self._wellsurvey_object_link.GetAzims()]
                data["MD"] = mds
                data["Inclination"] = incls
                data["Azimuth GN"] = azims
            return pd.DataFrame.from_dict(data)
        elif (self._well_survey_type == "XyTvdTrajectory"):
            xs = [x for x in self._wellsurvey_object_link.GetXs(get_calculated_trajectory)]
            ys = [y for y in self._wellsurvey_object_link.GetYs(get_calculated_trajectory)]
            data = {"X": xs, "Y": ys}
            if get_calculated_trajectory:
                zs = [z for z in self._wellsurvey_object_link.GetZs()]
                data["Z"] = zs
                mds = [md for md in self._wellsurvey_object_link.GetMds()]
                data["MD"] = mds
                incls = [incl for incl in self._wellsurvey_object_link.GetIncls()]
                data["Inclination"] = incls
                azims = [azim for azim in self._wellsurvey_object_link.GetAzims()]
                data["Azimuth GN"] = azims
            else:
                tvds = [tvd for tvd in self._wellsurvey_object_link.GetTvds()]
                data["TVD"] = tvds
            return pd.DataFrame.from_dict(data)
        elif (self._well_survey_type == "DxDyTvdTrajectory"):
            (dx_head, dy_head) = ("DX", "DY") if (self._wellsurvey_object_link.AzimuthReferenceIsGridNorth()) else ("DX TN", "DY TN") # type: ignore
            if get_calculated_trajectory:
                xs = [x for x in self._wellsurvey_object_link.GetXs()] 
                ys = [y for y in self._wellsurvey_object_link.GetYs()]
                zs = [z for z in self._wellsurvey_object_link.GetZs()]
                mds = [md for md in self._wellsurvey_object_link.GetMds()]
                incls = [incl for incl in self._wellsurvey_object_link.GetIncls()]
                azims = [azim for azim in self._wellsurvey_object_link.GetAzims()] # Azimuth values refer to grid north by default for DxdytvdWellSurvey
                data = {"X": xs, "Y": ys, "Z": zs, "MD": mds, "Inclination": incls, "Azimuth GN": azims}
            else:
                dxs = [dx for dx in self._wellsurvey_object_link.GetDxs()]
                dys = [dy for dy in self._wellsurvey_object_link.GetDys()] 
                tvds = [tvd for tvd in self._wellsurvey_object_link.GetTvds()]
                data = {dx_head: dxs, dy_head: dys, "TVD": tvds}
            return pd.DataFrame.from_dict(data)
        elif (self._well_survey_type == "MDInclinationAzimuthTrajectory"):
            mds = [md for md in self._wellsurvey_object_link.GetMds(get_calculated_trajectory)]
            incls = [incl for incl in self._wellsurvey_object_link.GetIncls(get_calculated_trajectory)]
            azims = [azim for azim in self._wellsurvey_object_link.GetAzims(get_calculated_trajectory)]
            azim_head = "Azimuth GN" if (self._wellsurvey_object_link.IsAzimuthReferenceGridNorth()) else "Azimuth TN" # type: ignore
            if get_calculated_trajectory:
                xs = [x for x in self._wellsurvey_object_link.GetXs()] 
                ys = [y for y in self._wellsurvey_object_link.GetYs()]
                zs = [z for z in self._wellsurvey_object_link.GetZs()]
                data = {"X": xs, "Y": ys, "Z": zs, "MD": mds, "Inclination": incls, "Azimuth GN": azims}
            else:
                data = {"MD": mds, "Inclination": incls, azim_head: azims}
            return pd.DataFrame.from_dict(data)
        elif (self._well_survey_type == "ExplicitTrajectory"):
            mds = [md for md in self._wellsurvey_object_link.GetMds()]
            incls = [incl for incl in self._wellsurvey_object_link.GetIncls()]
            azims = [azim for azim in self._wellsurvey_object_link.GetAzims()]
            xs = [x for x in self._wellsurvey_object_link.GetXs()]
            ys = [y for y in self._wellsurvey_object_link.GetYs()]
            zs = [z for z in self._wellsurvey_object_link.GetZs()]
            data = {"X": xs,"Y": ys, "Z": zs,"MD": mds, "Inclination": incls, "Azimuth GN": azims}
            return pd.DataFrame.from_dict(data)
        else:
            raise NotImplementedError("WellSurvey type not implemented")

    def set(self,
            xs: typing.Optional[typing.List[float]]=None,
            ys: typing.Optional[typing.List[float]]=None,
            zs: typing.Optional[typing.List[float]]=None,
            dxs: typing.Optional[typing.List[float]]=None,
            dys: typing.Optional[typing.List[float]]=None,
            tvds: typing.Optional[typing.List[float]]=None,
            mds: typing.Optional[typing.List[float]]=None,
            incls: typing.Optional[typing.List[float]]=None,
            azims: typing.Optional[typing.List[float]]=None)\
            -> None:
        """
        Replaces all the records with the supplied arrays.

        For X Y Z survey - xs, ys, and zs is required as input
        
        For X Y TVD survey - xs, ys, tvds is required as input
        
        For DX DY TVD survey - dxs, dys and tvds is required as input
        
        For MD inclination azimuth - mds, incls and azims is required as input
        
        For Explicit survey - cannot modify records for well survey of type Explicit survey

        Args:
            xs: a list of x values
            ys: a list of y values
            zs: a list of z values
            dxs: a list of dx values
            dys: a list of dy values
            mds: a list of md values
            incls: a list of inclination values
            azims: a list of azimuth values

        Raises:
            PythonToolException: If the well survey is type Explicit survey or if WellSurvey is readonly
            ValueError: If the required input arrays are not provided or if they are of un-equal lengths
        """

        if (self._well_survey_type == "ExplicitTrajectory"):
            raise exceptions.PythonToolException("Cannot modify records for well survey of type Explicit survey")

        if (self.readonly):
            raise exceptions.PythonToolException("WellSurvey is readonly")

        if (self._well_survey_type == "XyzTrajectory"):
            if (xs is None or ys is None or zs is None):
                raise ValueError("Required input when setting records for X Y Z survey is xs, ys and zs")
            if (len(xs) != len(ys) != len(zs)):
                raise ValueError("Input arrays must have same length")
            self._wellsurvey_object_link.SetRecords(xs, ys, zs) # type: ignore

        elif (self._well_survey_type == "XyTvdTrajectory"):
            if (xs is None or ys is None or tvds is None):
                raise ValueError("Required input when setting records for X Y TVD survey is xs, ys and tvds")
            if (len(xs) != len(ys) != len(tvds)):
                raise ValueError("Input arrays must have same length")
            self._wellsurvey_object_link.SetRecords(xs, ys, tvds) # type: ignore

        elif (self._well_survey_type == "DxDyTvdTrajectory"):
            if (dxs is None or dys is None or tvds is None):
                raise ValueError("Required input when setting records for DX DY TVD survey is dxs, dys and tvds")
            if (len(dxs) != len(dys) != len(tvds)):
                raise ValueError("Input arrays must have same length")
            self._wellsurvey_object_link.SetRecords(dxs, dys, tvds) # type: ignore

        elif (self._well_survey_type == "MDInclinationAzimuthTrajectory"):
            if (mds is None or incls is None or azims is None):
                raise ValueError("Required input when setting records for MD inclination azimuth survey is mds, incls and azims")
            if (len(mds) != len(incls) != len(azims)):
                raise ValueError("Input arrays must have same length")

            ## TODO: Check if incls and azims are within correct degree range

            self._wellsurvey_object_link.SetRecords(mds, incls, azims) # type: ignore

        else:
            raise NotImplementedError("Cannot set records for this WellSurvey object")

    @_docstring_utils.clone_docstring_decorator(return_type="WellSurvey", respects_subfolders=True)
    def clone(self, name_of_clone: str, copy_values: bool = False) -> "WellSurvey":
        return typing.cast("WellSurvey", self._clone(name_of_clone, copy_values = copy_values))
    

class WellSurveys(object):
    """An iterable collection of :class:`cegalprizm.pythontool.WellSurvey` objects, representing the well surveys for a Well.
    
    Surveys can be accessed by index or name. In case of duplicate names, a list of surveys will be returned.

    **Example**:

    Get a well survey by index:

    well = petrel.wells["Input/Wells/Other Wells/Well 1"]
    first_survey = well.surveys[0]

    **Example**:

    Get a well survey by name:

    well = petrel.wells["Input/Wells/Other Wells/Well 1"]
    survey = well.surveys["Survey 1"]
    """

    def __init__(self, well: "Well"):
        self._well = well

    def __iter__(self) -> typing.Iterator[WellSurvey]:
        for p in self._well._get_well_surveys():
            yield p

    def __getitem__(self, key) -> WellSurvey:
        surveys = [item for item in self._well._get_well_surveys()]
        if isinstance(key, int):
            return surveys[key]
        elif isinstance(key, str):
            matches = [match for match in surveys if match.petrel_name == key]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) == 0:
                raise KeyError(f"Could not find WellSurvey with name '{key}'")
            else:
                return matches
            

    def __len__(self) -> int:
        return self._well._get_number_of_well_surveys()

    def __str__(self) -> str:
        return 'WellSurveys(well="{0}")'.format(self._well)

    def __repr__(self) -> str:
        return str(self)

    @property
    def readonly(self) -> bool:
        return self._well.readonly