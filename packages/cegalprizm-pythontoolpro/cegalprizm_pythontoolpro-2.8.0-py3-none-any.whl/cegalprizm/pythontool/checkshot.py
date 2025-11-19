# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, _utils
from cegalprizm.pythontool import PetrelObjectWithParentFolder, PetrelObjectWithDeletion
from cegalprizm.pythontool.borehole import Well
from cegalprizm.pythontool import savedsearch
import typing
from typing import List
import pandas as pd


if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.checkshot_grpc import CheckShotGrpc
    from cegalprizm.pythontool import GlobalWellLogFolder

class CheckShot(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion):
    def __init__(self, petrel_object_link: "CheckShotGrpc"):
        super(CheckShot, self).__init__(petrel_object_link)
        self._petrel_object_link = petrel_object_link

    def __str__(self) -> str:
        return "CheckShot(petrel_name=\"{0}\")".format(self.petrel_name)
    
    def __repr__(self) -> str:
        return str(self)
    
    def as_dataframe(self,
                     include_unconnected_checkshots: bool = True,
                     include_user_defined_properties: bool = True,
                     wells_filter: List[Well] = None) -> pd.DataFrame:
        """Gets a dataframe with information about the CheckShotSamples for this CheckShot.

        **Example**:

        Get a dataframe with information about all CheckShotSamples in the CheckShot.

        .. code-block:: python

            checkshot = petrel_connection.checkshots["Input/Path/To/CheckShot"]
            df = checkshot.as_dataframe()

        **Example**:

        Get a dataframe with information about CheckShotSamples for only those wells that exist in the current Petrel project.

        .. code-block:: python

            checkshot = petrel_connection.checkshots["Input/Path/To/CheckShot"]
            df = checkshot.as_dataframe(include_unconnected_checkshots=False)

        **Example**:

        Get a dataframe with information about CheckShotSamples for two specific wells, excluding user-defined properties.

        .. code-block:: python

            well1 = petrel_connection.wells["Input/Path/To/Well1"]
            well2 = petrel_connection.wells["Input/Path/To/Well2"]
            checkshot = petrel_connection.checkshots["Input/Path/To/CheckShot"]
            df = checkshot.as_dataframe(include_user_defined_properties=False, wells_filter=[well1, well2])

        Args:
            include_unconnected_checkshots (bool, optional): Whether to include CheckShotSamples that are not connected to a well. Defaults to True.
            include_user_defined_properties (bool, optional): Whether to include user-defined properties in the dataframe. Defaults to True.
            wells_filter (List[Well], optional): Include CheckShotSamples from only specific wells by supplying a list of :class:`Well`. Defaults to None, which returns data for all wells.

        Returns:
            DataFrame: A dataframe with information about the CheckShotSamples for this CheckShot.
        """
        wells = _utils.get_wells(wells_filter=wells_filter)
        df = self._petrel_object_link.GetCheckShotDataFrame(include_unconnected_checkshots, wells, include_user_defined_properties)
        return df

    @property
    def parent_folder(self) -> typing.Union["GlobalWellLogFolder"]:
        """Returns the parent folder of this CheckShot in Petrel.

        Returns:
            :class:`GlobalWellLogFolder`: The parent folder of the CheckShot.

        **Example**:

        .. code-block:: python

            cs = petrel_connection.checkshots["Input/Wells/Global well logs/CheckShots/CheckShot 1"]
            cs.parent_folder
            >> GlobalWellLogFolder(petrel_name="CheckShots")
        """
        return self._parent_folder
    
    def get_wells(self, saved_search: savedsearch.SavedSearch = None) -> typing.List["Well"]:
        """Returns a list of wells associated with this CheckShot. Only wells that exist in this Petrel project will be returned.
        The result can be filtered by passing in a :class:`SavedSearch` object, this will return only the subset of wells that also exist in the saved search.

        Args:
            saved_search: Filter the result so that only wells that match the saved search are returned. Defaults to None.

        Returns:
            List[Well]: A list of :class:`Well` objects associated with this CheckShot. If no wells are associated, an empty list is returned.

        Raises:
            TypeError: If saved_search is not a :class:`SavedSearch` object.

        **Example**:

        Get all wells associated with a CheckShot

        .. code-block:: python

            checkshot = petrel_connection.checkshots["Input/Path/To/CheckShot"]
            wells = checkshot.get_wells()

        **Example**:

        Get all wells associated with a CheckShot, filtered by a saved search

        .. code-block:: python

            checkshot = petrel_connection.checkshots["Input/Path/To/CheckShot"]
            my_saved_search = petrel_connection.saved_searches["Input/Wells/Saved searches/My saved search"]
            wells_filtered = checkshot.get_wells(saved_search = my_saved_search)

        """
        if saved_search is not None and not isinstance(saved_search, savedsearch.SavedSearch):
            raise TypeError("saved_search must be a SavedSearch object")

        return [Well(well) for well in self._petrel_object_link.GetWells(saved_search)]