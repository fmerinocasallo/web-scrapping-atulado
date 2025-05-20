"""Tests for data validation in the parser module."""

import pytest
from pydantic import ValidationError

from src.web_scrapping.parser import (
    ConsumptionRates,
    ElectricityRates,
    PowerRates,
)


def test_consumption_rates_valid_data():
    """Test that valid consumption rates are accepted."""
    valid_data = {
        "peak": (0.1234, "€/kWh"),
        "flat": (0.1234, "€/kWh"),
        "valley": (0.1234, "€/kWh"),
    }
    consumption = ConsumptionRates(**valid_data)
    assert consumption.model_dump() == valid_data


def test_consumption_rates_invalid_value():
    """Test that negative consumption rates are rejected."""
    invalid_data = {
        "peak": (-0.1, "€/kWh"),
        "flat": (0.1234, "€/kWh"),
        "valley": (0.1234, "€/kWh"),
    }
    with pytest.raises(ValidationError) as exc_info:
        ConsumptionRates(**invalid_data)
    assert "Consumption rate values must be positive" in str(exc_info.value)


def test_consumption_rates_invalid_unit():
    """Test that consumption rates with wrong unit are rejected."""
    invalid_data = {
        "peak": (0.1234, "€/kW day"),
        "flat": (0.1234, "€/kWh"),
        "valley": (0.1234, "€/kWh"),
    }
    with pytest.raises(ValidationError) as exc_info:
        ConsumptionRates(**invalid_data)
    assert "Consumption rates units must be €/kWh" in str(exc_info.value)


def test_power_rates_valid_data():
    """Test that valid power rates are accepted."""
    valid_data = {
        "peak": (0.1234, "€/kW day"),
        "flat": (0.1234, "€/kW day"),
        "valley": (0.1234, "€/kW day"),
    }
    power = PowerRates(**valid_data)
    assert power.model_dump() == valid_data


def test_power_rates_invalid_value():
    """Test that negative power rates are rejected."""
    invalid_data = {
        "peak": (-0.1, "€/kW day"),
        "flat": (0.1234, "€/kW day"),
        "valley": (0.1234, "€/kW day"),
    }
    with pytest.raises(ValidationError) as exc_info:
        PowerRates(**invalid_data)
    assert "Rate value must be positive" in str(exc_info.value)


def test_power_rates_invalid_unit():
    """Test that power rates with wrong unit are rejected."""
    invalid_data = {
        "peak": (0.1234, "€/kWh"),
        "flat": (0.1234, "€/kW day"),
        "valley": (0.1234, "€/kW day"),
    }
    with pytest.raises(ValidationError) as exc_info:
        PowerRates(**invalid_data)
    assert "Power rates must use €/kW day" in str(exc_info.value)


def test_electricity_rates_valid_data():
    """Test that valid electricity rates are accepted."""
    valid_data = {
        "consumption": {
            "peak": (0.1234, "€/kWh"),
            "flat": (0.1234, "€/kWh"),
            "valley": (0.1234, "€/kWh"),
        },
        "power": {
            "peak": (0.1234, "€/kW day"),
            "flat": (0.1234, "€/kW day"),
            "valley": (0.1234, "€/kW day"),
        },
    }
    rates = ElectricityRates(**valid_data)
    assert rates.model_dump() == valid_data


def test_electricity_rates_missing_consumption():
    """Test that electricity rates without consumption rates are rejected."""
    invalid_data = {
        "power": {
            "peak": (0.1234, "€/kW day"),
            "flat": (0.1234, "€/kW day"),
            "valley": (0.1234, "€/kW day"),
        },
    }
    with pytest.raises(ValidationError) as exc_info:
        ElectricityRates(**invalid_data)
    assert "consumption" in str(exc_info.value)


def test_electricity_rates_missing_power():
    """Test that electricity rates without power rates are rejected."""
    invalid_data = {
        "consumption": {
            "peak": (0.1234, "€/kWh"),
            "flat": (0.1234, "€/kWh"),
            "valley": (0.1234, "€/kWh"),
        },
    }
    with pytest.raises(ValidationError) as exc_info:
        ElectricityRates(**invalid_data)
    assert "power" in str(exc_info.value)
