# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Laurent Bonnet
#
# License: MIT
"""
Example on Erase command
"""
import sys
from scaffold import Scaffold
from stmloader.bootloader import STM32


def main():
    """
    Mass erase id extended mode supported
    @return:
    """
    # Open connection with scaffold (port auto-detection)
    loader = STM32(Scaffold())
    # Reset to system memory and get Chip id.
    loader.reset_from_system_memory()
    # Get bootloader commands
    loader.get()
    # mass erase (if supported. The information is return by the GET command)
    if loader.extended_erase:
        loader.extended_erase_special('mass')
    else:
        print("Mass Erase not supported !")


if __name__ == '__main__':
    sys.exit(main())
