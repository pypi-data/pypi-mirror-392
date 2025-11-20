from pathlib import Path

import click

from ara_api_lua._core import LuaBridge
from ara_api_lua._utils import Logger

_logger = Logger(
    "ara-api-lua", log_level="INFO", log_to_file=False, log_to_terminal=True
)


@click.command
@click.argument("file_path")
def main(file_path: str, *args, **kwargs) -> None:
    file = Path(file_path)

    if not file.exists():
        _logger.error("Error: {file} doesn't exits")

    bridge = LuaBridge(_logger)
    bridge.execute(str(file))


if __name__ == "__main__":
    main()
