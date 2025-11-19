
from typing import Dict
from typing import List
from typing import NewType

from dataclasses import dataclass
from dataclasses import field

from umlmodel.UmlClassCommon import UmlClassCommon
from umlmodel.UmlInterface import UmlInterface
from umlmodel.UmlInterface import UmlInterfaces
from umlmodel.UmlLinkedObject import UmlLinkedObject
from umlmodel.enumerations.UmlDisplayMethods import UmlDisplayMethods
from umlmodel.enumerations.UmlDisplayParameters import UmlDisplayParameters


def umlInterfacesFactory() -> UmlInterfaces:
    return UmlInterfaces([])


@dataclass
class UmlClass(UmlLinkedObject, UmlClassCommon):
    """
    A standard class representation.

    A PyutClass represents a UML class in Pyut. It manages its:
        - object data fields (`PyutField`)
        - methods (`PyutMethod`)
        - parents (`PyutClass`)(classes from which this one inherits)
        - stereotype (`PyutStereotype`)
        - a description (`string`)

    Example:
        ```python
            myClass = PyutClass("Foo") # this will create a `Foo` class
            myClass.description = "Example class"

            fields = myClass.fields             # These are the original fields, not a copy
            fields.append(PyutField(name="bar", fieldType="int"))
        ```

    Correct multiple inheritance:
        https://stackoverflow.com/questions/59986413/achieving-multiple-inheritance-using-python-dataclasses
    """
    displayParameters:    UmlDisplayParameters = UmlDisplayParameters.UNSPECIFIED
    displayConstructor:   UmlDisplayMethods    = UmlDisplayMethods.UNSPECIFIED
    displayDunderMethods: UmlDisplayMethods    = UmlDisplayMethods.UNSPECIFIED
    interfaces:           UmlInterfaces        = field(default_factory=umlInterfacesFactory)

    def __post_init__(self):
        super().__post_init__()
        UmlClassCommon.__init__(self)

    def addInterface(self, umlInterface: UmlInterface):
        self.interfaces.append(umlInterface)

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


PyutClassName = NewType('PyutClassName',  str)

PyutClassList  = NewType('PyutClassList', List[UmlClass])
PyutClassIndex = NewType('PyutClassIndex', Dict[PyutClassName, UmlClass])
