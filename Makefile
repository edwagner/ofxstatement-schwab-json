all: test mypy black

.PHONY: test
test:
	pytest

.PHONY: coverage
coverage:
	pytest --cov src/ofxstatement

.PHONY: black
black:
	black src tests

.PHONY: mypy
mypy:
	mypy src tests
