# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




def affine_transform_docstring_decorator(func):
    func.__doc__ = affine_transform_docstring()
    return func

def affine_transform_docstring() -> str:
    return """ The affine transform of the object.

    returns:
        1d array: An array with 6 coefficients of the affine transformation matrix.
        If array is represented as [a, b, c, d, e, f] then this corresponds to a affine transformation matrix of form:

        | a b e |
        | c d f |
        | 0 0 1 |
    """

def chunk_all_docstring_decorator_horizon_property_3d_decorator(func):
    func.__doc__ = chunk_all_docstring("Horizon Property 3D object")
    return func

def chunk_all_docstring_decorator_horizon_interp_3d_decorator(func):
    func.__doc__ = chunk_all_docstring("Horizon Interpretation 3D object")
    return func

def chunk_all_docstring(object_description: str) -> str:
    return f"""Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the {object_description}.

    Returns:
        cegalprizm.pythontool.Chunk:  A `Slice` containing the values for the {object_description}
    """

def chunk_docstring_decorator_horizon_property_3d_decorator(func):
    func.__doc__ = chunk_docstring("Horizon Property 3D object")
    return func

def chunk_docstring_decorator_horizon_interp_3d_decorator(func):
    func.__doc__ = chunk_docstring("Horizon Interpretation 3D object")
    return func

def chunk_docstring(object_description: str) -> str:
    return f"""
    Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the {object_description}.

    Note:
        Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

    Args:
        i: A tuple(i1,i2) where i1 is the start index and i2 is the end index. The start and end value in this range is inclusive. If None include all i values.
        j: A tuple(j1,j2) where j1 is the start index and j2 is the end index. The start and end value in this range is inclusive. If None include all j values.

    Returns:
        cegalprizm.pythontool.Chunk:  A `Slice` containing the values for the {object_description}
    """

def extent_docstring_decorator(func):
    func.__doc__ = extent_docstring()
    return func

def extent_docstring() -> str:
    return """
    The number of nodes in the i and j directions

    Note:
        Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 5, j = 6) in Python corresponds to (i = 6, j = 7) in Petrel.

    Returns:
        A :class:`cegalprizm.pythontool.Extent` object
    """

def indices_docstring_decorator(*args, **kwargs):
    def decorator(func):
        func.__doc__ = indices_docstring(object_name = kwargs.get("object_name", "horizon interpretation"),
                                        property_name = kwargs.get("property_name", "horizon_interpretation"))
        return func
    return decorator

def indices_docstring(object_name: str, property_name: str) -> str:
    return f"""
    Returns the I, J indices of the seismic bin (cell) nearest to the specified spatial coordinates.

    The input coordinates (x, y) represent a position in world coordinates. The returned indices correspond to the center of the nearest seismic bin (cell) within the {object_name}.
    The K index is always None for {object_name}s.

    Note:
        Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

    Args:
        x (float): X coordinate in project CRS.
        y (float): Y coordinate in project CRS.

    Returns:
        A :class:`cegalprizm.pythontool.primitives.Indices` object representing the (i, j, k) indices of the nearest seismic bin (cell). k is always None.

    Raises:
        ValueError: If the specified coordinates are outside the spatial extent of the {object_name}.

    **Example**:

    .. code-block:: python

        from cegalprizm.pythontool import PetrelConnection
        petrel = PetrelConnection()
        hor = petrel.{property_name}["Input/Path/To/Object"]
        hor.indices(x=451199.8545998224, y=6780362.889868577)
        >> Indices(i=0, j=0, k=None)

    """

def is_undef_value_docstring_decorator(func):
    func.__doc__ = is_undef_value_docstring()
    return func

def is_undef_value_docstring() -> str:
    return """Whether the value is the 'undefined value' for the attribute

    Petrel represents some undefined values by ``MAX_INT``, others by ``NaN``.
    A comparison with ``NaN`` will always return ``False`` (e.g. ``float.nan != float.nan``) so it is preferable to always use this method to test for undefined values.

    Args:
        value: the value to test

    Returns:
        bool: True if value is 'undefined' for this horizon property attribute

    """

def position_docstring_decorator(*args, **kwargs):
    def decorator(func):
        func.__doc__ = position_docstring(object_name = kwargs.get("object_name", "horizon interpretation"),
                                        property_name = kwargs.get("property_name", "horizon_interpretation"))
        return func
    return decorator

def position_docstring(object_name: str, property_name: str) -> str:
    return f"""
    Returns the spatial position (X, Y, Z) of the {object_name} at the specified I, J indices.

    The input indices (i, j) represent a seismic bin (cell) on the underlying seismic grid. The returned coordinates correspond to the center of that bin (cell).
    The coordinates are expressed in world coordinates.

    Note:
        Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

    Args:
        i (int): I-index of the seismic bin (cell).
        j (int): J-index of the seismic bin (cell).

    Returns:
        A :class:`cegalprizm.pythontool.Point` object representing the (X, Y, Z) coordinates of the bin (cell) center in world coordinates.

    Raises:
        ValueError: If the specified indices are outside the {object_name} extent.

    **Example**:

    .. code-block:: python

        from cegalprizm.pythontool import PetrelConnection
        petrel = PetrelConnection()
        hor = petrel.{property_name}["Input/Path/To/Object"]
        hor.position(i=0, j=0)
        >> Point(x=451199.8545998224, y=6780362.889868577, z=-1234.5)

    """

def undef_value_docstring_decorator(func):
    func.__doc__ = undef_value_docstring()
    return func

def undef_value_docstring() -> str:
    return """The 'undefined value' for this attribute

    Use this value when setting a slice's value to 'undefined'.
    Do not attempt to test for undefinedness by comparing with this value, use :meth:`is_undef_value` instead.

    Returns:
        The 'undefined value' for this attribute
    """

def unit_symbol_docstring_decorator(func):
    func.__doc__ = unit_symbol_docstring()
    return func

def unit_symbol_docstring() -> str:
    return """The symbol for the unit which the values are measured in

    Returns:
        string: The symbol for the unit, or None if no unit is used
    """