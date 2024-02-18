# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Laurent Bonnet, 2024 python-gitlab team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
""" stm3éboot main entry """
import sys
from .subcommands.donjon import CommandError, DataLengthError, PageIndexError
from .subcommands.commands import Commands


def main():
    """
    stm32boot cli entry
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
