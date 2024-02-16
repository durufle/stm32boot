#!/usr/bin/env python
import sys
import os
import argparse
from donjon import STM32, CommandError, DataLengthError, PageIndexError
from scaffold import Scaffold
from intelhex import IntelHex
from pathlib import Path
from donjon import CommandError


def auto_int(x):
    """Convert to int with automatic base detection."""
    # This supports 0x10 == 16 and 10 == 10
    return int(x, 0)


def valid_file(param):
    base, ext = os.path.splitext(param)
    if ext.lower() not in ('.bin', '.hex'):
        raise argparse.ArgumentTypeError('File must have a bin or hex extension')
    return param


class STM32Boot:
    def __init__(self, arguments):
        self.scaffold = None
        self.loader = None
        if not arguments:
            arguments = ('get', '-i')
        self.config = self.parse_arguments(arguments)

    def parse_arguments(self, arguments):
        """Parse the given command-line arguments and return the configuration."""

        parser = argparse.ArgumentParser(prog="stm32boot")
        subparsers = parser.add_subparsers()
        # --------------------------------------------------------------------------------------------------------------
        # reader command subgroup
        # --------------------------------------------------------------------------------------------------------------
        parser_read = subparsers.add_parser('read', help='Read  command from flash')
        parser_read.add_argument(
            "-l", "--length", action="store", type=auto_int, required=True,
            help="Length of read"
        )
        parser_read.add_argument(
            "-a", "--address", action="store", type=auto_int, default=0x08000000, required=False,
            help="Target address for read.",
        )
        parser_read.add_argument(
            "-d", "--display", action="store_true", default=False, required=False,
            help="Display file content in intel hex format.",
        )
        parser_read.add_argument(
            "file", type=valid_file, nargs="?", help="File to read from flash.",
        )

        parser_read.set_defaults(func=self.read)
        # --------------------------------------------------------------------------------------------------------------
        # write command subgroup
        # --------------------------------------------------------------------------------------------------------------
        parser_write = subparsers.add_parser('write', help='Write file to flash command.')
        parser_write.add_argument(
            "-l", "--length", action="store", type=auto_int, required=False,
            help="Length data to write."
        )
        parser_write.add_argument(
            "-a", "--address", action="store", type=auto_int, default=0x08000000, required=False,
            help="Target address for write.",
        )
        parser_write.add_argument(
            "-v", "--verify", action="store_true", default=False, required=False,
            help="Perform a verification process after write.",
        )
        parser_write.add_argument(
            "file", type=valid_file, nargs="?", help="File to write in flash.",
        )
        parser_write.set_defaults(func=self.write)

        # --------------------------------------------------------------------------------------------------------------
        # erase command subgroup
        # --------------------------------------------------------------------------------------------------------------

        parser_erase = subparsers.add_parser('erase', help='Erase flash command')
        parser_erase.add_argument(
            "-l", "--length", action="store", type=auto_int, default=0, required=False,
            help="Length of erase in page mode."
        )

        parser_erase.add_argument(
            "-a", "--address", action="store", type=auto_int, default=0x08000000, required=False,
            help="Target address for write.",
        )
        parser_erase.add_argument(
            "-m", "--modes", action="store", type=str, choices=['None', 'mass', 'bank1', 'bank2'],
            default='None', required=False, help="Erase flash using special modes."
        )
        parser_erase.set_defaults(func=self.erase)
        # --------------------------------------------------------------------------------------------------------------
        # get command
        # --------------------------------------------------------------------------------------------------------------
        parser_get = subparsers.add_parser('get', help='Get information command')
        parser_get.add_argument(
            "-i", "--identifier", action="store_true", required=False, help="Get target identifier."
        )
        parser_get.add_argument(
            "-v", "--version", action="store_true", required=False, help="Get bootloader version."
        )
        parser_get.add_argument(
            "-s", "--size", action="store_true", required=False, help="Get flash size."
        )
        parser_get.set_defaults(func=self.get_command)
        # --------------------------------------------------------------------------------------------------------------
        # readout command
        # --------------------------------------------------------------------------------------------------------------
        parser_readout = subparsers.add_parser('readout', help='Flash memory protection ')
        parser_readout.add_argument(
            "-u", "--unprotect", action="store_true", required=False, help="Readout unprotect."
        )
        parser_readout.add_argument(
            "-p", "--protect", action="store_true", required=False, help="Readout protect."
        )
        parser_readout.set_defaults(func=self.readout)
        # --------------------------------------------------------------------------------------------------------------
        # go command
        # --------------------------------------------------------------------------------------------------------------
        parser_go = subparsers.add_parser('go', help='Start executing from address.')
        parser_go.add_argument(
            "-a", "--address", action="store", type=auto_int, default=0x08000000, required=False,
            help="Starting address.",
        )
        parser_go.set_defaults(func=self.readout)

        # --------------------------------------------------------------------------------------------------------------
        # global command
        # --------------------------------------------------------------------------------------------------------------
        parser.add_argument(
            "-p", "--port", action="store", type=str, required=False,
            help="Serial port (e.g. /dev/ttyUSB0. If None, tries to find automatically the device by scanning USB "
                 "description strings."
        )

        parser.add_argument(
            "-b", "--baud", action="store", type=int, default=115200, help="Baudrate.(115200 by default)"
        )

        parser.add_argument(
            "-v", "--verbose", dest="verbosity", action="store_const", const=10, default=5, help="Verbose mode."
        )

        parser.add_argument(
            "-q", "--quiet", dest="verbosity", action="store_const", const=0, help="Quiet mode."
        )
        default_family = os.environ.get("STM32LOADER_FAMILY")
        parser.add_argument(
            "-f", "--family", action="store", type=str, default=default_family,
            help=(
                    "Device family to read out device UID and flash size. "
                    + ("." if default_family else " (default: $STM32LOADER_FAMILY).")
            ),
        )
        return parser.parse_args(arguments)

    def connect(self):
        try:
            # Connect to Scaffold board
            self.scaffold = Scaffold(self.config.port)
            self.loader = STM32(self.scaffold, verbosity=self.config.verbosity)
            # start from system area
            self.loader.reset_from_system_memory()
        except Exception as e:
            print(e)
            sys.exit(-1)

    def get_command(self, args):
        if args.identifier:
            self.get_id()
        if args.version:
            self.get_version()
        if args.size:
            self.get_flash_size()

    def get(self):
        return self.loader.get()

    def get_id(self):
        return self.loader.get_id()

    def get_version(self):
        return self.loader.get_version()

    def get_uid(self):
        return self.loader.get_uid(self.config.family)

    def get_flash_size(self):
        return self.loader.get_flash_size(self.config.family)

    def readout(self, args):
        if args.unprotect:
            try:
                self.loader.readout_unprotect()
            except CommandError:
                self.loader.debug(0, "Flash readout unprotect failed")
                self.loader.debug(0, "Quit")
                self.loader.reset_from_flash()
                sys.exit(1)
        if args.protect:
            try:
                self.loader.readout_protect()
            except CommandError:
                self.loader.debug(0, "Flash readout unprotect failed")
                self.loader.debug(0, "Quit")
                self.loader.reset_from_flash()
                sys.exit(1)

    def read(self, args):
        data = self.loader.read_memory_data(args.address, args.length)
        ih = IntelHex()
        ih.frombytes(data, args.address)
        if args.display:
            ih.dump()
        if args.file:
            ih.write_hex_file(args.file)

    def write(self, args):
        ih = IntelHex()
        if Path(args.file).suffix in ['.BIN', '.bin']:
            ih.loadbin(args.file, offset=args.address)
        elif Path(args.file).suffix in ['.HEX', '.hex']:
            ih.loadhex(args.file)
        # write a chunks
        data = ih.tobinarray()
        self.loader.write_memory_data(ih.minaddr(), data)
        if args.verify:
            length = ih.maxaddr() - ih.minaddr() + 1
            offset = ih.minaddr()
            reload = self.loader.read_memory_data(offset, length)
            self.loader.debug(0, "Verification successfully" if (data == reload) else "Verification failed")

    def erase(self, args):
        try:
            if self.loader.extended_erase:
                if args.modes != 'None':
                    self.loader.extended_erase_special(special=args.modes)
                    return
                elif args.address and args.length:
                    pages = self.loader.pages_from_range(args.address, args.address + args.length)
                    self.loader.extended_erase_pages(pages=pages)
                    return
            elif args.address and args.length:
                pages = self.loader.pages_from_range(args.address, args.address + args.length)
                self.loader.erase_memory(pages=pages)
                return

        except CommandError as e:
            # may be caused by readout protection
            self.loader.debug(0, e)
            self.loader.reset_from_flash()
            sys.exit(1)

    def go(self, args):
        self.loader.go(args.address)

    def perform_commands(self):
        """Run all operations as defined by the configuration."""
        self.config.func(self.config)


def main(*arguments, **kwargs):
    """
    """
    boot = STM32Boot(arguments)
    boot.connect()
    boot.get()
    try:
        boot.perform_commands()
    except (CommandError, DataLengthError, PageIndexError) as e:
        print(e)
        sys.exit(-1)


if __name__ == "__main__":
    main(*sys.argv[1:])
