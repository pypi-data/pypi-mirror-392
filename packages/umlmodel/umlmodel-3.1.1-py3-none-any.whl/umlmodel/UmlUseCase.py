
from dataclasses import dataclass

from umlmodel.UmlLinkedObject import UmlLinkedObject


@dataclass
class UmlUseCase(UmlLinkedObject):
    """
    """
    def __init__(self, name: str = ''):

        super().__init__(name=name)
