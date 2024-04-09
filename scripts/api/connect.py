import sys
from stmloader.bootloader import STM32, CommandError
from scaffold import Scaffold


def main():
    # Open connection with scaffold (port auto-detection)
    loader = STM32(Scaffold())
    # Reset to system memory and get Chip id.
    loader.reset_from_system_memory()
    # Get bootloader commands
    loader.get()


if __name__ == '__main__':
    sys.exit(main())
