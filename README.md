# corpus-x

![Github CI](https://github.com/justmars/corpus-x/actions/workflows/main.yml/badge.svg)

Create the `x.db` sqlite database for lawdata; utilized in the [LawSQL dataset](https://lawsql.com).

## Documentation

See [documentation](https://justmars.github.io/corpus-x).

## Development

Checkout code, create a new virtual environment:

```sh
poetry add corpus-x # python -m pip install corpus-x
poetry update # install dependencies
poetry shell
```

Run tests:

```sh
pytest
```
