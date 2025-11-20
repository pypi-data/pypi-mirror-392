
from typing import List
from typing import NewType

from dataclasses import dataclass

from umlmodel.Parameter import Parameter
from umlmodel.enumerations.Visibility import Visibility


@dataclass
class Field(Parameter):
    """
    A class field

    A Field represents a UML field
        - parent (`Param`)
        - field  visibility

    Example:
        franField = Field("fran", "integer", "55")
        or
        ozzeeField = Field('Ozzee', 'str', 'GatoMalo', VisibilityEnum.Private)
    """

    visibility: Visibility = Visibility.PRIVATE

    def __str__(self):
        """
        Need our own custom string value

        Returns:  A nice string
        """

        return f'{self.visibility}{Parameter.__str__(self)}'

    def __repr__(self):
        return self.__str__()


Fields = NewType('Fields', List[Field])
