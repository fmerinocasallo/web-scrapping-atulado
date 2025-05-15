"""
Test suite for the web_scrapping.parser module using the online version of the website.

Contains tests for parsing electricity rates from A tu Lado Energía.
"""

import sys

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from tests.base_test_parser import BaseTestParser


class TestParserOnline(BaseTestParser):
    """Test suite for the web_scrapping.parser module using the online version of the website."""

    @pytest.fixture
    def html(self) -> str:
        """
        Fixture to load the online version of the A tu Lado Energía website.

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
        except TimeoutException:
            print(
                "ERROR: Could not find any reference to the 'Milenial' plan "
                "in the online version of the A tu Lado Energía website "
                "after 15 seconds. The website may have changed "
                "or there is a connection problem."
            )
            driver.quit()
            sys.exit(1)

        # Get the page source after JavaScript rendering
        html = driver.page_source

        # Close the browser (it's no longer needed, and frees up resources)
        driver.quit()

        return html
