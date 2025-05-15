"""Paths for data and static resources used by the web_scrapping package."""

from pathlib import Path

root = Path(__file__).parent.parent.parent

data_dir = root / "data"
web_dir = data_dir / "web"
static_html = web_dir / "static.html"
