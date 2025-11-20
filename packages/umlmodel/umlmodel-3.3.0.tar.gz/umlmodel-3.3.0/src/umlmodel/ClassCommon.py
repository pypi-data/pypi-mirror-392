
from dataclasses import dataclass
from dataclasses import field

from umlmodel.Field import Field
from umlmodel.Field import Fields

from umlmodel.Method import Method
from umlmodel.Method import Methods

from umlmodel.enumerations.Stereotype import Stereotype


def methodsFactory() -> Methods:
    return Methods([])


def fieldsFactory() -> Fields:
    return Fields([])


@dataclass
class ClassCommon:
    """
    These are the attributes shared between a Class and an Interface
    """

    description: str = ''
    showMethods: bool = True
    showFields:  bool = True

    displayStereoType: bool = True

    stereotype: Stereotype = Stereotype.NO_STEREOTYPE

    fields:  Fields  = field(default_factory=fieldsFactory)
    methods: Methods = field(default_factory=methodsFactory)

    def addMethod(self, newMethod: Method):
        self.methods.append(newMethod)

    def addField(self, umlField: Field):
        """
        Add a field

        Args:
            umlField:   New field to append

        """
        self.fields.append(umlField)
