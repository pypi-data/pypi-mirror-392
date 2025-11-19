# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import typing
from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistoryToBeDeprecated
from cegalprizm.pythontool import PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion
from cegalprizm.pythontool import Folder
from cegalprizm.pythontool.exceptions import PythonToolException
from cegalprizm.pythontool import _docstring_utils
from cegalprizm.pythontool.parameter_validation import validate_name
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.interpretation_collection_grpc import InterpretationCollectionGrpc

class InterpretationFolder(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistoryToBeDeprecated, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion):
    """A class holding information about an interpretation folder (InterpretationCollection)."""

    def __init__(self, petrel_object_link: "InterpretationCollectionGrpc"):
        super(InterpretationFolder, self).__init__(petrel_object_link)
        self._interpretation_collection_object_link = petrel_object_link
    
    def __str__(self) -> str:
        """A readable representation"""
        return 'InterpretationFolder(petrel_name="{0}")'.format(self.petrel_name)

    @_docstring_utils.create_folder_docstring_decorator(source="InterpretationFolder", source_in_code="interpretation_folders")
    @validate_name(param_name="name")
    def create_folder(self, name: str) -> "Folder":
        if self.readonly:
            raise PythonToolException("InterpretationFolder is readonly")
        grpc_object = self._interpretation_collection_object_link.CreateFolder(name)
        return Folder(grpc_object) if grpc_object else None

    @property
    def parent_folder(self) -> typing.Union["InterpretationFolder", None]:
        """Returns the parent folder of this InterpretationFolder in Petrel. Returns None if the object is the Input root or Seismic root.

        Returns:
            :class:`InterpretationFolder` or None: The parent folder of the InterpretationFolder, or None if the object is located at the root level.

        **Example**:

        .. code-block:: python

            folder = petrel_connection.interpretation_folders["Input/Seismic/Interpretation folder 1/Subfolder"]
            folder.parent_folder
            >> InterpretationFolder(petrel_name="Interpretation folder 1)
        """
        return self._parent_folder