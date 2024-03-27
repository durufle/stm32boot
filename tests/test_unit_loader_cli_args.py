# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Laurent Bonnet
#
# License: MIT

"""
Test loader cli parameters
"""

from typer.testing import CliRunner
from stmloader.boot import boot_app

runner = CliRunner()


# ----------------------------------------------------------------------------------------------------------------------
# main command parameter test parameters
# ----------------------------------------------------------------------------------------------------------------------

def test_main_no_args():
    """
    call without arguments -> print help
    """
    result = runner.invoke(boot_app, [])
    assert result.exit_code != 0
    assert "Error: Missing command." in result.stdout


def test_main_bad_command():
    """
    main bad command
    @return:
    """
    result = runner.invoke(boot_app, ["bad"])
    assert result.exit_code != 0
    assert "" in result.stdout


def test_main_verbose_option_no_args():
    """
    main verbose long no argument
    @return:
    """
    result = runner.invoke(boot_app, ["--verbose"])
    assert result.exit_code != 0
    assert "Error: Option '--verbose' requires an argument." in result.stdout


def test_main_verbose_option_short_no_args():
    """
    main verbose short no argument
    @return: 
    """
    result = runner.invoke(boot_app, ["-v"])
    assert result.exit_code != 0
    assert "Error: Option '-v' requires an argument." in result.stdout


def test_main_verbose_option_short_args_bad_type():
    """
    main verbose short bad type
    @return:
    """
    result = runner.invoke(boot_app, ["-v", 'a'])
    assert result.exit_code != 0
    assert "Error: Invalid value for '--verbose' / '-v': 'a' is not a valid integer." in result.stdout


def test_main_verbose_option_args_bad_type():
    """
    main verbose long bad type
    @return:
    """
    result = runner.invoke(boot_app, ["--verbose", 'a'])
    assert result.exit_code != 0
    assert "Error: Invalid value for '--verbose'" in result.stdout


def test_main_verbose_option_args_no_command():
    """
    main verbose long no argument
    @return:
    """
    result = runner.invoke(boot_app, ["--verbose", 1])
    assert result.exit_code != 0
    assert "Missing command" in result.stdout


def test_main_help_option():
    """
    main help option
    @return:
    """
    result = runner.invoke(boot_app, ["--help"])
    assert result.exit_code == 0
    # Commands
    assert "Commands" in result.stdout
    assert "erase" in result.stdout
    assert "get" in result.stdout
    assert "go" in result.stdout
    assert "protect" in result.stdout
    assert "read" in result.stdout
    assert "reset" in result.stdout
    assert "write" in result.stdout


# ----------------------------------------------------------------------------------------------------------------------
# erase command parameter test parameters
# ----------------------------------------------------------------------------------------------------------------------

def test_command_erase_no_args():
    """
    erase no arguments
    @return:
    """
    result = runner.invoke(boot_app, ["erase"])
    assert result.exit_code == 0
    assert "" in result.stdout


def test_command_erase_bad_option():
    """
    erase bad option
    @return:
    """
    result = runner.invoke(boot_app, ["erase", "--bad"])
    assert result.exit_code != 0
    assert "" in result.stdout


def test_command_erase_bad_address_type():
    """
    erase bad address type (long)
    @return:
    """
    result = runner.invoke(boot_app, ["erase", "--address", "a"])
    assert result.exit_code != 0
    assert "Invalid value (a) !" in result.stdout


def test_command_erase_bad_address_short_type():
    """
    erase bad address type (short)
    @return:
    """
    result = runner.invoke(boot_app, ["erase", "-a", "a"])
    assert result.exit_code != 0
    assert "Invalid value (a) !" in result.stdout


def test_command_erase_bad_length_type():
    """
    erase bad length type (long)
    @return:
    """
    result = runner.invoke(boot_app, ["erase", "--length", "a"])
    assert result.exit_code != 0
    assert "Error: Invalid value for '--length'" in result.stdout


def test_command_erase_bad_length_short_type():
    """
    erase bad length type (short)
    """
    result = runner.invoke(boot_app, ["erase", "-l", "a"])
    assert result.exit_code != 0
    assert "Error: Invalid value for '--length'" in result.stdout


def test_command_erase_help_option():
    """
    erase help option
    @return:
    """
    result = runner.invoke(boot_app, ["erase", "--help"])
    assert result.exit_code == 0
    # header
    assert "  Erase memory command" in result.stdout
    # Options
    assert "--mode" in result.stdout
    assert "--address" in result.stdout
    assert "--length" in result.stdout
    assert "help" in result.stdout


# ----------------------------------------------------------------------------------------------------------------------
# read command parameter test parameters
# ----------------------------------------------------------------------------------------------------------------------
def test_command_read_bad_option():
    """
    read bad option
    @return:
    """
    result = runner.invoke(boot_app, ["read", "--bad"])
    assert result.exit_code != 0
    assert "Error: No such option: --bad" in result.stdout


def test_command_read_bad_address_type_option():
    """
    read bad address type (long)
    @return:
    """
    result = runner.invoke(boot_app, ["read", "--address", "a"])
    assert result.exit_code != 0
    assert "Invalid value (a) !" in result.stdout


def test_command_read_bad_length_type_option():
    """
    read bad length type (long)
    @return:
    """
    result = runner.invoke(boot_app, ["read", "--length", "a"])
    assert result.exit_code != 0
    assert "Error: Invalid value for '--length' / '-l': 'a'" in result.stdout


def test_command_read_bad_length_short_type_option():
    """
    read bad length type (short)
    @return:
    """
    result = runner.invoke(boot_app, ["read", "-l", "a"])
    assert result.exit_code != 0
    assert "Error: Invalid value for '--length' / '-l': 'a'" in result.stdout


def test_command_read_help_option():
    """
    read help option
    @return:
    """
    result = runner.invoke(boot_app, ["read", "--help"])
    assert result.exit_code == 0
    # header
    assert "  Read memory command" in result.stdout
    # Arguments
    assert "file" in result.stdout
    # Options
    assert "--address" in result.stdout
    assert "--length" in result.stdout
    assert "--help" in result.stdout


# ----------------------------------------------------------------------------------------------------------------------
# get command parameter test parameters
# ----------------------------------------------------------------------------------------------------------------------

def test_command_get_bad_option():
    """
    get bad option
    @return:
    """
    result = runner.invoke(boot_app, ["get", "--bad"])
    assert result.exit_code != 0
    assert "Error: No such option: --bad" in result.stdout


def test_command_get_bad_info_type_option():
    """
    get bad info (long) type
    @return:
    """
    result = runner.invoke(boot_app, ["get", "--info", "a"])
    assert result.exit_code != 0
    assert "Error: Invalid value for '--info' / '-i': 'a'" in result.stdout


def test_command_get_bad_info_short_type_option():
    """
    get bad info (short) type
    @return:
    """
    result = runner.invoke(boot_app, ["get", "-i", "a"])
    assert result.exit_code != 0
    assert "Error: Invalid value for '--info' / '-i': 'a'" in result.stdout


def test_command_get_help_option():
    """
    get help
    @return:
    """
    result = runner.invoke(boot_app, ["get", "--help"])
    assert result.exit_code == 0
    # header
    assert "  Get information command" in result.stdout
    # Options
    assert "--info" in result.stdout
    assert "--help" in result.stdout
