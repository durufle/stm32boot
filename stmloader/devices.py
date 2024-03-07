# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Laurent Bonnet
#
# License: MIT
"""
Devices cli application
"""
import glob
import os
import shutil
from typing import List
from enum import Enum
import cerberus.validator
import typer
import yaml
from typing_extensions import Annotated
from cerberus import Validator
from .schema import template

try:
    import rich
    from rich.console import Console
    from rich.table import Table

    console_output = Console()
except ImportError:  # pragma: nocover
    rich = None

device_app = typer.Typer(help="Devices management cli")


def auto_desc_callback(files: []):
    """
    Check device description file format
    """
    for file in files:
        try:
            with open(file, 'r', encoding='UTF-8') as stream:
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


@device_app.command()
def list(ctx: typer.Context):
    """
    List supported devices
    """

    devices = []

    for f in ctx.obj['files']:
        with open(f, 'r', encoding='UTF-8') as file:
            elements = []
            device = yaml.safe_load(file)
            elements.append(device['DeviceID'])
            elements.append(device['Name'])
            elements.append(device['Series'])
            elements.append(device['CPU'])
            elements.append(device['Description'])
        devices.append(elements)

    if rich is None:
        for element in devices:
            print(f"0x{element[0]:X} , {element[1]}, {element[2]}, {element[3]}, {element[4]}")
    else:
        table = Table("Id", "Name", "Series", "Cpu", "Description")
        for device in devices:
            table.add_row(f"0x{device[0]:X}", f"{device[1]}", f"{device[2]}", f"{device[3]}", f"{device[4]}")
        console = Console()
        console.print(table)


class AddMode(str, Enum):
    """list by class"""
    CHECK = "check"
    COPY = "copy"


@device_app.command()
def add(ctx: typer.Context,
        files: Annotated[List[str], typer.Argument(callback=auto_desc_callback, help="Device description file(s).")],
        mode: Annotated[AddMode, typer.Option("--mode", "-m", help='Add mode.',
                                              case_sensitive=False)] = AddMode.CHECK,
        ):
    """
    Add device description
    """
    if mode == AddMode.COPY:
        for file in files:
            with open(file, 'r', encoding='UTF-8') as f:
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
