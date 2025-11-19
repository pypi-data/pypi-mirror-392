# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




import typing
import math
from cegalprizm.pythontool.chunk import Chunk
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithDomain, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory
from cegalprizm.pythontool.petrelobject import PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion, PetrelObjectWithParentFolder
from cegalprizm.pythontool.template import Template, DiscreteTemplate
from cegalprizm.pythontool.primitives import Extent, Annotation
from cegalprizm.pythontool.seismic import SeismicCube
from cegalprizm.pythontool import primitives
from cegalprizm.pythontool.chunktype import ChunkType
from cegalprizm.pythontool import _docstring_utils, _utils, horizoninterpretationutils
import cegalprizm.pythontool

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.horizoninterpretation_grpc import HorizonInterpretationGrpc, HorizonProperty3dGrpc, HorizonInterpretation3dGrpc
    from cegalprizm.pythontool import InterpretationFolder


class HorizonInterpretation(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithDomain, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion, PetrelObjectWithParentFolder):
    """A class holding information about a Horizon Interpretation"""
    def __init__(self, python_petrel_property: "HorizonInterpretationGrpc"):
        super(HorizonInterpretation, self).__init__(python_petrel_property)
        self._extent = None
        self._horizoninterpretation_object_link = typing.cast("HorizonInterpretationGrpc", python_petrel_property)

    @property
    def horizon_interpretation_3ds(self) -> typing.List["HorizonInterpretation3d"]:
        return [HorizonInterpretation3d(po) for po in self._horizoninterpretation_object_link.GetHorizonInterpretation3dObjects()]

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="HorizonInterpretation")
    def crs_wkt(self):
        return "Well-known text representation of coordinate reference systems not available for HorizonInterpretation objects."

    def __str__(self) -> str:
        """A readable representation of the HorizonInterpretation3D"""
        return 'HorizonInterpretation(petrel_name="{0}")'.format(self.petrel_name)

    @_docstring_utils.clone_docstring_decorator(return_type="HorizonInterpretation", respects_subfolders=True)
    def clone(self, name_of_clone: str, copy_values: bool = False) -> "HorizonInterpretation":
        return typing.cast("HorizonInterpretation", self._clone(name_of_clone, copy_values = copy_values))

    @property
    def parent_folder(self) -> typing.Union["InterpretationFolder"]:
        """Returns the parent folder of this HorizonInterpretation in Petrel.

        Returns:
            :class:`InterpretationFolder`: The parent folder of the HorizonInterpretation.

        **Example**:

        .. code-block:: python

            interpretation = petrel_connection.horizon_interpretations["Input/Seismic/Interpretations/HorizonInterpretation 1"]
            interpretation.parent_folder
            >> InterpretationFolder(petrel_name="Interpretations")
        """
        return self._parent_folder


class HorizonProperty3d(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    def __init__(self, python_petrel_property: "HorizonProperty3dGrpc"):
        super(HorizonProperty3d, self).__init__(python_petrel_property)
        self._extent: typing.Optional[Extent] = None
        self._horizonproperty3d_object_link = python_petrel_property
        self._shared_logic_helper = InterpretationSharedLogicHelper(self._horizonproperty3d_object_link, self)
        
    @property
    @horizoninterpretationutils.affine_transform_docstring_decorator
    def affine_transform(self):
        return self._shared_logic_helper.affine_transform

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="HorizonProperty3d")
    def crs_wkt(self):
        return self._horizonproperty3d_object_link.GetCrs()

    @property
    @horizoninterpretationutils.extent_docstring_decorator
    def extent(self) -> Extent:
        return self._shared_logic_helper.extent

    @horizoninterpretationutils.indices_docstring_decorator(object_name="horizon property", property_name="horizon_properties")
    def indices(self, x: float, y: float) -> primitives.Indices:
        return self._shared_logic_helper.indices(x, y)

    @horizoninterpretationutils.position_docstring_decorator(object_name="horizon property", property_name="horizon_properties")
    def position(self, i: int, j: int) -> primitives.Point:
        return self._shared_logic_helper.position(i, j)

    @horizoninterpretationutils.is_undef_value_docstring_decorator
    def is_undef_value(self, value: typing.Union[float, int]) -> bool:
        return self._shared_logic_helper._is_undef_value(value)

    @_docstring_utils.clone_docstring_decorator(return_type="HorizonProperty3d", respects_subfolders=True, continuous_template=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, template: "Template" = None) -> "HorizonProperty3d":
        _utils.verify_continuous_clone(copy_values, template)
        return typing.cast("HorizonProperty3d",self._clone(name_of_clone, copy_values = copy_values, template = template))

    @property
    @horizoninterpretationutils.undef_value_docstring_decorator
    def undef_value(self) -> float:
        return self._shared_logic_helper._undef_value()

    @property
    @horizoninterpretationutils.unit_symbol_docstring_decorator
    def unit_symbol(self) -> typing.Optional[str]:
        return self._shared_logic_helper._unit_symbol()

    @horizoninterpretationutils.chunk_all_docstring_decorator_horizon_property_3d_decorator
    def all(self) -> Chunk:
        return self._shared_logic_helper._make_chunk(i=None, j=None)

    @horizoninterpretationutils.chunk_docstring_decorator_horizon_property_3d_decorator
    def chunk(self, i: typing.Optional[typing.Tuple[int, int]] = None, j: typing.Optional[typing.Tuple[int, int]] = None) -> Chunk:
        return self._shared_logic_helper._make_chunk(i=i, j=j)

    def __str__(self) -> str:
        """A readable representation of the HorizonProperty3D"""
        return 'HorizonProperty3D(petrel_name="{0}")'.format(self.petrel_name)

    def positions_to_ijks(self, positions: typing.Union[typing.Tuple[typing.List[float], typing.List[float]], typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]])\
            -> typing.Tuple[typing.List[int], typing.List[int]]:
        """
        Converts lists of X and Y coordinates to I, J indices of the horizon property.

        The input coordinates represent positions in world coordinates. The returned indices correspond to the nearest seismic bin (cell) centers on the underlying seismic grid.
        
        The length of the output lists is determined by the length of the input [x] list. It is possible to provide a [y] list with more items than the [x] list, but no output is calculated for the extra items. Providing a [y] list with fewer items than the [x] list will raise an exception.

        Multiple positions may be located near the same seismic bin (cell), in which case the same ij indices will be returned for those positions.

        Note:
            When coordinates fall outside the spatial extent of the HorizonProperty3D, the returned I, J values represent the extrapolated grid positions based on the HorizonProperty3D's underlying seismic bin (cell) geometry. Both negative indices and positive indices greater than the object extent may be returned.

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

        Args:
            positions (tuple(list[float], list[float])): A tuple([x],[y]) are lists of coordinates in world units. The tuple may optionally contain a third list [z], although these values will not be used in the conversion.

        Returns:
            tuple(list[float], list[float]): A tuple([i],[j]) where [i] and [j] are lists of bin (cell) indices corresponding to the nearest seismic bin (cell) centers.

        Raises:
            UnexpectedErrorException: If the [y] list contains fewer items than the [x] list.

        **Example**:

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            hor = petrel.horizon_properties.get_by_name("Horizon Property 1")
            hor.positions_to_ijks(([451199.85, 451210.85], [6780362.88, 6780373.88]))
            >> ([0, 1], [1, 2])
        """
        return _utils.positions_to_ijks_2d(self._horizonproperty3d_object_link, positions)
    
    def ijks_to_positions(self, indices: typing.Tuple[typing.List[float], typing.List[float]]) -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        """
        Converts I, J indices to X, Y, Z coordinates for the specified horizon property.

        The input indices (i, j) represent seismic bins (cells) on the underlying seismic grid.
        The returned coordinates correspond to the centers of those bins (cells) in world coordinates. The K index is ignored for horizon properties.

        The length of the output lists is determined by the length of the input [i] list. It is possible to provide a [j] list with more items than the [i] list, but no output is calculated for the extra items. Providing a [j] list with fewer items than the [i] list will raise an exception.

        Note:
            The returned positions are the center of the seismic bin (cell) defined by the ij indices. This means a conversion from positions to ijs and back to positions may not always return the exact original positions.

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

        Args:
            indices (tuple(list[int], list[int])): A tuple([i],[j]) where [i] and [j] are lists of bin (cell) indices.

        Returns:
            tuple (list[float], list[float], list[float]): A tuple([x],[y],[z]) where [x], [y], and [z] are lists of world-coordinate positions corresponding to the bin (cell) centers.

        Raises:
            PythonToolException: If any of the I, J indices are outside the horizon property extent.
            UnexpectedErrorException: If the [j] list contains fewer items than the [i] list.

        **Example**:

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            hor = petrel.horizon_properties.get_by_name("Horizon Property 1")
            hor.ijks_to_positions(([0, 1], [1, 1]))
            >> ([451199.85, 451210.85], [6780362.88, 6780373.88], [-1875.4, -1876.1])

        """
        return _utils.ijks_to_positions(extent = self.extent, 
                                        object_link = self._horizonproperty3d_object_link, 
                                        indices = indices, 
                                        dimensions = 2)

    @property
    def horizon_interpretation_3d(self) -> "HorizonInterpretation3d":
        """The parent 3d horizon interpretation of the horizon property.

        Returns:
            cegalprizm.pythontool.HorizonInterpretation3d: The parent grid of the property
        """   
        return HorizonInterpretation3d(self._horizonproperty3d_object_link.GetParentHorizonInterpretation3d())

    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

class HorizonInterpretation3d(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    def __init__(self, interpretation_3d_grpc: "HorizonInterpretation3dGrpc"):
        super(HorizonInterpretation3d, self).__init__(interpretation_3d_grpc)
        self._extent = None
        self._horizoninterpretation3d_object_link = interpretation_3d_grpc
        self._shared_logic_helper = InterpretationSharedLogicHelper(self._horizoninterpretation3d_object_link, self)
        
    def __str__(self) -> str:
        """A readable representation of the HorizonInterpretation3d"""
        return 'HorizonInterpretation3D(petrel_name="{0}")'.format(self.petrel_name)

    @property
    @horizoninterpretationutils.affine_transform_docstring_decorator
    def affine_transform(self):
        return self._shared_logic_helper.affine_transform

    @property
    @_docstring_utils.crs_wkt_decorator(object_type="HorizonInterpretation3d")
    def crs_wkt(self):
        return self._horizoninterpretation3d_object_link.GetCrs()

    @property
    @horizoninterpretationutils.extent_docstring_decorator
    def extent(self) -> Extent:
        return self._shared_logic_helper.extent

    @horizoninterpretationutils.position_docstring_decorator(object_name="horizon interpretation", property_name="horizon_interpretation_3ds")
    def position(self, i: int, j: int) -> primitives.Point:
        return self._shared_logic_helper.position(i, j)

    @horizoninterpretationutils.is_undef_value_docstring_decorator
    def is_undef_value(self, value: typing.Union[float, int]) -> bool:
        return self._shared_logic_helper._is_undef_value(value)

    @property
    @horizoninterpretationutils.undef_value_docstring_decorator
    def undef_value(self) -> float:
        return self._shared_logic_helper._undef_value()

    @property
    def sample_count(self) -> int:
        """The number of samples contained in the Horizon Interpretation 3d object.

        Returns:
            int: The number of points in the interpretation.
        """        
        return self._horizoninterpretation3d_object_link.SampleCount()

    @property
    def horizon_interpretation(self) -> HorizonInterpretation:
        """Returns the parent Horizon interpretation of the 3d horizon interpretation grid."""            
        return HorizonInterpretation(self._horizoninterpretation3d_object_link.GetParent())

    @property
    def horizon_property_3ds(self) -> typing.List[HorizonProperty3d]:
        """A readonly iterable collection of the 3d horizon interpretation properties for the 3d horizon interpretation grid 
        
        Returns:
            cegalprizm.pythontool.HorizonProperties:the 3d horizon interpretation properties
              for the 3d horizon interpretation grid"""
        return [
            HorizonProperty3d(po)
            for po in self._horizoninterpretation3d_object_link.GetAllHorizonPropertyValues()
        ]

    @_docstring_utils.clone_docstring_decorator(return_type="HorizonInterpretation3d", respects_subfolders=True)
    def clone(self, name_of_clone: str, copy_values: bool = False) -> "HorizonInterpretation3d":
        return typing.cast("HorizonInterpretation3d", self._clone(name_of_clone, copy_values = copy_values))

    def positions_to_ijks(self, positions: typing.Union[typing.Tuple[typing.List[float], typing.List[float]], typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]])\
            -> typing.Tuple[typing.List[int], typing.List[int]]:
        """
        Converts lists of X and Y coordinates to I, J indices of the horizon interpretation grid.

        The input coordinates represent positions in world coordinates. The returned indices correspond to the nearest seismic bin (cell) centers on the underlying seismic grid.
        
        The length of the output lists is determined by the length of the input [x] list. It is possible to provide a [y] list with more items than the [x] list, but no output is calculated for the extra items. Providing a [y] list with fewer items than the [x] list will raise an exception.

        Multiple positions may be located near the same seismic bin (cell), in which case the same ij indices will be returned for those positions.

        Note:
            When coordinates fall outside the spatial extent of the HorizonInterpretation3D, the returned I, J values represent the extrapolated grid positions based on the HorizonInterpretation3Ds underlying seismic bin (cell) geometry. Both negative indices and positive indices greater than the object extent may be returned.

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

        Args:
            positions (tuple(list[float], list[float])): A tuple([x],[y]) where are lists of coordinates in world units. The tuple may optionally contain a third list [z], although these values will not be used in the conversion.

        Returns:
            tuple(list[float], list[float]): A tuple([i],[j]) where [i] and [j] are lists of bin (cell) indices corresponding to the nearest seismic bin (cell) centers.

        Raises:
            UnexpectedErrorException: If the [y] list contains fewer items than the [x] list.

        **Example**:

        .. code-block:: python

            from cegalprizm.pythontool import PetrelConnection
            petrel = PetrelConnection()
            hor = petrel.horizon_interpretation_3ds.get_by_name("Horizon Interpretation")
            hor.positions_to_ijks(([451199.85, 451210.85], [6780362.88, 6780373.88]))
            >> ([0, 1], [1, 2])
        """
        return _utils.positions_to_ijks_2d(self._horizoninterpretation3d_object_link, positions)
    
    def ijks_to_positions(self, indices: typing.Tuple[typing.List[float], typing.List[float]]) -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        """
        Converts I, J indices to X, Y, Z coordinates for the specified horizon interpretation.

        The input indices (i, j) represent seismic bins (cells) on the underlying seismic grid.
        The returned coordinates correspond to the centers of those bins (cells) in world coordinates. The K index is ignored for horizon interpretations.
        
        The length of the output lists is determined by the length of the input [i] list. It is possible to provide a [j] list with more items than the [i] list, but no output is calculated for the extra items. Providing a [j] list with fewer items than the [i] list will raise an exception.

        Note:
            The returned positions are the center of the seismic bin (cell) defined by the ij indices. This means a conversion from positions to ijs and back to positions may not always return the exact original positions.

        Note:
            Python Tool Pro I, J indices are 0-based, while in Petrel they are 1-based. For example, a bin (cell) identified as (i = 4, j = 5) in Python corresponds to (i = 5, j = 6) in Petrel.

        Args:
            indices (tuple(list[int], list[int])): A tuple([i],[j]) where [i] and [j] are lists of bin (cell) indices.

        Returns:
            tuple(list[float], list[float], list[float]): A tuple([x],[y],[z]) where [x], [y], and [z] are lists of world-coordinate positions corresponding to the bin (cell) centers.

        Raises:
            PythonToolException: If any of the I, J indices are outside the horizon interpretation extent.
            UnexpectedErrorException: If the [j] list contains fewer items than the [i] list.
        """
        return _utils.ijks_to_positions(extent = self.extent, 
                                        object_link = self._horizoninterpretation3d_object_link, 
                                        indices = indices, 
                                        dimensions = 2)

    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

    @horizoninterpretationutils.chunk_docstring_decorator_horizon_interp_3d_decorator
    def chunk(self, i: typing.Optional[typing.Tuple[int, int]] = None, j: typing.Optional[typing.Tuple[int, int]] = None) -> Chunk:
        return self._shared_logic_helper._make_chunk(i=i, j=j)

    @horizoninterpretationutils.chunk_all_docstring_decorator_horizon_interp_3d_decorator
    def all(self) -> Chunk:
        return self._shared_logic_helper._make_chunk(i=None, j=None)

    @horizoninterpretationutils.indices_docstring_decorator(object_name="horizon interpretation", property_name="horizon_interpretation_3ds")
    def indices(self, x: float, y: float) -> primitives.Indices:
        return self._shared_logic_helper.indices(x, y)

    @property
    @horizoninterpretationutils.unit_symbol_docstring_decorator
    def unit_symbol(self) -> typing.Optional[str]:
        return self._shared_logic_helper._unit_symbol()

    def annotations(self, i: typing.Union[int, typing.List[int]], j: typing.Union[int, typing.List[int]], reference_cube: "SeismicCube") -> typing.Union["Annotation", typing.List["Annotation"], None]:
        """Get the annotation(s) for the specified i, j index/indices based on the provided seismic cube. This allows determining the inline and xline of the horizon grid indices in the seismic cube's geometry.
        The method will convert the provided i, j values to real-world coordinates and match this position to the seismic cube's geometry in order to determine the corresponding inline and xline values.
        Input may be provided as single integer values or as lists of integers. If lists are provided, they must be of the same length. The method will return a single Annotation object if single integer values are provided, or a list of Annotation objects if lists are provided.

        Note:
            Depending on the relative position of the HorizonInterpretation3d and the reference SeismicCube, the provided i, j indices may be outside the bounds of either the HorizonInterpretation3D or the SeismicCube. In this case None is returned instead of an Annotation object.

        Args:
            i (int or List[int]): The i index or list of i indices in the horizon grid.
            j (int or List[int]): The j index or list of j indices in the horizon grid.
            reference_cube (SeismicCube): The :class:`SeismicCube` used to determine the inline and xline values.
        
        Returns:
            Annotation or List[Annotation]: The corresponding :class:`Annotation` object(s) with inline and xline values, or None if the i, j index is outside the bounds of either the HorizonInterpretation3D or the SeismicCube. The sample property of the Annotation(s) will always be set to None.

        Raises:
            ValueError: If the length of i and j inputs do not match.
            TypeError: If any of the values in the i or j inputs are not integers.
            TypeError: If reference_cube is not a :class:`SeismicCube` object.

        **Example**:

        Get a single annotation for a specific i, j index:

        .. code-block:: python

            interp = petrellink.horizon_interpretation_3ds.get_by_name('Interpretation 3')
            cube = petrellink.seismic_cubes.get_by_name('Cube 2')
            single_annotation = interp.annotations(12, 12, cube)
            print(single_annotation.inline)
            >> 28

        **Example**:

        Get annotations for multiple i, j indices:

        .. code-block:: python

            interp = petrellink.horizon_interpretation_3ds.get_by_name('Interpretation 3')
            cube = petrellink.seismic_cubes.get_by_name('Cube 2')
            annotations_list = interp.annotations(i = [2, 6, 10, 19, 28], j = [33, 25, 17, 8, 2], reference_cube = cube)
            first_annotation = annotations_list[0]
            print(first_annotation.xline)
            >> 12
        
        """
        i = i if isinstance(i, list) else [i]
        j = j if isinstance(j, list) else [j]
        
        if len(i) != len(j):
            raise ValueError("Length of i and j must be the same.")
        
        for idx in i:
            if not isinstance(idx, int):
                raise TypeError("All values in i must be integers.")
        for idx in j:
            if not isinstance(idx, int):
                raise TypeError("All values in j must be integers.")

        if not isinstance(reference_cube, cegalprizm.pythontool.SeismicCube):
            raise TypeError("reference_cube must be a SeismicCube object.")
        
        idx3s = self._horizoninterpretation3d_object_link.IndicesToAnnotations(i, j, reference_cube._seismiccube_object_link)
        annotations = []
        for idx3 in idx3s:
            if idx3 is None:
                annotations.append(None)
            else:
                annotations.append(Annotation(idx3.GetValue().I, idx3.GetValue().J, idx3.GetValue().K))
        return annotations if len(annotations) > 1 else annotations[0]


class InterpretationSharedLogicHelper():
    def __init__(self, grpc_object_link, python_petrel_object):
        self._extent: typing.Optional[Extent] = None
        self._object_link = grpc_object_link
        self._python_petrel_object = python_petrel_object

    @property
    def affine_transform(self):
        return _utils.from_backing_arraytype(
            self._object_link.GetAffineTransform()
        )

    def indices(self, x: float, y: float) -> primitives.Indices:
        index2 = self._object_link.IndexAtPosition(x, y)
        if index2 is None:
            raise ValueError("Position not in horizon property")
        if (
            index2 is None
            or index2.GetValue().I < 0
            or index2.GetValue().J < 0
            or index2.GetValue().I >= self.extent.i
            or index2.GetValue().J >= self.extent.j
        ):
            raise ValueError("Position not in horizon property")
        return primitives.Indices(index2.GetValue().I, index2.GetValue().J, None)

    @property
    def extent(self) -> Extent:
        if self._extent is None:
            i = self._object_link.NumI()
            j = self._object_link.NumJ()
            self._extent = Extent(i=i, j=j, k=1)

        return self._extent

    def position(self, i: int, j: int) -> primitives.Point:
        point3 = self._object_link.PositionAtIndex(i, j)
        if point3 is None:
            raise ValueError("Index not valid for interpretation")
        return primitives.Point(
            point3.GetValue().X, point3.GetValue().Y, point3.GetValue().Z
        )

    def _is_undef_value(self, value: typing.Union[float, int]) -> bool:
        return math.isnan(value)

    def _unit_symbol(self) -> typing.Optional[str]:
        return _utils.str_or_none(self._object_link.GetDisplayUnitSymbol())

    def _undef_value(self) -> float:
        return float("nan")

    def _make_chunk(self, i=None, j=None) -> "cegalprizm.pythontool.Chunk":
        value_getters = {
            ChunkType.k: lambda i, j, k: _utils.from_backing_arraytype(
                self._object_link.GetChunk(i, j)
            )
        }
        value_setters = {
            ChunkType.k: lambda i, j, k, values: self._object_link.SetChunk(
                i, j, _utils.to_backing_arraytype(values)
            )
        }
        value_shapers = {
            ChunkType.k: lambda i, j, k, values: _utils.ensure_2d_float_array(
                values, i, j
            )
        }
        value_accessors = {ChunkType.k: lambda i, j, k: _utils.native_accessor((i, j))}

        return Chunk(
            i,
            j,
            None,
            self._python_petrel_object,
            self.extent,
            value_getters,
            value_setters,
            value_shapers,
            value_accessors,
            (True, True, False),
            ChunkType.k,
            readonly=self._python_petrel_object.readonly,
        )