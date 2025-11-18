"""Validate changes in a branch against the default branch."""

from pathlib import Path

from pydriller.metrics.process.lines_count import LinesCount

from gng.core.mappings import ValidationMode


class GoNoGoValidator:
    """Validate changes in a working Git branch against the default branch."""

    def __init__(self, default_branch: str, threshold: int, mode: str | ValidationMode = ValidationMode.ALL) -> None:
        cwd = str(Path.cwd())

        self.metrics = LinesCount(cwd, from_commit=default_branch, to_commit="HEAD")
        self.threshold = threshold
        self.mode = ValidationMode(mode)

    def validate_branch(self):
        if self.mode == ValidationMode.ADDED:
            return sum(self.metrics.count_added().values()) <= self.threshold

        if self.mode == ValidationMode.REMOVED:
            return sum(self.metrics.count_removed().values()) <= self.threshold

        return sum(self.metrics.count().values()) <= self.threshold

