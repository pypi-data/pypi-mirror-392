
from dataclasses import dataclass
from dataclasses import field

from umlmodel.UmlField import UmlField
from umlmodel.UmlField import UmlFields
from umlmodel.UmlMethod import UmlMethod
from umlmodel.UmlMethod import UmlMethods
from umlmodel.enumerations.UmlStereotype import UmlStereotype


def methodsFactory() -> UmlMethods:
    return UmlMethods([])


def fieldsFactory() -> UmlFields:
    return UmlFields([])


@dataclass
class UmlClassCommon:

    description: str = ''
    showMethods: bool = True
    showFields:  bool = True

    displayStereoType: bool = True

    stereotype: UmlStereotype = UmlStereotype.NO_STEREOTYPE

    fields:  UmlFields  = field(default_factory=fieldsFactory)
    methods: UmlMethods = field(default_factory=methodsFactory)

    def addMethod(self, newMethod: UmlMethod):
        self.methods.append(newMethod)

    def addField(self, pyutField: UmlField):
        """
        Add a field

        Args:
            pyutField:   New field to append

        """
        self.fields.append(pyutField)
