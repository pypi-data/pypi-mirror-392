import argparse
import sys
from typing import Never, Sequence

_PROGRAM_DESC = """
bpt is a build+package tool for a new era.
"""


def main(argv: Sequence[str], *, prog: str = "bpt") -> int:
    """
    The main entrypoint for the bpt application, returning the appropriate
    exit code for the process.

    :param argv: The command-line argument strings for the application, NOT
        including the initial binary name argument from `sys.argv`. To set the
        program name, pass a ``prog``.
    :param prog: The name of the application as printed in any generated help
        messages.
    """
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        prog=prog,
        description=_PROGRAM_DESC,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _args = parser.parse_args(argv)
    return 0


def start() -> Never:
    """
    Launch the bpt application, passing the current process argv, and exiting
    the callling process when finished.
    """
    sys.exit(main(sys.argv[1:]))
