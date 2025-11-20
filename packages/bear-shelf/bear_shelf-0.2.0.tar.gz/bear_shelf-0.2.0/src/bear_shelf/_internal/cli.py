from __future__ import annotations

import sys

from bear_shelf._internal.debug import METADATA, _print_debug_info
from funcy_bear.constants.exit_code import ExitCode
from funcy_bear.context.arg_helpers import args_inject

from ._cmds import _ReturnedArgs, get_args
from ._versioning import cli_bump


@args_inject(process=get_args)
def main(args: _ReturnedArgs) -> ExitCode:
    """Entry point for the CLI application.

    This function is executed when you type `bear-shelf` or `python -m bear-shelf`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    match args.cmd:
        case "version":
            print(METADATA.version)
            return ExitCode.SUCCESS
        case "bump":
            return cli_bump(args.bump_type, METADATA.version_tuple)
        case "debug":
            _print_debug_info()
            return ExitCode.SUCCESS
        case "sync-storage":
            from bear_shelf.datastore.storage._generate_storage import generate_storage_file  # noqa: PLC0415

            generate_storage_file()
            return ExitCode.SUCCESS
        case _:
            print("Unknown command.")
            return ExitCode.FAILURE


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
