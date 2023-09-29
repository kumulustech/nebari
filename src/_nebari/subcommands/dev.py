import json
import pathlib

import typer

from _nebari.config import read_configuration
from nebari.hookspecs import hookimpl


@hookimpl
def nebari_subcommand(cli: typer.Typer):
    app_dev = typer.Typer(
        add_completion=False,
        no_args_is_help=True,
        rich_markup_mode="rich",
        context_settings={"help_option_names": ["-h", "--help"]},
    )

    cli.add_typer(
        app_dev,
        name="dev",
        help="Development tools and advanced features.",
        rich_help_panel="Additional Commands",
    )
