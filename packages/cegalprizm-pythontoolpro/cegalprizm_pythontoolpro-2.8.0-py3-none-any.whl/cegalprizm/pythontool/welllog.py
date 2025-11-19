# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory
from cegalprizm.pythontool.petrelobject import PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion
from cegalprizm.pythontool.template import Template, DiscreteTemplate
import typing
import math
import pandas as pd
import numpy as np
from warnings import warn
from cegalprizm.pythontool import primitives
from cegalprizm.pythontool import _utils, _docstring_utils
from cegalprizm.pythontool import exceptions
from cegalprizm.pythontool import borehole
from cegalprizm.pythontool import _config

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.borehole_grpc import DiscreteGlobalWellLogGrpc, GlobalWellLogGrpc, WellLogGrpc, DiscreteWellLogGrpc
    from cegalprizm.pythontool.borehole import Well
    from cegalprizm.pythontool import GlobalWellLogFolder

class LogSample(object):
    """An object representing a log sample, holding its position and value"""

    def __init__(self, md: float, x, y, z, twt:float, tvdss:float, tvd:float, value:float, is_discrete):
        self._is_discrete = is_discrete
        self._missing_value = (
            _config._INT32MAXVALUE if is_discrete else _config._DOUBLENAN
        )
        self._md = md
        self._twt = twt
        self._tvdss = tvdss
        self._tvd = tvd
        self._position: primitives.Point = primitives.Point(x, y, z)
        if self._is_missing_value(value):
            self._value = None
        else:
            self._value = value

    def __str__(self) -> str:
        """A readable representation of the sample"""
        return "LogSample(md={:.2f}, position={}, TWT={:.2f}, TVDSS={:.2f}, TVD={:.2f}, value={})".format(
            self._md, str(self._position), self._twt, self._tvdss, self._tvd, self._value_text()
        )

    def __repr__(self) -> str:
        return str(self)

    def _is_missing_value(self, v):
        if self._is_discrete:
            return v is None or v == _config._INT32MAXVALUE
        else:
            return v is None or math.isnan(v)

    def _value_text(self):
        if self.value is None:
            return str(None)
        else:
            return (
                "{}".format(self.value)
                if self._is_discrete
                else "{:.2f}".format(self._value)
            )

    @property
    def position(self) -> primitives.Point:
        """The position of the sample in world-coordinates

        Returns:
            cegalprizm.pythontool.Point: the world coordinates of the sample

        """
        return self._position

    @property
    def md(self) -> float:
        """Returns the measured depth of the sample"""
        return self._md

    @property
    def twt(self) -> float:
        """The two-way-time value of the sample

        Use this value instead of the ``z`` property of the
        ``position`` property when you want to work with logs and
        seismic objects in the time domain as opposed to objects in
        the depth domain.

        Returns:
            The TWT of the sample in the time domain.

        """
        return self._twt


    @property
    def tvdss(self) -> float:
        """Returns the true vertical depth sub sea level of the sample"""
        return self._tvdss
    
    @property
    def tvd(self) -> float:
        """Returns the true vertical depth below working reference level of the sample"""
        return self._tvd

    @property
    def value(self) -> typing.Optional[float]:
        """Gets and sets the value of the log sample

        N.b no conversion of units is made from Petrel. For discrete
        logs, the values are integers you can then map the integer
        values to strings using the log's ``discrete_codes`` property.

        Note that setting a sample's value in this way can be very
        slow, especially if you are setting lots of them one after the
        other down a log.  In this case, consider using
        :func:`cegalprizm.pythontool.WellLog.set_values` or calling
        :func:`cegalprizm.pythontool.LogSamples.clone` object to create a
        'disconnected' `LogSamples`.  When disconnected, setting the
        values individually is speedy. You can then use the `samples`
        property to assign the `LogSamples` object to the well.

        Raises:
            PythonToolException: if the log is read-only
            ValueError: if the log is discrete and the value is not an integer

        """
        return self._value

    @value.setter
    def value(self, v):
        if v is not None and self._is_discrete and not isinstance(v, int):
            raise ValueError("can only set integer values or None for a discrete well log")

        v2 = v
        if v2 is None:
            v2 = self._missing_value
        self._value = v

class LogSamples(object):
    """An object containing all the samples for a particular well log

    A ``LogSamples`` object contains multiple :class:`cegalprizm.pythontool.LogSample` objects.
    These can be iterated over, accessed by index, or queried by measured-depth.

    **Example**:

    .. code-block:: python

      # print all the samples' measured depths and values
      for sample in mylog.samples:
          print(sample.md, " --> ", sample.value)

      # print the 100th sample
      print(mylog.samples[99])

      # print the sample with measured depth 1000
      # n.b if there is no sample at that depth, None is returned
      print(mylog.samples.at(1000))

    """

    def __init__(self, samples):
        self._samples = samples

    def at(self, md: float) -> typing.Optional[LogSample]:
        """The log sample at the specified measured depth

        Args:
            md: the measured depth

        Returns:
            The log sample, or `None` if no sample is at that depth.

        """
        for s in self:
            if _utils.about_equal(s.md, md):
                return s
        return None

    def __getitem__(self, idx: int) -> LogSample:
        return self._samples[idx] # type: ignore

    def __iter__(self) -> typing.Iterator[LogSample]:
        idx = 0
        while idx < len(self._samples):
            yield self._samples[idx]
            idx += 1

    def __len__(self) -> int:
        return len(self._samples)

    def __str__(self) -> str:
        return "LogSamples(welllog=%s, count=%s)" % ("disconnected", len(self._samples))

    def __repr__(self) -> str:
        return str(self)

class WellLog(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithDeletion):
    """A class holding information about a continuous well log"""

    def __init__(self, petrel_object_link: "WellLogGrpc"):
        super(WellLog, self).__init__(petrel_object_link)
        self._welllog_object_link = petrel_object_link
        self._samples: typing.Optional["LogSamples"] = None

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="WellLog")
    def crs_wkt(self):
        return "Well-known text representation of coordinate reference systems not available for WellLog objects."

    def __str__(self) -> str:
        """A readable representation of the Well Log"""
        return 'WellLog(petrel_name="{0}")'.format(self.petrel_name)

    @property
    def well(self) -> typing.Optional["Well"]:
        """The well to which this log is measured down

        Returns:
            cegalprizm.pythontool.Well: the well for this log"""
        py_well = self._welllog_object_link.GetParentPythonBoreholeObject()
        if py_well:
            return borehole.Well(py_well)
        else:
            return None

    @property
    def unit_symbol(self) -> typing.Optional[str]:
        """The symbol for the unit which the values are measured in

        Returns:

            string: The symbol for the unit, or None if no unit is used
        """
        return _utils.str_or_none(self._welllog_object_link.GetDisplayUnitSymbol())

    @property
    def global_well_log(self) -> "GlobalWellLog":
        """The global well log this log is an instance of

        Returns:
            cegalprizm.pythontool.GlobalWellLog: the global well log for this log"""
        return GlobalWellLog(self._welllog_object_link.GetGlobalWellLog())

    @_docstring_utils.clone_docstring_decorator(return_type="WellLog", respects_subfolders=True, continuous_template=True, is_well_log=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, template: "Template" = None) -> "WellLog":
        _utils.verify_continuous_clone(copy_values, template)
        return typing.cast("WellLog", self._clone(name_of_clone, copy_values = copy_values, template = template))

    def _refresh_samples(self):
        cs_samples = self._petrel_object_link.Samples()
        if cs_samples is None:
            cs_samples = []
        disconnected_samples = [
            LogSample(
                s.Md, s.X, s.Y, s.ZMd, s.ZTwt, s.ZTvdss, s.ZTvd, s.Value, False
            )
            for s in cs_samples
        ]

        self._samples = LogSamples(disconnected_samples)

    @property
    def samples(self) -> LogSamples:
        """Gets or sets the log samples in the form of a :class:`cegalprizm.pythontool.LogSamples` object.
            The new LogSamples object is disconnected from any Petrel object.

        Note: 
            It is recommened to use the method .set_values() instead when working with WellLogs.

        Raises:
            PythonToolException: if the log is readonly
            ValueError: if the supplied value is not a `cegalprizm.pythontool.LogSamples` object
        """
        if self._samples is None:
            self._refresh_samples()
        return self._samples

    @samples.setter
    def samples(self, logsamples: LogSamples) -> None:
        if self.readonly:
            raise exceptions.PythonToolException("Log is readonly")
        if not isinstance(logsamples, LogSamples):
            raise ValueError("Value supplied is not a LogSamples object")
        mds = []
        values = []
        for s in logsamples:
            mds.append(s.md)
            values.append(s.value)
        self.set_values(mds, values)

    def set_values(self, mds: typing.List[float], values: typing.List[typing.Optional[float]]) -> None:
        """Replaces all the log samples with the supplied measured depths and values

        Args:
            mds: a list of measured depths, one per sample
            values: a list of values, one per sample

        Raises:
            PythonToolException: if the log is readonly
            ValueError: if the measured depths and values are of difference lengths
            """
        if self.readonly:
            raise exceptions.PythonToolException("Log is readonly")
        if len(mds) != len(values):
            raise ValueError("mds and values must be the same length")

        vals = [v if v is not None else self.missing_value for v in values]

        self._welllog_object_link.SetSamples(_utils.float64array(mds), _utils.float64array(vals))
        self._samples = None

    def as_dataframe(self) -> pd.DataFrame:
        """The values of the log as a Pandas DataFrame."""
        samples_generator = (
            (s.position.x, s.position.y, s.position.z, s.md, s.twt, s.tvdss, s.tvd, s.value)
            for s in self.samples
        )
        df = pd.DataFrame(
            samples_generator, columns=["X", "Y", "Z", "MD", "TWT", "TVDSS", "TVD", "Value"]
        )
        return df

    @_docstring_utils.log_as_array_decorator
    def as_array(self) -> 'np.array':
        return self._welllog_object_link.GetLogValues()

    @_docstring_utils.log_as_tuple_decorator
    def as_tuple(self, depth_index: str = "MD") -> typing.Tuple['np.array', 'np.array']:
        return self._welllog_object_link.GetTupleValues(depth_index)

    @property
    def missing_value(self) -> float:
        """The value interpreted by Petrel as a 'missing' one"""
        return float("nan")
    
    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

class GlobalWellLog(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion):
    def __init__(self, python_petrel_global_well_log: "GlobalWellLogGrpc"):
        super(GlobalWellLog, self).__init__(python_petrel_global_well_log)
        self._logs: typing.Optional[Logs] = None
        self._globalwelllog_object_link = python_petrel_global_well_log

    def retrieve_history(self):
        """DeprecationWarning: retrieve_history() not available for GlobalWellLog objects. This method will be removed in Python Tool Pro 3.0.
        """
        warn("retrieve_history() not available for GlobalWellLog objects. This method will be removed in Python Tool Pro 3.0.", DeprecationWarning, stacklevel=2)
        print("History not available for this object type.")

    def create_well_log(self, well: "Well") -> WellLog:
        """Creates a well log for a well which is assigned to the global well log.

        Args:
            well (Well): The well object for which the well log is to be created.

        Returns:
            A cegalprizm.pythontool.WellLog object
        """   
        var = self._globalwelllog_object_link.CreateWellLog(well)
        return WellLog(var)

    def log(self, well_name: str) -> typing.Union["WellLog", typing.List["WellLog"]]:
        """The well log for the well specified, or a list of well logs if multiple matches for wells with the same name are found.

        Args: 
            well_name: The Petrel name of the well
    
        Returns:
            One or more :class:`WellLog` object(s)
        """

        well_log_grpc_list = self._globalwelllog_object_link.GetWellLogByBoreholeName(well_name)
        if len(well_log_grpc_list) == 0:
            raise exceptions.PythonToolException("Cannot find log for the given well_name: " + well_name)
        elif len(well_log_grpc_list) == 1:
            return WellLog(well_log_grpc_list[0])
        else:
            return [WellLog(well_log_grpc) for well_log_grpc in well_log_grpc_list]

    @property
    def logs(self) -> "Logs":
        """An iterable collection of well logs of the GlobalWellLog.
        
        Returns:
            cegalprizm.pythontool.Logs: the logs of the GlobalWellLog.

        **Example**:

        .. code-block:: python

            gwl = petrel_connection.global_well_logs.get_by_name("GammaRay")

            ## Get the WellLog for a specific well by the well name
            well_log = gwl.logs["Well 1"]

            ## Iterate through all the WellLogs in the GlobalWellLog
            for log in gwl.logs:
                print(log)

        """      
        if self._logs is None:
            self._logs = Logs(self)
        return self._logs

    @_docstring_utils.clone_docstring_decorator(return_type="GlobalWellLog", respects_subfolders=True, continuous_template=True, is_global_well_log=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, template: "Template" = None, folder: "GlobalWellLogFolder" = None) -> "GlobalWellLog":
        if(copy_values is True):
            warn("The copy_values argument is not implemented for GlobalWellLog objects and will be removed in Python Tool Pro version 3.0.", DeprecationWarning, stacklevel=2)
        _utils.verify_continuous_clone(copy_values, template)
        _utils.verify_globalwelllogfolder(folder)
        return typing.cast("GlobalWellLog", self._clone(name_of_clone, copy_values = copy_values, template = template, destination = folder))

    def __str__(self) -> str:
        """A readable representation of the Global Well Log"""
        return 'GlobalWellLog(petrel_name="{0}")'.format(self.petrel_name)

    @property
    def unit_symbol(self) -> typing.Optional[str]:
        """The symbol for the unit which the values are measured in

        Returns:

            string: The symbol for the unit, or None if no unit is used
        """
        return _utils.str_or_none(self._globalwelllog_object_link.GetDisplayUnitSymbol())
    
    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

    @property
    def parent_folder(self) -> typing.Union["GlobalWellLogFolder"]:
        """Returns the parent folder of this GlobalWellLog in Petrel.

        Returns:
            :class:`GlobalWellLogFolder`: The parent folder of the GlobalWellLog.

        **Example**:

        .. code-block:: python

            gwl = petrel_connection.global_well_logs["Input/Wells/Global well logs/Subfolder/GlobalLog"]
            gwl.parent_folder
            >> GlobalWellLogFolder(petrel_name="Subfolder")
        """
        return self._parent_folder

class DiscreteGlobalWellLog(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion):
    def __init__(self, python_petrel_global_well_log: "DiscreteGlobalWellLogGrpc"):
        super(DiscreteGlobalWellLog, self).__init__(python_petrel_global_well_log)
        self._logs: typing.Optional[Logs] = None
        self._discreteglobalwelllog_object_link = python_petrel_global_well_log
        self._discrete_codes: typing.Dict[int, str] = None

    def retrieve_history(self):
        """DeprecationWarning: retrieve_history() not available for DiscreteGlobalWellLog objects. This method will be removed in Python Tool Pro 3.0.
        """
        warn("retrieve_history() not available for DiscreteGlobalWellLog objects. This method will be removed in Python Tool Pro 3.0.", DeprecationWarning, stacklevel=2)
        print("History not available for this object type.")

    def create_well_log(self, well: "Well") -> "DiscreteWellLog":
        """Creates a discrete well log for a well which is assigned to the global discrete well log.

        Args:
            well (Well): The well object for which the well log is to be created.

        Returns:
            A cegalprizm.pythontool.DiscreteWellLog object
        """
        var = self._discreteglobalwelllog_object_link.CreateDictionaryWellLog(well)
        return DiscreteWellLog(var)

    def log(self, well_name: str) -> typing.Union["DiscreteWellLog", typing.List["DiscreteWellLog"]]:
        """The discrete well log for the well specified, or a list of discrete well logs if multiple matches for wells with the same name are found.

        Args: 
            well_name: The Petrel name of the well
    
        Returns:
            One or more :class:`DiscreteWellLog` object(s)
        """
        disc_well_log_grpc_list = self._discreteglobalwelllog_object_link.GetWellLogByBoreholeName(well_name)
        if len(disc_well_log_grpc_list) == 0:
            raise exceptions.PythonToolException("Cannot find \""+ self.petrel_name + "\" log for the given well_name: \"" + well_name + "\"")
        elif len(disc_well_log_grpc_list) == 1:
            return DiscreteWellLog(disc_well_log_grpc_list[0])
        else:
            return [DiscreteWellLog(disc_well_log_grpc) for disc_well_log_grpc in disc_well_log_grpc_list]

    @property
    def logs(self) -> "Logs":
        """An iterable collection of discrete well logs of the DiscreteGlobalWellLog.
        
        Returns:
            cegalprizm.pythontool.Logs: the discrete logs of the DiscreteGlobalWellLog.

        **Example**:

        .. code-block:: python

            gwl = petrel_connection.discrete_global_well_logs.get_by_name("Facies")

            ## Get the DiscreteWellLog for a specific well by the well name
            well_log = gwl.logs["Well 1"]

            ## Iterate through all the WellLogs in the DiscreteGlobalWellLog
            for log in gwl.logs:
                print(log)

        """ 
        if self._logs is None:
            self._logs = Logs(self)
        return self._logs

    @_docstring_utils.clone_docstring_decorator(return_type="DiscreteGlobalWellLog", respects_subfolders=True, discrete_template=True, is_global_well_log=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, discrete_template: "DiscreteTemplate" = None, folder: "GlobalWellLogFolder" = None) -> "DiscreteGlobalWellLog":
        if(copy_values is True):
            warn("The copy_values argument is not implemented for DiscreteGlobalWellLog objects and will be removed in Python Tool Pro version 3.0.", DeprecationWarning, stacklevel=2)
        _utils.verify_discrete_clone(copy_values, discrete_template)
        _utils.verify_globalwelllogfolder(folder)
        return typing.cast("DiscreteGlobalWellLog", self._clone(name_of_clone, copy_values = copy_values, template = discrete_template, destination = folder))


    def __str__(self) -> str:
        """A readable representation of the Discrete Global Well Log"""
        return 'DiscreteGlobalWellLog(petrel_name="{0}")'.format(self.petrel_name)
    
    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

    def discrete_codes(self) -> typing.Dict[int, str]:
        """A dictionary of discrete codes and values. Changes to this dictionary will not be persisted or affect any Petrel objects.

        **Example**:

        .. code-block:: Python

            mylog = petrellink.discrete_global_well_logs["Input/Path/To/Log"]
            print(mylog.discrete_codes[1])
            >> 'Fine sand'

        Returns:
            dict: A dictionary of discrete codes and values.

        """
        if self._discrete_codes is None:
            self._discrete_codes = _utils.get_discrete_codes_dict(self._discreteglobalwelllog_object_link.GetAllDictionaryCodes())
        return self._discrete_codes

    @property
    def parent_folder(self) -> typing.Union["GlobalWellLogFolder"]:
        """Returns the parent folder of this DiscreteGlobalWellLog in Petrel.

        Returns:
            :class:`GlobalWellLogFolder`: The parent folder of the DiscreteGlobalWellLog.

        **Example**:

        .. code-block:: python

            gwl = petrel_connection.global_well_logs["Input/Wells/Global well logs/Subfolder/GlobalLog"]
            gwl.parent_folder
            >> GlobalWellLogFolder(petrel_name="Subfolder")
        """
        return self._parent_folder

class DiscreteWellLog(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithDeletion):
    """A class holding information about a discrete well log."""

    def __init__(self, python_petrel_welllog: "DiscreteWellLogGrpc"):
        super(DiscreteWellLog, self).__init__(python_petrel_welllog)
        self._samples = None
        self._discrete_codes: typing.Optional[typing.Dict[int, str]] = None
        self._discretewelllog_object_link = python_petrel_welllog

    def __str__(self) -> str:
        """A readable representation of the Well Log"""
        return 'DiscreteWellLog(petrel_name="{0}")'.format(self.petrel_name)

    @property
    def well(self) -> "Well":
        """The well to which this log is measured down

        Returns:
            cegalprizm.pythontool.Well: the well for this log"""
        return borehole.Well(self._discretewelllog_object_link.GetParentPythonBoreholeObject())

    @property
    def unit_symbol(self) -> None:
        """The symbol for the unit which the values are measured in

        Returns:

            string: The symbol for the unit, or None if no unit is used
        """    
        return None

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="DiscreteWellLog")
    def crs_wkt(self):
        return "Well-known text representation of coordinate reference systems not available for DiscreteWellLog objects."

    @_docstring_utils.clone_docstring_decorator(return_type="DiscreteWellLog", respects_subfolders=True, discrete_template=True, is_well_log=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, discrete_template: "DiscreteTemplate" = None) -> "DiscreteWellLog":
        _utils.verify_discrete_clone(copy_values, discrete_template)
        return typing.cast("DiscreteWellLog", self._clone(name_of_clone, copy_values = copy_values, template = discrete_template))

    def _refresh_samples(self):
        cs_samples = self._petrel_object_link.Samples()
        if cs_samples is None:
            cs_samples = []
        disconnected_samples = [
            LogSample(
                s.Md, s.X, s.Y, s.ZMd, s.ZTwt, s.ZTvdss, s.ZTvd, s.Value, True
            )
            for s in cs_samples
        ]

        self._samples = LogSamples(disconnected_samples)

    @property
    def samples(self) -> LogSamples:
        """Gets or sets the log samples in the form of a :class:`cegalprizm.pythontool.LogSamples` object

        Raises:
            PythonToolException: if the log is readonly
            ValueError: if the supplied value is not a `cegalprizm.pythontool.LogSamples` object
        """
        if self._samples is None:
            self._refresh_samples()
        return self._samples

    @samples.setter
    def samples(self, logsamples: LogSamples):
        if self.readonly:
            raise exceptions.PythonToolException("Log is readonly")
        if not isinstance(logsamples, LogSamples):
            raise ValueError("Value supplied is not a LogSamples object")
        mds = []
        values = []
        for s in logsamples:
            mds.append(s.md)
            values.append(s.value)
        self.set_values(mds, values)

    def set_values(self, mds: typing.List[float], values: typing.List[typing.Optional[float]]):
        """Replaces all the log samples with the supplied measured depths and values

        Args:
            mds: a list of measured depths, one per sample
            values: a list of values, one per sample

        Raises:
            PythonToolException: if the log is readonly
            ValueError: if the measured depths and values are of difference lengths
        """
        if len(mds) != len(values):
            raise ValueError("mds and values must be the same length")
        if self.readonly:
            raise exceptions.PythonToolException("Log is readonly")

        vals = [v if not ((v is None) or (math.isnan(v))) else self.missing_value for v in values]

        self._discretewelllog_object_link.SetSamples(_utils.float64array(mds), _utils.intarray(vals))
        self._samples = None

    @property
    def discrete_codes(self) -> typing.Dict[int, str]:
        """A dictionary of discrete codes and values

        Changes to this dictionary will not be persisted or affect any Petrel objects.

        **Example:**

        .. code-block:: Python

            mylog = petrellink.welllog['facies']
            print(mylog.discrete_codes[1])
            # outputs 'Fine sand'
        """
        if self._discrete_codes is None:
            self._discrete_codes = _utils.get_discrete_codes_dict(self._discretewelllog_object_link.GetAllDictionaryCodes())
        return self._discrete_codes

    @property
    def global_well_log(self) -> DiscreteGlobalWellLog:
        """The global well log this log is an instance of

        Returns:
            cegalprizm.pythontool.DiscreteGlobalWellLog: the global well log for this log"""
        return DiscreteGlobalWellLog(self._discretewelllog_object_link.GetGlobalWellLog())

    def __value_text(self, sample):
        value_text = self.discrete_codes[sample.value] if sample.value in self.discrete_codes else "" 
        if value_text == "" and sample.value is not None and sample.value < 0:
            value_text = "UNDEF"
        return value_text

    def as_dataframe(self) -> pd.DataFrame:
        """The values of the log as a Pandas DataFrame."""
        import pandas as pd

        samples_unpacked = (
            (
                s.position.x,
                s.position.y,
                s.position.z,
                s.md,
                s.twt,
                s.tvdss,
                s.tvd,
                s.value,
                self.__value_text(s),
            )
            for s in self.samples
        )
        df = pd.DataFrame(
            samples_unpacked, columns=["X", "Y", "Z", "MD", "TWT", "TVDSS", "TVD", "Value", "ValueText"]
        )
        return df

    @_docstring_utils.log_as_array_decorator
    def as_array(self) -> 'np.array':
        return self._discretewelllog_object_link.GetLogValues()

    @_docstring_utils.log_as_tuple_decorator
    def as_tuple(self, depth_index: str = "MD") -> typing.Tuple['np.array', 'np.array']:
        return self._discretewelllog_object_link.GetTupleValues(depth_index)

    @property
    def missing_value(self) -> int:
        """The value interpreted by Petrel as a 'missing' one"""
        return _config._INT32MAXVALUE

    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

class Logs(object):
    """An iterable collection of :class:`cegalprizm.pythontool.WellLog` and :class:`cegalprizm.pythontool.DiscreteWellLog`
    objects for the logs belonging to this well."""

    def __init__(self, parent):
        # import here to break cyclical dependecy welllog -> borehole -> welllog
        from cegalprizm.pythontool import WellLog, DiscreteWellLog, Well

        if isinstance(parent, Well):
            self._parent_is_well = True
            borehole = parent
            self._logs = [
                WellLog(log)
                for log in borehole._borehole_object_link.GetAllContinuousLogs()
            ]
            self._logs.extend(
                [
                    DiscreteWellLog(log)
                    for log in borehole._borehole_object_link.GetAllDictionaryLogs()
                ]
            )
        elif isinstance(parent, GlobalWellLog):
            self._parent_is_well = False
            gwl = parent
            self._logs = [
                WellLog(cs_welllog)
                for cs_welllog in gwl._globalwelllog_object_link.GetAllWellLogs()
            ]
        elif isinstance(parent, DiscreteGlobalWellLog):
            self._parent_is_well = False
            gwl = parent
            self._logs = [
                DiscreteWellLog(cs_welllog)
                for cs_welllog in gwl._discreteglobalwelllog_object_link.GetAllWellLogs()
            ]
        else:
            raise TypeError(
                "Parent must be Well, GlobalWellLog or DiscreteGlobalWellLog"
            )
        self._parent_obj = parent

    def __getitem__(self, key: str) -> typing.Union[WellLog, DiscreteWellLog]:
        def key_extractor_log_name(log):
            return log.petrel_name

        def key_extractor_well_name(log):
            return log.well.petrel_name

        # if the Logs owner is a well, then the logs are of different name and we'd be searching by name,
        # if the owner is a Global Well Log then the logs are of the same name and we'd be searching by borehole
        key_func = (
            key_extractor_log_name
            if self._parent_is_well
            else key_extractor_well_name
        )
        matching = [log for log in self._logs if key_func(log) == key]
        if len(matching) == 1:
            return matching[0] # type: ignore
        else:
            raise KeyError("Cannot find unique log name " + key)

    def __iter__(self) -> typing.Iterator[typing.Union[WellLog, DiscreteWellLog]]:
        return iter(self._logs)

    def __len__(self) -> int:
        return len(self._logs)

    def __str__(self) -> str:
        return 'Logs({0}="{1}")'.format(self._parent_obj._petrel_object_link._sub_type, self._parent_obj)
    
    def __repr__(self) -> str:
        return str(self)