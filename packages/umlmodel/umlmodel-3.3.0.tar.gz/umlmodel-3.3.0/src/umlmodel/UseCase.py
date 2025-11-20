
from dataclasses import dataclass

from umlmodel.LinkedObject import LinkedObject


@dataclass
class UseCase(LinkedObject):
    """
    """
    def __init__(self, name: str = ''):

        super().__init__(name=name)
