# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import pandas as pd
import typing
import datetime
from cegalprizm.pythontool import _utils
from cegalprizm.pythontool.completions_casingstring import CasingString
from cegalprizm.pythontool.completions_perforation import Perforation
from cegalprizm.pythontool.completions_plugback import Plugback
from cegalprizm.pythontool.completions_squeeze import Squeeze
from cegalprizm.pythontool.grpc.completions_casingstring_grpc import CasingStringGrpc
from cegalprizm.pythontool.grpc.completions_perforation_grpc import PerforationGrpc
from cegalprizm.pythontool.grpc.completions_plugback_grpc import PlugbackGrpc
from cegalprizm.pythontool.grpc.completions_squeeze_grpc import SqueezeGrpc
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.completionsset_grpc import CompletionsSetGrpc

class CompletionsSet():
    """A class holding information about a completions set for a well."""

    def __init__(self, petrel_object_link: "CompletionsSetGrpc"):
        self._completionsset_object_link = petrel_object_link
    
    def __str__(self) -> str:
        """A readable representation"""
        return 'CompletionsSet(well_petrel_name="{0}")'.format(self._completionsset_object_link._parent_well.petrel_name)
    
    def __repr__(self) -> str:
        return self.__str__()

    def as_dataframe(self) -> pd.DataFrame:
        """ Gets a dataframe with information about a the active completions set for a well. 

        Returns:
            Dataframe: A dataframe with completions information. 
        """
        df = self._completionsset_object_link.GetDataframe()
        return df
    
    @property
    def casings(self):
        """ Gets an iterator with the casing strings for the completions set.
        
        Returns:
            An iterable collection of :class:`CasingString` objects for a completions set.
        """
        return CasingStrings(self)
    
    @property
    def perforations(self):
        """ Gets an iterator with the perforations for the completions set.
        
        Returns:
            An iterable collection of :class:`Perforation` objects for a completions set.
        """
        return Perforations(self)
    
    @property
    def plugbacks(self):
        """ Gets an iterator with the plugbacks for the completions set.
        
        Returns:
            An iterable collection of :class:`Plugback` objects for a completions set.
        """
        return Plugbacks(self)
    
    @property
    def squeezes(self):
        """ Gets an iterator with the squeezes for the completions set.
        
        Returns:
            An iterable collection of :class:`Squeeze` objects for a completions set.
        """
        return Squeezes(self)

    def add_perforation(self, name: str, top_md: float, bottom_md: float) -> Perforation:
        """ Adds a new perforation to the completions set.
        
        Args:
            name: The name of the new perforation as a string.
            top_md: The top MD of the new perforation as a float.
            bottom_md: The bottom MD of the new perforation as a float.

        Returns:
            The new perforation as a :class:`Perforation` object.
        """
        if(len(name) < 1):
            raise ValueError("name can not be an empty string")
        reference = self._completionsset_object_link.AddPerforation(name, top_md, bottom_md)
        grpc = PerforationGrpc(reference.guid, self._completionsset_object_link._plink)
        return Perforation(grpc)
    
    def add_plugback(self, name: str, top_md: float) -> Plugback:
        """ Adds a new plugback to the completions set.
        
        Args:
            name: The name of the new plugback as a string.
            top_md: The top MD of the new plugback as a float.

        Returns:
            The new plugback as a :class:`Plugback` object.
        """
        if(len(name) < 1):
            raise ValueError("name can not be an empty string")
        reference = self._completionsset_object_link.AddPlugback(name, top_md)
        grpc = PlugbackGrpc(reference.guid, self._completionsset_object_link._plink)
        return Plugback(grpc)
    
    def add_squeeze(self, name: str, top_md: float, bottom_md: float) -> Squeeze:
        """ Adds a new squeeze to the completions set.
        
        Args:
            name: The name of the new squeeze as a string.
            top_md: The top MD of the new squeeze as a float.
            bottom_md: The bottom MD of the new squeeze as a float.

        Returns:
            The new squeeze as a :class:`Squeeze` object.
        """
        if(len(name) < 1):
            raise ValueError("name can not be an empty string")
        reference = self._completionsset_object_link.AddSqueeze(name, top_md, bottom_md)
        grpc = SqueezeGrpc(reference.guid, self._completionsset_object_link._plink)
        return Squeeze(grpc)
    
    def available_casing_equipment(self):
        """ Retrieve a list of available casing equipment.

        Returns:
            Available casing equipment as a list of text strings.
        """
        return self._completionsset_object_link.GetAvailableCasingEquipment()

    
    def add_casing(self, name: str, bottom_md: float, equipment_name: str, start_date: datetime.datetime) -> CasingString:
        """ Adds a new casing string to the completions set. A casing string part will be added to the casing string using the supplied equipment name.
        (Petrel has a limitation that a casing string must always contain at least one casing string part.)
        
        Args:
            name: The name of the new casing string as a string.
            bottom_md: The bottom MD of the new casing string as a float.
            equipment_name: Name of casing equipment as retrieved by completions_set.available_casing_equipment().
            start_date: The start date of the casing string as a datetime.datetime object.

        Returns:
            The new casing string as a :class:`CasingString` object.
        """
        if(len(name) < 1):
            raise ValueError("The name can not be an empty string")
        if(bottom_md <= 0):
            raise ValueError("The bottom MD must be greater than 0")
        if not isinstance(start_date, datetime.datetime):
            raise TypeError("The start date must be a datetime.datetime object")
        reference = self._completionsset_object_link.AddCasingString(name, bottom_md, equipment_name, start_date)
        grpc = CasingStringGrpc(reference.guid, self._completionsset_object_link._plink)
        return CasingString(grpc)

class CasingStrings(object):
    """An iterable collection  of :class:`CasingString` objects for a completions set.
    """

    def __init__(self, parent):
        self._parent = parent
        if isinstance(parent, CompletionsSet):
            petrel_connection = parent._completionsset_object_link._plink
            grpcs = [
                CasingStringGrpc(petrelObjectRef.guid, petrel_connection)
                for petrelObjectRef in parent._completionsset_object_link.GetCasingStrings()
            ]
            self._casing_strings =  [
                CasingString(grpc)
                for grpc in grpcs
            ]
        else:
            raise TypeError("Parent must be a CompletionsSet object")
        
    def __len__(self) -> int:
        return len(self._casing_strings)

    def __iter__(self) -> typing.Iterator[CasingString]:
        return iter(self._casing_strings)
    
    def __getitem__(self, key):
        return _utils.get_item_from_collection_petrel_name(self._casing_strings, key)

    def __str__(self) -> str:
        return 'CasingStrings(CompletionsSet="{0}")'.format(self._parent)

    def __repr__(self) -> str:
        return str(self)
    
class Perforations(object):
    """An iterable collection  of :class:`Perforation` objects for a completions set.
    """

    def __init__(self, parent):
        self._parent = parent
        if isinstance(parent, CompletionsSet):
            petrel_connection = parent._completionsset_object_link._plink
            grpcs = [
                PerforationGrpc(petrelObjectRef.guid, petrel_connection)
                for petrelObjectRef in parent._completionsset_object_link.GetPerforations()
            ]
            self._perforations =  [
                Perforation(grpc)
                for grpc in grpcs
            ]
        else:
            raise TypeError("Parent must be a CompletionsSet object")
        
    def __len__(self) -> int:
        return len(self._perforations)

    def __iter__(self) -> typing.Iterator[Perforation]:
        return iter(self._perforations)
    
    def __getitem__(self, key):
        return _utils.get_item_from_collection_petrel_name(self._perforations, key)

    def __str__(self) -> str:
        return 'Perforations(CompletionsSet="{0}")'.format(self._parent)

    def __repr__(self) -> str:
        return str(self)
    
class Plugbacks(object):
    """An iterable collection  of :class:`Plugback` objects for a completions set.
    """

    def __init__(self, parent):
        self._parent = parent
        if isinstance(parent, CompletionsSet):
            petrel_connection = parent._completionsset_object_link._plink
            grpcs = [
                PlugbackGrpc(petrelObjectRef.guid, petrel_connection)
                for petrelObjectRef in parent._completionsset_object_link.GetPlugbacks()
            ]
            self._plugbacks =  [
                Plugback(grpc)
                for grpc in grpcs
            ]
        else:
            raise TypeError("Parent must be a CompletionsSet object")
        
    def __len__(self) -> int:
        return len(self._plugbacks)

    def __iter__(self) -> typing.Iterator[Plugback]:
        return iter(self._plugbacks)
    
    def __getitem__(self, key):
        return _utils.get_item_from_collection_petrel_name(self._plugbacks, key)

    def __str__(self) -> str:
        return 'Plugbacks(CompletionsSet="{0}")'.format(self._parent)

    def __repr__(self) -> str:
        return str(self)
    
class Squeezes(object):
    """An iterable collection  of :class:`Squeeze` objects for a completions set.
    """

    def __init__(self, parent):
        self._parent = parent
        if isinstance(parent, CompletionsSet):
            petrel_connection = parent._completionsset_object_link._plink
            grpcs = [
                SqueezeGrpc(petrelObjectRef.guid, petrel_connection)
                for petrelObjectRef in parent._completionsset_object_link.GetSqueezes()
            ]
            self._squeezes =  [
                Squeeze(grpc)
                for grpc in grpcs
            ]
        else:
            raise TypeError("Parent must be a CompletionsSet object")
        
    def __len__(self) -> int:
        return len(self._squeezes)
    
    def __iter__(self) -> typing.Iterator[Squeeze]:
        return iter(self._squeezes)
    
    def __getitem__(self, key):
        return _utils.get_item_from_collection_petrel_name(self._squeezes, key)
        
    def __str__(self) -> str:
        return 'Squeezes(CompletionsSet="{0}")'.format(self._parent)
    
    def __repr__(self) -> str:
        return str(self)