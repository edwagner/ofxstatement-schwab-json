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
    assert len(statement.invest_lines) == 27


def test_ids(statement):
    assert statement.invest_lines[0].id == "20230922-1"
    assert statement.invest_lines[1].id == "20230922-2"


def test_transfer_cash(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240212-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "XFER"
    assert line.amount == -1500
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_transfer_cash_bank(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250529-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "XFER"
    assert line.amount == -100
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_journal_cash(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240207-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "XFER"
    assert line.amount == Decimal("-0.09")
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_security_transfer_cash(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240121-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "XFER"
    assert line.amount == 1000
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_journal_security(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240208-1")
    assert line.trntype == "TRANSFER"
    assert line.trntype_detailed is None
    assert line.units == -6
    assert line.security_id == "SWVXX"
    assert line.unit_price == 1
    assert line.amount == 0


def test_security_transfer(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240120-1")
    assert line.trntype == "TRANSFER"
    assert line.trntype_detailed is None
    assert line.units == 1377
    assert line.security_id == "AAPL"
    assert line.unit_price == 0
    assert line.amount == 0


def test_buy(statement):
    line = next(x for x in statement.invest_lines if x.id == "20230922-1")
    assert line.trntype == "BUYSTOCK"
    assert line.trntype_detailed == "BUY"
    assert line.units == 100
    assert line.amount == -100
    assert line.security_id == "SWVXX"
    assert line.unit_price == 1


def test_sell(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240209-1")
    assert line.trntype == "SELLSTOCK"
    assert line.trntype_detailed == "SELL"
    assert line.units == -1000
    assert line.amount == 1000
    assert line.security_id == "SWVXX"
    assert line.unit_price == 1


def test_dividend(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240117-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("25.81")
    assert line.security_id == "SWVXX"
    assert line.unit_price is None


def test_dividend2(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240118-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("100.76")
    assert line.security_id == "AAPL"
    assert line.unit_price is None


def test_dividend3(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240119-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("96.00")
    assert line.security_id == "AAPL"
    assert line.unit_price is None


def test_dividend4(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250110-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("622.50")
    assert line.security_id == "HASI"
    assert line.unit_price is None


def test_dividend5_special_dividend(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250321-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("19.59")
    assert line.security_id == "MTUM"
    assert line.unit_price is None


def test_interest(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240116-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "INT"
    assert line.amount == Decimal("0.30")
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_wire(statement):
    line = next(x for x in statement.invest_lines if x.id == "20231212-3")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "DEBIT"
    assert line.amount == Decimal("-4005.44")
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_bank_fee(statement):
    line = next(x for x in statement.invest_lines if x.id == "20231212-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "SRVCHG"
    assert line.amount == Decimal("-15")
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_bank_misc(statement):
    line = next(x for x in statement.invest_lines if x.id == "20231212-2")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "OTHER"
    assert line.amount == Decimal("15")
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_split(statement):
    line = next(x for x in statement.invest_lines if x.id == "20241011-1")
    assert line.trntype == "TRANSFER"
    assert line.trntype_detailed is None
    assert line.security_id == "SCHG"
    assert line.units == 300
    assert line.amount == 0
    assert line.unit_price == Decimal("26.3375")


def test_spin_off(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240401-1")
    assert line.trntype == "TRANSFER"
    assert line.trntype_detailed is None
    assert line.security_id == "SOLV"
    assert line.units == 123
    assert line.amount == 0
    assert line.unit_price == 0


def test_cash_in_lieu(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240402-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "CREDIT"
    assert line.amount == Decimal("32.68")
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_div_adjustment(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250228-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("-1.50")
    assert line.security_id == "GEV"
    assert line.unit_price is None


def test_adr_mgmt_fee(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250410-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "SRVCHG"
    assert line.units is None
    assert line.amount == Decimal("-2.63")
    assert line.security_id is None
    assert line.unit_price is None

def test_nra_tax_adj(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250515-1")
    assert line.trntype == "INVEXPENSE"
    assert line.trntype_detailed is None
    assert line.units is None
    assert line.amount == Decimal("-0.29")
    assert line.security_id == "AAPL"
    assert line.unit_price is None


def test_advisor_fee(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250610-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "XFER"
    assert line.units is None
    assert line.amount == Decimal("-419.08")
    assert line.security_id is None
    assert line.unit_price is None
