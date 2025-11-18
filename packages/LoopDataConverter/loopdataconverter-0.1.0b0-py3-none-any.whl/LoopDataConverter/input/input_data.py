from dataclasses import dataclass
from ..datatypes import Datatype


@dataclass
class InputData:
    """Class to store input data for the loop data converter

    Attributes:
        geology: Optional[Datatype] = None
        structure: Optional[Datatype] = None
        fault: Optional[Datatype] = None
        fold: Optional[Datatype] = None
    """

    GEOLOGY: Datatype.GEOLOGY = None
    STRUCTURE: Datatype.STRUCTURE = None
    FAULT: Datatype.FAULT = None
    FOLD: Datatype.FOLD = None

    def __getitem__(self, datatype: str):
        """Method to get the file directory of a datatype

        Parameters:
            datatype (str): The datatype to get the file directory of

        Returns:
            The file directory of the datatype

        Raises:
            KeyError: If the datatype is not found in InputData
        """
        try:
            return getattr(self, datatype.name)
        except AttributeError:
            raise KeyError(f"Datatype {datatype.name} not found in InputData")


@dataclass
class OutputData(InputData):

    def __getitem__(self, datatype: Datatype):
        return super().__getitem__(datatype)
