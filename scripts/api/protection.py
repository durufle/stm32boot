import sys
import argparse
from stmloader.bootloader import STM32, CommandError
from scaffold import Scaffold


def main():
    parser = argparse.ArgumentParser(description='This script uses Scaffold to communicate with CEVAL firmware')
    parser.add_argument('-m', '--mode', default='unprotect', choices=['unprotect', 'protect'], help='readout protection')
    args = parser.parse_args()

    # Open connection with scaffold (port auto-detection)
    loader = STM32(Scaffold())

    # Reset to system memory and get Chip id.
    loader.reset_from_system_memory()

    try:
        if args.mode == 'unprotect':
            # Disable read protection
            loader.readout_unprotect()
        if args.mode == 'protect':
            # Enable readout protect
            loader.readout_protect()
    except CommandError as e:
        print(e)

    input("press a key to exit...")


if __name__ == '__main__':
    sys.exit(main())
