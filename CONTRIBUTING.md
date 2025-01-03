# Contributing

## Installation
- Clone this repository
- Install [Poetry](https://python-poetry.org/docs/)
    - Generally `curl -sSL https://install.python-poetry.org | python3 -` works well
- Activate Poetry: `poetry shell`
- Install dependencies: `poetry install`

## CLI Development
This project uses [Typer](https://typer.tiangolo.com/) for its CLI. To develop and test commands, use the following command: `typer postit/cli.py run [COMMAND]`.

For example, to run the example command, run `typer postit/cli.py run example`.