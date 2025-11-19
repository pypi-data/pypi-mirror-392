# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.exceptions import PythonToolException
import typing

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.petrelobject_grpc import PetrelObjectGrpc

class BaseTemplate(object):
    def __init__(self, petrel_object_link: "PetrelObjectGrpc") -> None:
        self._petrel_object_link = petrel_object_link
        petrel_object_link._domain_object = self

    def __repr__(self) -> str:
        return str(self)

    @property
    def petrel_name(self) -> str:
        """Returns the name of this object in Petrel"""
        return self._petrel_object_link.GetPetrelName()
    
    @property
    def path(self) -> str:
        """ The path of this object in Petrel. Neither the Petrel name nor the path is guaranteed to be unique.
        
        Returns:
            str: The path of the Petrel object"""
        return self._petrel_object_link.GetPath()

    @property
    def droid(self) -> str:
        """The Petrel Droid (object id or guid) for the object

        Returns the Petrel Droid or object id or guid for the object.
        If not available, will throw a PythonToolException.

        This property is planned to be deprecated in favour of a similar
        but more general id schema in future releases.
        
        Returns:
            str: The Petrel Droid of the object
        """
        try:
            return self._petrel_object_link._guid
        except Exception:
            raise PythonToolException("Droid not available")

class Template(BaseTemplate):
    """A class holding information about a template"""
    def __init__(self, petrel_object_link: "PetrelObjectGrpc") -> None:
        super(Template, self).__init__(petrel_object_link)

    def __str__(self) -> str:
        return 'Template(petrel_name="{0}")'.format(self.petrel_name)

    @property
    def unit_symbol(self) -> str:
        """Returns the unit symbol of this template"""
        symbol = self._petrel_object_link.UnitSymbol() # str
        return symbol
    
    @property
    def _available_units(self) -> "list[str]":
        # """Returns a list of available units for this template.
        # Use .unit_symbol to get the currently selected unit of the template.
        # Changes to this list will not be persisted or affect any Petrel objects.
        # **Example:**
        # .. code-block:: Python
        #     my_continous_template = petrellink.templates['Templates/Well log templates/S-sonic']
        #     print(my_continous_template._available_units)
        #     # outputs ['min/ft', 'min/m', 'ms/ft', 'ms/m', 'ns/m', 's/ft', 's/m', 'us/ft', 'us/m']
        # """
        return [u for u in self._petrel_object_link.Units()]

class DiscreteTemplate(BaseTemplate):
    """A class holding information about a discrete template"""
    def __init__(self, petrel_object_link: "PetrelObjectGrpc") -> None:
        super(DiscreteTemplate, self).__init__(petrel_object_link)
        self._discrete_codes = None

    def __str__(self) -> str:
        return 'DiscreteTemplate(petrel_name="{0}")'.format(self.petrel_name)
    
    @property
    def discrete_codes(self) -> typing.Dict[int, str]:
        """Returns a dictionary of discrete codes and values for this discrete template

        Changes to this dictionary will not be persisted or affect any Petrel objects.

        **Example:**

        .. code-block:: Python

            my_discrete_template = petrellink.discrete_templates['facies']
            print(my_discrete_template.discrete_codes[1])
            # outputs 'Fine sand'
        """
        if self._discrete_codes is None:
            self._discrete_codes = self.__make_discrete_codes_dict()
        return self._discrete_codes
    
    def __make_discrete_codes_dict(self) -> typing.Dict[int, str]:
        codes = {}
        for tup in self._petrel_object_link.GetAllDictionaryCodes():
            k = tup.Item1
            v = tup.Item2
            codes[k] = v
        self._discrete_codes = codes
        return codes