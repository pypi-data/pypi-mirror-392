# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




import typing
from cegalprizm.pythontool import PetrelObject, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion
from cegalprizm.pythontool.exceptions import PythonToolException
from .stratigraphyzone import StratigraphyZone
from enum import Enum

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.markerstratigraphy_grpc import MarkerStratigraphyGrpc
    from cegalprizm.pythontool.markercollection import MarkerCollection

class HorizonTypeEnum(Enum):
    """An enumeration of the different types of horizons in the context of a MarkerStratigraphy"""

    Conformable = "Conformable"
    Erosional = "Erosional"
    Base = "Base"
    Discontinuous = "Discontinuous"

class MarkerStratigraphy(PetrelObject, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    """A class holding information about a MarkerStratigraphy"""

    def __init__(self, petrel_object_link: "MarkerStratigraphyGrpc", parent_markercollection: "MarkerCollection" = None):
        super(MarkerStratigraphy, self).__init__(petrel_object_link)
        self._markerstratigraphy_object_link = petrel_object_link
        self._parent_markercollection = petrel_object_link.GetStratigraphyParent() if parent_markercollection is None else parent_markercollection
        self._unique_name = petrel_object_link._unique_name
        self._droid = petrel_object_link._guid

    def __str__(self) -> str:
        """A readable representation"""
        return 'MarkerStratigraphy("{0}")'.format(self._unique_name)

    def __repr__(self) -> str:
        return str(self)

    def _get_name(self) -> str:
        return self._unique_name

    @property
    def markercollection(self):
        """The parent MarkerCollection of the MarkerStratigraphy"""
        return self._parent_markercollection

    @property
    def is_horizon(self) -> bool:
        """Boolean value indicating if the MarkerStratigraphy is a horizon. Returns True if it is a horizon, False otherwise."""
        return self._markerstratigraphy_object_link.IsHorizon()

    @property
    def horizon_type(self) -> str:
        """The type of the horizon for the MarkerStratigraphy, corresponding to the 'Horizon type' dropdown selection in the Petrel settings UI.
        The output is a string. When setting the value, then input can be either a string or a HorizonTypeEnum. 
        It is not possible to get or set the value if the MarkerStratigraphy is not a horizon, this can be checked using the is_horizon property.

        **Example**:

        Retrieve the horizon type:

        .. code-block:: python

            horizon = petrel_connection.MarkerCollections["Input/WellTops"].stratigraphies["MyHorizon"]
            print(horizon.horizon_type)
            >> "Conformable"

        **Example**:

        Set the horizon type using a string:

        .. code-block:: python

            horizon = petrel_connection.MarkerCollections["Input/WellTops"].stratigraphies["MyHorizon"]
            horizon.horizon_type = "Erosional"

        **Example**:

        Set the horizon type using a HorizonTypeEnum:

        .. code-block:: python

            from cegalprizm.pythontool import HorizonTypeEnum
            horizon = petrel_connection.MarkerCollections["Input/WellTops"].stratigraphies["MyHorizon"]
            horizon.horizon_type = HorizonTypeEnum.Erosional

        Args:
            horizon_type (str): The type of the horizon. Valid types are "Conformable", "Erosional", "Base", "Discontinuous".
            horizon_type (HorizonTypeEnum): The type of the horizon. Import HorizonTypeEnum from cegalprizm.pythontool to use this option.

        Returns:
            str: The type of the horizon. Possible values are "Conformable", "Erosional", "Base", "Discontinuous". If the MarkerStratigraphy is not a horizon an empty string is returned.

        Raises:
            UserWarning: If the MarkerStratigraphy is not a horizon. Use the is_horizon property to check if the MarkerStratigraphy is a horizon before trying to read or write the value.
            PythonToolException: If the MarkerStratigraphy is readonly.
            TypeError: If the input is not a string or a HorizonTypeEnum.

         Returns a string indicating the type of the horizon. Valid types are \"Conformable\", \"Erosional\", \"Base\", \"Discontinuous\""""
        return self._markerstratigraphy_object_link.GetHorizonType()

    @horizon_type.setter
    def horizon_type(self, horizon_type: typing.Union [str, HorizonTypeEnum]):
        if self.readonly:
            raise PythonToolException("MarkerStratigraphy is readonly")
        if not isinstance(horizon_type, (str, HorizonTypeEnum)):
            raise TypeError("horizon_type must be either a string or an instance of HorizonTypeEnum")
        if isinstance(horizon_type, HorizonTypeEnum):
            horizon_type = horizon_type.value
        self._markerstratigraphy_object_link.SetHorizonType(horizon_type)

    @property
    def parent_zone(self) -> "StratigraphyZone":
        """The parent zone of the StratigraphyHorizon as a :class:`StratigraphyZone` object.
        It is not possible to get parent zone if the MarkerStratigraphy is not a horizon, this can be checked using the is_horizon property.
        
        Returns:
            StratigraphyZone: The parent zone of the StratigraphyHorizon as a :class:`StratigraphyZone` object. If the MarkerStratigraphy is not a horizon, or it is a top level horizon, None is returned.

        Raises:
            UserWarning: If the MarkerStratigraphy is not a horizon. Use the is_horizon property to check if the MarkerStratigraphy is a horizon before trying to read the value.
        """
        parent_guid = self._parent_markercollection._markercollection_object_link._guid
        grpc = self._markerstratigraphy_object_link.GetStratigraphyHorizonParentZone(parent_guid)
        if grpc:
            return StratigraphyZone(grpc, self._parent_markercollection)
        else:
            return None