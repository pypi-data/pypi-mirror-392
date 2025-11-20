
from typing import ClassVar

from dataclasses import dataclass

from umlmodel.BaseAttributes import BaseAttributes


@dataclass
class Text(BaseAttributes):

    DEFAULT_TEXT: ClassVar[str] = 'Text to display'

    content: str = DEFAULT_TEXT
    """
    The model has to remember additional text attributes
    """
    def __init__(self, content: str = DEFAULT_TEXT):
        """

        Args:
            content: The text string to display
        """
        super().__init__()
        self.content = content
