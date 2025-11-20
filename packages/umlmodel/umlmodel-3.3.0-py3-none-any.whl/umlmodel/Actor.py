
from dataclasses import dataclass

from umlmodel.LinkedObject import LinkedObject

@dataclass
class Actor(LinkedObject):
    """
    Represents a Use Case actor (data model).
    An actor, in the data model, only has a name. Linking is resolved by the
    parent class's `LinkedObject`.  It defines everything needed for
    link connections.
    """
    def __init__(self, actorName: str = ''):
        """
        Args:
            actorName: The name of the actor
        """
        super().__init__(name=actorName)
