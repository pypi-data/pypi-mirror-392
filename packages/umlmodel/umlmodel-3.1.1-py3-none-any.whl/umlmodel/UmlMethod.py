
from typing import NewType
from typing import List

from dataclasses import dataclass
from dataclasses import field

from umlmodel.UmlModifier import UmlModifier
from umlmodel.UmlObject import UmlObject
from umlmodel.UmlParameter import UmlParameter
from umlmodel.UmlType import UmlType

from umlmodel.enumerations.UmlVisibility import UmlVisibility

SourceCode    = NewType('SourceCode',     List[str])
UmlModifiers  = NewType('UmlModifiers', List[UmlModifier])
UmlParameters = NewType('UmlParameters', List[UmlParameter])


def pyutModifiersFactory() -> UmlModifiers:
    return UmlModifiers([])


def sourceCodeFactory() -> SourceCode:
    return SourceCode([])


def parametersFactory() -> UmlParameters:
    return UmlParameters([])


@dataclass
class UmlMethod(UmlObject):
    """
    A method representation.

    A PyutMethod represents a method of a UML class in Pyut. It manages its:

        - parameters (`PyutParameter`)
        - visibility (`PyutVisibility`)
        - modifiers (`PyutModifier`)
        - return type (`PyutType`)
        - source code if reverse-engineered
        - isProperty indicates if the method is really a property
    """
    parameters: UmlParameters = field(default_factory=parametersFactory)
    modifiers:  UmlModifiers  = field(default_factory=pyutModifiersFactory)

    visibility: UmlVisibility  = UmlVisibility.PUBLIC
    returnType: UmlType        = UmlType('')
    isProperty: bool            = False
    sourceCode: SourceCode      = field(default_factory=sourceCodeFactory)

    def addParameter(self, parameter: UmlParameter):
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


UmlMethods  = NewType('UmlMethods', List[UmlMethod])
