# Web Scrapping to Monitor Electricity Rates

This package contains a script to parse the current electricity rates
from the website of [A tu Lado Energía (Hidroelectrica El Carmen Energía)](https://www.atuladoenergia.com),
a Spanish electricity company.

## Table of contents
1. [:question: Problem](#problem)
2. [:dart: Goal](#goal)
3. [:toolbox: Solution](#solution)
4. [:hammer: Installation](#install)
5. [:white_check_mark: Testing](#tests)
6. [:robot: Continuous Integration & Monitoring](#ci)
<div id="problem"></div>

## :question: Problem

My previous provider, [Naturgy](https://www.naturgy.es), updated my contract rates
and I was not happy with the new prices.

As a result, I have recently changed my electricity provider to [A tu Lado Energía (Hidroelectrica El Carmen Energía)](https://www.atuladoenergia.com), which at the time was offering the best rates
for my consumption profile.

However, the company does not provide an API to access the current rates,
which, I was told, may change at the 1st of every month without prior notice.

Their alternatives (call them or check their website) were not appealing to me,
so I decided to automate the process of checking their website
to get the latest information.

<div id="goal"></div>

## :dart: Goal

The goal of this project is to provide a simple tool to parse the current electricity rates
from the website of [A tu Lado Energía (Hidroelectrica El Carmen Energía)](https://www.atuladoenergia.com),
a Spanish electricity company, and export them as a JSON file.

<div id="solution"></div>

## :toolbox: Solution

The source code of the proposed solution is located in [`src/web_scrapping/parser.py`](src/web_scrapping/parser.py).

The proposed solution leverages [Typer](https://typer.tiangolo.com)
to develop a CLI application so users can easly call the proposed parser from terminal.

It also uses [Selenium](https://www.selenium.dev)
to scrape the website of the electricity company
and [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/)
to parse the HTML content.

<div id="install"></div>

## :hammer: Installation

### Recommended: Using Pixi

[Pixi](https://prefix.dev/docs/pixi/) is a modern environment and package manager
that ensures reproducibility and easy setup.
To create and activate the development environment, run:

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

> **Note:** The `requirements.txt` and `environment.yml` files are kept in sync with
the main dependencies. If you add or update dependencies,
please update these files accordingly.

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

<div id="tests"></div>

## :white_check_mark: Testing

Writing tests for your code is a great practice.
Tests helps you not only identify and resolve issues early but also debug your code faster.
As a result, tests boost your productivity and promote more robust software.
If you depend on a chunk of code, you should write tests for it.

During software development, you may inadvertently alter
an existing chunk of code on which your project depends.
This change may break other functions or workflows
that rely on that code snippet.
Writing tests that get automatically executed automatically and continuously
will help you catch these changes before you merge them into your codebase.

I opted to use [pytest](https://docs.pytest.org/en/stable/) to write some tests
to ensure that my social networking application behaves as expected.
`pytest` makes it easy to write small and readable tests,
and is also well-equipped to grow in complexity if needed.

See `tests/` for more details about the written tests.

To automatically run all the tests included in this project,
execute the following shell command from the main directory:
```
pytest tests
```

You may want to get more details about the test coverage
by running the following shell command:
```
pytest tests --cov=src.sr_sw_dev --cov-report=term-missing
```

Note that other tools such as [mypy](https://www.mypy-lang.org/index.html)
(a static type checker) could also help you identify bugs in your programs
without even running them!

#### :traffic_light: Test-Driven Development

I have applied [**Test-Driven Development (TDD)**](https://en.wikipedia.org/wiki/Test-driven_development)
principles to this project.
This means that I have written the tests before the code.
This is a great practice because it forces you to think about the requirements
and the expected behavior of the code before you actually write it.

<div id="ci"></div>

## :robot: Continuous Integration & Monitoring
This project uses [GitHub Actions](https://docs.github.com/en/actions)
to ensure code quality and monitor the parser’s real-world performance:

#### :white_check_mark: Continuous Integration (CI)

**Workflow**: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

**When**: On every push and pull request to the main branch.

**What**: Runs the full offline test suite to ensure that no breaking changes
are introduced before merging.

**Why**: This guarantees that all code in main is stable
and passes all tests using a static, reproducible copy of the website.

#### :satellite: Online Parser Monitoring

**Workflow**: [`.github/workflows/online-monitor.yml`](.github/workflows/online-monitor.yml)

**When**: Automatically runs at 14:00 UTC on the 5th of every month
(and can be triggered manually).

**What**: Runs the online test suite against the live A tu Lado Energía website.

**Why**: Detects if the website structure has changed and the parser
is no longer working as expected or if the rates of the Milenial plan have changed.

**Alert**: If the online tests fail, an email notification is sent to the maintainer.

These workflows help ensure the parser remains robust and up-to-date,
both in development and in production.

<div id="license"></div>

## :memo: License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.