
from typing import ClassVar
from typing import Generator

from dataclasses import dataclass

from human_id import generate_id


def uniqueIdentifier() -> Generator[str, None, None]:

    while True:
        yield generate_id()


@dataclass
class UmlObject:
    idGenerator: ClassVar[Generator[str, None, None]] = uniqueIdentifier()

    name:     str = ''
    id:       str = ''
    fileName: str = ''

    def __post_init__(self):
        self.id   = next(UmlObject.idGenerator)
