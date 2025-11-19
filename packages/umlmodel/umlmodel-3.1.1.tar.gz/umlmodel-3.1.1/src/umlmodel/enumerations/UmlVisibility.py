
from typing import List

from enum import Enum
from typing import cast


class UmlVisibility(Enum):

    PRIVATE   = '-'
    PROTECTED = '#'
    PUBLIC    = '+'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'{self.name} - {self.__str__()}'

    @staticmethod
    def values() -> List[str]:
        retList: List[str] = []
        for valEnum in UmlVisibility:
            val:    UmlVisibility = cast(UmlVisibility, valEnum)
            retList.append(val.__str__())
        return retList

    @staticmethod
    def toEnum(strValue: str) -> 'UmlVisibility':
        """
        Converts the input string to the visibility enum
        Args:
            strValue:   A serialized string value

        Returns:  The visibility enumeration
        """
        canonicalStr: str = strValue.lower().strip(' ')
        if canonicalStr == 'public':
            return UmlVisibility.PUBLIC
        elif canonicalStr == 'private':
            return UmlVisibility.PRIVATE
        elif canonicalStr == 'protected':
            return UmlVisibility.PROTECTED
        elif canonicalStr == '+':
            return UmlVisibility.PUBLIC
        elif canonicalStr == '-':
            return UmlVisibility.PRIVATE
        elif canonicalStr == '#':
            return UmlVisibility.PROTECTED
        else:
            assert False, f'Warning: UmlVisibility.toEnum - Do not recognize visibility type: `{canonicalStr}`'
