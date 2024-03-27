# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Laurent Bonnet
#
# License: MIT

"""
Test loader reset command with stm32l276 target
This test is performed under manual workflow and using
a local runner connected to a board.
"""

from typer.testing import CliRunner
from stmloader.boot import boot_app

runner = CliRunner()


# ----------------------------------------------------------------------------------------------------------------------
# test reset command
# ----------------------------------------------------------------------------------------------------------------------

def test_reset_no_args():
    """
    call reset with default value
    """
    result = runner.invoke(boot_app, ['reset'])
    assert result.exit_code == 0
    assert "Consider to change reset startup time with option --timeout/-t" in result.stdout


def test_reset_good_timeout():
    """
    call reset with default value
    """
    result = runner.invoke(boot_app, ['reset', '-t 2.7'])
    assert result.exit_code == 0
    assert "Chip id: 0x415" in result.stdout


def test_reset_system_short_no_args():
    """
    call reset with default value
    """
    result = runner.invoke(boot_app, ['reset', '-m', 'system'])
    assert result.exit_code == 0
    assert "Consider to change reset startup time with option --timeout/-t" in result.stdout


def test_reset_system_long_no_args():
    """
    call reset with default value
    """
    result = runner.invoke(boot_app, ['reset', '--mode', 'system'])
    assert result.exit_code == 0
    assert "Consider to change reset startup time with option --timeout/-t" in result.stdout


def test_reset_system_short_good_timeout():
    """
    call reset with default value
    """
    result = runner.invoke(boot_app, ['reset', '-m', 'system', '-t 2.7'])
    assert result.exit_code == 0
    assert "Chip id: 0x415" in result.stdout


def test_reset_system_long_good_timeout():
    """
    call reset with default value
    """
    result = runner.invoke(boot_app, ['reset', '--mode', 'system', '-t 2.7'])
    assert result.exit_code == 0
    assert "Chip id: 0x415" in result.stdout
