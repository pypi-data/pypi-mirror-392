# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.deletion import deletion_method
from cegalprizm.pythontool.exceptions import PythonToolException, UserErrorException
from cegalprizm.pythontool.experimental import experimental_method
from cegalprizm.pythontool import exceptions
from cegalprizm.pythontool.grpc import utils as grpc_utils
from cegalprizm.pythontool.grpc.template_grpc import TemplateGrpc, DiscreteTemplateGrpc
from cegalprizm.pythontool.parameter_validation import validate_name
from cegalprizm.pythontool.template import Template, DiscreteTemplate
from cegalprizm.pythontool import _utils
from cegalprizm.pythontool._well_known_object_description import WellKnownObjectDescription
from warnings import warn
import re
import typing
import pandas as pd

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.petrelobject_grpc import PetrelObjectGrpc
    from cegalprizm.pythontool import GlobalWellLogFolder, Folder, PropertyFolder, InterpretationFolder, SeismicCube

class PetrelObject(object):
    def __init__(self, petrel_object_link: "PetrelObjectGrpc") -> None:
        self._petrel_object_link = petrel_object_link
        self._readonly: bool = True
        petrel_object_link._domain_object = self

    @property
    def readonly(self) -> bool:
        """The read-only status of this object. By default objects retrieved from Petrel are read-only, and can only be modified if the readonly property is set to False.

        **Example**:

        .. code-block:: python

            well = petrel.wells["Input/Wells/Well1"]
            well.uwi = "123456789"
            >> PythonToolException: The well is read-only
            well.readonly = False
            well.uwi = "123456789"

        Parameters:
            value (bool): False to allow modifying the object, True if the object should be read-only

        Raises:
            PythonToolException: If the read-only status of the object type cannot be modified.

        Returns:
            bool: True if the object is read-only, False if the object can be modified."""
        return self._readonly

    @readonly.setter
    def readonly(self, value: bool) -> None:
        if value is False:
            readonly_error = self._petrel_object_link.IsAlwaysReadonly()
            if readonly_error:
                raise exceptions.PythonToolException(readonly_error + ' Cannot modify read-only for this object.' )

        self._readonly = value

    @property
    def path(self) -> str:
        """ The path of this object in Petrel. Neither the Petrel name nor the path is guaranteed to be unique.
        
        Returns:
            str: The path of the Petrel object"""
        return self._petrel_object_link.GetPath()

    def retrieve_stats(self) -> typing.Dict[str, str]:
        """Retrieves a dictionary summarizing the statistics for the object

        The statistics are a snapshot of the information in the
        Statistics page of the Settings panel of the object in the
        Petrel tree.  Both the dict key and value are strings, and may
        contain punctuation, English phrases or just filler
        information.  Any changes to the dict returned will not be
        saved or affect anything.

        Note: this operation may be slow, since the statistics are
        'live' - they represent the most up to date information.

        Returns:
            dict: The statistics of the object as reported by Petrel
        """
        s = self._petrel_object_link.RetrieveStats()
        return s

    @property
    def petrel_name(self) -> str:
        """Returns the name of this object in Petrel"""
        return self._petrel_object_link.GetPetrelName()

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
            
    def __repr__(self) -> str:
        return str(self)
            
    def _clone(self, name_of_clone, 
                    copy_values = False, 
                    template: typing.Union["Template", "DiscreteTemplate"] = None, 
                    destination: typing.Union["Folder","GlobalWellLogFolder", "PropertyFolder"] = None,
                    realize_path: str = ""):
        _utils.verify_clone_name(name_of_clone)
        path_of_clone = re.sub('[^/]+$', '',  self.path) + name_of_clone
        return self._petrel_object_link.ClonePetrelObject(path_of_clone, copy_values, template, destination, realize_path)

    def _move(self, destination: "Folder"):
        return self._petrel_object_link.MovePetrelObject(destination)

    @property
    def comments(self):
        """The comments on the PetrelObject.
        
        Returns:
            string: The comments on the PetrelObject as a string.
        """
        return self._petrel_object_link.GetComments()

    def add_comment(self, new_comment: str, overwrite: bool = False) -> None:
        """Add a comment to the already existing comments on the PetrelObject, or overwrite the existing comments.
        
        Args:
            new_comment: The new comment to add to the PetrelObject.
            overwrite: Boolean flag to overwrite all existing comments with the new comment. Default is False.
        
        Raises:
            PythonToolException: if object is read-only, or the object type is always read-only.

        **Example**:

        Add a new comment to already existing comments:

        .. code-block:: python

            well = petrel.wells["Input/Wells/Well1"]
            well.comments
            >> "This is an already existing comment."
            well.readonly = False
            well.add_comment("This is a new comment.")
            well.comments
            >> "This is an already existing comment.\\nThis is a new comment."

        **Example**:

        Overwrite existing comments with a new comment:

        .. code-block:: python

            well = petrel.wells["Input/Wells/Well1"]
            well.comments
            >> "This is an already existing comment."
            well.readonly = False
            well.add_comment("This is a new comment.", overwrite=True)
            well.comments
            >> "This is a new comment."
        
        """
        if self._petrel_object_link.IsAlwaysReadonly():
            raise exceptions.PythonToolException(f"Cannot add comment. The {str(type(self))} object is always readonly")

        if self.readonly:
            raise exceptions.PythonToolException("Object is readonly")

        ok = self._petrel_object_link.AddComments(new_comment, overwrite)
        if not ok:
            raise UserErrorException("An error occured while adding the comment.")

    # Helper method
    def _get_template(self) -> typing.Union[Template, DiscreteTemplate, None]:
        template_ref = self._petrel_object_link.GetTemplate()
        template = grpc_utils.pb_PetrelObjectRef_to_grpcobj(template_ref, self._petrel_object_link._plink)
        if isinstance(template, TemplateGrpc):
            return Template(template)
        elif isinstance(template, DiscreteTemplateGrpc):
            return DiscreteTemplate(template)
        else:
            return None
        
    @experimental_method
    def _get_color_table_droid(self) -> str:
        """
        Helper method to get the droid of the color table of the object. Used for unit testing.
        """
        return self._petrel_object_link.GetColorTableDroid()

class PetrelObjectWithTemplate(object):
    def __init__(self, petrel_object_link: "PetrelObjectGrpc") -> None:
        self._petrel_object_link = petrel_object_link
        petrel_object_link._domain_object = self

    @property
    def template(self) -> str:
        """Returns the Petrel template for the object as a string. If no template available, will return an empty string."""
        return self._petrel_object_link.GetTemplateString()

class PetrelObjectWithDomain(object):
    def __init__(self, petrel_object_link: "PetrelObjectGrpc") -> None:
        self._petrel_object_link = petrel_object_link
        petrel_object_link._domain_object = self

    @property
    def domain(self) -> str:
        """Returns the domain of the object as a string. If no domain available, will return an empty string."""
        return self._petrel_object_link.GetDomainString()

class PetrelObjectWithTemplateToBeDeprecated(object):
    def __init__(self, petrel_object_link: "PetrelObjectGrpc") -> None:
        self._petrel_object_link = petrel_object_link
        petrel_object_link._domain_object = self

    @property
    def template(self) -> str:
        """DeprecationWarning: template property not available for this object type. This method will be removed in Python Tool Pro 3.0.
        """
        warn("template property not available for this object type. This method will be removed in Python Tool Pro 3.0.", DeprecationWarning, stacklevel=2)
        return ""

class PetrelObjectWithHistory(object):
    def __init__(self, petrel_object_link: "PetrelObjectGrpc") -> None:
        self._petrel_object_link = petrel_object_link
        petrel_object_link._domain_object = self

    def retrieve_history(self) -> pd.DataFrame:
        """The Petrel history for the object.

        Returns the Petrel history for the object as Pandas dataframe.

        Returns:
            DataFrame: The history of the object as reported by Petrel
        """
        s = self._petrel_object_link.RetrieveHistory()
        return pd.DataFrame.from_dict({"Date": [el for el in s[0]],
                                        "User": [el for el in s[1]],
                                        "Action": [el for el in s[2]],
                                        "Description": [el for el in s[3]]})

class PetrelObjectWithHistoryToBeDeprecated(object):
    def __init__(self, petrel_object_link: "PetrelObjectGrpc") -> None:
        self._petrel_object_link = petrel_object_link
        petrel_object_link._domain_object = self

    def retrieve_history(self) -> pd.DataFrame:
        """DeprecationWarning: retrieve_history() not available for this object type. This method will be removed in Python Tool Pro 3.0.
        """
        warn("retrieve_history() not available for this object type. This method will be removed in Python Tool Pro 3.0.", DeprecationWarning, stacklevel=2)
        s = 4*[[]]
        return pd.DataFrame.from_dict({"Date": [el for el in s[0]],
                                        "User": [el for el in s[1]],
                                        "Action": [el for el in s[2]],
                                        "Description": [el for el in s[3]]})

class PetrelObjectWithPetrelNameSetter(object):
    @validate_name(param_name="petrel_name", can_be_empty=False)
    def set_petrel_name(self, petrel_name: str) -> None:
        """Set the name of this object in Petrel.

        Note:
            Some objects may not allow changing the name. E.g. the main WellFolder (Input/Wells) or the TWT SurfaceAttribute.

        Args:
            petrel_name (str): The name of this object in Petrel.
        
        Raises:
            TypeError: If the petrel_name argument is not a string.
            ValueError: If the petrel_name argument is empty or None.
            ValueError: If the petrel_name argument is not a valid string.
            PythonToolException: If the object is read-only or the object type is always read-only.
            PythonToolException: If the name cannot be set for the specific object.

        Example:

        .. code-block:: python

            well = petrel.wells["Input/Wells/Well1"]
            well.petrel_name
            >> 'Well1'
            well.set_petrel_name("Well1 Updated")
            well.petrel_name
            >> 'Well1 Updated'
        """
        if self._petrel_object_link.IsAlwaysReadonly():
            raise exceptions.PythonToolException(f"Cannot set petrel_name. The {str(type(self))} object is always readonly")

        if self.readonly:
            raise exceptions.PythonToolException("Object is readonly")

        updated_ok = self._petrel_object_link.SetPetrelName(petrel_name)
        if not updated_ok:
            raise exceptions.PythonToolException("Failed to set petrel_name, the name is not editable for this object")

class PetrelObjectWithDeletion(object):
    def __init__(self, petrel_object_link: "PetrelObjectGrpc") -> None:
        self._petrel_object_link = petrel_object_link
        petrel_object_link._domain_object = self

    @deletion_method
    def delete(self) -> None:
        """Delete the Petrel object.  

        Note:
            This is a destructive action, the Petrel object will be deleted and any further access attempts to it will result in an exception or unexpected behavior.  
            Already defined python objects with reference to the deleted object might not work as expected, and will require a refresh of the object.  
            The deleted object will become a :class:`_DeletedPetrelObject` proxy, blocking all access to the original object's properties and methods.

        Raises:
            PythonToolException: If allow_deletion is set to False on PetrelConnection. (Default is False)
            PythonToolException: If the object is read-only.
            PythonToolException: If the object could not be deleted.
        
        **Example**:

        .. code-block:: python

            petrel = PetrelConnection(allow_deletion=True)
            surface = petrel.surfaces['Path/To/Surface']
            surface.delete()
            >> None
        """
        if self.readonly:
            raise exceptions.PythonToolException(f"{self} object is readonly")
        try:
            result = self._petrel_object_link.DeletePetrelObject()
            if not result:
                raise exceptions.PythonToolException(f"Failed to delete '{self}'")
            original_type = str(type(self))
            self.__class__ = _DeletedPetrelObject
            self.__init__(original_type)
        except exceptions.PythonToolException:
            raise
        except Exception as e:
            raise exceptions.PythonToolException(f"An unexpected error occurred while deleting '{self}': {e}")

class PetrelObjectWithParentFolder(object):
    @property
    def _parent_folder(self) -> typing.Union["Folder", "InterpretationFolder", "SeismicCube", None]:
        parent_folder_ref = self._petrel_object_link.GetParentFolder()
        if parent_folder_ref.sub_type == WellKnownObjectDescription.RootInput:
            return None
        from cegalprizm.pythontool.workflow import _pb_grpcobj_to_pyobj
        return _pb_grpcobj_to_pyobj(grpc_utils.pb_PetrelObjectRef_to_grpcobj(parent_folder_ref, self._petrel_object_link._plink))

class _DeletedPetrelObject(object):
    """
    A proxy class representing a deleted Petrel object.
    """
    def __init__(self, original_type=None):
        self._original_type = original_type

    def __str__(self) -> str:
        return f"<Deleted {self._original_type}>"

    def __repr__(self) -> str:
        return str(self)