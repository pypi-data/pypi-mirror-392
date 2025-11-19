
from dataclasses import dataclass

from umlmodel.UmlLinkedObject import UmlLinkedObject

@dataclass
class UmlActor(UmlLinkedObject):
    """
    Represents a Use Case actor (data layer).
    An actor, in data layer, only has a name. Linking is resolved by
    parent class `PyutLinkedObject` that defines everything needed for
    link connections.
    """
    def __init__(self, actorName: str = ''):
        """
        Args:
            actorName: The name of the actor
        """
        super().__init__(name=actorName)
