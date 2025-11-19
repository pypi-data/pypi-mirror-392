# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




import typing
from enum import Enum
from cegalprizm.pythontool.polylineattribute import PolylineAttribute
import pandas as pd
from pandas.api.types import is_bool_dtype
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_integer_dtype

from warnings import warn
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithDomain, PetrelObjectWithHistory
from cegalprizm.pythontool.petrelobject import PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion
from cegalprizm.pythontool.template import Template, DiscreteTemplate
from cegalprizm.pythontool import primitives, exceptions, _docstring_utils, _utils
from cegalprizm.pythontool.grpc import utils
from cegalprizm.pythontool.grpc.polylineattribute_grpc import PolylineAttributeGrpc

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.polylines_grpc import PolylineSetGrpc
    from cegalprizm.pythontool import Folder, InterpretationFolder

class PolylineTypeEnum(Enum):
    """An enumeration of the different types of PolylineSets in Petrel"""
    FaultSticks = "Fault sticks"
    FaultLines = "Fault lines"
    FaultCenterline = "Fault centerline"
    FaultPolygons = "Fault polygons"
    HorizonContours = "Horizon contours"
    HorizonErosionLine = "Horizon erosion line"
    GenericBoundaryPolygon = "Generic boundary polygon"
    GenericSeismic2DLines = "Generic seismic 2D lines"
    GenericSeismic3DLines = "Generic seismic 3D lines"
    GenericZeroLines = "Generic zero lines"
    TrendLines = "Trend lines"
    FlowLines = "Flow lines"
    GenericSingleLine = "Generic single line"
    ManyPoints = "Many points"
    FewPoints = "Few points"
    MultiZHorizon = "Multi-Z horizon"
    Other = "Other"

class PolylinePoint(object):
    def __init__(self, polyline: "Polyline", index: int):
        self._polyline = polyline
        self._index = index

    def __eq__(self, other) -> bool:
        try:
            return other.x == self.x and other.y == self.y and other.z == self.z # type: ignore
        except Exception:
            return False

    def __str__(self) -> str:
        return "PolylinePoint(parent_polyline={0})".format(self._polyline)

    def __repr__(self) -> str:
        return str(self)

    @property
    def x(self) -> float:
        """Returns the x coordinate of the point as a float.
        """
        return self._polyline.positions()[0][self._index]

    @property
    def y(self) -> float:
        """Returns the y coordinate of the point as a float.
        """
        return self._polyline.positions()[1][self._index]

    @property
    def z(self) -> float:
        """Returns the z coordinate of the point as a float.
        """
        return self._polyline.positions()[2][self._index]

class Polyline(object):
    """Represents a single polyline in a
    :class:`cegalprizm.pythontool.PolylineSet` object.

    It is an iterable, returning :class:`cegalprizm.pythontool.PolylinePoint` objects.
    """

    def __init__(self, polyline_set: "PolylineSet", polyline_index: int):
        self._polyline_set = polyline_set
        self._polyline_index = polyline_index

        self._position_array: typing.Optional[typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]] = None
        self._point_count: typing.Optional[int] = None
        self._points_cache: typing.Optional[typing.List[typing.Union[primitives.Point, PolylinePoint]]] = None

    def _load_points_cache(self) -> typing.List[typing.Union[PolylinePoint, primitives.Point]]:
        self._position_array = self._polyline_set.get_positions(self._polyline_index)
        self._point_count = len(self._position_array[0])
        self._points_cache = [PolylinePoint(self, i) for i in range(self._point_count)]
        return self._points_cache

    def _set_points(self, xs, ys, zs):
        self._polyline_set.set_positions(self._polyline_index, xs, ys, zs)

    def __repr__(self) -> str:
        return str(self)

    @property
    def closed(self) -> bool:
        """A property to check if the polyline closed or open?

        Returns:
            `True` if the polyline is closed, `False` if open"""
        return self._polyline_set.is_closed(self._polyline_index)

    @property
    def parent_polylineset(self) -> None:
        """DeprecationWarning: 'parent_polylineset' has been removed. Use 'polylineset' instead
        """
        warn("'parent_polylineset' has been removed. Use 'polylineset' instead", 
             DeprecationWarning, stacklevel=2)
        raise RuntimeError("'parent_polylineset' has been removed. Use 'polylineset' instead")

    @property
    def polylineset(self) -> "PolylineSet":
        """Returns the parent 'PolylineSet' of the 'Polyline'"""
        return self._polyline_set

    @property
    def readonly(self) -> bool:
        """The readonly status of the parent `PolylineSet`

        Returns:
            bool: True if the parent `PolylineSet` is readonly"""
        return self._polyline_set.readonly

    def __str__(self) -> str:
        return "Polyline(parent_polylineset={0})".format(self.polylineset)

    def positions(self) -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        """Returns a tuple([x], [y], [z]), where x is a list of x positions, y is a list of y positions and z is a list of z positions"""        
        if self._position_array is None:
            self._load_points_cache()
        return typing.cast(typing.Tuple[typing.List[float], typing.List[float], typing.List[float]], self._position_array)

    @property
    def points(self) -> typing.List[typing.Union[PolylinePoint, primitives.Point]]:
        """A list of the :class:`cegalprizm.pythontool.PolylinePoint` objects making up the polyline"""
        if self._points_cache is None:
            self._load_points_cache()
        return typing.cast(typing.List[typing.Union[PolylinePoint, primitives.Point]], self._points_cache)

    @points.setter
    def points(self, lst: typing.List[typing.Union[PolylinePoint, primitives.Point]]) -> None:
        if self.readonly:
            raise exceptions.PythonToolException("Parent PolylineSet is readonly")

        try:
            arrayx = [float(0)] * len(lst)
            arrayy = [float(0)] * len(lst)
            arrayz = [float(0)] * len(lst)
                
            for i, p in enumerate(lst):
                arrayx[i] = p.x
                arrayy[i] = p.y
                arrayz[i] = p.z
            self._set_points(arrayx, arrayy, arrayz)
            self._load_points_cache()
        except TypeError:
            raise TypeError("You must pass an iterable (list) of PolylinePoints")

    def add_point(self, point: primitives.Point) -> None:
        """Adds a point

        Adds a single point in displayed world co-ordinates to the polyline.  
        Using this method multiple times will
        be slower than building up a list of
        :class:`primitives.Point` objects and assigning it to
        the :func:`points` property in one go.

        **Example**:

        .. code-block:: python

          # slower
          mypolyline.add_point(primitives.Point(100.0, 123.0, 50.3))
          mypolyline.add_point(primitives.Point(102.0, 125.3, 50.2))

          # faster
          new_polylinepoints = [primitives.Point(100.0, 123.0, 50.3), primitives.Point(102.0, 125.3, 50.2)]
          mypolyline.points = new_polylinepoints

        Args:
            point (primitives.Point): the point to add

        Raises:
            PythonToolException: If the parent PolylineSet is readonly
            TypeError: If points is not a list of :class:`cegalprizm.pythontool.PolylinePoint` or :class:`cegalprizm.pythontool.Point` objects

        """
        if self.readonly:
            raise exceptions.PythonToolException("Parent PolylineSet is readonly")
        if not hasattr(point, "x") or not hasattr(point, "y") or not hasattr(point, "z"):
                raise TypeError("point must be of type Point")
        if self._points_cache is None:
            self._load_points_cache()
        self._points_cache = typing.cast(typing.List[typing.Union[PolylinePoint, primitives.Point]], self._points_cache)
        self._points_cache.append(point)
        self.points = self._points_cache
        self._load_points_cache()

    def delete_point(self, point: PolylinePoint) -> None:
        """Deletes a point

        Deletes one point from the polyline. Using this
        method multiple times will be slower than manipulating a list
        of :class:`cegalprizm.pythontool.PolylinePoint` objects and assigning it
        to the :func:`points` property in one go.

        Note that :class:`cegalprizm.pythontool.PolylinePoint` objects are compared by
        reference, not value.   In order to delete a point you must refer to
        the actual `PolylinePoint` object you wish to delete:

        **Example**:

        .. code-block:: python

          # set up the PointSet
          new_polylinepoints = [PolylinePoint(100.0, 123.0, 50.3), PolylinePoint(102.0, 125.3, 50.2)]
          mypolyline.points = new_polylinepoints

          # delete the second point in a Polyline
          # mypolyline.delete_point(PolylinePoint(102.0, 125.3, 50.2)) will not work
          p = mypolyline.points[1]  # the 2nd point
          mypolyline.delete_point(p)

        Args:
            point (cegalprizm.pythontool.PolylinePoint): the point to delete

        Raises:
            PythonToolException: If the parent PolylineSet is readonly
            ValueError: If the point is not in the polyline

        """
        if self.readonly:
            raise exceptions.PythonToolException("Parent PolylineSet is readonly")
        if self._points_cache is None:
            self._points_cache = self._load_points_cache()
        try:
            self._points_cache.remove(point)
        except ValueError:
            raise ValueError("Point is not in the polyline")
        self.points = self._points_cache
        self._load_points_cache()

    def __getitem__(self, idx):
        if self._points_cache is None:
            self._load_points_cache()
        return self._points_cache[idx]

    def __len__(self):
        if self._points_cache is None:
            self._load_points_cache()
        return self._point_count

class PolylineSet(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithDomain, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion):
    """A class holding many :class:`cegalprizm.pythontool.Polyline` objects.

    This is an iterable, returning  :class:`cegalprizm.pythontool.Polyline` objects.
    When iterating over this, do not modify the collection by adding or deleting lines
    - like many other Python iterators, undefined behaviour may result.
    """

    def __init__(self, python_petrel_polylineset: "PolylineSetGrpc"):
        super(PolylineSet, self).__init__(python_petrel_polylineset)
        self._polylines: typing.Dict[int, Polyline] = {}
        self._polylineset_object_link = python_petrel_polylineset

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="PolylineSet")
    def crs_wkt(self):
        return self._polylineset_object_link.GetCrs()

    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

    @property
    @_docstring_utils.get_polyline_type_decorator
    def polyline_type(self):
        return self._polylineset_object_link.GetPolylineType()

    @polyline_type.setter
    def polyline_type(self, polyline_type: typing.Union [str, PolylineTypeEnum]) -> None:
        if self.readonly:
            raise exceptions.PythonToolException("PolylineSet is readonly")
        if not isinstance(polyline_type, str) and not isinstance(polyline_type, PolylineTypeEnum):
            raise TypeError("The polyline type must be either a string or an instance of PolylineTypeEnum.")
        if isinstance(polyline_type, PolylineTypeEnum):
            polyline_type = polyline_type.value
        self._polylineset_object_link.SetPolylineType(polyline_type)

    def __str__(self) -> str:
        return 'PolylineSet(petrel_name="{0}")'.format(self.petrel_name)

    def __getitem__(self, idx: int) -> Polyline:
        self._check_index(idx)

        if idx not in self._polylines:
            self._polylines[idx] = Polyline(self, idx)
        return self._polylines[idx]

    def __iter__(self) -> typing.Iterator[Polyline]:
        for i in range(0, len(self)):
            yield self[i]

    def __len__(self) -> int:
        """The number of lines in this `PolylineSet`"""
        return self._polylineset_object_link.GetNumPolylines()
    
    def _check_index(self, idx: int) -> None:
        if not isinstance(idx, int):
            raise TypeError("Index (idx) must be an integer")
        if idx >= len(self) or idx < 0:
            raise ValueError("Index (idx) out of range")

    def is_closed(self, idx: int) -> bool:
        """Information if polygon is closed or open. 
                
        Args:
            idx (int): Index of the polygon in the PolylineSet

        Note: Index in Python starts at 0. Index in Petrel starts at 1.

        Raises:
            TypeError: If the index is not an integer
            ValueError: If provided index is outside the range of indexes

        Returns:
            bool: True if closed, False otherwise.
        """        
        self._check_index(idx)
        return self._polylineset_object_link.IsClosed(idx)

    @property
    def polylines(self) -> typing.Iterable[Polyline]:
        """Python iterator returning the polylines in a PolylineSet

        Use to retrieve the polylines :class:`cegalprizm.pythontool.Polyline` from the PolylineSet
        
        **Example**:

        Retrieve the first Polyline from the PolylineSet

        .. code-block:: python

            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
            polylines = polylineset.polylines
            first_polyline = next(polylines)

        Returns:
            Iterable[Polyline]: An iterator returning the polylines in a PolylineSet
        """
        return (val for val in self)

    def get_positions(self, idx: int) -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        """Gets the xyz positions of the polygons in a PolylineSet. 

        Args:
            idx: Index of the polygon in the PolylineSet

        Note: Index in Python starts at 0. Index in Petrel starts at 1.

        Raises:
            TypeError: If the index is not an integer
            ValueError: If provided index is outside the range of indexes

        Returns:
            A tuple([x], [y], [z]): where [x] is a list of x positions, [y] is a list of y positions and [z] is a list of z positions
        """ 
        self._check_index(idx)
        pts = self._polylineset_object_link.GetPoints(idx)
        return (*pts,) # type: ignore

    def set_positions(self, idx: int, xs: typing.List[float], ys: typing.List[float], zs: typing.List[float], closed: bool = False) -> None:
        """Replaces all xyz positions of the given polygon in a PolylineSet.  Use the idx parameter to specify which polygon to update, and the closed parameter to specify whether the polygon is closed or not.
             
        Note: Index in Python starts at 0. Index in Petrel starts at 1.

        Args:
            idx: Index of the polygon in the PolylineSet
            xs: A list with x-coordinates
            ys: A list with y-coordinates
            zs: A list with z-coordinates
            closed: `True` if the polygon is closed, `False` if open. Defaults to False.

        Raises:
            PythonToolException: if the PolylineSet is readonly
            TypeError: If the index is not an integer
            ValueError: if the number of x-coordinates is lower than 1, or lower than 2 if closed = True
        """        
        self._check_index(idx)
        if self.readonly:
            raise exceptions.PythonToolException("PolylineSet is readonly")
        if len(xs) < 2:
            raise ValueError("You must supply at least 2 points")
        if closed and (len(xs) < 3):
            raise ValueError("You must supply at least 3 points to create a closed polyline")

        array_x = [float(0)] * len(xs)
        array_y = [float(0)] * len(xs)
        array_z = [float(0)] * len(xs)

            
        for i, (x, y, z) in enumerate(zip(xs, ys, zs)):
            array_x[i] = x
            array_y[i] = y
            array_z[i] = z
        self._polylineset_object_link.SetPolylinePoints(idx, array_x, array_y, array_z, closed)

    def add_line(self, points: typing.List[typing.Union[PolylinePoint, primitives.Point]], closed: bool = True) -> None:
        """Adds a line to the set

        You must supply at least two points, or three if the polyline is closed.

        Args:
            points: a list of :class:`cegalprizm.pythontool.Point` objects.
            closed: `True` if the polyline is closed, `False` if open. Defaults to True.

        **Example**:

        .. code-block:: python

            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
            polylineset.readonly = False
            from cegalprizm.pythontool import Point
            point_list = [Point(487000, 6224500, -3000), Point(488000, 6224500, -3000), Point(487000, 6225000, -3000)]
            p1.add_line(point_list, closed = True)

        Raises:
            exceptions.PythonToolException: If PolylineSet is readonly
            TypeError: If points is not a list of :class:`cegalprizm.pythontool.PolylinePoint` or :class:`cegalprizm.pythontool.Point` objects
            ValueError: if fewer than 2 points are given, or fewer than 3 if closed=True
        """        
        if self.readonly:
            raise exceptions.PythonToolException("PolylineSet is readonly")
        if len(points) < 2:
            raise ValueError("You must supply at least 2 points")
        if closed and (len(points) < 3):
            raise ValueError("You must supply at least 3 points to create a closed polyline")
        for point in points:
            if not hasattr(point, "x") or not hasattr(point, "y") or not hasattr(point, "z"):
                raise TypeError("All points must be of type Point")
      
        arrayx = [float(0)] * len(points)
        arrayy = [float(0)] * len(points)
        arrayz = [float(0)] * len(points)
            
        for i, p in enumerate(points):
            arrayx[i] = p.x
            arrayy[i] = p.y
            arrayz[i] = p.z
        self._polylineset_object_link.AddPolyline(arrayx, arrayy, arrayz, closed)


    def add_lines(self, dataframe: pd.DataFrame) -> None:
        """Adds multiple lines to the set. This is a more efficient way to add many lines in one function call instead of adding each line individually.

        The input is a pandas dataframe with the same columns as the output of points_dataframe(), where each row corresponds to one point in a polyline.
        The dataframe must contain the following columns:
            "Poly" (int): The index of each polyline
            "Vert" (int): The index of each vertex (point) in the individual polylines
            "X" (float): The x-coordinate of each point
            "Y" (float): The y-coordinate of each point
            "Z" (float): The z-coordinate of each point
        Optionally the dataframe may contain an additional column:
            "Closed" (bool): True if the polyline is closed, False if open. Defaults to True.
        If the "Closed" column is provided, the value at the first row of each polyline will be used to determine if the polyline is closed or open.
        If the "Closed" column is not provided, each polyline will be closed by default.
        Any other columns in the dataframe will be ignored.
        Each polyline must have at least 2 points, or 3 if the polyline is closed.

        Args:
            dataframe: A pandas dataframe with the columns "Poly", "Vert", "X", "Y" and "Z", and optionally "Closed"
        
        **Example**:

        Add all polylines from one polylineset to another polylineset

        .. code-block:: python

            source_polylineset = petrel_connection.polylinesets["Input/Path/To/SourcePolylineSet"]
            destination_polylineset = petrel_connection.polylinesets["Input/Path/To/DestinationPolylineSet"]
            destination_polylineset.readonly = False
            points_dataframe = source_polylineset.points_dataframe()
            ## if adding a closed column to the dataframe it must have the same length as the other columns
            points_dataframe["Closed"] = [True, True, True, False, False, False, True, True, True]
            destination_polylineset.add_lines(points_dataframe)

        Raises:
            PythonToolException: If PolylineSet is readonly
            ValueError: If the dataframe does not contain the required columns
            ValueError: If each polyline does not have at least 2 points, or 3 if the polyline is closed
        """
        if self.readonly:
            raise exceptions.PythonToolException("PolylineSet is readonly")
        self._check_correct_columns(dataframe)
        contains_closed = "Closed" in dataframe.columns
        if contains_closed and not is_bool_dtype(dataframe["Closed"].dtype):
            raise ValueError("The column 'Closed' must contain boolean values")

        sorted_dataframe = dataframe.sort_values(by = ["Poly", "Vert"], inplace = False)
        polylines_dict = self._create_polylines_dict(sorted_dataframe, contains_closed)

        self._polylineset_object_link.AddMultiplePolylines(polylines_dict, contains_closed)

    def _create_polylines_dict(self, dataframe, contains_closed):
        polylines_dict = {}
        vertices, xs, ys, zs, closed = [], [], [], [], []
        current_index = dataframe["Poly"][0]

        for overall_index in dataframe.index:
            if dataframe["Poly"][overall_index] != current_index:
                ## Add to parent dict and reset
                self._verify_number_of_points(vertices, closed, contains_closed)
                polylines_dict[current_index] = (vertices, xs, ys, zs, closed)
                current_index = dataframe["Poly"][overall_index]
                vertices, xs, ys, zs, closed = [], [], [], [], []
            ## Add each point to the list
            vertices.append(dataframe["Vert"][overall_index])
            xs.append(dataframe["X"][overall_index])
            ys.append(dataframe["Y"][overall_index])
            zs.append(dataframe["Z"][overall_index])
            if contains_closed:
                closed.append(dataframe["Closed"][overall_index])

        # Add last polyline
        self._verify_number_of_points(vertices, closed, contains_closed)

        polylines_dict[current_index] = (vertices, xs, ys, zs, closed)
        return polylines_dict
    
    def _verify_number_of_points(self, vertices, closed, contains_closed):
        if len(vertices) < 2:
            raise ValueError("Each polyline must have at least 2 points")
        if contains_closed:
            if closed[0] and len(vertices) < 3:
                raise ValueError("Each closed polyline must have at least 3 points")

    def _check_correct_columns(self, dataframe: pd.DataFrame) -> None:
        if "Poly" not in dataframe.columns:
            raise ValueError("The dataframe must contain a column named 'Poly'")
        elif not is_integer_dtype(dataframe["Poly"].dtype):
            raise ValueError("The column 'Poly' must contain integer values")
        if "Vert" not in dataframe.columns:
            raise ValueError("The dataframe must contain a column named 'Vert'")
        elif not is_integer_dtype(dataframe["Vert"].dtype):
            raise ValueError("The column 'Vert' must contain integer values")
        if "X" not in dataframe.columns:
            raise ValueError("The dataframe must contain a column named 'X'")
        elif is_bool_dtype(dataframe["X"].dtype) or not is_numeric_dtype(dataframe["X"].dtype):
            raise ValueError("The column 'X' must contain float or int values")
        if "Y" not in dataframe.columns:
            raise ValueError("The dataframe must contain a column named 'Y'")
        elif is_bool_dtype(dataframe["Y"].dtype) or not is_numeric_dtype(dataframe["Y"].dtype):
            raise ValueError("The column 'Y' must contain float or int values")
        if "Z" not in dataframe.columns:
            raise ValueError("The dataframe must contain a column named 'Z'")
        elif is_bool_dtype(dataframe["Z"].dtype) or not is_numeric_dtype(dataframe["Z"].dtype):
            raise ValueError("The column 'Z' must contain float or int values")

    def delete_line(self, line: Polyline) -> None:
        """Deletes a polyline from the PolylineSet

        Args:
            line: the line to delete as a :class:`cegalprizm.pythontool.Polyline` object

        **Example**:

        Delete the second Polyline from the PolylineSet

        .. code-block:: python

            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
            polylineset.readonly = False
            polylines = polylineset.polylines
            first_polyline = next(polylines)
            second_polyline = next(polylines)
            polylineset.delete_line(second_polyline)
            
        Raises:
            PythonToolException: If PolylineSet is readonly
            TypeError: If line is not a :class:`cegalprizm.pythontool.Polyline` object
        """
        if self.readonly:
            raise exceptions.PythonToolException("PolylineSet is readonly")
        if not isinstance(line, Polyline):
            raise TypeError("Input must be a Polyline object")

        self._polylineset_object_link.DeletePolyline(line._polyline_index)

        # it's too tricky to maintain the cache so blow it away
        self._polylines = {}

    def clear(self) -> None:
        """Deletes all the lines from the PolylineSet
        
        Raises:
            PythonToolException: If PolylineSet is readonly
        """
        if self.readonly:
            raise exceptions.PythonToolException("PolylineSet is readonly")

        self._polylineset_object_link.DeleteAll()
        self._polylines = {}

    @_docstring_utils.clone_docstring_decorator(return_type="PolylineSet", respects_subfolders=True, supports_folder = True)
    def clone(self, name_of_clone: str, copy_values: bool = False, folder: "Folder" = None) -> "PolylineSet":
        _utils.verify_folder(folder)
        return typing.cast("PolylineSet", self._clone(name_of_clone, copy_values = copy_values, destination = folder))

    @_docstring_utils.move_docstring_decorator(object_type="PolylineSet")
    def move(self, destination: "Folder"):
        if self.readonly:
            raise exceptions.PythonToolException("PolylineSet is readonly")
        _utils.verify_folder(destination)
        self._move(destination)

    @property
    def parent_folder(self) -> typing.Union["Folder", "InterpretationFolder", None]:
        """Returns the parent folder of this PolylineSet in Petrel. Returns None if the object is the Input root.

        Returns:
            :class:`Folder`, :class:`InterpretationFolder` or None: The parent folder of the PolylineSet, or None if the object is located at the root level.

        **Example**:

        .. code-block:: python

            ps = petrel_connection.polylinesets["Input/Folder/PolylineSet"]
            ps.parent_folder
            >> Folder(petrel_name="Folder")
        """
        return self._parent_folder
    
    def points_dataframe(self) -> pd.DataFrame:
        """Returns a dataframe with information about the points (vertices) for all polylines in the PolylineSet.
        
        **Example**:

        .. code-block:: python

            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
            df = polylineset.points_dataframe()

        Returns:
            DataFrame: A pandas dataframe with information about the points (vertices) for all polylines in the PolylineSet.
        
        """
        df = self._polylineset_object_link.GetPointsDataFrame()
        return df
   
    def attributes_dataframe(self) -> pd.DataFrame:
        """Returns a dataframe with information about the attributes for all polylines in the PolylineSet.

        Note: Due to limitations in the Ocean API the order of the attributes cannot be guaranteed to be the same as in the Attribute spreadsheet in Petrel.

        Note: The calculation of values for well-known attributes such as Label X, Label Y and Label Z cannot be triggered through the Ocean API.
        This means that in specific cases where the Attribute spreadsheet for the PolylineSet has never been opened these values will return as NaN.
        Opening the Attribute spreadsheet in Petrel will trigger the calculation and make values available. Values are persisted when the project is saved.
        
        **Example**:

        .. code-block:: python

            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
            df = polylineset.attributes_dataframe()

        Returns:
            DataFrame: A pandas dataframe with information about the attributes for all polylines in the PolylineSet.
        
        """
        df = self._polylineset_object_link.GetAttributesDataFrame()
        return df
    
    def add_attribute(self, name: str, data_type: str, template: typing.Union[Template, DiscreteTemplate] = None) -> "PolylineAttribute":
        """Adds a user-defined attribute to the PolylineSet.

        The string and bool types do not support templates. For continuous and discrete attributes, default templates will be used if no template is specified.
        
        Args:
            name (str): Name of the attribute
            data_type (str): A string specifying the data_type. Supported strings are: string | bool | continuous | discrete
            template (Template or DiscreteTemplate): Template for the attribute. Can be specified for continuous and discrete attributes.

        Raises:
            PythonToolException: If PolylineSet is readonly
            ValueError: If data_type is not string, bool, continuous or discrete
            ValueError: If template is set for string or bool attributes
            TypeError: If template is not of type Template for continuous attribute or DiscreteTemplate for discrete attribute

        **Example**:

        .. code-block:: python

            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
            polylineset.readonly = False
            new_string_attribute = polylineset.add_attribute("New String Attribute", "string")

            template = petrel_connection.templates["Templates/Path/To/Template"]
            new_cont_attribute = polylineset.add_attribute("New Continuous Attribute", "continuous", template)

        Returns:
            PolylineAttribute: The newly created attribute as a PolylineAttribute object
        """

        if self.readonly:
            raise exceptions.PythonToolException("PolylineSet is readonly")

        prop_type = utils.GetPropTypeFromString(data_type)
        if prop_type is None:
            raise ValueError("Unsupported data_type, supported values are: string | bool | continuous | discrete")
        
        template_guid = ""
        if template is not None:
            if not isinstance(template, (Template, DiscreteTemplate)):
                raise TypeError("template must be of type Template or DiscreteTemplate")
            if data_type.lower() == "string" or data_type.lower() == "bool":
                raise ValueError("template cannot be set for string or bool attributes")
            if data_type.lower() == "discrete" and not isinstance(template, DiscreteTemplate):
                raise TypeError("template must be of type DiscreteTemplate for discrete attributes")
            if data_type.lower() == "continuous" and not isinstance(template, Template):
                raise TypeError("template must be of type Template for continuous attributes")
            template_guid = template.droid

        object_ref = self._polylineset_object_link.AddAttribute(name, prop_type, template_guid)
        grpc = PolylineAttributeGrpc(object_ref.guid, self._polylineset_object_link._plink)
        attribute = PolylineAttribute(grpc, self)
        return attribute
    
    def delete_attribute(self, attribute: PolylineAttribute) -> None:
        """Deletes a user-defined attribute from the PolylineSet.

        Note: Well-known attributes such as Label X, Label Y and Label Z cannot be deleted.

        Args:
            attribute (PolylineAttribute): The attribute to delete as a PolylineAttribute object

        Raises:
            PythonToolException: If PolylineSet is readonly
            TypeError: If the attribute is not a PolylineAttribute object
            UserErrorException: If the attribute is not found in the PolylineSet
            UserErrorException: If the attribute is a well-known attribute such as Label X, Label Y or Label Z

        **Example**:

        .. code-block:: python

            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
            polylineset.readonly = False
            incorrectly_added_attribute = polylineset.add_attribute("New Bool Attribute", "string")
            
            polylineset.delete_attribute(incorrectly_added_attribute)
        """

        if self.readonly:
            raise exceptions.PythonToolException("PolylineSet is readonly")
        if not isinstance(attribute, PolylineAttribute):
            raise TypeError("attribute must be a PolylineAttribute object")

        polylineset_guid = self._polylineset_object_link._guid
        attribute_guid = attribute._guid
        self._polylineset_object_link.DeleteAttribute(polylineset_guid, attribute_guid)

    @property
    def attributes(self) -> typing.Iterable[PolylineAttribute]:
        """Python iterator returning the attributes in a PolylineSet

        Use to retrieve the attributes :class:`cegalprizm.pythontool.PolylineAttribute` from the PolylineSet.
        Attributes can be iterated over, or accessed by index or name.
        Note that in the case of duplicate names, the unique name must be used to retrieve the attribute by name. (See example below)
        
        **Example**:

        Retrieve the first attribute from the PolylineSet

        .. code-block:: python

            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
            first_attribute = polylineset.attributes[0]

        **Example**:

        Retrieve a named attribute from the PolylineSet

        .. code-block:: python

            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]
            my_attribute = polylineset.attributes["MyAttribute"]

        **Example**:

        Retrieve a named attribute from the PolylineSet where mulitple attributes have the same name

        .. code-block:: python

            # As an example, imagine Petrel has two attributes named "Custom". 
            # In PTP they will get a suffix added as a unique name, "Custom (1) and "Custom (2)"
            polylineset = petrel_connection.polylinesets["Input/Path/To/PolylineSet"]

            custom1 = polylineset.attributes["Custom (1)"]
            print(custom1) 
            >> 'PolylineAttribute(unique_name="Custom (1)")'
            print(custom1.petrel_name)
            >> 'Custom'

            custom2 = polylineset.attributes["Custom (2)"]
            print(custom2)
            >> 'PolylineAttribute(unique_name="Custom (2)")'
            print(custom2.petrel_name)
            >> 'Custom'

            # In this example, the line below will raise a KeyError
            custom = polylineset.attributes["Custom"]

        Returns:
            Iterable[PolylineAttribute]: An iterator returning the attributes in a PolylineSet
        """
        return PolylineAttributes(self)



class PolylineAttributes(object):
    """An iterable collection of :class:`cegalprizm.pythontool.PolylineAttribute` objects for the PolylineAttributes in the PolylineSet."""

    def __init__(self, parent: PolylineSet):
        self._parent = parent
        if isinstance(parent, PolylineSet):
            petrel_connection = parent._polylineset_object_link._plink
            grpcs = [
                PolylineAttributeGrpc(object_ref.guid, petrel_connection, object_ref.petrel_name) for object_ref in parent._polylineset_object_link.GetAllAttributes()
            ]
            self._polyline_attributes = [PolylineAttribute(grpc, parent) for grpc in grpcs]
            self._polyline_attributes_dict = {attr._get_name(): attr for attr in self._polyline_attributes}
        else:
            raise TypeError("Parent must be a PolylineSet object")
        
    def __iter__(self) -> typing.Iterable[PolylineAttribute]:
        return iter(self._polyline_attributes)
    
    def __getitem__(self, key) -> PolylineAttribute:
        if isinstance(key, int):
            return self._polyline_attributes[key]
        elif isinstance(key, str):
            return self._polyline_attributes_dict[key]
        
    def __str__(self) -> str:
        return 'PolylineAttributes({0}="{1}")'.format(self._parent._petrel_object_link._sub_type, self._parent)

    def __repr__(self) -> str:
        return str(self)
    




