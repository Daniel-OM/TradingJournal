from random import randint
import time
import datetime as dt
import numpy as np
import pandas as pd
# import requests
from curl_cffi import requests, BrowserTypeLiteral, CurlHttpVersion

timeframes: list[str] = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd", "max"]

class YahooBase:

    base_url: str = 'https://query1.finance.yahoo.com'

    headers: dict[str, str] = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8,es-ES;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Cookie': 'A1=d=AQABBDtm1WYCEFys__46DFFzlPqGPNYPx9EFEgABCAHegGetZ-S2b2UBAiAAAAcInXrRZskjzuQ&S=AQAAAh5MvLzwu_PDCuOIGDVnUjk;',
        'Host': base_url.split('//')[-1],
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-crumb': 'e4rJKMRoY0B',
    }

    def __init__(self, verify:bool=True, impersonate:BrowserTypeLiteral='chrome', wait:bool=True, verbose:bool=False) -> None:
        self.verify: bool = verify
        self.impersonate:BrowserTypeLiteral = impersonate
        self.wait: bool = wait
        self.verbose: bool = verbose
        self._last_time = None
        self.session = requests.Session()
        self.getCrumb(init=False)

    def _get(self, url:str, params:dict[str, str]=None, headers:dict[str, str]=None) -> requests.Response:
        if self.wait:
            wait = randint(5, 20)/10 - (dt.datetime.now() - self._last_time).total_seconds() if self._last_time is not None else 0
            if self.verbose: print('Waiting GET: ', wait)
            if wait > 0: time.sleep(wait)
            
        self.r: requests.Response = self.session.get(url=url, params=params, headers=headers, http_version=CurlHttpVersion.V1_1, timeout=300, impersonate=self.impersonate, verify=self.verify)
        self._last_time: dt.datetime = dt.datetime.now()
        return self.r
    
    def _post(self, url:str, params:dict[str, str]=None, data:dict[str, str]=None, headers:dict[str, str]=None) -> requests.Response:
        if self.wait:
            wait = randint(5, 20)/10 - (dt.datetime.now() - self._last_time).total_seconds() if self._last_time is not None else 0
            if self.verbose: print('Waiting POST: ', wait)
            if wait > 0: time.sleep(wait)
            
        self.r: requests.Response = requests.post(url=url, params=params, json=data, headers=headers, http_version=CurlHttpVersion.V1_1, timeout=300, impersonate=self.impersonate, verify=self.verify)
        self._last_time: dt.datetime = dt.datetime.now()
        return self.r

    def getCrumb(self, init:bool=False) -> str:

        if init:
            url = 'https://query2.finance.yahoo.com/v1/test/getcrumb'
            headers: dict[str, str] = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'en-US,en;q=0.9,es;q=0.8,es-ES;q=0.7',
                'Content-Type': 'text/plain',
                'Cookie': 'dflow=210; GUC=AQABCAFn5ZBoFEIhcgSk&s=AQAAAEagaMWl&g=Z-RGdg; A1=d=AQABBKuyRGACEHbfmOBdBeCkRMrYGIFxTsYFEgABCAGQ5WcUaOTo7L8AAiAAAAcIq7JEYIFxTsY&S=AQAAAge6ioa3POgOxm8OdvEsvpI; A3=d=AQABBKuyRGACEHbfmOBdBeCkRMrYGIFxTsYFEgABCAGQ5WcUaOTo7L8AAiAAAAcIq7JEYIFxTsY&S=AQAAAge6ioa3POgOxm8OdvEsvpI; A1S=d=AQABBKuyRGACEHbfmOBdBeCkRMrYGIFxTsYFEgABCAGQ5WcUaOTo7L8AAiAAAAcIq7JEYIFxTsY&S=AQAAAge6ioa3POgOxm8OdvEsvpI; EuConsent=CQFwyQAQFwyQAAOACKESBJFgAAAAAAAAACiQAAAAAAAA; cmp=t=1743703482&j=1&u=1---&v=74; PRF=t%3DRYCEY%252BRR.L%252BRRU.HM%252BRRU.DU%252B500.PA%252BTSLA%252BSPY%252BRLLCF%252BRYCEF%252BIXP%252BWOOD%252BSLVP%252BPICK%252BILIT%252BRING%26qct-neo%3Dcandle%26qke-neo%3Dfalse%26theme%3Dauto',
                'origin': 'https://es.finance.yahoo.com',
                'priority': 'u=1, i',
                'referer': f'https://es.finance.yahoo.com',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Google Chrome";v="134", "Chromium";v="134", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }
            r: requests.Response = self._get(url=url, headers=headers)
            self.headers['x-crumb'] = r.text
            return r.text
        else:
            return self.headers['x-crumb']

class YahooFinance(YahooBase):

    base_url: str = 'https://query1.finance.yahoo.com'
    headers: dict[str, str] = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Cookie': 'dflow=810; A1=d=AQABBKsOemgCEJBzssV3jVnb5VzSOWffCa8FEgABCAFUe2ipaOTy7L8AAiAAAAcIqA56aHi_6WY&S=AQAAAtjvN91_FsfuyrYGHk8Oodw; EuConsent=CQUv5EAQUv5EAAOACKESBzFgAAAAAAAAACiQAAAAAAAA; A1S=d=AQABBKsOemgCEJBzssV3jVnb5VzSOWffCa8FEgABCAFUe2ipaOTy7L8AAiAAAAcIqA56aHi_6WY&S=AQAAAtjvN91_FsfuyrYGHk8Oodw; GUC=AQABCAFoe1RoqUIf1QRh&s=AQAAALUoiRx2&g=aHoOtQ; A3=d=AQABBKsOemgCEJBzssV3jVnb5VzSOWffCa8FEgABCAFUe2ipaOTy7L8AAiAAAAcIqA56aHi_6WY&S=AQAAAtjvN91_FsfuyrYGHk8Oodw; PRF=t%3DGETR; cmp=t=1752840502&j=1&u=1---&v=89',
        'Host': 'query1.finance.yahoo.com',
        'Origin': 'https://finance.yahoo.com',
        'Pragma': 'no-cache',
        'Referer': 'https://finance.yahoo.com/research-hub/screener/day_gainers/?start=0&count=25',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-crumb': 'e4rJKMRoY0B',
    }
        
    def getMarketTime(self) -> dict:

        url: str = f'{self.base_url}/v6/finance/markettime'
        params: dict[str, str] = {
            'formatted': 'true',
            'key': 'finance',
            'lang': 'en-US',
            'region': 'US'
        }
        headers: dict[str, str] = self.headers
        r: requests.Response = self._get(url=url, params=params, headers=headers)
        data = r.json()

        return {
            'open': data['finance']['marketTimes'][0]['marketTime'][0]['open'],
            'close': data['finance']['marketTimes'][0]['marketTime'][0]['close'],
            'current': data['finance']['marketTimes'][0]['marketTime'][0]['time'],
            'timezone': data['finance']['marketTimes'][0]['marketTime'][0]['timezone'][0]['$text'],
        }

    def _generateScreenerOperator(self, key:str, val:int|float|str=None, min:int|float=None, max:int|float=None) -> dict:

        if min is not None and max is not None:
            return {
                "operator":"btwn",
                "operands":[key,min,max]
            }
        elif min is not None:
            return {
                "operator":"gt",
                "operands":[key,min]
            }
        elif max is not None:
            return {
                "operator":"lt",
                "operands":[key,max]
            }
        elif val is not None:
            return {
                "operator":"eq",
                "operands":[key,val]
            }

    def getScreener(self, min_price:float=0.01, max_price:float=10, 
                    min_avg_volume:int=100000, 
                    min_market_cap:int=None, max_market_cap:int=None, 
                    min_change:float=3, max_change:float=None,
                    gainers:bool=True, limit:int=100, df:bool=True) -> list | pd.DataFrame:
        '''
        To get screener columns: https://query1.finance.yahoo.com/ws/screeners/v1/finance/screener/instrument/equity/columns?formatted=true&lang=en-US&region=US

        Different type of operators available:       
        {
            "operator":"btwn",
            "operands":["intradayprice",0,5]
        },
        {
            "operator":"gt",
            "operands":["intradayprice",0.01]
        },
        {
            "operator":"lt",
            "operands":["intradayprice",10]
        },
        {
            "operator":"eq",
            "operands":["intradayprice",10]
        }
        '''
        url = f"{self.base_url}/v1/finance/screener"
        params: dict = {
            'formatted': True,
            'useRecordsResponse': True,
            'lang': 'en-US',
            'region': 'US',
            'crumb': 'e4rJKMRoY0B'#self.headers['x-crumb']
        }
        data: dict = {
            "size":limit,
            "offset":0,
            "sortType":"DESC",
            "sortField":"percentchange",
            "quoteType":"EQUITY",
            "includeFields": [
                "ticker",
                "companyshortname",
                "intradayprice",
                "intradaypricechange",
                "percentchange",
                "fiftytwowkpercentchange",
                "dayvolume",
                "avgdailyvol3m",
                "totalsharesoutstanding",
                "intradaymarketcap",
                # "peratio.lasttwelvemonths",
                "short_percentage_of_shares_outstanding.value",
                "short_percentage_of_float.value",
                "peratio.lasttwelvemonths",
                "day_open_price",
                "fiftytwowklow",
                "fiftytwowkhigh",
                "short_percentage_of_float.value",
                "years_of_consecutive_positive_eps",
                "indices",
                "region"
            ],
            "topOperator":"AND",
            "query":{
                "operator":"and",
                "operands":[
                    {
                        "operator":"or",
                        "operands":[
                            "region", "us"
                        ]
                    },
                    {
                        "operator":"or",
                        "operands":[
                            self._generateScreenerOperator(key='exchange', val='NYQ'),
                            self._generateScreenerOperator(key='exchange', val='NMW'),
                            self._generateScreenerOperator(key='exchange', val='NAS'),
                        ]
                    },{
                        "operator":"or",
                        "operands":[
                            self._generateScreenerOperator(key='intradaymarketcap', min=1000000000),
                        ]
                    },{
                        "operator":"or",
                        "operands":[
                            self._generateScreenerOperator(key='intradayprice', min=0.01, max=10),
                        ]
                    },{
                        "operator":"or",
                        "operands":[
                            self._generateScreenerOperator(key='avgdailyvol3m', min=100000),
                        ]
                    },{
                        "operator":"or",
                        "operands":[
                            self._generateScreenerOperator(key='dayvolume', min=100000),
                        ]
                    },
                    {
                        "operator":"or",
                        "operands":[
                            self._generateScreenerOperator(key='percentchange', min=min_change, max=max_change),
                        ]
                    }
                ]
            },
        }
        headers: dict[str, str] = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'es-ES,es;q=0.9,en;q=0.8',
            'content-length': len(str(data)),
            'content-type': 'application/json',
            'cookie': 'dflow=810; A1=d=AQABBKsOemgCEJBzssV3jVnb5VzSOWffCa8FEgABCAFUe2ipaOTy7L8AAiAAAAcIqA56aHi_6WY&S=AQAAAtjvN91_FsfuyrYGHk8Oodw; EuConsent=CQUv5EAQUv5EAAOACKESBzFgAAAAAAAAACiQAAAAAAAA; A1S=d=AQABBKsOemgCEJBzssV3jVnb5VzSOWffCa8FEgABCAFUe2ipaOTy7L8AAiAAAAcIqA56aHi_6WY&S=AQAAAtjvN91_FsfuyrYGHk8Oodw; GUC=AQABCAFoe1RoqUIf1QRh&s=AQAAALUoiRx2&g=aHoOtQ; A3=d=AQABBKsOemgCEJBzssV3jVnb5VzSOWffCa8FEgABCAFUe2ipaOTy7L8AAiAAAAcIqA56aHi_6WY&S=AQAAAtjvN91_FsfuyrYGHk8Oodw; PRF=t%3DGETR; cmp=t=1752840502&j=1&u=1---&v=89',
            'origin': 'https://finance.yahoo.com',
            'priority': 'u=1, i',
            'referer': 'https://finance.yahoo.com/research-hub/screener/most_active_penny_stocks/?start=0&count=25',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'x-crumb': 'Ce9NsrXTAnw'
        }
        print(data)
        r: requests.Response = self._post(url=url, params=params, data=data, headers=headers)
        temp = [{**{ 
                'ticker': v['ticker'],
                'name': v['companyName'],
                'price': v['regularMarketPrice']['raw'],
                'change': v['regularMarketChange']['raw'],
                'change_pct': v['regularMarketChangePercent']['raw'],
                'avg_vol': v['avgDailyVol3m']['raw'],
                'volume': v['regularMarketVolume']['raw'],
                'float': v.get('totalSharesOutstanding', {}).get('raw', 0) * v.get('shortPercentageOfSharesOutstanding', {}).get('raw', 0) / v.get('shortPercentageOfFloat', {}).get('raw', 0) if 'shortPercentageOfFloat' in v else None,
                'outstanding': v['totalSharesOutstanding']['raw'],
                'market_cap': v['marketCap']['raw'],
                'ytd_high': v['fiftyTwoWeekHigh']['raw'],
                'ytd_low': v['fiftyTwoWeekLow']['raw'],
            }, **{key: (val['raw'] if isinstance(val, dict) else val) for key, val in v if key not in ['ticker', 'companyName', 'regularMarketPrice', 'regularMarketChange', 'regularMarketChangePercent', 'avgDailyVol3m',
                                                            'regularMarketVolume', 'totalSharesOutstanding', 'marketCap', 'fiftyTwoWeekHigh', 'fiftyTwoWeekLow']}}
            for v in r.json()['finance']['result'][0]['records']]
        
        if df:
            return pd.DataFrame(data=temp)
        else:
            return temp

    def search(self, text:str) -> dict:
        url: str = f'{self.base_url}/v1/finance/search'
        params: dict = {
            'q': text,
            'quotesCount': 10,
            'newsCoount': 5,
            'listsCount': 2,
            'enableFuzzyQuery': False,
            'quotesQueryId': 'tss_match_phrase_query',
            'multiQuoteQueryId': 'multi_quote_single_token_query',
            'newsQueryId': 'news_cie_vespa',
            'enableCb': True,
            'enableNavLinks': True,
            'enableEnhancedTrivialQuery': True,
            'enableResearchReports': True,
            'enableCulturalAssets': True,
            'enableLogoUrl': True,
            'enableLists': False,
            'recommendCount': '5',
            'lang': 'en-US',
            'region': 'US'
        }
        headers: dict[str, str] = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8,es-ES;q=0.7',
            'cache-control': 'no-cache',
            'connection': 'keep-alive',
            'Cookie': 'A1=d=AQABBDtm1WYCEFys__46DFFzlPqGPNYPx9EFEgABCAHegGetZ-S2b2UBAiAAAAcInXrRZskjzuQ&S=AQAAAh5MvLzwu_PDCuOIGDVnUjk;',
            'Host': self.base_url.split('//')[-1],
            'origin': 'https://es.finance.yahoo.com',
            'pragma': 'no-cache',
            'referer': f'https://es.finance.yahoo.com/research-hub/screener/day_gainers',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        r: requests.Response = self._get(url=url, params=params, headers=headers)
        return r.json()

    def getCalendar(self, tickers:list[str]) -> dict:
        url: str = f'{self.base_url}/ws/screeners/v1/finance/calendar-events'
        params: dict[str, str] = {
            'countPerDay': '100',
            'economicEventsHighImportanceOnly': 'true',
            'economicEventsRegionFilter': '',
            'modules': 'earnings',
            'startDate': '1747000800000',
            'endDate': '1748296799999',
            'tickersFilter': ','.join(tickers),
            'lang': 'en-US',
            'region': 'US'
        }
        headers: dict[str, str] = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'dflow=627; PRF=t%3DAAPL%252BXLK%252BSPY%252B500.PA%252BRRU.DU%26theme%3Dauto%26su-oo%3Dtrue%26dock-collapsed%3Dtrue; GUC=AQABCAFoI0ZoS0IZ3wPq&s=AQAAAOEyJ2la&g=aCH-ng; A1=d=AQABBFOTkGcCEDNLPt4eAn0stcNEiUDDjRkFEgABCAFGI2hLaOTo7L8AAiAAAAcIU5OQZ0DDjRk&S=AQAAAtp_iUhvfQ5xsxvZktepZpU; A1S=d=AQABBFOTkGcCEDNLPt4eAn0stcNEiUDDjRkFEgABCAFGI2hLaOTo7L8AAiAAAAcIU5OQZ0DDjRk&S=AQAAAtp_iUhvfQ5xsxvZktepZpU; A3=d=AQABBFOTkGcCEDNLPt4eAn0stcNEiUDDjRkFEgABCAFGI2hLaOTo7L8AAiAAAAcIU5OQZ0DDjRk&S=AQAAAtp_iUhvfQ5xsxvZktepZpU; _yb=MgE0ATEBLTEBMTY3MDMxNzk4Mw==; cmp=t=1747637215&j=1&u=1---&v=80; EuConsent=CQRTEQAQRTEQAAOACKESBpFgAAAAAAAAACiQAAAAAAAA',
            'Host': 'query1.finance.yahoo.com',
            'Origin': 'https://es.finance.yahoo.com',
            'Pragma': 'no-cache',
            'Referer': 'https://es.finance.yahoo.com/quote/AAPL/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
        }
        
        r: requests.Response = self._get(url=url, params=params, headers=headers)
        data = r.json()

        return data['finance']['result']['earnings']
    
class YahooTicker(YahooBase):

    base_url: str = 'https://query1.finance.yahoo.com'
    profile: dict = {}
    prices: dict = {}
    news: list|pd.DataFrame = []
    press_releases: list|pd.DataFrame = []
    sec_reports: list|pd.DataFrame = []

    headers: dict[str, str] = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8,es-ES;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Cookie': 'A1=d=AQABBDtm1WYCEFys__46DFFzlPqGPNYPx9EFEgABCAHegGetZ-S2b2UBAiAAAAcInXrRZskjzuQ&S=AQAAAh5MvLzwu_PDCuOIGDVnUjk;',
        'Host': base_url.split('//')[-1],
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-crumb': 'e4rJKMRoY0B',
    }

    def __init__(self, ticker:str, verify:bool=True, impersonate:str='chrome', wait:bool=True, verbose:bool=False):
        super().__init__(verify, impersonate, wait, verbose)
        self.ticker: str = ticker

    def quoteType(self) -> dict:
        url: str = f'{self.base_url}/v1/finance/quoteType/'
        params: dict[str, str] = {
            'symbol': self.ticker,
            'lang': 'en-US',
            'region': 'US'
        }
        headers: dict[str, str] = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8,es-ES;q=0.7',
            'Cookie': 'A1=d=AQABBDtm1WYCEFys__46DFFzlPqGPNYPx9EFEgABCAHegGetZ-S2b2UBAiAAAAcInXrRZskjzuQ&S=AQAAAh5MvLzwu_PDCuOIGDVnUjk;',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        r: requests.Response = self._get(url=url, params=params, headers=headers)
        data = r.json()['quoteType']['result']
        
        return data[0] if data else {}

    def getTicker(self, formatted:bool=True) -> dict:
        
        url: str = f'{self.base_url}/v10/finance/quoteSummary/{self.ticker}'
        params: dict = {
            'formatted': True,
            'modules': 'assetProfile,secFilings',
            'lang': 'en-US',
            'region': 'US',
            'crumb': 'e4rJKMRoY0B'
        }
        headers: dict[str, str] = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8,es-ES;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': 'A1=d=AQABBDtm1WYCEFys__46DFFzlPqGPNYPx9EFEgABCAHegGetZ-S2b2UBAiAAAAcInXrRZskjzuQ&S=AQAAAh5MvLzwu_PDCuOIGDVnUjk;',
            'Host': self.base_url.split('//')[-1],
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-crumb': self.getCrumb(),
        }
        r: requests.Response = self._get(url=url, params=params, headers=headers)
        data = r.json()
        profile = {}
        if data['quoteSummary']['result']:
            if 'assetProfile' not in data['quoteSummary']['result'][0]:
                return {}
            profile: dict = data['quoteSummary']['result'][0]['assetProfile']
            profile['secFilings'] = data['quoteSummary']['result'][0]['secFilings']['filings'] if 'secFilings' in data['quoteSummary']['result'][0] else []

            profile = {''.join(['_' + l.lower() if l.isupper() else l for l in k]): v for k, v in profile.items()}
            if 'compensation_as_of_epoch_date' in profile: profile['compensation_as_of_epoch_date'] = dt.datetime.fromtimestamp(profile['compensation_as_of_epoch_date'])
            if 'governance_epoch_date' in profile: profile['governance_epoch_date'] = dt.datetime.fromtimestamp(profile['governance_epoch_date'])
            if not formatted:
                profile['compensation_as_of_epoch_date'] = profile['compensation_as_of_epoch_date'].strftime('%Y-%m-%d %H:%M:%S')
                profile['governance_epoch_date'] = profile['governance_epoch_date'].strftime('%Y-%m-%d %H:%M:%S')
            profile['company_officers'] = [{'name': o.get('name', None), 
                                            'title': o.get('title', None), 
                                            'age':o.get('age', None), 
                                            'exercised_value': o.get('exercisedValue', {}).get('raw', None), 
                                            'year': o.get('fiscalYear', None), 
                                            'pay': o.get('totalPay', {}).get('raw', None), 
                                            'unexercised_value': o.get('unexercisedValue', {}).get('raw', None), 
                                            'birth': o.get('yearBorn', None)} for o in profile['company_officers']]
            profile['sec_filings'] = [{'date': f['date'], 'epoch_date': f['epochDate'], 'title': f['title'], 'type': f['type'], 'url': f['edgarUrl']} for f in profile['sec_filings']]

        # profile = {**profile, **self.quoteType(), **self.quote()}
        
        self.profile: dict = profile

        return profile

    def getProfile(self, formatted:bool=True) -> dict:
        
        quote = self.quote()
        quote_type = self.quoteType()
        info = self.getTicker(formatted=formatted)
        if len(info.keys()) <= 0:
            if len(quote.keys()) > 0:
                response = YahooFinance(verify=self.verify, impersonate=self.impersonate, wait=self.wait).search(text=quote['longName'])
                if 'quotes' in response:
                    temp = self.ticker
                    self.ticker = response['quotes'][0]['symbol']
                    info = self.getTicker()
                    self.ticker = temp

        return {**info, **quote, **quote_type}
                
    def dateToTimestamp(self, date:str|dt.datetime) -> float:
        return date.timestamp() if isinstance(date, dt.datetime) else dt.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timestamp()

    def getPrice(self, start:dt.datetime, end:dt.datetime, timeframe:str='1m', df:bool=True) -> list | pd.DataFrame:
        
        url: str = f'{self.base_url}/v8/finance/chart/{self.ticker}'
        params: dict = {
            'period1': str(int(start)),
            'period2': str(int(end)),
            'interval': timeframe,
            'includePrePost': True,
            'events': 'div|split|earn',
            'lang': 'en-US',
            'region': 'US'
        }
        headers: dict[str, str] = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8,es-ES;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': 'A1=d=AQABBDtm1WYCEFys__46DFFzlPqGPNYPx9EFEgABCAHegGetZ-S2b2UBAiAAAAcInXrRZskjzuQ&S=AQAAAh5MvLzwu_PDCuOIGDVnUjk;',
            'Host': self.base_url.split('//')[-1],
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-crumb': self.getCrumb(),
        }
        r: requests.Response = self._get(url=url, params=params, headers=headers)
        data = r.json()
        if data['chart']['result'] and 'timestamp' in data['chart']['result'][0]:
            tz = data['chart']['result'][0]['meta']['exchangeTimezoneName']
            sessions = data['chart']['result'][0]['meta']['currentTradingPeriod']
            prices = pd.DataFrame(data=data['chart']['result'][0]['indicators']['quote'][0], 
                                index=data['chart']['result'][0]['timestamp'])
            prices.index = pd.to_datetime(prices.index, unit='s')
            prices.index = prices.index.tz_localize(tz).tz_convert('UTC')
            prices['session'] = np.where(prices.index.time < dt.datetime.fromtimestamp(sessions['regular']['start']).time(), 'PRE', 
                                np.where(dt.datetime.fromtimestamp(sessions['regular']['end']).time() < prices.index.time, 'POST', 'REG'))
            if not df: prices.index = prices.index.strftime('%Y-%m-%d %H:%M:%S')
            prices['date'] = prices.index
            prices.dropna(axis=0, inplace=True)
            self.prices[timeframe] = prices if df else prices.to_dict(orient='records')
        else:
            prices = pd.DataFrame()

        return prices if df else prices.to_dict(orient='records')

    def getNews(self, limit:int=20, df:bool=True) -> list|pd.DataFrame:

        url = f'https://finance.yahoo.com/xhr/ncp?location=US&queryRef=newsAll&serviceKey=ncp_fin&listName={self.ticker}-news&lang=en-US&region=US'
        params: dict = {
            'location': 'US', 
            'queryRef': 'newsAll',
            'serviceKey': 'ncp_fin',
            'listName': f'{self.ticker}-news', 
            'lang': 'en-US', 
            'region': 'US'
        }
        headers: dict[str, str] = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Length': '3862',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Cookie': 'A1=d=AQABBDtm1WYCEFys__46DFFzlPqGPNYPx9EFEgABCAHegGetZ-S2b2UBAiAAAAcInXrRZskjzuQ&S=AQAAAh5MvLzwu_PDCuOIGDVnUjk;',
            'Host': 'finance.yahoo.com',
            'Origin': 'https://finance.yahoo.com',
            'Pragma': 'no-cache',
            'Referer': f'https://finance.yahoo.com/quote/{self.ticker}/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-crumb': self.getCrumb(),
        }
        data: dict = {
            "serviceConfig":{
                "count":250,
                "imageTags":["168x126|1|80","168x126|2|80"],
                "thumbnailSizes":["170x128"],
                "spaceId":"95993639",
                "snippetCount":limit,
                "s":[self.ticker]
            },
            "session":{
                "consent":{
                    "allowContentPersonalization":False,
                    "allowCrossDeviceMapping":False,
                    "allowFirstPartyAds":False,
                    "allowSellPersonalInfo":True,
                    "canEmbedThirdPartyContent":False,
                    "canSell":True,
                    "consentedVendors":[],
                    "allowAds":True,
                    "allowOnlyLimitedAds":True,
                    "rejectedAllConsent":True,
                    "allowOnlyNonPersonalizedAds":False
                },
                "authed":"0",
                "ynet":"0",
                "ssl":"1",
                "spdy":"0",
                "ytee":"0",
                "mode":"normal",
                "tpConsent":False,
                "site":"finance",
                "adblock":"0",
                "bucket":["yf-csn-on","newslatestnativead-test","yf-advchart-nimbus"],
                "colo":"ir2",
                "device":"desktop",
                "bot":"0",
                "browser":"chrome",
                "app":"unknown",
                "ecma":"modern",
                "environment":"prod",
                "gdpr":True,
                "lang":"en-US",
                "dir":"ltr",
                "intl":"us",
                "network":"broadband",
                "os":"windows nt",
                "partner":"none",
                "region":"US",
                "time":int(dt.datetime.now().timestamp()*1000),
                "tz":"Europe/Madrid",
                "usercountry":"ES",
                "rmp":"0",
                "webview":"0",
                "feature":["disableServiceRewrite","disableBack2Classic","disableYPFTaxArticleDisclosure","enableAdRefresh20s","enableAnalystRatings","enableAPIRedisCaching","enableChartbeat","enableChatSupport","enableCompare","enableCompareConvertCurrency","enableConsentAndGTM","enableCrumbRefresh","enableCSN","enableCurrencyConverter","enableDockAddToFollowing","enableDockCondensedHeader","enableDockNeoOptoutLink","enableDockPortfolioControl","enableExperimentalDockModules","enableLazyQSP","enableLiveBlogStatus","enableLivePage","enableMarketsLeafHeatMap","enableMultiQuote","enableNeoAdvancedChart","enableNeoArticle","enableNeoAuthor","enableNeoBasicPFs","enableNeoGreen","enableNeoHouseCalcPage","enableNeoInvestmentIdea","enableNeoMortgageCalcPage","enableNeoOptOut","enableNeoPortfolioDetail","enableNeoQSPReportsLeaf","enableNeoResearchReport","enableNeoTopics","enableNewsLatestNewsNativeAd","enablePersonalFinanceArticleReadMoreAlgo","enablePersonalFinanceNewsletterIntegration","enablePersonalFinanceZillowIntegration","enablePf2SubsSpotlight","enablePfLandingP2","enablePfPremium","enablePfStreaming","enablePinholeScreenshotOGForQuote","enablePlus","enablePortalStockStory","enableQSPChartEarnings","enableQSPChartNewShading","enableQSPChartRangeTooltips","enableQSPEarnings","enableQSPEarningsVsRev","enableQSPHistoryPlusDownload","enableQSPNavIcon","enableQSPWebviews","enableQuoteLookup","enableRecentQuotes","enableResearchHub","enableScreenerRedesign","enableSECFiling","enableSigninBeforeCheckout","enableSmartAssetMsgA","enableStockStoryPfPage","enableStockStoryTimeToBuy","enableTradeNow","enableVideoInHero","enableDockQuoteEventsDateRangeSelect","enableCompareFeatures","enableGenericHeatMap","enableQSPIndustryHeatmap","enableStatusBadge"],
                "isDebug":False,
                "isForScreenshot":False,
                "isWebview":False,
                "theme":"light",
                "pnrID":"",
                "isError":False,
                "areAdsEnabled":True,
                "ccpa":{
                    "warning":"",
                    "footerSequence":["terms_and_privacy","privacy_settings"],
                    "links":{
                        "privacy_settings":{
                            "url":"https://guce.yahoo.com/privacy-settings?locale=en-US",
                            "label":"Privacy & Cookie Settings",
                            "id":"privacy-link-privacy-settings"
                        },
                        "terms_and_privacy":{
                            "multiurl":True,
                            "label":"${terms_link}Terms${end_link} and ${privacy_link}Privacy Policy${end_link}",
                            "urls":{
                                "terms_link":"https://guce.yahoo.com/terms?locale=en-US",
                                "privacy_link":"https://guce.yahoo.com/privacy-policy?locale=en-US"
                            },
                            "ids":{
                                "terms_link":"privacy-link-terms-link",
                                "privacy_link":"privacy-link-privacy-link"
                            }
                        }
                    }
                },
                "yrid":"6l1sngpjo1fbk",
                "user":{
                    "age":-2147483648,
                    "crumb":"CkiKVmOEA..",
                    "firstName":None,
                    "gender":"",
                    "year":0
                }
            }
        }

        r: requests.Response = self._post(url=url, data=data, headers=headers)
        print(r.url)
        print(r.content)
        if len(r.json()['data']['tickerStream']['stream']) > 0:
            news = pd.DataFrame(data=[{ 
                'id': v['content']['id'],
                'url': v['content']['clickThroughUrl']['url'] if v['content']['clickThroughUrl'] is not None else v['content']['canonicalUrl']['url'],
                'provider': v['content']['provider']['displayName'],
                'date': v['content']['pubDate'],
                'type': v['content']['contentType'],
                'tickers': [t['symbol'] for t in v['content']['finance']['stockTickers']],
                'summary': v['content']['summary'],
                'title': v['content']['title']
            } 
            for v in r.json()['data']['tickerStream']['stream']])
            news['date'] = pd.to_datetime(news['date'])
            if not df: news['date'] = news['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        else: 
            news = pd.DataFrame()
        
        self.news: list | pd.DataFrame = news if df else news.to_dict(orient='records')

        return news if df else news.to_dict(orient='records')

    def getPressReleases(self, limit:int=100, df:bool=True) -> list|pd.DataFrame:

        url = f'https://finance.yahoo.com/xhr/ncp?location=US&queryRef=pressRelease&serviceKey=ncp_fin&listName={self.ticker}-press-releases&lang=en-US&region=US'
        params: dict = {
            'location': 'US', 
            'queryRef': 'pressRelease',
            'serviceKey': 'ncp_fin',
            'listName': f'{self.ticker}-press-releases', 
            'lang': 'en-US', 
            'region': 'US'
        }
        headers: dict[str, str] = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Length': '3862',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Cookie': 'A1=d=AQABBDtm1WYCEFys__46DFFzlPqGPNYPx9EFEgABCAHegGetZ-S2b2UBAiAAAAcInXrRZskjzuQ&S=AQAAAh5MvLzwu_PDCuOIGDVnUjk;',
            'Host': 'finance.yahoo.com',
            'Origin': 'https://finance.yahoo.com',
            'Pragma': 'no-cache',
            'Referer': f'https://finance.yahoo.com/quote/{self.ticker}/chart/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-crumb': 'e4rJKMRoY0B',
        }
        data: dict = {
            "serviceConfig":{
                "count":250,
                "imageTags":["168x126|1|80","168x126|2|80"],
                "thumbnailSizes":["170x128"],
                "spaceId":"95993639",
                "snippetCount":limit,
                "s":[self.ticker]
            },
            "session":{
                "consent":{
                    "allowContentPersonalization":False,
                    "allowCrossDeviceMapping":False,
                    "allowFirstPartyAds":False,
                    "allowSellPersonalInfo":True,
                    "canEmbedThirdPartyContent":False,
                    "canSell":True,
                    "consentedVendors":[],
                    "allowAds":True,
                    "allowOnlyLimitedAds":True,
                    "rejectedAllConsent":True,
                    "allowOnlyNonPersonalizedAds":False
                },
                "authed":"0",
                "ynet":"0",
                "ssl":"1",
                "spdy":"0",
                "ytee":"0",
                "mode":"normal",
                "tpConsent":False,
                "site":"finance",
                "adblock":"0",
                "bucket":["yf-csn-on","newslatestnativead-test","yf-advchart-nimbus"],
                "colo":"ir2",
                "device":"desktop",
                "bot":"0",
                "browser":"chrome",
                "app":"unknown",
                "ecma":"modern",
                "environment":"prod",
                "gdpr":True,
                "lang":"en-US",
                "dir":"ltr",
                "intl":"us",
                "network":"broadband",
                "os":"windows nt",
                "partner":"none",
                "region":"US",
                "time":int(dt.datetime.now().timestamp()*1000),
                "tz":"Europe/Madrid",
                "usercountry":"ES",
                "rmp":"0",
                "webview":"0",
                "feature":["disableServiceRewrite","disableBack2Classic","disableYPFTaxArticleDisclosure","enableAdRefresh20s","enableAnalystRatings","enableAPIRedisCaching","enableChartbeat","enableChatSupport","enableCompare","enableCompareConvertCurrency","enableConsentAndGTM","enableCrumbRefresh","enableCSN","enableCurrencyConverter","enableDockAddToFollowing","enableDockCondensedHeader","enableDockNeoOptoutLink","enableDockPortfolioControl","enableExperimentalDockModules","enableLazyQSP","enableLiveBlogStatus","enableLivePage","enableMarketsLeafHeatMap","enableMultiQuote","enableNeoAdvancedChart","enableNeoArticle","enableNeoAuthor","enableNeoBasicPFs","enableNeoGreen","enableNeoHouseCalcPage","enableNeoInvestmentIdea","enableNeoMortgageCalcPage","enableNeoOptOut","enableNeoPortfolioDetail","enableNeoQSPReportsLeaf","enableNeoResearchReport","enableNeoTopics","enableNewsLatestNewsNativeAd","enablePersonalFinanceArticleReadMoreAlgo","enablePersonalFinanceNewsletterIntegration","enablePersonalFinanceZillowIntegration","enablePf2SubsSpotlight","enablePfLandingP2","enablePfPremium","enablePfStreaming","enablePinholeScreenshotOGForQuote","enablePlus","enablePortalStockStory","enableQSPChartEarnings","enableQSPChartNewShading","enableQSPChartRangeTooltips","enableQSPEarnings","enableQSPEarningsVsRev","enableQSPHistoryPlusDownload","enableQSPNavIcon","enableQSPWebviews","enableQuoteLookup","enableRecentQuotes","enableResearchHub","enableScreenerRedesign","enableSECFiling","enableSigninBeforeCheckout","enableSmartAssetMsgA","enableStockStoryPfPage","enableStockStoryTimeToBuy","enableTradeNow","enableVideoInHero","enableDockQuoteEventsDateRangeSelect","enableCompareFeatures","enableGenericHeatMap","enableQSPIndustryHeatmap","enableStatusBadge"],
                "isDebug":False,
                "isForScreenshot":False,
                "isWebview":False,
                "theme":"light",
                "pnrID":"",
                "isError":False,
                "areAdsEnabled":True,
                "ccpa":{
                    "warning":"",
                    "footerSequence":["terms_and_privacy","privacy_settings"],
                    "links":{
                        "privacy_settings":{
                            "url":"https://guce.yahoo.com/privacy-settings?locale=en-US",
                            "label":"Privacy & Cookie Settings",
                            "id":"privacy-link-privacy-settings"
                        },
                        "terms_and_privacy":{
                            "multiurl":True,
                            "label":"${terms_link}Terms${end_link} and ${privacy_link}Privacy Policy${end_link}",
                            "urls":{
                                "terms_link":"https://guce.yahoo.com/terms?locale=en-US",
                                "privacy_link":"https://guce.yahoo.com/privacy-policy?locale=en-US"
                            },
                            "ids":{
                                "terms_link":"privacy-link-terms-link",
                                "privacy_link":"privacy-link-privacy-link"
                            }
                        }
                    }
                },
                "yrid":"6l1sngpjo1fbk",
                "user":{
                    "age":-2147483648,
                    "crumb":"CkiKVmOEA..",
                    "firstName":None,
                    "gender":"",
                    "year":0
                }
            }
        }

        self.r: requests.Response = self._post(url=url, data=data, headers=headers)
        news = pd.DataFrame(data=[{ 
            'id': v['content']['id'],
            'url': v['content']['clickThroughUrl']['url'] if v['content']['clickThroughUrl'] is not None else v['content']['canonicalUrl']['url'],
            'provider': v['content']['provider']['displayName'],
            'date': v['content']['pubDate'],
            'type': v['content']['contentType'],
            'summary': v['content']['summary'],
            'title': v['content']['title']
        } 
        for v in self.r.json()['data']['tickerStream']['stream']])
        news['date'] = pd.to_datetime(news['date'])
        if not df: news['date'] = news['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        self.press_releases: list | pd.DataFrame = news if df else news.to_dict(orient='records')

        return news

    def getSecReports(self, df:bool=True) -> list|pd.DataFrame:

        url: str = f'{self.base_url}/ws/market-analytics/v2/finance/insights'
        params: dict[str, str] = {
            'modules': 'sec_reports',
            'symbol': self.ticker,
            'lang': 'en-US',
            'region': 'US'
        }
        headers: dict[str, str] = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'A1=d=AQABBDtm1WYCEFys__46DFFzlPqGPNYPx9EFEgABCAHegGetZ-S2b2UBAiAAAAcInXrRZskjzuQ&S=AQAAAh5MvLzwu_PDCuOIGDVnUjk;',
            'Host': 'query1.finance.yahoo.com',
            'Origin': 'https://finance.yahoo.com',
            'Pragma': 'no-cache',
            'Referer': f'https://finance.yahoo.com/quote/{self.ticker}/chart/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-crumb': self.getCrumb(),
        }
        r: requests.Response = self._get(url=url, params=params, headers=headers)
        result = r.json()['finance']['result']
        if 'secReports' in result:
            reports = pd.DataFrame(data=result['secReports'])
            reports['filingDate'] = pd.to_datetime(reports['filingDate'], unit='ms')
            if not df: reports['filingDate'] = reports['filingDate'].dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            reports = pd.DataFrame()

        self.sec_reports: list | pd.DataFrame = reports if df else reports.to_dict(orient='records')
        
        return reports if df else reports.to_dict(orient='records')
    
    def quote(self) -> dict:

        url: str = f'{self.base_url}/v7/finance/quote'
        params: dict[str, str|int] = {
            'symbols': self.ticker,
            'lang': 'en-US',
            'region': 'US',
            'formatted': True,
            'imgHeights': 50,
            'imgLabels': 'logoUrl',
            'imgWidths': 50,
            'crumb': self.getCrumb(),
            'fields': 'optionsType,fromExchange,longName,regularMarketPrice,postMarketChangePercent,postMarketTime,headSymbolAsString,regularMarketChange,preMarketChangePercent,logoUrl,preMarketTime,fiftyTwoWeekLow,shortName,marketCap,preMarketPrice,fromCurrency,preMarketChange,fiftyTwoWeekHigh,regularMarketTime,toCurrency,postMarketPrice,regularMarketVolume,regularMarketOpen,regularMarketChangePercent,underlyingExchangeSymbol,postMarketChange,toExchange,regularMarketSource,underlyingSymbol,messageBoardId'
        }
        headers: dict[str, str] = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8,es-ES;q=0.7',
            'Cookie': 'dflow=210; GUC=AQABCAFn5ZBoFEIhcgSk&s=AQAAAEagaMWl&g=Z-RGdg; A1=d=AQABBKuyRGACEHbfmOBdBeCkRMrYGIFxTsYFEgABCAGQ5WcUaOTo7L8AAiAAAAcIq7JEYIFxTsY&S=AQAAAge6ioa3POgOxm8OdvEsvpI; A3=d=AQABBKuyRGACEHbfmOBdBeCkRMrYGIFxTsYFEgABCAGQ5WcUaOTo7L8AAiAAAAcIq7JEYIFxTsY&S=AQAAAge6ioa3POgOxm8OdvEsvpI; A1S=d=AQABBKuyRGACEHbfmOBdBeCkRMrYGIFxTsYFEgABCAGQ5WcUaOTo7L8AAiAAAAcIq7JEYIFxTsY&S=AQAAAge6ioa3POgOxm8OdvEsvpI; EuConsent=CQFwyQAQFwyQAAOACKESBJFgAAAAAAAAACiQAAAAAAAA; cmp=t=1743703482&j=1&u=1---&v=74; PRF=t%3DRYCEY%252BRR.L%252BRRU.HM%252BRRU.DU%252B500.PA%252BTSLA%252BSPY%252BRLLCF%252BRYCEF%252BIXP%252BWOOD%252BSLVP%252BPICK%252BILIT%252BRING%26qct-neo%3Dcandle%26qke-neo%3Dfalse%26theme%3Dauto',
            'origin': 'https://es.finance.yahoo.com',
            'priority': 'u=1, i',
            'referer': f'https://es.finance.yahoo.com/quote/{self.ticker}/profile/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="134", "Chromium";v="134", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        r: requests.Response = self._get(url=url, params=params, headers=headers)
        data = r.json()['quoteResponse']['result']
        return data[0] if data else {}

    def search(self, text:str) -> list:
        url: str = f'{self.base_url}/v1/finance/search'
        params: dict = {
            'q': text,
            'quotesCount': 10,
            'newsCoount': 5,
            'listsCount': 2,
            'enableFuzzyQuery': False,
            'quotesQueryId': 'tss_match_phrase_query',
            'multiQuoteQueryId': 'multi_quote_single_token_query',
            'newsQueryId': 'news_cie_vespa',
            'enableCb': True,
            'enableNavLinks': True,
            'enableEnhancedTrivialQuery': True,
            'enableResearchReports': True,
            'enableCulturalAssets': True,
            'enableLogoUrl': True,
            'enableLists': False,
            'recommendCount': '5',
            'lang': 'en-US',
            'region': 'US'
        }
        headers: dict[str, str] = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8,es-ES;q=0.7',
            'cache-control': 'no-cache',
            'connection': 'keep-alive',
            'Cookie': 'A1=d=AQABBDtm1WYCEFys__46DFFzlPqGPNYPx9EFEgABCAHegGetZ-S2b2UBAiAAAAcInXrRZskjzuQ&S=AQAAAh5MvLzwu_PDCuOIGDVnUjk;',
            'Host': self.base_url.split('//')[-1],
            'origin': 'https://es.finance.yahoo.com',
            'pragma': 'no-cache',
            'referer': f'https://es.finance.yahoo.com/quote/{self.ticker}/chart/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        r: requests.Response = self._get(url=url, params=params, headers=headers)
        return r.json()

    def realTimePrice(self):
        headers = {
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9,es;q=0.8',
            'cache-control': 'no-cache',
            'connection': 'Upgrade',
            'host': 'streamer.finance.yahoo.com',
            'origin': 'https://finance.yahoo.com',
            'pragma': 'no-cache',
            'sec-websocket-extensions': 'permessage-deflate; client_max_window_bits',
            'sec-websocket-key': 'rc/ZXS2DNagxof9EDJDWrw==',
            'sec-websocket-version': '13',
            'upgrade': 'websocket',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }
        self._get('wss://streamer.finance.yahoo.com/', params={'version': 2}, headers=headers)

    def getFundamental(self, start:dt.datetime, end:dt.datetime, type:str=None, df:bool=True) -> dict:

        if type == None: type = 'quarterlyMarketCap,trailingMarketCap,quarterlyEnterpriseValue,trailingEnterpriseValue,quarterlyPeRatio,trailingPeRatio,quarterlyForwardPeRatio,trailingForwardPeRatio,quarterlyPegRatio,trailingPegRatio,quarterlyPsRatio,trailingPsRatio,quarterlyPbRatio,trailingPbRatio,quarterlyEnterprisesValueRevenueRatio,trailingEnterprisesValueRevenueRatio,quarterlyEnterprisesValueEBITDARatio,trailingEnterprisesValueEBITDARatio'
        url: str = f'{self.base_url}/ws/fundamentals-timeseries/v1/finance/timeseries/{self.ticker}'
        params: dict[str, bool|str] = {
            'merge': False,
            'padTimeSeries': True,
            'symbol': self.ticker,
            'period1': str(start),
            'period2': str(end),
            'type': type,
            'lang': 'en-US',
            'region': 'US'
        }
        headers: dict[str, str] = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'A1=d=AQABBDtm1WYCEFys__46DFFzlPqGPNYPx9EFEgABCAHegGetZ-S2b2UBAiAAAAcInXrRZskjzuQ&S=AQAAAh5MvLzwu_PDCuOIGDVnUjk;',
            'Host': 'query1.finance.yahoo.com',
            'Origin': 'https://finance.yahoo.com',
            'Pragma': 'no-cache',
            'Referer': f'https://finance.yahoo.com/quote/{self.ticker}/chart/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-crumb': self.getCrumb(),
        }
        r: requests.Response = self._get(url=url, params=params, headers=headers)
        data = {}
        for series in r.json()['timeseries']['result']:
            key = series['meta']['type'][0]
            if series['meta']['symbol'][0] == self.ticker and key in series:
                temp = pd.DataFrame(data=[{'date': val['asOfDate'], 'value': val['reportedValue']['raw']} for val in series[key]])#, index=series['timestamp'])
                # temp.index = pd.to_datetime(temp.index, unit='s')
                # temp.index = temp.index.tz_localize('UTC').tz_convert('Europe/Madrid')
                temp.dropna(axis=0, inplace=True)
                data[key] = temp if df else temp.to_dict(orient='records')
        
        return data

    def getCalendar(self) -> dict:
        url: str = f'{self.base_url}/ws/screeners/v1/finance/calendar-events'
        params: dict[str, str] = {
            'countPerDay': '100',
            'economicEventsHighImportanceOnly': 'true',
            'economicEventsRegionFilter': '',
            'modules': 'earnings',
            'startDate': '1747000800000',
            'endDate': '1748296799999',
            'tickersFilter': self.ticker,
            'lang': 'en-US',
            'region': 'US'
        }
        headers: dict[str, str] = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'dflow=627; PRF=t%3DAAPL%252BXLK%252BSPY%252B500.PA%252BRRU.DU%26theme%3Dauto%26su-oo%3Dtrue%26dock-collapsed%3Dtrue; GUC=AQABCAFoI0ZoS0IZ3wPq&s=AQAAAOEyJ2la&g=aCH-ng; A1=d=AQABBFOTkGcCEDNLPt4eAn0stcNEiUDDjRkFEgABCAFGI2hLaOTo7L8AAiAAAAcIU5OQZ0DDjRk&S=AQAAAtp_iUhvfQ5xsxvZktepZpU; A1S=d=AQABBFOTkGcCEDNLPt4eAn0stcNEiUDDjRkFEgABCAFGI2hLaOTo7L8AAiAAAAcIU5OQZ0DDjRk&S=AQAAAtp_iUhvfQ5xsxvZktepZpU; A3=d=AQABBFOTkGcCEDNLPt4eAn0stcNEiUDDjRkFEgABCAFGI2hLaOTo7L8AAiAAAAcIU5OQZ0DDjRk&S=AQAAAtp_iUhvfQ5xsxvZktepZpU; _yb=MgE0ATEBLTEBMTY3MDMxNzk4Mw==; cmp=t=1747637215&j=1&u=1---&v=80; EuConsent=CQRTEQAQRTEQAAOACKESBpFgAAAAAAAAACiQAAAAAAAA',
            'Host': 'query1.finance.yahoo.com',
            'Origin': 'https://es.finance.yahoo.com',
            'Pragma': 'no-cache',
            'Referer': f'https://es.finance.yahoo.com/quote/{self.ticker}/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
        }
        
        r: requests.Response = self._get(url=url, params=params, headers=headers)
        data = r.json()

        return data['finance']['result']['earnings']
    
if __name__ == '__main__':

    # print(YahooFinance().search(text='AAPL'))

    yf_ticker = YahooTicker(ticker='AAPL', verify=False)
    fundamental = yf_ticker.getFundamental(start=int((dt.datetime.now() - dt.timedelta(days=2*365)).timestamp()), end=int(dt.datetime.now().timestamp()), df=True)
    profile: dict = yf_ticker.getProfile()
    info: dict = yf_ticker.getTicker()
    news: list|pd.DataFrame = yf_ticker.getNews()
    sec: list|pd.DataFrame = yf_ticker.getSecReports()
    intraday: list|pd.DataFrame = yf_ticker.getPrice(start=int((dt.datetime.now() - dt.timedelta(days=6)).timestamp()), end=int(dt.datetime.now().timestamp()), timeframe='1m')
    daily: list|pd.DataFrame = yf_ticker.getPrice(start=int((dt.datetime.now() - dt.timedelta(days=365*2)).timestamp()), end=int(dt.datetime.now().timestamp()), timeframe='1d')


    from zoneinfo import ZoneInfo
    price = YahooTicker('500.PA') \
                                            .getPrice(start=-90000000000000, end=int(dt.datetime.now().replace(tzinfo=ZoneInfo('Europe/Paris'), hour=0, minute=0, second=0).timestamp()), timeframe='1d', df=True)