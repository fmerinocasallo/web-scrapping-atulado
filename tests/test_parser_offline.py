"""
Test suite for the web_scrapping.parser module using an offline copy of the website.

Contains tests for parsing electricity rates from A tu Lado Energía.
"""

import pytest

from src.web_scrapping import paths
from tests.base_test_parser import BaseTestParser


class TestParserOffline(BaseTestParser):
    """Test suite for the web_scrapping.parser module using an offline copy of the website."""

    @pytest.fixture
    def html(self) -> str:
        """
        Fixture to load the offline copy of the A tu Lado Energía website.

        Returns:
            str: The HTML content of the A tu Lado Energía website.
        """
        with open(paths.static_html, encoding="utf-8") as f:
            return f.read()
