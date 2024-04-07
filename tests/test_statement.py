import os

import ofxstatement
import pytest
from decimal import Decimal

from ofxstatement_schwab_json.plugin import SchwabJsonPlugin

import logging

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def statement() -> ofxstatement.statement.Statement:
    plugin = SchwabJsonPlugin(ofxstatement.ui.UI(), {})
    here = os.path.dirname(__file__)
    test_filename = os.path.join(here, "sample-statement.json")

    parser = plugin.get_parser(test_filename)
    return parser.parse()


def test_parsing(statement):
    assert statement is not None
    assert len(statement.invest_lines) == 16


def test_ids(statement):
    assert statement.invest_lines[0].id == "20230922-1"
    assert statement.invest_lines[1].id == "20230922-2"


def test_transfer(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240212-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "XFER"


def test_journal_cash(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240207-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "XFER"


def test_journal_security(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240208-1")
    assert line.trntype == "TRANSFER"
    assert line.trntype_detailed is None
    assert line.units == -6
    assert line.amount == 0
    assert line.unit_price == 1


def test_sell(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240209-1")
    assert line.trntype == "SELLSTOCK"
    assert line.trntype_detailed == "SELL"
    assert line.units == -1000
    assert line.amount == 1000


def test_interest(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240116-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "INT"


def test_wire(statement):
    line = next(x for x in statement.invest_lines if x.id == "20231212-3")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "DEBIT"


def test_bank_fee(statement):
    line = next(x for x in statement.invest_lines if x.id == "20231212-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "SRVCHG"


def test_bank_misc(statement):
    line = next(x for x in statement.invest_lines if x.id == "20231212-2")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "OTHER"


def test_spin_off(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240401-1")
    assert line.trntype == "TRANSFER"
    assert line.trntype_detailed is None
    assert line.units == 123
    assert line.amount == 0
    assert line.unit_price == 0


def test_cash_in_lieu(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240402-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "CREDIT"
    assert line.amount == Decimal("32.68")
