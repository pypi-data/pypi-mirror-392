# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion
import datetime
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.completions_squeeze_grpc import SqueezeGrpc

class Squeeze(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    """A class holding information about a Squeeze"""

    def __init__(self, petrel_object_link: "SqueezeGrpc"):
        super(Squeeze, self).__init__(petrel_object_link)
        self._squeeze_object_link = petrel_object_link

    def __str__(self) -> str:
        """A readable representation"""
        return 'Squeeze("{0}")'.format(self.petrel_name)
    
    def __repr__(self) -> str:
        return str(self)
    
    @property
    def top_md(self) -> float:
        """The top MD of the squeeze.
        
        Returns:
            float: The top MD of the squeeze as a float value.
        """
        return self._squeeze_object_link.GetTopMd()
    
    @top_md.setter
    def top_md(self, new_depth: float) -> None:
        self._squeeze_object_link.SetTopMd(new_depth)

    @property
    def bottom_md(self) -> float:
        """The bottom MD of the squeeze.
        
        Returns:
            float: The bottom MD of the squeeze as a float value.
        """
        return self._squeeze_object_link.GetBottomMd()
    
    @bottom_md.setter
    def bottom_md(self, new_depth: float) -> None:
        self._squeeze_object_link.SetBottomMd(new_depth)

    @property
    def start_date(self) -> datetime.datetime:
        """The start date of the squeeze.
        
        Returns:
            datetime.datetime: The start date of the squeeze as a datetime object.
        """
        return self._squeeze_object_link.GetStartDate()
    
    @start_date.setter
    def start_date(self, new_date: datetime.datetime) -> None:
        if not isinstance(new_date, datetime.datetime):
            raise TypeError("The new date must be a datetime.datetime object.")
        self._squeeze_object_link.SetStartDate(new_date)