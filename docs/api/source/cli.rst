stmloader utility
*****************

.. note::
    By default, only typer package is installed. You can install rich, and you can have nicely formatted outputs.

Introduction
============

stmloader utility is composed of two independent parsing cli: devices and loader (shows as Commands in the following
screen capture).

.. code-block:: console

    $ stmloader --help
    Usage: stmloader [OPTIONS] COMMAND [ARGS]...

    Options:
      --install-completion  Install completion for the current shell.
      --show-completion     Show completion for the current shell, to copy it or
                            customize the installation.
      --help                Show this message and exit.

    Commands:
      devices  Devices management cli
      loader   stm32 bootloader cli
    $

For each, it is possible to list all implemented sub-command as follows:

.. code-block:: console
    :caption: loader help

    $ stmloader loader --help
    Usage: stmloader loader [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

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
    $

.. code-block:: console
    :caption: devices help

    $ stmloader devices --help
    Usage: stmloader devices [OPTIONS] COMMAND [ARGS]...

      Devices management cli

    Options:
      --help  Show this message and exit.

    Commands:
      add   Add device description
      list  List supported devices
    $

Devices managements
===================

The devices cli is used to manage devices supported by the loader utility. For each device id supported, a device description
file is created under the package data folder. The description file follow a scheme which is validate using `cerberus <https://pypi.org/project/Cerberus/>`_

The description scheme is detailed in the schema.py file. Each device description file shall follow this syntax.

.. literalinclude:: ../../../stmloader/schema.py
    :language: py
    :linenos:
    :caption: devices description scheme

.. note::
    We can observe that some description field can be required or not (e.g DeviceID is a required field)

#. FlashSize: Address where flash size information can be read. Not required
#. UniversalID: Address where universal id information can be read. Not required
#. PageSize: Programming page size. Required.
#. Bootloader ID: Address  where the bootloader version can be read. Required.

Devices list
------------
To list supported target, enter the following command

.. code-block:: console
    :caption: List supported devices

    $ stmloader devices list
    0x462 , STM32L45x/L46x, STM32L4, Cortex-M4, ARM 32-bit Cortex-M4 based device
    0x415 , STM32L4x1/STM32L475xx/STM32L476xx/STM32L486xx, STM32L4, Cortex-M4, ARM 32-bit Cortex-M4 based device
    0x460 , STM32G07x/STM32G08x, STM32G0, Cortex-M0+, ARM 32-bit Cortex-M0+ based device
    0x450 , STM32H7xx, STM32H7, Cortex-M7, ARM 32-bit Cortex-M7 and ARM 32-bit Cortex-M4 dual core based device
    0x451 , STM32F76x/STM32F77x, STM32F7, Cortex-M7, ARM 32-bit Cortex-M7 based device
    $

According to the device description scheme, the following headers are displayed:

    ======== ===== ====== === ===========
    DeviceID  Name Series CPU Description
    ======== ===== ====== === ===========

Devices add
-----------

The devices add command allow to add device description files.

.. code-block:: console
    :caption: Add new devices description file(s)

    $ stmloader devices add --help
    Usage: stmloader devices add [OPTIONS] FILES...

      Add device description

    Arguments:
      FILES...  Device description file(s).  [required]

    Options:
      -m, --mode [check|copy]  Add mode.  [default: check]
      --help                   Show this message and exit.
    $

Two modes are available:

#. **check mode**. This is the default mode, its allow to check only the received description file(s).
#. **copy mode**. Copy description file(s) in the package data folder.

.. note::
    The received description file(s) name is not important. If the checking pass, during copy execution the utility
    store it using an internal naming convention: **stm32_<DeviceID>.yml**

Example
^^^^^^^

Suppose that we have the following description in the file **device_a.yml**:

.. code-block:: console

    DeviceID: 0x482
    Name: 'STM32U575/STM32U585'
    Series: 'STM32U5'
    CPU: 'Cortex-M33'
    Description: 'ARM 32-bit Cortex-M33 based device'
    FlashSize:
      address: 0x0BFA07A0
    UniversalID:
      address: 0x00000000
    Flash:
      PageSize:
    Bootloader:
      ID: 0x0BF99EFE

Now check the file using stmloader devices utility as follow:

.. code-block:: console

    $ stmloader devices add device_a.yml
    {'Flash': [{'PageSize': ['null value not allowed']}]} in file device_a.yml
    $

.. note::
    In device description scheme, bootloader RAM and SYSTEM memory range are present but not used at the moment.

Add the Flash page size information in the previous device description file, and check again.

.. code-block:: console

    $ stmloader devices add device_a.yml
    $

No error are return by the utility, we can add this new device description:

.. code-block:: console

    $ stmloader devices add -m copy device_a.yml
    $

Then list

.. code-block:: console

    $ stmloader devices list
    0x462 , STM32L45x/L46x, STM32L4, Cortex-M4, ARM 32-bit Cortex-M4 based device
    0x415 , STM32L4x1/STM32L475xx/STM32L476xx/STM32L486xx, STM32L4, Cortex-M4, ARM 32-bit Cortex-M4 based device
    0x460 , STM32G07x/STM32G08x, STM32G0, Cortex-M0+, ARM 32-bit Cortex-M0+ based device
    0x450 , STM32H7xx, STM32H7, Cortex-M7, ARM 32-bit Cortex-M7 and ARM 32-bit Cortex-M4 dual core based device
    0x451 , STM32F76x/STM32F77x, STM32F7, Cortex-M7, ARM 32-bit Cortex-M7 based device
    0x482 , STM32U575/STM32U585, STM32U5, Cortex-M33, ARM 32-bit Cortex-M33 based device
    $

The device (0x482) has been successfully added.