"""
Test suite for the web_scrapping.parser module.

Contains tests for parsing electricity rates from A tu Lado Energía.
"""

import pytest
from bs4 import BeautifulSoup

from src.web_scrapping import parser, paths


@pytest.fixture
def static_html() -> str:
    """
    Fixture to load the Milenial HTML content.

    Returns:
        str: The HTML content of the Milenial page.
    """
    with open(paths.static_html, encoding="utf-8") as f:
        return f.read()


def _remove_rates_divs(html: str) -> str:
    """Remove the rates divs from the HTML."""
    soup = BeautifulSoup(html, "html.parser")
    for div in soup.find_all("div", class_="rates"):
        div.decompose()
    return str(soup)


def test_extract_value_unit_consumption():
    """Test the extraction of value and unit from a text for consumption."""
    text = "100 €/kWh"
    value, unit = parser._extract_value_unit(text)
    assert value == 100
    assert unit == "€/kWh"


def test_extract_value_unit_power():
    """Test the extraction of value and unit from a text for power."""
    text = "100 €/kW día"
    value, unit = parser._extract_value_unit(text)
    assert value == 100
    assert unit == "€/kW day"


def test_extract_value_unit_raises_value_error():
    """Test that the extraction of value and unit from a text raises a ValueError."""
    text = "100 €"
    with pytest.raises(ValueError):
        parser._extract_value_unit(text)


def test_parse_rates_no_consumption(static_html: str):
    """Test that the parsing of rates raises a ValueError when the consumption rates are not found."""
    with pytest.raises(ValueError):
        parser.parse_rates(static_html.replace("Consumo", ""), "milenial")


def test_parse_rates_no_power(static_html: str):
    """Test that the parsing of rates raises a ValueError when the power rates are not found."""
    with pytest.raises(ValueError):
        parser.parse_rates(static_html.replace("Potencia", ""), "milenial")


def test_parse_rates_no_rates(static_html: str):
    """Test that the parsing of rates raises a ValueError when the rates are not found."""
    with pytest.raises(ValueError) as excinfo:
        result = parser.parse_rates(_remove_rates_divs(static_html), "milenial")
        print(f"result: {result}")
    assert str(excinfo.value) == "Rates not found in the provided HTML."


def test_parse_rates_no_plan(static_html: str):
    """Test that the parsing of rates raises a ValueError when the plan is not found."""
    with pytest.raises(ValueError) as excinfo:
        result = parser.parse_rates(static_html.replace("Milenial", ""), "milenial")
        print(f"result: {result}")
    assert str(excinfo.value) == "Plan 'milenial' not found in the provided HTML."


def test_parse_rates_invalid_html():
    """Test that the parsing of rates raises a ValueError when the HTML is invalid."""
    with pytest.raises(ValueError) as excinfo:
        result = parser.parse_rates("invalid HTML", "milenial")
        print(f"result: {result}")
    assert str(excinfo.value) == "Plan 'milenial' not found in the provided HTML."


def test_parse_rates_milenial(static_html: str):
    """
    Test the parsing of electricity rates for the Milenial plan.

    Args:
        static_html (str): The HTML content of the plans page.
    """
    expected = {
        "consumption": {
            "peak": (0.089022, "€/kWh"),
            "flat": (0.089022, "€/kWh"),
            "valley": (0.089022, "€/kWh"),
        },
        "power": {
            "peak": (0.101597, "€/kW day"),
            "flat": (0.101597, "€/kW day"),
            "valley": (0.033202, "€/kW day"),
        },
    }
    result = parser.parse_rates(static_html, "milenial")
    print(f"result: {result}")
    assert result == expected
