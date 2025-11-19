
from dataclasses import dataclass


@dataclass(frozen=True)
class UmlType:
    value: str = ''

    def __str__(self) -> str:
        """
        String representation.
        """
        return self.value
