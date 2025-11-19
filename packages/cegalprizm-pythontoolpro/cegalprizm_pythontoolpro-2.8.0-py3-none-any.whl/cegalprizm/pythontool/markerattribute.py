# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import pandas as pd
import numpy as np
import typing
from cegalprizm.pythontool.markerstratigraphy import MarkerStratigraphy
from cegalprizm.pythontool.borehole import Well
from cegalprizm.pythontool import exceptions, PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion
from cegalprizm.pythontool.template import Template, DiscreteTemplate
from cegalprizm.pythontool import _docstring_utils
from typing import List
from warnings import warn

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.markerattribute_grpc import MarkerAttributeGrpc
    from cegalprizm.pythontool.markercollection import MarkerCollection

class MarkerAttribute(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    """A class holding information about a MarkerAttribute"""

    def __init__(self, petrel_object_link: "MarkerAttributeGrpc", parent_markercollection: "MarkerCollection" = None):
        super(MarkerAttribute, self).__init__(petrel_object_link)
        self._markerattribute_object_link = petrel_object_link
        self._parent_markercollection = petrel_object_link.GetAttributeParent() if parent_markercollection is None else parent_markercollection
        self._unique_name = petrel_object_link._unique_name
        self._droid = petrel_object_link._guid

    def __str__(self) -> str:
        """A readable representation"""
        return 'MarkerAttribute(unique_name="{0}")'.format(self._unique_name)

    def __repr__(self) -> str:
        return str(self)

    def _get_name(self) -> str:
        return self._unique_name

    def retrieve_stats(self) -> typing.Dict[str, str]:
        """Due to limitations in the Ocean API, this function is not implemented for MarkerAttribute objects.

        Returns:
            Dictionary: An empty dictionary.
        """
        return self._markerattribute_object_link.RetrieveStats()

    def as_dataframe(self, 
                     include_unconnected_markers: bool = True, 
                     marker_stratigraphy: MarkerStratigraphy = None, 
                     well: Well = None, 
                     wells_filter: List[Well] = None,
                     marker_stratigraphies_filter: List[MarkerStratigraphy] = None) -> pd.DataFrame:
        """ Gets a dataframe with information about a MarkerAttribute in the MarkerCollection. 

        Args:
            include_unconnected_markers: Flag to include markers where the borehole does not exist in the project. Defaults to true.
            marker_stratigraphy: WARNING: This argument will be removed in the future. Use marker_stratigraphies_filter instead. Limit dataframe to include only markers for one specified MarkerStratigraphy (as returned my markercollection.stratigraphies). Defaults to None.
            well: WARNING: This argument will be removed in the future. Use wells_filter instead. Limit dataframe to include only markers for a specified Well (as returned by petrelconnection.wells). Defaults to None.
            wells_filter: Limit dataframe to include a subset of some Wells by supplying a list of :class:`Well`. By default this is None which will return data for all Wells.
            marker_stratigraphies_filter: Limit dataframe to include a subset of some MarkerStratigraphies by supplying a list of :class:`MarkerStratigraphy`. By default this is None which will return data for all MarkerStratigraphies.

        Returns:
            Dataframe: A dataframe with MarkerAttribute information together with Petrel index, Well identifier and Surface information. 

        **Example**:

        Get a dataframe with attribute information for all Markers in the MarkerCollection

        .. code-block:: python

            mc = petrelconnection.markercollections["Input/Path/To/MarkerCollection"]
            attribute = mc.attributes["My Attribute"]
            df = attribute.as_dataframe()
        
        **Example**:

        Get a dataframe with attribute information for a specific well and two stratigraphies

        .. code-block:: python

            my_well = petrelconnection.wells["Input/Path/To/Well"]
            mc = petrelconnection.markercollections["Input/Path/To/MarkerCollection"]
            strat1 = mc.stratigraphies["First Stratigraphy"]
            strat2 = mc.stratigraphies["Second Stratigraphy"]
            attribute = mc.attributes["My Attribute"]
            df = attribute.as_dataframe(wells_filter=[my_well], marker_stratigraphies_filter=[strat1, strat2])
        """
        if marker_stratigraphy is not None:
            warn("The 'marker_stratigraphy' argument is deprecated and will be removed in Python Tool Pro version 3.0. Use 'marker_stratigraphies_filter' instead.", DeprecationWarning, stacklevel=2)
        if well is not None:
            warn("The 'well' argument is deprecated and will be removed in Python Tool Pro version 3.0. Use 'wells_filter' instead.", DeprecationWarning, stacklevel=2)
        if marker_stratigraphy is not None and marker_stratigraphies_filter is not None:
            raise ValueError("The marker_stratigraphy and marker_stratigraphies_filter arguments cannot be used at the same time")
        if well is not None and wells_filter is not None:
            raise ValueError("The well and wells_filter arguments cannot be used at the same time")

        if marker_stratigraphies_filter is None and marker_stratigraphy is not None:
            marker_stratigraphies_filter = [marker_stratigraphy]

        if wells_filter is None and well is not None:
            wells_filter = [well]

        df = self._parent_markercollection._as_dataframe_for_attribute(self._droid, include_unconnected_markers, marker_stratigraphies_filter, wells_filter)
        return df

    def as_array(self, include_unconnected_markers: bool = True, marker_stratigraphy: MarkerStratigraphy = None, well: Well = None) -> 'np.array':
        """ Gets a numpy array with the values for MarkerAttribute in the MarkerCollection. 
        
        Args:
            include_unconnected_markers: Flag to include markers where the borehole does not exist in the project. Defaults to true.
            marker_stratigraphy: Limit array to include only markers for one specified MarkerStratigraphy (as returned my markercollection.stratigraphies). Defaults to None.
            well: Limit array to include only markers for a specified Well (as returned by petrelconnection.wells). Defaults to None.

        Returns:
            Array: A numpy array with the values for the MarkerAttribute.
        """
        array = self._parent_markercollection._as_array_for_attribute(self._droid, include_unconnected_markers, marker_stratigraphy, well)
        return array

    def set_values(self, data: 'np.array', include_unconnected_markers: bool = True, marker_stratigraphy: MarkerStratigraphy = None, well: Well = None) -> None:
        """Attribute values are written to Petrel. The data parameter must be a numpy array.
           The length of the array must match the number of selected markers in the markercollection.

        Args:
            data: A numpy array of attributes with format as returned by as_array() 
            include_unconnected_markers: A boolean flag to include markers where the borehole does not exist in the project. Defaults to True.
            marker_stratigraphy: Limit array to include only markers for one specified MarkerStratigraphy (as returned my markercollection.stratigraphies). Defaults to None.
            well: Limit array to include only markers for a specified Well (as returned by petrelconnection.wells). Defaults to None.

        Raises:
            PythonToolException: if the parent MarkerCollection is read-only
            ValueError: if the data input is empty

        **Example**:

        Set a new numpy array as the values of a specified attribute and write the new data back to Petrel.

        .. code-block:: python

          import numpy as np
          new_attribute_values = np.array([1.1, 2.2, 3.3])
          my_attribute = markercollection.attributes['my attribute']
          my_attribute.set_values(new_attribute_values, False)
        """
        if self._parent_markercollection.readonly:
            raise exceptions.PythonToolException("MarkerCollection is readonly")

        if len(data) < 1:
            raise ValueError("Input array does not contain any values")
        
        return self._parent_markercollection._set_values_for_attribute(self._droid, data, include_unconnected_markers, marker_stratigraphy, well)

    @property
    def markercollection(self):
        """Returns the :class:`MarkerCollection` that this MarkerAttribute belongs to."""
        return self._parent_markercollection
    
    @_docstring_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()