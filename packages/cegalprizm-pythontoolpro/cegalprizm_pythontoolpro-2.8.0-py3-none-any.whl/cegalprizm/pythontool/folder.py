# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




from cegalprizm.pythontool.parameter_validation import validate_name
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion
from cegalprizm.pythontool.exceptions import PythonToolException
from cegalprizm.pythontool import _docstring_utils, _utils
from cegalprizm.pythontool.enums import FolderObjectTypeEnum
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.folder_grpc import FolderGrpc
    from cegalprizm.pythontool import InterpretationFolder, SeismicCube

class Folder(PetrelObject, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion):
    """A class holding information about a folder object in Petrel."""
    def __init__(self, grpc_object: "FolderGrpc"):
        super(Folder, self).__init__(grpc_object)
        self._object_link = grpc_object

    def __str__(self) -> str:
        """A readable representation"""
        return 'Folder(petrel_name="{0}")'.format(self.petrel_name)

    def retrieve_stats(self) -> typing.Dict[str, str]:
        """Due to limitations in the Ocean API, this function is not implemented for Folder objects.

        Returns:
            Dictionary: An empty dictionary.
        """
        return self._object_link.RetrieveStats()

    @_docstring_utils.create_folder_docstring_decorator(source="Folder", source_in_code="folders")
    @validate_name(param_name="name")
    def create_folder(self, name: str) -> "Folder":
        if self.readonly:
            raise PythonToolException("Folder is readonly")
        grpc_object = self._object_link.CreateFolder(name)
        return Folder(grpc_object) if grpc_object else None

    @_docstring_utils.move_docstring_decorator(object_type="Folder", is_folder=True)
    def move(self, destination: "Folder"):
        if self.readonly:
            raise PythonToolException("Folder is readonly")
        _utils.verify_folder(destination)
        self._move(destination)

    @property
    def parent_folder(self) -> typing.Union["Folder", "InterpretationFolder", "SeismicCube", None]:
        """Returns the parent folder of this Folder in Petrel. Returns None if the object is the Input root.

        Returns:
            :class:`Folder`, :class:`InterpretationFolder`, :class:`SeismicCube` or None: The parent folder of the Folder, or None if the object is located at the root level.

        **Example**:

        .. code-block:: python

            folder = petrel_connection.polylinesets["Input/Folder/Subfolder"]
            folder.parent_folder
            >> Folder(petrel_name="Folder")
        """
        return self._parent_folder

    def get_objects(self, recursive: bool = False, object_types: typing.List[typing.Union[FolderObjectTypeEnum, str]] = None) -> typing.List[PetrelObject]:
        """Retrieves objects from this folder. Retrieve objects from subfolders by setting the recursive flag to True. The type of objects to retrieve can be filtered by providing a list of object types.
        Object types can be provided as strings or as entries from the :class:`FolderObjectTypeEnum` enum. Supported string entries are "Folder", "MarkerCollection", "PointSet", "PolylineSet", "Surface" and "Wavelet".

        Args:
            recursive (bool, optional): If True, retrieves objects also from any subfolders of the current folder. Defaults to False.
            object_types (List[FolderObjectTypeEnum | str], optional): A list of object types to filter the retrieved objects. If None, all object types are retrieved. Defaults to None.

        Returns:
            List[PetrelObject]: A list of objects in the folder matching the specified criteria. If no objects match, an empty list is returned.

        Raises:
            TypeError: If object_types is not a list or any of the entries is not one of the supported object types.

        **Example**:

        Get all objects in a folder:

        .. code-block:: python

            folder = petrel_connection.folders["Input/Folder"]
            all_objects = folder.get_objects()

        **Example**:

        Recursively retrieve all subfolders in a folder:

        .. code-block:: python

            folder = petrel_connection.folders["Input/Folder"]
            all_subfolders = folder.get_objects(recursive=True, object_types=["Folder"])

        **Example**:

        Retrieve all PointSet and PolylineSet objects in a folder, using both string and enum filtering:

        .. code-block:: python

            from cegalprizm.pythontool import FolderObjectTypeEnum
            folder = petrel_connection.folders["Input/Folder"]
            point_and_polyline_sets = folder.get_objects(object_types=[FolderObjectTypeEnum.PointSet, "PolylineSet"])

        """
        if object_types is not None and not isinstance(object_types, list):
            raise TypeError("object_types must be None or a list of supported object types")
        object_types_string = self._handle_object_filtering(object_types)
        
        grpcs = self._object_link.GetObjects(recursive, object_types_string)
        from cegalprizm.pythontool.workflow import _pb_grpcobj_to_pyobj
        return [_pb_grpcobj_to_pyobj(grpc) if grpc else None for grpc in grpcs]

    def _handle_object_filtering(self, object_types: typing.List[typing.Union[FolderObjectTypeEnum, str]]) -> typing.List[str]:
        object_types_string = []
        if object_types is None:
            return object_types_string
        
        supported_types = [e.value.lower() for e in FolderObjectTypeEnum]

        for entry in object_types:
            if not (isinstance(entry, FolderObjectTypeEnum) or isinstance(entry, str)):
                raise TypeError("All entries in object_types must be of type FolderObjectTypeEnum or str")
            if isinstance(entry, str):
                if entry.lower() not in supported_types:
                    raise TypeError(f"Unsupported object type string: {entry}. Supported types are {[e.value for e in FolderObjectTypeEnum]}")
                object_types_string.append(entry.lower())
            else:
                object_types_string.append(entry.value.lower())
        return object_types_string


