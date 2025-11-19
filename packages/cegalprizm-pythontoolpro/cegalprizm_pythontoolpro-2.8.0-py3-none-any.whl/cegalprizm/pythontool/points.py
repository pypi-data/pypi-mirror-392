# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import typing

import pandas as pd

from contextlib import contextmanager
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithDomain, PetrelObjectWithTemplate, PetrelObjectWithHistory
from cegalprizm.pythontool.petrelobject import PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion
from cegalprizm.pythontool import primitives, exceptions, _docstring_utils, _utils
from cegalprizm.pythontool.exceptions import PythonToolException
from cegalprizm.pythontool.template import Template, DiscreteTemplate
from cegalprizm.pythontool.chunking_array import _ChunkingArray
import base64

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.points_grpc import PointSetGrpc
    from cegalprizm.pythontool import Folder, InterpretationFolder

class PointsetPoint(object):
    def __init__(self, pointset: "PointSet", index):
        self._pointset = pointset
        self._index = index

    def __eq__(self, other) -> bool:
        try:
            return other.x == self.x and other.y == self.y and other.z == self.z # type: ignore
        except Exception:
            return False

    def __str__(self) -> str:
        return "PointsetPoint(x={:.2f}, y={:.2f}, z={:.2f})".format(self.x, self.y, self.z)

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def x(self) -> float:
        """Returns the x coordinate of the point as a float."""
        return self._pointset._get_position(self._index)[0] # type: ignore

    @property
    def y(self) -> float:
        """Returns yhe y coordinate of the point as a float."""
        return self._pointset._get_position(self._index)[1] # type: ignore

    @property
    def z(self) -> float:
        """Returns the z coordinate of the point as a float."""
        return self._pointset._get_position(self._index)[2] # type: ignore

class _PointsProvider:
    def __init__(self, petrel_object_link: "PointSetGrpc"):
        self._petrel_object_link = petrel_object_link
        self._hits = 0
        self._len = None

    def get_range(self, start_incl, end_excl):
        self._hits += 1
        if (
            start_incl >= len(self)
            or start_incl < 0
            or end_excl > len(self)
            or end_excl <= 0
        ):
            raise Exception("Provider get_range oob: %d, %d" % (start_incl, end_excl))

        return self._petrel_object_link.GetPositionValuesByRange(start_incl, end_excl - 1, 1, None, None, None, -1).values

    def get_len(self) -> int:
        if self._len is None:
            self._len = self._petrel_object_link.GetPointCount()
        return self._len
    
    def __len__(self) -> int:
        return self.get_len()

    # for checking cache hits in tests
    @property
    def hits(self) -> int:
        return self._hits

class PointSet(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithDomain, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithParentFolder, PetrelObjectWithDeletion):
    """Class representing a point set in Petrel."""
    
    def __init__(self, python_petrel_pointset: "PointSetGrpc") -> None:
        super(PointSet, self).__init__(python_petrel_pointset)
        self._points_cache: typing.Optional[typing.List[typing.Union[primitives.Point, PointsetPoint]]] = None

        self._pointset_object_link = python_petrel_pointset

    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="PointSet")
    def crs_wkt(self):
        return self._pointset_object_link.GetCrs()

    def as_dataframe(self, 
            indices: typing.Optional[typing.List[int]] = None, 
            start: typing.Optional[int] = None, 
            end: typing.Optional[int] = None, 
            step: typing.Optional[int] = None,
            x_range: typing.Union[typing.Tuple[int], typing.Tuple[int, int]] = None, 
            y_range: typing.Union[typing.Tuple[int], typing.Tuple[int, int]] = None, 
            z_range: typing.Union[typing.Tuple[int], typing.Tuple[int, int]] = None, 
            max_points: typing.Optional[int] = None,
            show_units=False) -> pd.DataFrame:
        """Gets a dataframe with point coordinates and attribute data.

        **Example**:

        With the following code, where pointset is an instance of PointSet,
        we get a dataframe named df and print the column names

        .. code-block:: python

          df = pointset.as_dataframe()
          print('Columns of the dataframe:', list(df.columns))

        
        Each column of the dataframe represents an attribute or point coordinate.
        The column names are the names of the attributes. If there are attributes with
        equal names, these attribute names are given a suffix with a number to make the column
        names unique.

        **Example:**

        With the following code we get data of an attribute named TWT

        .. code-block:: python

          df = pointset.as_dataframe()
          # The values of attribute TWT
          twt = df['TWT']
          print(twt)
           
        Point sets can be large, and there are several ways of retrieving just a part of the point set
        from Petrel. The following example shows how to select based on point indices.

        **Example**:

        Selecting the attributes for a range of indices from index 10_000 to index 19_999
        with step length 10

        .. code-block:: python        

          df = pointset.as_dataframe(start = 10_000, end = 19_999, step = 10)

        The step must be a positive integer and end must be larger or equal to start.
        To select the attributes for some given indices do the following.

        .. code-block:: python
                
          df = pointset.as_dataframe(indices = [10, 12, 15, 22])
       
        The values in indices must be monotonically increasing integers.
        
        In the next examples we filter the attributes based on spatial coordinates.

        **Examples**:

        Selecting attributes only for points within specified ranges of x, y and z.

        .. code-block:: python

          df = pointset.as_dataframe(x_range = [10_000, 11_000], 
                                     y_range = [23_000, 24_000], 
                                     z_range = [-3_000, 0])

        Selecting attributes for points with a range in x, for any values of y and z, but start
        searching at index 1_000_000 and receiving a maximum number of 200_000 attributes

        .. code-block:: python
                
          df = pointset.as_dataframe(x_range = [10_000, 20_000], 
                                     start = 1_000_000, 
                                     max_points = 200_000)
       
        Note: As from Petrel 2021 the autogenerated elevation time pointset attribute are named 'TWT' instead of previously used 'TWT auto' for NEW pointsets.

        Args:
            indices: A list or tuple of point indices. Values must be monotonically increasing.
            start: Start index, larger or equal to zero.
            end: End index.
            step: The step. Typically used together with ``start`` and ``end``.
            x_range: A list with minimum and maximum point coordinate in x dimension
            y_range: A list with minimum and maximum point coordinate in y dimension
            z_range: A list with minimum and maximum point coordinate in z dimension
            max_points: Maximum number of points in dataframe.
            show_units: If this flag is set to true the unit symbol of the PointSet attribute will be attached to the DataFrame column name in square brackets.

        Returns:
            Dataframe: A dataframe with points and attributes data.
        """
        
        self._verify_parameters(indices, start, end, step, x_range, y_range, z_range, max_points)
        
        if not x_range:
            x_range = (0,)
        if not y_range:
            y_range = (0,)
        if not z_range:
            z_range = (0,)
        if not max_points:
            max_points = -1
        
        has_xyz_range = len(x_range) or len(y_range) or len(z_range)

        if indices is not None:
            xyz_df = self._pointset_object_link.GetPositionValuesByInds(indices)

            if has_xyz_range:
                indices = xyz_df.index
            df = self._pointset_object_link.GetPropertiesValuesByInds(indices)
        else:
            if start is None:
                start = 0
            if end is None:
                end = -1
            if step is None:
                step = 1
            xyz_df = self._pointset_object_link.GetPositionValuesByRange(start, end, step, x_range, y_range, z_range, max_points)
            if has_xyz_range:
                indices = xyz_df.index
                df = self._pointset_object_link.GetPropertiesValuesByInds(indices)

        if df is not None:
            ordered_column_names = ['x', 'y', 'z'] + df.columns.tolist()
            df = pd.concat([xyz_df, df], axis=1)
            df = df[ordered_column_names]
        else:
            df = xyz_df[['x', 'y', 'z']]

        if show_units:
            attributes_info = self._attributes_info()
            for key in attributes_info:
                if attributes_info[key]['Template'] is None or attributes_info[key]['Type'] == 'Discrete':
                    continue
                unit = attributes_info[key]['Unit']
                new_name = _utils.to_unit_header(key, unit)
                df.rename(columns = {key:new_name}, inplace=True)
        
        return df

    def _verify_parameters(self, indices, start, end, step, x_range, y_range, z_range, max_points):
        error_messages = []
        
        start_ok = start is None or (self._is_int(start) and start >= 0)
        end_ok = end is None or (self._is_int(end) and ((start is None and end >= 0) or (start is not None and end >= start)))
        step_ok = step is None or (self._is_int(step) and step >= 1)

        if not start_ok:
            error_messages.append('Parameter "start" must be an integer larger or equal to zero')
        if not end_ok:
            error_messages.append('Parameter "end" must be an integer larger or equal to 0, or larger or equal to "start" if "start" is given')
        if not step_ok:
            error_messages.append('Parameter "step" must be an integer larger or equal to 1')

        x_range_ok = x_range is None or self._range_ok(x_range)
        y_range_ok = y_range is None or self._range_ok(y_range)
        z_range_ok = z_range is None or self._range_ok(z_range)
        
        if not x_range_ok or not y_range_ok or not z_range_ok:
            error_messages.append('Parameters "x_range", "y_range" and "z_range" must be iterables (typically a list or a tuple) with length 2')

        if max_points is not None and (max_points % 1 != 0 or max_points < 0):
            error_messages.append('Parameter "max_points" must be a an integer larger or equal to zero')

        if indices is not None and not self._is_iterable(indices):
            error_messages.append('Parameter "indices" must be iterable, typically a list or a tuple')

        if len(error_messages) > 0:
            raise PythonToolException('Errors in parameter values:\n' +'./n'.join(error_messages))
    
    def _range_ok(self, r):
        return self._is_iterable(r) and len(r) == 2 and self._is_number(r[0]) and self._is_number(r[1])

    def _is_int(self, x):
        return x % 1 == 0
    
    def _is_number(self, x):
        try:
            float(x)
            ok = True
        except Exception:
            ok = False
        return ok

    def _is_iterable(self, x):
        try:
            iter(x)
            ok = True
        except Exception:
            ok = False
        return ok
 
    def _refresh(self):
        self._points_chunking_array = _ChunkingArray(_PointsProvider(self._pointset_object_link), chunk_size=1000)
        self._points_cache = [PointsetPoint(self, i) for i in range(self._pointset_object_link.GetPointCount())]
        self._propertyCount = self._pointset_object_link.GetPropertyCount()

    def _load_cache(self):
        self._refresh()

    def __str__(self):
        """String representation of the `PointSet` object"""
        return 'PointSet(petrel_name="{0}")'.format(self.petrel_name)

    @property
    def points(self) -> typing.List[PointsetPoint]:
        """A list of the :class:`cegalprizm.pythontool.PointsetPoint` objects making up the pointset.
        
        To set the multiple points, assign a list of :class:`cegalprizm.pythontool.Point` objects to this property.

        **Example**:

        Get first point of a PointSet and print it

        .. code-block:: python

            pointset = petrel_connection.pointsets.get_by_name("MyPointSet")
            points_list = pointset.points
            first_point = points_list[0]
            print(first_point)  
            >> PointsetPoint(x=1.01, y=2.02, z=987.65)

        **Example**:

        Set the points of a PointSet by providing a list of points

        .. code-block:: python

            from cegalprizm.pythontool import Point
            pointset = petrel_connection.pointsets.get_by_name("MyPointSet")
            new_points = [Point(100.0, 123.0, 50.3), Point(102.0, 125.3, 50.2)]
            pointset.readonly = False
            pointset.points = new_points
        
        """
        if self._points_cache is None:
            self._load_cache()
        return self._points_cache # type: ignore

    @points.setter
    def points(self, lst: typing.List[primitives.Point]) -> None:
        if self.readonly:
            raise exceptions.PythonToolException("Object is readonly")
        try:
            arrayx = [float(0)] * len(lst)
            arrayy = [float(0)] * len(lst)
            arrayz = [float(0)] * len(lst)
            delete_array = [int(0)] * len(self)
            
            for i, pp in enumerate(self.points):
                delete_array[i] = pp._index
            
            for i, p in enumerate(lst):
                arrayx[i] = p.x
                arrayy[i] = p.y
                arrayz[i] = p.z

            self._pointset_object_link.DeletePoints(delete_array)
            self._pointset_object_link.AddPoints(arrayx, arrayy, arrayz)
            self._refresh()
        except TypeError as e:
            print(e)
            raise TypeError("You must pass an iterable (list) of points")

    def add_point(self, point: primitives.Point) -> None:
        """Adds a point

        Adds a single point in displayed world co-ordinates to the pointset.
        Using this method multiple times will be slower than building up a list of :class:`cegalprizm.pythontool.Point` objects and assigning it to the :func:`points` property in one go.

        **Example**:

        .. code-block:: python

          from cegalprizm.pythontool import Point

          # slower
          mypointset.add_point(Point(100.0, 123.0, 50.3))
          mypointset.add_point(Point(102.0, 125.3, 50.2))

          # faster
          new_points = [Point(100.0, 123.0, 50.3), Point(102.0, 125.3, 50.2)]
          mypointset.points = new_points

        Args:
            point: the point to add

        """
        if self.readonly:
            raise exceptions.PythonToolException("Object is readonly")
        try:
            lst = [point]
            arrayx = [float(0)] * len(lst)
            arrayy = [float(0)] * len(lst)
            arrayz = [float(0)] * len(lst)
        
            for i, p in enumerate(lst):
                arrayx[i] = p.x
                arrayy[i] = p.y
                arrayz[i] = p.z

            self._pointset_object_link.AddPoints(arrayx, arrayy, arrayz)
            self._refresh()
        except TypeError:
            raise TypeError("You must pass an iterable (list) of points")


    def delete_point(self, point: PointsetPoint) -> None:
        """Deletes a point

        Deletes one point from the pointset.  Using this
        method multiple times will be slower than manipulating a list
        of :class:`cegalprizm.pythontool.PointsetPoint` objects and assigning it
        to the :func:`points` property in one go.

        Note that :class:`cegalprizm.pythontool.PointsetPoint` objects are compared by
        reference, not value.   In order to delete a point you must refer to
        the actual `PointsetPoint` object you wish to delete:

        **Example**:

        .. code-block:: python

          # set up the PointSet
          new_points = [PointsetPoint(100.0, 123.0, 50.3), PointsetPoint(102.0, 125.3, 50.2)]
          mypointset.points = new_points

          # delete the second point in a PointSet
          # mypointset.delete_point(PointsetPoint(102.0, 125.3, 50.2)) will not work
          p = mypointset.points[1]  # the 2nd point
          mypointset.delete_point(p)

        Args:
            point: the point to delete

        """
        if self.readonly:
            raise exceptions.PythonToolException("Object is readonly")
        if self._points_cache is None:
            self._refresh()

        self._points_cache = typing.cast(typing.List[typing.Union[primitives.Point, PointsetPoint]], self._points_cache)

        if isinstance(point, PointsetPoint):
            index_to_delete = point._index
        elif point in self._points_cache:
            index_to_delete = self._points_cache.index(point)
        else:
            raise ValueError("PointsetPoint is not in the pointset")

        try:
            delete_array = [int(0)]
            delete_array[0] = index_to_delete
            self._pointset_object_link.DeletePoints(delete_array)
        except TypeError:
            raise TypeError("You must pass an iterable (list) of points")

        self._refresh()

    @_docstring_utils.clone_docstring_decorator(return_type="PointSet", respects_subfolders=True, supports_folder=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, folder: "Folder" = None) -> "PointSet":
        _utils.verify_folder(folder)
        return typing.cast("PointSet", self._clone(name_of_clone, copy_values = copy_values, destination = folder))

    @_docstring_utils.move_docstring_decorator(object_type="PointSet")
    def move(self, destination: "Folder"):
        if self.readonly:
            raise PythonToolException("PointSet is readonly")
        _utils.verify_folder(destination)
        self._move(destination)
    
    @property
    def parent_folder(self) -> typing.Union["Folder", "InterpretationFolder", None]:
        """Returns the parent folder of this PointSet in Petrel. Returns None if the object is the Input root.

        Returns:
            :class:`Folder`, :class:`InterpretationFolder` or None: The parent folder of the PointSet, or None if the object is located at the root level.

        **Example**:

        .. code-block:: python

            ps = petrel_connection.pointsets["Input/Folder/PointSet"]
            ps.parent_folder
            >> Folder(petrel_name="Folder")
        """
        return self._parent_folder

    def __getitem__(self, idx: int) -> typing.Union[primitives.Point, PointsetPoint]:
        if self._points_cache is None:
            self._refresh()
        self._points_cache = typing.cast(typing.List[typing.Union[primitives.Point, PointsetPoint]], self._points_cache)
        return self._points_cache[idx]

    def __len__(self) -> int:
        return self._pointset_object_link.GetPointCount()

    def _get_position(self, index):
        """The x, y and z coordinates of the points of the point set.

        Returns:

            List of list of floats: A table with x, y and z values.
        """
        return self._points_chunking_array[index]

    def set_values(self, 
            data: pd.DataFrame, 
            create: typing.Optional[typing.List[str]] = None, 
            df_includes_units: bool =  False) -> None:
        """Attribute values are written to Petrel. The data parameter must be a Pandas Dataframe with a format as returned by the as_dataframe method.
        
        To create a new attributes, list the attribute names in the optional parameter create.
        The names listed in create must be existing columns in the input dataframe.

        The data type of the created attributes is determined by the data type of the columns in the input dataframe.
        Possible data types are: Continuous (double/float), Discrete (int), Boolean (bool), String (str) and DateTime (datetime).

        **Example**:

        Get the attributes of pointset, add a new column based on the existing column
        named TWT, and create an attribute in Petrel with the values of this new column.

        .. code-block:: python

          df = pointset.as_dataframe()
          # Creates two new columns
          df['TWT adjusted 1'] = 0.95 * df['TWT']
          df['TWT adjusted 2'] = 0.97 * df['TWT']
          # Create the new attributes in Petrel
          pointset.set_values(df, create = ['TWT adjusted 1', 'TWT adjusted 2'])
                
        Raises:
            PythonToolException: If the name of any of the attributes to create is not a column name in the input dataframe.

        Args:
            data: A Pandas Dataframe of attributes with format as returned by as_dataframe() 
            create: A list of attribute names to create. Defaults to [].
            df_includes_units: A flag to indicate that the dataframe columns in the input contains unit values which need to be stripped.
        """


        if create is None:
            create = []

        input_create = create.copy()

        import pandas as pd
        if df_includes_units:

            if input_create:
                new_create = []
                for c in input_create:
                    if _utils.is_valid_unit_header(c):
                        name = _utils.name_from_unit_header(c)
                        new_create.append(name)
                input_create = new_create

            if isinstance(data, pd.core.frame.DataFrame):
                column_headers = data.columns
                old_name = column_headers.copy()
                attributes_info = self._attributes_info()
                for column_header in column_headers:
                    name = _utils.name_from_unit_header(column_header)
                    if attributes_info.get(name) is not None:
                        if attributes_info[name]['Template'] is None or attributes_info[name]['Type'] == 'Discrete':
                            continue
                        data.rename(columns = {column_header: name}, inplace=True)
                    else:
                        if _utils.is_valid_unit_header(column_header):
                            name = _utils.name_from_unit_header(column_header)
                            if name in input_create:
                                data.rename(columns = {column_header: name}, inplace=True)
            elif isinstance(data, pd.core.series.Series):
                old_name = data.name
                name = _utils.name_from_unit_header(data.name)
                data.rename(name, inplace=True)

        if isinstance(data, pd.core.frame.DataFrame):
            self._verify_create_names(list(data.columns), input_create)
        elif isinstance(data, pd.core.series.Series):
            self._verify_create_names([data.name], input_create)

        unique_property_names = self._pointset_object_link.OrderedUniquePropertyNames()        
        restricted_property_names = ["x", "y", "z"]
        if data.index.empty: # Empty dataframe
            return
        
        attributes_to_create = []
        data_to_write = [] 

        if isinstance(data, pd.core.frame.DataFrame):
            for col_name in data:
                if col_name not in unique_property_names and col_name in input_create:
                    point_property_data_type = self._pointset_object_link._property_range_handler.find_element_type_from_array(data[col_name])
                    attributes_to_create.append((col_name, point_property_data_type))
                    data_to_write.append((data[col_name], point_property_data_type))
                elif col_name in unique_property_names and col_name not in restricted_property_names:
                    data_to_write.append((data[col_name], None))
        elif isinstance(data, pd.core.series.Series):
            if data.name not in unique_property_names and data.name  in input_create:
                point_property_data_type = self._pointset_object_link._property_range_handler.find_element_type_from_array(data)
                attributes_to_create.append((data.name, point_property_data_type))
                data_to_write.append((data, point_property_data_type))
            elif data.name in unique_property_names and data.name not in restricted_property_names:
                data_to_write.append((data, None))

        if attributes_to_create:
            self._pointset_object_link.AddProperties(attributes_to_create)

        if data_to_write:
            self._pointset_object_link.SetPropertyValues(data_to_write)

        if df_includes_units:
            if isinstance(data, pd.core.frame.DataFrame):
                data.rename(columns = dict(zip(data.columns, old_name)), inplace=True)
            elif isinstance(data, pd.core.series.Series):
                data.rename(old_name, inplace=True)

    def _verify_create_names(self, df_column_names, create_names):
        
        if not self._is_iterable(create_names):
            raise PythonToolException('Parameter create must be an iterable (typically a list or a tuple) of strings')

        if not create_names:
            return

        non_existing_in_dataframe = []
        for name in create_names:
            if name not in df_column_names:
                non_existing_in_dataframe.append(name)

        if len(non_existing_in_dataframe) > 0:
            raise PythonToolException('Names of attributes to create must be present as columns in the dataframe. ' +\
                'non_existing_in_dataframe')

    @contextmanager
    def values(self, 
            indices: typing.Optional[typing.List[int]] = None, 
            start: typing.Optional[int] = None, 
            end: typing.Optional[int] = None, 
            step: typing.Optional[int] = None,
            x_range: typing.Tuple[int, int] = None, 
            y_range: typing.Tuple[int, int] = None, 
            z_range: typing.Tuple[int, int] = None, 
            max_points: typing.Optional[int] = None) -> typing.Iterator[pd.DataFrame]:
        """A context manager to use for reading and writing attribute data. The input parameters
        are the same as for method as_dataframe.

        **Example**:
            
        Read part of a point set from Petrel and change a value of an attribute called 'TWT'.
        
        .. code-block:: python
        
          with pointset.values(start = 0, end = 1000) as df:
              df.loc[999, 'TWT'] = 123.4

        At the end of the with block, the content of df is automatically written back to Petrel.
        """

        df = self.as_dataframe(indices = indices, start = start, end = end, step = step,
            x_range = x_range, y_range = y_range, z_range = z_range, max_points = max_points)

        try:
            yield df
        finally:            
            self.set_values(df)

    def _attributes_info(self, as_string = False):
        """A dict of dicts with information on the attributes. The keys are the attribute names
        and each value of the dict is itself a dict with information on an attribute. 

        **Example**:

        With the following code we information on an attribute named ``TWT``

        .. code-block:: python

          info = pointset._attributes_info()
        
          # The unit symbol of the attribute
          unit_symbol = info['TWT']['Unit']

          # All info on attribute 'TWT'
          for name, value in info['TWT']:
              print(f'{name}: {value}')

        Args:
            as_string (bool, optional): Return a string with information instead of a dict. Defaults to False.

        Returns:
            dict of dicts: A dict of dicts with information on the attributes.
        """
        attributes_info_string = str(self._pointset_object_link.AttributesInfo())
        split_by_semicolon = attributes_info_string.split(";")
        first_row = split_by_semicolon[0].split(",")
        d = {}
        for idx in range(1, len(split_by_semicolon) - 1):
            comma_split = split_by_semicolon[idx].split(",")
            attribute_info = {self._decode_string(first_row[1]): self._decode_string(comma_split[1]),
                              self._decode_string(first_row[2]): self._decode_string(comma_split[2]), 
                              self._decode_string(first_row[3]): self._decode_string(comma_split[3]), 
                              self._decode_string(first_row[4]): self._decode_string(comma_split[4]), 
                              self._decode_string(first_row[5]): self._decode_string(comma_split[5])}
            d[self._decode_string(comma_split[0])] = attribute_info

        if not as_string:
            return d

    def _decode_string(self, base64_string_to_be_decoded):
        base64_bytes_to_be_decoded = base64_string_to_be_decoded.encode('ascii')
        decoded_bytes = base64.b64decode(base64_bytes_to_be_decoded)
        decoded_message = decoded_bytes.decode('ascii')
        if not decoded_message:
            return None
        return decoded_message

