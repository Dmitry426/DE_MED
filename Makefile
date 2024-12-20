.PHONY: dev pre-commit isort black mypy flake8 pylint lint

dev: pre-commit

pre-commit:
	pre-commit install
	pre-commit autoupdate

isort:
	isort . --profile black

flake8:
	flake8  mvp_sneakers_api

black:
	black .

mypy:
	mypy -p mvp_sneakers_api

pylint:
	pylint mvp_sneakers_api


lint: isort black mypy  pylint flake8

build:
	poetry build

