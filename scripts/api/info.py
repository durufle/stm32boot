import sys
from intelhex import IntelHex
from stmloader.bootloader import STM32, CommandError
from scaffold import Scaffold


def main():
    # Open connection with scaffold (port auto-detection)
    loader = STM32(Scaffold())

    # Reset to system memory and get Chip id.
    loader.reset_from_system_memory()
    try:
        # Get bootloader commands
        loader.get()
        # Get protocol version
        loader.get_protocol_version()
        # Get bootloader version
        loader.get_bootloader_id()
    except CommandError as e:
        print(e)


if __name__ == '__main__':
    sys.exit(main())
