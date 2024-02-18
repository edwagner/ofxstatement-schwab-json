import os

from ofxstatement.ui import UI

from ofxstatement_schwab_json.plugin import SchwabJsonPlugin

import logging
LOGGER = logging.getLogger(__name__)

def test_sample() -> None:
    plugin = SchwabJsonPlugin(UI(), {})
    here = os.path.dirname(__file__)
    test_filename = os.path.join(here, "sample-statement.json")

    parser = plugin.get_parser(test_filename)
    statement = parser.parse()

    assert statement is not None
    assert len(statement.invest_lines) == 8

    transfer_line = next(x for x in statement.invest_lines if x.id == "20240212-1")
    assert transfer_line.trntype == "INVBANKTRAN"
    assert transfer_line.trntype_detailed == "XFER"
    
    sell_line = next(x for x in statement.invest_lines if x.id == "20240209-1")
    assert sell_line.trntype == "SELLSTOCK"
    assert sell_line.trntype_detailed == "SELL"
    assert sell_line.units == -1000
    assert sell_line.amount == 1000
    
    interest_line = next(x for x in statement.invest_lines if x.id == "20240116-1")
    assert interest_line.trntype == "INVBANKTRAN"
    assert interest_line.trntype_detailed == "INT"
