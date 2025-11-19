# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import typing
from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistoryToBeDeprecated, Well
from cegalprizm.pythontool import PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion
from cegalprizm.pythontool import savedsearch
from cegalprizm.pythontool.exceptions import PythonToolException
from cegalprizm.pythontool.parameter_validation import validate_name
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.borehole_collection_grpc import BoreholeCollectionGrpc

class WellFolder(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistoryToBeDeprecated, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion):
    """A class holding information about a well folder (BoreholeCollection)."""

    def __init__(self, petrel_object_link: "BoreholeCollectionGrpc"):
        super(WellFolder, self).__init__(petrel_object_link)
        self._borehole_collection_object_link = petrel_object_link

    def __str__(self) -> str:
        """A readable representation"""
        return 'WellFolder(petrel_name="{0}")'.format(self.petrel_name)

    @property
    def wells(self):
        """
        Python iterator with the well objects for the WellFolder.

        Use to retrieve the :class:`cegalprizm.pythontool.Well` instances from the WellFolder.
        Wells can be iterated over or accessed by index.

        **Example**:

        Retrieve the first well from the WellFolder:

        .. code-block:: python

            well_folder = petrel_connection.well_folders["Input/Path/To/WellFolder"]
            first_well = well_folder.wells[0]

        **Example**:

        Retrieve the first 10 wells from the WellFolder:

        .. code-block:: python

            well_folder = petrel_connection.well_folders["Input/Path/To/WellFolder"]
            first_well = well_folder.wells[0:10]

        **Example**:

        Iterate over all the wells in the folder and print out their name:

        .. code-block:: python

            well_folder = petrel_connection.well_folders["Input/Path/To/WellFolder"]
            for well in well_folder.wells:
                print(well.petrel_name)

        Returns:
            An iterable collection of :class:`cegalprizm.pythontool.Well` objects for the well folder.
        """
        return Wells(self)

    @property
    def well_folders(self):
        """
        Python iterator with the well folder objects within a WellFolder.

        Use to retrieve :class:`cegalprizm.pythontool.WellFolder` instances from a parent WellFolder.
        Well folders can be iterated over or accessed by index.

        **Example**:

        Retrieve the first well folder from the parent WellFolder:

        .. code-block:: python

            parent_wf = petrel_connection.well_folders["Input/Path/To/ParentWellFolder"]
            first_well_folder = parent_wf.well_folders[0]

        **Example**:

        Retrieve the first two well folders from the parent WellFolder:

        .. code-block:: python

            parent_wf = petrel_connection.well_folders["Input/Path/To/ParentWellFolder"]
            first_well_folder = parent_wf.well_folders[0:2]

        **Example**:

        Iterate over all the well folders from the parent WellFolder and print out their name:

        .. code-block:: python

            parent_wf = petrel_connection.well_folders["Input/Path/To/ParentWellFolder"]
            for folder in parent_wf:
                print(folder.petrel_name)

        Returns:
            An iterable collection of :class:`cegalprizm.pythontool.WellFolder` objects for the parent well folder.
        """
        return WellFolders(self)

    def get_wells(self, recursive: bool = False, saved_search: savedsearch.SavedSearch = None) -> typing.List["Well"]:
        """Returns a list of wells in this well folder. Use flag recursive to include wells in sub folders.

        **Example**:

        Get the wells of a well folder

        .. code-block:: python

            well_folder = petrel_connection.well_folders["Input/Wells/Well folder 1"]
            wells_recursive = well_folder.get_wells(recursive=True)

            # Use list comprehension to get a list of wells with a specific name
            wells_named_prod = [well for well in wells_recursive if well.petrel_name == "Production well 1"]

        **Example**:

        Get the wells from the top level of a well folder and filtered by a saved search

        .. code-block:: python

            well_folder = petrel_connection.well_folders["Input/Wells/Well folder 1"]
            my_saved_search = petrel_connection.saved_searches["Input/Wells/Saved searches/My saved search"]
            wells_filtered = well_folder.get_wells(recursive = False, saved_search = my_saved_search)

        Args:
            recursive: If True, all wells in all sub folders will be included. Defaults to False.
            saved_search: Filter the result so that only wells that match the saved search are returned. Defaults to None.
        """
        if saved_search is not None and not isinstance(saved_search, savedsearch.SavedSearch):
            raise TypeError("saved_search must be a SavedSearch object")

        return [Well(well) for well in self._borehole_collection_object_link.GetWells(recursive, saved_search)]

    @property
    def parent_folder(self) -> typing.Union["WellFolder", None]:
        """Returns the parent folder of this WellFolder in Petrel. Returns None if the parent is the Wells root folder.

        Returns:
            :class:`WellFolder` or None: The parent WellFolder of the object, or None if the parent is the Wells root folder.

        **Example**:

        .. code-block:: python

            well_folder = petrel_connection.well_folders["Input/Wells/Well Folder 1"]
            well_folder.parent_folder
            >> WellFolder(petrel_name="Wells")
            well_folder.parent_folder.parent_folder
            >> None
        """
        return self._parent_folder


    @validate_name(param_name="name")
    def create_well_folder(self, name: str = "") -> "WellFolder":
        """Create a new WellFolder with the given name in this WellFolder.

        Args:
            name (str): The name of the new WellFolder. If an empty string is provided, a default name will be generated.

        Returns:
            WellFolder: The newly created WellFolder object.

        Raises:
            TypeError: If the name argument is not a string.
            ValueError: If the name argument is not a valid string.
            PythonToolException: If the parent WellFolder is read-only.

        **Example**:

        Create a new WellFolder in the main Wells folder:

        .. code-block:: python

            main_well_folder = petrel_connection.well_folders["Input/Wells"]
            main_well_folder.readonly = False
            new_well_folder = main_well_folder.create_well_folder("NewWellFolder")

        """
        if self.readonly:
            raise PythonToolException("WellFolder is readonly")
        grpc_object = self._borehole_collection_object_link.CreateBoreholeCollection(name)
        return WellFolder(grpc_object) if grpc_object else None

class WellFolders(object):
    """An iterable collection of :class:`cegalprizm.pythontool.WellFolder` objects for the sub well folders belonging to this well folder."""

    def __init__(self, parent_well_folder):
        if not isinstance(parent_well_folder, WellFolder):
            raise TypeError("parent_well_folder must be a WellFolder object")
        self._parent_well_folder = parent_well_folder
        self._well_folders = [WellFolder(well_folder) for well_folder in parent_well_folder._borehole_collection_object_link.GetBoreholeCollections()]

    def __getitem__(self, key: int) -> "WellFolder":
        return self._well_folders[key]

    def __iter__(self) -> typing.Iterator["WellFolder"]:
        return iter(self._well_folders)

    def __len__(self) -> int:
        return len(self._well_folders)

    def __str__(self) -> str:
        return f'WellFolders(Parent WellFolder="{self._parent_well_folder}")'

    def __repr__(self) -> str:
        return str(self)
        
class Wells(object):
    """An iterable collection of :class:`cegalprizm.pythontool.Well` objects for the wells belonging to this well folder."""

    def __init__(self, parent_well_folder):
        if not isinstance(parent_well_folder, WellFolder):
            raise TypeError("parent_well_folder must be a WellFolder object")
        self._parent_well_folder = parent_well_folder
        self._wells = [Well(well) for well in parent_well_folder._borehole_collection_object_link.GetWells(recursive=False, saved_search=None)]

    def __getitem__(self, key: int) -> "Well":
        return self._wells[key]

    def __iter__(self) -> typing.Iterator["Well"]:
        return iter(self._wells)

    def __len__(self) -> int:
        return len(self._wells)

    def __str__(self) -> str:
        return f'Wells(Parent WellFolder="{self._parent_well_folder}")'

    def __repr__(self) -> str:
        return str(self)
    