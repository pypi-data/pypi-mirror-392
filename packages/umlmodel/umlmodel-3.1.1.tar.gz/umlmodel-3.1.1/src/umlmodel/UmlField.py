
from typing import List
from typing import NewType

from dataclasses import dataclass

from umlmodel.UmlParameter import UmlParameter
from umlmodel.enumerations.UmlVisibility import UmlVisibility


@dataclass
class UmlField(UmlParameter):
    """
    A class field

    A PyutField represents a UML field
        - parent (`PyutParam`)
        - field  visibility

    Example:
        franField = PyutField("fran", "integer", "55")
        or
        ozzeeField = PyutField('Ozzee', 'str', 'GatoMalo', PyutVisibilityEnum.Private)
    """

    visibility: UmlVisibility = UmlVisibility.PRIVATE

    def __str__(self):
        """
        Need our own custom string value

        Returns:  A nice string
        """

        return f'{self.visibility}{UmlParameter.__str__(self)}'

    def __repr__(self):
        return self.__str__()


UmlFields = NewType('UmlFields', List[UmlField])
