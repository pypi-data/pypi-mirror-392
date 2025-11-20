
from enum import Enum

from dataclasses import dataclass

from umlmodel.BaseAttributes import BaseAttributes


class SDInstanceType(Enum):
    INSTANCE_TYPE_ACTOR = 'Actor'
    INSTANCE_TYPE_CLASS = 'Class'


@dataclass
class SDInstance(BaseAttributes):
    instanceName:           str = "Unnamed instance"
    instanceLifeLineLength: int = 200
    instanceGraphicalType:  SDInstanceType = SDInstanceType.INSTANCE_TYPE_CLASS
    """
    Data model representation of a UML Collaboration instance (C.Diagram).
    """
