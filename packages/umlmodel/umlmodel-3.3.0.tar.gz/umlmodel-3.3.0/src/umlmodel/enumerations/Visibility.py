
from typing import List

from enum import Enum
from typing import cast


class Visibility(Enum):

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
        for valEnum in Visibility:
            val:    Visibility = cast(Visibility, valEnum)
            retList.append(val.__str__())
        return retList

    @staticmethod
    def toEnum(strValue: str) -> 'Visibility':
        """
        Converts the input string to the visibility enum
        Args:
            strValue:   A serialized string value

        Returns:  The visibility enumeration
        """
        canonicalStr: str = strValue.lower().strip(' ')
        if canonicalStr == 'public':
            return Visibility.PUBLIC
        elif canonicalStr == 'private':
            return Visibility.PRIVATE
        elif canonicalStr == 'protected':
            return Visibility.PROTECTED
        elif canonicalStr == '+':
            return Visibility.PUBLIC
        elif canonicalStr == '-':
            return Visibility.PRIVATE
        elif canonicalStr == '#':
            return Visibility.PROTECTED
        else:
            assert False, f'Warning: Visibility.toEnum - Do not recognize visibility type: `{canonicalStr}`'
