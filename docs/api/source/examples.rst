:mod:`Examples`
***************

Simple connection
=================

This example show a connection to the donjon-scaffold, bootloader activation and send a GET command
to the bootloader.

.. literalinclude:: ../../../scripts/api/connect.py
   :language: py
   :linenos:
   :caption: **Simple connection script**

Output:

.. code-block:: console

    Chip id: 0x462
    Available commands: 0x0, 0x1, 0x2, 0x11, 0x21, 0x31, 0x44, 0x63, 0x73, 0x82, 0x92

Mass erase
==========

The GET command return if erase extended mode are supported by the bootloader. This example
execute a mass erase if supported by the target.

.. literalinclude:: ../../../scripts/api/erase.py
   :language: py
   :linenos:
   :caption: **Mass erase script**

Output:

.. code-block:: console

    Chip id: 0x462
    Available commands: 0x0, 0x1, 0x2, 0x11, 0x21, 0x31, 0x44, 0x63, 0x73, 0x82, 0x92

Read Flash Memory
=================

This example show how to read data from flash, and display to screen:


.. literalinclude:: ../../../scripts/api/read.py
   :language: py
   :linenos:
   :caption: **Read script**

Output:

.. code-block:: console

    Chip id: 0x462
    Available commands: 0x0, 0x1, 0x2, 0x11, 0x21, 0x31, 0x44, 0x63, 0x73, 0x82, 0x92
    8000000  FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF  |................|
    8000010  FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF  |................|
    8000020  FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF  |................|
    8000030  FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF  |................|


Write file
==========

This example show how to write an intel hex file.

.. literalinclude:: ../../../scripts/api/load.py
   :language: py
   :linenos:
   :caption: **Load script**

Output:

.. code-block:: console

    Chip id: 0x462
    Available commands: 0x0, 0x1, 0x2, 0x11, 0x21, 0x31, 0x44, 0x63, 0x73, 0x82, 0x92
     100% |████████████████████████████████████████████████████████| Time:  0:00:00

Get some information
====================

This example get bootloader's information

.. literalinclude:: ../../../scripts/api/info.py
   :language: py
   :linenos:
   :caption: **Get information script**

Output:

.. code-block:: console

    Chip id: 0x415
    Available commands: 0x0, 0x1, 0x2, 0x11, 0x21, 0x31, 0x44, 0x63, 0x73, 0x82, 0x92
    Bootloader protocol version: 0x31
    Bootloader version (Id) : 0x92


Readout protection
==================

This script enable or disable readout protection according to an argument:

.. literalinclude:: ../../../scripts/api/protection.py
   :language: py
   :linenos:
   :caption: **Protection script**

.. code-block:: console

    python protection.py --help

    This script uses Scaffold to communicate with CEVAL firmware

    optional arguments:
      -h, --help            show this help message and exit
      -m {unprotect,protect}, --mode {unprotect,protect}
                            readout protection

Execute the following scenario:

#. Execute the **load** script. This ensure to flash data at the beginning of the flash.
#. Execute the **read** script to verify content.
#. Execute the **protection** with mode set to protect. This enable the readout protection.
#. Execute the **read** script again, you need to receive a NACK byte.
#. Execute the **protection** with mode set to unprotect. This disable the readout protection.
#. Execute the **read** script again, and check that the memory has been properly erase.
