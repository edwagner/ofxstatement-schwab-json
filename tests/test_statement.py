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
    assert len(statement.lines) == 12
    assert len(statement.invest_lines) == 36


def test_ids(statement):
    assert statement.lines[0].id == "20250529-1"
    assert statement.invest_lines[0].id == "20230922-1"
    assert statement.invest_lines[1].id == "20230922-2"


def test_advisor_fee(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250610-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "SRVCHG"
    assert line.units is None
    assert line.amount == Decimal("-419.08")
    assert line.security_id is None
    assert line.unit_price is None


def test_journal_security3(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250602-2")
    assert line.trntype == "TRANSFER"
    assert line.trntype_detailed is None
    assert line.units == Decimal("103.26")
    assert line.security_id == "SNSXX"
    assert line.unit_price == Decimal("0")
    assert line.amount == Decimal("0")


def test_journal_security2(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250602-1")
    assert line.trntype == "TRANSFER"
    assert line.trntype_detailed is None
    assert line.units == Decimal("-103.26")
    assert line.security_id == "SNSXX"
    assert line.unit_price == Decimal("0")
    assert line.amount == Decimal("0")


def test_transfer_cash_bank(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250529-2")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "XFER"
    assert line.amount == -100
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_nra_tax_adj(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250515-1")
    assert line.trntype == "INVEXPENSE"
    assert line.trntype_detailed is None
    assert line.units is None
    assert line.amount == Decimal("-0.29")
    assert line.security_id == "AAPL"
    assert line.unit_price is None


def test_adr_mgmt_fee(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250410-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "SRVCHG"
    assert line.units is None
    assert line.amount == Decimal("-2.63")
    assert line.security_id is None
    assert line.unit_price is None


def test_dividend5_special_dividend(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250321-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("19.59")
    assert line.security_id == "MTUM"
    assert line.unit_price is None


def test_div_adjustment(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250228-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("-1.50")
    assert line.security_id == "GEV"
    assert line.unit_price is None


def test_dividend4(statement):
    line = next(x for x in statement.invest_lines if x.id == "20250110-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("622.50")
    assert line.security_id == "HASI"
    assert line.unit_price is None


def test_split(statement):
    line = next(x for x in statement.invest_lines if x.id == "20241011-1")
    assert line.trntype == "TRANSFER"
    assert line.trntype_detailed is None
    assert line.security_id == "SCHG"
    assert line.units == 300
    assert line.amount == 0
    assert line.unit_price == Decimal("26.3375")


def test_funds_received(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240404-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "DEP"
    assert line.amount == Decimal("5555.00")
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_moneylink_deposit(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240403-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "DEP"
    assert line.amount == Decimal("1000.00")
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_cash_in_lieu(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240402-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "CREDIT"
    assert line.amount == Decimal("32.68")
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_spin_off(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240401-1")
    assert line.trntype == "TRANSFER"
    assert line.trntype_detailed is None
    assert line.security_id == "SOLV"
    assert line.units == 123
    assert line.amount == 0
    assert line.unit_price == 0


def test_transfer_cash(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240212-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "XFER"
    assert line.amount == -1500
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_sell(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240209-1")
    assert line.trntype == "SELLSTOCK"
    assert line.trntype_detailed == "SELL"
    assert line.units == -1000
    assert line.amount == 1000
    assert line.security_id == "SWVXX"
    assert line.unit_price == 1


def test_journal_security(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240208-1")
    assert line.trntype == "TRANSFER"
    assert line.trntype_detailed is None
    assert line.units == -6
    assert line.security_id == "SWVXX"
    assert line.unit_price == 1
    assert line.amount == 0


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


def test_security_transfer(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240120-1")
    assert line.trntype == "TRANSFER"
    assert line.trntype_detailed is None
    assert line.units == 1377
    assert line.security_id == "AAPL"
    assert line.unit_price == 0
    assert line.amount == 0


def test_dividend3(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240119-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("96.00")
    assert line.security_id == "AAPL"
    assert line.unit_price is None


def test_dividend2(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240118-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("100.76")
    assert line.security_id == "AAPL"
    assert line.unit_price is None


def test_dividend(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240117-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("25.81")
    assert line.security_id == "SWVXX"
    assert line.unit_price is None


def test_dividend6_prior_year_special_dividend(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240116-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("42.41")
    assert line.security_id == "QQQ"
    assert line.unit_price is None


def test_prior_year_dividend_reinvest(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240115-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("55.55")
    assert line.security_id == "SPY"
    assert line.unit_price is None


def test_special_qualified_dividend(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240114-1")
    assert line.trntype == "INCOME"
    assert line.trntype_detailed == "DIV"
    assert line.units is None
    assert line.amount == Decimal("1.00")
    assert line.security_id == "F"
    assert line.unit_price is None


def test_interest(statement):
    line = next(x for x in statement.invest_lines if x.id == "20240110-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "INT"
    assert line.amount == Decimal("0.30")
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_returned_check(statement):
    line = next(x for x in statement.invest_lines if x.id == "20231213-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "DEBIT"
    assert line.amount == Decimal("-555.00")
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


def test_bank_misc(statement):
    line = next(x for x in statement.invest_lines if x.id == "20231212-2")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "OTHER"
    assert line.amount == Decimal("15")
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


def test_interest_adjustment(statement):
    line = next(x for x in statement.invest_lines if x.id == "20231211-1")
    assert line.trntype == "INVBANKTRAN"
    assert line.trntype_detailed == "OTHER"
    assert line.amount == Decimal("-0.05")
    assert line.security_id is None
    assert line.units is None
    assert line.unit_price is None


def test_buy(statement):
    line = next(x for x in statement.invest_lines if x.id == "20230922-1")
    assert line.trntype == "BUYSTOCK"
    assert line.trntype_detailed == "BUY"
    assert line.units == 100
    assert line.amount == -100
    assert line.security_id == "SWVXX"
    assert line.unit_price == 1


def test_posted_incoming_wire(statement):
    line = next(x for x in statement.lines if x.id == "20251010-1")
    assert line.memo == "Incoming Wire"
    assert line.trntype == "CREDIT"
    assert line.amount == Decimal("399.00")


def test_posted_outgoing_wire(statement):
    line = next(x for x in statement.lines if x.id == "20251009-1")
    assert line.memo == "Outgoing Wire"
    assert line.trntype == "DEBIT"
    assert line.amount == Decimal("-400.00")


def test_posted_check(statement):
    line = next(x for x in statement.lines if x.id == "20251001-1")
    assert line.memo == "Check Paid #101"
    assert line.trntype == "CHECK"
    assert line.amount == Decimal("-870.80")


def test_posted_deposit(statement):
    line = next(x for x in statement.lines if x.id == "20250712-1")
    assert line.memo == "Deposit Mobile Banking"
    assert line.trntype == "DEP"
    assert line.amount == Decimal("8.00")


def test_posted_atmrebate(statement):
    line = next(x for x in statement.lines if x.id == "20250630-1")
    assert line.memo == "ATM Fee Rebate"
    assert line.trntype == "CREDIT"
    assert line.amount == Decimal("14.50")


def test_posted_visa_debit(statement):
    line = next(x for x in statement.lines if x.id == "20250625-1")
    assert line.memo == "ABC COMPANY LIMITED"
    assert line.trntype == "POS"
    assert line.amount == Decimal("-30.79")


def test_posted_ach_deposit(statement):
    line = next(x for x in statement.lines if x.id == "20250616-1")
    assert line.memo == "TRIAL ACCTVERIFY 250615"
    assert line.trntype == "CREDIT"
    assert line.amount == Decimal("0.25")


def test_posted_ach_withdrawal(statement):
    line = next(x for x in statement.lines if x.id == "20250616-2")
    assert line.memo == "TRIAL ACCTVERIFY 250615"
    assert line.trntype == "DEBIT"
    assert line.amount == Decimal("-0.46")


def test_posted_debit(statement):
    line = next(x for x in statement.lines if x.id == "20250615-1")
    assert line.memo == "ZELLE TO JOHN DOE"
    assert line.trntype == "DEBIT"
    assert line.amount == Decimal("-100")


def test_posted_atm_withdrawal(statement):
    line = next(x for x in statement.lines if x.id == "20250607-1")
    assert line.memo == "CHASE MAIN ST ANYTOWN"
    assert line.trntype == "ATM"
    assert line.amount == Decimal("-23.50")


def test_posted_interest(statement):
    line = next(x for x in statement.lines if x.id == "20250530-1")
    assert line.memo == "Interest Paid"
    assert line.trntype == "INT"
    assert line.amount == Decimal("0.03")


def test_posted_transfer(statement):
    line = next(x for x in statement.lines if x.id == "20250529-1")
    assert line.memo == "Funds Transfer from Brokerage"
    assert line.trntype == "XFER"
    assert line.amount == Decimal("100")
