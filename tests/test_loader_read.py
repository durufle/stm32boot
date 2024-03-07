# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Laurent Bonnet
#
# License: MIT

"""
Test loader read command with stm32l276 target
This test is performed under manual workflow and using
a local runner connected to a board.
"""

from typer.testing import CliRunner
from stmloader.boot import boot_app

runner = CliRunner()


# ----------------------------------------------------------------------------------------------------------------------
# test reset command
# ----------------------------------------------------------------------------------------------------------------------

def test_read_no_reset():
    """
    call reset with default value
    """
    result = runner.invoke(boot_app, ['read'])
    assert result.exit_code == 0
    assert "" in result.stdout


def test_read_default_args():
    """
    call read with default value
    """
    result = runner.invoke(boot_app, ['reset', '-t 2.7', 'read'])
    assert result.exit_code == 0
    assert "" in result.stdout


def test_read_length_1x_chunk():
    """
    call read 1 chunk of data
    """
    result = runner.invoke(boot_app, ['reset', '-t 2.7', 'read', '-l 255'])
    assert result.exit_code == 0
    assert "8000000" in result.stdout
    assert "8000100" not in result.stdout


def test_read_length_4x_chunk():
    """
    call reset with default value
    """
    result = runner.invoke(boot_app, ['reset', '-t 2.7', 'read', '-l 1024'])
    assert result.exit_code == 0
    assert "8000000" in result.stdout
    assert "8000100" in result.stdout
    assert "8000200" in result.stdout
    assert "8000300" in result.stdout
    assert "8000400" not in result.stdout
