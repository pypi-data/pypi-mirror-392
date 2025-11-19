# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




from cegalprizm.pythontool import _docstring_utils, _utils
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithDomain, PetrelObjectWithHistory
from cegalprizm.pythontool.petrelobject import PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion
from cegalprizm.pythontool.exceptions import PythonToolException
import numpy as np
import pandas as pd
import typing

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.wavelet_grpc import WaveletGrpc
    from cegalprizm.pythontool import Folder

class Wavelet(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithDomain, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion):
    """A class holding information about a wavelet"""
    def __init__(self, python_petrel_property:"WaveletGrpc"):
        super(Wavelet, self).__init__(python_petrel_property)
        self._wavelet_object_link = python_petrel_property

    @property
    def amplitudes(self) -> 'np.array':
        """ Returns the amplitudes of the wavelet object as a numpy array"""
        amplitudes = [v for v in self._wavelet_object_link.Amplitudes()] # numpy.array[float]
        return np.array(amplitudes)

    @amplitudes.setter
    def amplitudes(self, values: typing.Iterable[float]) -> None:
        self._wavelet_object_link.SetAmplitudes(values)

    @property
    def sample_count(self) -> int:
        """ The number of samples contained in the Wavelet object.

        returns:
            The number of points in the wavelet.

        """
        sample_count = self._wavelet_object_link.SampleCount() # int
        return sample_count

    @property
    def sampling_interval(self) -> float:
        sampling_interval = self._wavelet_object_link.SamplingInterval() # float
        return sampling_interval
    
    @sampling_interval.setter
    def sampling_interval(self, value: float) -> None:
        """ Returns the sampling rate of the wavelet object as a float"""
        if value <= 0:
            raise PythonToolException("Wavelet sampling interval must be positive")
        self._wavelet_object_link.SetSamplingInterval(value) 

    @property
    def sampling_start(self) -> float:
        """ Returns the first time value of the wavelet object as a float"""
        sampling_start  = self._wavelet_object_link.SamplingStart() # float
        return sampling_start

    @sampling_start.setter
    def sampling_start(self, value: float) -> None:
        self._wavelet_object_link.SetSamplingStart(value)

    @property
    def sample_points(self) -> "np.ndarray":
        """ Returns the time values of the wavelet object as a numpy array"""
        sample_points = [v for v in self._wavelet_object_link.SamplePoints()] # numpy.array[float]
        return np.array(sample_points)

    @property
    def time_unit_symbol(self) -> str:
        """Returns the time unit of the wavelet object"""        
        time_unit_symbol = self._wavelet_object_link.TimeUnitSymbol() # str
        return time_unit_symbol

    def as_dataframe(self) -> pd.DataFrame:
        """The values of the position and amplitude of the wavelet as a Pandas DataFrame"""
        positions = [v for v in self._wavelet_object_link.SamplePoints()] # numpy.array[float]
        amplitudes = [v for v in self._wavelet_object_link.Amplitudes()] # numpy.array[float]
        data = {'position': positions, 'amplitude': amplitudes}
        return pd.DataFrame.from_dict(data)  
    
    def set(self, amplitudes: typing.Iterable[float], 
            sampling_start: typing.Optional[float] = None, 
            sampling_interval: typing.Optional[float] = None) -> None:
        """Replaces all the wavelet amplitude with the supplied values

        Args:
            amplitudes: a list of the amplitude values
            sampling_start: the starting values of the wavelet. Defaults to None.
            sampling_interval: the sampling interval of the wavelet. Defaults to None.

        Raises:
            PythonToolException: Wavelet sampling interval must be positive
        """ 
        if sampling_interval and sampling_interval <= 0:
            raise PythonToolException("Wavelet sampling interval must be positive")
        
        ok = self._wavelet_object_link.SetAmplitudes(amplitudes)
        if sampling_start:
            ok &= self._wavelet_object_link.SetSamplingStart(sampling_start)
        
        if sampling_interval:
            ok &= self._wavelet_object_link.SetSamplingInterval(sampling_interval) 

    def __str__(self) -> str:
        return 'Wavelet(petrel_name="{0}")'.format(self.petrel_name)

    @_docstring_utils.clone_docstring_decorator(return_type="Wavelet", supports_folder = True)
    def clone(self, name_of_clone: str, copy_values: bool = False, folder: "Folder" = None) -> "Wavelet":
        _utils.verify_folder(folder)
        return typing.cast("Wavelet", self._clone(name_of_clone, copy_values = copy_values, destination = folder))

    @_docstring_utils.move_docstring_decorator(object_type="Wavelet")
    def move(self, destination: "Folder"):
        if self.readonly:
            raise PythonToolException("Wavelet is readonly")
        _utils.verify_folder(destination)
        self._move(destination)

    @property
    def parent_folder(self) -> typing.Union["Folder", None]:
        """Returns the parent folder of this Wavelet in Petrel. Returns None if the object is the Input root.

        Returns:
            :class:`Folder` or None: The parent folder of the Wavelet, or None if the object is located at the root level.

        **Example**:

        .. code-block:: python

            wavelet = petrel_connection.surfaces["Input/Folder/Wavelet"]
            wavelet.parent_folder
            >> Folder(petrel_name="Folder")
        """
        return self._parent_folder