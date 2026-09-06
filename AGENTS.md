# AGENTS.md

## Project overview

`ofxstatement-schwab-json` is a plugin for
[ofxstatement](https://github.com/kedder/ofxstatement) that converts a JSON
export of Charles Schwab investment account transaction history into OFX,
suitable for importing into GnuCash. See [README.md](README.md) for user-facing
documentation, including known limitations and OFX structure notes.

## Code layout

* `src/ofxstatement_schwab_json/plugin.py` — the plugin implementation
  (parses the Schwab JSON export and produces OFX statement data).
* `tests/test_statement.py` — the test suite.
* `tests/sample-statement.json` — sample Schwab JSON export used by the tests.
* `docs/` — reference material, including the OFX specification.

## Build, test, and lint commands

Run tests, type checks, and formatting via the [Makefile](Makefile):

## Code style

* Format code with `black` (see Makefile for invocation).
* Type-check with `mypy`; keep new code fully typed.
* Match the style and conventions of the surrounding code.

## Dependency upgrades / Dependabot alerts

To check for GitHub Dependabot security alerts and upgrade dependencies:

1. Run `gh api /repos/<owner>/<repo_name>/dependabot/alerts` to retrieve a
   JSON list of all open alerts.
2. Upgrade dependencies (see README.md).
3. Verify that the updated versions resolve the alerts.

## Commit and PR guidelines

* Run the full test suite (`uv run make all`) before committing.
* Increment the version number in pyproject.toml as appropriate using semantic versioning.
* Commit changes with a clear, conventional message, e.g.
  `chore(deps): Upgrade dependencies to fix security advisories`.
* Wait for user confirmation before pushing a new branch to the remote
  repository.
