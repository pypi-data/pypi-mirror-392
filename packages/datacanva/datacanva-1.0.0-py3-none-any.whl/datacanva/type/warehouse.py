from typing import TypedDict
from enum import Enum


class WriteMode(str, Enum):
    APPEND = "APPEND"
    UPSERT = "UPSERT"
    OVERWRITE = "OVERWRITE"


class DataType(str, Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    TIMESTAMP = "TIMESTAMP"


class SchemaField(TypedDict):
    name: str
    dataType: str
    nonNullable: bool
    primaryKey: bool
    unique: bool
    displayFormat: str


class Schema(TypedDict):
    fields: list[SchemaField]
