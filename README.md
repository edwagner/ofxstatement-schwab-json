# Schwab JSON plugin for ofxstatement

This project is a plugin for [ofxstatement](https://github.com/kedder/ofxstatement)
that will process a JSON file of investment account transaction history from Charles Schwab
and convert it to OFX format, suitable for importing into GnuCash.

## Running

Use `pipenv` to run the converter:

```
$ pip3 install pipenv --user (if it hasn't already been set up)
$ cd ofxstatement-schwab-json
$ pipenv sync --dev
$ pipenv shell
$ ofxstatement convert -t schwab_json Name_XXX321_Transactions_20240101-123456.json import.ofx
```

## Setting up development environment

Use `pipenv` to make a clean development environment.

```
$ cd ofxstatement-schwab-json
$ pipenv sync --dev
$ pipenv shell
$ pytest
$ pip3 install mypy black
$ mypy src
$ black src
```

This will download all the dependencies and install them into your virtual
environment. After this, you should be able to do:

```
$ ofxstatement list-plugins
The following plugins are available:

  schwab_json      Parses Schwab JSON export of investment transactions
```

### Upgrading Dependencies

After running `pipenv shell`, run `pipenv update` to update everything.

## Packaging

```
$ python -m build
```

## References

* [OFX specification](https://financialdataexchange.org/common/Uploaded%20files/OFX%20files/OFX%20Banking%20Specification%20v2.3.pdf)
