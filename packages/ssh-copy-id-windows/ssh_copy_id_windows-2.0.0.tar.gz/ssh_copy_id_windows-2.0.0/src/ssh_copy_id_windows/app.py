import os
from typing import Annotated

import typer
from loguru import logger  # noqa: F401

from .backend.copy_id import copy_id

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode=None,
    pretty_exceptions_enable=False,
)


@app.command(no_args_is_help=True)
def copy_id_cli(
        host: Annotated[str, typer.Argument(help="Host name in format name@host or hostname from ssh config.")],
        file: Annotated[str | None, typer.Option(
            "-i", "--id-file",
            help="Name or path of id key file. By default copy all keys from ~/.ssh directory.")] = None,
        port: Annotated[int | None, typer.Option("-p", "--port", help="Host port")] = None,
             ) -> None:

    if "@" in host:
        username, hostname = host.split("@")
    else:
        username, hostname = None, host

    copy_id(host=hostname, port=port, username=username, id_path=file)


def main() -> None:
    if os.environ.get("SSH_COPY_ID__DEBUG") != "true":
        logger.disable("")
    app()