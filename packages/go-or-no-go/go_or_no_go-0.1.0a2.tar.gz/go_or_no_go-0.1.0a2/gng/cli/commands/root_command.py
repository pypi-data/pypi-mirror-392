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


# UPDATEME With subcommand apps in `cli/commands/`, see documentation at:
# https://typer.tiangolo.com/tutorial/
# See recommended configuration for multicommand applications at:
# https://typer.tiangolo.com/tutorial/one-file-per-command/#main-module-mainpy
"""Pre-commit hooks to check that your contributions meet project guidelines."""

from typing import Annotated

import typer
from rich.console import Console

from gng import __version__
from gng.cli.styling import AppCustomThemes

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")


def version_callback(print_version: bool) -> None:
    """Print the program version in a Rich console with the Noctis theme."""
    if print_version:
        Console(theme=AppCustomThemes.NOCTIS).print(
            f":package:[declaration]Go or NO GO[/] [bold fstring]{__version__}[/]"
        )

        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help=":bulb: Print the current version of this program and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Pre-commit hooks to check that your contributions meet project guidelines and the mission to merge is good to go.

    See below for commands and options.
    """  # noqa: E501,W505
    pass
