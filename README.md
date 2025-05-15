# Web Scrapping to Monitor Electricity Rates

This package contains a script to parse the current electricity rates
from the website of [A tu Lado Energía (Hidroelectrica El Carmen Energía)](https://www.atuladoenergia.com),
a Spanish electricity company.

## Installation

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

To install the proposed solution as a Python library,
run the following shell command from the root directory of this project:

```
pip install --upgrade build
python -m build
python -m pip install -e .
```

<div id="license"></div>

## :memo: License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.