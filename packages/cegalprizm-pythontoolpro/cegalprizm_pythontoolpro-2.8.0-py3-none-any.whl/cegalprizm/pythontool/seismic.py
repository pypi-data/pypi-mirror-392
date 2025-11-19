# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import typing
import os
from cegalprizm.pythontool import primitives
from cegalprizm.pythontool.chunk import Chunk
from cegalprizm.pythontool.chunktype import ChunkType
from cegalprizm.pythontool import _docstring_utils, _utils
from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithDomain, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion
from cegalprizm.pythontool import exceptions
from cegalprizm.pythontool.template import Template, DiscreteTemplate

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.seismic_grpc import Seismic2DGrpc, SeismicCubeGrpc

class SeismicCube(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithDomain, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    """A class holding information about a seismic cube

    Seismic files of format SEG-Y are always read-only.
    """    
    def __init__(self, petrel_object_link: "SeismicCubeGrpc"):
        super(SeismicCube, self).__init__(petrel_object_link)
        self._seismiccube_object_link = petrel_object_link
        self.__extent: typing.Optional[primitives.Extent] = None

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="SeismicCube")
    def crs_wkt(self):
        return self._seismiccube_object_link.GetCrs()

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
            self._seismiccube_object_link.GetAffineTransform()
        )

    def reconnect(self, path: str) -> None:
        """Reconnects the 3D seismic object to the given file path. 

        Note:
            The file path has to be written with 2 backslashes.
            This method only works on external seismic objects with broken links.

        Args:
            path (str): The seismic file path to reconnect the seismic object.
        """        
        self._seismiccube_object_link.Reconnect(path)

    def seismic_file_path(self) -> str:
        """Returns the seismic file path of the seismic object. 
        Returns 'Not available' for virtual seismic.
        """        
        return self._seismiccube_object_link.BulkFile()
    
    @property
    def is_virtual(self) -> bool:
        """Returns True if the seismic object is virtual, False otherwise.
        """
        path = self.seismic_file_path()
        return path == 'Not available'

    def set_value(self, value: float):
        """Sets the values of the entire seismic cube to the value provided. This is useful to set all values to zero. But any value can be provided.

        Args:
            value: The value to set the seismic cube.

        Raises:
            exceptions.PythonToolException: If seismic cube is readonly.
            exceptions.PythonToolException: If set_value fails
        """        
        if self.readonly:
            raise exceptions.PythonToolException("Seismic volume is readonly")
        ok = self._seismiccube_object_link.SetConstantValue(float(value))
        if not ok:
            raise exceptions.PythonToolException("Could not set value of seismic volume")

    @property
    def extent(self) -> primitives.Extent:
        """The extent of the cube in the i, j and k directions

        Seismic traces are indexed by `i` and `j`, with `k` specifying the sample number in a trace.

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Returns:
            cegalprizm.pythontool.Extent: The number of traces in each direction and number of samples per trace
        """
        if self.__extent is None:
            i = self._seismiccube_object_link.NumI()
            j = self._seismiccube_object_link.NumJ()
            k = self._seismiccube_object_link.NumK()
            self.__extent = primitives.Extent(i=i, j=j, k=k)

        return self.__extent

    @property
    def unit_symbol(self) -> typing.Optional[str]:
        """Returns the symbol of the object unit, None if template of object is unitless."""
        return _utils.str_or_none(self._seismiccube_object_link.GetDisplayUnitSymbol())

    @_docstring_utils.clone_docstring_decorator(return_type="SeismicCube", respects_subfolders=True, continuous_template=True, realize_path=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, template: "Template" = None, realize_path: str = "") -> "SeismicCube":
        _utils.verify_continuous_clone(copy_values, template)

        if not isinstance(realize_path, str):
            raise TypeError("realize_path must be a string")
        if len(realize_path) > 0:
            (folder, filename) = os.path.split(realize_path)
            if not os.path.exists(folder):
                raise ValueError(f"The folder {folder} does not exist")
            if realize_path.endswith("\\"):
                realize_path = realize_path + name_of_clone
            if not realize_path.endswith(".zgy"):
                realize_path = realize_path + ".zgy"
        
        return typing.cast("SeismicCube", self._clone(name_of_clone, copy_values = copy_values, template = template, realize_path = realize_path))

    def __make_chunk(self, i=None, j=None, k=None) -> Chunk:
        value_getters = {ChunkType.ij:
                         lambda i, j, k: _utils.from_backing_arraytype(self._seismiccube_object_link.GetColumn(i, j)),
                         ChunkType.k:
                         lambda i, j, k: _utils.from_backing_arraytype(self._seismiccube_object_link.GetLayer(k)),
                         ChunkType.chunk:
                         lambda i, j, k: _utils.from_backing_arraytype(self._seismiccube_object_link.GetChunk(i, j, k))}
        value_setters = {ChunkType.ij:
                         lambda i, j, k, values: self._seismiccube_object_link.SetColumn(i, j, _utils.to_backing_arraytype(values)),
                         ChunkType.k:
                         lambda i, j, k, values: self._seismiccube_object_link.SetLayer(k, _utils.to_backing_arraytype(values)),
                         ChunkType.chunk:
                         lambda i, j, k, values: self._seismiccube_object_link.SetChunk(i, j, k, _utils.to_backing_arraytype(values))}
        value_shapers = {ChunkType.ij:
                         lambda i, j, k, values: _utils.ensure_1d_float_array(values, k),
                         ChunkType.k:
                         lambda i, j, k, values: _utils.ensure_2d_float_array(values, i, j),
                         ChunkType.chunk:
                         lambda i, j, k, values: _utils.ensure_3d_float_array(values, i, j, k)}
        value_accessors = {ChunkType.ij:
                           lambda i, j, k: k,
                           ChunkType.k:
                           lambda i, j, k: _utils.native_accessor((i, j)),
                           ChunkType.chunk:
                           lambda i, j, k: _utils.native_accessor((i, j, k))}

        return Chunk(i, j, k,
                           self,
                           self.extent,
                           value_getters,
                           value_setters,
                           value_shapers,
                           value_accessors,
                           (True, True, True),
                           readonly=self.readonly)

    def layer(self, k: int) -> Chunk:
        """Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the specified sample index

        Args:
            k: the sample index

        Returns:
            A `Slice` containing the values for all the traces for a particular sample index

        Raises:
            ValueError: if the cube does not have the seismic sample specified
        """
        return self.__make_chunk(k=k)

    def column(self, i: int, j: int) -> Chunk:
        """Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the specified traces

        Args:
            i: the index in the i-direction
            j: the index in the j-direction

        Returns:
            A `Slice` containing the values for all specified traces 

        Raises:
            ValueError: if the cube does not have the traces specified
        """
        return self.__make_chunk(i, j)

    def chunk(self, 
            irange: typing.Optional[typing.Tuple[int, int]], 
            jrange: typing.Optional[typing.Tuple[int, int]],    
            krange: typing.Optional[typing.Tuple[int, int]]) \
            -> Chunk:
        """
        Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the specified index ranges

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Args:
            irange: Inclusive range of i-values, or () or None for all
            jrange: Inclusive range of j-values, or () or None for all
            krange: Inclusive range of k-values, or () or None for all

        Returns:
            A `Chunk` containing the values contained in the ranges specified
        """
        return self.__make_chunk(i=irange, j=jrange, k=krange)
        

    def all(self) -> Chunk:
        """Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the entire cube

        Note:
            This can be an expensive operation in time and memory depending on the size of cube.

        Returns:
            A `Chunk` containing the values contained in the entire cube
        """
        return self.chunk(None, None, None)

    def columns(self, irange: typing.Tuple[int, int] = None, jrange: typing.Tuple[int, int] = None) -> typing.Iterator[Chunk]:
        """The columns in given i- and j-range
        
        Args:
            irange: an iterable (e.g list) of i-values to
                generate columns for.  If `None`,
                generate for all i-values
            jrange: an iterable (e.g. list) of j-values to
                generate columns for.  If `None`,
                generate for all j-values.
        
        Yields:
            A generator of column :class:`cegalprizm.pythontool.Chunk` objects covering the
                `irange` and `jrange` passed.

        Raises:
            ValueError: if the indices are invalid.

        **Example**:

        .. code-block:: python

          # sets to 0 all values in the i-slices i=10 through to i=19,
          for col in my_prop.columns(range(10, 20), jrange=None):
              col.set(0)

          # sets to 0 all values in the property
          for col in my_prop.columns():
              col.set(0)

        """
        irange_used = irange if irange is not None else range(self.extent.i)
        jrange_used = jrange if jrange is not None else range(self.extent.j)
        for i in irange_used:
            for j in jrange_used:
                yield self.column(i, j)

    def __str__(self) -> str:
        """A readable representation of the Seismic 3d object"""
        return "SeismicCube(petrel_name=\"{0}\")".format(self.petrel_name)

    def indices(self, x: float, y: float, z: float) -> primitives.Indices:
        """
        Returns the I, J, K indices of the seismic bin (cell) nearest to the specified spatial coordinates.

        Finds the indices within the 3D seismic cube that correspond to the bin (cell) center closest to the given X, Y, Z coordinates.

        If you are working primarily with annotations (crossline/inline), use the :func:`annotation_indices` and :func:`annotation` methods to convert annotations to and from `Indices`.

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Args:
            x (float): X coordinate in project CRS.
            y (float): Y coordinate in project CRS.
            z (float): Z coordinate in the seismic domain (time or depth).

        Returns:
            A :class:`cegalprizm.pythontool.Indices` object representing the (i,j,k) indices of the nearest seismic bin (cell).

        Raises:
            ValueError: If the specified coordinates are outside the spatial extent of the seismic cube.

        **Example**:

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            seismic_cube = petrel.seismic_cubes.get_by_name("SeismicCube")
            seismic_cube.indices(x=453612.28, y=6479213.44, z=-1820.0)
            >> Indices(i=11, j=12, k=25)

        """ 
        idx3 = self._seismiccube_object_link.IndexAtPosition(x, y, z)
        if idx3 is None:
            raise ValueError("position is outside seismic object")
        return primitives.Indices(idx3.GetValue().I, idx3.GetValue().J, idx3.GetValue().K)

    def position(self, i: int, j: int, k: int) -> primitives.Point:
        """
        Returns the spatial position (X, Y, Z) of the bin (cell) center at the specified I, J, K indices.
        The Z coordinate represents the midpoint of the seismic sample at index k.

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.


        Args:
            i (int): Inline index of the bin (cell).
            j (int): Crossline index of the bin (cell).
            k (int): Sample index along the vertical (time/depth) axis.

        Returns:
            A :class:`cegalprizm.pythontool.Point` object representing the (X, Y, Z) coordinate of the bin (cell) center in world coordinates.

        Raises:
            ValueError: If the indices are outside the seismic cube extent.

        **Example**:

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            seismic_cube = petrel.seismic_cubes.get_by_name("SeismicCube")
            seismic_cube.position(i=11, j=12, k=25)
            >> Point(x=453612.280000, y=6479213.440000, z=-1820.000000)
        """ 
        point3 = self._seismiccube_object_link.PositionAtIndex(i, j, k)
        if point3 is None:
            raise ValueError("Index not valid for seismic")
        return primitives.Point(point3.GetValue().X, point3.GetValue().Y, point3.GetValue().Z)

    def annotation(self, i: int, j: int, k: int=0) -> primitives.Annotation:
        """The annotations for seismic indices

        Args:
            i: the i-index
            j: the j-index
            k: the k-index (defaults to 0)

        Returns:
            cegalprizm.pythontool.Annotation: an Annotation object with the inline, xline and sample of the given index

        Raises:
            ValueError: if the i, j or k index are beyond the valid range
        """
        idx3 = self._seismiccube_object_link.IndexToAnnotation(i, j, k)
        if idx3 is None:
            raise ValueError("indices not in seismic")
        return primitives.Annotation(idx3.GetValue().I, idx3.GetValue().J, idx3.GetValue().K)

    def annotation_indices(self, inline: int, crossline: int, samplenumber: int = 1) -> primitives.Indices:
        """The i,j and k index of a particular inline/crossline/samplenumber

        Args:
            inline: the inline annotation
            crossline: the crossline annotation
            samplenumber: the sample number (defaults to 1)

        Returns: an 'Indices' object with the i, j and k index
        of the given inline, crossline and samplenumber
        """
        idx3 = self._seismiccube_object_link.AnnotationToIndex(inline, crossline, samplenumber)
        if idx3 is None:
            raise ValueError("annotations are invalid")
        return primitives.Indices(idx3.GetValue().I, idx3.GetValue().J, idx3.GetValue().K)


    @property
    def coords_extent(self) -> primitives.CoordinatesExtent:
        """
        The spatial extent of the seismic cube in world coordinates.

        Returns the minimum and maximum X, Y, and Z coordinates defining the full spatial extent of the seismic cube in project coordinates.

        Returns:
            A :class:`cegalprizm.pythontool.CoordinatesExtent` object representing the extent of the seismic cube in world coordinates.

        **Example**:

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            seismic_cube = petrel.seismic_cubes.get_by_name("SeismicCube")
            seismic_cube.coords_extent
            >> CoordinatesExtent(
                x_axis=AxisExtent(min=451257.380000, max=458757.080000),
                y_axis=AxisExtent(min=6784375.050000, max=6784479.840000),
                z_axis=AxisExtent(min=-2304.680000, max=-1396.000000)
               )
        """
        return primitives.CoordinatesExtent(self._seismiccube_object_link.AxesRange())


    def has_same_parent(self, other: "SeismicCube") -> bool:
        """Tests whether the seismic cube has the same parent collection

        Args:
            other: the other seismic cube

        Returns:
            bool: ``True`` if the ``other`` object has the same parent collection

        Raises:
            ValueError: if ``other`` is not a SeismicCube
        """
        if not isinstance(other, SeismicCube):
            raise ValueError("can only compare parent with other SeismicCube")
        return self._seismiccube_object_link.GetParentCollectionDroidString() == \
            other._seismiccube_object_link.GetParentCollectionDroidString()
    
    def positions_to_ijks(self, positions: typing.Tuple[typing.List[float], typing.List[float], typing.List[float]])\
            -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        """Converts a tuple with xyz positions to ijk indices. 
        
        The length of the output lists is determined by the length of the input [x] list.
        The [y] and [z] lists must contain at least as many items as the [x] list. No output will be calculated for any extra items. Providing [y] and/or [z] lists with fewer items than the [x] list will raise an exception.

        Multiple positions may be located within the same bin (cell), in which case the same ijk indices will be returned for those positions.
        The returned indices represent the bin (cell) center closest to the provided xyz coordinates.

        Note:
            When coordinates fall outside the spatial extent of the SeismicCube, the returned I, J, K values represent the extrapolated grid positions based on the cube's underlying grid geometry. Both negative indices and positive indices greater than the object extent may be returned.

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Args:
            positions: A tuple([x], [y], [z]), where [x] is a list of x positions, [y] is a list of y positions and [z] is a list of z (time/depth) positions.
            
        Returns:
            A tuple([i],[j],[k]) where [i] is a list of i indices, [j] is a list of j indices and [k] is a list of k indices.

        Raises:
            UnexpectedErrorException: If the [y] or [z] lists contain fewer items than the [x] list.

        Example:

        .. code-block:: python
        
            cube = petrel_connection.seismic_cubes["Input/Path/To/Cube"]
            indices = cube.positions_to_ijks(([486450, 486460, 489000, 0], [6223400, 6227800, 7654321, 1], [-3400, -3400, -10000, 0]))
            print(indices)
            >> ([11, 180, 55001, -205836], [12, 320, 100394, -454901], [250, 250, 1900, -600])

        """
        return _utils.positions_to_ijks_3d(object_link=self._seismiccube_object_link, positions=positions)

    def ijks_to_positions(self, indices: typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]) -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        """
        Converts a tuple with ijk indices to xyz.

        The length of the output lists is determined by the length of the input [i] list. It is possible to provide a [j] or [k] list with more items than the [i] list, but no output is calculated for the extra items. Providing a [j] and/or [k] list with fewer items than the [i] list will raise an exception.

        Note:
            The returned positions represent the center of the bin (cell) defined by the ijk indices. This means a conversion from positions to ijks and back to positions may not always return the exact original positions.

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Args:
            indices: A tuple([i],[j],[k]) where [i] is a list of i indices, [j] is a list of j indices and [k] is a list of k indices.

        Returns:
            tuple: A tuple([x], [y], [z]), where [x] is a list of x coordinates, [y] is a list of y coordinates and [z] is a list of z (time/depth) coordinates.

        Raises:
            PythonToolException: If any of the i, j or k indices are negative or greater than the object extent.
            UnexpectedErrorException: If the [j] or [k] lists contain fewer items than the [i] list.
        """
        return _utils.ijks_to_positions(extent = self.extent, 
                                        object_link = self._seismiccube_object_link, 
                                        indices = indices, 
                                        dimensions = 3)

    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

class SeismicLine(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithDomain, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):

    def __init__(self, petrel_object_link: "Seismic2DGrpc"):
        super(SeismicLine, self).__init__(petrel_object_link)
        self.__extent: typing.Optional[primitives.Extent] = None
        self._seismicline_object_link = petrel_object_link

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="SeismicLine")
    def crs_wkt(self):
        return self._seismicline_object_link.GetCrs()

    @property
    def unit_symbol(self) -> typing.Optional[str]:
        """The symbol for the unit which the values are measured in

        Returns:

            string: The symbol for the unit, or None if no unit is used
        """
        return _utils.str_or_none(self._seismicline_object_link.GetDisplayUnitSymbol())

    @property
    def extent(self) -> primitives.Extent:
        """The extent of the seismic line

        Seismic Lines are indexed by `j` and `k`. `i` will always be `None`.

        Note:
            Python Tool Pro J, K indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (j = 5, k = 6) in Python corresponds to (j = 6, k = 7) in Petrel.
        """

        if self.__extent is None:
            j = self._seismicline_object_link.NumJ()
            k = self._seismicline_object_link.NumK()
            self.__extent = primitives.Extent(i=1, j=j, k=k)

        return self.__extent

    def column(self, j: int) -> Chunk:
        """Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the specified column

        Args:
            j: the index in the j-direction

        Returns:
            A `Slice` containing the values for all layers

        Raises:
            ValueError: if the line does not have the column specified
        """
        value_getters = {ChunkType.ij:
                         lambda i, j, k: _utils.from_backing_arraytype(self._seismicline_object_link.GetColumn(j))}
        value_setters = {ChunkType.ij:
                         lambda i, j, k, values: self._seismicline_object_link.SetColumn(j, _utils.to_backing_arraytype(values))}
        value_shapers = {ChunkType.ij:
                         lambda i, j, k, values: _utils.ensure_1d_float_array(values, k)}
        value_accessors = {ChunkType.ij:
                          lambda i, j, k: k}

        return Chunk(None, j, None,
                           self,
                           self.extent,
                           value_getters,
                           value_setters,
                           value_shapers,
                           value_accessors,
                           (False, True, True),
                           chunk_type=ChunkType.ij,
                           readonly=self.readonly)

    def chunk(self, jrange: typing.Iterable[int] = None, krange: typing.Iterable[int] = None) -> Chunk:
        """
        Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the specified column and layer range

        Note:
            Python Tool Pro J, K indices are 0-based, while in Petrel they are 1-based. For example, a sample identified as (j = 5, k = 6) in Python corresponds to (j = 6, k = 7) in Petrel.

        Args:
            jrange: Inclusive range of j-values, or () or None for all
            krange: Inclusive range of k-values, or () or None for all

        Returns:
            A `Chunk` containing the values contained in the ranges specified
        """
        value_getters = {ChunkType.chunk:
                         lambda i, j, k: _utils.from_backing_arraytype(self._seismicline_object_link.GetMultipleColumns(jrange, krange))}
        value_setters = {ChunkType.chunk:
                         lambda i, j, k, values: self._seismicline_object_link.SetMultipleColumns(jrange, krange, _utils.to_backing_arraytype(values))}
        value_shapers = {ChunkType.chunk:
                         lambda i, j, k, values: _utils.ensure_3d_float_array(values, i, j, k)}
        value_accessors = {ChunkType.chunk:
                          lambda i, j, k: _utils.native_accessor((j, k))} 
        return Chunk(None, jrange, krange,
                            self,
                            self.extent,
                            value_getters,
                            value_setters,
                            value_shapers,
                            value_accessors,
                            (False, True, True),
                            chunk_type=ChunkType.chunk,
                            readonly=self.readonly)

    def all(self) -> Chunk:
        """Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the entire seismic line

        Returns:
            A `Chunk` containing the values contained in the entire seismic line
        """
        return self.chunk(None, None)

    def columns(self, jrange: typing.Iterable[int] = None) -> typing.Iterable[Chunk]:
        """The columns in given j-range
        
        Args:
            jrange: an iterable (e.g. list) of j-values to
                generate columns for.  If `None`,
                generate for all j-values.
        
        Yields:
            A generator of column :class:`cegalprizm.pythontool.Chunk` objects covering the
                `jrange` passed.

        Raises:
            ValueError: if the indices are invalid.


        **Example**:

        .. code-block:: python

          # sets to 0 all values in the i-slices i=10 through to i=19,
          for col in my_prop.columns(range(10, 20)):
              col.set(0)

          # sets to 0 all values in the property
          for col in my_prop.columns():
              col.set(0)

        """
        jrange_used = jrange if jrange is not None else range(self.extent.j)
        for j in jrange_used:
            yield self.column(j)

    def indices(self, x: float, y: float, z: float) -> primitives.Indices:
        """The indices (I, J, K) of the seismic sample nearest to the specified spatial coordinates.

        Returns the indices of the trace and sample in the 2D seismic line that are closest to the given X, Y, Z coordinates. The result corresponds to the nearest trace-sample midpoint along the seismic line.

        Note:
            Python Tool Pro J, K indices are 0-based, while in Petrel they are 1-based. For example, a sample identified as (j = 5, k = 6) in Python corresponds to (j = 6, k = 7) in Petrel.

        Args:
            x (float): The X coordinate in project CRS.
            y (float): The Y coordinate in project CRS.
            z (float): The Z coordinate in seismic sample domain (time or depth).

        Returns:
            A :class:`cegalprizm.pythontool.Indices` object representing the indices of the nearest seismic sample. The `i` value will always be `None` for 2D seismic lines.

        Raises:
            ValueError: If the Z coordinate lies outside the vertical range of the seismic line.

        Note:
            X and Y coordinates may lie outside the seismic line geometry; the nearest trace is used.
            The Z coordinate must be within the seismic line's time/depth range.
            The returned indices correspond to the sample midpoint nearest to the given point.

        **Example**:

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            seismic_line = petrel.seismic_lines.get_by_name("SeismicLine")
            seismic_line.indices(x=453612.28, y=6479213.44, z=-1820.0)
            >> Indices(i=None, j=0, k=0)
        """
        idx2 = self._seismicline_object_link.IndexAtPosition(x, y, z)
        if idx2 is None:
            raise ValueError("position is outside seismic object")
        return primitives.Indices(None, idx2.GetValue().I, idx2.GetValue().J)

    def position(self, j: int, k: int) -> primitives.Point:
        """The spatial position (X, Y, Z) of a seismic sample in the 2D seismic line.

        Returns the coordinate of the midpoint of the seismic trace sample specified by its indices along the seismic line (trace index j, sample index k).

        Note:
            Python Tool Pro J, K indices are 0-based, while in Petrel they are 1-based. For example, a sample identified as (j = 5, k = 6) in Python corresponds to (j = 6, k = 7) in Petrel.

        Args:
            j (int): The trace index along the seismic line.
            k (int): The sample index along the trace (vertical time/depth direction).

        Returns: 
            A :class:`cegalprizm.pythontool.Point` object representing the position (X, Y, Z) of the seismic sample midpoint.

        Raises:
            If the indices are outside the valid seismic line range.

        Note:
            Each trace corresponds to a single X, Y location; each sample corresponds to a Z position.

            The returned coordinate represents the center point of that sample.

        **Example**:

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            seismic_line = petrel.seismic_lines.get_by_name("SeismicLine")
            seismic_line.position(j=0, k=0)
            >> Point(x=453612.28, y=6479213.44, z=-1820.0)
        """
        point3 = self._seismicline_object_link.PositionAtIndex(j, k)
        if point3 is None:
            raise ValueError("Index not valid for seismic")
        return primitives.Point(point3.GetValue().X, point3.GetValue().Y, point3.GetValue().Z)

    @_docstring_utils.clone_docstring_decorator(return_type="SeismicLine", respects_subfolders=True, continuous_template=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, template: "Template" = None) -> "SeismicLine":
        _utils.verify_continuous_clone(copy_values, template)
        return typing.cast("SeismicLine", self._clone(name_of_clone, copy_values = copy_values, template = template))

    @property
    def coords_extent(self) -> primitives.CoordinatesExtent:
        """The spatial extent of the 2D seismic line in world coordinates.

        Returns the minimum and maximum X, Y, and Z values defining the bounding box of the seismic line in project coordinates. 

        Returns:
            A :class:`cegalprizm.pythontool.CoordinatesExtent` object representing the extent of the SeismicLine in world coordinates.

        **Example**:

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            seismic_line= petrel.seismic_lines.get_by_name("SeismicLine")
            seismic_line.coords_extent
            >> CoordinatesExtent(
                x_axis=AxisExtent(min=451257.380000, max=458757.080000),
                y_axis=AxisExtent(min=6784375.050000, max=6784479.840000),
                z_axis=AxisExtent(min=-2304.680000, max=-1396.000000)
               )
        """
        return primitives.CoordinatesExtent(self._seismicline_object_link.AxesRange())

    def has_same_parent(self, other: "SeismicLine") -> bool:
        """Tests whether the seismic line has the same parent collection

        Args:
            other: the other seismic line

        Returns:
            bool: ``True`` if the ``other`` object has the same parent collection

        Raises:
            ValueError: if ``other`` is not a SeismicLine
        """
        if not isinstance(other, SeismicLine):
            raise ValueError("can only compare parent with other SeismicLine")
        return self._seismicline_object_link.GetParentCollectionDroidString() == \
            other._seismicline_object_link.GetParentCollectionDroidString()

    def __str__(self) -> str:
        """A readable representation of the SeismicLine object"""
        return "SeismicLine(petrel_name=\"{0}\")".format(self.petrel_name)

    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()