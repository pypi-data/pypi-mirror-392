from enum import Enum

class DataFormatEnum(Enum):
    JSON = "json"
    XML = "xml"

class ModeOfConnection(Enum):
    PUSH = "PUSH"
    PULL = "PULL"
