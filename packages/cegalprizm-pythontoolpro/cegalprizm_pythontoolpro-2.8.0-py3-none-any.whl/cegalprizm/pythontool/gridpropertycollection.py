# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import itertools
import typing
from cegalprizm.pythontool import _utils, exceptions
from cegalprizm.pythontool import grid
from cegalprizm.pythontool.grpc.gridpropertycollection_grpc import PropertyFolderGrpc
from cegalprizm.pythontool.enums import NumericDataTypeEnum
from cegalprizm.pythontool.parameter_validation import validate_name
from cegalprizm.pythontool.template import Template, DiscreteTemplate
from . import gridproperty
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithDeletion

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.gridproperty import GridProperty, GridDiscreteProperty
    from cegalprizm.pythontool.grpc.gridpropertycollection_grpc import PropertyCollectionGrpc

class PropertyCollection(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory):
    """
    .. warning::
        **Deprecated** - This Class will be removed in Python Tool Pro 3.0. Use :attr:`PropertyFolder` instead.

    A readonly collection of a set of grid properties, including both continuous and discrete.

    Although this object wraps a Petrel collection, it does not support any operations on it apart from iterating through its contents. 
    It does not support operations to navigate through hierarchies of collections."""
    def __init__(self, petrel_object_link: "PropertyCollectionGrpc"):
        super(PropertyCollection, self).__init__(petrel_object_link)
        self._propertycollection_object_link = petrel_object_link

    @property
    def _continuous_properties(self):
        return [gridproperty.GridProperty(prop) for prop in self._propertycollection_object_link.GetPropertyObjects()]
    
    @property
    def _discrete_properties(self):
        return [gridproperty.GridDiscreteProperty(prop) for prop in self._propertycollection_object_link.GetDictionaryPropertyObjects()]

    def __str__(self) -> str:
        """A readable representation of the PropertyCollection"""
        return "PropertyCollection(petrel_name=\"{0}\")".format(self.petrel_name)

    def __iter__(self) -> typing.Iterator[typing.Union["GridProperty", "GridDiscreteProperty"]]:
        for p in self._continuous_properties:
            yield p
        for p in self._discrete_properties:
            yield p

    def __len__(self) -> int:
        return len(self._continuous_properties) + len(self._discrete_properties)

class PropertyFolder(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    """A class holding information about a property folder."""
    def __init__(self, petrel_object_link: "PropertyFolderGrpc"):
        super(PropertyFolder, self).__init__(petrel_object_link)
        self._object_link = petrel_object_link

    def _continuous_properties(self, recursive: bool = False) -> typing.Iterator["GridProperty"]:
        return (gridproperty.GridProperty(prop) for prop in self._object_link.GetPropertyObjects(recursive))

    def _discrete_properties(self, recursive: bool = False) -> typing.Iterator["GridDiscreteProperty"]:
        return (gridproperty.GridDiscreteProperty(prop) for prop in self._object_link.GetDictionaryPropertyObjects(recursive))

    def __str__(self) -> str:
        """A readable representation of the PropertyFolder"""
        return "PropertyFolder(petrel_name=\"{0}\")".format(self.petrel_name)

    @property
    def grid(self) -> "grid.Grid":
        """The parent grid of the property folder

        Returns:
            cegalprizm.pythontool.Grid: The parent grid of the property folder
        """
        return grid.Grid(self._object_link.GetParentGrid())

    @property
    def parent_folder(self) -> typing.Optional["PropertyFolder"]:
        """The parent property folder of this property folder
        The root property folder `Properties` will return `None`.

        **Example**:

        The root folder's parent folder will return `None`:

        .. code-block:: Python

            # Using a PetrelConnection object:
            property_collection = petrel_connection.grid_property_folders["Models/Structural grids/Model/Properties"]
            parent = property_collection.parent_folder
            # returns 'None' since this is the root folder

            # Using a Grid object:
            property_folder = grid.property_folder
            parent = property_folder.parent_folder
            # returns 'None' since this is the root folder

        **Example**:

        A sub-folder's parent folder will return the parent folder object:

        .. code-block:: Python

            # Using a PetrelConnection object:
            property_folder = petrel_connection.grid_property_folders["Models/Structural grids/Model/Properties/Subfolder"]
            parent = property_folder.parent_folder
            # returns a PropertyFolder object

            # Using a Grid object:
            property_folder = grid.property_folder
            parent = property_folder.parent_folder
            # returns a PropertyFolder object

        Returns:
            cegalprizm.pythontool.PropertyFolder: the parent folder, or `None`"""
        coll = self._object_link.GetParentPropertyCollection()
        if coll is None:
            return None

        return PropertyFolder(coll)

    @property
    def properties(self) -> "gridproperty.GridProperties":
        """Get the properties contained within this PropertyFolder.

        Returns:
            cegalprizm.pythontool.GridProperties: The properties contained within this PropertyFolder.
        """
        return gridproperty.GridProperties(self, False)

    @property
    def property_folders(self) -> "PropertyFolders":
        """Python iterator with the folder of property folders objects within a PropertyFolder.
        Property folders can be iterated over or accessed by index or name.

        **Example**:

        Retrieve the first property folder in a PropertyFolder:

        .. code-block:: Python

            # Using a PetrelConnection object:
            project_grid_property_folders = petrel_connection.grid_property_folders
            first_property_folder = project_grid_property_folders[0]

            # Using a Grid object:
            grid_property_folder = grid.property_folder
            first_property_folder = grid_property_folder.property_folders[0]

        **Example**:

        Iterate over all the property folders from the parent PropertyFolder and print out their name:

        .. code-block:: python

            project_grid_property_folders = petrel_connection.grid_property_folders
            for folder in project_grid_property_folders:
                print(folder.petrel_name)

            # Using a Grid object:
            grid_property_folder = grid.property_folder
            for folder in grid_property_folder.property_folders:
                print(folder.petrel_name)

        Returns:
            cegalprizm.pythontool.PropertyFolder: An iterable collection of property folders.
        """
        return PropertyFolders(self)

    def get_properties(self, data_type: typing.Union[str, "NumericDataTypeEnum"] = None, recursive: bool = False) -> typing.List[typing.Union["GridProperty", "GridDiscreteProperty"]]:
        """Returns a list of the properties in the folder, both continuous and/or discrete.
        If data_type is specified, only properties of that type will be returned.

        Args:
            data_type (str or NumericDataTypeEnum): The type of properties to return. Can be "continuous", "discrete", or None for all properties.
            recursive (bool): Whether to include properties from sub-folders. Defaults to False.

        Raises:
            TypeError: If recursive is not a boolean.
            TypeError: If data_type is not a string or NumericDataTypeEnum.
            ValueError: If data_type is not one of "continuous", "discrete" or None.

        Returns:
            List[Union[GridProperty, GridDiscreteProperty]]: A list of properties in the folder.
        
        **Example**:

        Get all properties in the folder:

        .. code-block:: Python

            # Using a PetrelConnection object:
            property_folder = petrel_connection.grid_property_folders["Models/Structural grids/Model/Properties"]
            all_properties = property_folder.get_properties()

            # Using a Grid object:
            property_folder = grid.property_folder
            all_properties = property_folder.get_properties()

        **Example**:

        Get only continuous properties in the folder:

        .. code-block:: Python

            # Using a PetrelConnection object:
            property_folder = petrel_connection.grid_property_folders["Models/Structural grids/Model/Properties"]
            continuous_properties = property_folder.get_properties(data_type=NumericDataTypeEnum.Continuous)

            # Using a Grid object:
            property_folder = grid.property_folder
            continuous_properties = property_folder.get_properties(data_type="continuous")
            
        **Example**:

        Get only continuous properties in the folder and include properties from sub-folders:

        .. code-block:: Python

            # Using a PetrelConnection object:
            property_folder = petrel_connection.grid_property_folders["Models/Structural grids/Model/Properties"]
            continuous_properties = property_folder.get_properties(data_type=NumericDataTypeEnum.Continuous, recursive=True)

            # Using a Grid object:
            property_folder = grid.property_folder
            continuous_properties = property_folder.get_properties(data_type="continuous", recursive=True)
        """
        if not isinstance(recursive, bool):
            raise TypeError("recursive must be a boolean")

        if data_type is None:
            return list(self._get_grid_properties(recursive=recursive))

        if not isinstance(data_type, (str, NumericDataTypeEnum)):
            raise TypeError("data_type must be a string or NumericDataTypeEnum")

        is_continuous = False
        
        if isinstance(data_type, str):
            data_type_lower = data_type.lower()
            if data_type_lower not in [e.value for e in NumericDataTypeEnum]:
                raise ValueError("data_type must be 'continuous', 'discrete' or None")
            is_continuous = data_type_lower == "continuous"
        else:
            is_continuous = data_type == NumericDataTypeEnum.Continuous

        return list(self._continuous_properties(recursive) if is_continuous else self._discrete_properties(recursive))

    @validate_name(param_name="name", can_be_empty=False)
    def create_property_folder(self, name: str) -> "PropertyFolder":
        """Create a new property folder within this PropertyFolder.

        Args:
            name (str): The name of the new property folder to be created.

        Returns:
            cegalprizm.pythontool.PropertyFolder: The newly created property folder.

        Raises:
            TypeError: If the name argument is not a string.
            ValueError: If the name argument is an empty string.
            ValueError: If the name argument is not a valid string.
            PythonToolException: If the PropertyFolder is readonly.

        **Example**:

        Create a new property folder named "New Folder":

        .. code-block:: Python

                property_folder = grid.property_folder
                property_folder.readonly = False
                new_folder = property_folder.create_property_folder("New Folder")

        **Example**:

        Create a new property folder in sub-folder:

        .. code-block:: Python

                property_folder = grid.property_folder
                property_folder.readonly = False
                new_folder = property_folder.property_folders["Subfolder"].create_property_folder("New Folder")
        """
        if self.readonly:
            raise exceptions.PythonToolException("The PropertyFolder is readonly")
        return self._object_link.CreatePropertyFolder(name)

    @validate_name(param_name="name")
    def create_property(self, name: str = "",
                              data_type: typing.Union[str, "NumericDataTypeEnum"] = None,
                              template: typing.Union[Template, DiscreteTemplate] = None) -> typing.Union["gridproperty.GridProperty", "gridproperty.GridDiscreteProperty"]:
        """Create a new continuous or discrete property within this PropertyFolder.  
        If no name, data_type or template is provided, a continuous property will be created with a default template and name.  
        Providing an incorrect combination of data_type and template will raise an error.

        Args:
            name (str, optional): The name of the new property to be created. If an empty string is provided, a default name will be generated.
            data_type (str or NumericDataTypeEnum, optional): The type of property to create. Can be "continuous" or "discrete". Defaults to None, which means the data_type is inferred from the template, or set to "continuous" if no template is provided.
            template (Template or DiscreteTemplate, optional): The template to use for the new property. Defaults to None, which means the default continuous or discrete template will be used depending on the data_type input.

        Returns:
            GridProperty or GridDiscreteProperty: The newly created object.

        Raises:
            TypeError: If the name argument is not a string.
            ValueError: If the name argument is not a valid string.
            TypeError: If data_type is not a string or NumericDataTypeEnum.
            ValueError: If data_type is not one of "continuous", "discrete" or None.
            TypeError: If the template argument is None.
            TypeError: If the template argument is not of type Template or DiscreteTemplate.
            ValueError: If the template and type arguments are not compatible.
            PythonToolException: If the PropertyFolder is readonly.

        **Example**:

        Create a new continuous property named "New Continuous Property":

        .. code-block:: Python

            property_folder = grid.property_folder
            continuous_template = petrel.templates.get_by_name("Velocity")
            property_folder.readonly = False
            new_property = property_folder.create_property("New Continuous Property", "continuous", continuous_template)

        **Example**:

        Create a new discrete property named "New Discrete Property":
        
        .. code-block:: Python

            from cegalprizm.pythontool import NumericDataTypeEnum
            property_folder = grid.property_folder
            discrete_template = petrel.discrete_templates.get_by_name("Facies")
            property_folder.readonly = False
            new_property = property_folder.create_property("New Discrete Property", NumericDataTypeEnum.Discrete, discrete_template)
        """
        data_type = _utils.get_and_validate_data_type(data_type, template)
        discrete = data_type == NumericDataTypeEnum.Discrete
        _utils.validate_template(template, discrete, "property")
        
        if self.readonly:
            raise exceptions.PythonToolException("The PropertyFolder is readonly")
        grpc_object = self._object_link.CreateProperty(name, template, discrete)

        if discrete:
            return gridproperty.GridDiscreteProperty(grpc_object) if grpc_object else None
        return gridproperty.GridProperty(grpc_object) if grpc_object else None

    def _get_property_folders(self) -> typing.Iterator["PropertyFolder"]:
        """Internal method to get property folders from the Petrel object link.

        Returns:
            An iterator over PropertyFolder objects.
        """
        for coll in self._object_link.GetPropertyCollections():
            yield PropertyFolder(coll)

    def _get_grid_properties(self, recursive: bool) -> typing.Iterable[typing.Union["gridproperty.GridProperty", "gridproperty.GridDiscreteProperty"]]:
        """Internal method to get grid properties from the Petrel object link.

        Returns:
            An iterator over GridProperties objects.
        """
        return itertools.chain(self._continuous_properties(recursive=recursive), self._discrete_properties(recursive=recursive))
    
    def _get_number_of_properties(self, recursive: bool) -> int:
        return self._object_link.GetNumberOfProperties(recursive=recursive)

class PropertyFolders():
    """An iterable collection of :class:`cegalprizm.pythontool.PropertyFolders` objects for the sub property folders belonging to this property folder."""

    def __init__(self, parent_obj: PetrelObject):
        self._parent_obj = parent_obj
        self._property_folders = list(self._parent_obj._get_property_folders())

    def __iter__(self) -> typing.Iterator[PropertyFolder]:
        return iter(self._property_folders)

    def __getitem__(self, key) -> PropertyFolder:
        return _utils.get_item_from_collection_petrel_name(self._property_folders, key)

    def __len__(self) -> int:
        return len(self._property_folders)

    def __str__(self) -> str:
        return 'PropertyFolders({0}="{1}")'.format(self._parent_obj._petrel_object_link._sub_type, self._parent_obj)
    
    def __repr__(self):
        return str(self)