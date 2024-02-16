# STM32 Bootloader utility with scaffold v1.1

Python module to upload or download firmware to / from ST Microelectronics STM32 microcontrollers over scaffold.
Some utility command are also accessible.

## Installation

```bash
pip install stm32boot
```
To install the latest development version

```bash
pip install git+https://github.com/durufle/stm32boot.git
```

## Usage

```bash
usage: stm32boot [-h] [-p PORT] [-b BAUD] [-v] [-q] [-f FAMILY] {read,write,erase,get,readout,go} ...

positional arguments:
  {read,write,erase,get,readout,go}
    read                Read command from flash
    write               Write file to flash command.
    erase               Erase flash command
    get                 Get information command
    readout             Flash memory protection
    go                  Start executing from address.

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Serial port (e.g. /dev/ttyUSB0. If None, tries to find automatically the device by scanning USB description strings.
  -b BAUD, --baud BAUD  Baudrate.(115200 by default)
  -v, --verbose         Verbose mode.
  -q, --quiet           Quiet mode.
  -f FAMILY, --family FAMILY
                        Device family to read out device UID and flash size. (default: $STM32LOADER_FAMILY).
```

### Read memory command

```bash
usage: stm32boot read [-h] -l LENGTH [-a ADDRESS] [-d] [file]

positional arguments:
  file                  File to read from flash.

optional arguments:
  -h, --help            show this help message and exit
  -l LENGTH, --length LENGTH
                        Length of read
  -a ADDRESS, --address ADDRESS
                        Target address for read.
  -d, --display         Display file content in intel hex format.
```

### Write memory command

```bash
usage: stm32boot write [-h] [-l LENGTH] [-a ADDRESS] [-v] [file]

positional arguments:
  file                  File to write in flash.

optional arguments:
  -h, --help            show this help message and exit
  -l LENGTH, --length LENGTH
                        Length data to write.
  -a ADDRESS, --address ADDRESS
                        Target address for write.
  -v, --verify          Perform a verification process after write.
```


### Erase memory command

```bash
usage: stm32boot erase [-h] [-l LENGTH] [-a ADDRESS] [-m {None,mass,bank1,bank2}]

optional arguments:
  -h, --help            show this help message and exit
  -l LENGTH, --length LENGTH
                        Length of erase in page mode.
  -a ADDRESS, --address ADDRESS
                        Target address for write.
  -m {None,mass,bank1,bank2}, --modes {None,mass,bank1,bank2}
                        Erase flash using special modes.
```

### Get command

```bash
usage: stm32boot get [-h] [-i] [-v] [-s]

optional arguments:
  -h, --help        show this help message and exit
  -i, --identifier  Get target identifier.
  -v, --version     Get bootloader version.
  -s, --size        Get flash size.
```
