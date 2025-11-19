from enum import StrEnum
from maleo.types.string import ListOfStrs


class Granularity(StrEnum):
    STANDARD = "standard"
    FULL = "full"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    KEY = "key"
    NAME = "name"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]

    @property
    def column(self) -> str:
        return self.value


class ExaminationType(StrEnum):
    HISTORICAL = "historical"
    PHYSICAL = "physical"
    LABORATORY = "laboratory"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


class LaboratoryExaminationCategory(StrEnum):
    HEMATOLOGY = "hematology"
    IMMUNOLOGY = "immunology"
    CLINCAL_CHEMISTRY = "clinical_chemistry"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


class HistoricalParameter(StrEnum): ...


class ParameterGroup(StrEnum):
    """Enum for parameter groups."""

    PHYISICAL_EXAMINATION = "Physical Examination"
    HEMATOLOGY = "Hematology"
    CLINICAL_CHEMISTRY = "Clinical Chemistry"
    IMMUNOLOGY = "Immunology"
    OTHERS = "Others"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


class ParameterType(StrEnum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    TEXT = "text"
    BOOLEAN = "boolean"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]
