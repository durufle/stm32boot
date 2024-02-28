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
STM32 Bootloader over donjon-scaffold CLI
"""
from typing import Optional
from enum import Enum
from pathlib import Path
import typer
from typing_extensions import Annotated
from scaffold import Scaffold
from intelhex import IntelHex
from serial.serialutil import SerialException
from .bootloader import STM32, CommandError

app = typer.Typer(help="stm32 bootloader shell ", chain=True)


def auto_int_callback(value: str):
    """Convert to int with automatic base detection."""
    # This supports 0x10 == 16 and 10 == 10
    try:
        return int(value, 0)
    except ValueError as exc:
        print(f"Invalid value ({value}) !")
        raise typer.Exit(code=1) from exc


class ResetMode(str, Enum):
    """Reset mode enumerate"""
    SYSTEM = 'system'
    FLASH = "flash"


@app.command()
def reset(ctx: typer.Context,
          mode: Annotated[ResetMode, typer.Option(case_sensitive=False, help="Reset mode")] = ResetMode.SYSTEM,
          startup: Annotated[float, typer.Option(help="Minimum startup time")] = 0.1,
          ):
    """
    Reset to system/flash  memory command
    """
    if mode == 'system':
        ctx.obj['loader'].reset_from_system_memory(startup)
        ctx.obj['reset'] = True
    else:
        ctx.obj['loader'].reset_from_flash_memory(startup)


@app.command()
def read(ctx: typer.Context,
         address: Annotated[str, typer.Option(callback=auto_int_callback, help="Starting address")] = '0x08000000',
         length: Annotated[int, typer.Option(help="Length to read")] = 0,
         file: Annotated[Optional[str], typer.Argument(help="Output Intel hex file name")] = None,
         ):
    """
    Read memory command
    """
    if ctx.obj['reset'] is not True:
        raise typer.Exit()
    data = ctx.obj['loader'].read_memory_data(address, length)
    ih = IntelHex()
    ih.frombytes(data, address)
    ih.dump()
    if file:
        ih.write_hex_file(file)


@app.command()
def write(ctx: typer.Context,
          address: Annotated[str, typer.Option(callback=auto_int_callback, help="Starting address")] = '0x08000000',
          file: Annotated[Optional[str], typer.Argument(help="File to write")] = None,
          verify: Annotated[bool, typer.Option(help="Write verify")] = False):
    """
    Write memory command
    """
    if ctx.obj['reset'] is not True:
        raise typer.Exit()
    ih = IntelHex()
    if Path(file).suffix in ['.BIN', '.bin']:
        ih.loadbin(file, offset=address)
    elif Path(file).suffix in ['.HEX', '.hex']:
        ih.loadhex(file)
    # write a chunks
    data = ih.tobinarray()
    ctx.obj.loader.write_memory_data(ih.minaddr(), data)
    if verify:
        length = ih.maxaddr() - ih.minaddr() + 1
        offset = ih.minaddr()
        reload = ctx.obj['loader'].read_memory_data(offset, length)
        ctx.obj['loader'].debug(0, "Verification successfully" if (data == reload) else "Verification failed")


class EraseMode(str, Enum):
    """
    Erase mode enumerate
    """
    NONE = 'None'
    MASS = "mass"
    BANK1 = "bank1"
    BANK2 = "bank2"


@app.command()
def erase(ctx: typer.Context,
          address: Annotated[str, typer.Option(callback=auto_int_callback, help="Starting address")] = '0x08000000',
          length: Annotated[int, typer.Option(help="Length to erase")] = 0,
          mode: Annotated[EraseMode, typer.Option(help='Erase extended mode', case_sensitive=False)] = EraseMode.NONE,
          ):
    """
    Erase memory command
    """
    if ctx.obj['reset'] is not True:
        raise typer.Exit()
    try:
        if ctx.obj.loader.extended_erase and mode != EraseMode.NONE:
            ctx.obj['loader'].extended_erase_special(special=mode)
            raise typer.Exit()
        if address and length:
            pages = ctx.obj['loader'].pages_from_range(address, int(address) + length)
            ctx.obj['loader'].erase_memory(pages=pages)
            return
    except CommandError as e:
        # may be caused by readout protection
        ctx.obj['loader'].debug(0, e)
        ctx.obj['loader'].reset_from_flash()
        raise typer.Exit()


class GetInfo(str, Enum):
    """
    Get command enumerate
    """
    VERSION = "version"
    IDENTIFIER = "identifier"
    COMMAND = 'command'
    FLASH = "flash"


@app.command()
def get(ctx: typer.Context,
        info: Annotated[GetInfo, typer.Option(case_sensitive=False, help="Get information")] = GetInfo.VERSION):
    """
    Get information command
    """
    if ctx.obj['reset'] is not True:
        raise typer.Exit()
    if info == GetInfo.VERSION:
        ctx.obj['loader'].get_version()
    if info == GetInfo.IDENTIFIER:
        ctx.obj['loader'].get_id()
    if info == GetInfo.COMMAND:
        ctx.obj['loader'].get()


@app.command()
def go(ctx: typer.Context,
       address: Annotated[str, typer.Option(callback=auto_int_callback, help="Starting address")] = '0x08000000',
       ):
    """
    Go command
    """
    if ctx.obj['reset'] is not True:
        raise typer.Exit()
    ctx.obj['loader'].go(address)


class ProtecMode(str, Enum):
    """
    Erase mode enumerate
    """
    READ = 'Read'
    WRITE = "Write"


class ProtecState(str, Enum):
    """
    Erase mode enumerate
    """
    ENABLE = 'enable'
    DISABLE = 'disable'


@app.command()
def protect(ctx: typer.Context,
            mode: Annotated[ProtecMode, typer.Option(case_sensitive=False, help="Protection mode")] = ProtecMode.READ,
            state: Annotated[
                ProtecState, typer.Option(case_sensitive=False, help="Protection state")] = ProtecState.DISABLE,
            ):
    """
    protection command
    """
    if ctx.obj['reset'] is not True:
        raise typer.Exit()
    if mode == "Read" and state == 'disable':
        ctx.obj['loader'].readout_unprotect()
    elif mode == "Read" and state == 'enable':
        ctx.obj['loader'].readout_protect()
    else:
        ctx.obj['loader'].debug(0, f"Operation protect {mode} {state} not yet supported")


@app.callback()
def main(ctx: typer.Context,
         port: Annotated[str, typer.Option(help="Scaffold Communication port")] = '/dev/ttyUSB0',
         family: Annotated[str, typer.Option(help="Target family")] = '',
         verbose: Annotated[int, typer.Option(help="Verbosity level")] = 5,
         ):
    """
    Command callback
    """
    try:
        loader = STM32(Scaffold(port), family=family, verbosity=verbose)
        # save object into the context
        if ctx.obj is None:
            ctx.obj = {}
        ctx.obj['loader'] = loader
        ctx.obj['reset'] = False

    except SerialException as exc:
        pass

