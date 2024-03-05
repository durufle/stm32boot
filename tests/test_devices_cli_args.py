# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Laurent Bonnet, 2024 python-gitlab team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
test cli parameters
"""
import os
from typer.testing import CliRunner
from stm32boot.devices import device_app

runner = CliRunner()


# ----------------------------------------------------------------------------------------------------------------------
# main command parameter test parameters
# ----------------------------------------------------------------------------------------------------------------------


def test_main_no_args():
    """
    call without arguments -> print help
    """
    result = runner.invoke(device_app, [])
    assert result.exit_code != 0
    assert "Error: Missing command." in result.stdout


def test_main_bad_command():
    result = runner.invoke(device_app, ["bad"])
    assert result.exit_code != 0
    assert "Error: No such command 'bad'" in result.stdout


def test_main_help_option():
    result = runner.invoke(device_app, ["--help"])
    assert result.exit_code == 0
    # header
    assert "  Devices management cli" in result.stdout
    # Commands
    assert "Commands" in result.stdout
    assert "  add   Add device description" in result.stdout
    assert "  list  List supported devices" in result.stdout


# ----------------------------------------------------------------------------------------------------------------------
# add command parameter test parameters
# ----------------------------------------------------------------------------------------------------------------------

def test_command_add_no_args():
    result = runner.invoke(device_app, ["add"])
    assert result.exit_code != 0
    assert "Error: Missing argument 'FILES...'." in result.stdout


def test_command_add_bad_option():
    result = runner.invoke(device_app, ["add", "--bad"])
    assert result.exit_code != 0
    assert "Error: No such option: --bad" in result.stdout


def test_command_add_option_check_no_file_name():
    result = runner.invoke(device_app, ["add", "none.yml"])
    assert result.exit_code == -1
    assert "[Errno 2] No such file or directory: 'none.yml'" in result.stdout


def test_command_add_option_check_desc_empty(request):
    file = os.path.join(os.path.dirname(__file__), "data/desc_empty.yml")
    result = runner.invoke(device_app, ["add", f"{file}"])
    assert result.exit_code != 0
    assert f"document is missing in file {file}" in result.stdout


def test_command_add_option_check_miss_id():
    file = os.path.join(os.path.dirname(__file__), "data/desc_miss_id.yml")
    result = runner.invoke(device_app, ["add", f"{file}"])
    assert result.exit_code == 0
    assert "{'DeviceID': ['required field']}" in result.stdout


def test_command_add_option_check_miss_bad_type():
    file = os.path.join(os.path.dirname(__file__), "data/desc_miss_bad_type.yml")
    result = runner.invoke(device_app, ["add", f"{file}"])
    assert result.exit_code == 0
    assert "{'DeviceID': ['must be of integer type']}" in result.stdout


def test_command_add_option_check_name_null():
    file = os.path.join(os.path.dirname(__file__), "data/desc_name_null.yml")
    result = runner.invoke(device_app, ["add", f"{file}"])
    assert result.exit_code == 0
    assert "{'Name': ['null value not allowed']}" in result.stdout


def test_command_erase_help_option():
    result = runner.invoke(device_app, ["add", "--help"])
    assert result.exit_code == 0
    # header
    assert "  Add device description" in result.stdout
    # Arguments
    assert "  FILES...  Device description file(s).  [required]" in result.stdout
    # Options
    assert "-m, --mode" in result.stdout
    assert "--help" in result.stdout
