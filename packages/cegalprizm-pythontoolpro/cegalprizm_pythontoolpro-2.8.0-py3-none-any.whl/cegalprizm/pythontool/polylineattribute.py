# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import typing
import numpy as np
from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, exceptions
from cegalprizm.pythontool import PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion
from cegalprizm.pythontool.grpc import utils

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool import PolylineSet
    from cegalprizm.pythontool.grpc.polylineattribute_grpc import PolylineAttributeGrpc

class PolylineAttribute(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    """A class holding information about a PolylineAttribute"""

    def __init__(self, petrel_object_link: "PolylineAttributeGrpc", parent_polylineset: "PolylineSet" = None):
        super(PolylineAttribute, self).__init__(petrel_object_link)
        self._polylineattribute_object_link = petrel_object_link
        self._guid = petrel_object_link._guid
        self._parent_polylineset = petrel_object_link.GetAttributeParent() if parent_polylineset is None else parent_polylineset
        self._parent_guid = self._parent_polylineset._polylineset_object_link._guid
        self._unique_name = petrel_object_link._unique_name

    def __str__(self) -> str:
        """A readable representation"""
        return 'PolylineAttribute(unique_name="{0}")'.format(self._unique_name)
    
    def _get_name(self) -> str:
        return self._unique_name
    
    @property
    def path(self) -> str:
        """ The path of this object in Petrel. Neither the Petrel name nor the path is guaranteed to be unique.
        
        Returns:
            str: The path of the Petrel object"""
        parent_path = self._parent_polylineset.path
        return parent_path + '/Attributes/' + self.petrel_name
    
    @property
    def polylineset(self) -> "PolylineSet":
        """Returns the parent PolylineSet"""
        return self._parent_polylineset
    
    @property
    def is_well_known_attribute(self) -> bool:
        """Returns True if the attribute is a predefined (native) attribute object in Petrel.
        
        Returns:
            bool: True if the attribute is a predefined (native) attribute object in Petrel. False if not.
        """
        return self._polylineattribute_object_link.IsWellKnownAttribute()
    
    def as_array(self) -> 'np.array':
        """ Returns a numpy array with the values of the PolylineAttribute. Each value corresponds to one Polyline in the PolylineSet.
        
        **Example**:

        Get the values of an existing attribute

        .. code-block:: python

            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
            my_attribute = polylineset.attributes["My Attribute"]
            values = my_attribute.as_array()

        Returns:
            np.array: A numpy array with the values of the PolylineAttribute
        """
        return self._polylineattribute_object_link.GetIndividualAttributeValues(self._parent_guid)
    
    def set_values(self, values: typing.Union[np.array, typing.List]) -> None:
        """ Set the values of the PolylineAttribute. Each value corresponds to one Polyline in the PolylineSet.

        The length of the input array (or list) must match the number of Polylines in the PolylineSet, and the data type must match the type of the attribute.
        
        Args:
            values (np.array | list): A numpy array (or list) with the values of the PolylineAttribute

        **Example**:

        Update the first value of an existing attribute

        .. code-block:: python

            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
            my_attribute = polylineset.attributes["My Attribute"]
            values = my_attribute.as_array()

            values[0] = 1234.56
            
            polylineset.readonly = False
            my_attribute.set_values(values)

        **Example**:

        Set the values after adding an attribute

        .. code-block:: python
        
            import numpy as np
        
            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
            new_attribute = polylineset.add_attribute("New String Attribute", "string")

            values = ["FirstString", "SecondString", "ThirdString"]
            
            polylineset.readonly = False
            my_attribute.set_values(values)

        Raises:
            PythonToolException: If the parent PolylineSet is readonly
            ValueError: If the input array does not contain any data.
            ValueError: If the number of elements in the input array does not match the number of Polylines in the PolylineSet
            ValueError: If the input data type does not match expected data type
        """
        if self._parent_polylineset.readonly:
            raise exceptions.PythonToolException("PolylineSet is readonly")
        utils.check_input_contains_data(values)

        current_array = self.as_array()
        self._check_input_data_has_correct_length(current_array, len(values))
        currentPropType = utils.GetPropTypeForValue(current_array[0])
        utils.check_input_has_expected_data_type(values, currentPropType)

        self._polylineattribute_object_link.SetIndividualAttributeValues(self._parent_guid, values)

    def _check_input_data_has_correct_length(self, data: np.array, requiredLength) -> None:
        if len(data) != requiredLength:
            raise ValueError("Number of elements in array must match number of Polylines in PolylineSet")