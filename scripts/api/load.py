# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Laurent Bonnet
#
# License: MIT
"""
Example on load meory command
"""
import sys
from intelhex import IntelHex
from scaffold import Scaffold
from stmloader.bootloader import STM32


def main():
    """
    Load test file in memory
    @return:
    """
    # Open connection with scaffold (port auto-detection)
    loader = STM32(Scaffold())
    # Reset to system memory and get Chip id.
    loader.reset_from_system_memory()
    # Get bootloader commands
    loader.get()
    # Write intel hex file
    ih = IntelHex()

    ih.loadhex('test.hex')
    # write
    data = ih.tobinarray()
    loader.write_memory_data(ih.minaddr(), data)


if __name__ == '__main__':
    sys.exit(main())
