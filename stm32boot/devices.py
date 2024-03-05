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
"""
Devices cli application
"""
import glob
import os
import importlib.util

import cerberus.validator
import typer
import yaml
import shutil
from typing import List
from typing_extensions import Annotated
from enum import Enum
from cerberus import Validator
from .schema import template

device_app = typer.Typer(help="Devices management cli")


def auto_desc_callback(files: list):
    """
    Check device description file format
    """
    for file in files:
        try:
            with open(file, 'r') as stream:
                try:
                    doc = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    raise typer.Exit(code=1) from exc
        except FileNotFoundError as e:
            print(f"{e}")
            raise typer.Exit(code=-1)

        v = Validator()
        try:
            if not v.validate(doc, template):
                print(f"{v.errors} in file {file}")
        except cerberus.validator.DocumentError as exc:
            print(f"{exc} in file {file}")
            raise typer.Exit(code=-2) from exc
    return files


class ListMode(str, Enum):
    """list by class"""
    Basic = "Basic"


@device_app.command()
def list(ctx: typer.Context):
    """
    List supported devices
    """

    devices = []

    for f in ctx.obj['files']:
        with open(f, 'r') as file:
            elements = []
            device = yaml.safe_load(file)
            elements.append(device['DeviceID'])
            elements.append(device['Name'])
            elements.append(device['Series'])
            elements.append(device['CPU'])
            elements.append(device['Description'])
        devices.append(elements)

    if importlib.util.find_spec('rich') is None:
        for element in devices:
            print(f"0x{element[0]:X} , {element[1]}, {element[2]}, {element[3]}, {element[4]}")
    else:
        from rich.console import Console
        from rich.table import Table
        table = Table("Id", "Name", "Series", "Cpu", "Description")
        for device in devices:
            table.add_row(f"0x{device[0]:X}", f"{device[1]}", f"{device[2]}", f"{device[3]}", f"{device[4]}")
        console = Console()
        console.print(table)


class AddMode(str, Enum):
    """list by class"""
    check = "check"
    copy = "copy"


@device_app.command()
def add(ctx: typer.Context,
        files: Annotated[List[str], typer.Argument(callback=auto_desc_callback, help="Device description file(s).")],
        mode: Annotated[AddMode, typer.Option("--mode", "-m", help='Add mode.',
                                              case_sensitive=False)] = AddMode.check,
        ):
    """
    Add device description
    """
    if mode == AddMode.copy:
        for file in files:
            with open(file, 'r') as f:
                description = yaml.safe_load(f)
            # get device id
            ident = f"0x{description['DeviceID']:X}"
            # copy to  destination file
            shutil.copy(file, os.path.join(ctx.obj['path'], f'stm32_{ident}.yml'))


@device_app.callback()
def main(ctx: typer.Context):
    """
    Application callback
    @param ctx: application context
    """
    path = os.path.join(os.path.dirname(__file__), 'data')
    # create list of devices files found in data folder
    files = glob.glob(pathname=f'{path}/stm32_*.yml')
    if ctx.obj is None:
        ctx.obj = {}
    # add data path and files list object into context
    ctx.obj['path'] = path
    ctx.obj['files'] = files
