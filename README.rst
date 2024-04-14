STM32 Bootloader utility with scaffold v1.1
*******************************************

Python module to upload or download firmware to / from ST Microelectronics STM32 microcontrollers over donjon-scaffold.

Installation
************

.. code-block:: bash

    pip install ragnarok_stmloader

To install the latest development version

.. code-block:: bash

    pip install git+https://github.com/durufle/stm32boot.git

stmloader utility usage
***********************

general usage:

.. code-block:: bash

    Usage: stmloader [OPTIONS] COMMAND [ARGS]...

    Options:
      --install-completion [bash|zsh|fish|powershell|pwsh]
                                      Install completion for the specified shell.
      --show-completion [bash|zsh|fish|powershell|pwsh]
                                      Show completion for the specified shell, to
                                      copy it or customize the installation.
      --help                          Show this message and exit.

    Commands:
      devices  Devices management cli
      loader   stm32 bootloader cli


loader usage:

.. code-block:: bash

    Usage: stmloader loader [OPTIONS] COMMAND1 [ARGS]... [COMMAND2
                                      [ARGS]...]...

      stm32 bootloader cli

    Options:
      -p, --port TEXT        Scaffold Communication port  [default: /dev/ttyUSB0]
      -v, --verbose INTEGER  Verbosity level  [default: 5]
      --help                 Show this message and exit.

    Commands:
      erase    Erase memory command
      get      Get information command
      go       Go command
      protect  protection command
      read     Read memory command
      reset    Reset to system/flash memory command
      write    Write memory command


devices usage:

.. code-block:: bash

    Usage: stmloader devices [OPTIONS] COMMAND [ARGS]...

      Devices management cli

    Options:
      --help  Show this message and exit.

    Commands:
      add   Add device description
      list  List supported devices


By default, only typer is installed. You can install rich, and stm32boot show nicely formatted output.

Issues
******
 🐛 `Github Issues`_

Documentations
**************
 📚 `Latest documentation`_

Reference documents
*******************

- `AN2606`_: STM32 microcontroller system memory boot mode
- `AN3155`_: UART protocol in the STM32 bootloader

.. _Github Issues: https://github.com/durufle/stm32boot/issues
.. _Latest documentation: https://stm32boot.readthedocs.io/en/latest/
.. _AN2606: https://www.st.com/content/st_com/en/search.html#q=AN2606-t=resources-page=1
.. _AN3155: https://www.st.com/content/st_com/en/search.html#q=AN2606-t=resources-page=1
