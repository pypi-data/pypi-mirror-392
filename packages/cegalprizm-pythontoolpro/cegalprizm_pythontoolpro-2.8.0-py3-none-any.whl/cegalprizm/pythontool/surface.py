# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import typing
from warnings import warn

import cegalprizm.pythontool
import math
from cegalprizm.pythontool.parameter_validation import validate_name
import pandas as pd
from cegalprizm.pythontool import _docstring_utils, _utils
from cegalprizm.pythontool import primitives
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithDeletion, PetrelObjectWithTemplate, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory
from cegalprizm.pythontool.petrelobject import PetrelObjectWithHistoryToBeDeprecated, PetrelObjectWithParentFolder, PetrelObjectWithPetrelNameSetter
from cegalprizm.pythontool import _config
from cegalprizm.pythontool.chunk import Chunk
from cegalprizm.pythontool.chunktype import ChunkType
from cegalprizm.pythontool.enums import NumericDataTypeEnum
from cegalprizm.pythontool.exceptions import PythonToolException
from cegalprizm.pythontool.folder import Folder
from cegalprizm.pythontool.template import Template, DiscreteTemplate

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.surface_grpc import SurfaceCollectionGrpc, SurfaceDiscretePropertyGrpc, SurfaceGrpc, SurfacePropertyGrpc
    from cegalprizm.pythontool import InterpretationFolder

class Surface(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion, PetrelObjectWithParentFolder):
    def __init__(self, petrel_object_link: "SurfaceGrpc"):
        super(Surface, self).__init__(petrel_object_link)
        self._surface_object_link = petrel_object_link
        self.__extent: typing.Optional[primitives.Extent] = None    

    @property
    def affine_transform(self):
        """ The affine transform of the object.

        returns:
            1d array: An array with 6 coefficients of the affine transformation matrix. If array is
            represented as [a, b, c, d, e, f] then this corresponds to a affine transformation matrix of
            form:
            | a b e |
            | c d f |
            | 0 0 1 |
        """
        return _utils.from_backing_arraytype(
            self._surface_object_link.GetAffineTransform()
        )

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="Surface")
    def crs_wkt(self):
        return self._surface_object_link.GetCrs()

    @property
    def extent(self) -> primitives.Extent:
        """The number of surface nodes in the i and j directions.

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a node identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

        Returns:
            `cegalprizm.pythontool.Extent`: The number of surface nodes in each direction.
        """
        if self.__extent is None:
            i = self._surface_object_link.NumI()
            j = self._surface_object_link.NumJ()
            self.__extent = cegalprizm.pythontool.Extent(i=i, j=j, k=1)

        return self.__extent

    def __str__(self) -> str:
        """A readable representation of the Surface"""
        return "Surface(petrel_name=\"{0}\")".format(self.petrel_name)

    def indices(self, x: float, y: float) -> primitives.Indices:
        """
        Returns the I, J indices of the surface node nearest to the specified spatial coordinates.

        The returned indices identify the grid node (corner point) closest to the given (X, Y) position on the surface.

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a node identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

        Args:
            x (float): X coordinate in project CRS.
            y (float): Y coordinate in project CRS.

        Returns:
            A :class:`cegalprizm.pythontool.primitives.Indices` object representing the (i, j, k) indices of the nearest surface node (corner point). `k` will always be `None`.

        Raises:
            ValueError: If the specified point lies outside the surface extent.

        **Example:**

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel_connection = PetrelConnection()
            surface = petrel_connection.surfaces.get_by_name("Surface")
            surface.indices(456000.123, 6785000.456)
            >> Indices(i=10, j=20, k=None)

        """
        index2 = self._surface_object_link.IndexAtPosition(x, y)
        if index2 is None:
            raise ValueError("position not in surface")
        if index2 is None or \
           index2.GetValue().I < 0 or \
           index2.GetValue().J < 0 or \
           index2.GetValue().I >= self.extent.i or \
           index2.GetValue().J >= self.extent.j:
            raise ValueError("position not in surface")
        return primitives.Indices(index2.GetValue().I, index2.GetValue().J, None)

    def position(self, i: int, j: int) -> primitives.Point:
        """
        Returns the spatial position (X, Y, Z) of the surface grid node at the specified I, J indices.

        The input indices (i, j) represent a surface grid node, and the returned coordinates correspond to the corner point (node) that defines the origin (lower-left) corner of the corresponding cell in grid space. 
        The coordinates are expressed in world coordinates. The Z value may be NaN if the surface has no defined elevation at that location.

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a node identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.


        Args:
            i (int): I-index of the surface grid node.
            j (int): J-index of the surface grid node.

        Returns:
            A :class:`cegalprizm.pythontool.Point` object representing the (X, Y, Z) coordinates of the surface grid node in world coordinates.

        Raises:
            ValueError: If the specified indices are outside the surface extent.

        **Example:**

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel_connection = PetrelConnection()
            surface = petrel_connection.surfaces.get_by_name("Surface")
            surface.position(10, 20)
            >> Point(x=450560.0, y=6780240.0, z=nan)
        """
        point3 = self._surface_object_link.PositionAtIndex(i, j)
        if point3 is None:
            raise ValueError("Index not valid for surface")
        return primitives.Point(
            point3.GetValue().X, point3.GetValue().Y, point3.GetValue().Z
        )

    def as_dataframe(self, dropna: bool = False) -> pd.DataFrame:
        """Get a dataframe with the I, J, X, Y and Z values of the surface nodes.

        The values in the Z column will be in either time or depth units, depending on the domain of the surface.

        Note:
            surface.as_dataframe() prints out all Is and Js of a regular 2-dimensional grid covering the extent of the surface. This means many Z-values might show up as NaN because no Z value is defined in Petrel. Set the dropna parameter to True to drop all rows where Z is NaN.

        **Example:**
        
        Retrieve the dataframe and drop all rows where Z is NaN

        .. code-block:: Python

            surface = petrellink.surfaces["Input/Path/To/Surface"]
            df = surface.as_dataframe(dropna=True)
        
        Returns:
            pd.DataFrame: A dataframe with the I, J, X, Y and Z values of the surface nodes

        Raises:
            ValueError: if the dropna parameter is not a boolean
        """
        if not isinstance(dropna, bool):
            raise ValueError("dropna must be a boolean")
        return self._surface_object_link.GetPositionsDataframe(dropna)

    @property
    def coords_extent(self) -> primitives.CoordinatesExtent:
        """
        The spatial extent of the surface in world coordinates.

        Returns the minimum and maximum X, Y, and Z coordinates defining the bounding box of the surface grid in project coordinates.
        The extents are calculated from the outermost grid nodes (corner points) of the surface.

        Returns:
            :class:`cegalprizm.pythontool.CoordinatesExtent`: The spatial extent of the surface in world coordinates.

        **Example:**

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel_connection = PetrelConnection()
            surface = petrel_connection.surfaces.get_by_name("Surface")
            surface.coords_extent
            >> CoordinatesExtent(
                x_axis=AxisExtent(min=450800.0, max=459080.0),
                y_axis=AxisExtent(min=6780240.0, max=6790240.0),
                z_axis=AxisExtent(min=-2500.0, max=-1500.0)
               )

        """
        return primitives.CoordinatesExtent(self._surface_object_link.AxesRange())

    @property
    def parent_collection(self) -> "Surfaces":
        """
        .. warning::
            **Deprecated** - This property will be removed in Python Tool Pro 3.0. Use :attr:`parent_folder` instead.

        The parent collection containing this surface.

        Iterating through this collection will return this surface and all its siblings in the Petrel Input Tree.

        Returns:

            cegalprizm.pythontool.Surfaces: the parent collection
        """
        warn("parent_collection property will be removed in Python Tool Pro 3.0. Use parent_folder instead.", DeprecationWarning, stacklevel=2)
        return Surfaces(self._surface_object_link.ParentSurfaceCollection())

    @property
    def surface_attributes(self) -> "SurfaceAttributes":
        """The attributes for this surface

        Returns:

            cegalprizm.pythontool.SurfaceAttributes: the attributes for the surface
        """
        surface_properties = self._surface_object_link.GetSurfaceProperties()
        surface_dict_properties = self._surface_object_link.GetDictionarySurfaceProperties()
        
        return SurfaceAttributes(self, surface_properties, surface_dict_properties)

    @_docstring_utils.create_surface_attribute_docstring_decorator()
    @validate_name(param_name="name")
    def create_attribute(self, name: str = "", data_type: typing.Union[str, "NumericDataTypeEnum"] = None, template: typing.Union["DiscreteTemplate", "Template"] = None) -> typing.Union["SurfaceAttribute", "SurfaceDiscreteAttribute"]:
        if self.readonly:
            raise PythonToolException("Surface is readonly")

        if data_type is None:
            if template is None or isinstance(template, Template):
                data_type = NumericDataTypeEnum.Continuous
            else:
                data_type = NumericDataTypeEnum.Discrete

        if not isinstance(data_type, NumericDataTypeEnum):
            if not isinstance(data_type, str):
                raise TypeError("data_type must be a string or NumericDataTypeEnum")
            elif data_type.lower() == NumericDataTypeEnum.Continuous.value:
                data_type = NumericDataTypeEnum.Continuous
            elif data_type.lower() == NumericDataTypeEnum.Discrete.value:
                data_type = NumericDataTypeEnum.Discrete
            else:
                raise ValueError("data_type must be 'continuous' or 'discrete'")
        else:
            if data_type != NumericDataTypeEnum.Continuous and data_type != NumericDataTypeEnum.Discrete:
                raise ValueError("data_type must be NumericDataTypeEnum.Continuous or NumericDataTypeEnum.Discrete")
        
        if not isinstance(template, (Template, DiscreteTemplate)) and template is not None:
            raise TypeError("Template must be a Template or DiscreteTemplate object")

        discrete = data_type == NumericDataTypeEnum.Discrete

        if discrete and isinstance(template, Template):
            raise ValueError("Cannot create a discrete attribute with a continuous Template.")
        if not discrete and isinstance(template, DiscreteTemplate):
            raise ValueError("Cannot create a continuous attribute with a DiscreteTemplate.")

        grpc_object = self._surface_object_link.CreateAttribute(name, discrete, template)
        if discrete:
            return SurfaceDiscreteAttribute(grpc_object) if grpc_object else None
        else:
            return SurfaceAttribute(grpc_object) if grpc_object else None

    def positions_to_ijks(self, positions: typing.Union[typing.Tuple[typing.List[float], typing.List[float]], typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]])\
            -> typing.Tuple[typing.List[int], typing.List[int]]:
        """
        Converts lists of X and Y coordinates to I, J indices of surface grid nodes.

        The input coordinates represent positions in world coordinates. The returned indices correspond to the nearest surface grid nodes (corner points).
        
        The length of the output lists is determined by the length of the input [x] list. It is possible to provide a [y] list with more items than the [x] list, but no output is calculated for the extra items. Providing a [y] list with fewer items than the [x] list will raise an exception.

        Multiple positions may be located near the same surface grid node, in which case the same I, J indices will be returned for those positions.

        Note:
            When coordinates fall outside the spatial extent of the surface, the returned I, J values represent the extrapolated grid positions based on the surface's underlying grid geometry. Both negative indices and positive indices greater than the surface extent may be returned.

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a node identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

        Args:
            positions (tuple(list[float], list[float])): A tuple([x],[y]) where [x] and [y] are lists of coordinates in world units. The tuple may optionally contain a third list [z], although these values will not be used in the conversion.

        Returns:
            tuple(list[int], list[int]): A tuple([i],[j]) where [i] and [j] are lists of node indices corresponding to the nearest surface grid nodes (corner points).

        Raises:
            UnexpectedErrorException: If the [y] list contains fewer items than the [x] list.

        **Example:**

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            surface = petrel.surfaces.get_by_name("Surface")
            surface.positions_to_ijks(([450800.0, 451280.0, 451760.0], [6780240.0, 6780340.0, 6780440.0]))
            >> ([0, 1, 2], [4, 5, 6])
        """
        return _utils.positions_to_ijks_2d(self._surface_object_link, positions)

    def ijks_to_positions(self, indices: typing.Tuple[typing.List[float], typing.List[float]])\
            -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        """
        Converts lists of I, J indices to X, Y, Z coordinates of surface grid nodes (corner points).
        
        The input indices (i, j) represent surface grid nodes. The returned coordinates correspond to the corner points (nodes), not cell centers.

        The length of the output lists is determined by the length of the input [i] list. It is possible to provide a [j] list with more items than the [i] list, but no output is calculated for the extra items. Providing a [j] list with fewer items than the [i] list will raise an exception.

        Note:
            The returned position is the position of the nearest node (cell corner). This means a conversion from positions to ijs and back to positions may not always return the exact original positions.

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a node identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

        Args:
            indices (tuple(list[int], list[int])): A tuple([i],[j]) where [i] and [j] are lists of node indices.

        Returns:
            tuple(list[float], list[float], list[float]): A tuple([x],[y],[z]) containing the world-coordinate positions of the requested nodes. Z values may be NaN if the surface has no defined elevation at those nodes.

        Raises:
            PythonToolException: If any of the i or j indices are negative or greater than the object extent.
            UnexpectedErrorException: If the [j] list contains fewer items than the [i] list.

        **Example:**

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            surface = petrel.surfaces.get_by_name("SurfaceName")
            surface.ijks_to_positions(([0, 1, 2], [10, 11, 12]))
            >> ([450800.0, 451280.0, 451760.0], [6780240.0, 6780240.0, 6780240.0], [nan, -1234.56, nan])
        """
        return _utils.ijks_to_positions(extent = self.extent, 
                                        object_link = self._surface_object_link, 
                                        indices = indices, 
                                        dimensions = 2)

    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

    @_docstring_utils.move_docstring_decorator(object_type="Surface")
    def move(self, destination: "Folder"):
        if self.readonly:
            raise PythonToolException("Surface is readonly")
        _utils.verify_folder(destination)
        self._move(destination)

    @property
    def parent_folder(self) -> typing.Union["Folder", "InterpretationFolder", None]:
        """Returns the parent folder of this Surface in Petrel. Returns None if the object is the Input root.

        Returns:
            :class:`Folder`, :class:`InterpretationFolder` or None: The parent folder of the Surface, or None if the object is located at the root level.

        **Example**:

        .. code-block:: python

            surface = petrel_connection.surfaces["Input/Folder/Surface"]
            surface.parent_folder
            >> Folder(petrel_name="Folder")
        """
        return self._parent_folder


class SurfaceAttributes():
    """A readonly iterable collection of a set of surface attributes

    This example prints out all sibling attributes of a particular attribute:

    **Example:**

        .. code-block:: Python

            all_attributes = my_attr.surface.surface_attributes
            for attr in all_attributes:
                if attr != my_attr:
                    print(attr)

    """
    def __init__(self, parent, surface_properties, surface_dict_properties):
        self._parent_obj = parent
        self._surface_attributes = []

        for attr in surface_properties:
            self._surface_attributes.append(SurfaceAttribute(attr))
        for attr in surface_dict_properties:
            self._surface_attributes.append(SurfaceDiscreteAttribute(attr))
        
    def __len__(self) -> int:
        return len(self._surface_attributes)

    def __iter__(self) -> typing.Iterable[typing.Union["SurfaceAttribute", "SurfaceDiscreteAttribute"]]:
        return iter(self._surface_attributes)

    def __str__(self) -> str:
        return 'SurfaceAttributes({0}="{1}")'.format(self._parent_obj._petrel_object_link._sub_type, self._parent_obj)

    def __repr__(self) -> str:
        return str(self)

class Surfaces(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistoryToBeDeprecated):
    """A readonly collection of a set of regular surfaces.

    Although this object wraps a Petrel collection, it does not support any operations on it apart from iterating through its contents.
    """

    def __init__(self, petrel_object_link: "SurfaceCollectionGrpc"):
        super(Surfaces, self).__init__(petrel_object_link)
        self._surfaces_object_link = petrel_object_link
        
    def __len__(self) -> int:
        surfaces = []
        for surface in self._surfaces_object_link.GetRegularHeightFieldObjects():
            s = Surface(surface)
            surfaces.append(s)
        return len(surfaces)

    def __iter__(self) -> typing.Iterable[Surface]:
        surfaces = []
        for surface in self._surfaces_object_link.GetRegularHeightFieldObjects():
            s = Surface(surface)
            surfaces.append(s)
        return iter(surfaces)

    def __getitem__(self, idx: int) -> Surface:
        surfaces = []
        for surface in self._surfaces_object_link.GetRegularHeightFieldObjects():
            s = Surface(surface)
            surfaces.append(s)
        return surfaces[idx] # type: ignore

    def __str__(self) -> str:
        """A readable representation of the Surfaces collection"""
        return 'Surfaces(petrel_name="{0}")'.format(self.petrel_name)


class SurfaceAttribute(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):

    def __init__(self, petrel_object_link: "SurfacePropertyGrpc"):
        super(SurfaceAttribute, self).__init__(petrel_object_link)
        self._surfaceattribute_object_link = petrel_object_link

    @property
    def affine_transform(self):
        """ The affine transform of the object.

        returns:
            1d array: An array with 6 coefficients of the affine transformation matrix. If array is
            represented as [a, b, c, d, e, f] then this corresponds to a affine transformation matrix of
            form:
            | a b e |
            | c d f |
            | 0 0 1 |
        """
        return _utils.from_backing_arraytype(
            self._surfaceattribute_object_link.GetAffineTransform()
        )

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="SurfaceAttribute")
    def crs_wkt(self):
        return "Well-known text representation of coordinate reference systems not available for SurfaceAttribute objects"

    def __str__(self) -> str:
        """A readable representation of the SurfaceAttribute"""
        return 'SurfaceAttribute(petrel_name="{0}")'.format(self.petrel_name)

    def is_undef_value(self, value: typing.Union[int, float]) -> bool:
        """Whether the value is the 'undefined value' for the attribute

        Petrel represents some undefined values by ``MAX_INT``, others
        by ``NaN``.  A comparison with ``NaN`` will always return
        ``False`` (e.g. ``float.nan != float.nan``) so it is
        preferable to always use this method to test for undefined
        values.

        Args:
            value: the value to test

        Returns:
            bool: True if value is 'undefined' for this surface
            attribute

        """
        return self._is_undef_value(value)

    @property
    def undef_value(self) -> float:
        """The 'undefined value' for this attribute

        Use this value when setting a slice's value to 'undefined'.
        Do not attempt to test for undefinedness by comparing with
        this value, use :meth:`is_undef_value` instead.

        Returns:
           The 'undefined value' for this attribute
        """
        return self._undef_value()

    def _undef_value(self) -> float:
        return float("nan")

    @property
    def unit_symbol(self) -> typing.Optional[str]:
        """The symbol for the unit which the values are measured in

        Returns:

            string: The symbol for the unit, or None if no unit is used
        """
        return self._unit_symbol()

    @_docstring_utils.clone_docstring_decorator(return_type="SurfaceAttribute", respects_subfolders=True, continuous_template=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, template: "Template" = None) -> "SurfaceAttribute":
        _utils.verify_continuous_clone(copy_values, template)
        return typing.cast("SurfaceAttribute", self._clone(name_of_clone, copy_values = copy_values, template = template))

    def _unit_symbol(self) -> typing.Optional[str]:
        return _utils.str_or_none(self._surfaceattribute_object_link.GetDisplayUnitSymbol())

    def _is_undef_value(self, value: typing.SupportsFloat) -> bool:
        return math.isnan(value)

    @property
    def parent_surface(self) -> None:
        """DeprecationWarning: 'parent_surface' has been removed. Use 'surface' instead
        """
        warn("'parent_surface' has been removed. Use 'surface' instead", 
             DeprecationWarning, stacklevel=2)
        raise RuntimeError("'parent_surface' has been removed. Use 'surface' instead")

    @property
    def surface(self) -> Surface:
        """The parent surface of the attribute

        Returns:

            cegalprizm.pythontool.Surface: The parent surface of the attribute
        """
        parent = self._surfaceattribute_object_link.GetParentSurface()
        parent_s = Surface(parent)

        return parent_s 

    def all(self) -> Chunk:
        """Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the attribute

        Returns:

            cegalprizm.pythontool.Chunk:  A `Slice` containing the values for the attribute
        """
        return self._make_chunk(i = None, j = None)

    def chunk(self, irange: typing.Tuple[int, int] = None, jrange: typing.Tuple[int, int] = None) -> Chunk:
        """
        Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the attribute
        
        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a node identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

        Args:
            i: A tuple(i1,i2) where i1 is the start index and i2 is the end index. The start and end value in this range is inclusive. If None include all i values.
            j: A tuple(j1,j2) where j1 is the start index and j2 is the end index. The start and end value in this range is inclusive. If None include all j values.

        Returns:

            cegalprizm.pythontool.Chunk:  A `Slice` containing the values for the attribute
        """
        return self._make_chunk(i=irange, j=jrange)

    def _make_chunk(self, i=None, j=None) -> Chunk:
        extent = self.surface.extent
        value_getters = {
            ChunkType.k: lambda i, j, k: _utils.from_backing_arraytype(
                self._surfaceattribute_object_link.GetChunk(i, j)
            )
        }
        value_setters = {
            ChunkType.k: lambda i, j, k, values: self._surfaceattribute_object_link.SetChunk(
                i, j, _utils.to_backing_arraytype(values)
            )
        }
        value_shapers = {
            ChunkType.k: lambda i, j, k, values: _utils.ensure_2d_float_array(
                values, i, j
            )
        }
        value_accessors = {ChunkType.k: lambda i, j, k: _utils.native_accessor((i, j))}

        return cegalprizm.pythontool.Chunk(
            i,
            j,
            None,
            self,
            extent,
            value_getters,
            value_setters,
            value_shapers,
            value_accessors,
            (True, True, False),
            ChunkType.k,
            readonly=self.readonly,
        )

    def has_same_parent(self, other: "SurfaceAttribute") -> bool:
        """Tests whether the surface attribute has the same parent surface

        Args:
            other: the other surface attribute

        Returns:
            bool: ``True`` if the ``other`` object has the same parent surface

        Raises:
            ValueError: if ``other`` is not a SurfaceAttribute
        """
        if not isinstance(other, SurfaceAttribute):
            raise ValueError("can only compare parent with other SurfaceAttribute")
        return ( 
            self.surface._surface_object_link.GetDroidString()
            == other.surface._surface_object_link.GetDroidString()
        )

    def positions_to_ijks(self, positions: typing.Union[typing.Tuple[typing.List[float], typing.List[float]], typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]]) \
            -> typing.Tuple[typing.List[int], typing.List[int]]:
        """
        Converts lists of X and Y coordinates to I, J indices of surface grid nodes.

        The input coordinates represent positions in world coordinates. The returned indices correspond to the nearest surface grid nodes (corner points).
        
        The length of the output lists is determined by the length of the input [x] list. It is possible to provide a [y] list with more items than the [x] list, but no output is calculated for the extra items. Providing a [y] list with fewer items than the [x] list will raise an exception.

        Multiple positions may be located near the same surface grid node, in which case the same I, J indices will be returned for those positions.

        Note:
            When coordinates fall outside the spatial extent of the surface attribute, the returned I, J values represent the extrapolated grid positions based on the surface attribute's underlying grid geometry. Both negative indices and positive indices greater than the surface attribute extent may be returned.

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a node identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

        Args:
            positions (tuple(list[float], list[float])): A tuple([x],[y]) where [x] and [y] are lists of coordinates in world units. The tuple may optionally contain a third list [z], although these values will not be used in the conversion.

        Returns:
            tuple(list[int], list[int]): A tuple([i],[j]) where [i] and [j] are lists of node indices corresponding to the nearest surface grid nodes (corner points).

        Raises:
            UnexpectedErrorException: If the [y] list contains fewer items than the [x] list.

        **Example:**

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            surface_attribute = petrel.surface_attributes.get_by_name("AttributeName")
            surface_attribute.positions_to_ijks(([450800.0, 451280.0, 451760.0], [6780240.0, 6780340.0, 6780440.0]))
            >> ([0, 1, 2], [4, 5, 6])
        """
        return _utils.positions_to_ijks_2d(self._surfaceattribute_object_link, positions)

    def ijks_to_positions(self, indices: typing.Tuple[typing.List[float], typing.List[float]]) -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        """
        Converts lists of I, J indices to X, Y, Z coordinates of surface grid nodes (corner points).
        
        The input indices (i, j) represent surface grid nodes. The returned coordinates correspond to the corner points (nodes), not cell centers.

        The length of the output lists is determined by the length of the input [i] list. It is possible to provide a [j] list with more items than the [i] list, but no output is calculated for the extra items. Providing a [j] list with fewer items than the [i] list will raise an exception.

        Note:
            The returned position is the position of the nearest node (cell corner). This means a conversion from positions to ijs and back to positions may not always return the exact original positions.

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a node identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

        Args:
            indices (tuple(list[int], list[int])): A tuple([i],[j]) where [i] and [j] are lists of node indices.

        Returns:
            tuple(list[float], list[float], list[float]): A tuple([x],[y],[z]) containing the world-coordinate positions of the requested nodes. Z values may be NaN if the surface has no defined elevation at those nodes.

        Raises:
            PythonToolException: If any of the i or j indices are negative or greater than the object extent.
            UnexpectedErrorException: If the [j] list contains fewer items than the [i] list.

        **Example:**

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            surface_attribute = petrel.surface_attributes.get_by_name("AttributeName")
            surface_attribute.ijks_to_positions(([0, 1, 2], [10, 11, 12]))
            >> ([450800.0, 451280.0, 451760.0], [6780240.0, 6780240.0, 6780240.0], [nan, -1234.56, nan])
        """
        return _utils.ijks_to_positions(extent = self.surface.extent, 
                                        object_link = self._surfaceattribute_object_link, 
                                        indices = indices, 
                                        dimensions = 2)

    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

class SurfaceDiscreteAttribute(SurfaceAttribute):

    def __init__(self, petrel_object_link: "SurfaceDiscretePropertyGrpc"):
        super(SurfaceDiscreteAttribute, self).__init__(petrel_object_link)
        self._surfacediscreteattribute_object_link = petrel_object_link
        self._discrete_codes = None

    def __str__(self) -> str:
        """A readable representation of the SurfaceDiscreteAttribute"""
        return 'SurfaceDiscreteAttribute(petrel_name="{0}")'.format(self.petrel_name)

    def _unit_symbol(self) -> None:
        return None

    @property
    def discrete_codes(self) -> typing.Dict[str, str]:
        """A dictionary of discrete codes and values

        Changes to this dictionary will not be persisted or affect any Petrel objects.

        **Example:**

        .. code-block:: Python

            myattr = petrellink.surface_discrete_attributes['facies']
            print(myattr.discrete_codes[1])
            # outputs 'Fine sand'
        """
        if self._discrete_codes is None:
            self._discrete_codes = self.__make_discrete_codes_dict()
        return self._discrete_codes

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="SurfaceDiscreteAttribute")
    def crs_wkt(self):
        return "Well-known text representation of coordinate reference systems not available for SurfaceDiscreteAttribute objects"

    @_docstring_utils.clone_docstring_decorator(return_type="SurfaceDiscreteAttribute", respects_subfolders=True, discrete_template=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, discrete_template: "DiscreteTemplate" = None) -> "SurfaceDiscreteAttribute":
        _utils.verify_discrete_clone(copy_values, discrete_template)
        return typing.cast("SurfaceDiscreteAttribute", self._clone(name_of_clone, copy_values = copy_values, template = discrete_template))

    def _undef_value(self) -> int:
        return _config._INT32MAXVALUE

    def _is_undef_value(self, value) -> bool:
        return value == _config._INT32MAXVALUE

    def __make_discrete_codes_dict(self) -> typing.Dict[int, str]:
        codes = {}
        for tup in self._surfacediscreteattribute_object_link.GetAllDictionaryCodes():
            k = tup.Item1
            v = tup.Item2
            codes[k] = v
        return codes

    def _make_chunk(self, i=None, j=None):
        extent = self.surface.extent
        value_getters = {
            ChunkType.k: lambda i, j, k: _utils.from_backing_arraytype(
                self._surfacediscreteattribute_object_link.GetChunk(i, j)
            )
        }
        value_setters = {
            ChunkType.k: lambda i, j, k, values: self._surfacediscreteattribute_object_link.SetChunk(
                i, j, _utils.to_backing_arraytype(values)
            )
        }
        value_shapers = {
            ChunkType.k: lambda i, j, k, values: _utils.ensure_2d_int_array(values, i, j)
        }
        value_accessors = {ChunkType.k: lambda i, j, k: _utils.native_accessor((i, j))}

        return cegalprizm.pythontool.Chunk(
            i,
            j,
            None,
            self,
            extent,
            value_getters,
            value_setters,
            value_shapers,
            value_accessors,
            (True, True, False),
            ChunkType.k,
            readonly=self.readonly,
        )

