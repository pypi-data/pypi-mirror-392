# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import datetime
from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.completions_casingstring_grpc import CasingStringGrpc

class CasingString(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion):
    """A class holding information about a CasingString"""

    def __init__(self, petrel_object_link: "CasingStringGrpc"):
        super(CasingString, self).__init__(petrel_object_link)
        self._casingstring_object_link = petrel_object_link

    def __str__(self) -> str:
        """A readable representation"""
        return 'CasingString("{0}")'.format(self.petrel_name)
    
    def __repr__(self) -> str:
        return str(self)
    
    @property
    def bottom_md(self) -> float:
        """The bottom MD of the casing string.
        
        Returns:
            float: The bottom MD of the casing string as a float value.
        """
        return self._casingstring_object_link.GetEndDepth()
    
    @bottom_md.setter
    def bottom_md(self, new_depth: float) -> None:
        self._casingstring_object_link.SetEndDepth(new_depth)
    
    @property
    def start_date(self) -> datetime.datetime:
        """The start date the casing string.
        
        Returns:
            datetime.datetime: The start date of the casing string as a datetime object.
        """
        return self._casingstring_object_link.GetStartDate()
    
    @start_date.setter
    def start_date(self, new_date: datetime.datetime) -> None:
        if not isinstance(new_date, datetime.datetime):
            raise TypeError("The new date must be a datetime.datetime object")
        return self._casingstring_object_link.SetStartDate(new_date)

    def add_part(self, split_md: float, equipment_name: str,):
        """ Adds a new casing string part to the casing string. The depth of any parts above or below will be adjusted.
        
        Args:
            split_md: The MD where existing casing parts are split to insert the new part.
            equipment_name: Name of casing equipment as retrieved by completions_set.available_casing_equipment().

        Returns:
            CasingStringPart: The added casing string part as a CasingStringPart object.
        """
        if(split_md <= 0):
            raise ValueError("The split MD must be greater than 0")
        name, start_depth, end_depth = self._casingstring_object_link.AddCasingStringPart(split_md, equipment_name)
        return CasingStringPart(self, name, start_depth, end_depth)
    
    def remove_part(self, part):
        """ Removes a casing string part from the casing string. The depth of any parts above or below will be adjusted.
        
        Args:
            part: The part to remove as a CasingStringPart object.
        """

        if type(part) is not CasingStringPart:
            raise TypeError("The part must be of type CasingStringPart")

        self._casingstring_object_link.RemoveCasingStringPart(part._start_depth, part._end_depth)

    @property
    def parts(self):
        """ Gets an iterator with the individual parts of the casing string.
        
        Returns:
            An iterable collection of :class:`CasingStringPart` objects for a casing string.
        """
        return CasingStringParts(self)

class CasingStringPart(object):
    """A part of a :class:`CasingString` object for a completions set.
    """
    def __init__(self, parent, name, start_depth, end_depth):
        self._parent = parent
        self._name = name
        self._start_depth = start_depth
        self._end_depth = end_depth

    def __str__(self) -> str:
        return 'CasingStringPart({0} ({1}-{2}))'.format(self._name, self._start_depth, self._end_depth)
    
    def __repr__(self) -> str:
        return str(self)

    @property
    def bottom_md(self) -> float:
        """The bottom MD of the casing part.
        
        Returns:
            float: The bottom MD of the casing string part as a float value.
        """
        return self._end_depth

    @bottom_md.setter
    def bottom_md(self, new_depth: float) -> None:
        new_inserted_depth = self._parent._casingstring_object_link.SetCasingPartDepth(self._start_depth, self._end_depth, new_depth)
        ## Due to rounding we update the depth of the python object to keep track of the correct casing part
        self._end_depth = new_inserted_depth

class CasingStringParts(object):
    """An iterable collection  of :class:`CasingStringPart` objects for a completions set.
    """

    def __init__(self, parent):
        self._parent = parent
        if isinstance(parent, CasingString):
            container = parent._casingstring_object_link.GetCasingStringParts()
            names = container[0]
            start_depths = container[1]
            end_depths = container[2]
            self._parts = []
            for i in range(len(names)):
                self._parts.append(CasingStringPart(parent, names[i], start_depths[i], end_depths[i]))
        else:
            raise TypeError("Parent must be a CasingString object")

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._parts[key]
        elif isinstance(key, str):
            index = None
            i = 0
            while i < len(self._parts):
                if key == self._parts[i]._name:
                    index = i
                    break
                i += 1
            if index is None:
                return None
            return self._parts[index]

    def __len__(self) -> int:
        return len(self._parts)

    def __iter__(self) -> typing.Iterator[CasingStringPart]:
        return iter(self._parts)

    def __str__(self) -> str:
        return 'CasingStringParts({0})'.format(self._parent)
    
    def __repr__(self) -> str:
        return str(self)