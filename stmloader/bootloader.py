# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Laurent Bonnet
#
# License: MIT


"""
Bootloader command donjon-scaffold interface
"""
import dataclasses
import sys
import os
import operator
import struct
import math
from time import sleep
from functools import reduce
import yaml
from progressbar import ProgressBar, Percentage, GranularBar, AdaptiveETA


class STM32Error(Exception):
    """Generic exception type for errors occurring in stm32loader."""


class CommandError(STM32Error, IOError):
    """Exception: a command in the STM32 native bootloader failed."""


class DataLengthError(STM32Error, ValueError):
    """Exception: invalid data length given."""


class PageIndexError(STM32Error, ValueError):
    """Exception: invalid page index given."""


class STM32:
    """
    Class for instrumenting STM32 devices using Scaffold board and API. The
    following Scaffold IOs are used:

    - D0: STM32 UART MCU RX pin, Scaffold UART TX
    - D1: STM32 UART MCU TX pin, Scaffold UART RX
    - D2: STM32 NRST pin for reset
    - D6: STM32 BOOT0 pin
    - D7: STM32 BOOT1 pin

    The uart0 peripheral of Scaffold board is used for serial communication
    with the ST bootloader.

    This class can communicate with the ST bootloader via USART1. This allows
    programming the Flash memory and then execute the loaded code.
    """

    @dataclasses.dataclass
    class Command:
        """STM32 native bootloader command values."""

        # See ST AN3155, AN4872
        GET = 0x00
        GET_VERSION = 0x01
        GET_ID = 0x02
        READ_MEMORY = 0x11
        GO = 0x21
        WRITE_MEMORY = 0x31
        ERASE = 0x43
        READOUT_PROTECT = 0x82
        READOUT_UNPROTECT = 0x92
        # these not supported on BlueNRG
        EXTENDED_ERASE = 0x44
        WRITE_PROTECT = 0x63
        WRITE_UNPROTECT = 0x73
        # not really listed under commands, but still...
        # 'wake the bootloader' == 'activate USART' == 'synchronize'
        SYNCHRONIZE = 0x7F

    @dataclasses.dataclass
    class Reply:
        """STM32 native bootloader reply status codes."""
        # See ST AN3155, AN4872
        ACK = 0x79
        NACK = 0x1F

    UID_SWAP = [[1, 0], [3, 2], [7, 6, 5, 4], [11, 10, 9, 8]]
    # stmloader does not know the address for the unique ID.
    UID_ADDRESS_UNKNOWN = -1
    # Part do not support flash size.
    FLASH_SIZE_NOT_SUPPORTED = 0
    # stmloader does not know the address for flash size.
    FLASH_SIZE_ADDRESS_UNKNOWN = -1
    # default flash page size
    FLASH_PAGE_SIZE_DEFAULT = 1024
    BOOT_VERSION_ADDRESS_UNKNOWN = -1
    DATA_TRANSFER_SIZE_DEFAULT = 256
    SYNCHRONIZE_ATTEMPTS = 2

    def __init__(self, scaffold, verbosity=5):
        """
        Command class constructor
        @param scaffold: A scaffold object
        @param verbosity: verbosity level
        """
        self.scaffold = scaffold
        self.scaffold.timeout = 1
        self.nrst = scaffold.d2
        self.uart = uart = scaffold.uart0
        self.boot0 = scaffold.d6
        self.boot1 = scaffold.d7
        # Connect the UART peripheral to D0 and D1.
        var = uart.rx << scaffold.d1
        var = scaffold.d0 << uart.tx
        uart.baudrate = 115200

        self.verbosity = verbosity
        self.extended_erase = False
        self.data_transfer_size = self.DATA_TRANSFER_SIZE_DEFAULT
        self.flash_page_size = self.FLASH_PAGE_SIZE_DEFAULT
        self.uid_address = self.UID_ADDRESS_UNKNOWN
        self.flash_size_address = self.FLASH_SIZE_ADDRESS_UNKNOWN
        self.boot_version_address = self.BOOT_VERSION_ADDRESS_UNKNOWN

    def _write(self, *data):
        """
        Write the given data to the MCU.
        """
        for data_bytes in data:
            if isinstance(data_bytes, int):
                data_bytes = struct.pack("B", data_bytes)
            self.uart.transmit(data_bytes, False)

    def _write_and_ack(self, message, *data):
        """
        Write data to the MCU and wait until it replies with ACK.
        """
        # this is a separate method from write() because a keyword
        # argument after *args is not possible in Python 2
        self._write(*data)
        return self._wait_for_ack(message)

    def _wait_ack(self, info=""):
        """
        Wait for ACK byte.

        :param info: info which is set when error are thrown. Useful for error diagnostic.
        """
        data = self.uart.receive(1)[0]
        if data == self.Reply.NACK:
            raise CommandError("NACK " + info)
        if data != self.Reply.ACK:
            raise ValueError(f"Received 0x{data:02x} byte instead of ACK or NACK.")

    def _search_device(self, identifier):
        """
        Search if identifier is a known DeviceId
        @param identifier: Device ID number
        @return:
        """
        path = os.path.join(os.path.dirname(__file__), 'data')
        # create file name to search
        name = f'{path}/stm32_{hex(identifier)}.yml'
        if os.path.isfile(name):
            self.debug(10, f"Device File {name} found !")
            # Read device description file, and initialize internal variables
            with open(name, 'r', encoding='UTF-8') as f:
                desc = yaml.safe_load(f)
                self.uid_address = desc['UniversalID']['address']
                self.flash_size_address = desc['FlashSize']['address']
                self.flash_page_size = desc['Flash']['PageSize']
                self.boot_version_address = desc['Bootloader']['ID']

    def debug(self, level, message):
        """
        Print the given message if its level is low enough.
        :@param level: level compare to verbose
        :@param message: message to proit
        """
        if self.verbosity >= level:
            print(message, file=sys.stderr)

    def reset_from_system_memory(self, startup=2.7):
        """
        Power-cycle and reset target device in bootloader mode (boot on System
        Memory) and initiate serial communication. The byte 0x7f is sent and
        the response byte 0x79 (ACK) is expected. If the device does not
        respond, a Timeout exception is thrown by Scaffold. The device will not
        respond if it is locked in RDP2 state (Readout Protection level 2).
        statr
        """
        self.scaffold.power.dut = 0
        var = self.boot0 << 1
        var = self.boot1 << 0
        var = self.nrst << 0
        sleep(0.1)
        self.scaffold.power.dut = 1
        sleep(0.1)
        var = self.nrst << 1
        sleep(startup)

        # Send 0x7f byte for initiating communication
        self.uart.flush()
        for attempt in range(self.SYNCHRONIZE_ATTEMPTS):
            if attempt:
                print("Bootloader activation timeout -- retrying", file=sys.stderr)
            self._write(0, self.Command.SYNCHRONIZE)
            data = bytearray(self.uart.receive(1))
            if data and data[0] in (self.Reply.ACK, self.Reply.NACK):
                # successful. Check if known DeviceId
                self._search_device(self.get_id())
                return
        # not successful
        raise CommandError("Bad reply from bootloader")

    def reset_from_flash(self, startup=0.1):
        """
        Power-cycle and reset target device and boot from user Flash memory.
        """
        self.scaffold.power.dut = 0
        var = self.boot0 << 0
        var = self.boot1 << 0
        var = self.nrst << 0
        sleep(0.1)
        self.scaffold.power.dut = 1
        sleep(0.1)
        var = self.nrst << 1
        sleep(startup)

    def command(self, command, description):
        """
        Send the given command to the MCU.

        Raise CommandError if there's no ACK replied.
        """
        self.debug(10, f"*** Command: {description}")
        ack_received = self._write_and_ack("Command", command, command ^ 0xFF)
        if not ack_received:
            raise CommandError(f"{description} ({command}) failed: no ack")

    def get(self):
        """
        Execute the Get command of the bootloader, which returns the version
        and the supported commands.
        """
        self.command(command=self.Command.GET, description="Get")
        header = self.uart.receive(2)
        length = header[0]
        data = self.uart.receive(length)
        if self.Command.EXTENDED_ERASE in data:
            self.extended_erase = True
        self.debug(5, "Available commands: " + ", ".join(hex(b) for b in data))
        self._wait_for_ack(f"{self.Command.GET} end")
        return data

    def get_id(self):
        """
        Execute the Get ID command. The result is interpreted and the class
        will try to find information if the ID matches a known device.
        """
        self.command(command=self.Command.GET_ID, description="Get ID")
        length = self.uart.receive(1)[0]
        data = self.uart.receive(length + 1)
        self._wait_for_ack(f"{self.Command.GET_ID} end")
        device_id = reduce(lambda x, y: x * 0x100 + y, data)
        self.debug(5, f"Chip id: 0x{device_id:X}")
        return device_id

    def get_uid(self):
        """
        Send the 'Get UID' command and return the device UID.

        Return UID_ADDRESS_UNKNOWN if the device's UID address is not known.

        :return bytearray: UID bytes of the device, or 0 or -1 when
          not available.
        """
        if self.uid_address == self.UID_ADDRESS_UNKNOWN:
            return self.UID_ADDRESS_UNKNOWN
        uid = self.read_memory(self.uid_address, 12)
        self.debug(0, f"Device UID: {self.format_uid(uid)}")
        return uid

    @classmethod
    def format_uid(cls, uid):
        """Return a readable string from the given UID."""
        if uid == cls.UID_ADDRESS_UNKNOWN:
            return "UID address unknown"

        swapped_data = [[uid[b] for b in part] for part in STM32.UID_SWAP]
        uid_string = "-".join("".join(format(b, "02X") for b in part) for part in swapped_data)
        return uid_string

    def get_flash_size(self):
        """Return the MCU flash size in bytes."""
        if self.flash_size_address == self.FLASH_SIZE_ADDRESS_UNKNOWN:
            return self.FLASH_SIZE_NOT_SUPPORTED
        flash_size_bytes = self.read_memory(self.flash_size_address, 2)
        flash_size = flash_size_bytes[0] + (flash_size_bytes[1] << 8)
        self.debug(0, f"flash size {flash_size}")
        return flash_size

    def get_protocol_version(self):
        """
        Return the bootloader version

        Read protection status readout is not yet implemented.
        """
        self.command(command=self.Command.GET_VERSION, description="Get version")
        data = self.uart.receive(3)
        self._wait_for_ack(f"{self.Command.GET_VERSION} end")
        self.debug(5, "Bootloader protocol version: " + hex(data[0]))
        self.debug(5, "- Option byte 1: " + hex(data[1]))
        self.debug(5, "- Option byte 2: " + hex(data[2]))
        return data[1]

    def get_bootloader_id(self):
        """
        Return the Bootloader ID.

        Return BOOT_VERSION_ADDRESS_UNKNOWN if the bootloader's UID address is not known.
        """
        if self.boot_version_address == self.BOOT_VERSION_ADDRESS_UNKNOWN:
            return self.BOOT_VERSION_ADDRESS_UNKNOWN
        boot_id = hex(self.read_memory(self.boot_version_address, 1)[0])
        self.debug(0, f"Bootloader version (Id) : {boot_id}")
        return boot_id

    def read_memory(self, address, length):
        """
        Return the memory contents of flash at the given address.

        Supports maximum 256 bytes.

        :param address: Memory address to be read.
        :param length: Number of bytes to be read.
        """
        if length > self.data_transfer_size:
            raise DataLengthError("Can not read more than 256 bytes at once.")
        self.command(command=self.Command.READ_MEMORY, description="Read memory", )
        self._write_and_ack("0x11 address failed", self._encode_address(address))
        nr_of_bytes = (length - 1) & 0xFF
        checksum = nr_of_bytes ^ 0xFF
        self._write_and_ack("0x11 length failed", nr_of_bytes, checksum)
        return bytearray(self.uart.receive(length))

    def read_memory_data(self, address, length):
        """
        Tries to read some memory from the device. If requested size is larger
        than 256 bytes, many Read Memory commands are sent.

        :param address: Memory address to be read.
        :param length: Number of bytes to be read.
        """
        data = bytearray()
        chunk_count = int(math.ceil(length / float(self.data_transfer_size)))
        self.debug(10, f"Read {length:d} bytes in {chunk_count:d} chunks at address 0x{address:X}...")
        widgets = [
            ' ', Percentage(),
            ' ', GranularBar(),
            ' ', AdaptiveETA(),
        ]
        with ProgressBar(widgets=widgets, max_value=chunk_count) as progress:
            while length:
                read_length = min(length, self.data_transfer_size)
                self.debug(10, f"Read {read_length:d} bytes at {address:X}")
                data = data + self.read_memory(address, read_length)
                length = length - read_length
                address = address + read_length
                progress.next()
            return data

    def write_memory(self, address, data):
        """
        Write the given data to flash at the given address.

        Supports maximum 256 bytes.

        :param address: Address.
        :param data: Data to be written. bytes or bytearray.
        """
        nr_of_bytes = len(data)
        if nr_of_bytes == 0:
            return
        if nr_of_bytes > self.data_transfer_size:
            raise DataLengthError("Can not write more than 256 bytes at once.")
        self.command(self.Command.WRITE_MEMORY, "Write memory")
        self._write_and_ack("0x31 address failed", self._encode_address(address))

        # pad data length to multiple of 4 bytes
        if nr_of_bytes % 4 != 0:
            padding_bytes = 4 - (nr_of_bytes % 4)
            nr_of_bytes += padding_bytes
            # append value 0xFF: flash memory value after erase
            data = bytearray(data)
            data.extend([0xFF] * padding_bytes)

        self.debug(10, f"    [{nr_of_bytes}] bytes to write")
        checksum = reduce(operator.xor, data, nr_of_bytes - 1)
        self._write_and_ack("0x31 programming failed", nr_of_bytes - 1, data, checksum)
        self.debug(10, "    Write memory done")

    def write_memory_data(self, address, data):
        """
        Write the given data to flash.

        Data length may be more than 256 bytes.
        """
        length = len(data)
        chunk_count = int(math.ceil(length / float(self.data_transfer_size)))
        offset = 0
        self.debug(10, f"Write {length:d} bytes in {chunk_count}d chunks at address 0x{address:X}...")
        widgets = [
            ' ', Percentage(),
            ' ', GranularBar(),
            ' ', AdaptiveETA(),
        ]
        with ProgressBar(widgets=widgets, max_value=chunk_count) as progress:
            while length:
                write_length = min(length, self.data_transfer_size)
                self.debug(
                    10,
                    "Write %(len)d bytes at 0x%(address)X"
                    % {"address": address, "len": write_length},
                )
                self.write_memory(address, data[offset: offset + write_length])
                length -= write_length
                offset += write_length
                address += write_length
                progress.next()

    def readout_protect(self):
        """Enable readout protection of the flash memory."""
        self.command(self.Command.READOUT_PROTECT, "Readout protect")
        self.debug(10, "    Read protect done")

    def readout_unprotect(self):
        """
        Execute the Readout Unprotect command. If the device is locked, it will
        perform mass flash erase, which can be very long.
        """
        self.command(self.Command.READOUT_UNPROTECT, "Readout unprotect")
        self.debug(10, "    Mass erase -- this may take a while")
        previous_timeout = self.scaffold.timeout
        self.scaffold.timeout = 30
        try:
            self._wait_ack()
        finally:
            # Restore timeout setting, even if something bad happened!
            self.scaffold.timeout = previous_timeout
        self.debug(10, "    Unprotect / mass erase done")
        self.debug(10, "    Reset after automatic chip reset due to readout unprotect")
        self.reset_from_system_memory()

    def write_protect(self, pages):
        """Enable write protection on the given flash pages."""
        self.command(self.Command.WRITE_PROTECT, "Write protect")
        nr_of_pages = (len(pages) - 1) & 0xFF
        page_numbers = bytearray(pages)
        checksum = reduce(operator.xor, page_numbers, nr_of_pages)
        self._write_and_ack("0x63 write protect failed", nr_of_pages, page_numbers, checksum)
        self.debug(10, "    Write protect done")

    def write_unprotect(self):
        """Disable write protection of the flash memory."""
        self.command(self.Command.WRITE_UNPROTECT, "Write unprotect")
        self._wait_for_ack("0x73 write unprotect failed")
        self.debug(10, "    Write Unprotect done")

    def extended_erase_pages(self, pages=None):
        """
        Execute the Extended Erase command to erase all the Flash memory of the device.
        """
        self.command(self.Command.EXTENDED_ERASE, "Extended erase memory")
        if pages:
            # page erase, see ST AN3155
            if len(pages) > 65535:
                raise PageIndexError(
                    "Can not erase more than 65535 pages at once.\n"
                    "Set pages to None to do global erase or supply fewer pages."
                )
            page_count = (len(pages) & 0xFFFF) - 1
            page_count_bytes = bytearray(struct.pack(">H", page_count))
            page_bytes = bytearray(len(pages) * 2)
            for i, page in enumerate(pages):
                struct.pack_into(">H", page_bytes, i * 2, page)
            checksum = reduce(operator.xor, page_count_bytes)
            checksum = reduce(operator.xor, page_bytes, checksum)
            self.debug(level=10, message=f"Page erase mode ({page_count} pages)")
            self._write(page_count_bytes, page_bytes, checksum)
        previous_timeout = self.scaffold.timeout
        self.scaffold.timeout = 30
        try:
            self._wait_for_ack("0x44 erasing failed")
        finally:
            self.scaffold.timeout = previous_timeout
        self.debug(10, "    Extended Erase memory done")

    def extended_erase_special(self, special=None):
        """
        Execute the Extended Erase command to erase all the Flash memory of the device.
        """
        self.command(self.Command.EXTENDED_ERASE, "Extended erase memory")
        if special == 'mass':
            self.debug(level=10, message="Mass erase mode ")
            self._write(b"\xff\xff\x00")

        if special == 'bank1':
            self.debug(level=10, message="Bank 1 erase mode ")
            self._write(b"\xff\xfe\x01")

        if special == 'bank2':
            self.debug(level=10, message="Bank 2 erase mode ")
            self._write(b"\xff\xfd\x02")
        previous_timeout = self.scaffold.timeout
        self.scaffold.timeout = 30
        try:
            self._wait_for_ack("0x44 erasing failed")
        finally:
            self.scaffold.timeout = previous_timeout
        self.debug(10, "Extended Erase memory done")

    def erase_memory(self, pages=None):
        """
        Erase flash memory at the given pages.

        Set pages to None to erase the full memory.
        :param iterable pages: Iterable of integer page addresses, zero-based.
          Set to None to trigger global mass erase.
        """
        self.command(self.Command.ERASE, "Erase memory")
        if pages:
            # page erase, see ST AN3155
            if len(pages) > 255:
                raise PageIndexError(
                    "Can not erase more than 255 pages at once.\n"
                    "Set pages to None to do global erase or supply fewer pages."
                )
            page_count = (len(pages) - 1) & 0xFF
            page_numbers = bytearray(pages)
            checksum = reduce(operator.xor, page_numbers, page_count)
            self._write(page_count, page_numbers, checksum)
        else:
            # global erase: n=255 (page count)
            self._write(255, 0)

        self._wait_for_ack("0x43 erase failed")
        self.debug(10, "    Erase memory done")

    def go(self, address):
        """
        Execute the Go command.

        :param address: Jump to address.
        """
        # pylint: disable=invalid-name
        self.command(self.Command.GO, "Go")
        self._write_and_ack("0x21 go failed", self._encode_address(address))

    def pages_from_range(self, start, end):
        """Return page indices for the given memory range."""
        if start % self.flash_page_size != 0:
            raise PageIndexError(f"Erase start address should be at a flash page boundary: 0x{start:08X}.")
        if end % self.flash_page_size != 0:
            raise PageIndexError(f"Erase end address should be at a flash page boundary: 0x{end:08X}.")

        # Assemble the list of pages to erase.
        first_page = start // self.flash_page_size
        last_page = end // self.flash_page_size
        num_pages = last_page - first_page
        pages = list(range(num_pages))

        return pages

    def _wait_for_ack(self, info=""):
        """Read a byte and raise CommandError if it's not ACK."""
        reply = self.uart.receive(1)[0]
        if not reply:
            raise CommandError("Can't read port or timeout")

        if reply == self.Reply.NACK:
            raise CommandError("NACK " + info)
        if reply != self.Reply.ACK:
            raise CommandError("Unknown response. " + info + ": " + hex(reply))
        return 1

    @staticmethod
    def _encode_address(address):
        """Return the given address as big-endian bytes with a checksum."""
        # address in four bytes, big-endian
        address_bytes = bytearray(struct.pack(">I", address))
        # checksum as single byte
        checksum_byte = struct.pack("B", reduce(operator.xor, address_bytes))
        return address_bytes + checksum_byte
