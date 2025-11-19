# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




import typing
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithDomain, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory
from cegalprizm.pythontool import gridproperty
from cegalprizm.pythontool import zone
from cegalprizm.pythontool import segment
from cegalprizm.pythontool import _docstring_utils, _utils
from cegalprizm.pythontool import primitives


if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.grid_grpc import GridGrpc

class Grid(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithDomain):
    def __init__(self, petrel_object_link: "GridGrpc"):
        super(Grid, self).__init__(petrel_object_link)

        self._grid_object_link = petrel_object_link
        self.__extent: typing.Optional[primitives.Extent] = None

    @property
    def extent(self) -> primitives.Extent:
        """The number of cells in the i, j and k directions

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Returns:
            cegalprizm.pythontool.Extent: The number of cells in each direction
        """
        if self.__extent is None:
            i = self._grid_object_link.NumI()
            j = self._grid_object_link.NumJ()
            k = self._grid_object_link.NumK()
            self.__extent = primitives.Extent(i=i, j=j, k=k)

        return self.__extent

    def __str__(self) -> str:
        """A readable representation of the Grid"""
        return "Grid(petrel_name=\"{0}\")".format(self.petrel_name)

    def indices(self, x: float, y: float, z: float) -> primitives.Indices:
        """The indices of a cell containing the specified point

        Note:
            Due to rounding errors and the way a pillar grid is defined, more than one cell might contain a given point; only one set of indices is ever returned.

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Args:
            x: the x-coordinate
            y: the y-coordinate
            z: the z-coordinate

        Returns:
            :class:`cegalprizm.pythontool.Indices`: object representing the indices of the cell containing the xyz coordinates

        Raises:
            ValueError: if no cell contains the specified point
        """       

        index3 = self._grid_object_link.GetCellAtPoint(x, y, z)
        if index3 is None:
            raise ValueError("position not in grid")
        return primitives.Indices(index3.GetValue().I, index3.GetValue().J, index3.GetValue().K)

    def position(self, i: int, j: int, k: int) -> primitives.Point:
        """The XYZ position of the cell center in the Petrel coordinate system 

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Args:
            i: the i-index
            j: the j-index
            k: the k-index

        Returns:
            :class:`cegalprizm.pythontool.Point`: The XYZ position of the cell center in the Petrel coordinate system 

        Raises:
            ValueError: if the indices are invalid for the grid
        """
        point3 = self._grid_object_link.GetCellCenter(i, j, k)
        if point3 is None:
            raise ValueError("Index not valid for grid")
        return primitives.Point(point3.GetValue().X, point3.GetValue().Y, point3.GetValue().Z)

    def vertices(self, i: int, j: int, k: int) -> typing.List[primitives.Point]:
        """
        The positions of the vertices of the cell.

        Use :func:`vertices_unchecked` if you do not wish to spend time checking if the cell is defined. In that case, the method will return an list of undefined points.

        See :class:`cegalprizm.pythontool.vertices` for how to query the returned list for specific vertices.

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Args:
            i: the i-index
            j: the j-index
            k: the k-index

        Returns:
            A list of :class:`cegalprizm.pythontool.Point` objects.
        
        Raises:
            ValueError: if the cell is undefined or outside of the grid
        """        

        points = self._grid_object_link.GetCellCorners(i, j, k)
        if points is None:
            raise ValueError("indices not in grid")
        if self.is_undef_cell(i, j, k):
            raise ValueError("cell is undefined")
        return [primitives.Point(pt.X, pt.Y, pt.Z) for pt in points.GetValue()]

    def vertices_unchecked(self, i: int, j: int, k: int) -> typing.List[primitives.Point]:
        """
        The positions of the vertices of the cell

        See :class:`cegalprizm.pythontool.vertices` for how to query the returned list for specific vertices.

        If the cell is not defined, a list of undefined points (where x, y and z are equal to NaN) will be returned. (Use :func:`vertices` to check for undefined cells).

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Args:
            i: the i-index
            j: the j-index
            k: the k-index

        Returns:
            A list of :class:`cegalprizm.pythontool.Point` objects.
        
        Raises:
            ValueError: if the cell outside of the grid
        """

        points = self._grid_object_link.GetCellCorners(i, j, k)
        if points is None:
            raise ValueError("indices not in grid")
        return [primitives.Point(pt.X, pt.Y, pt.Z) for pt in points.GetValue()]

    def is_undef_cell(self, i: int, j: int, k: int) -> bool:
        """
        Checks if the cell with given i,j and k index is undefined

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Args:
            i: the i-index
            j: the j-index
            k: the k-index

        Returns:
            bool: ``True`` if the cell is undefined at the indices specified
        """        

        return not self._grid_object_link.IsCellDefined(i, j, k)

    @property
    def coords_extent(self) -> primitives.CoordinatesExtent:
        """The extent of the object in world-coordinates

        Returns:

            cegalprizm.pythontool.CoordinatesExtent: the extent of the object in world-coordinate
        """
        return primitives.CoordinatesExtent(self._grid_object_link.AxesRange())

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="Grid")
    def crs_wkt(self):
        return "Well-known text representation of coordinate reference systems not available for Grid objects."
    
    def positions_to_ijks(self, positions: typing.Tuple[typing.List[float], typing.List[float], typing.List[float]])\
            -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        """
        Converts a tuple with xyz positions to ijk indices. The length of the output lists is determined by the length of the input [x] list. 
        The [y] and [z] lists must contain at least as many items as the [x] list. No output will be calculated for any extra items. Providing [y] and/or [z] lists with fewer items than the [x] list will raise an exception.

        Multiple positions may be located within the same cell, in which case the same ijk indices will be returned for those positions.
        
        Note:
            Positions outside of the spatial extent of the grid will be returned as -1 indices. This indicates that the position does not intersect the grid geometry.

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Args:
            positions: A tuple([x], [y], [z]), where [x] is a list of x positions, [y] is a list of y positions and [z] is a list of z (time/depth) positions.
            
        Returns:
            A tuple([i],[j],[k]) where [i] is a list of i indices, [j] is a list of j indices and [k] is a list of k indices.

        Raises:
            UnexpectedErrorException: If the [y] or [z] lists contain fewer items than the [x] list.

        Example:

        .. code-block:: python
        
            grid = petrel_connection.grids["Models/Path/To/Grid"]
            indices = grid.positions_to_ijks(([483200, 483300, 0], [6225050, 6225100, 0], [-7000, -7000, 0]))
            print(indices)
            >> ([10, 11, -1], [15, 16, -1], [650, 650, -1])

        """
        return _utils.positions_to_ijks_3d(object_link=self._grid_object_link, positions=positions)
    
    def ijks_to_positions(self, indices: typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]) -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        """
        Converts a tuple with ijk indices to xyz.
        The length of the output lists is determined by the length of the input [i] list. It is possible to provide a [j] or [k] list with more items than the [i] list, but no output is calculated for the extra items. Providing a [j] and/or [k] list with fewer items than the [i] list will raise an exception.

        Note:
            The returned positions are the center of the cell defined by the ijk indices. This means a conversion from positions to ijks and back to positions may not always return the exact original positions.

        Note:
            Python Tool Pro I, J, K indices are 0-based, while in Petrel they are 1-based. For example, a cell identified as (i = 4, j = 5, k = 6) in Python corresponds to (i = 5, j = 6, k = 7) in Petrel.

        Args:
            indices: A tuple([i],[j],[k]) where [i] is a list of i indices, [j] is a list of j indices and [k] is a list of k indices.

        Returns:
            tuple: A tuple([x], [y], [z]), where [x] is a list of x coordinates, [y] is a list of y positions and [z] is a list of z (time/depth) coordinates.

        Raises:
            PythonToolException: If any of the i, j or k indices are negative or greater than the object extent.
            UnexpectedErrorException: If the [j] or [k] lists contain fewer items than the [i] list.
        """
        return _utils.ijks_to_positions(extent = self.extent,
                                        object_link = self._grid_object_link,
                                        indices = indices,
                                        dimensions = 3)

    @property
    def properties(self) -> "gridproperty.GridProperties":
        """A readonly iterable collection of the grid properties for the grid
        
        Returns: 
            a list of the grid properties (continuous and discrete)
        """
        return gridproperty.GridProperties(self.property_folder, recursive=True)

    @property
    def property_folder(self) -> "gridproperty.PropertyFolder":
        """The root property folder `Properties` for the grid

        **Example**:

        Retrieve the property folder for a Grid object:

        .. code-block:: Python
        
            grid = petrel_connection.grids["Input/Path/To/Grid"]
            grid_property_folder = grid.property_folder

        Returns:
            cegalprizm.pythontool.PropertyFolder: the root property folder for the grid"""
        collection = self._grid_object_link.GetPropertyCollection()
        return gridproperty.PropertyFolder(collection)

    @property
    def zones(self) -> "zone.Zones":
        """A readonly iterable collection of the zones for the grid
        
        Returns:
            cegalprizm.pythontool.Zones: the zones for the grid"""
        return zone.Zones(self)

    def _get_zones(self):
        for zone_obj in self._grid_object_link.GetZones():
            zone_py = zone.Zone(zone_obj)
            yield zone_py

    def _get_number_of_zones(self) -> int:
        return self._grid_object_link.GetNumberOfZones()


    @property
    def segments(self) -> "segment.Segments":
        """A readonly iterable collection of the segments for the grid
        
        Returns:
            cegalprizm.pythontool.Segments: the segments for the grid"""
        return segment.Segments(self)

    def _get_segments(self):
        for segment_obj in self._grid_object_link.GetSegments():
            segment_py = segment.Segment(segment_obj)
            yield segment_py

    def _get_number_of_segments(self) -> int:
        return self._grid_object_link.GetNumberOfSegments()