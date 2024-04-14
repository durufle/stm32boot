import os
import sys
import logging
import argparse

import scaffold
import yaml
import binascii
import serial.tools.list_ports
from scaffold import Scaffold
from time import sleep
from time import time
from gooey import Gooey, GooeyParser


class Ceva:
    """
    Class to control Nordic nRF53XX with donjon-scaffold board

    DO: Rx PIN
    D1: Tx PIN
    D2: RST PIN
    D4: Pulse start
    D5: Pulse Out

    """

    def __init__(self, timeout, dev, trigger=False) -> None:
        self.scaffold = Scaffold(dev)
        self.scaffold.timeout = timeout
        # Reset signal
        self.nrst = self.scaffold.d2
        # boot signals
        self.boot0 = self.scaffold.d6
        self.boot1 = self.scaffold.d7
        self.clock = self.scaffold.clock0
        # Connect the UART peripheral to D0 and D1.
        self.uart = self.scaffold.uart0
        self.uart.rx << self.scaffold.d1
        self.scaffold.d0 << self.uart.tx
        # Output uart trigger on D5
        self.scaffold.d5 << self.uart.trigger
        self.uart.baudrate = 115200
        self.uart.flush()
        self.trigger = trigger

    def send(self, data):
        self.uart.transmit(binascii.unhexlify(data), trigger=self.trigger)

    def read(self, number=1):
        try:
            return binascii.hexlify(self.uart.receive(number)).decode().upper()
        except scaffold.TimeoutError as e:
            print(e)
            sys.exit(-1)

    def command(self, data, number):
        self.uart.flush()
        self.send(data)
        sleep(0.10)
        return self.read(number)

    def reset(self, wait=0.1, frequency=1e6):
        """
        Perform a cold reset -  A complete power on and reset sequence
        """
        # dut power off and reset rst signal
        self.scaffold.power.dut = 0
        var = self.boot0 << 0
        var = self.boot1 << 0
        var = self.nrst << 0
        sleep(0.1)
        # clock value > 0 -> external clock s
        if frequency > 0:
            self.clock.frequency = frequency
            self.clock.out >> self.scaffold.a0

        # dut power on and set rst signal
        self.scaffold.power.dut = 1
        sleep(0.1)
        var = self.nrst << 1
        sleep(wait)


@Gooey(program_name='CEVAL')
def main():
    parser = GooeyParser(description='This script uses Scaffold to communicate with CEVAL firmware')

    # Create serial interface list
    choices = []
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        choices.append(port)

    parser.add_argument('-f', '--file', default='ceval_stm32l4xx.yaml', help='specify a yaml configuration file', widget='FileChooser')
    parser.add_argument('-d', '--dev', choices=choices, help='scaffold serial device path')
    parser.add_argument('-i', '--iteration', default=1, help='command iteration number')
    parser.add_argument('-w', '--waiting', type=float, default=1, help='uart reception timeout')
    parser.add_argument('-t', '--trigger', action="store_true", default=False, help='uart transmission trigger')
    parser.add_argument('-s', '--scenario', default='aes', choices=['aes'], help='ceva command')
    parser.add_argument('-c', '--clock', type=float, default=1e6, help='Target external clock frequency value')
    parser.add_argument('-l', '--log', action="store_true", default=False, help='Enable or disable logging in file')
    args = parser.parse_args()

    # get script path
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # open yaml file
    config = os.path.join(current_dir, args.file)
    try:
        with open(config, 'r') as file:
            cfg = yaml.safe_load(file)
    except FileNotFoundError as e:
        print(f"Configuration file opening error: {e}")
        sys.exit(-1)

    # create log file
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)

    # log file name is composed of configuration file name and a timestamp.
    if args.log:
        stamp = "%d" % time()
        name = os.path.splitext(config)[0] + "_" + stamp + ".log"
        file = logging.FileHandler(name)
        file_format = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        file.setFormatter(file_format)
        log.addHandler(file)

    stream = logging.StreamHandler()
    stream_format = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    stream.setFormatter(stream_format)
    log.addHandler(stream)

    try:
        # Connect to Scaffold board
        ceva = Ceva(timeout=args.waiting, dev=args.dev)
    except Exception as e:
        print(e)
        sys.exit(-1)

    # power reset
    ceva.reset(frequency=args.clock)
    ceva.trigger = args.trigger

    if args.scenario == 'aes':
        """
        Test aes command
        """
        for k in range(0, int(args.iteration)):
            resp = ceva.command("FE8A00020020" + cfg['aes']['key'] + cfg['aes']['plain'], number=16)
            log.info(f"{resp.strip()}, iteration={k + 1}")


if __name__ == "__main__":
    main()
