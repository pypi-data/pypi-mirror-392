
from typing import List
from typing import NewType
from typing import cast

from typing import Union
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from umlmodel.UmlObject import UmlObject
from umlmodel.enumerations.UmlLinkType import UmlLinkType

if TYPE_CHECKING:
    from umlmodel.UmlClass import UmlClass              # noqa
    from umlmodel.UmlNote import UmlNote                # noqa
    from umlmodel.UmlUseCase import UmlUseCase          # noqa
    from umlmodel.UmlSDInstance import UmlSDInstance    # noqa
    from umlmodel.UmlActor import UmlActor              # noqa


# Using type aliases on purpose
LinkSource      = Union['UmlClass', 'UmlNote', 'UmlSDInstance', 'UmlActor']
LinkDestination = Union['UmlClass', 'UmlUseCase',  'UmlSDInstance']

NONE_LINK_SOURCE:      LinkSource      = cast(LinkSource, None)
NONE_LINK_DESTINATION: LinkDestination = cast(LinkDestination, None)


@dataclass
class UmlLink(UmlObject):
    """
    A standard link between a classes or Note.

    A UmlLink represents a link between a class, another class or a note in a UML diagram.

    Example:
    ```python

        myLink  = UmlLink("linkName", UmlLinkType.OGL_INHERITANCE, "0", "*")
    ```
    """

    linkType: UmlLinkType = UmlLinkType.INHERITANCE

    sourceCardinality:      str  = ''
    destinationCardinality: str  = ''
    bidirectional:          bool = False

    source:                 LinkSource      = NONE_LINK_SOURCE
    destination:            LinkDestination = NONE_LINK_DESTINATION

    # noinspection PyUnresolvedReferences
    def __init__(self, name="", linkType: UmlLinkType = UmlLinkType.INHERITANCE,
                 cardinalitySource:       str  = "",
                 cardinalityDestination:  str  = "",
                 bidirectional: bool = False,
                 source:        LinkSource      = NONE_LINK_SOURCE,
                 destination:   LinkDestination = NONE_LINK_DESTINATION):
        """
        Args:
            name:                   The link name
            linkType:               The enum representing the link type
            cardinalitySource:      The source cardinality
            cardinalityDestination: The destination cardinality
            bidirectional:          If the link is bidirectional `True`, else `False`
            source:                 The source of the link
            destination:            The destination of the link
        """
        super().__init__(name)

        self.logger: Logger       = getLogger(__name__)

        self.linkType               = linkType
        self.sourceCardinality      = cardinalitySource
        self.destinationCardinality = cardinalityDestination

        self.bidirectional = bidirectional
        self.source        = source
        self.destination   = destination

    def __str__(self):
        """
        String representation.

        Returns:
             string representing link
        """
        return f'("{self.name}") links from {self.source} to {self.destination}'


UmlLinks = NewType('UmlLinks', List[UmlLink])
