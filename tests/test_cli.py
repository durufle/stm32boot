from typer.testing import CliRunner

from stm32boot.main import app

runner = CliRunner(mix_stderr=True)


def test_main_no_args():
    result = runner.invoke(app, [])
    assert result.exit_code != 0
    assert "Missing command" in result.stdout


def test_main_bad_command():
    result = runner.invoke(app, ["bad"])
    assert result.exit_code != 0
    assert "No such command 'bad" in result.stdout


def test_main_verbose_option_no_args():
    result = runner.invoke(app, ["--verbose"])
    assert result.exit_code != 0
    assert "Option '--verbose' requires an argument." in result.stdout


def test_main_verbose_option_args_bad_type():
    result = runner.invoke(app, ["--verbose", 'a'])
    assert result.exit_code != 0
    assert "Invalid value" in result.stdout


def test_main_verbose_option_args_no_command():
    result = runner.invoke(app, ["--verbose", 1])
    assert result.exit_code != 0
    assert "Missing command" in result.stdout


def test_main_help_option():
    result = runner.invoke(app, ["--help"])
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


def test_command_erase_no_args():
    result = runner.invoke(app, ["erase"])
    assert result.exit_code == 0
    assert "" in result.stdout


def test_command_erase_bad_option():
    result = runner.invoke(app, ["erase", "--bad"])
    assert result.exit_code != 0
    assert " No such option: --bad " in result.stdout


def test_command_erase_bad_address_type():
    result = runner.invoke(app, ["erase", "--address", "a"])
    assert result.exit_code != 0
    assert "Invalid value (a) !" in result.stdout


def test_command_erase_bad_length_type():
    result = runner.invoke(app, ["erase", "--length", "a"])
    assert result.exit_code != 0
    assert "Invalid value for '--length': 'a'" in result.stdout


def test_command_erase_help_option():
    result = runner.invoke(app, ["erase", "--help"])
    assert result.exit_code == 0
    # header
    assert " Erase memory command " in result.stdout
    # Options
    assert "--mode" in result.stdout
    assert "--address" in result.stdout
    assert "--length" in result.stdout
    assert "help" in result.stdout


def test_command_read_bad_option():
    result = runner.invoke(app, ["read", "--bad"])
    assert result.exit_code != 0
    assert " No such option: --bad " in result.stdout


def test_command_read_bad_address_type_option():
    result = runner.invoke(app, ["read", "--address", "a"])
    assert result.exit_code != 0
    assert "Invalid value (a) !" in result.stdout


def test_command_read_bad_length_type_option():
    result = runner.invoke(app, ["read", "--length", "a"])
    assert result.exit_code != 0
    assert "Invalid value for '--length': 'a'" in result.stdout


def test_command_read_help_option():
    result = runner.invoke(app, ["read", "--help"])
    assert result.exit_code == 0
    # header
    assert " Read memory command " in result.stdout
    # Arguments
    assert "file" in result.stdout
    # Options
    assert "--address" in result.stdout
    assert "--length" in result.stdout
    assert "--help" in result.stdout
