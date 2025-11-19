
from dataclasses import dataclass

from umlmodel.UmlObject import UmlObject
from umlmodel.UmlType import UmlType


@dataclass
class UmlParameter(UmlObject):

    type:         UmlType = UmlType("")
    defaultValue: str      = ''

    def __str__(self) -> str:
        """
        We need our own custom representation

        Returns:  String version of a UML Parameter
        """
        s = self.name

        if str(self.type.value) != "":
            s = f'{s}: {self.type.value}'

        if self.defaultValue != '':
            s = f'{s} = {self.defaultValue}'

        return s

    def __repr__(self) -> str:
        return self.__str__()
