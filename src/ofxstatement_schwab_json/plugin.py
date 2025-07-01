from datetime import datetime
from decimal import Decimal
import re
from os import path
from typing import Dict

from ofxstatement.plugin import Plugin
from ofxstatement.parser import AbstractStatementParser
from ofxstatement.statement import Statement, InvestStatementLine, StatementLine

import logging

LOGGER = logging.getLogger(__name__)

import json

POSTED_TRANSACTION_TYPES = {
    # Map Schwab PostedTransactions types to ofxstatement TRANSACTION_TYPES
    "ATM": "ATM",
    "ATMREBATE": "CREDIT",
    "DEBIT": "DEBIT",
    "INTADJUST": "INT",
    "TRANSFER": "XFER",
    "VISA": "POS",
}


class SchwabJsonPlugin(Plugin):
    """Parses Schwab JSON export of investment transactions"""

    def get_parser(self, filename: str) -> "SchwabJsonParser":
        return SchwabJsonParser(filename)


class SchwabJsonParser(AbstractStatementParser):
    statement: Statement

    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename = filename
        self.statement = Statement()
        self.statement.broker_id = "Schwab"
        match = re.search(r"(.*)_Transactions_.*\.json", path.basename(filename))
        if match:
            self.statement.account_id = match[1]
        self.id_generator = IdGenerator()

    def parse(self) -> Statement:
        """Main entry point for parsers"""
        with open(self.filename, "r") as f:
            # Reverse the lines so that they are in chronological order
            loaded = json.load(f)
            posted_transactions = reversed(
                # Banking / Checking accounts
                loaded.get("PostedTransactions", [])
            )
            brokerage_transactions = reversed(
                # Brokerage accounts
                loaded.get("BrokerageTransactions", [])
            )
            self.import_lines(
                posted_transactions=posted_transactions,
                brokerage_transactions=brokerage_transactions,
            )
            return self.statement

    def import_lines(self, posted_transactions, brokerage_transactions):
        for tran in posted_transactions:
            date = datetime.strptime(tran["Date"][0:10], "%m/%d/%Y")
            id = self.id_generator.create_id(date)
            self.add_statement_line(id, date, tran)

        for tran in brokerage_transactions:
            date = datetime.strptime(tran["Date"][0:10], "%m/%d/%Y")
            id = self.id_generator.create_id(date)

            action = tran["Action"]
            if action == "Sell":
                self.add_sell_line(id, date, tran)
            elif (
                action == "Cash Dividend"
                or action == "Qualified Dividend"
                or action == "Non-Qualified Div"
                or action == "Pr Yr Cash Div"
                or action == "Pr Yr Non Qual Div"
                or action == "Pr Yr Non-Qual Div"
                or action == "Qual Div Reinvest"
                or action == "Reinvest Dividend"
                or action == "Special Dividend"
                or action == "Div Adjustment"
            ):
                self.add_income_line(id, date, "DIV", tran)
            elif action == "Long Term Cap Gain":
                self.add_income_line(id, date, "CGLONG", tran)
            elif action == "Short Term Cap Gain":
                self.add_income_line(id, date, "CGSHORT", tran)
            elif action == "Bank Interest" and len(tran["Symbol"]) > 0:
                self.add_income_line(id, date, "INTEREST", tran)
            elif action == "NRA Tax Adj" and len(tran["Symbol"]) > 0:
                self.add_invexpense_line(id, date, tran)
            elif action == "Buy" or action == "Reinvest Shares":
                self.add_buy_line(id, date, tran)
            elif action == "ADR Mgmt Fee" or action == "Advisor Fee":
                self.add_bank_line(id, date, "SRVCHG", tran)
            elif len(tran["Symbol"]) > 0 and (
                action == "Journal"
                or action == "Journaled Shares"
                or action == "Spin-off"
                or action == "Stock Split"
                or action == "Security Transfer"
            ):
                self.add_transfer_line(id, date, tran)
            elif len(tran["Symbol"]) == 0:
                if (
                    action == "Bank Interest"
                    or action == "Bond Interest"
                    or action == "Credit Interest"
                ):
                    self.add_bank_line(id, date, "INT", tran)
                elif (
                    action == "MoneyLink Transfer"
                    or action == "Bank Transfer"
                    or action == "Internal Transfer"
                    or action == "Journal"
                    or action == "Journaled Shares"
                    or action == "Security Transfer"
                ):
                    self.add_bank_line(id, date, "XFER", tran)
                elif action == "Wire Sent":
                    self.add_bank_line(id, date, "DEBIT", tran)
                elif action == "Service Fee":
                    self.add_bank_line(id, date, "SRVCHG", tran)
                elif action == "Misc Cash Entry":
                    self.add_bank_line(id, date, "OTHER", tran)
                else:
                    raise Exception(f'Unrecognized bank action: "{action}"')
            elif action == "Cash In Lieu":
                self.add_bank_line(id, date, "CREDIT", tran)
            else:
                raise Exception(f'Unrecognized action: "{action}"')

    def add_buy_line(self, id, date, details):
        line = InvestStatementLine(
            id=id,
            date=date,
            memo=f'{details["Action"]} {details["Description"]}',
        )
        line.trntype = "BUYSTOCK"
        line.trntype_detailed = "BUY"
        line.security_id = details["Symbol"]
        line.units = Decimal(re.sub("[,]", "", details["Quantity"]))
        line.unit_price = Decimal(re.sub("[$,]", "", details["Price"]))
        line.amount = Decimal(re.sub("[$,]", "", details["Amount"]))
        if len(details["Fees & Comm"]) > 0:
            line.fees = Decimal(re.sub("[$,]", "", details["Fees & Comm"]))
        line.assert_valid()
        self.statement.invest_lines.append(line)

    def add_sell_line(self, id, date, details):
        line = InvestStatementLine(
            id=id,
            date=date,
            memo=f'{details["Action"]} {details["Description"]}',
        )
        line.trntype = "SELLSTOCK"
        line.trntype_detailed = "SELL"
        line.security_id = details["Symbol"]
        line.units = Decimal(
            "-" + re.sub("[,-]", "", details["Quantity"])
        )  # Ensure a negative number
        line.unit_price = Decimal(re.sub("[$,]", "", details["Price"]))
        line.amount = Decimal(re.sub("[$,]", "", details["Amount"]))
        if len(details["Fees & Comm"]) > 0:
            line.fees = Decimal(re.sub("[$,]", "", details["Fees & Comm"]))
        line.assert_valid()
        self.statement.invest_lines.append(line)

    def add_transfer_line(self, id, date, details):
        line = InvestStatementLine(
            id=id,
            date=date,
            memo=f'{details["Action"]} {details["Description"]}',
        )
        line.trntype = "TRANSFER"
        line.security_id = details["Symbol"]
        line.units = Decimal(re.sub("[,]", "", details["Quantity"]))
        if len(details["Price"]) > 0:
            line.unit_price = Decimal(re.sub("[$,]", "", details["Price"]))
        else:
            line.unit_price = Decimal(0)
        if len(details["Amount"]) > 0:
            line.amount = Decimal(re.sub("[$,]", "", details["Amount"]))
        else:
            line.amount = Decimal(0)
        if details["Action"] == "Spin-off":
            LOGGER.warning(
                f"You will probably want to allocate some cost basis for the {line.security_id} spin-off."
            )
        if details["Action"] == "Stock Split":
            LOGGER.warning(
                f"You will probably want to allocate some cost basis for the {line.units} additional shares of {line.security_id} due to the stock split."
            )
        line.assert_valid()
        self.statement.invest_lines.append(line)

    def add_income_line(self, id, date, income_type, details):
        line = InvestStatementLine(
            id=id,
            date=date,
            memo=f'{details["Action"]} {details["Description"]}',
        )
        line.trntype = "INCOME"
        line.trntype_detailed = income_type
        line.security_id = details["Symbol"]
        line.amount = Decimal(re.sub("[$,]", "", details["Amount"]))
        line.assert_valid()
        self.statement.invest_lines.append(line)

    def add_invexpense_line(self, id, date, details):
        line = InvestStatementLine(
            id=id,
            date=date,
            memo=f'{details["Action"]} {details["Description"]}',
        )
        line.trntype = "INVEXPENSE"
        line.security_id = details["Symbol"]
        line.amount = Decimal(re.sub("[$,]", "", details["Amount"]))
        line.assert_valid()
        self.statement.invest_lines.append(line)

    def add_bank_line(self, id, date, action_type, details):
        line = InvestStatementLine(
            id=id,
            date=date,
            memo=f'{details["Action"]} {details["Description"]}',
        )
        line.trntype = "INVBANKTRAN"
        line.amount = Decimal(re.sub("[$,]", "", details["Amount"]))
        line.trntype_detailed = action_type
        line.assert_valid()
        self.statement.invest_lines.append(line)

    def add_statement_line(self, id, date, details):
        withdrawal = (
            Decimal(f'-{re.sub("[$,]", "", details["Withdrawal"])}')
            if details.get("Withdrawal")
            else None
        )

        deposit = (
            Decimal(f'{re.sub("[$,]", "", details["Deposit"])}')
            if details.get("Deposit")
            else None
        )

        line = StatementLine(
            id=id,
            date=date,
            memo=details.get("Description"),
            amount=withdrawal or deposit,
        )
        line.check_no = details.get("CheckNumber")
        if details["Type"] == "ACH":
            if withdrawal:
                line.trntype = "DEBIT"
            else:
                line.trntype = "CREDIT"
        else:
            line.trntype = POSTED_TRANSACTION_TYPES[details["Type"]]

        line.assert_valid()
        self.statement.lines.append(line)


class IdGenerator:
    """Generates a unique ID based on the date

    Hopefully any JSON file that we get will have all the transactions for a
    given date, and hopefully in the same order each time so that these IDs
    will match up across exports.
    """

    def __init__(self) -> None:
        self.date_count: Dict[datetime, int] = {}

    def create_id(self, date) -> str:
        self.date_count[date] = self.date_count.get(date, 0) + 1
        return f'{datetime.strftime(date, "%Y%m%d")}-{self.date_count[date]}'
