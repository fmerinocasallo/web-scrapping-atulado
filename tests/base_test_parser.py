"""
Base test suite for the web_scrapping.parser module.

Contains tests for parsing electricity rates from A tu Lado Energía.
"""

import pytest
from bs4 import BeautifulSoup

from src.web_scrapping import parser


class BaseTestParser:
    """Base test suite for the web_scrapping.parser module."""

    @pytest.fixture
    def html(self):
        """Override this fixture in subclasses to provide HTML."""
        raise NotImplementedError

    def _remove_rates_divs(self, html: str) -> str:
        """Remove the rates divs from the HTML."""
        soup = BeautifulSoup(html, "html.parser")
        for div in soup.find_all("div", class_="rates"):
            div.decompose()
        return str(soup)

    def _remove_plan_div(self, html: str, plan_name: str) -> str:
        """
        Remove the div containing the specified plan from the HTML.

        Args:
            html (str): The HTML content.
            plan_name (str): The name of the plan to remove (case-insensitive).

        Returns:
            str: The modified HTML with the plan removed.
        """
        soup = BeautifulSoup(html, "html.parser")
        # Find all cards in the rates grid
        rates_grid = soup.find("div", class_="rates-grid")
        if not rates_grid:
            return str(soup)
        for card in rates_grid.find_all("div", recursive=False):
            header = card.find("div", class_="card-header")
            if header:
                name_tag = header.find("p")
                if (
                    name_tag
                    and plan_name.lower() in name_tag.get_text(strip=True).lower()
                ):
                    # Remove the card from the rates grid
                    card.decompose()
                    break

        return str(soup)

    def _remove_section_card(self, html: str, section_name: str) -> str:
        """
        Remove the card containing the specified section (e.g., 'Consumo' or 'Potencia') from the HTML.

        Args:
            html (str): The HTML content.
            section_name (str): The section name to remove (case-insensitive).

        Returns:
            str: The modified HTML with the section card removed.
        """
        soup = BeautifulSoup(html, "html.parser")
        # Find all cards in the rates grid
        rates_grid = soup.find("div", class_="rates-grid")
        if not rates_grid:
            return str(soup)
        for card in rates_grid.find_all("div", recursive=False):
            rates = card.find("div", class_="rates")
            if rates:
                # Look for a <p> tag with the section name
                section_p = rates.find(
                    "p", string=lambda t: t and section_name.lower() in t.lower()
                )
                if section_p:
                    # Remove the card from the rates grid
                    card.decompose()
                    break

        return str(soup)

    def test_extract_value_unit_consumption(self):
        """Test the extraction of value and unit from a text for consumption."""
        text = "100 €/kWh"
        value, unit = parser._extract_value_unit(text)
        assert value == 100
        assert unit == "€/kWh"

    def test_extract_value_unit_power(self):
        """Test the extraction of value and unit from a text for power."""
        text = "100 €/kW día"
        value, unit = parser._extract_value_unit(text)
        assert value == 100
        assert unit == "€/kW day"

    def test_extract_value_unit_raises_value_error(self):
        """Test that the extraction of value and unit from a text raises a ValueError."""
        text = "100 €"
        with pytest.raises(ValueError):
            parser._extract_value_unit(text)

    def test_parse_rates_no_consumption(self, html: str):
        """Test that the parsing of rates raises a ValueError when the consumption rates are not found."""
        with pytest.raises(ValueError):
            parser.parse_rates(html.replace("Consumo", ""), "milenial")

    def test_parse_rates_no_power(self, html: str):
        """Test that the parsing of rates raises a ValueError when the power rates are not found."""
        with pytest.raises(ValueError):
            parser.parse_rates(html.replace("Potencia", ""), "milenial")

    def test_parse_rates_no_rates(self, html: str):
        """Test that the parsing of rates raises a ValueError when the rates are not found."""
        with pytest.raises(ValueError) as excinfo:
            result = parser.parse_rates(self._remove_rates_divs(html), "milenial")
            print(f"result: {result}")
        assert str(excinfo.value) == "Rates not found in the provided HTML."

    def test_parse_rates_no_plan(self, html: str):
        """Test that the parsing of rates raises a ValueError when the plan is not found."""
        with pytest.raises(ValueError) as excinfo:
            result = parser.parse_rates(html.replace("Milenial", ""), "milenial")
            print(f"result: {result}")
        assert str(excinfo.value) == "Plan 'milenial' not found in the provided HTML."

    def test_parse_rates_invalid_html(self):
        """Test that the parsing of rates raises a ValueError when the HTML is invalid."""
        with pytest.raises(ValueError) as excinfo:
            result = parser.parse_rates("invalid HTML", "milenial")
            print(f"result: {result}")
        assert str(excinfo.value) == "Plan 'milenial' not found in the provided HTML."

    def test_parse_rates_milenial(self, html: str):
        """
        Test the parsing of electricity rates for the Milenial plan.

        Args:
            html (str): The HTML content of the plans page.
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
        result = parser.parse_rates(html, "milenial")
        print(f"result: {result}")
        assert result.model_dump() == expected
