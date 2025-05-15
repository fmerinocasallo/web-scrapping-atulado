import pytest
from src.web_scrapping import parser


def test_get_rates_not_implemented():
    with pytest.raises(NotImplementedError):
        parser.get_rates()
