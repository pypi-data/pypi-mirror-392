
from typing import NewType
from typing import List

from dataclasses import dataclass
from dataclasses import field

from umlmodel.Modifier import Modifier
from umlmodel.BaseAttributes import BaseAttributes
from umlmodel.Parameter import Parameter
from umlmodel.ReturnType import ReturnType
from umlmodel.UmlType import UmlType

from umlmodel.enumerations.Visibility import Visibility

SourceCode = NewType('SourceCode', List[str])
Modifiers  = NewType('Modifiers',  List[Modifier])
Parameters = NewType('Parameters', List[Parameter])


def modifiersFactory() -> Modifiers:
    return Modifiers([])


def sourceCodeFactory() -> SourceCode:
    return SourceCode([])


def parametersFactory() -> Parameters:
    return Parameters([])


@dataclass
class Method(BaseAttributes):
    """
    A method representation.

    A Method instance represents a method in a UML class in the UML Diagrammer. It manages its:

        - parameters (`Parameter`)
        - visibility (`Visibility`)
        - modifiers (`Modifier`)
        - return type (`Type`)
        - source code if reverse-engineered
        - isProperty indicates if the method is really a property
    """
    parameters: Parameters = field(default_factory=parametersFactory)
    modifiers:  Modifiers  = field(default_factory=modifiersFactory)

    visibility: Visibility  = Visibility.PUBLIC
    returnType: ReturnType  = ReturnType('')
    isProperty: bool        = False
    sourceCode: SourceCode  = field(default_factory=sourceCodeFactory)

    def addParameter(self, parameter: Parameter):
        """
        Add a parameter.

        Args:
            parameter: parameter to add
        """
        self.parameters.append(parameter)

    def methodWithoutParameters(self):
        """
        Returns:   String representation without parameters.
        """
        string = f'{self.visibility}{self.name}()'
        # add the parameters
        if self.returnType.value != "":
            string = f'{string}: {self.returnType}'
        return string

    def methodWithParameters(self):
        """

        Returns: The string representation with parameters
        """
        string = f'{self.visibility}{self.name}('
        # add the params
        if not self.parameters:
            string = f'{string}  '  # to compensate the removing [:-2]
        for param in self.parameters:
            string = f'{string}{param}, '

        string = string[:-2] + ")"      # remove the last comma and add a trailing parenthesis
        if self.returnType.value != "":
            string = f'{string}: {self.returnType}'

        return string

    def __str__(self) -> str:
        """
        Returns: Nice human-readable form
        """
        return self.methodWithParameters()

    def __repr__(self) -> str:
        internalRepresentation: str = (
            f'{self.__str__()} '
            f'{self.modifiers} '
            f'{self.sourceCode}'
        )
        return internalRepresentation


Methods  = NewType('Methods', List[Method])
