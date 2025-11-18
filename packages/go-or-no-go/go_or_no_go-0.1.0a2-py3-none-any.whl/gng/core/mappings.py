"""Mapping objects for the Go/NO GO validator."""

from enum import Enum

class ValidationMode(Enum):
    ALL = "all"
    ADDED = "added"
    REMOVED = "removed"
