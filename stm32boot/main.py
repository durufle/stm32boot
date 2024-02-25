from typing import Optional, List
from enum import Enum
from pathlib import Path
import typer
from typing_extensions import Annotated
from scaffold import Scaffold
from intelhex import IntelHex

from .bootloader import STM32, CommandError

app = typer.Typer(help="stm32 bootloader shell ", chain=True)


@app.command()
def reset(ctx: typer.Context,
          startup: Annotated[float, typer.Option(help="Minimum startup time")] = 2.7,
          ):
    """
    Reset to system memory command
    """
    ctx.obj['loader'].reset_from_system_memory(startup)
    ctx.obj['reset'] = True


@app.command()
def read(ctx: typer.Context,
         address: Annotated[int, typer.Option(help="Starting address")] = 0x08000000,
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
          address: Annotated[int, typer.Option(help="Starting address")] = 0x08000000,
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
    none = 'None'
    mass = "mass"
    bank1 = "bank1"
    bank2 = "bank2"


@app.command()
def erase(ctx: typer.Context,
          mode: Annotated[EraseMode, typer.Option(help='Erase extended mode', case_sensitive=False)] = EraseMode.none,
          address: Annotated[int, typer.Option(help="Starting address")] = 0x08000000,
          length: Annotated[int, typer.Option(help="Length to erase")] = 0,
          ):
    """
    Erase memory command
    """
    if ctx.obj['reset'] is not True:
        raise typer.Exit()
    try:
        if ctx.obj.loader.extended_erase and mode != EraseMode.none:
            ctx.obj['loader'].extended_erase_special(special=mode)
            raise typer.Exit()
        if address and length:
            pages = ctx.obj['loader'].pages_from_range(address, address + length)
            ctx.obj['loader'].erase_memory(pages=pages)
            return
    except CommandError as e:
        # may be caused by readout protection
        ctx.obj['loader'].debug(0, e)
        ctx.obj['loader'].reset_from_flash()
        raise typer.Exit()


class GetInfo(str, Enum):
    version = "version"
    identifier = "identifier"
    command = 'command'
    flash = "flash"


@app.command()
def get(ctx: typer.Context,
        info: Annotated[GetInfo, typer.Option(case_sensitive=False, help="Get information")] = GetInfo.version):
    """
    Get information command
    """
    if ctx.obj['reset'] is not True:
        raise typer.Exit()
    if info == GetInfo.version:
        ctx.obj['loader'].get_version()
    if info == GetInfo.identifier:
        ctx.obj['loader'].get_id()
    if info == GetInfo.command:
        ctx.obj['loader'].get()


@app.callback()
def main(ctx: typer.Context,
         port: Annotated[str, typer.Option(help="Scaffold Communication port")] = '/dev/ttyUSB0',
         family: Annotated[str, typer.Option(help="Target family")] = '',
         verbose: Annotated[int, typer.Option(help="Verbosity level")] = 5,
         ):

    try:
        loader = STM32(Scaffold(port), family=family, verbosity=verbose)
        # save object into the context
        if ctx.obj is None:
            ctx.obj = dict()
        ctx.obj['loader'] = loader
        ctx.obj['reset'] = False

    except Exception:
        raise typer.Exit(code=1)
