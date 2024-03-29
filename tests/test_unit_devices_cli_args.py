# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Laurent Bonnet
#
# License: MIT

"""
Test devices cli parameters
"""
import os
from typer.testing import CliRunner
from stmloader.devices import device_app

runner = CliRunner()


# ----------------------------------------------------------------------------------------------------------------------
# main command parameter test parameters
# ----------------------------------------------------------------------------------------------------------------------


def test_main_no_args():
    """
    main no args
    @return:
    """
    result = runner.invoke(device_app, [])
    assert result.exit_code != 0
    assert "Error: Missing command." in result.stdout


def test_main_bad_command():
    """
    main invalid command
    @return:
    """
    result = runner.invoke(device_app, ["bad"])
    assert result.exit_code != 0
    assert "Error: No such command 'bad'" in result.stdout


def test_main_help_option():
    """
    main show help
    @return:
    """
    result = runner.invoke(device_app, ["--help"])
    assert result.exit_code == 0
    assert "  Devices management cli" in result.stdout
    assert "Commands" in result.stdout
    assert "  add   Add device description" in result.stdout
    assert "  list  List supported devices" in result.stdout


# ----------------------------------------------------------------------------------------------------------------------
# add command parameter test parameters
# ----------------------------------------------------------------------------------------------------------------------

def test_command_add_no_args():
    """
    add command no args
    @return:
    """
    result = runner.invoke(device_app, ["add"])
    assert result.exit_code != 0
    assert "Error: Missing argument 'FILES...'." in result.stdout


def test_command_add_bad_option():
    """
    add command bad option
    @return:
    """
    result = runner.invoke(device_app, ["add", "--bad"])
    assert result.exit_code != 0
    assert "Error: No such option: --bad" in result.stdout


def test_command_add_option_check_no_file_name():
    """
    add command option check file
    @return:
    """
    result = runner.invoke(device_app, ["add", "none.yml"])
    assert result.exit_code == -1
    assert "[Errno 2] No such file or directory: 'none.yml'" in result.stdout


def test_command_add_option_check_desc_empty():
    """
    add command option check empty description file
    @return:
    """
    file = os.path.join(os.path.dirname(__file__), "data/desc_empty.yml")
    result = runner.invoke(device_app, ["add", f"{file}"])
    assert result.exit_code != 0
    assert f"document is missing in file {file}" in result.stdout


def test_command_add_option_check_miss_id():
    """
    add command option: check device id missing
    """
    file = os.path.join(os.path.dirname(__file__), "data/desc_miss_id.yml")
    result = runner.invoke(device_app, ["add", f"{file}"])
    assert result.exit_code == 0
    assert "{'DeviceID': ['required field']}" in result.stdout


def test_command_add_option_check_miss_bad_type():
    """
    add command option check bad type
    @return:
    """
    file = os.path.join(os.path.dirname(__file__), "data/desc_miss_bad_type.yml")
    result = runner.invoke(device_app, ["add", f"{file}"])
    assert result.exit_code == 0
    assert "{'DeviceID': ['must be of integer type']}" in result.stdout


def test_command_add_option_check_name_null():
    """
    add command option check no name
    """
    file = os.path.join(os.path.dirname(__file__), "data/desc_name_null.yml")
    result = runner.invoke(device_app, ["add", f"{file}"])
    assert result.exit_code == 0
    assert "{'Name': ['null value not allowed']}" in result.stdout


def test_command_add_help_option():
    """
    add command show help
    @return:
    """
    result = runner.invoke(device_app, ["add", "--help"])
    assert result.exit_code == 0
    assert "  Add device description" in result.stdout
    assert "  FILES...  Device description file(s).  [required]" in result.stdout
    assert "-m, --mode" in result.stdout
    assert "--help" in result.stdout


# ----------------------------------------------------------------------------------------------------------------------
# list command parameter test parameters
# ----------------------------------------------------------------------------------------------------------------------
def test_command_list_help_option():
    """
    list command show help
    @return:
    """
    result = runner.invoke(device_app, ["list", "--help"])
    assert result.exit_code == 0
    assert "  List supported devices" in result.stdout
    assert "--help" in result.stdout


def test_command_list_bad_option():
    """
    list command bad option
    @return:
    """
    result = runner.invoke(device_app, ["list", "--bad"])
    assert result.exit_code != 0
    assert "Error: No such option: --bad" in result.stdout


def test_command_list_no_extra_args():
    """
    list command bad extra option
    @return:
    """
    result = runner.invoke(device_app, ["list", "bad"])
    assert result.exit_code != 0
    assert "Error: Got unexpected extra argument (bad)" in result.stdout


def test_command_list_basic_option():
    """
    list command check available id
    @return:
    """
    result = runner.invoke(device_app, ["list"])
    assert result.exit_code == 0
    assert "0x415" in result.stdout
    assert "0x460" in result.stdout
