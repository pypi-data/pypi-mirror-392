from enum import Enum


class UmlLinkType(Enum):

    """
     Types of UML Links
    """
    ASSOCIATION = 0
    AGGREGATION = 1
    COMPOSITION = 2
    INHERITANCE = 3
    INTERFACE   = 4
    NOTELINK    = 5
    SD_MESSAGE  = 6
    LOLLIPOP    = 7

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.name

    @staticmethod
    def toEnum(strValue: str) -> 'UmlLinkType':
        """
        Converts the input string to the link type enum
        Args:
            strValue:   The serialized string representation

        Returns:  The link type enumeration
        """
        canonicalStr: str = strValue.lower().strip(' ')
        if canonicalStr == 'association':
            return UmlLinkType.ASSOCIATION
        elif canonicalStr == 'aggregation':
            return UmlLinkType.AGGREGATION
        elif canonicalStr == 'composition':
            return UmlLinkType.COMPOSITION
        elif canonicalStr == 'inheritance':
            return UmlLinkType.INHERITANCE
        elif canonicalStr == 'interface':
            return UmlLinkType.INTERFACE
        elif canonicalStr == 'notelink':
            return UmlLinkType.NOTELINK
        elif canonicalStr == 'sd_message':
            return UmlLinkType.SD_MESSAGE
        else:
            print(f'Warning: LinkType.toEnum - Do not recognize link type: `{canonicalStr}`')
            return UmlLinkType.ASSOCIATION
