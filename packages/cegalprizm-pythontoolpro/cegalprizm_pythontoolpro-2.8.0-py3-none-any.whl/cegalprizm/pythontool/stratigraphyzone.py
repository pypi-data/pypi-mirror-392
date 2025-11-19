# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




import typing
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from cegalprizm.pythontool import PetrelObject, PetrelObjectWithPetrelNameSetter
import cegalprizm.pythontool.markerstratigraphy as markerstratigraphy

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.stratigraphyzone_grpc import StratigraphyZoneGrpc
    from cegalprizm.pythontool.markercollection import MarkerCollection
    from cegalprizm.pythontool.markerstratigraphy import MarkerStratigraphy

class StratigraphyZone(PetrelObject, PetrelObjectWithPetrelNameSetter):
    """A class holding information about a StratigraphyZone in the context of a MarkerCollection"""

    def __init__(self, petrel_object_link: "StratigraphyZoneGrpc", parent_markercollection: "MarkerCollection" = None):
        super(StratigraphyZone, self).__init__(petrel_object_link)
        self._stratigraphyzone_object_link = petrel_object_link
        self._parent_markercollection = petrel_object_link.GetStratigraphyParent() if parent_markercollection is None else parent_markercollection
        self._unique_name = petrel_object_link._unique_name
        self._droid = petrel_object_link._guid

    def __str__(self) -> str:
        """A readable representation"""
        return 'StratigraphyZone("{0}")'.format(self._unique_name)

    def __repr__(self) -> str:
        return str(self)

    def _get_name(self) -> str:
        return self._unique_name

    @property
    def markercollection(self):
        """Returns the :class:`MarkerCollection` that this StratigraphyZone belongs to."""
        return self._parent_markercollection

    @property
    def parent_zone(self) -> "StratigraphyZone":
        """The parent zone of the StratigraphyZone as a :class:`StratigraphyZone` object.
        
        Returns:
            StratigraphyZone: The parent zone of the StratigraphyZone as a :class:`StratigraphyZone` object. If the StratigraphyZone is a top-level zone, None is returned.
        """
        parent_guid = self._parent_markercollection._markercollection_object_link._guid
        grpc = self._stratigraphyzone_object_link.GetStratigraphyZoneParentZone(parent_guid)
        if grpc:
            return StratigraphyZone(grpc, self._parent_markercollection)
        else:
            return None

    @property
    def children(self) -> typing.Iterable[typing.Union["StratigraphyZone", "MarkerStratigraphy"]]:
        """The children of the StratigraphyZone as a list of :class:`StratigraphyZone` and :class:`MarkerStratigraphy` objects.
        Note that this property only returns the first level children of the StratigraphyZone, and does not recursively return any children of the children.

        Returns:
            typing.Iterable[typing.Union["StratigraphyZone", "MarkerStratigraphy"]]: The children of the StratigraphyZone as a list of :class:`StratigraphyZone` and :class:`MarkerStratigraphy` objects. If the StratigraphyZone has no children, and empty list is returned.
        """
        parent_guid = self._parent_markercollection._markercollection_object_link._guid
        grpcs = self._stratigraphyzone_object_link.GetStratigraphyZoneChildren(parent_guid)
        children = []
        if len(grpcs) > 0:
            for grpc in grpcs:
                if grpc._sub_type == WellKnownObjectDescription.MarkerStratigraphyZone:
                    children.append(StratigraphyZone(grpc, self._parent_markercollection))
                elif grpc._sub_type == WellKnownObjectDescription.MarkerStratigraphyHorizon:
                    children.append(markerstratigraphy.MarkerStratigraphy(grpc, self._parent_markercollection))

        return children