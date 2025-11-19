
from typing import Dict
from typing import List
from typing import NewType

from dataclasses import dataclass

from umlmodel.UmlClassCommon import UmlClassCommon
from umlmodel.UmlModelTypes import ClassName
from umlmodel.UmlModelTypes import Implementors
from umlmodel.UmlObject import UmlObject


def implementorsFactory() -> Implementors:
    return Implementors([])


@dataclass
class UmlInterface(UmlObject, UmlClassCommon):

    def __init__(self, name: str = ''):
        """

        Args:
            name:  The interface name
        """
        super().__init__(name=name)
        UmlClassCommon.__init__(self)

        self._implementors: Implementors = Implementors([])

    @property
    def implementors(self) -> Implementors:
        return self._implementors

    @implementors.setter
    def implementors(self, newValue: Implementors):
        self._implementors = newValue

    def addImplementor(self, newClassName: ClassName):
        self.implementors.append(newClassName)

    def __hash__(self) -> int:
        return hash((self.name, self.id))

    def __eq__(self, other) -> bool:
        """

             Args:
                 other:

             Returns:  True if the defined PointNodes are 'functionally' equal
        """
        ans: bool = False

        if isinstance(other, UmlInterface) is False:
            pass
        else:
            if self.name == other.name and self.id == other.id:
                ans = True

        return ans

    def __repr__(self):

        methodsStr = ''
        for method in self.methods:
            methodsStr = f'{methodsStr} {method} '

        return f'UmlInterface {self.name} {methodsStr}'


UmlInterfaces     = NewType('UmlInterfaces',     List[UmlInterface])
UmlInterfacesDict = NewType('UmlInterfacesDict', Dict[str, UmlInterface])
