"""
Parser for current electricity rates from A tu Lado Energía.

Provides tools to extract consumption and power prices from the company's website.
"""

import re
import sys
from typing import Literal

import typer
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, field_validator
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from unidecode import unidecode
from webdriver_manager.chrome import ChromeDriverManager

from src.web_scrapping import paths

app = typer.Typer()


class ConsumptionRates(BaseModel):
    """Model for consumption rates."""

    peak: tuple[float, str] = Field(description="Peak rate (value, unit)")
    flat: tuple[float, str] = Field(description="Flat rate (value, unit)")
    valley: tuple[float, str] = Field(description="Valley rate (value, unit)")

    @field_validator("peak", "flat", "valley")
    @classmethod
    def validate_period(cls, v: tuple[float, str]) -> tuple[float, str]:
        """Validate that consumption rates use €/kWh and have positive values."""
        value, unit = v
        if value <= 0:
            raise ValueError("Consumption rate values must be positive")
        if unit != "€/kWh":
            raise ValueError("Consumption rate units must be €/kWh")
        return v


class PowerRates(BaseModel):
    """Model for power rates."""

    peak: tuple[float, str] = Field(description="Peak rate (value, unit)")
    flat: tuple[float, str] = Field(description="Flat rate (value, unit)")
    valley: tuple[float, str] = Field(description="Valley rate (value, unit)")

    @field_validator("peak", "flat", "valley")
    @classmethod
    def validate_period(cls, v: tuple[float, str]) -> tuple[float, str]:
        """Validate that power rates use €/kW day and have positive values."""
        value, unit = v
        if value <= 0:
            raise ValueError("Power rate values must be positive")
        if unit != "€/kW day":
            raise ValueError("Power rate units must be €/kW day")
        return v


class ElectricityRates(BaseModel):
    """Model for electricity rates."""

    consumption: ConsumptionRates
    power: PowerRates


def get_html() -> str:
    """
    Load the online version of the A tu Lado Energía website.

    Returns:
        str: The HTML content of the A tu Lado Energía website.
    """
    URL = "https://clientes.atuladoenergia.com/tarifas"

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    # Initialize WebDriver
    # This will automatically download and manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    # Create a new Chrome browser instance, with the options we've set up
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Get the page
    driver.get(URL)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//p[contains(translate(., 'milenial', 'MILENIAL'), 'MILENIAL')]",
                )
            )
        )
    except TimeoutException as e:
        print(
            "ERROR: Could not find any reference to the 'Milenial' plan "
            "in the online version of the A tu Lado Energía website "
            "after 15 seconds. The website may have changed "
            "or there is a connection problem.",
            file=sys.stderr,
        )
        driver.quit()
        raise typer.Exit(1) from e

    # Get the page source after JavaScript rendering
    html = driver.page_source

    # Close the browser (it's no longer needed, and frees up resources)
    driver.quit()

    return html


def _extract_value_unit(text: str) -> tuple[float, str]:
    """
    Extract the value and unit from the text.

    Args:
        text (str): The text to extract the value and unit from.

    Raises:
        ValueError: If the value and unit cannot be extracted from the text.

    Returns:
        tuple[float, str]: The value and unit.
    """
    match = re.search(r"([0-9]+[\.,]?[0-9]*)\s*(€/kWh|€/kW\s*día)", text)
    if match:
        value = float(match.group(1).replace(",", "."))
        unit = match.group(2).strip().replace("día", "day")
        return value, unit
    else:
        raise ValueError(f"Could not extract value and unit from {text}")


def _parse_section_rates(
    section_title: Literal["consumo", "potencia"],
    rates: BeautifulSoup,
) -> dict:
    """
    Parse rates for a section (consumption or power) from the rates div.

    Args:
        section_title (str): The section title to search for (case-insensitive).
        rates (BeautifulSoup): The rates div.

    Returns:
        dict: Nested dictionary with consumption and power rates by period.
    """
    PERIOD_TRANSLATE = {
        "punta": "peak",
        "llano": "flat",
        "valle": "valley",
    }
    PERIODS = ["peak", "flat", "valley"]
    result = {}
    title = rates.find("p", string=lambda t: t and section_title in t.lower())
    if not title:
        raise ValueError(f"Section '{section_title}' not found in the provided HTML.")
    else:
        # Gather all <p> after the title until the next title or end
        ps = []
        p = title.find_next_sibling("p")
        stop_class = "potencias-title" if section_title == "consumo" else None
        while p and not (
            stop_class and p.get("class") and stop_class in p.get("class", [])
        ):
            ps.append(p)
            p = p.find_next_sibling("p")
        if len(ps) == 1:
            # Single value for all periods
            value, unit = _extract_value_unit(ps[0].get_text(strip=True))
            for period in PERIODS:
                result[period] = (value, unit)
        else:
            # Multiple values for different periods
            for pp in ps:
                text = pp.get_text(strip=True)
                if ":" in text:
                    label, value_part = text.split(":", 1)
                    # Split by ' y ' to get all periods, strip and lowercase
                    periods_in_label = [p.strip().lower() for p in label.split(" y ")]
                    value, unit = _extract_value_unit(value_part.strip())
                    for period_es in periods_in_label:
                        period_en = PERIOD_TRANSLATE.get(period_es)
                        if period_en:
                            result[period_en] = (value, unit)
        return result


def parse_rates(html: str, plan: str) -> ElectricityRates:
    """
    Parse the electricity rates for the given plan from the HTML.

    Args:
        html (str): The HTML content.
        plan (str): The plan name to search for (case-insensitive).

    Returns:
        ElectricityRates: Validated electricity rates.

    Raises:
        ValueError: If the plan or rates are not found in the HTML.
    """
    # Parse the HTML
    soup = BeautifulSoup(html, "html.parser")
    rates_grid = soup.find("div", class_="rates-grid")
    plan_card = None

    # Find the plan card
    if rates_grid:
        for card in rates_grid.find_all("div", recursive=False):
            header = card.find("div", class_="card-header")
            if header:
                name_tag = header.find("p")
                if name_tag and plan.lower() in name_tag.get_text(strip=True).lower():
                    plan_card = card
                    break

    # Check if the plan card was found
    if not plan_card:
        raise ValueError(f"Plan '{plan}' not found in the provided HTML.")
    else:
        # Find the consumption and power rates
        rates = plan_card.find("div", class_="rates")
        if not rates:
            raise ValueError("Rates not found in the provided HTML.")
        else:
            # Parse the consumption and power rates
            consumption_rates = _parse_section_rates("consumo", rates)
            power_rates = _parse_section_rates("potencia", rates)

            # Convert to Pydantic models
            return ElectricityRates(
                consumption=ConsumptionRates(
                    peak=consumption_rates["peak"],
                    flat=consumption_rates["flat"],
                    valley=consumption_rates["valley"],
                ),
                power=PowerRates(
                    peak=power_rates["peak"],
                    flat=power_rates["flat"],
                    valley=power_rates["valley"],
                ),
            )


@app.command()
def main(plan: str = "milenial") -> None:
    """
    Parse the electricity rates for the given plan from the HTML.

    Args:
        plan (str, optional): The plan name to search for (case-insensitive).
            Defaults to "milenial".
    """
    try:
        html = get_html()
        parsed_rates = parse_rates(html, plan)

        with open(
            paths.data_dir / f"{unidecode(plan).replace(' ', '-')}_rates.json",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(parsed_rates.model_dump_json(indent=4))
    except (ValueError, PermissionError) as e:
        print(str(e), file=sys.stderr)
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
