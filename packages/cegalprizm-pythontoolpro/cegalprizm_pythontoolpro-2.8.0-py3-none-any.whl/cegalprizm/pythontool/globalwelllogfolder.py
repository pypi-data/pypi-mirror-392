# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




from cegalprizm.pythontool.parameter_validation import validate_name
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder
from cegalprizm.pythontool import GlobalWellLog, DiscreteGlobalWellLog
from cegalprizm.pythontool.enums import NumericDataTypeEnum
from cegalprizm.pythontool.template import Template, DiscreteTemplate
from cegalprizm.pythontool.exceptions import PythonToolException
from cegalprizm.pythontool import _docstring_utils
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from cegalprizm.pythontool import _utils
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.globalwelllogfolder_grpc import GlobalWellLogFolderGrpc


class GlobalWellLogFolder(PetrelObject, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder):
    def __init__(self, grpc_object: "GlobalWellLogFolderGrpc"):
        super(GlobalWellLogFolder, self).__init__(grpc_object)
        self._object_link = grpc_object

    def __str__(self) -> str:
        """A readable representation"""
        return 'GlobalWellLogFolder("{0}")'.format(self.petrel_name)

    def retrieve_stats(self) -> typing.Dict[str, str]:
        """Due to limitations in the Ocean API, this function is not implemented for GlobalWellLogFolder objects.

        Returns:
            Dictionary: An empty dictionary.
        """
        return self._object_link.RetrieveStats()

    @_docstring_utils.create_global_well_log_docstring_decorator()
    @validate_name(param_name="name")
    def create_global_well_log(self, name: str = "", data_type: typing.Union[str, "NumericDataTypeEnum"] = None, template: typing.Union["DiscreteTemplate", "Template"] = None) -> typing.Union["GlobalWellLog", "DiscreteGlobalWellLog"]:
        if self.readonly:
            raise PythonToolException("GlobalWellLogFolder is readonly")

        data_type =_utils.get_and_validate_data_type(data_type, template)
        discrete = data_type == NumericDataTypeEnum.Discrete
        _utils.validate_template(template, discrete, "global well log")

        grpc_object = self._object_link.CreateGlobalWellLog(name, discrete, template)

        if discrete:
            return DiscreteGlobalWellLog(grpc_object) if grpc_object else None
        else:
            return GlobalWellLog(grpc_object) if grpc_object else None

    @validate_name(param_name="name")
    def create_global_well_log_folder(self, name: str) -> "GlobalWellLogFolder":
        """Create a new GlobalWellLogFolder with the given name. The new folder will be created as a subfolder of the current GlobalWellLogFolder.

        Args:
            name (str): The name of the new GlobalWellLogFolder. If an empty string is provided, a default name will be generated.

        Returns:
            GlobalWellLogFolder: The newly created GlobalWellLogFolder object.

        Raises:
            TypeError: If the name argument is not a string.
            ValueError: If the name argument is not a valid string.
            PythonToolException: If the GlobalWellLogFolder is read-only.

        **Example**:

        Create a new GlobalWellLogFolder in the main GlobalWellLogFolder:

        .. code-block:: python

            main_folder = petrel.global_well_log_folders["Input/Global well logs"]
            main_folder.readonly = False
            new_folder = main_folder.create_global_well_log_folder("NewFolder")

        """
        if self.readonly:
            raise PythonToolException("GlobalWellLogFolder is readonly")
        grpc_object = self._object_link.CreateGlobalWellLogFolder(name)
        return GlobalWellLogFolder(grpc_object) if grpc_object else None

    @property
    def parent_folder(self) -> typing.Union["GlobalWellLogFolder", None]:
        """Returns the parent folder of this GlobalWellLogFolder in Petrel. Returns None if the parent is the Global well logs root folder.

        Returns:
            :class:`GlobalWellLogFolder` or None: The parent folder of the GlobalWellLogFolder, or None if the parent is the Global well logs root folder.

        **Example**:

        .. code-block:: python

            gwlf = petrel_connection.global_well_log_folders["Input/Wells/Global well logs/Subfolder"]
            gwlf.parent_folder
            >> GlobalWellLogFolder(petrel_name="Global well logs")
        """
        return self._parent_folder

    def get_logs(self, recursive: bool = False, data_type: typing.Union[str, "NumericDataTypeEnum"] = None) -> typing.List[typing.Union["GlobalWellLog", "DiscreteGlobalWellLog"]]:
        """Returns a list of all logs in this GlobalWellLogFolder. Use the recursive flag to include logs in subfolders of this GlobalWellLogFolder.
        Use the data_type parameter to filter logs by type (continuous or discrete). By default both types are returned.
        
        Args:
            recursive (bool, optional): If True, all logs in all subfolders will be included. Defaults to False.
            data_type (str or NumericDataTypeEnum, optional): Filter the result so that only logs of the specified type are returned. Valid inputs are 'continuous' and 'discrete' or the corresponding NumericDataTypeEnum values. Defaults to None, which includes both types.

        Returns:
            List[GlobalWellLog or DiscreteGlobalWellLog]: A list of :class:`GlobalWellLog` and/or :class:`DiscreteGlobalWellLog` objects.

        Raises:
            TypeError: If recursive is not a boolean, or if data_type is not a string or NumericDataTypeEnum.
            ValueError: If data_type is not 'continuous' or 'discrete'.

        **Example**:

        Get all logs in a specific GlobalWellLogFolder:

        .. code-block:: python

            gwlf = petrel_connection.global_well_log_folders["Input/Wells/Global well logs/Folder1"]
            all_logs = gwlf.get_logs()

        **Example**:

        Get all discrete logs the main GlobalWellLogFolder and its subfolders:

        .. code-block:: python

            gwlf = petrel_connection.global_well_log_folders["Input/Wells/Global well logs"]
            all_discrete_logs = gwlf.get_logs(recursive=True, data_type="discrete")

        """
        if not isinstance(recursive, bool):
            raise TypeError("recursive must be a boolean")

        if isinstance(data_type, NumericDataTypeEnum):
            if data_type == NumericDataTypeEnum.Continuous:
                data_type = WellKnownObjectDescription.WellLogGlobal
            elif data_type == NumericDataTypeEnum.Discrete:
                data_type = WellKnownObjectDescription.WellLogGlobalDiscrete
            else:
                raise ValueError(f"Unsupported NumericDataTypeEnum: {data_type}")
        elif isinstance(data_type, str):
            if data_type.lower() == NumericDataTypeEnum.Continuous.value:
                data_type = WellKnownObjectDescription.WellLogGlobal
            elif data_type.lower() == NumericDataTypeEnum.Discrete.value:
                data_type = WellKnownObjectDescription.WellLogGlobalDiscrete
            else:
                raise ValueError(f"Invalid data_type: {data_type}. Must be 'continuous' or 'discrete'.")
        elif data_type is not None:
            raise TypeError("data_type must be a string or NumericDataTypeEnum or None")

        grpcs = self._object_link.GetGlobalWellLogs(recursive, data_type)
        from cegalprizm.pythontool.workflow import _pb_grpcobj_to_pyobj
        return [_pb_grpcobj_to_pyobj(grpc) if grpc else None for grpc in grpcs]
