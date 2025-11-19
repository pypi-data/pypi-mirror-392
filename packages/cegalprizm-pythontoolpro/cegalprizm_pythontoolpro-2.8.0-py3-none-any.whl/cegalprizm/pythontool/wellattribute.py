# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from enum import Enum
import typing
from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithDeletion, PetrelObjectWithPetrelNameSetter, _docstring_utils, _utils
from cegalprizm.pythontool.exceptions import PythonToolException
from cegalprizm.pythontool.experimental import experimental_class

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.wellattribute_grpc import WellAttributeGrpc
    from cegalprizm.pythontool.borehole import Well

class WellAttributeFilterEnum(Enum):
    Default = "Default"
    User = "User"
    All = "All"

class WellAttributeType(Enum):
    Continuous = "Continuous"
    Discrete = "Discrete"
    String = "String"
    Datetime = "Datetime"
    Boolean = "Boolean"

@experimental_class
class WellAttribute(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    """
    A class holding information about a WellAttribute
    """

    def __init__(self, petrel_object_link: "WellAttributeGrpc"):
        super(WellAttribute, self).__init__(petrel_object_link)
        self._petrel_object_link = petrel_object_link
        self._unique_name = petrel_object_link._unique_name
        self._droid = petrel_object_link._guid
        self._is_writable = None
        self._is_supported = None
    
    def __str__(self) -> str:
        """A readable representation"""
        if self.petrel_name == self._unique_name:
            return 'WellAttribute(petrel_name="{0}")'.format(self.petrel_name)
        return 'WellAttribute(petrel_name="{0}", unique_name="{1}")'.format(self.petrel_name, self._unique_name)

    def __repr__(self) -> str:
        return str(self)
    
    def _get_name(self) -> str:
        return self.petrel_name
    
    @property
    def is_writable(self) -> bool:
        """Check if the WellAttribute is writable"""
        if self._is_writable is None:
            self._is_writable = self._petrel_object_link.GetAttributeIsWritable()
        return self._is_writable

    @property
    def is_supported(self) -> bool:
        """Indicates whether the WellAttribute is fully supported by the Ocean API.

        Some attributes available in Petrel may not be fully supported via the Ocean API.
        Unsupported attributes do not allow for getting or setting values which limits their use in Python Tool Pro.

        Returns:
            bool: True if the WellAttribute is supported, False otherwise
        """
        if self._is_supported is None:
            self._is_supported = self._petrel_object_link.GetAttributeIsSupported()
        return self._is_supported
    
    def get_value(self, well: "Well") -> typing.Any:
        """  
        Get the value of the WellAttribute for a specific well.

        Args:
            well (Well): The well object to get the attribute value for.

        Returns:
            typing.Any: The value of the WellAttribute for the specified well.

        Raises:
            PythonToolException: If the provided well parameter isn't a Well object
            PythonToolException: If this attribute isn't supported by the Ocean API
        
        **Example**:

        Get the value of a WellAttribute for a specific well:
    
        .. code-block:: python

            petrel = cegalprizm.pythontool.PetrelConnection()
            well = petrel.wells['path/to/well']
            well_attribute = petrel.well_attributes['Input/Wells/Well Attributes/UWI']
            value = well_attribute.get_value(well)
        """

        from cegalprizm.pythontool.borehole import Well
        if not isinstance(well, Well):
            raise PythonToolException(f"Expected a Well object, got {type(well)} instead.")
        if not self.is_supported:
            raise PythonToolException(f"WellAttribute {self._unique_name} is not supported.")
        attribute = self._petrel_object_link.GetAttribute(well.droid)
        return _utils.convert_well_attribute_value(attribute)

    def set_value(self, well: "Well", value: typing.Any) -> None:
        """  
        Set the value of the WellAttribute for a specific well.

        Args:
            well (Well): The well object to set the attribute value for.
            value (typing.Any): The value to set for the WellAttribute.

        Raises:
            PythonToolException: If this attribute is set to read-only
            PythonToolException: If this attribute isn't writable
            PythonToolException: If this attribute isn't supported by the Ocean API
            PythonToolException: If the provided well parameter isn't a Well object
            PythonToolException: If the operation fails for any other reason
        
        **Example**:

        Set the value of a WellAttribute for a specific well:

        .. code-block:: python

            petrel = cegalprizm.pythontool.PetrelConnection()
            well = petrel.wells['path/to/well']
            well_attribute = petrel.well_attributes['Input/Wells/Well Attributes/UWI']
            well_attribute.readonly = False
            well_attribute.set_value(well, 'ExampleUWI123')
        """

        from cegalprizm.pythontool.borehole import Well
        if self.readonly:
            raise PythonToolException(f"WellAttribute {self._unique_name} is read-only.")
        if not self.is_writable:
            raise PythonToolException(f"WellAttribute {self._unique_name} cannot be written to.")
        if not self.is_supported:
            raise PythonToolException(f"WellAttribute {self._unique_name} is not supported.")
        if not isinstance(well, Well):
            raise PythonToolException(f"Expected a Well object, got {type(well)} instead.")
        ok = self._petrel_object_link.SetAttributeValue(well_guid=well.droid,value=[value])
        if not ok:
            raise PythonToolException(f"Failed to set value for WellAttribute {self._unique_name}.")

    @_docstring_utils.get_template_decorator
    def get_template(self):
        return self._get_template()
    
    @property
    def path(self) -> str:
        """Get the path of the well attribute."""
        return "Input/Wells/Well Attributes/{0}".format(self.petrel_name)

@experimental_class
class WellAttributeInstance(object):
    """
    A class holding information about a WellAttributeInstance for a specific well.
    """

    def __init__(self, well_attribute_ref: "WellAttribute", parent_well: "Well"):
        self._petrel_object_link = well_attribute_ref._petrel_object_link
        self.well_attribute = well_attribute_ref
        self.droid = well_attribute_ref.droid
        self._parent_well = parent_well
        self.is_writable = well_attribute_ref.is_writable
        self.is_supported = well_attribute_ref.is_supported
        self.petrel_name = well_attribute_ref.petrel_name
        self._unique_name = well_attribute_ref._unique_name
    
    def __str__(self) -> str:
        """A readable representation"""
        if self.petrel_name == self._unique_name:
            return 'WellAttributeInstance(petrel_name="{0}")'.format(self.petrel_name)
        return 'WellAttributeInstance(petrel_name="{0}", unique_name="{1}")'.format(self.petrel_name, self._unique_name)

    def __repr__(self) -> str:
        return str(self)
    
    def _get_name(self) -> str:
        return self.well_attribute.petrel_name

    @property
    def path(self) -> str:
        """Get the path of the WellAttribute for this WellAttributeInstance.

        Returns:
            str: The full Petrel path to the well attribute in the format 
            'Input/Wells/Well Attributes/{attribute_name}'
        """
        return self.well_attribute.path

    @property
    def readonly(self) -> bool:
        """Check if the WellAttribute is read-only for this WellAttributeInstance.
        
        Returns:
            bool: True if the WellAttribute is read-only, False otherwise.
        """
        return self.well_attribute.readonly
    
    @readonly.setter
    def readonly(self, value: bool) -> None:
        """Set the read-only status of the WellAttribute for this WellAttributeInstance."""
        self.well_attribute.readonly = value
    
    @property
    def value(self):
        """Get the value of the WellAttribute for this WellAttributeInstance.
        
        Returns:
            typing.Any: The value of the WellAttribute for this WellAttributeInstance.
        """
        return self.well_attribute.get_value(self._parent_well)
    
    @value.setter
    def value(self, value: typing.Any) -> None:
        """Set the value of the WellAttribute for this WellAttributeInstance."""
        self.well_attribute.set_value(self._parent_well, value)

    @_docstring_utils.get_template_decorator
    def get_template(self):
        return self.well_attribute.get_template()

    @property
    def template(self):
        """Returns the Petrel template for the object as a string. If no template available, will return an empty string."""
        return self.well_attribute.template

    def get_well_attribute(self) -> "WellAttribute":
        """  
        Get the WellAttribute associated with this WellAttributeInstance.

        Returns:
            WellAttribute: The WellAttribute object associated with this WellAttributeInstance.

        **Example**:

        Get the WellAttribute for this WellAttributeInstance:

        .. code-block:: python

            petrel = cegalprizm.pythontool.PetrelConnection()
            well = petrel.wells['path/to/well']
            well_attribute_instance = well.attributes['UWI']
            well_attribute = well_attribute_instance.get_well_attribute()
        """

        return self.well_attribute