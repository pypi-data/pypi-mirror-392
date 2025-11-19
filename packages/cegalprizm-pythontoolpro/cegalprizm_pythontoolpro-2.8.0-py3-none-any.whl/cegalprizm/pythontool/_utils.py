# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import numpy as np
import pandas as pd
import datetime
import typing
import re
from distutils.util import strtobool
from cegalprizm.pythontool.enums import NumericDataTypeEnum
from cegalprizm.pythontool.exceptions import PythonToolException, UserErrorException
from cegalprizm.pythontool.template import Template, DiscreteTemplate

CPY3 = 'cpy3'


def python_env():
    return CPY3


def iterable_values(arr):
    return arr.flat


def clone_array(arr: np.ndarray) -> np.ndarray:
    return arr.copy()


def to_backing_arraytype(nparray):
    ''' Creates and returns a .NET Array that mirrors the provided numpy array

    @nparray: numpy array

    @Returns: .NET Array with element type matching nparray.dtype and identical dimensions with content that matches the provided numpy array
    '''
    return nparray

######################## Conversions from .NET ###########################

def from_backing_arraytype(src):
    ''' Creates and returns a numpy Array that mirrors the provided .NET array

    @src: .NET Array in in-process mode and a protobuf type in out-of-process mode

    @Returns: numpy Array with dtype matching src's element type, and identical dimensions with content that matches the provided .NET Array
    '''
    return src

def _to_shaped_ndarray(val, size_i, size_j, size_k, np_type, spanning_dims = 'ijk'):
    if isinstance(size_i, int):
        size_i = (size_i, size_i+1)
    if isinstance(size_j, int):
        size_j = (size_j, size_j+1)
    if isinstance(size_k, int):
        size_k = (size_k, size_k+1)
    if isinstance(val, list):
        val = np.array(val, dtype=np_type)

    if not hasattr(val, "__len__"):
        val_ndarray = np.empty(size_k, dtype = np_type)
        val_ndarray.fill(val)        
    else:
        val_ndarray = val
    
    if spanning_dims == 'ij':
        di, dj = size_i[1]-size_i[0], size_j[1] - size_j[0]
        val_ndarray.shape = (di, dj)
    elif spanning_dims == 'k':
        dk = size_k[1]-size_k[0]
        val_ndarray.shape = (dk)
    else:
        di, dj, dk = size_i[1]-size_i[0], size_j[1] - size_j[0], size_k[1]-size_k[0]
        val_ndarray.shape = (di, dj, dk)
            
    return val_ndarray.astype(np_type, copy = False, subok = True)

###################

def _ensure_1d_array(val, i, np_typ, net_typ, convert):
    if isinstance(val, np.ndarray):
        return val.astype(dtype=np_typ, copy=False)
    elif isinstance(val, list):
        if len(val) > i:
            raise ValueError("too many values")
        array = np.empty((i), np_typ)
        for index in range(0, i):
            array[index] = convert(val[index])
        return array

    raise ValueError("Cannot convert %s into 1d array" % val)

def ensure_1d_float_array(val, i):
    """Converts a flat list into a Array[float] if necessary"""
    return _to_shaped_ndarray(val, 1, 1, (0, i), np.float32, spanning_dims = 'k')

def ensure_1d_float64_array(val, i):
    """Converts a flat list into a Array[float64] if necessary"""
    return _to_shaped_ndarray(val, 1, 1, (0, i), np.float64, spanning_dims = 'k')

def ensure_1d_int_array(val, i):
    """Converts a flat list into a Array[int] if necessary"""
    return _to_shaped_ndarray(val, 1, 1, (0, i), np.int32, spanning_dims = 'k')

def ensure_2d_float_array(val, i, j):
    """Converts a flat or nested list into a Array[float] if necessary"""
    return _to_shaped_ndarray(val, (0, i), (0, j), 1, np.float32, spanning_dims = 'ij')

def ensure_2d_int_array(val, i, j):
    """Converts a flat or nested list into a Array[float]
    if necessary"""
    return _to_shaped_ndarray(val, (0, i), (0, j), 1, np.int32, spanning_dims = 'ij')

def ensure_3d_float_array(val, i, j, k):
    return _to_shaped_ndarray(val, (0, i), (0, j), (0, k), np.float32)

def ensure_3d_int_array(val, i, j, k):
    return _to_shaped_ndarray(val, (0, i), (0, j), (0, k), np.int32)

def str_has_content(s: typing.Optional[str]) -> bool:
    """Returns False if the string is None, empty, or just whitespace"""
    if s is None:
        return False
    return bool(s.strip())

def str_or_none(s: typing.Optional[str]) -> typing.Optional[str]:
    if not str_has_content(s):
        return None
    return s

def about_equal(a, b):
    return abs(a-b) < 0.0000001

def float64array(lst):
    return ensure_1d_float64_array(lst, len(lst))

def intarray(lst):
    return ensure_1d_int_array(lst, len(lst))

def to_python_datetime(dt: typing.Union[typing.Any, datetime.datetime]) -> datetime.datetime:
    if isinstance(dt, datetime.datetime):
        return dt
    else:
        raise ValueError("Argument was expected to be a datetime.datetime object, got {}".format(dt))

def from_python_datetime(dt):
    return dt

def native_accessor(accessor):
    if not isinstance(accessor, tuple):
        raise TypeError("accessor is not tuple")
    return accessor

## Get object from iterable collection
def get_item_from_collection_petrel_name(collection: typing.Iterable, key):
    if isinstance(key, int):
        return collection[key]
    elif isinstance(key, str):
        result = [x for x in collection if x.petrel_name == key]
        if(len(result) == 0):
            return None
        elif len(result) == 1:
            return result[0]
        else:
            return result
        
## Check and Get wells for wells_filter
def get_wells(well = None, wells_filter = None):
    check_wells(well, wells_filter)
    if well is None and wells_filter is None:
        return []
    if wells_filter is not None:
        return wells_filter
    if well is not None:
        return [well]

def check_well(well):
    from cegalprizm.pythontool.borehole import Well
    if well is not None:
        if not isinstance(well, Well):
            raise ValueError("Each well input must be a Well object as returned from petrelconnection.wells")
        
def check_wells(well = None, wells_filter = None):
    if well is None and wells_filter is None:
        return
    if wells_filter is not None:
        if not isinstance(wells_filter, list):
            raise TypeError("wells_filter must be a list of Well objects as returned from petrelconnection.wells")
        for well in wells_filter:
            check_well(well)
    if well is not None:
        check_well(well)

# Unit header is on the form "{name} [{unit}]"
unit_header_regex = r"(?P<objectname>.+)(?P<unit>\[.+\]|\[\])$"
def to_unit_header(name, unit):
    header = name + ' [' + unit + ']'
    if not is_valid_unit_header(header):
        raise ValueError("\"" + header + "\" is not a valid unit header")
    return header

def name_from_unit_header(header):
    if is_valid_unit_header(header):
        return re.search(unit_header_regex, header).group(1).rstrip()

def unit_from_unit_header(header):
    unit_with_brackets = re.search(unit_header_regex, header).group(2)
    return str(unit_with_brackets)[1:-1]

def is_valid_unit_header(header):
    return re.fullmatch(unit_header_regex, header) is not None

## IJK

def check_extent_2d(extent, indices):
        for i_, j_ in zip(*indices[:2]):
            if i_ < 0 or j_ < 0 :
                raise PythonToolException("Index cannot be less than zero")
            if i_ >= extent.i or j_ >= extent.j:
                raise PythonToolException("Index cannot be greater than object extent")

def check_extent_3d(extent, indices):
     for i_, j_, k_ in zip(*indices):
            if i_ < 0 or j_ < 0 or k_ < 0:
                raise PythonToolException("Index cannot be less than zero")
            if i_ >= extent.i or j_ >= extent.j or k_ >= extent.k:
                raise PythonToolException("Index cannot be greater than object extent")
            
def ijks_to_positions(
            extent,
            object_link, 
            indices: typing.Tuple[typing.List[float], typing.List[float], typing.List[float]],
            dimensions: int)\
            -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
    if dimensions == 3:
        check_extent_3d(extent, indices)
        [i, j, k] = indices
    elif dimensions == 2:
        check_extent_2d(extent, indices)
        [i, j] = indices[:2]
    else: 
        raise PythonToolException("ijks_to_positions called with unsupported number of dimensions")
    
    lst_x = []
    lst_y = []
    lst_z = []
    n = 1000
    for i_ in range(0, len(i), n):
        if dimensions == 3:
            data = object_link.GetPositions(i[i_:i_+n], j[i_:i_+n], k[i_:i_+n])
        elif dimensions == 2:
            data = object_link.GetPositions(i[i_:i_+n], j[i_:i_+n])
        lst_x.append(data[0])
        lst_y.append(data[1])
        lst_z.append(data[2])

    d = ([i for i_s in lst_x for i in i_s ], 
        [j for j_s in lst_y for j in j_s ], 
        [k for k_s in lst_z for k in k_s ])
    return d

def positions_to_ijks_2d(
        object_link,
        positions: typing.Union[typing.Tuple[typing.List[float], typing.List[float]], typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]])\
        -> typing.Tuple[typing.List[int], typing.List[int]]:
    if len(positions) == 2:
        positions = typing.cast(typing.Tuple[typing.List[float], typing.List[float]], positions)
        [x, y] = positions
    elif len(positions) == 3:
        positions = typing.cast(typing.Tuple[typing.List[float], typing.List[float], typing.List[float]], positions)
        [x, y, _] = positions
    lst_is = []
    lst_js = []
    n = 1000
    for i in range(0, len(x), n):
        data = object_link.GetIjk(x[i:i+n], y[i:i+n])
        lst_is.append(data[0])
        lst_js.append(data[1])
    d = ([int(round(i)) for i_s in lst_is for i in i_s ], 
        [int(round(j)) for js in lst_js for j in js ])
    return d

def positions_to_ijks_3d(
            object_link, 
            positions: typing.Tuple[typing.List[float], typing.List[float], typing.List[float]])\
            -> typing.Tuple[typing.List[int], typing.List[int], typing.List[int]]:            
        [x, y, z] = positions
        lst_is = []
        lst_js = []
        lst_ks = []
        n = 1000
        for i in range(0, len(x), n):
            data = object_link.GetIjk(x[i:i+n], y[i:i+n], z[i:i+n])
            lst_is.append(data[0])
            lst_js.append(data[1])
            lst_ks.append(data[2])
        d = ([int(round(i)) for i_s in lst_is for i in i_s ], 
            [int(round(j)) for js in lst_js for j in js ], 
            [int(round(k)) for ks in lst_ks for k in ks ])
        return d

def is_valid_guid(guid: str) -> bool:
    pattern = re.compile(
        r"^(?:[0-9a-fA-F]{32}|"                                                                 # 32-character hexadecimal string without dashes
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}|"         # with dashes
        r"\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}|"     # with dashes in braces
        r"\([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\)|"     # with dashes in parentheses
        r"\{0x[0-9a-fA-F]{8},0x[0-9a-fA-F]{4},0x[0-9a-fA-F]{4},\{0x[0-9a-fA-F]{2}," \
            r"0x[0-9a-fA-F]{2},0x[0-9a-fA-F]{2},0x[0-9a-fA-F]{2},0x[0-9a-fA-F]{2}," \
                r"0x[0-9a-fA-F]{2},0x[0-9a-fA-F]{2},0x[0-9a-fA-F]{2}\}\})$"                     # hex format
        )
    xml_pattern = re.compile(r"<\?xml\s+version=\"[^\"]+\"\s+encoding=\"[^\"]+\"\?>")  # xml format
    return bool(pattern.match(guid) or xml_pattern.match(guid))

def verify_continuous_clone(copy_values, template):
    if (copy_values and template is not None):
        raise UserErrorException('Cannot clone with template if copy_values=True')
    if (template is not None and not isinstance(template, Template)):
        raise UserErrorException('The template argument must be a Template object')
        
def verify_discrete_clone(copy_values, discrete_template):
    if (copy_values and discrete_template is not None):
        raise UserErrorException('Cannot clone with discrete_template if copy_values=True')
    if (discrete_template is not None and not isinstance(discrete_template, DiscreteTemplate)):
        raise UserErrorException('The discrete_template argument must be a DiscreteTemplate object')

def verify_globalwelllogfolder(folder):
    from cegalprizm.pythontool.globalwelllogfolder import GlobalWellLogFolder ## Import here to avoid circular import issues
    if folder is not None and not isinstance(folder, GlobalWellLogFolder):
        raise TypeError('The folder argument must be a GlobalWellLogFolder object')

def verify_folder(folder):
    from cegalprizm.pythontool import Folder  ## Import here to avoid circular import issues
    if folder is not None and not isinstance(folder, Folder):
        raise TypeError('The folder argument must be a Folder object')

def verify_clone_name(name_of_clone):
    if not name_of_clone or '/' in name_of_clone or not name_of_clone.strip() or has_special_whitespace(name_of_clone):
        raise ValueError('Name of clone cannot be empty, None, whitespace or contain slashes')

def has_special_whitespace(s: str) -> bool:
    return '\n' in s or '\r' in s or '\t' in s

def get_discrete_codes_dict(grpc_tuple: tuple) -> typing.Dict[int, str]:
    codes = {}
    for tup in grpc_tuple:
        key = tup.Item1
        value = tup.Item2
        codes[key] = value
    return codes

def convert_well_attribute_value(attribute):
    value = attribute.values[0]
    data_type = attribute.data_type

    converters = {
        0: lambda v: float(v) if v else None,
        1: lambda v: float(v) if v else None,
        2: lambda v: int(v) if v else None,
        3: lambda v: v,
        4: lambda v: datetime.datetime.strptime(v, "%Y/%m/%d/%H/%M/%S") if v else datetime.datetime(1, 1, 1, 0, 0),
        5: lambda v: bool(strtobool(v)) if v else None,
    }
    converter = converters.get(data_type, lambda v: v)
    try:
        return converter(value)
    except Exception:
        if data_type == 4:
            return pd.NaT
        return None

def get_valid_well_attributes(attributes, df, ignore_duplicates=False):
    df_columns = set(df.columns)
    flattened_attributes = []
    all_petrel_names = []

    for attr in attributes:
        if isinstance(attr, list):
            flattened_attributes.extend(attr)
            if ignore_duplicates:
                all_petrel_names.extend(sub_attr.petrel_name for sub_attr in attr)
        else:
            flattened_attributes.append(attr)
            if ignore_duplicates:
                all_petrel_names.append(attr.petrel_name)

    name_counts = None
    if ignore_duplicates:
        from collections import Counter
        name_counts = Counter(all_petrel_names)

    valid_attributes = []
    for attr in flattened_attributes:
        if ignore_duplicates and name_counts[attr.petrel_name] > 1:
            continue
        if not (attr.is_supported and attr._unique_name != "Name"):
            continue
        if attr._unique_name in df_columns or attr.petrel_name in df_columns:
            valid_attributes.append(attr)
    return valid_attributes

def map_well_attributes_to_columns(valid_attributes, df):
    attr_column_map = {}
    for attr in valid_attributes:
        if attr._unique_name in df.columns:
            attr_column_map[attr] = attr._unique_name
        elif attr.petrel_name in df.columns:
            attr_column_map[attr] = attr.petrel_name
    return attr_column_map

def get_and_validate_data_type(data_type: typing.Union[str, "NumericDataTypeEnum"], template: typing.Union["DiscreteTemplate", "Template"]) -> "NumericDataTypeEnum":
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
            raise ValueError(f"Invalid data_type: {data_type}. Must be 'continuous' or 'discrete'.")

    return data_type

def validate_template(template: typing.Union["DiscreteTemplate", "Template"], discrete: bool, type_name: str = ""):
    if not isinstance(template, (Template, DiscreteTemplate)) and template is not None:
        raise TypeError("Template must be a Template or DiscreteTemplate object")

    if discrete and isinstance(template, Template):
        raise ValueError(f"Cannot create a discrete {type_name} with a continuous template.")
    if not discrete and isinstance(template, DiscreteTemplate):
        raise ValueError(f"Cannot create a continuous {type_name} with a discrete template.")