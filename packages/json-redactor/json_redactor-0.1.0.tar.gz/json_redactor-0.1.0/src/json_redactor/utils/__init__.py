from enum import Enum


class RedactionMode(str, Enum):
    MASK = "mask"
    HASH = "hash"
