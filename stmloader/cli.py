# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Laurent Bonnet
#
# License: MIT

"""
Global CLI
"""
import typer

from .boot import boot_app
from .devices import device_app

cli = typer.Typer()
cli.add_typer(device_app, name="devices")
cli.add_typer(boot_app, name="loader")
