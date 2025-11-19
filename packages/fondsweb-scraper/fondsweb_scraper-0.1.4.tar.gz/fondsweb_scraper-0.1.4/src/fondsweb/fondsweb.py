import datetime
import json
import re

from lxml import html
# see https://stackoverflow.com/questions/49087990/python-request-being-blocked-by-cloudflare
import cloudscraper
from requests.exceptions import JSONDecodeError
import pandas as pd
import numpy as np

from fondsweb import fondsweb_config as config

BASE_URL = "https://www.fondsweb.com/de"
SEARCH_URL = BASE_URL + "/suchen"

BASE_URL_CONFIG = "https://www.fondsweb.com/de/IE00B4L5Y983"

# BASE_URL_TS="https://cf.fww.de/ws/timeseries-jsonp/2.1/ts.js"
# API_KEY="iDnLoTi2H6E7ntCdWNvepFDp4rpRuFyx"
# STH="0cb2483cad65c06565e85508e8c02310f60923c1"
# RANGE="max"
# EUR="1"
TODAY=datetime.datetime.now().strftime("%Y%m%d")

SCRAPER = cloudscraper.create_scraper()

YEARS = [1,3,5,10,15,20]

TRADING_DAYS = 252   # roughly 365 * 5/7 (5 working days per week) - 8 holidays

def fetch_config():
    response = SCRAPER.get(BASE_URL_CONFIG)
    tree = html.fromstring(response.content)
    texts = tree.xpath("//main/script[1]/text()")
    text = texts[0]
    # Remove HTML comments to help json parser
    text = re.sub("(<!--.*?-->)", "", text, flags=re.DOTALL)
    start = text.find("{")
    # Remove trailing comma to help json parser 
    trailing_comma = text.rfind(",")
    text = text[start:trailing_comma] + "}"

    raw_config = json.loads(text)

    if "api_key" not in raw_config:
        raise KeyError("api_key not fetched from fondsweb")
    if "sth" not in raw_config:
        raise KeyError("sth not feteched from fondsweb")
    if "ts" not in raw_config:
        raw_config["ts"] = TODAY

    config = {}
    config["url_ts"] = "https://cf.fww.de/ws/timeseries-jsonp/2.1/ts.js"
    config["api_key"] = raw_config["api_key"]
    config["ts"] = raw_config["ts"]
    config["sth"] = raw_config["sth"]
    config["range"] = "max"
    config["eur"] = "1"

    return config
    

def convert_percent_to_float(text):
    text = text.strip()
    if not text or "n.v." in text:
        return float("nan")
    else:
        return float(text.replace(",",".").strip("%"))

def convert_fundvol_to_float(text):
    factor = 1.0
    if "Mio." in text:
        factor = 1.0e6
        number = text.split("Mio.")[0]
    elif "Mrd." in text:
        factor = 1.0e9
        number = text.split("Mrd.")[0]
    else:
        number = text
    value = float(number.replace(".","").replace(",",".")) * factor
    return value


def create_search_url(afocus=None, rfocus=None, cfocus=None, issuer=None, yields=0, etf=None,
                      sort="PremiumService-Fonds"):

    url = SEARCH_URL

    if afocus:
        afocus_values = []
        for entry in afocus:
            afocus_values.append(config.focus_options["afocus"][entry])
        if afocus_values:
            url += "/afocus/" + ",".join(afocus_values)
    if rfocus:
        rfocus_values = []
        for entry in rfocus:
            rfocus_values.append(config.focus_options["rfocus"][entry])
        if rfocus_values:
            url += "/rfocus/" + ",".join(rfocus_values)
    if cfocus:
        cfocus_values = []
        for entry in cfocus:
            cfocus_values.append(config.focus_options["cfocus"][entry])
        if cfocus_values:
            url += "/cfocus/" + ",".join(cfocus_values)
    if issuer:
        issuer_values = []
        for entry in issuer:
            issuer_values.append(config.focus_options["issuer"][entry])
        if issuer_values:
            url += "/issuer/" + ",".join(issuer_values)
    if etf:
        etf_value = config.etf_options[etf]
        url += f"/etf/{etf_value}"
    if yields:
        yields_value = config.yields_options[yields]
        url += f"/yield/{yields_value}"
    if sort:
        sort_value = config.sort_options[sort]
        url += f"/sort/{sort_value}"

    return url

def parse_response(response):
    tree = html.fromstring(response.content)

    rows = tree.xpath("//div[contains(@class,'f-maxi_container')]/div")

    results = []

    for row in rows:
        name = row.xpath(".//h3/a/text()")[0]
        isin = row.xpath(".//h3/a/@href")[0]

        cells = row.xpath('.//tr/td//text()')

        current_year = convert_percent_to_float(cells[4])
        year_1 = convert_percent_to_float(cells[6])
        year_3 = convert_percent_to_float(cells[8])
        year_5 = convert_percent_to_float(cells[10])
        year_10 = convert_percent_to_float(cells[12])

        costs = float("nan")
        volat = float("nan")
        sharpe = float("nan")

        lines = row.xpath(".//div[contains(@class,'col-lg-5')]//text()")
        for line in lines:
            if "Summe" in line:
                number = line.split(":")[1].strip()
                costs = convert_percent_to_float(number)
            if "Volatilität" in line:
                number = line.split(":")[1].strip()
                volat = convert_percent_to_float(number)
            if "Sharpe" in line:
                number = line.split(":")[1].strip()
                sharpe = convert_percent_to_float(number)

        entry = {"name": name, "isin": isin, "current_year": current_year,
                 "year_1": year_1, "year_3": year_3, "year_5": year_5, "year_10": year_10,
                 "costs": costs, "volat": volat, "sharpe": sharpe}

        results.append(entry)

    return results


def search_fondsweb(afocus=None, rfocus=None, cfocus=None, issuer=None, yields=None, etf=None, sort=None):

    url = create_search_url(afocus, rfocus, cfocus, issuer, yields, etf, sort)

    print(url)

    response = SCRAPER.get(url)

    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}")
    else:
        results = parse_response(response)

    return results


def get_fund_timeseries(isin, config=None, end_date=None):
    if not config:
        print("Error: No config provided!")
        return pd.DataFrame()
    if not end_date:
        end_date = config["ts"]
    URL=f"{config['url_ts']}?API_KEY={config['api_key']}&TS={end_date}&STH={config['sth']}&ID={isin}&RANGE={config['range']}&EUR={config['eur']}"
    response = SCRAPER.get(URL)
    try:
        data = response.json()
        df = pd.DataFrame(data[0]["ts"],columns=["date", "value"])
        df['date'] = pd.to_datetime(df['date'])
        return df
    except (IndexError, KeyError, JSONDecodeError) as e:
        print(f"Error for {isin}: {e}")
        print(response)
        return pd.DataFrame()


def get_fund_between(df, start_date=None, end_date=None):
    if not start_date and not end_date:
        return df
    if start_date and end_date:
        return df[(df["date"].between(start_date, end_date))]
    if not end_date:
        return df[df["date"] >= start_date]
    if not start_date:
        return df[df["date"] <= end_date]      


def get_fund_performance(df, start_date, end_date=None):
    try:
        df_filtered = get_fund_between(df, start_date, end_date)
        perf = 100*(df_filtered['value'].iloc[-1] - df_filtered['value'].iloc[0])/df_filtered['value'].iloc[0]
        return float(perf)
    except (IndexError, KeyError) as e:
        print(e)
        print(df)
        return float("nan")
   
    
def get_fund_volatility(df, start_date, end_date=None, log=True):
    try:
        df_filtered = get_fund_between(df, start_date, end_date)
        df_returns = df_filtered['value'].pct_change()
        if log:
            # see https://stackoverflow.com/questions/31287552/logarithmic-returns-in-pandas-dataframe
            df_returns = np.log1p(df_returns)
        return float(np.sqrt(TRADING_DAYS) * df_returns.std())
    except (IndexError, KeyError) as e:
        print(e)
        print(df)
        return float("nan")


def parse_fund(response, debug=False):

    tree = html.fromstring(response.content)
    name = tree.xpath("//h1/text()")[0]

    tables = pd.read_html(response.content, decimal=",", thousands=None)

    if debug:
        return tables

    currency = tables[0]["Währung"][0]
    costs = convert_percent_to_float(tables[0]["Sum. lfd. Kosten"][0])
    fund_vol = convert_fundvol_to_float(tables[-3].loc[3][1])

    column = [col for col in tables[-6].columns if 'Fonds' in col and 'EUR' in col][0]

    per = {}
    value = tables[-6].iloc[0][column]
    per_current = convert_percent_to_float(value)
    per[0] = per_current

    values = list(tables[-5].iloc[1:][column])
    per |= {YEARS[i]: convert_percent_to_float(txt) for i, txt in enumerate(values)}

    values = list(tables[-2].iloc[:-2, 1])
    vol = {YEARS[i]: convert_percent_to_float(txt) for i, txt in enumerate(values)}

    values = list(tables[-1].iloc[:-1, 1])
    sharpe = {YEARS[i]: float(txt) for i, txt in enumerate(values)}

    return {"name": name, "currency": currency, "costs": costs, "fund_vol": fund_vol,
            "per (EUR)": per,
            "vol": vol,
            "sharpe": sharpe}


def get_fund(isin, debug=False):
    url = BASE_URL + "/" + isin

    response = SCRAPER.get(url)

    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}")
    else:
        return parse_fund(response, debug)

