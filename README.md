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
 Usage: stm32boot [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...                                                                                                                                                              
                                                                                                                                                                                                                                    
 stm32 bootloader shell                                                                                                                                                                                                             
                                                                                                                                                                                                                                    
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --port                      TEXT     Scaffold Communication port [default: /dev/ttyUSB0]                                                                                                                                         │
│ --family                    TEXT     Target family                                                                                                                                                                               │
│ --verbose                   INTEGER  Verbosity level [default: 5]                                                                                                                                                                │
│ --install-completion                 Install completion for the current shell.                                                                                                                                                   │
│ --show-completion                    Show completion for the current shell, to copy it or customize the installation.                                                                                                            │
│ --help                               Show this message and exit.                                                                                                                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ erase                                          Erase memory command                                                                                                                                                              │
│ get                                            Get information command                                                                                                                                                           │
│ go                                             Go command                                                                                                                                                                        │
│ protect                                        protection command                                                                                                                                                                │
│ read                                           Read memory command                                                                                                                                                               │
│ reset                                          Reset to system/flash  memory command                                                                                                                                             │
│ write                                          Write memory command                                                                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯


```


## Reference documents
- `AN2606`: STM32 microcontroller system memory boot mode
- `AN3155`: UART protocol in the STM32 bootloader

