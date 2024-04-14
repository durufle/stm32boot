# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Laurent Bonnet
#
# License: MIT
"""
Exemple on connect dveice
"""
import sys
from scaffold import Scaffold
from stmloader.bootloader import STM32


def main():
    """
    Simple connection - get commands
    @return:
    """
    # Open connection with scaffold (port auto-detection)
    loader = STM32(Scaffold())
    # Reset to system memory and get Chip id.
    loader.reset_from_system_memory()
    # Get bootloader commands
    loader.get()


if __name__ == '__main__':
    sys.exit(main())
