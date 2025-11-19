# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion
import datetime
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.completions_plugback_grpc import PlugbackGrpc

class Plugback(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    """A class holding information about a Plugback"""

    def __init__(self, petrel_object_link: "PlugbackGrpc"):
        super(Plugback, self).__init__(petrel_object_link)
        self._plugback_object_link = petrel_object_link

    def __str__(self) -> str:
        """A readable representation"""
        return 'Plugback("{0}")'.format(self.petrel_name)
    
    def __repr__(self) -> str:
        return str(self)
    
    @property
    def top_md(self) -> float:
        """The top MD of the plugback.
        
        Returns:
            float: The top MD of the plugback as a float value.
        """
        return self._plugback_object_link.GetTopMd()
    
    @top_md.setter
    def top_md(self, new_depth: float) -> None:
        self._plugback_object_link.SetTopMd(new_depth)

    @property
    def bottom_md(self) -> float:
        """The bottom MD of the plugback.
        
        Returns:
            float: The bottom MD of the plugback as a float value.
        """
        return self._plugback_object_link.GetBottomMd()
    
    @property
    def start_date(self) -> datetime.datetime:
        """The start date of the plugback.
        
        Returns:
            datetime.datetime: The start date of the plugback as a datetime object.
        """
        return self._plugback_object_link.GetStartDate()
    
    @start_date.setter
    def start_date(self, new_date: datetime.datetime) -> None:
        if not isinstance(new_date, datetime.datetime):
            raise TypeError("The new date must be a datetime.datetime object.")
        self._plugback_object_link.SetStartDate(new_date)