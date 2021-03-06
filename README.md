# API

## Running

You can run this API with or without docker. Either way, it will
bind to your port 8000 and offer a browsable API schema at
[localhost:8000/docs](http://localhost:8000/docs)

### With Docker

0. Build the image with `docker build . -t api`
1. Run with `docker run -d -p 80:80 -v $(pwd):/app -e MODULE_NAME="api.main" api /start-reload.sh` (with Live reload for testing) or
Run with gnicorn `docker run -d -p 80:80 -v $(pwd):/app -e MODULE_NAME="api.main" api`
2. The server will be available at [0.0.0.0:80](http://0.0.0.0:80)
4. More infos in (https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker)

### With Poetry

0. Install Python >= 3.7
1. Install [Poetry](https://python-poetry.org/)
2. Clone this project and install its dependencies with `poetry install`
3. Run it with `poetry run uvicorn api.main:app --reload`

## Tests

This API was developed on an TDD/BDD-like fashion. Currently, the tests cover
mostly sucess cases for the features and may be executed with

```sh
poetry run pytest
```

A line coverage report will be displayed by default.

## Developing

This project uses `pre-commit` to enabled it, install `pre-commit` and
issue a `pre-commit install --install-hooks` command
