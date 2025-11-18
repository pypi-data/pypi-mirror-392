"""Unit tests for the Clinkey CLI interface."""

import pytest
from click.testing import CliRunner
from clinkey_cli.cli import main


@pytest.fixture
def runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


class TestCLIBasic:
    """Test basic CLI functionality."""

    def test_cli_help(self, runner):
        """Test that --help flag works."""
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'Usage:' in result.output

    def test_cli_version(self, runner):
        """Test that --version flag works."""
        result = runner.invoke(main, ['--version'])
        assert result.exit_code == 0

    def test_cli_default_direct_mode(self, runner):
        """Test CLI in direct mode with defaults."""
        result = runner.invoke(main, ['-l', '16'])
        assert result.exit_code == 0
        # Should output a password
        assert len(result.output.strip()) > 0


class TestCLILength:
    """Test CLI length parameter."""

    @pytest.mark.parametrize("length", [10, 16, 20, 30])
    def test_cli_length_parameter(self, runner, length):
        """Test --length parameter."""
        result = runner.invoke(main, ['-l', str(length)])
        assert result.exit_code == 0
        password = result.output.strip().split('\n')[-1]
        assert len(password) == length

    def test_cli_invalid_length(self, runner):
        """Test invalid length parameter."""
        result = runner.invoke(main, ['-l', '-5'])
        assert result.exit_code != 0


class TestCLIType:
    """Test CLI password type parameter."""

    @pytest.mark.parametrize("pwd_type", ["normal", "strong", "super_strong"])
    def test_cli_type_parameter(self, runner, pwd_type):
        """Test --type parameter with all valid types."""
        result = runner.invoke(main, ['-t', pwd_type, '-l', '20'])
        assert result.exit_code == 0

    def test_cli_invalid_type(self, runner):
        """Test invalid password type."""
        result = runner.invoke(main, ['-t', 'invalid', '-l', '16'])
        assert result.exit_code != 0


class TestCLIOptions:
    """Test CLI optional flags."""

    def test_cli_lowercase_flag(self, runner):
        """Test --lower flag."""
        result = runner.invoke(main, ['-l', '16', '--lower'])
        assert result.exit_code == 0
        password = result.output.strip().split('\n')[-1]
        # Check if lowercase (ignoring non-alpha characters)
        alpha_chars = [c for c in password if c.isalpha()]
        assert all(c.islower() for c in alpha_chars)

    def test_cli_no_separator_flag(self, runner):
        """Test --no-sep flag."""
        result = runner.invoke(main, ['-l', '20', '--no-sep'])
        assert result.exit_code == 0
        password = result.output.strip().split('\n')[-1]
        assert '-' not in password
        assert '_' not in password

    def test_cli_custom_separator(self, runner):
        """Test --separator flag."""
        result = runner.invoke(main, ['-l', '20', '-s', '@'])
        assert result.exit_code == 0
        password = result.output.strip().split('\n')[-1]
        # Custom separator should appear in password
        assert '@' in password or len(password) < 10


class TestCLIBatch:
    """Test CLI batch generation."""

    def test_cli_batch_generation(self, runner):
        """Test --number flag for batch generation."""
        result = runner.invoke(main, ['-l', '16', '-n', '5'])
        assert result.exit_code == 0
        lines = result.output.strip().split('\n')
        # Should have 5 passwords
        passwords = [line for line in lines if line and not line.startswith('╭')]
        assert len(passwords) >= 5

    def test_cli_batch_invalid_count(self, runner):
        """Test invalid batch count."""
        result = runner.invoke(main, ['-l', '16', '-n', '0'])
        assert result.exit_code != 0


class TestCLIOutput:
    """Test CLI file output functionality."""

    def test_cli_output_file(self, runner, tmp_path):
        """Test --output flag writes to file."""
        output_file = tmp_path / "passwords.txt"
        result = runner.invoke(main, ['-l', '16', '-o', str(output_file)])
        assert result.exit_code == 0
        # File should be created
        assert output_file.exists()
        # File should contain a password
        content = output_file.read_text()
        assert len(content.strip()) > 0

    def test_cli_output_file_batch(self, runner, tmp_path):
        """Test file output with batch generation."""
        output_file = tmp_path / "batch_passwords.txt"
        result = runner.invoke(main, ['-l', '16', '-n', '10', '-o', str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text()
        lines = content.strip().split('\n')
        assert len(lines) == 10
