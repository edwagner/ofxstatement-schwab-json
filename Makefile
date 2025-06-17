all: test mypy black

.PHONY: test
test:
	pytest

.PHONY: coverage
coverage:
	pytest --cov src/ofxstatement_schwab_json --cov-report term --cov-report html

.PHONY: black
black:
	black src tests

.PHONY: mypy
mypy:
	mypy src tests
