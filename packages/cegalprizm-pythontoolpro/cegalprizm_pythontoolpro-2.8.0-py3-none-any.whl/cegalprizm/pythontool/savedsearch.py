# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool import PetrelObject, Well
from cegalprizm.pythontool.exceptions import PythonToolException
import typing
import warnings
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.savedsearch_grpc import SavedSearchGrpc

class SavedSearch(PetrelObject):
    """A class holding information about a Saved Search in Petrel"""

    def __init__(self, petrel_object_link: "SavedSearchGrpc"):
        super(SavedSearch, self).__init__(petrel_object_link)
        self._savedsearch_object_link = petrel_object_link

    def __str__(self):
        """A readable representation of the object"""
        return 'SavedSearch(petrel_name="{0}")'.format(self.petrel_name)

    def retrieve_stats(self) -> typing.Dict[str, str]:
        """Due to limitations in the Ocean API, this function is not implemented for SavedSearch objects.

        Returns:
            Dictionary: An empty dictionary.
        """
        return self._savedsearch_object_link.RetrieveStats()

    def get_wells(self):
        """Returns a list of wells in this saved search.

        **Example**:

        Get the wells of a saved search:

        .. code-block:: python

            saved_search = petrel_connection.saved_searches["Input/Wells/Saved searches/My saved search"]
            wells_in_search = saved_search.get_wells()

            # Use list comprehension to get a list of wells with a specific name
            wells_named_prod = [well for well in wells_in_search if well.petrel_name == "Production well 1"]

        Returns:
            list: A list of :class:`cegalprizm.pythontool.Well` objects in the saved search
        """
        return [Well(well) for well in self._savedsearch_object_link.GetWells()]

    @property
    def is_dynamic(self) -> bool:
        """Boolean property indicating if this saved search is a dynamic (extended) saved search.

        Returns:
            bool: True if the saved search is dynamic, False otherwise.
        """
        return self._savedsearch_object_link.IsDynamic()

    def add_comment(self, new_comment: str, overwrite: bool = False) -> None:
        """Add a comment to the already existing comments on the SavedSearch, or overwrite the existing comments.

        Note:
            Due to limitations in the Ocean API, this function is not implemented for dynamic saved searches. Use the is_dynamic property to check if adding a comment is supported.

        Args:
            new_comment (str): The new comment to add to the SavedSearch.
            overwrite (bool, optional): If True, the new comment will overwrite the existing comments. Defaults to False.
        
        Raises:
            PythonToolException: If the SavedSearch is read-only.
            UserWarning: If the SavedSearch is dynamic and a commend cannot be added.

        **Example**:

        Add a new comment to already existing comments:

        .. code-block:: python

            saved_search = petrel.saved_searches["Input/Wells/Saved searches/My saved search"]
            saved_search.comments
            >> "This is an already existing comment."
            saved_search.readonly = False
            saved_search.add_comment("This is a new comment.")
            saved_search.comments
            >> "This is an already existing comment.\\nThis is a new comment."

        **Example**:

        Overwrite existing comments with a new comment:

        .. code-block:: python

            saved_search = petrel.saved_searches["Input/Wells/Saved searches/My saved search"]
            saved_search.comments
            >> "This is an already existing comment."
            saved_search.readonly = False
            saved_search.add_comment("This is a new comment.", overwrite=True)
            saved_search.comments
            >> "This is a new comment."
        
        """
        if self._savedsearch_object_link.IsDynamic():
            warnings.warn("Unable to add comment to a dynamic saved search. Use the is_dynamic property to check if adding a comment is supported.")
            return
        if self.readonly:
            raise PythonToolException("SavedSearch is readonly")
        self._savedsearch_object_link.AddComments(new_comment, overwrite)