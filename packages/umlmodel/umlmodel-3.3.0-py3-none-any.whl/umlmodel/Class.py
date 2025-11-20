
from typing import Dict
from typing import List
from typing import NewType

from dataclasses import dataclass
from dataclasses import field

from umlmodel.ClassCommon import ClassCommon
from umlmodel.Interface import Interface
from umlmodel.Interface import Interfaces
from umlmodel.LinkedObject import LinkedObject
from umlmodel.ModelTypes import ClassName
from umlmodel.enumerations.DisplayMethods import DisplayMethods
from umlmodel.enumerations.DisplayParameters import DisplayParameters


def interfacesFactory() -> Interfaces:
    return Interfaces([])


@dataclass
class Class(LinkedObject, ClassCommon):
    """
    A standard class representation.

    A Class instance represents a UML class in the UML Diagrammer. It manages:
        - object data fields (`Field`)
        - methods (`Method`)
        - parents (`Class`)(classes from which this one inherits)
        - stereotype (`Stereotype`)
        - a description (`string`)

    Example:
        ```python
            myClass = Class("Foo") # this will create a `Foo` class
            myClass.description = "Example class"

            fields = myClass.fields             # These are the original fields, not a copy
            fields.append(Field(name="bar", fieldType="int"))
        ```

    Correct multiple inheritance:
        https://stackoverflow.com/questions/59986413/achieving-multiple-inheritance-using-python-dataclasses
    """
    displayParameters:    DisplayParameters = DisplayParameters.UNSPECIFIED
    displayConstructor:   DisplayMethods    = DisplayMethods.UNSPECIFIED
    displayDunderMethods: DisplayMethods    = DisplayMethods.UNSPECIFIED
    interfaces:           Interfaces        = field(default_factory=interfacesFactory)

    def __post_init__(self):
        super().__post_init__()
        ClassCommon.__init__(self)

    def addInterface(self, interface: Interface):
        self.interfaces.append(interface)

    def __getstate__(self):
        """
        For deepcopy operations, specifies which fields to avoid copying.
        Deepcopy must not copy the links to other classes, or it would result
        in copying the entire diagram.
        """
        aDict = self.__dict__.copy()
        aDict["parents"]    = []
        return aDict

    def __str__(self):
        """
        String representation.
        """
        return f"Class : {self.name}"

    def __repr__(self):
        return self.__str__()


ClassList  = NewType('ClassList',  List[Class])
ClassIndex = NewType('ClassIndex', Dict[ClassName, Class])
