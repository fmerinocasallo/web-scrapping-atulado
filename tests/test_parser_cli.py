"""Tests for the CLI interface of the parser module."""

import sys
from pathlib import Path

import pytest
import typer
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from src.web_scrapping import parser
from src.web_scrapping.parser import ConsumptionRates, ElectricityRates, PowerRates


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Typer CLI test runner."""
    return CliRunner(mix_stderr=True)


@pytest.fixture
def mock_rates() -> ElectricityRates:
    """Create mock electricity rates for testing."""
    return ElectricityRates(
        consumption=ConsumptionRates(
            peak=(0.1234, "€/kWh"),
            flat=(0.1234, "€/kWh"),
            valley=(0.1234, "€/kWh"),
        ),
        power=PowerRates(
            peak=(0.1234, "€/kW day"),
            flat=(0.1234, "€/kW day"),
            valley=(0.1234, "€/kW day"),
        ),
    )


def test_main_cli_default_plan(
    cli_runner: CliRunner,
    mocker: MockerFixture,
    tmp_path: Path,
    mock_rates: ElectricityRates,
) -> None:
    """Test main function CLI with default plan."""
    # Setup
    mocker.patch(
        "src.web_scrapping.parser.get_html",
        return_value="<html><body>Test</body></html>",
    )
    mocker.patch("src.web_scrapping.parser.parse_rates", return_value=mock_rates)
    mocker.patch("src.web_scrapping.parser.paths.data_dir", tmp_path)

    # Execute
    result = cli_runner.invoke(parser.app)

    # Assert
    assert result.exit_code == 0

    output_file = tmp_path / "milenial_rates.json"
    assert output_file.exists()

    with open(output_file) as f:
        result = ElectricityRates.model_validate_json(f.read())
    assert result == mock_rates


def test_main_cli_custom_plan(
    cli_runner: CliRunner,
    mocker: MockerFixture,
    tmp_path: Path,
    mock_rates: ElectricityRates,
) -> None:
    """Test main function CLI with custom plan."""
    # Setup
    custom_plan = "custom-plan"
    mocker.patch(
        "src.web_scrapping.parser.get_html",
        return_value="<html><body>Test</body></html>",
    )
    mocker.patch("src.web_scrapping.parser.parse_rates", return_value=mock_rates)
    mocker.patch("src.web_scrapping.parser.paths.data_dir", tmp_path)

    # Execute
    result = cli_runner.invoke(parser.app, ["--plan", custom_plan])

    # Assert
    assert result.exit_code == 0
    output_file = tmp_path / f"{custom_plan}_rates.json"

    assert output_file.exists()

    with open(output_file) as f:
        result = ElectricityRates.model_validate_json(f.read())
    # Convert tuples to lists for comparison since JSON doesn't support tuples
    assert result == mock_rates


def test_main_cli_help(cli_runner: CliRunner) -> None:
    """Test main function CLI help text."""
    # Execute
    result = cli_runner.invoke(parser.app, ["--help"])

    # Assert
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "Args:" in result.stdout
    assert "Options" in result.stdout
    assert "plan" in result.stdout


def test_main_cli_html_error(cli_runner: CliRunner, mocker: MockerFixture) -> None:
    """Test main function CLI with HTML retrieval error."""

    # Setup
    def mock_get_html():
        print(
            "ERROR: Could not find any reference to the 'Milenial' plan "
            "in the online version of the A tu Lado Energía website "
            "after 15 seconds. The website may have changed "
            "or there is a connection problem.",
            file=sys.stderr,
        )
        raise typer.Exit(1)

    mocker.patch("src.web_scrapping.parser.get_html", side_effect=mock_get_html)

    # Execute
    result = cli_runner.invoke(parser.app)

    # Assert
    assert result.exit_code == 1
    assert "ERROR" in result.stdout
    assert "Could not find any reference to the 'Milenial' plan" in result.stdout


def test_main_cli_parse_error(cli_runner: CliRunner, mocker: MockerFixture) -> None:
    """Test main function CLI with parsing error."""
    # Setup
    mocker.patch(
        "src.web_scrapping.parser.get_html",
        return_value="<html><body>Test</body></html>",
    )
    mocker.patch(
        "src.web_scrapping.parser.parse_rates",
        side_effect=ValueError("Plan 'invalid-plan' not found in the provided HTML."),
    )

    # Execute
    result = cli_runner.invoke(parser.app, ["--plan", "invalid-plan"])

    # Assert
    assert result.exit_code == 1
    assert "Plan 'invalid-plan' not found in the provided HTML." in result.stdout


def test_main_cli_file_error(
    cli_runner: CliRunner,
    mocker: MockerFixture,
    tmp_path: Path,
    mock_rates: ElectricityRates,
) -> None:
    """Test main function CLI with file writing error."""
    # Setup
    mocker.patch(
        "src.web_scrapping.parser.get_html",
        return_value="<html><body>Test</body></html>",
    )
    mocker.patch("src.web_scrapping.parser.parse_rates", return_value=mock_rates)
    mocker.patch("src.web_scrapping.parser.paths.data_dir", tmp_path)

    # Make the directory read-only to simulate file writing error
    tmp_path.chmod(0o444)

    # Execute
    result = cli_runner.invoke(parser.app)

    # Assert
    assert result.exit_code == 1
    assert "Permission denied" in result.stdout

    # Cleanup
    tmp_path.chmod(0o755)
