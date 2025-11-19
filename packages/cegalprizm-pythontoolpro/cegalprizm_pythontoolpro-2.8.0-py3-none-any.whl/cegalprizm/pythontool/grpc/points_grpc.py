# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool.grpc import petrelinterface_pb2, utils
from cegalprizm.pythontool import _config
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from datetime import datetime
from math import ceil, isnan
from numbers import Number

import itertools
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.points_hub import PointsHub

class PointSetGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(PointSetGrpc, self).__init__(WellKnownObjectDescription.PointSet, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("PointsHub", petrel_connection._service_points)
        self._table_handler = PropertyTableHandler(self._guid, self._plink, self._channel, WellKnownObjectDescription.PointSet)
        self._property_range_handler = PropertyRangeHandler()
    
    def GetCrs(self):
        self._plink._opened_test()

        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._channel.PointSet_GetCrs(request)
             
        return response.value

    def GetPositionValuesByInds(self, indices):
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        request = petrelinterface_pb2.PetrelObjectGuidAndIndices(guid = po_guid, indices = indices)
        responses = self._channel.PointSet_GetPositionValuesByInds(request)
        return self._property_range_handler.get_dataframe(responses)
        
    def GetPropertiesValuesByInds(self, indices):
        self._plink._opened_test()
        po_guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        request = petrelinterface_pb2.PetrelObjectGuidAndIndices(guid = po_guid, indices = indices)
        responses = self._channel.PointSet_GetPropertiesValuesByInds(request)
        return self._property_range_handler.get_dataframe(responses)

    def GetPositionValuesByRange(self, start, end, step, xRange, yRange, zRange, maxNumberOfPoints):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuidAndRange(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            start = start,
            end = end,
            step = step,
            max_number_of_points = maxNumberOfPoints
        )
        if xRange is not None and len(xRange) == 2:
            request.x_range.x = xRange[0]
            request.x_range.y = xRange[1]
        if yRange is not None and len(yRange) == 2:
            request.y_range.x = yRange[0]
            request.y_range.y = yRange[1]
        if zRange is not None and len(zRange) == 2:
            request.z_range.x = zRange[0]
            request.z_range.y = zRange[1]

        responses = self._channel.PointSet_GetPositionValuesByRange(request)
        return self._property_range_handler.get_dataframe(responses)
    
    def _add_properties_request(self, properties):
        for (name, dtype) in properties:
            request = petrelinterface_pb2.AddProperty_request(
                guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
                name = name,
                type = dtype
            )
            yield request
    
    def AddProperties(self, properties):
        self._plink._opened_test()
        payloads = self._add_properties_request(properties)
        return self._channel.PointSet_AddProperties(payloads)
        
    def AttributesInfo(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        return self._channel.PointSet_AttributesInfo(request)

    def AddPoints(self, xs, ys, zs):
        self._plink._opened_test()
        request = petrelinterface_pb2.AddPoints_request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            xs = xs,
            ys = ys,
            zs = zs
        )
        return self._channel.PointSet_AddPoints(request).value

    def DeletePoints(self, indices):
        self._plink._opened_test()
        request = petrelinterface_pb2.DeletePoints_request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type), 
            indices = indices
        )
        return self._channel.PointSet_DeletePoints(request).value

    def SetPropertyValues(self, data_to_write):
        self._plink._opened_test()

        it = iter([])
        for (data, data_type) in data_to_write:
            it = itertools. chain(it, self._property_range_handler.get_property_range_datas(data.name, data.index.values, data.values, data_type = data_type))
        
        iterable_requests = (
            petrelinterface_pb2.SetPropertiesValues_Request(
                    guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type), 
                    data = prd
                    )
            for prd in it
        )
        ok = self._channel.PointSet_SetPropertyValues(iterable_requests)
        return ok.value

    def OrderedUniquePropertyNames(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        return self._channel.PointSet_OrderedUniquePropertyNames(request).values
        
    def GetPointCount(self) -> int:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)        
        return self._channel.PointSet_GetPointCount(request).value 

    def GetPropertyCount(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)        
        return self._channel.PointSet_GetPropertyCount(request).value

class PropertyRangeHandler(object):

    def __init__(self, number_of_streamed_elements = 1024):
        self.number_of_streamed_elements = number_of_streamed_elements

    def _point_property_type(self, value):
        import numpy as np
        import pandas as pd
        if utils.isFloat(value):
            prop_type = petrelinterface_pb2.PointPropertyType.DOUBLE_FLOAT
        elif isinstance(value, (bool, np.bool_)):
            prop_type = petrelinterface_pb2.PointPropertyType.BOOL
        elif isinstance(value, (int, np.int64, np.int32)):
            prop_type = petrelinterface_pb2.PointPropertyType.INT
        elif isinstance(value, (datetime, np.datetime64)):
            prop_type = petrelinterface_pb2.PointPropertyType.DATETIME
        elif isinstance(value, (str, np.str_)): 
            prop_type = petrelinterface_pb2.PointPropertyType.STRING
        elif isinstance(value, type(pd.NA)):
            # <NA> values in int columns
            prop_type = petrelinterface_pb2.PointPropertyType.INT
        else:
            raise Exception("Value is not recognized: Python type not matching any dotnet type.")
        return prop_type

    def get_dataframe(self, responses):
        import pandas as pd
        data = {}
        dtypes = {}
        for property_data in responses:
            indices = [int(v) for v in property_data.indices] #SLOW
            name = property_data.name
            string_values = property_data.values
            value_type = property_data.data_type
            converter = utils.get_from_grpc_converter(value_type)
            values = [converter(v) for v in string_values] #slow
            if name not in data:
                data[name] = {
                    "index" : indices,
                    "values" : values
                }
                dtypes[name] = value_type
            else:
                data[name]["index"] += indices
                data[name]["values"] += values
        
        df = None
        for key, val in data.items():
            if df is not None :
                df = pd.merge(df, pd.DataFrame({key:val["values"]}, index=val["index"]), left_index = True, right_index=True)
            else: 
                df = pd.DataFrame({key:val["values"]}, index=val["index"])

        df = self.cast_dataframe(df, dtypes)
        return df

    def cast_dataframe(self, df, dtypes):
        if df is None:
            return
        import numpy as np
        import pandas as pd
        for name in list(df):
            if dtypes[name] == petrelinterface_pb2.STRING:
                df[name] = df[name].astype(str)
            if dtypes[name] == petrelinterface_pb2.SINGLE_FLOAT or dtypes[name] == petrelinterface_pb2.DOUBLE_FLOAT:
                df[name] = df[name].astype(np.float64)
            if dtypes[name] == petrelinterface_pb2.INT:
                df[name] = df[name].astype(pd.Int64Dtype())
            if dtypes[name] == petrelinterface_pb2.BOOL:
                df[name] = df[name].astype(bool)
            if dtypes[name] == petrelinterface_pb2.DATETIME:
                df[name] = pd.to_datetime(df[name])
        return df


    def _serialize_value_to_string(self, value):
        import numpy as np
        import pandas as pd
        if utils.isFloat(value):
            float_string = str(value)
            if float_string == "nan":
                return "NaN"
            return float_string
        elif isinstance(value, (int, np.int64, np.int32)):
            return str(value)
        elif isinstance(value, type(pd.NA)):
            return str(_config._INT32MAXVALUE)
        elif isinstance(value, (str, np.str_)): 
            return str(value)
        elif isinstance(value, (bool, np.bool_)):
            return str(value)
        elif isinstance(value, (np.datetime64, datetime)):
            dt = pd.Timestamp(value)
            if pd.isnull(dt):
                ret = "1/1/1/0/0/0"
            else:
                ret = "{}/{}/{}/{}/{}/{}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            return ret
        elif value is None:
            return ""
        else:
            raise Exception("Value is not recognized")

    def chunk(self, lst, n):
        result = []
        for i in range(0, len(lst), n):
            start = i
            end = min(start+n, len(lst))
            result.append(lst[start:end])
        return result

    def get_property_range_datas(self, uniquePropertyName, indexes, vals, attribute_droid = "", data_type = None):
        data_type_for_property = data_type
        for _ind, _val in zip(self.chunk(indexes, self.number_of_streamed_elements), self.chunk(vals, self.number_of_streamed_elements)):
            if data_type_for_property is None:
                data_type_for_property = self.find_element_type_from_array(_val)
            yield petrelinterface_pb2.PropertyRangeData(
                name = uniquePropertyName,
                attributeDroid = attribute_droid,
                indices = _ind,
                values = [self._serialize_value_to_string(v) for v in _val],
                data_type = data_type_for_property
            )

    def find_element_type_from_array(self, values_array):
        current_type = None
        nan_found = False
        for item in values_array:
            ## Don't infer type from None or NaN values, move on to the next value
            if item is not None:
                if isinstance(item, Number) and isnan(item):
                    nan_found = True
                    continue
                else:
                    current_type = self._point_property_type(item)
                    break
        if current_type is not None:
            return current_type
        ## If we found only NaN values, use float type
        if nan_found:
            return self._point_property_type(float("nan"))
        ## If only None assume string
        return self._point_property_type("")

class PropertyTableHandler:
    def __init__(self, guid, plink, channel, sub_type):
        self._guid = guid
        self._plink = plink
        self._channel = channel
        self._sub_type = sub_type

    def setpoints_request(self, start_index, po_guid, xs, ys, zs, no_points_per_streamed_unit, idx = None, closed = False):
        part_xs = xs[start_index:(start_index + no_points_per_streamed_unit)]
        part_ys = ys[start_index:(start_index + no_points_per_streamed_unit)]
        part_zs = zs[start_index:(start_index + no_points_per_streamed_unit)]
        points = petrelinterface_pb2.Points(start_point_index = start_index)
        points.xs[:] = part_xs # pylint: disable=no-member
        points.ys[:] = part_ys # pylint: disable=no-member
        points.zs[:] = part_zs # pylint: disable=no-member
        
        if idx is not None:
            return petrelinterface_pb2.SetPolylinePoints_Request(
                guid = po_guid,
                points = points,
                index = idx,
                closed = closed
            )
        else:
            return petrelinterface_pb2.SetPoints_Request(
                guid = po_guid,
                points = points
            )
    
    def no_points_per_streamed_unit(self, no_points, max_size_bytes):
        max_no_points_per_streamed_unit = ceil(max_size_bytes / 100)
        no_parts = ceil(no_points/max_no_points_per_streamed_unit)
        return ceil(no_points/no_parts)