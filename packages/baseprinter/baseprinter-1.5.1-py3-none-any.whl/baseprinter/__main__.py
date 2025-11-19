import sys, warnings
from typing import Any, TextIO

from . import cli


def custom_warning(
    message: Warning | str,
    category: type[Warning],
    filename: str,
    lineno: int,
    file: TextIO | None = None,
    line: str | None = None,
) -> None:
    print(message, file=sys.stderr)


def main(args: Any = None) -> int:
    warnings.showwarning = custom_warning
    try:
        return cli.main(args)
    except Exception as ex:
        print(ex, file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit(main())
