# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




import typing
from warnings import warn
from cegalprizm.pythontool.gridpropertycollection import PropertyCollection, PropertyFolder
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithDeletion
from cegalprizm.pythontool.petrelobject import PetrelObjectWithPetrelNameSetter
from cegalprizm.pythontool.template import Template, DiscreteTemplate

import math

from cegalprizm.pythontool.chunk import Chunk
from cegalprizm.pythontool import grid
from cegalprizm.pythontool import _utils, _docstring_utils
from cegalprizm.pythontool import exceptions
from cegalprizm.pythontool import primitives
from datetime import datetime
from cegalprizm.pythontool.chunktype import ChunkType

from cegalprizm.pythontool import _config

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.gridproperty_grpc import GridDiscretePropertyGrpc, GridPropertyGrpc

class GridProperty(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    def __init__(self, petrel_object_link: "GridPropertyGrpc"):
        super(GridProperty, self).__init__(petrel_object_link)
        self._gridproperty_object_link = petrel_object_link
        self._grid = None

    @property
    def parent_grid(self) -> None:
        """DeprecationWarning: 'parent_grid' has been removed. Use 'grid' instead
        """
        warn("'parent_grid' has been removed. Use 'grid' instead", 
             DeprecationWarning, stacklevel=2)
        raise RuntimeError("'parent_grid' has been removed. Use 'grid' instead")

    @property
    def grid(self) -> grid.Grid:
        """The parent grid of the property

        Returns:
            cegalprizm.pythontool.Grid: The parent grid of the property
        """
        if self._grid is None:
            self._grid = grid.Grid(self._gridproperty_object_link.GetParentPythonGridObject())
        return self._grid


    @property
    def date(self) -> typing.Optional[datetime]:
        """The date and time recorded for the property, if the property is associated with a date. Use the 'use_date' property to check if the property is associated with a date.
        If the property is not associated with a date, 'None' is returned.
        The date can be set by providing a datetime object. In case the use_date property is set to False, it will be set to True in order to set the date for the GridProperty.

        **Example**:

        .. code-block:: Python

            import datetime
            myproperty = petrel.grid_properties["Models/Structural grids/Model/Properties/MyProperty"]
            print(myproperty)
            >> GridProperty(petrel_name="MyProperty")
            myproperty.readonly = False
            new_date = datetime.datetime(2025, 5, 5, 11, 30, 45)
            myproperty.date = new_date
            print(myproperty)
            >> GridProperty(petrel_name="MyProperty", date="2025-05-05 11:30:45")

        Args:
            date: The datetime to set for the GridProperty

        Returns:
            datetime: The datetime recorded, or `None` if not used
        
        Raises:
            PythonToolException: If the property is read-only.
            TypeError: If the provided input is not a datetime object.
        """
        raw_date = self._gridproperty_object_link.GetDate()
        return raw_date

    @date.setter
    def date(self, date: typing.Optional[datetime]):
        if self.readonly:
            raise exceptions.PythonToolException("GridProperty is readonly")
        if not isinstance(date, datetime):
            raise TypeError("date must be a datetime.datetime object")
        self._gridproperty_object_link.SetDate(date)

    @property
    def use_date(self) -> bool:
        """Boolean value indicating whether this property is associated with a date. This corresponds to the Date checkbox in Petrel, and can be used to determine if the date property can be read and written to.
        Note that changing this also changes the display name of the property in Petrel and when printing the python object.
        If the date value was not previously set, it will be set to the current date and time. If the date value was previously set, the same date as before will be used.

        **Example**:

        .. code-block:: Python

            myproperty = petrel.grid_properties["Models/Structural grids/Model/Properties/MyProperty"]
            print(myproperty)
            >> GridProperty(petrel_name="MyProperty")
            myproperty.readonly = False
            myproperty.use_date = True
            print(myproperty)
            >> GridProperty(petrel_name="MyProperty", date="2025-05-05 12:00:00")

        Args:
            use_date: A boolean value indicating whether this property is associated with a date.

        Returns:
            bool: True if the property is associated with a date, False otherwise.

        Raises:
            PythonToolException: If the property is read-only.
            TypeError: If attempting to set a non-boolean value.
        """
        return self._gridproperty_object_link.GetUseDate()
    
    @use_date.setter
    def use_date(self, use_date: bool):
        if self.readonly:
            raise exceptions.PythonToolException("GridProperty is readonly")
        if not isinstance(use_date, bool):
            raise TypeError("use_date must be a boolean")
        self._gridproperty_object_link.SetUseDate(use_date)

    def is_undef_value(self, value: typing.Union[float, int]) -> bool:
        """Whether the value is the 'undefined' value for the property

        Petrel represents some undefined values by ``MAX_INT``, others by ``NaN``.  A comparison with ``NaN`` will always return
        ``False`` (e.g. ``float.nan != float.nan``) so it is preferable to always use this method to test for undefined values.

        Args:
            value: The value to test if it is 'undefined' in Petrel

        Returns:
            bool: True if the value is 'undefined' for this property
        """        
        return self._is_undef_value(value)

    @property
    def undef_value(self) -> float:
        """The 'undefined value' for this property

        Use this value when setting a slice's value to 'undefined'.
        Do not attempt to test for undefined value by comparing with
        this value, use :meth:`is_undef_value` instead.

        Returns:
           The 'undefined value' for this property
        """
        return self._undef_value()

    @property
    def unit_symbol(self) -> typing.Optional[str]:
        """Returns the symbol of the object unit, None if template of object is unitless."""
        return self._unit_symbol()

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="GridProperty")
    def crs_wkt(self):
        return "Well-known text representation of coordinate reference systems not available for GridProperty objects."

    @property
    def upscaled_cells(self) -> typing.List[primitives.Indices]:
        """Get/set the cell indices of values which have been upscaled

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        **Example:**

        .. code-block:: Python

            myproperty.upscaled_cells = [Indices(20, 24, 5), Indices(20, 24, 6)]
            print(len(myproperty.upscaled_cells))
            # outputs '2'

        Returns:
            List: a list of :class:`cegalprizm.pythontool.Indices` of the upscaled cells
        """
        tuples = self._gridproperty_object_link.GetUpscaledCells()
        return [primitives.Indices(tup.Item1, tup.Item2, tup.Item3) for tup in tuples]

    @upscaled_cells.setter
    def upscaled_cells(self, cells: typing.List[primitives.Indices]):
        if self.readonly:
            raise exceptions.PythonToolException("GridProperty is readonly")
        if cells is None:
            cells = []
        num = len(cells)
        ii = [int(0)] * num
        jj = [int(0)] * num
        kk = [int(0)] * num
        
        for i, cell in enumerate(cells):
            ii[i] = cell.i
            jj[i] = cell.j
            kk[i] = cell.k
        self._gridproperty_object_link.SetUpscaledCells(ii, jj, kk)

    @_docstring_utils.clone_docstring_decorator(return_type="GridProperty", respects_subfolders=True, continuous_template=True, supports_folder=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, template: "Template" = None, folder: "PropertyFolder" = None) -> "GridProperty":
        _utils.verify_continuous_clone(copy_values, template)
        return typing.cast("GridProperty", self._clone(name_of_clone, copy_values = copy_values, template = template, destination = folder))

    def _unit_symbol(self) -> typing.Optional[str]:
        return _utils.str_or_none(self._gridproperty_object_link.GetDisplayUnitSymbol())

    def _undef_value(self) -> float:
        return float('nan')

    def _is_undef_value(self, value) -> bool:
        return math.isnan(value)

    def _make_chunk(self, i=None, j=None, k=None) -> "Chunk":
        value_getters = {ChunkType.ij:
                         lambda i, j, k: _utils.from_backing_arraytype(self._gridproperty_object_link.GetColumn(i, j)),
                         ChunkType.k:
                         lambda i, j, k: _utils.from_backing_arraytype(self._gridproperty_object_link.GetLayer(k)),
                         ChunkType.none:
                         lambda i, j, k: _utils.from_backing_arraytype(self._gridproperty_object_link.GetAll()),
                         ChunkType.chunk:
                         lambda i, j, k: _utils.from_backing_arraytype(self._gridproperty_object_link.GetChunk(i, j, k))}
        value_setters = {ChunkType.ij:
                         lambda i, j, k, values: self._gridproperty_object_link.SetColumn(i, j, _utils.to_backing_arraytype(values)),
                         ChunkType.k:
                         lambda i, j, k, values: self._gridproperty_object_link.SetLayer(k, _utils.to_backing_arraytype(values)),
                         ChunkType.none:
                         lambda i, j, k, values: self._gridproperty_object_link.SetAll(_utils.to_backing_arraytype(values)),
                         ChunkType.chunk:
                         lambda i, j, k, values: self._gridproperty_object_link.SetChunk(i, j, k, _utils.to_backing_arraytype(values))}
        value_shapers = {ChunkType.ij:
                         lambda i, j, k, values: _utils.ensure_1d_float_array(values, k),
                         ChunkType.k:
                         lambda i, j, k, values: _utils.ensure_2d_float_array(values, i, j),
                         ChunkType.none:
                         lambda i, j, k, values: _utils.ensure_3d_float_array(values, i, j, k),
                         ChunkType.chunk:
                         lambda i, j, k, values: _utils.ensure_3d_float_array(values, i, j, k)}
        value_accessors = {ChunkType.ij:
                           lambda i, j, k: k,
                           ChunkType.k:
                           lambda i, j, k:  _utils.native_accessor((i, j)),
                           ChunkType.none:
                           lambda i, j, k: _utils.native_accessor((i, j, k)),
                           ChunkType.chunk:
                           lambda i, j, k: _utils.native_accessor((i, j, k))}
        return Chunk(i, j, k,
                           self,
                           self.grid.extent,
                           value_getters,
                           value_setters,
                           value_shapers,
                           value_accessors,
                           (True, True, True),
                           readonly=self.readonly)

    def all(self) -> Chunk:
        """Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the property

        Returns:
            cegalprizm.pythontool.Chunk:  A `Chunk` containing the values for the property
        """
        return self._make_chunk(i=None, j=None, k=None)

    def chunk(self,
            irange: typing.Tuple[int, int],
            jrange: typing.Tuple[int, int],
            krange: typing.Tuple[int, int])\
            -> Chunk:
        """Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the specified ranges

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Args:
            i: inclusive range in the i-direction
            j: inclusive range in the j-direction
            k: inclusive range in the k-direction

        Returns:
            cegalprizm.pythontool.Chunk: A `Chunk` containing the values for all layers

        Raises:
            ValueError: if the ranges specify volumes outside the property's extent
        """
        return self._make_chunk(i=irange, j=jrange, k=krange)

    def column(self, i: int, j: int) -> Chunk:
        """
        Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the specified column

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

        Args:
            i: the index in the i-direction
            j: the index in the j-direction

        Returns:
            cegalprizm.pythontool.Chunk: A `Chunk` containing the values for all layers

        Raises:
            ValueError: if the property does not have the column specified
        """
        return self._make_chunk(i=i, j=j)

    def layer(self, k: int) -> Chunk:
        """
        Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the specified layer

        Note:
            Python Tool Pro K indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (k = 6) in Python corresponds to (k = 7) in Petrel.

        Args:
            k: the index in the k-direction (the layer)

        Returns:
            cegalprizm.pythontool.Chunk: A `Chunk` containing the values for the layer

        Raises:
            ValueError: if the property does not have the layer specified
        """
        return self._make_chunk(k=k)

    def __str__(self) -> str:
        """A readable representation of the GridProperty"""
        if self.date is None:
            return "GridProperty(petrel_name=\"{0}\")".format(self.petrel_name)
        else:
            return "GridProperty(petrel_name=\"{0}\", date=\"{1}\")".format(self.petrel_name, self.date)

    def columns(self,
            irange: typing.Tuple[int, int] = None,
            jrange: typing.Tuple[int, int] = None)\
            -> typing.Iterator[Chunk]:
        """
        Returns a generator of column slices

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.        
        
        Args:
            irange: an iterable (e.g list) of i-values to generate columns for. If `None`, generate for all i-values.
            jrange: an iterable (e.g. list) of j-values to generate columns for.  If `None`, generate for all j-values.
        
        Yields:
            A generator of column :class:`cegalprizm.pythontool.Chunk` objects covering the `irange` and `jrange` passed.

        Raises:
            ValueError: if the indices are invalid.

        **Example**:

        .. code-block:: python

          # sets to 0 all values in the i-slices i=10 through to i=19,
          for col in my_prop.columns(irange=range(10, 20), jrange=None):
              col.set(0)

          # sets to 0 all values in the property
          for col in my_prop.columns():
              col.set(0)        
        """        

        irange_used = irange if irange is not None else range(self.grid.extent.i)
        jrange_used = jrange if jrange is not None else range(self.grid.extent.j)
        for i in irange_used:
            for j in jrange_used:
                yield self.column(i, j)

    def layers(self, krange: typing.Tuple[int, int] = None)\
            -> typing.Iterator[Chunk]:
        """
        Returns a generator of layer slices
        
        Note:
            Python Tool Pro K indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (k = 6) in Python corresponds to (k = 7) in Petrel.

        Args:
          krange: an iterable (e.g.) of k-values to generate layers for. If `None`, generate for all k-values.

        Yields:
            A generator of layer :class:`cegalprizm.pythontool.Chunk` objects covering the
            `krange` passed
        
        **Example**:

        .. code-block:: python

          # sets to 0 all values in the k-slices k=10 through to k=19,
          for layer in my_prop.layers(range(10, 20)):
              layer.set(0)

          # sets to 0 all values in the property
          for layer in my_prop.layers():
              layer.set(0)
        """   
        krange_used = krange if krange is not None else range(self.grid.extent.k)
        for k in krange_used:
            yield self.layer(k)


    def has_same_parent(self, other: "GridProperty") -> bool:
        """Tests whether the grid property has the same parent grid

        Args:
            other: the other grid property

        Returns:
            bool: ``True`` if the ``other`` object has the same grid

        Raises:
            ValueError: if ``other`` is not a GridProperty
        """
        if not isinstance(other, GridProperty):
            raise ValueError("can only compare parent with other GridProperty")
        return self.grid._grid_object_link.GetDroidString() == other.grid._grid_object_link.GetDroidString()

    @property
    def parent_collection(self) -> typing.Optional["PropertyCollection"]:
        """
        .. warning::
            **Deprecated** - This property will be removed in Python Tool Pro 3.0. Use :attr:`parent_folder` instead.

        The parent collection for the grid property

        Returns:
            cegalprizm.pythontool.PropertyCollection: the parent collection, or `None`"""
        warn("parent_collection property will be removed in Python Tool Pro 3.0. Use parent_folder instead.", DeprecationWarning, stacklevel=2)
        coll = self._gridproperty_object_link.GetParentPropertyCollection()
        if coll is None:
            return None

        return PropertyCollection(coll)

    @property
    def parent_folder(self) -> typing.Optional["PropertyFolder"]:
        """The parent folder for the grid property

        Returns:
            cegalprizm.pythontool.PropertyFolder: the parent folder, or `None`"""
        coll = self._gridproperty_object_link.GetParentPropertyFolder()
        if coll is None:
            return None

        return PropertyFolder(coll)

    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()
    



class GridDiscreteProperty(GridProperty):
    def __init__(self, petrel_object_link: "GridDiscretePropertyGrpc"):
        super(GridDiscreteProperty, self).__init__(petrel_object_link)
        self._griddiscreeteproperty_object_link = petrel_object_link
        self._discrete_codes = None

    @_docstring_utils.clone_docstring_decorator(return_type="GridDiscreteProperty", respects_subfolders=True, discrete_template=True, supports_folder=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, discrete_template: "DiscreteTemplate" = None, folder: "PropertyFolder" = None) -> "GridDiscreteProperty":
        _utils.verify_discrete_clone(copy_values, discrete_template)
        return typing.cast("GridDiscreteProperty", self._clone(name_of_clone, copy_values = copy_values, template = discrete_template, destination = folder))

    @property
    def discrete_codes(self) -> typing.Dict[int, str]:
        """A dictionary of discrete codes and values

        Changes to this dictionary will not be persisted or affect any Petrel objects.

        **Example:**

        .. code-block:: Python

            print(my_discreteprop.discrete_codes[1])
            # outputs 'Fine sand'
        """
        if self._discrete_codes is None:
            self._discrete_codes = self.__make_discrete_codes_dict()
        return self._discrete_codes

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="GridDiscreteProperty")
    def crs_wkt(self):
        return "Well-known text representation of coordinate reference systems not available for GridDiscreteProperty objects."

    def _undef_value(self):
        return _config._INT32MAXVALUE

    def _is_undef_value(self, value):
        return value == _config._INT32MAXVALUE

    def _unit_symbol(self):
        return None

    def __make_discrete_codes_dict(self) -> typing.Dict[int, str]:
        codes = {}
        for tup in self._griddiscreeteproperty_object_link.GetAllDictionaryCodes():
            k = tup.Item1
            v = tup.Item2
            codes[k] = v
        return codes

    def _make_chunk(self, i=None, j=None, k=None):
        value_getters = {ChunkType.ij:
                         lambda i, j, k: _utils.from_backing_arraytype(self._griddiscreeteproperty_object_link.GetColumn(i, j)),
                         ChunkType.k:
                         lambda i, j, k: _utils.from_backing_arraytype(self._griddiscreeteproperty_object_link.GetLayer(k)),
                         ChunkType.none:
                         lambda i, j, k: _utils.from_backing_arraytype(self._griddiscreeteproperty_object_link.GetAll()),
                         ChunkType.chunk:
                         lambda i, j, k: _utils.from_backing_arraytype(self._griddiscreeteproperty_object_link.GetChunk(i, j, k))}
        value_setters = {ChunkType.ij:
                         lambda i, j, k, values: self._griddiscreeteproperty_object_link.SetColumn(i, j, _utils.to_backing_arraytype(values)),
                         ChunkType.k:
                         lambda i, j, k, values: self._griddiscreeteproperty_object_link.SetLayer(k, _utils.to_backing_arraytype(values)),
                         ChunkType.none:
                         lambda i, j, k, values: self._griddiscreeteproperty_object_link.SetAll(_utils.to_backing_arraytype(values)),
                         ChunkType.chunk:
                         lambda i, j, k, values: self._griddiscreeteproperty_object_link.SetChunk(i, j, k, _utils.to_backing_arraytype(values))}
        value_shapers = {ChunkType.ij:
                         lambda i, j, k, values: _utils.ensure_1d_int_array(values, k),
                         ChunkType.k:
                         lambda i, j, k, values: _utils.ensure_2d_int_array(values, i, j),
                         ChunkType.none:
                         lambda i, j, k, values: _utils.ensure_3d_int_array(values, i, j, k),
                         ChunkType.chunk:
                         lambda i, j, k, values: _utils.ensure_3d_int_array(values, i, j, k)}
        value_accessors = {ChunkType.ij:
                           lambda i, j, k: k,
                           ChunkType.k:
                           lambda i, j, k:  _utils.native_accessor((i, j)),
                           ChunkType.none:
                           lambda i, j, k: _utils.native_accessor((i, j, k)),
                           ChunkType.chunk:
                           lambda i, j, k: _utils.native_accessor((i, j, k))}
        return Chunk(i, j, k,
                           self,
                           self.grid.extent,
                           value_getters,
                           value_setters,
                           value_shapers,
                           value_accessors,
                           (True, True, True),
                           readonly=self.readonly)

    def __str__(self) -> str:
        """A readable representation of the GridDiscreteProperty"""
        if self.date is None:
            return "GridDiscreteProperty(petrel_name=\"{0}\")".format(self.petrel_name)
        else:
            return "GridDiscreteProperty(petrel_name=\"{0}\", date=\"{1}\")".format(self.petrel_name, self.date)


class GridProperties(object):
    """An iterable collection of :class:`cegalprizm.pythontool.GridProperty` and :class:`cegalprizm.pythontool.GridDiscreteProperty`
    objects for the grid properties and discrete grid properties belonging to this property folder."""

    def __init__(self, property_folder: "PropertyFolder", recursive=False):
        self._property_folder = property_folder
        self._recursive = recursive
        self._properties = list(self._property_folder._get_grid_properties(recursive=self._recursive))

    def __iter__(self) -> typing.Iterator[typing.Union[GridProperty, GridDiscreteProperty]]:
        return iter(self._properties)
    
    def __getitem__(self, key) -> typing.Union[GridProperty, GridDiscreteProperty]:
        return _utils.get_item_from_collection_petrel_name(self._properties, key)

    def __len__(self) -> int:
        return self._property_folder._get_number_of_properties(recursive=self._recursive)

    def __str__(self) -> str:
        return 'GridProperties({0}="{1}")'.format(self._property_folder._object_link._sub_type, self._property_folder)

    def __repr__(self) -> str:
        return str(self)

    @property
    def readonly(self) -> bool:
        """
        .. warning::
            **Deprecated** - This property will be removed in Python Tool Pro 3.0.
        """
        warn("This property will be removed in Python Tool Pro 3.0.", DeprecationWarning, stacklevel=2)
        return self._property_folder.readonly