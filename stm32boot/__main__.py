import sys
from .subcommands.donjon import CommandError, DataLengthError, PageIndexError
from .subcommands.commands import Commands


def main(*arguments):
    """
    """
    boot = Commands(arguments)
    boot.connect()
    boot.get()
    try:
        boot.perform_commands()
    except (CommandError, DataLengthError, PageIndexError) as e:
        print(e)
        sys.exit(-1)


if __name__ == "__main__":
    main(*sys.argv[1:])
