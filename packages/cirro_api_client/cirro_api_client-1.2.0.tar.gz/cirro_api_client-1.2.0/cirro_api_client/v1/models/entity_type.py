from enum import Enum


class EntityType(str, Enum):
    DATASET = "DATASET"
    DISCUSSION = "DISCUSSION"
    NOTEBOOK = "NOTEBOOK"
    PROCESS = "PROCESS"
    PROJECT = "PROJECT"
    REFERENCE = "REFERENCE"
    SAMPLE = "SAMPLE"
    SHARE = "SHARE"
    TAG = "TAG"
    USER = "USER"
    UNKNOWN = "UNKNOWN"
    """ This is a fallback value for when the value is not known, do not use this value when making requests """

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _missing_(cls, number):
        return cls(cls.UNKNOWN)
