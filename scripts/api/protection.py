# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Laurent Bonnet
#
# License: MIT
"""
Example on readout protection command
"""
import sys
import argparse
from scaffold import Scaffold
from stmloader.bootloader import STM32, CommandError


def main():
    """
    protect - unprotect readout
    @return:
    """
    parser = argparse.ArgumentParser(description='Enable / Disable readout protection')
    parser.add_argument('-m', '--mode', default='unprotect', choices=['unprotect', 'protect'],
                        help='readout protection')
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
