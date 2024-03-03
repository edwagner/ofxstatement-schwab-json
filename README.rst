~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Schwab JSON plugin for ofxstatement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project is a plugin for ofxstatement that will process a JSON file
of investment account transaction history from Charles Schwab.

`ofxstatement`_ is a tool to convert proprietary bank statement to OFX format,
suitable for importing to GnuCash. Plugin for ofxstatement parses a
particular proprietary bank statement format and produces common data
structure, that is then formatted into an OFX file.

.. _ofxstatement: https://github.com/kedder/ofxstatement


```
ofxstatement convert -t schwab_json Name_XXX321_Transactions_20240101-123456.json out.ofx
```

Running
=======

I've needed to make a few changes to ofxstatement, so this depends on my fork of that project.

Use ``pipenv`` to run the converter::

  $ pip3 install pipenv --user (if it hasn't already been set up)
  $ cd ofxstatement-schwab-json
  $ pipenv sync --dev
  $ pipenv shell
  $ ofxstatement convert -t schwab_json Name_* name.ofx


Setting up development environment
==================================

It is recommended to use ``pipenv`` to make a clean development environment.
Setting up dev environment for writing a plugin is easy::

  $ cd ofxstatement-schwab-json
  $ pipenv sync --dev
  $ pipenv shell
  $ pytest

This will download all the dependencies and install them into your virtual
environment. After this, you should be able to do::

  $ ofxstatement list-plugins
  The following plugins are available:

    schwab_json      Parses Schwab JSON export of investment transactions

