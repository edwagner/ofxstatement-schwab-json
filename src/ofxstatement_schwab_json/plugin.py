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
        match = re.search(r'(.*)_Transactions_.*\.json', path.basename(filename))
        if match:
            self.statement.account_id = match[1]
        self.id_generator = IdGenerator()

    def parse(self) -> Statement:
        """Main entry point for parsers"""
        with open(self.filename, "r") as f:
            # Reverse the lines so that they are in chronological order
            self.import_lines(reversed(json.load(f)['BrokerageTransactions']))
            return self.statement

    def import_lines(self, transactions):
        for tran in transactions:
            date = datetime.strptime(tran["Date"][0:10], '%m/%d/%Y')
            id = self.id_generator.create_id(date)
            line = InvestStatementLine(
                id=id,
                date=date,
                memo=f'{tran["Action"]} {tran["Description"]}')
            if len(tran["Amount"]) > 0:
                line.amount = Decimal(re.sub("[$,]","",tran["Amount"]))

            action = tran["Action"]
            if action == "Sell":
                line.trntype = "SELLSTOCK"
                line.trntype_detailed = "SELL"
                line.security_id=tran["Symbol"]
                line.units = Decimal("-" + re.sub("[,-]","",tran["Quantity"])) # Ensure a negative number
                line.unit_price = Decimal(re.sub("[$,]","",tran["Price"]))
                if len(tran["Fees & Comm"]) > 0:
                    line.fees = Decimal(re.sub("[$,]","",tran["Fees & Comm"]))
            elif (action == "Cash Dividend"
                  or action == "Qualified Dividend"
                  or action == "Non-Qualified Div"
                  or action == "Pr Yr Non Qual Div"
                  or action == "Pr Yr Non-Qual Div"
                  or action == "Qual Div Reinvest"
                  or action == "Reinvest Dividend"):
                line.trntype = "INCOME"
                line.trntype_detailed = "DIV"
                line.security_id=tran["Symbol"]
            elif action == "Long Term Cap Gain":
                line.trntype = "INCOME"
                line.trntype_detailed = "CGLONG"
                line.security_id=tran["Symbol"]
            elif action == "Short Term Cap Gain":
                line.trntype = "INCOME"
                line.trntype_detailed = "CGSHORT"
                line.security_id=tran["Symbol"]
            elif action == "Bank Interest" and len(tran["Symbol"]) > 0:
                line.trntype = "INCOME"
                line.trntype_detailed = "INTEREST"
                line.security_id=tran["Symbol"]
            elif action == "Buy" or action == "Reinvest Shares":
                line.trntype = "BUYSTOCK"
                line.trntype_detailed = "BUY"
                line.security_id=tran["Symbol"]
                line.units = Decimal(re.sub("[,]","",tran["Quantity"]))
                line.unit_price = Decimal(re.sub("[$,]","",tran["Price"]))
                if len(tran["Fees & Comm"]) > 0:
                    line.fees = Decimal(re.sub("[$,]","",tran["Fees & Comm"]))
            elif len(tran["Symbol"]) > 0 and (action == "Journaled Shares" or action == "Spin-off"):
                line.trntype = "TRANSFER"
                line.security_id=tran["Symbol"]
                line.units = Decimal(re.sub("[,]","",tran["Quantity"]))
                if len(tran["Price"]) > 0:
                    line.unit_price = Decimal(re.sub("[$,]","",tran["Price"]))
                else:
                    line.unit_price = Decimal(0)
                if line.amount is None:
                    line.amount = Decimal(0)
                if action == "Spin-off":
                    LOGGER.warning(f'You will probably want to allocate some cost basis for the {line.security_id} spin-off.')
            elif len(tran["Symbol"]) == 0 or action == "Cash In Lieu":
                line.trntype = "INVBANKTRAN"
                if (action == "Bank Interest"
                        or action == "Bond Interest"
                        or action == "Credit Interest"):
                    line.trntype_detailed = "INT"
                elif (action == "MoneyLink Transfer"
                      or action == "Internal Transfer"
                      or action == "Journal"
                      or action == "Journaled Shares"):
                    line.trntype_detailed = "XFER"
                elif action == "Wire Sent":
                    line.trntype_detailed = "DEBIT"
                elif action == "Service Fee":
                    line.trntype_detailed = "SRVCHG"
                elif action == "Misc Cash Entry":
                    line.trntype_detailed = "OTHER"
                elif action == "Cash In Lieu":
                    line.trntype_detailed = "CREDIT"
                else:
                    raise Exception(f'Unrecognized bank action: "{action}"')
            else:
                raise Exception(f'Unrecognized action: "{action}"')
            line.assert_valid()
            self.statement.invest_lines.append(line)

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
