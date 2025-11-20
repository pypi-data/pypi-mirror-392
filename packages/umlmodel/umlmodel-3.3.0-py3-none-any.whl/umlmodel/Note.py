
from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from umlmodel.LinkedObject import LinkedObject


@dataclass
class Note(LinkedObject):

    content: str = ''

    def __init__(self, content: str = ''):

        super().__init__(name='')

        self.logger: Logger = getLogger(__name__)

        self.content  = content

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return f'model ID: {self.id} {self.content[:6]}'
