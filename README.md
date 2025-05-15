# Web Scrapping to Monitor Electricity Rates

This package contains a script to parse the current electricity rates
from the website of [A tu Lado Energía (Hidroelectrica El Carmen Energía)](https://www.atuladoenergia.com),
a Spanish electricity company.

<div id="problem"></div>

## :question: Problem

My previous provider, [Naturgy](https://www.naturgy.es), updated my contract rates
and I was not happy with the new prices.

As a result, I have recently changed my electricity provider to [A tu Lado Energía (Hidroelectrica El Carmen Energía)](https://www.atuladoenergia.com), which at the time was offering the best rates
for my consumption profile.

However, the company does not provide an API to access the current rates,
which, I was told, may change at the 1st of every month without prior notice.

Their alternatives (call them or check their website) were not appealing to me,
so I decided to automate the process of checking their website to get the latest information.

<div id="goal"></div>

## :dart: Goal

The goal of this project is to provide a simple tool to parse the current electricity rates
from the website of [A tu Lado Energía (Hidroelectrica El Carmen Energía)](https://www.atuladoenergia.com),
a Spanish electricity company, and export them as a JSON file.

<div id="solution"></div>

## :toolbox: Solution

The source code of the proposed solution is located in [`src/web_scrapping/parser.py`](src/web_scrapping/parser.py).

The proposed solution leverages [Typer](https://typer.tiangolo.com) to develop a CLI application
so users can easly call the proposed parser from terminal.

It also uses [Selenium](https://www.selenium.dev) to scrape the website of the electricity company
and [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/) to parse the HTML content.

## :hammer: Installation

### Recommended: Using Pixi

[Pixi](https://prefix.dev/docs/pixi/) is a modern environment and package manager that ensures reproducibility and easy setup. To create and activate the development environment, run:

```bash
pixi install
pixi shell
```

### Alternative methods

You can also set up the development environment using your preferred tool:

#### Using pip
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Using Poetry
```bash
poetry add $(cat requirements.txt)
```

#### Using conda
```bash
conda env create -f environment.yml
conda activate web-scrapping
```

> **Note:** The `requirements.txt` and `environment.yml` files are kept in sync with the main dependencies. If you add or update dependencies, please update these files accordingly.

***

After setting up the development environment,
run the following shell command from the root directory of this project
to install the package as a Python library:

```
pip install --upgrade build
python -m build
python -m pip install -e .
```

Once installed, run the following shell command to see the accepted arguments:

```
python -m src.web_scrapping.parser --help
```

Next, run the following shell command to see it in action:

```
python -m src.web_scrapping.parser --plan "milenial"
```

It will create a JSON file [`milenial_rates.json`](data/milenial_rates.json)
in the [`data`](data) directory with the rates for the `milenial` plan.

<div id="license"></div>

## :memo: License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.