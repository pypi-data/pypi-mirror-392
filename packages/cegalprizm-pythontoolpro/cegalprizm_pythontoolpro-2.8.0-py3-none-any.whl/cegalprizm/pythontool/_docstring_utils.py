# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




def get_template_docstring() -> str:
    return """Returns the Petrel template for the object as a Template or DiscreteTemplate object."""

def get_template_decorator(func):
    func.__doc__ = get_template_docstring()
    return func

def crs_wkt_decorator(*args, **kwargs):
    def decorator(func):
        func.__doc__ = crs_wkt_docstring(object_type=kwargs.get('object_type', 'project'))
        return func
    return decorator

def crs_wkt_docstring(object_type: str) -> str:
    docstring = f"""The PROJCS (Projected Coordinate System) Well Known Text representation of the {object_type} CRS.

        Returns:
            string: Either (1) PROJCS well known text representation of the CRS, (2) an empty string if the CRS is not available, or (3) a message that the CRS is not available for the object type.
    """
    return docstring

def create_surface_attribute_docstring_decorator(*args, **kwargs):
    def decorator(func):
        func.__doc__ = create_surface_attribute_docstring()
        return func
    return decorator

def create_surface_attribute_docstring() -> str:
    docstring = """Create a new attribute for the Surface with the given name, data_type and template. 
    
    If no name, data_type or template is provided a continuous attribute will be created with a default template and name. Providing an incorrect combination of data_type and template will raise an error.

    Args:
        name (str, optional): The name of the new attribute. If an empty string is provided, a default name will be generated based on the template.
        data_type (str or NumericDataTypeEnum, optional): The type of attribute to create. Can be either "continuous" or "discrete". Defaults to None, which means the data_type is inferred from the template, or set to "continuous" if no template is provided.
        template (Template or DiscreteTemplate, optional): The template to use for the new attribute. Defaults to None, which means the default continuous or discrete template will be used depending on the data_type input.

    Returns:
        SurfaceAttribute or SurfaceDiscreteAttribute: The newly created object.

    Raises:
        TypeError: If 'name' is not a string.
        ValueError: If 'name' is not a valid string.
        PythonToolException: If the Surface is readonly.
        TypeError: if 'data_type' is not None and is not a string or NumericDataTypeEnum.
        TypeError: If 'template' is not None and is not a Template or DiscreteTemplate object.
        ValueError: If 'data_type' is a string and is not "continuous" or "discrete".
        ValueError: If 'data_type' is "continuous" and 'template' is a DiscreteTemplate, or if 'data_type' is "discrete" and 'template' is a Template.

    **Example:**

    Create a new SurfaceAttribute for the Surface with a specified template:

    .. code-block:: python

        surface = petrel_connection.surfaces["Input/Path/To/Surface"]
        surface.readonly = False
        cont_template = petrel.templates["Templates/Path/To/Template"]
        new_attribute = surface.create_attribute("MyNewAttribute", template = cont_template)

    **Example:**

    Create a ne SurfaceDiscreteAttribute for the Surface with the default discrete template:

    .. code-block:: python

        from cegalprizm.pythontool import NumericDataTypeEnum
        surface = petrel_connection.surfaces["Input/Path/To/Surface"]
        surface.readonly = False
        new_discrete_attribute = surface.create_discrete_attribute("MyNewDiscreteAttribute", NumericDataTypeEnum.Discrete)

    """
    return docstring

def create_folder_docstring_decorator(*args, **kwargs):
    def decorator(func):
        func.__doc__ = create_folder_docstring(root = kwargs.get('root', False),
                                               source = kwargs.get('source', ''),
                                               source_in_code = kwargs.get('source_in_code', ''))
        return func
    return decorator

def create_folder_docstring(root: bool, source: str, source_in_code: str) -> str:
    if root:
        additional_raises = """""" 
        first_line = "Creates a new root level :class:`Folder` with the given name in the Petrel project."
        example_code = """    
    **Example**:

    Create a new Folder in the Petrel project:

    .. code-block:: python

        petrel = PetrelConnection()
        folder = petrel.create_folder("MyTopLevelFolder")
    """
    else:
        additional_raises = f"""
        PythonToolException: If the {source} is readonly."""
        first_line = f"""Creates a new :class:`Folder` with the given name in this {source}."""
        example_code = f"""
    **Example**:

    Create a new Folder in the {source}:

    .. code-block:: python

        source = petrel.{source_in_code}.get_by_name("My{source}")
        source.readonly = False
        new_folder = source.create_folder("MyNewFolder")
    """

    return f"""{first_line} If the name is an empty string a default name will be generated.

    Args:
        name (str): The name of the new Folder.

    Returns:
        Folder: The newly created :class:`Folder` object.

    Raises:
        TypeError: If the name argument is not a string.
        ValueError: If the name argument is not a valid string.{additional_raises}
    {example_code}

    """

def create_global_well_log_docstring_decorator(*args, **kwargs):
    def decorator(func):
        func.__doc__ = create_global_well_log_docstring(folder_argument = kwargs.get('folder_argument', False))
        return func
    return decorator

def create_global_well_log_docstring(folder_argument: bool = False) -> str:
    if folder_argument:
        intro_where = "in the provided GlobalWellLogFolder"
        intro_end = " If no folder is provided, the new global well log will be created in the root GlobalWellLogFolder."
        args_folder = """folder (GlobalWellLogFolder, optional): The GlobalWellLogFolder to create the new global well log in. Defaults to None which means the new global well log will be created in the root GlobalWellLogFolder.\n"""
        raises_folder = """TypeError: If 'folder' is not a GlobalWellLogFolder object or None.\n"""
    else:
        intro_where = "in this GlobalWellLogFolder"
        intro_end = ""
        args_folder = ""
        raises_folder = ""

    examples = _get_create_global_well_log_examples(folder_argument)

    docstring = f"""Create a new global well log {intro_where} with the given name and template.{intro_end}

    If no name, data_type or template is provided, a continuous global well log will be created with a default template and name. Providing an incorrect combination of data_type and template will raise an error.

    Args:
        name (str, optional): The name of the new global well log. If an empty string is provided, a default name will be generated based on the template.
        data_type (str or NumericDataTypeEnum, optional): The type of global well log to create. Can be either "continuous" or "discrete". Defaults to None, which means the data_type is inferred from the template, or set to "continuous" if no template is provided.
        template (Template or DiscreteTemplate, optional): The template to use for the new global well log. Defaults to None, which means the default continuous or discrete template will be used depending on the data_type input.
        {args_folder}
    Returns:
        GlobalWellLog or DiscreteGlobalWellLog: The newly created object.

    Raises:
        TypeError: If 'name' is not a string.
        ValueError: If 'name' is not a valid string.
        PythonToolException: If the GlobalWellLogFolder is readonly.
        TypeError: If 'data_type' is not None and is not a string or NumericDataTypeEnum.
        TypeError: If 'template' is not None and is not a Template or DiscreteTemplate object.
        ValueError: If 'data_type' is a string and is not "continuous" or "discrete".
        ValueError: If 'data_type' is "continuous" and 'template' is a DiscreteTemplate, or if 'data_type' is "discrete" and 'template' is a Template.
        {raises_folder}
    {examples}

    """
    return docstring

def _get_create_global_well_log_examples(folder_argument: bool) -> str:
    if folder_argument:
        return """**Example:**

    Create a new GlobalWellLog in the main GlobalWellLogFolder using the default continuous template:

    .. code-block:: python

        petrel = PetrelConnection()
        new_global_log = petrel.create_global_well_log("MyNewGlobalLog")

    **Example:**

    Create a new DiscreteGlobalWellLog in a subfolder of the main GlobalWellLogFolder, using a specific discrete template:

    .. code-block:: python

        from cegalprizm.pythontool import NumericDataTypeEnum
        petrel = PetrelConnection()
        global_log_folder = petrel.global_well_log_folders.get_by_name("Subfolder")
        global_log_folder.readonly = False
        disc_template = petrel.templates.get_by_name("MyDiscreteTemplate")
        new_discrete_log = petrel.create_global_well_log("MyNewDiscreteGlobalLog", NumericDataTypeEnum.Discrete, disc_template, global_log_folder)

        """
    else:
        return """**Example:**

    Create a new GlobalWellLog in the main GlobalWellLogFolder:

    .. code-block:: python

        global_log_folder = petrel.global_well_log_folders["Input/Wells/Global well logs"]
        global_log_folder.readonly = False
        cont_template = petrel.templates["Templates/Path/To/Template"]
        new_log = global_log_folder.create_global_well_log("MyNewGlobalLog", template = cont_template)

    **Example:**

    Create a new DiscreteGlobalWellLog in a subfolder of the main GlobalWellLogFolder, using the default discrete template:

    .. code-block:: python

        from cegalprizm.pythontool import NumericDataTypeEnum
        global_log_folder = petrel.global_well_log_folders["Input/Wells/Global well logs/Subfolder"]
        global_log_folder.readonly = False
        new_discrete_log = global_log_folder.create_global_well_log("MyNewDiscreteGlobalLog", NumericDataTypeEnum.Discrete)

        """

def move_docstring_decorator(*args, **kwargs):
    def decorator(func):
        func.__doc__ = move_docstring(object_type=kwargs.get('object_type', ''),
                                      is_folder=kwargs.get('is_folder', False))
        return func
    return decorator

def move_docstring(object_type: str, is_folder: bool) -> str:
    property_name = object_type.lower()
    docstring = f"""Moves this {object_type} to the specified destination :class:`Folder`.
    """
    if is_folder:
        docstring += """
    Note:
        Moving a Folder object requires updating the path of all objects within the Folder and any subfolders. This operation may be slow in projects with many objects.
    """
    
    docstring += f"""
    Args:
        destination (Folder): The :class:`Folder` this {object_type} should be moved to.

    Raises:
        PythonToolException: If the {object_type} is readonly.
        TypeError: If the destination is not a :class:`Folder` object."""
    if is_folder:
        docstring += """
        UnexpectedErrorException: If attempting to move the Folder to itself.
        UnexpectedErrorException: If attempting to move the Folder to a subfolder of itself."""
    docstring += f"""

    **Example:**

    Move the {object_type} to a new Folder:

    .. code-block:: python

        {property_name} = petrel.{property_name}s.get_by_name("My{object_type}")
        destination_folder = petrel.folders.get_by_name("DestinationFolder")
        {property_name}.readonly = False
        {property_name}.move(destination_folder)

    """
    return docstring

def clone_docstring_decorator(*args, **kwargs):
    def decorator(func):
        func.__doc__ = clone_docstring(
            return_type=kwargs.get('return_type', 'Petrel object'),
            respects_subfolders=kwargs.get('respects_subfolders', False),
            continuous_template=kwargs.get('continuous_template', False),
            discrete_template=kwargs.get('discrete_template', False),
            is_global_well_log=kwargs.get('is_global_well_log', False),
            is_well_log=kwargs.get('is_well_log', False),
            is_fault_interpretation=kwargs.get('is_fault_interpretation', False),
            supports_folder=kwargs.get('supports_folder', False),
            realize_path=kwargs.get('realize_path', False))
        return func
    return decorator

def clone_docstring(return_type: str,
                    respects_subfolders: bool = False,
                    continuous_template: bool = False,
                    discrete_template: bool = False,
                    is_global_well_log: bool = False,
                    is_well_log: bool = False,
                    is_fault_interpretation: bool = False,
                    supports_folder: bool = False,
                    realize_path: bool = False) -> str:
    docstring = _get_clone_docstring_introduction(return_type, respects_subfolders, is_well_log, is_global_well_log, supports_folder)
    docstring += _get_clone_docstring_notes(continuous_template, discrete_template, is_fault_interpretation, realize_path)
    docstring += _get_clone_docstring_parameters(return_type, continuous_template, discrete_template, is_global_well_log, supports_folder, realize_path)
    docstring += _get_clone_docstring_returns(return_type)
    docstring += _get_clone_docstring_raises(continuous_template, discrete_template, is_global_well_log, supports_folder, realize_path)
    if realize_path:
        docstring += _get_clone_docstring_examples(realize_path)
    return docstring

def _get_clone_docstring_examples(realize_path: bool = False) -> str:
    if realize_path:
        return """

    **Example:**

    .. code-block:: python

        seismic_cube = petrel.seismic_cubes["Input/Path/To/SeismicCube"]

        ## Using double backslashes when specifying realize path as variable
        clone_path = 'C:\\\\RealizedCubes\\\\RealizedCube.zgy'
        ## Using raw string when specifying realize path as variable
        clone_path_raw_string = r'\\\\networklocation\\folder\\file.zgy'
        
        cloned_cube_1 = seismic_cube.clone("ClonedSeismicCube1", copy_values=True, realize_path=clone_path)
        cloned_cube_2 = seismic_cube.clone("ClonedSeismicCube2", copy_values=True, realize_path=clone_path_raw_string)

        """

def _get_clone_docstring_introduction(return_type: str, respects_subfolders: bool, is_well_log: bool, is_global_well_log: bool, supports_folder: bool) -> str:
    docstring = f"""Creates a clone of the {return_type}."""
    if is_well_log:
        docstring += """ Note that the corresponding global well log will also be cloned."""
    if is_global_well_log:
        docstring += """ The clone is placed in the same GlobalWellLogFolder as the source object, unless a different folder is specified using the 'folder' argument."""
        return docstring
    if supports_folder:
        docstring += """ The clone is placed in the same Folder as the source object, unless a different folder is specified using the 'folder' argument."""
    elif respects_subfolders:
        docstring += """ The clone is placed in the same collection as the source object."""
    return docstring

def _get_clone_docstring_notes(continuous_template: bool = False, discrete_template: bool = False, is_fault_interpretation: bool = False, realize_path: bool = False):
    docstring = """
    """
    if continuous_template:
        docstring += _get_clone_docstring_cont_template_details()
    if discrete_template:
        docstring += _get_clone_docstring_disc_template_details()
    if is_fault_interpretation:
        docstring += _get_clone_docstring_fault_interpretation_notes()
    if realize_path:
        docstring += _get_clone_docstring_realize_path_details()
    return docstring

def _get_clone_docstring_parameters(return_type: str, continuous_template: bool, discrete_template: bool, is_global_well_log: bool, supports_folder: bool, realize_path: bool) -> str:
    docstring = """
    Parameters:
        name_of_clone: Petrel name of the clone"""
    if is_global_well_log:
        docstring += f"""
        copy_values: WARNING: This argument is not implemented for {return_type} objects and will be removed in the future. Defaults to False."""
    else:
        docstring += """
        copy_values: Set to True if values shall be copied into the clone. Defaults to False."""
    if continuous_template:
        docstring += """
        template: Template to use for the clone. Defaults to None."""
    if discrete_template:
        docstring += """
        discrete_template: DiscreteTemplate to use for the clone. Defaults to None."""
    if is_global_well_log:
        docstring += """
        folder: The GlobalWellLogFolder to place the clone in. Defaults to None, which means the clone will be placed in the same folder as the source object."""
    if supports_folder:
        docstring += """
        folder: The Folder to place the clone in. Defaults to None, which means the clone will be placed in the same folder as the source object."""
    if realize_path:
        docstring += """
        realize_path: Directory path where the seismic cube will be realized in the file system. Defaults to an empty string, meaning the cube will be realized in the Petrel project data folder."""
    return docstring

def _get_clone_docstring_returns(return_type):
    return f"""
    
    Returns:
        {return_type}: The clone as a {return_type} object."""

def _get_clone_docstring_raises(continuous_template: bool, discrete_template: bool, is_global_well_log: bool, supports_folder: bool, realize_path: bool) -> str:
    docstring = """

    Raises:
        ValueError: If name_of_clone is empty or contains slashes"""
    if continuous_template:
        docstring += _get_clone_docstring_cont_template_exceptions()
    if discrete_template:
        docstring += _get_clone_docstring_disc_template_exceptions()
    if is_global_well_log:
        docstring += """
        TypeError: If folder is not a GlobalWellLogFolder object or None."""
    if supports_folder:
        docstring += """
        TypeError: If folder is not a Folder object or None."""
    if realize_path:
        docstring += """
        TypeError: If realize_path is not a string.
        ValueError: If the folder in realize_path does not exist."""
    return docstring

def _get_clone_docstring_cont_template_details():
    return """
    The clone can be created with a continuous Template. Cloning with template is only possible if copy_values=False.
    When cloning with template, the clone will get the default color table of the given template.
    If a template argument is not provided, the clone will have the same template and color table as the source object.
    """

def _get_clone_docstring_disc_template_details():
    return """
    The clone can be created with a DiscreteTemplate. Cloning with a discrete_template is only possible if copy_values=False.
    When cloning with discrete template, the clone will get the default color table of the given discrete template.
    If a discrete_template argument is not provided, the clone will have the same discrete template and color table as the source object.
    """

def _get_clone_docstring_fault_interpretation_notes():
    return """
    If copy_values is set to False, only the geometry (polylines) will be copied
    If copy_values is set to True, the polylines and any attributes with their values will be copied to the clone.
    """

def _get_clone_docstring_realize_path_details():
    return """
    By default the cloned seismic cube will be realized in the Petrel project data folder. This can be customized by providing a directory path using the realize_path argument.
    If a full path including the *.zgy extension is provided, the cube will be realized with that name in the given directory. If the extension is missing, it will be added automatically.
    If a directory path is provided (input ending with a backslash), the cube will be realized in that directory with the name of the clone as filename.
    Providing a directory that does not exist will raise a ValueError.
    Note that the backslash character is an escape character in Python strings. Use double backslashes or raw strings to ensure the correct path is used.
    """

def _get_clone_docstring_cont_template_exceptions():
    return """
        UserErrorException: If template is used as argument when copy_values=True. Can only clone with template if copy_values=False
        UserErrorException: If template is not a Template object"""

def _get_clone_docstring_disc_template_exceptions():
    return """
        UserErrorException: If both copy_values=True and discrete_template is used as arguments. Can only clone with discrete_template if copy_values=False
        UserErrorException: If discrete_template is not a DiscreteTemplate object"""

def log_as_array_decorator(func):
    func.__doc__ = log_as_array_docstring()
    return func

def log_as_array_docstring() -> str:
    return """The values of the log as a numpy array.
    
Returns:
    numpy.ndarray: A one-dimensional NumPy array containing the values of the log.
"""

def log_as_tuple_decorator(func):
    func.__doc__ = log_as_tuple_docstring()
    return func

def log_as_tuple_docstring() -> str:
    return """The values of the log as a tuple of NumPy Arrays.

Returns:
    tuple: A tuple containing two one-dimensional NumPy arrays. The first array contains the depths and the second array contains the values of the log.

Args:
    depth_index (str, optional): Used to specify which depth index to use as the first array in the tuple. Accepted inputs are 'MD', 'TWT', 'TVDSS', 'TVD'. Defaults to 'MD'.

Raises:
    ValueError: If the depth_index is not one of the accepted inputs.
"""

def get_supported_polyline_types() -> str:
    supported_types = [
        'Fault sticks',
        'Fault lines',
        'Fault centerline',
        'Fault polygons',
        'Horizon contours',
        'Horizon erosion line',
        'Generic boundary polygon',
        'Generic seismic 2D lines',
        'Generic seismic 3D lines',
        'Generic zero lines',
        'Trend lines',
        'Flow lines',
        'Generic single line',
        'Many points',
        'Few points',
        'Multi-Z horizon',
        'Other'
    ]
    supported_types_string = ""
    for supported_type in supported_types:
        supported_types_string += f"\n- '{supported_type}'"
    return supported_types_string

def get_polyline_type_decorator(func):
    func.__doc__ = _get_polyline_type_docstring()
    return func

def _get_polyline_type_docstring() -> str:
    return f"""The type of polylines contained within this PolylineSet instance. The type corresponds to the 'Line type' dropdown selection in the Petrel settings UI.
The output is a string. When setting the value, the input can be either a string or a PolylineTypeEnum.

**Example**:

Retrieve the polyline_type as a string

.. code-block:: python

    polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
    print(polylineset.polyline_type)
    >> "Fault polygons"

**Example**:

Set the type of the polyline using a string

.. code-block:: python

    polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
    polylineset.polyline_type = "Fault polygons"

**Example**:

Set the type of the polyline using a PolylineTypeEnum

.. code-block:: python

    from cegalprizm.pythontool import PolylineTypeEnum
    polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
    polylineset.polyline_type = PolylineTypeEnum.FaultPolygons

Args:
    polyline_type (PolylineTypeEnum): The type of the polyline.
        Import PolylineTypeEnum from cegalprizm.pythontool to use this option.
    polyline_type (str): The type of the polyline. Possible values are: {get_supported_polyline_types()}

Returns:
    str: The type of the polyline. Possible return values are the same as the input values mentioned in the args section.

Raises:
    PythonToolException: If attempting to set the polyline_type when the PolylineSet is readonly
    TypeError: If attempting to set the polyline_type with an input that is not a string or a PolylineTypeEnum
"""

def get_by_name_decorator(*args, **kwargs):
    def decorator(func):
        func.__doc__ = get_by_name_docstring(object_type=kwargs.get('object_type', ''),
                                             deprecated_msg = kwargs.get('deprecated_msg', ''))
        return func
    return decorator

def get_by_name_docstring(object_type: str, deprecated_msg: str = '') -> str:
    docstring = f"""{deprecated_msg}Retrieve one or more {object_type} object(s) by Petrel name.
    If a single matching {object_type} is found a single object is returned. If multiple matching {object_type}s are found, a list of objects is returned.
    By default the search is case-insensitive, however this can be changed by setting the `case_sensitive` parameter to `True`.

    Args:
        name (str): The name of the {object_type} to search for.
        case_sensitive (bool, optional): If set to True the search will be case-sensitive, only matching the exact capitalization of the name. Defaults to False.
    
    Returns:
        Union[{object_type}, list[{object_type}], None]: A single {object_type} object if a unique match is found, a list of {object_type} objects if multiple matches are found, or None if no matches are found.
    """
    return docstring

def object_dictionary_decorator(*args, **kwargs):
    def decorator(func):
        func.__doc__ = object_dictionary_docstring(object_name_singular = kwargs.get('object_name_singular', 'object'),
                                                    object_type = kwargs.get('object_type', 'PetrelObject'),
                                                    property_name = kwargs.get('property_name', ''),
                                                    additional_info = kwargs.get('additional_info', ''),
                                                    object_name_plural = kwargs.get('object_name_plural', ''),
                                                    object_type_plural = kwargs.get('object_type_plural', ''),
                                                    deprecated_msg = kwargs.get('deprecated_msg', ''))
        return func
    return decorator

def object_dictionary_docstring(object_name_singular, object_type: str, property_name: str, additional_info, object_name_plural: str = '', object_type_plural: str = '', deprecated_msg: str = '') -> str:
    if object_name_plural == '':
        object_name_plural = object_name_singular + 's'
    if object_type_plural == '':
        object_type_plural = object_type + 's'
    docstring = f"""
    {deprecated_msg}Retrieve all {object_name_plural} in Petrel as {object_type} objects and collect them in a dictionary with their paths as keys.

    When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys). If multiple objects have the same path, a list of them is returned.
    {additional_info}
    Use the `get_by_name` method to retrieve one or more {object_type} object(s) by name, see example below.

    **Example**

    Retrieve a specific {object_name_singular} by path with 'petrel' as your defined PetrelConnection:

    .. code-block:: python

        my_object = petrel.{property_name}['Path/To/Object']

    **Example**

    Retrieve a specific {object_name_singular} by name with 'petrel' as your defined PetrelConnection:

    .. code-block:: python

        my_object = petrel.{property_name}.get_by_name("My{object_type}")

    Returns:
        {object_type_plural}: A dictionary of {object_type} objects by their path.
    """
    return docstring