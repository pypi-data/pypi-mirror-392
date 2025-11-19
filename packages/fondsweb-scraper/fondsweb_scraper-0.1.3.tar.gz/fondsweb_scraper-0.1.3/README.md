# fondsweb-scraper

This is a web scraper for ETF data from the Fondsweb website.

[Fondsweb](https://fondsweb.com) is a lesser known german website, that provides information
about funds. Unlike its competitors, it offers the ability to sort funds
by volatility, [Sharpe ratio](https://en.wikipedia.org/wiki/Sharpe_ratio), costs, FWW and ISS ratings, etc.

But apart from an old Perl package 
[Finance::Quote::Fondsweb](https://github.com/finance-quote/finance-quote/blob/master/lib/Finance/Quote/Fondsweb.pm)
there seems to be no other way to access Fondsweb data. 
This Python package is a new implementation that makes accessing the data from Fondsweb easier.  

## Usage

Install the package from PyPi

    $ pip install fondsweb-scraper

To import do 

    >>> from fondsweb import fondsweb as fw

Get information about a single fund by its ISIN

    >>> fw.get_fund("LU1834983477")
    {'name': 'Amundi STOXX Europe 600 Banks UCITS ETF Acc',
    'currency': 'EUR',
    'costs': 0.3,
    'fund_vol': 1520550000.0,
    'per (EUR)': {0: 54.72, 1: 60.55, 3: 42.21, 5: 37.15},
    'vol': {1: 16.1, 3: 19.01, 5: 23.43},
    'sharpe': {1: 3.66, 3: 2.22, 5: 1.49}}

Search for all stock funds sorted by sharpe ratio of the last year 

    >>> response = fw.search_fondsweb(afocus=["Aktienfonds"], sort="Sharpe Ratio 1 Jahr")
    https://www.fondsweb.com/de/suchen/afocus/2-123/sort/sharpe1j

It will print the url used for the search. You can then show the top10 results like

    >>> for entry in response[:10]:
    ...     print(entry["sharpe"], entry["year_1"], entry["isin"], entry["name"])
    ... 
    6.33 39.74 LI0181971842 ASPOMA Japan Opportunities Fund E
    6.31 41.74 LI0393642439 ASPOMA Japan Opportunities Fund A
    5.71 58.19 IE000YYE6WK5 VanEck Defense UCITS ETF USD A
    5.32 71.47 IE000JCW3DZ3 Global X Defence Tech UCITS ETF USD thes.
    4.73 63.91 LU0832413909 ALKEN FUND - European Opportunities US1
    4.69 63.48 LU0866838492 ALKEN FUND - European Opportunities US2
    4.65 63.44 LU0235308136 ALKEN FUND - European Opportunities H
    4.65 63.36 LU0866838575 ALKEN FUND - European Opportunities EU1
    4.63 63.13 LU0432793510 ALKEN FUND - European Opportunities Z
    4.63 63.08 LU0235308482 ALKEN FUND - European Opportunities R

To retrieve time series information about a fund you first need to fetch some config data from the 
Fondsweb website. 

    config = fw.fetch_config()

The `config` object is the needed as parameter to access the time series data. 

    df = fw.get_fund_timeseries("IE00B4L5Y983", config=config)
    print(df)
              date   value
    0   2009-09-25  100.00
    1   2009-09-28  101.24
    2   2009-10-12  102.06
    3   2009-10-26   99.74
    4   2009-11-09  101.60
    ..         ...     ...
    741 2025-10-24  660.64
    742 2025-10-27  666.20
    743 2025-10-28  667.90
    744 2025-10-29  667.39
    745 2025-10-30  665.80

The time series data is returned as a pandas DataFrame.
    
For more examples have a look at the jupyter notebooks in the [notebooks](https://github.com/asmaier/fondsweb/tree/main/notebooks) directory.