import sys
from .subcommands.donjon import CommandError, DataLengthError, PageIndexError
from .subcommands.commands import Commands


def main():
    """
    """
    boot = Commands(sys.argv[1:])
    boot.connect()
    boot.get()
    try:
        boot.perform_commands()
    except (CommandError, DataLengthError, PageIndexError) as e:
        print(e)
        sys.exit(-1)


if __name__ == "__main__":
    main()
