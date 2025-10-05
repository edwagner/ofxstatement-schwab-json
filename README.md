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

## Known Limitations

### Splits, Spin-offs

Schwab doesn't provide ratio information for stock splits which is required for
the OFX `<SPLIT>` element.
Nor does GnuCash support importing the OFX `<SPLIT>` element.
So that you at least get some information imported,
these generate `<TRANSFER>` transactions and a warning message to remind you
that you'll likely want to manually update these transactions depending on
how you choose to track splits and their cost basis.

One approach for tracking splits in GnuCash is to change the import transaction
to reverse out the existing lots and their remaining cost bases,
and add back in the new total shares with a corresponding buy cost.

For example, a 4:1 split on 100 shares would be imported as a net 300 share transfer.
Change that transaction to be:
* -100 shares at a sale price of the remaining cost basis
* +400 shares at a buy price of the remaining cost basis

The date won't be correct for calculating the long-term capital gain tax implications,
but at least the per-share gain calculations should be correct.

## Setting up development environment

Use `pipenv` to make a clean development environment.

```
$ cd ofxstatement-schwab-json
$ pipenv sync --dev
```

This will download all the dependencies and install them into your virtual
environment. To enter the development environment:

```
$ pipenv shell
```

Inside the `pipenv` shell:

```
$ ofxstatement list-plugins
The following plugins are available:

  schwab_json      Parses Schwab JSON export of investment transactions
```

Alternatively, single commands can be run inside the `pipenv` environment
directly from the main shell:

```
$ pipenv run ofxstatement list-plugins
```

### Upgrading Dependencies

After running `pipenv shell`, run `pipenv update` to update everything.

### Testing

Run the following command to run the test suite, type checks, and text
formatting (see [Makefile](Makefile) for details):

```
$ pipenv run make all
```

## Packaging

```
$ python -m build
```

## References

* [OFX specification](https://financialdataexchange.org/common/Uploaded%20files/OFX%20files/OFX%20Banking%20Specification%20v2.3.pdf)
* [GnuCash OFX code](https://github.com/Gnucash/gnucash/blob/stable/gnucash/import-export/ofx/gnc-ofx-import.cppx)
* [libofx](https://github.com/libofx/libofx)

## OFX Structure

For easy reference, here is the structure of the most relevant parts of the OFX statement.
This is not complete, but should give you an idea of what gets produced.
The comments point out the corresponding sections in the [OFX specification v2.3](https://financialdataexchange.org/common/Uploaded%20files/OFX%20files/OFX%20Banking%20Specification%20v2.3.pdf).

```xml
<OFX>
  <BANKMSGSRSV1>
    <STMTTRNRS>
      <STMTRS> <!-- 11.4.2.2 -->
        <BANKTRANLIST>
          <STMTTRN> <!-- 11.4.4.1 -->
            <TRNTYPE>CHECK</TRNTYPE> <!-- 11.4.4.3 -->
            <DTPOSTED>20251001</DTPOSTED>
            <TRNAMT>-870.80</TRNAMT>
            <FITID>20251001-1</FITID>
            <CHECKNUM>101</CHECKNUM>
            <MEMO>Check Paid #101</MEMO>
          </STMTTRN>
        </BANKTRANLIST>
      </STMTRS>
    </STMTTRNRS>
  </BANKMSGSRSV1>
  <SECLISTMSGSRSV1>
    <SECLIST> <!-- 13.8.4 -->
      <STOCKINFO>
        <SECINFO> <!-- 13.8.5.1 -->
          <SECID>
            <UNIQUEID>AAPL</UNIQUEID>
            <UNIQUEIDTYPE>TICKER</UNIQUEIDTYPE>
          </SECID>
          <SECNAME>AAPL</SECNAME>
          <TICKER>AAPL</TICKER>
        </SECINFO>
      </STOCKINFO>
    </SECLIST>
  </SECLISTMSGSRSV1>
  <INVSTMTMSGSRSV1>
    <INVSTMTTRNRS> <!-- 13.9.2.1 -->
      <INVSTMTRS> <!-- 13.9.2.2 -->
        <INVTRANLIST>
          <INCOME> <!-- 13.9.2.4.4 -->
            <INCOMETYPE>DIV</INCOMETYPE>
            <INVTRAN> <!-- 13.9.2.4.1 -->
              <FITID>20250815-1</FITID>
              <DTTRADE>20250815</DTTRADE>
              <MEMO>Non-Qualified Div Apple, Inc.</MEMO>
            </INVTRAN>
            <SECID>
              <UNIQUEID>AAPL</UNIQUEID>
              <UNIQUEIDTYPE>TICKER</UNIQUEIDTYPE>
            </SECID>
            <SUBACCTSEC>OTHER</SUBACCTSEC>
            <SUBACCTFUND>OTHER</SUBACCTFUND>
            <TOTAL>100.00</TOTAL>
          </INCOME>
          <SELLSTOCK> <!-- 13.9.2.4.4 -->
            <SELLTYPE>SELL</SELLTYPE>
            <INVSELL> <!-- 13.9.2.4.3 -->
              <INVTRAN>
                <FITID>20250908-1</FITID>
                <DTTRADE>20250908</DTTRADE>
                <MEMO>Sell Apple, Inc.</MEMO>
              </INVTRAN>
              <SECID>
                <UNIQUEID>AAPL</UNIQUEID>
                <UNIQUEIDTYPE>TICKER</UNIQUEIDTYPE>
              </SECID>
              <SUBACCTSEC>OTHER</SUBACCTSEC>
              <SUBACCTFUND>OTHER</SUBACCTFUND>
              <UNITPRICE>257.90000</UNITPRICE>
              <UNITS>-1.00000</UNITS>
              <TOTAL>257.90</TOTAL>
            </INVSELL>
          </SELLSTOCK>
          <INVBANKTRAN> <!-- 13.9.2.3, contents are similar to <BANKTRANLIST> above -->
            <STMTTRN> <!-- 11.4.4.1 -->
              <TRNTYPE>INT</TRNTYPE> <!-- 11.4.4.3 -->
              <DTPOSTED>20250929</DTPOSTED>
              <TRNAMT>0.16</TRNAMT>
              <FITID>20250929-1</FITID>
              <MEMO>Credit Interest SCHWAB1 INT 08/28-09/28</MEMO>
            </STMTTRN>
            <SUBACCTFUND>OTHER</SUBACCTFUND>
          </INVBANKTRAN>
        </INVTRANLIST>
      </INVSTMTRS>
    </INVSTMTTRNRS>
  </INVSTMTMSGSRSV1>
</OFX>
```
