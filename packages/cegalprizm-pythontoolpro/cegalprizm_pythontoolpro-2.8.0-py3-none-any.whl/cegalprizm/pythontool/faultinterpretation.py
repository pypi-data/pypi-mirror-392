# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import typing
import pandas as pd
from pandas.api.types import is_bool_dtype
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_integer_dtype
from cegalprizm.pythontool import exceptions, _docstring_utils
from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithDomain, PetrelObjectWithHistory
from cegalprizm.pythontool import PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion, PetrelObjectWithParentFolder
from cegalprizm.pythontool.experimental import experimental_method

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.faultinterpretation_grpc import FaultInterpretationGrpc
    from cegalprizm.pythontool import InterpretationFolder

class FaultInterpretation(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithDomain, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter, PetrelObjectWithDeletion, PetrelObjectWithParentFolder):
    """A class holding information about a fault interpretation in Petrel.
    """  

    def __init__(self, interpretation_grpc: "FaultInterpretationGrpc"):
        super(FaultInterpretation, self).__init__(interpretation_grpc)
        self._fault_interpretation_object_link = interpretation_grpc

    def __str__(self) -> str:
        return "FaultInterpretation(petrel_name=\"{0}\")".format(self.petrel_name)
    
    def as_dataframe(self) -> pd.DataFrame:
        """ Get a dataframe with the interpreted fault polylines (fault sticks) for the FaultInterpretation.

        The values in the Z column will be in either time or depth units, depending on the domain of the FaultInterpretation. Domain information can be retrieved through the domain property.

        Returns:
            pd.DataFrame: A dataframe with Fault Stick ID, X, Y and Z values for the polylines in the FaultInterpretation.
        """
        return self._fault_interpretation_object_link.GetFaultSticksDataframe()
    
    @_docstring_utils.clone_docstring_decorator(return_type="FaultInterpretation", respects_subfolders=True, is_fault_interpretation=True)
    def clone(self, name_of_clone: str, copy_values: bool = False) -> "FaultInterpretation":
        return typing.cast("FaultInterpretation", self._clone(name_of_clone, copy_values))
    
    def clear(self) -> None:
        """Clear all polylines from the FaultInterpretation.

        Raises:
            PythonToolException: If the FaultInterpretation is readonly
        """
        if(self.readonly):
            raise exceptions.PythonToolException("The FaultInterpretation is readonly")
        self._fault_interpretation_object_link.ClearAllPolylines()

    @experimental_method
    def set_polylines(self, dataframe: pd.DataFrame, connected_seismic = None) -> None:
        """
        Set the polylines on the FaultInterpretation object.

        Setting polylines will overwrite any existing polylines on the FaultInterpretation. To preserve data, use the as_dataframe() method to retrieve the existing polylines and set those together with the new data.
        The input is a pandas dataframe with the same columns as the output of the as_dataframe() method, with multiple points making up each polyline.
        In addition to the dataframe a :class:`SeismicLine` or :class:`SeismicCube` can be provided as a seismic context for the polylines. If not provided, the polylines will be added without a defined context.

        The dataframe must contain the following columns:
            "Fault Stick ID" (int): The id of the polyline (The ID identifies which points belong to the same polyline, but the value will likely change when the data is later retrieved).
            
            "X" (float): The x-coordinate of each point.
            
            "Y" (float): The y-coordinate of each point.
            
            "Z" (float): The z-coordinate of each point.

        Any other columns in the dataframe will be ignored.

        Note that any duplicate points will be ignored, even if they are in different polylines. (This limitation is set in the Ocean API.)
        
        Note that the values in the Z column may be in either time or depth units, depending on the domain of the FaultInterpretation. Domain information can be retrieved through the domain property.
        
        Note that when the polylines are later retrieved using as_dataframe(), Petrel might have retriangulated the order of the points to ensure continuity. The user must make sure that the points are ordered in the way that defines the interpreted geometry of the fault. Incorrect ordering of the points by X, Y or Z, might lead to Petrel rendering or triangulating the points differently to the intention of the user.

        **Example**:

        Copy the polylines from one FaultInterpretation to another:

        .. code-block:: Python

            fault_interpretation1 = petrelconnection.faultinterpretations["Input/Path/To/FaultInterpretation1"]
            fault_interpretation2 = petrelconnection.faultinterpretations["Input/Path/To/FaultInterpretation2"]
            df = fault_interpretation1.as_dataframe()
            fault_interpretation2.set_polylines(df)

        **Example**:

        Append polylines from a FaultInterpretation to existing polyline data in another FaultInterpretation:

        .. code-block:: Python

            import pandas as pd
            fault_interpretation1 = petrelconnection.faultinterpretations["Input/Path/To/FaultInterpretation1"]
            fault_interpretation2 = petrelconnection.faultinterpretations["Input/Path/To/FaultInterpretation2"]
            existing_data = fault_interpretation2.as_dataframe()
            additional_data = fault_interpretation1.as_dataframe()
            ## Assuming the Fault Stick ID is unique between the two dataframes
            combined_data = pd.concat([existing_data, additional_data], ignore_index=True)
            fault_interpretation2.set_polylines(combined_data)

        Args:
            dataframe (pd.DataFrame): A dataframe with Fault Stick ID, X, Y and Z values for the polylines to be added.
            connected_seismic (SeismicLine or SeismicCube, optional): The seismic context for the polylines, must be either a SeismicLine or a SeismicCube object. Defaults to None.

        Raises:
            PythonToolException: If the FaultInterpretation is readonly
        """
        if self.readonly:
            raise exceptions.PythonToolException("The FaultInterpretation is readonly")
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("The input must be a pandas dataframe")
        self._check_correct_columns(dataframe)
        sorted_dataframe = dataframe.sort_values(by=["Fault Stick ID"], inplace=False)
        polylines_dict = self._create_polylines_dict(sorted_dataframe)

        self._fault_interpretation_object_link.SetPolylines(polylines_dict, connected_seismic)

    def _check_correct_columns(self, dataframe: pd.DataFrame) -> None:
        if "Fault Stick ID" not in dataframe.columns:
            raise ValueError("The dataframe must contain the column 'Fault Stick ID'")
        elif not is_integer_dtype(dataframe["Fault Stick ID"]):
            raise ValueError("The column 'Fault Stick ID' must contain integer values")
        if "X" not in dataframe.columns:
            raise ValueError("The dataframe must contain the column 'X'")
        elif is_bool_dtype(dataframe["X"].dtype) or not is_numeric_dtype(dataframe["X"]):
            raise ValueError("The column 'X' must contain float or int values")
        if "Y" not in dataframe.columns:
            raise ValueError("The dataframe must contain the column 'Y'")
        elif is_bool_dtype(dataframe["Y"].dtype) or not is_numeric_dtype(dataframe["Y"]):
            raise ValueError("The column 'Y' must contain float or int values")
        if "Z" not in dataframe.columns:
            raise ValueError("The dataframe must contain the column 'Z'")
        elif is_bool_dtype(dataframe["Z"].dtype) or not is_numeric_dtype(dataframe["Z"]):
            raise ValueError("The column 'Z' must contain float or int values")
        
    def _create_polylines_dict(self, dataframe: pd.DataFrame):
        polylines_dict = {}
        xs, ys, zs = [], [], []
        current_index = dataframe["Fault Stick ID"][0]

        for index in dataframe.index:
            if dataframe["Fault Stick ID"][index] != current_index:
                polylines_dict[current_index] = (xs, ys, zs)
                xs, ys, zs = [], [], []
                current_index = dataframe["Fault Stick ID"][index]
            xs.append(dataframe["X"][index])
            ys.append(dataframe["Y"][index])
            zs.append(dataframe["Z"][index])
        polylines_dict[current_index] = (xs, ys, zs)
        return polylines_dict

    @property
    def parent_folder(self) -> "InterpretationFolder":
        """Returns the parent folder of this FaultInterpretation in Petrel.

        Returns:
            :class:`InterpretationFolder`: The parent InterpretationFolder of the object.

        **Example**:

        .. code-block:: python

            fault_interpretation = petrel_connection.faultinterpretations["Input/FaultInterpretations/FaultInterpretation123"]
            fault_interpretation.parent_folder
            >> InterpretationFolder(petrel_name="FaultInterpretations")
        """
        return self._parent_folder
