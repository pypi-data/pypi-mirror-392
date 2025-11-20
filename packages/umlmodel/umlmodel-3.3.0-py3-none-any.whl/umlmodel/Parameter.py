
from dataclasses import dataclass

from umlmodel.BaseAttributes import BaseAttributes

from umlmodel.UmlType import UmlType
from umlmodel.FieldType import FieldType
from umlmodel.ParameterType import ParameterType

Type = ParameterType | FieldType | UmlType

@dataclass
class Parameter(BaseAttributes):

    type:         Type = UmlType('')
    defaultValue: str  = ''

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
