import sys
from intelhex import IntelHex
from stmloader.bootloader import STM32, CommandError
from scaffold import Scaffold


def main():
    # Open connection with scaffold (port auto-detection)
    loader = STM32(Scaffold())
    # Reset to system memory and get Chip id.
    loader.reset_from_system_memory()
    # Get bootloader commands
    loader.get()
    try:
        # Read data from flash
        data = loader.read_memory(address=0x08000000, length=64)
    except CommandError as e:
        print(e)
        sys.exit(-1)

    ih = IntelHex()
    ih.frombytes(data, 0x08000000)
    ih.dump()


if __name__ == '__main__':
    sys.exit(main())
