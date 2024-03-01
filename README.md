# STM32 Bootloader utility with scaffold v1.1

Python module to upload or download firmware to / from ST Microelectronics STM32 microcontrollers over donjon-scaffold.

## Installation

```bash
pip install ragnarok_stmloader
```
To install the latest development version

```bash
pip install git+https://github.com/durufle/stm32boot.git
```

## Usage

```bash
 Usage: python -m stmloader [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                           [ARGS]...]...

  stm32 bootloader shell

Options:
  -p, --port TEXT                 Scaffold Communication port  [default:
                                  /dev/ttyUSB0]
  -f, --family TEXT               Target family
  -v, --verbose INTEGER           Verbosity level  [default: 5]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  erase    Erase memory command
  get      Get information command
  go       Go command
  protect  protection command
  read     Read memory command
  reset    Reset to system/flash memory command
  write    Write memory command
```

By default, only typer is installed. You can install rich, and stm32boot show nicely formatted output.


## Reference documents
- `AN2606`: STM32 microcontroller system memory boot mode
- `AN3155`: UART protocol in the STM32 bootloader

