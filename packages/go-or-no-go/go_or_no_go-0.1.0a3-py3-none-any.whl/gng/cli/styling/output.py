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


"""Collection of objects and special classes for rendering Go/NO GO output."""

from typing import TYPE_CHECKING

from rich.console import Console, ConsoleOptions, RenderResult
from rich.table import Table
from rich.text import Text

from gng.cli.styling.themes import AppCustomThemes
from gng.core.mappings import ValidationMode

if TYPE_CHECKING:
    from gng.core import GoNoGoValidator


class GNGFailSummary:
    """Custom class to render a text and a table in a single Rich ConsoleRenderable.

    Parameters
    ----------
    text : str
        Text containing Rich markup to function as the header of the renderable.
    table: Table
        Rich table object to render below the text.
    """

    def __init__(self, text: str, table: Table) -> None:
        """Initialise the renderable."""
        self.text = Text.from_markup(text)
        self.table = table

    def __rich_console__(  # noqa: PLW3201
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Dunder method to be read by the Rich API."""
        yield self.text
        yield self.table


def print_output(validator: "GoNoGoValidator") -> None:
    """Render the message with a summary on the state of the validation.

    Parameters
    ----------
    validator : GoNoGoValidator
        The instantiated validator with metrics for comparison.
    """
    console = Console(theme=AppCustomThemes.NOCTIS)

    if validator.above_threshold:
        fail_output = build_failing_output(validator)
        console.print(fail_output)

    else:
        success_msg = "[bold string]All systems are good to go![/] :rocket:"
        console.print(success_msg)


def build_failing_output(validator: "GoNoGoValidator") -> GNGFailSummary:
    """Render the message with a summary on the state of the validation.

    Parameters
    ----------
    validator : GoNoGoValidator
        The instantiated validator with metrics for comparison.

    Returns
    -------
    GNGFailSummary
        A customised Rich ConsoleRenderable with the summary for failed Go/NO GO runs.
    """
    grid = Table.grid(padding=(0, 1, 0, 0))
    grid.add_column()
    grid.add_column(justify="right")

    header = (
        ":stop_sign: [bold declaration]Branch changes above admissible threshold![/]"
    )

    added_string = f"[bold fstring]{validator.added_lines}[/]"
    removed_string = f"[bold property]{validator.removed_lines}[/]"

    if validator.mode == ValidationMode.ADDED:
        grid.add_row("Threshold:", f"[bold number]{validator.threshold}[/]")
        grid.add_row("Added lines:", added_string)

    elif validator.mode == ValidationMode.REMOVED:
        grid.add_row("Threshold:", f"[bold number]{validator.threshold}[/]")
        grid.add_row("Removed lines:", removed_string)

    else:
        grid.add_column()
        grid.add_row("Threshold:", f"[bold number]{validator.threshold}[/]", "")
        grid.add_row(
            "Changes:",
            f"[bold constant]{validator.change_count}[/]",
            f"({added_string} added, {removed_string} removed)",
        )

    return GNGFailSummary(header, grid)
