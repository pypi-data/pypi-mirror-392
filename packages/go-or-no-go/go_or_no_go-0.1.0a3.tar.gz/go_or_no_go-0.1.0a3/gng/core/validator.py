# The MIT License (MIT)
# Copyright (c) 2025 The Galactipy Contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.


"""Validate changes in a branch against the default branch."""

from pathlib import Path

from git.repo.base import InvalidGitRepositoryError  # type: ignore[attr-defined]
from pydriller.metrics.process.lines_count import LinesCount

from gng.core.mappings import ValidationMode


class GoNoGoValidator:
    """Validate changes in a working Git branch against the default branch.

    Parameters
    ----------
    default_branch : str
        The default Git branch for the repository.
    threshold : int
        The maximum number of changes allowed when comparing to the default branch.
    mode : {"all", "added", "removed"}, default "all"
        Which type of change to consider when comparing to `threshold`.
    """

    def __init__(
        self,
        default_branch: str,
        threshold: int,
        mode: str | ValidationMode = ValidationMode.ALL,
    ) -> None:
        self._validate_references(default_branch)

        self.threshold = threshold
        self.mode = ValidationMode(mode)

    @property
    def above_threshold(self) -> bool:
        """Return the comparison of the branch's change count against the threshold."""
        return self.change_count > self.threshold

    def _validate_references(self, default_branch: str) -> None:
        cwd = str(Path.cwd())

        try:
            self.metrics = LinesCount(cwd, from_commit=default_branch, to_commit="HEAD")

        except InvalidGitRepositoryError:
            msg = f'"{cwd}" is not a valid Git repository'
            raise InvalidGitRepositoryError(msg) from None

    @property
    def change_count(self) -> int:
        """Count the number of changes considering all modified values.

        Returns
        -------
        int
            The number of changes considering the validation mode.
        """
        self.added_lines = sum(self.metrics.count_added().values())
        self.removed_lines = sum(self.metrics.count_removed().values())
        self.changed_lines = sum(self.metrics.count().values())

        if self.mode == ValidationMode.ADDED:
            return self.added_lines

        if self.mode == ValidationMode.REMOVED:
            return self.removed_lines

        return self.changed_lines
