
import datetime as dt
import json
from random import choice

import certifi
import pandas as pd
import requests
import urllib3
from bs4 import BeautifulSoup


class BenzingaError(Exception):
    
    '''
    Class to raise custom errors.
    '''

    def __init__(self, message=''):
        self.message = message
        super().__init__(self.message)


class Benzinga():

    '''
    Class used to get data from Benzinga.
    '''
    
    USER_AGENTS: str = ['Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3) Gecko/20090305 Firefox/3.1b3 GTB5',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; ko; rv:1.9.1b2) Gecko/20081201 Firefox/3.1b2',
        'Mozilla/5.0 (X11; U; SunOS sun4u; en-US; rv:1.9b5) Gecko/2008032620 Firefox/3.0b5',
        'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.8.1.12) Gecko/20080214 Firefox/2.0.0.12',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; cs; rv:1.9.0.8) Gecko/2009032609 Firefox/3.0.8',
        'Mozilla/5.0 (X11; U; OpenBSD i386; en-US; rv:1.8.0.5) Gecko/20060819 Firefox/1.5.0.5',
        'Mozilla/5.0 (Windows; U; Windows NT 5.0; es-ES; rv:1.8.0.3) Gecko/20060426 Firefox/1.5.0.3',
        'Mozilla/5.0 (Windows; U; WinNT4.0; en-US; rv:1.7.9) Gecko/20050711 Firefox/1.0.6',
        'Mozilla/5.0 (Windows; Windows NT 6.1; rv:2.0b2) Gecko/20100720 Firefox/4.0b2',
        'Mozilla/5.0 (X11; Linux x86_64; rv:2.0b4) Gecko/20100818 Firefox/4.0b4',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2) Gecko/20100308 Ubuntu/10.04 (lucid) Firefox/3.6 GTB7.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b7) Gecko/20101111 Firefox/4.0b7',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b8pre) Gecko/20101114 Firefox/4.0b8pre',
        'Mozilla/5.0 (X11; Linux x86_64; rv:2.0b9pre) Gecko/20110111 Firefox/4.0b9pre',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b9pre) Gecko/20101228 Firefox/4.0b9pre',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.2a1pre) Gecko/20110324 Firefox/4.2a1pre',
        'Mozilla/5.0 (X11; U; Linux amd64; rv:5.0) Gecko/20100101 Firefox/5.0 (Debian)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110613 Firefox/6.0a2',
        'Mozilla/5.0 (X11; Linux i686 on x86_64; rv:12.0) Gecko/20100101 Firefox/12.0',
        'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2',
        'Mozilla/5.0 (X11; Ubuntu; Linux armv7l; rv:17.0) Gecko/20100101 Firefox/17.0',
        'Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130328 Firefox/21.0',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:22.0) Gecko/20130328 Firefox/22.0',
        'Mozilla/5.0 (Windows NT 5.1; rv:25.0) Gecko/20100101 Firefox/25.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:25.0) Gecko/20100101 Firefox/25.0',
        'Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0',
        'Mozilla/5.0 (X11; Linux i686; rv:30.0) Gecko/20100101 Firefox/30.0',
        'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:58.0) Gecko/20100101 Firefox/58.0',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.36 Safari/525.19',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.540.0 Safari/534.10',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.4 (KHTML, like Gecko) Chrome/6.0.481.0 Safari/534.4',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en-US) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.375.86 Safari/533.4',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.2 (KHTML, like Gecko) Chrome/4.0.223.3 Safari/532.2',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.201.1 Safari/532.0',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.27 Safari/532.0',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/530.5 (KHTML, like Gecko) Chrome/2.0.173.1 Safari/530.5',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.558.0 Safari/534.10',
        'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.600.0 Safari/534.14',
        'Mozilla/5.0 (X11; U; Windows NT 6; en-US) AppleWebKit/534.12 (KHTML, like Gecko)Chrome/9.0.587.0 Safari/534.12',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.0 Safari/534.13',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.11 Safari/534.16',
        'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20',
        'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.792.0 Safari/535.1',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.872.0 Safari/535.2',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
        'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.45 Safari/535.19',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.103 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.38 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    ]

    headers: dict = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                        'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                        'Chrome/108.0.0.0 Safari/537.36',
    }

    BASE_URL: str = 'https://www.benzinga.com'
    TICKER_URL: str = f'{BASE_URL}/quote/'
    EARNINGS_URL: str = f'{BASE_URL}/calendars/earnings'
    PREMARKET_URL: str = f'{BASE_URL}/premarket/'
    symbol: str = None

    def __init__(self, symbol:str=None, headers:dict=None, random_headers:bool=True) -> None:
        
        self.headers: dict = headers if headers != None else self.headers
        self.random_headers: bool = random_headers
        self.data = None

        if symbol != None:

            self._newSymbol(symbol)
    
    def _random_header(self) -> dict:

        '''
        This function selects a random User-Agent from the User-Agent list. 
        User-Agents are used in order to avoid the limitations of the requests 
        to Finviz.com. The User-Agent is specified on the headers of the 
        requests and is different for every request.
        '''

        self.header: dict = {'User-Agent': choice(self.USER_AGENTS)}

        return self.header

    def _request(self, url:str, params:dict=None) -> requests.Response:

        self.r: requests.Response = requests.get(url, params=params, 
                                        headers=self._random_header() if self.random_headers \
                                            else self.headers)
        print(self.r.url)

        return self.r

    def _newSymbol(self, symbol:str=None, url:str=TICKER_URL) -> None:
        
        if (symbol != None and symbol != self.symbol) or (url != self.TICKER_URL):
            
            if url == self.TICKER_URL:
                url: str = url + symbol
                self.symbol: str = symbol
                

            if True:
                self.r: requests.Response = self._request(url)
                html: BeautifulSoup = BeautifulSoup(self.r.text,'html.parser')
                self.data = json.loads(html.find_all('script', {'id':"__NEXT_DATA__"})[0] \
                                .prettify().split('json">')[1].split('</script')[0]) \
                                ['props']['pageProps']
            else:
                content = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where()) \
                        .urlopen('GET',url,headers=self.headers)
                html = BeautifulSoup(content.data,'html.parser')
                self.data = json.loads(html.find_all('script', {'id':"__NEXT_DATA__"})[0].contents[0]) \
                        ['props']['pageProps']

        elif self.data == None:

            raise(BenzingaError(f"There is no symbol. Please enter a valid symbol."))

    def symbolsQuote(self, symbols:list=None, df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get data for a list of symbols.

        Parameters
        ----------
        symbols: list
            List containing the symbols.

        Returns
        -------
        info: dict | DataFrame
            Dictionary or DataFrame with data requested.
        '''

        apiKey: str = 'anBvLgmzgKHJhQdQQzBe24yKFpHwcBJN'
        symbols: list = [i.replace('/','%2F') for i in symbols]
        symbols: str = '%2C'.join(symbols)
        quote_url: str = f'https://data-api.benzinga.com/rest/v2/quote?apikey={apiKey}&symbols={symbols}'

        content: requests.Response = self._request(quote_url)
        info = json.loads(content.content)
        if df:
            info = pd.DataFrame(info).T

        return info

    def info(self, symbol:str=None) -> dict:

        '''
        Get data for the symbol.

        Parameters
        ----------
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict
            Dictionary with data requested.
        '''
            
        self._newSymbol(symbol)

        info: dict = {
            **self.data['metaProps'],
            **self.data['profile']['fundamentals']['company'],
            **self.data['profile']['fundamentals']['companyProfile'],
            **self.data['profile']['fundamentals']['shareClass'],
            **self.data['profile']['fundamentals']['assetClassification'],
        }
        del info['translations']

        return info
        
    def classification(self, symbol:str=None) -> dict:

        '''
        Get data for the symbol classification.

        Parameters
        ----------
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict
            Dictionary with data requested.
        '''
            
        self._newSymbol(symbol)

        info: dict = self.data['profile']['fundamentals']['assetClassification']

        return info

    def marketCap(self, symbol:str=None) -> dict:

        '''
        Get data for the symbol. The dictionary contains
        the last date of update, market capitalization, 
        enterprise value and shares outstanding.

        Parameters
        ----------
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict
            Dictionary with data requested.
        '''

        self._newSymbol(symbol)

        info: dict = self.data['profile']['fundamentals']['shareClassProfile']

        return info

    def shareData(self, symbol:str=None) -> dict:

        '''
        Get data for the symbol shares.

        Parameters
        ----------
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict
            Dictionary with data requested.
        '''

        self._newSymbol(symbol)

        info: dict = self.data['profile']['richQuoteData']

        return info

    def schedule(self, symbol:str=None, df:bool=False) -> (dict | pd.DataFrame):

        '''
        Get data for the symbol trading schedule.

        Parameters
        ----------
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict | pd.DataFrame
            Dictionary with data requested.
        '''

        self._newSymbol(symbol)

        if df:
            info: pd.DataFrame = pd.DataFrame(self.data['profile']['schedule']['schedule']['sessions'])
            info['tz'] = self.data['profile']['schedule']['schedule']['timeZoneId']
        else:
            info: dict = {}
            for t in self.data['profile']['schedule']['schedule']['sessions']:
                info[t['type']] = {}
                for i in t:
                    info[t['type']][i] = t[i]
            info['tz'] = self.data['profile']['schedule']['schedule']['timeZoneId']

        return info

    def valuations(self, symbol:str=None) -> dict:

        '''
        Get data for the symbol valuations.

        Parameters
        ----------
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict
            Dictionary with data requested.
        '''

        self._newSymbol(symbol)

        info: dict = self.data['profile']['fundamentals']['valuationRatios'][0]
        key: list = []
        for t in info['id']:
            info[t] = info['id'][t]
            key.append(info['id'][t])
        info['id'] = '_'.join(key)

        return info

    def balanceSheet(self, symbol:str=None) -> dict:

        '''
        Get data for the symbol balance sheet.

        Parameters
        ----------
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict
            Dictionary with data requested.
        '''

        self._newSymbol(symbol)

        info: dict = self.data['profile']['fundamentals']['financials'][0]['balanceSheet']
        key: list = []
        for t in info['id']:
            info[t] = info['id'][t]
            key.append(info['id'][t])
        info['id'] = '_'.join(key)

        return info

    def cashFlow(self, period:str='3M', symbol:str=None) -> dict:

        '''
        Get data for the symbol cash flow statement.

        Parameters
        ----------
        period: str
            String containing the period. It can be: 3M (3 month)
            or 1Y (1 year).
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict
            Dictionary with data requested.
        '''

        self._newSymbol(symbol)

        if period == '3M':

            info: dict = self.data['profile']['fundamentals']['financials'][0]['cashFlowStatement']
            key: list = []
            for t in info['id']:
                info[t] = info['id'][t]
                key.append(info['id'][t])
            info['id'] = '_'.join(key)
        
        elif period == '1Y':

            info: dict = self.data['profile']['fundamentalsAnnual']['financials'][0]['cashFlowStatement']
            key: list = []
            for t in info['id']:
                info[t] = info['id'][t]
                key.append(info['id'][t])
            info['id'] = '_'.join(key)
        
        else:

            raise(BenzingaError('Period not valid. It must be 3M (3 month) or 1Y (1 year).'))
        
        return info

    def incomeStatement(self, period:str='3M', symbol:str=None) -> dict:

        '''
        Get data for the symbol income statement.

        Parameters
        ----------
        period: str
            String containing the period. It can be: 3M (3 month)
            or 1Y (1 year).
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict
            Dictionary with data requested.
        '''

        self._newSymbol(symbol)

        if period == '3M':

            info: dict = self.data['profile']['fundamentals']['financials'][0]['incomeStatement']
            key: list = []
            for t in info['id']:
                info[t] = info['id'][t]
                key.append(info['id'][t])
            info['id'] = '_'.join(key)
        
        elif period == '1Y':

            info: dict = self.data['profile']['fundamentalsAnnual']['financials'][0]['incomeStatement']
            key: list = []
            for t in info['id']:
                info[t] = info['id'][t]
                key.append(info['id'][t])
            info['id'] = '_'.join(key)
        
        else:

            raise(BenzingaError('Period not valid. It must be 3M (3 month) or 1Y (1 year).'))
        
        return info

    def operationRatios(self, symbol:str=None) -> dict:

        '''
        Get data for the symbol operation ratios.

        Parameters
        ----------
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict
            Dictionary with data requested.
        '''

        self._newSymbol(symbol)

        info: dict = self.data['profile']['fundamentals']['operationRatios'][0]
        key: list = []
        for t in info['id']:
            info[t] = info['id'][t]
            key.append(info['id'][t])
        info['id'] = '_'.join(key)

        return info

    def listFilling(self, period:str='3M', symbol:str=None) -> dict:

        '''
        Get data for the symbol filling.

        Parameters
        ----------
        period: str
            String containing the period. It can be: 3M (3 month)
            or 1Y (1 year).
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict
            Dictionary with data requested.
        '''

        self._newSymbol(symbol)

        if period == '3M':

            info: dict = self.data['profile']['fundamentals']['earningReports'][0]
            key: list = []
            for t in info['id']:
                info[t] = info['id'][t]
                key.append(info['id'][t])
            info['id'] = '_'.join(key)
        
        elif period == '1Y':

            info: dict = self.data['profile']['fundamentalsAnnual']['earningReports'][0]
            key: list = []
            for t in info['id']:
                info[t] = info['id'][t]
                key.append(info['id'][t])
            info['id'] = '_'.join(key)
        
        else:

            raise(BenzingaError('Period not valid. It must be 3M (3 month) or 1Y (1 year).'))
        
        return info

    def earnings(self, symbol:str=None, df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get data for the symbol earnings.

        Parameters
        ----------
        symbol: str
            String containing the symbol.
        df: bool
            True to return data in DataFrame format instead of 
            dictionary.

        Returns
        -------
        info: dict | pd.DataFrame
            Dictionary or DataFrame with data requested.
        '''

        self._newSymbol(symbol)

        try:
            info: dict = self.data['profile']['earnings'] if 'earnings' in self.data['profile'] \
                        else self.data['profile']['earningsSummary']
            if df:
                info: pd.DataFrame = pd.DataFrame(info).iloc[::-1]
                info.reset_index(inplace=True)
        except Exception as e:
            print(e)
            if df:
                info: pd.DataFrame = pd.DataFrame()
            else:
                info: dict = {}

        return info

    def dividends(self, symbol:str=None, df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get data for the symbol dividend data.

        Parameters
        ----------
        symbol: str
            String containing the symbol.
        df: bool
            True to return data in DataFrame format instead of 
            dictionary.

        Returns
        -------
        info: dict | pd.DataFrame
            Dictionary or DataFrame with data requested.
        '''

        self._newSymbol(symbol)

        try:
            info: dict = self.data['profile']['dividendData'] if 'dividendData' in self.data['profile'] \
                        else self.data['profile']['dividendSummary']
            if df:
                info: pd.DataFrame = pd.DataFrame(info).iloc[::-1]
                info.reset_index(inplace=True)
        except Exception as e:
            print(e)
            if df:
                info: pd.DataFrame = pd.DataFrame()
            else:
                info: dict = {}

        return info

    def splits(self, symbol:str=None, df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get data for the symbol splits data.

        Parameters
        ----------
        symbol: str
            String containing the symbol.
        df: bool
            True to return data in DataFrame format instead of 
            dictionary.

        Returns
        -------
        info: dict | pd.DataFrame
            Dictionary or DataFrame with data requested.
        '''

        self._newSymbol(symbol)

        info: dict = self.data['profile']['splitsData']
        if df:
            info: pd.DataFrame = pd.DataFrame(info)

        return info

    def ownership(self, symbol:str=None) -> dict:

        '''
        Get data for the symbol ownership ratios.

        Parameters
        ----------
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict
            Dictionary with data requested.
        '''

        self._newSymbol(symbol)
        info: dict = self.data['profile']['fundamentals']['ownership'][0]
        
        if isinstance(info['id'], dict):
            key: list = []
            for t in info['id']:
                info[t] = info['id'][t]
                key.append(info['id'][t])
            info['id'] = '_'.join(key)

        return info

    def shortInterest(self, symbol:str=None, df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get data for the symbol short interest.

        Parameters
        ----------
        symbol: str
            String containing the symbol.
        df: bool
            True to return data in DataFrame format instead of 
            dictionary.

        Returns
        -------
        info: dict | pd.DataFrame
            Dictionary or DataFrame with data requested.
        '''

        self._newSymbol(symbol)

        info: dict = self.data['profile']['shortInterest']
        if df:
            info: pd.DataFrame = pd.DataFrame(info)

        return info

    def mergersAcquisitions(self, symbol:str=None, df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get data for the symbol mergers and acquisitions.

        Parameters
        ----------
        symbol: str
            String containing the symbol.
        df: bool
            True to return data in DataFrame format instead of 
            dictionary.

        Returns
        -------
        info: dict | pd.DataFrame
            Dictionary or DataFrame with data requested.
        '''

        self._newSymbol(symbol)

        info: dict = self.data['profile']['maSummary']['ma']
        if df:
            info: pd.DataFrame = pd.DataFrame(info)

        return info

    def news(self, symbol:str=None, df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get data for the symbol news.

        Parameters
        ----------
        symbol: str
            String containing the symbol.
        df: bool
            True to return data in DataFrame format instead of 
            dictionary.

        Returns
        -------
        info: dict | pd.DataFrame
            Dictionary or DataFrame with data requested.
        '''

        self._newSymbol(symbol)

        info: dict = self.data['profile']['newsAll']
        if df:
            info: pd.DataFrame = pd.DataFrame(info)

        return info

    def relatedStocks(self, symbol:str=None, df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get data for the stocks related with the symbol.

        Parameters
        ----------
        symbol: str
            String containing the symbol.
        df: bool
            True to return data in DataFrame format instead of 
            dictionary.

        Returns
        -------
        info: dict | pd.DataFrame
            Dictionary or DataFrame with data requested.
        '''

        self._newSymbol(symbol)

        info: dict = self.data['profile']['quotes']
        for j in self.data['profile']['tickerDetails']['peers']:
            for i in j:
                if i not in info[j['symbol']].keys():
                    info[j['symbol']][i] = j[i]
    
        if df:
            info: pd.DataFrame = pd.DataFrame(info).T

        return info

    def keyData(self, symbol:str=None) -> dict:

        '''
        Get key data for the symbol.

        Parameters
        ----------
        symbol: str
            String containing the symbol.

        Returns
        -------
        info: dict
            Dictionary with data requested.
        '''
            
        self._newSymbol(symbol)

        info: dict = {}
        if 'profile' not in self.data:
            print(f'BenzingaError: Ticker ({symbol if symbol != None else self.symbol}) not found in Benzinga!')
            return {}
        for i in self.data['profile']['tickerDetails']:
            if not isinstance(self.data['profile']['tickerDetails'][i], list) and \
                not isinstance(self.data['profile']['tickerDetails'][i], dict):
                info[i] = self.data['profile']['tickerDetails'][i]
                
        info: dict = {
            **info,
            **self.data['profile']['tickerDetails']['financialStats'],
            **self.data['profile']['tickerDetails']['keyStatistics'],
        }
        if len(self.data['profile']['tickerDetails']['percentiles']) > 0:
            info: dict = {**info, **self.data['profile']['tickerDetails']['percentiles'][0]}

        return info

    def percentileStats(self, symbol:str=None, df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get data for the symbol percentile stats.

        Parameters
        ----------
        symbol: str
            String containing the symbol.
        df: bool
            True to return data in DataFrame format instead of 
            dictionary.

        Returns
        -------
        info: dict | pd.DataFrame
            Dictionary or DataFrame with data requested.
        '''

        self._newSymbol(symbol)

        info: dict = self.data['profile']['tickerDetails']['percentiles']
        if df:
            info: pd.DataFrame = pd.DataFrame(info)

        return info

    def earningsCalendar(self, df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get the earnings calendar for the day.

        Parameters
        ----------
        symbol: str
            String containing the symbol.
        df: bool
            True to return data in DataFrame format instead of 
            dictionary.

        Returns
        -------
        data: dict | pd.DataFrame
            Dictionary or DataFrame with data requested.
        '''
        
        self._newSymbol(url=self.EARNINGS_URL)
        data: dict = self.data['calendarDataSet']

        if df:
            data: pd.DataFrame = pd.DataFrame(data)

        return data

    def earningsHistoric(self, date_from:str=None, date_to:str=None, 
        df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get the earnings calendar between two dates.

        Parameters
        ----------
        date_from: str
            String containing the initial date.
        date_to: str
            String containing the final date.
        df: bool
            True to return data in DataFrame format instead of 
            dictionary.

        Returns
        -------
        data: dict | pd.DataFrame
            Dictionary or DataFrame with the requested data.
        '''

        if date_to == None:
            date_to = dt.datetime.today()
        if date_from == None:
            if isinstance(date_to, str):
                date_to = dt.datetime.strptime(date_to, '%Y-%m-%d')
            date_from = date_to - dt.timedelta(days=30)

        token: str = '1c2735820e984715bc4081264135cb90'
 
        finished: bool = False
        dfs: list = []
        date_from = date_from if isinstance(date_from, str) else date_from.strftime('%Y-%m-%d')
        temp_to: str = date_to if isinstance(date_to, str) else date_to.strftime('%Y-%m-%d')
        while not finished:
        
            url: str = f'https://api.benzinga.com/api/v2.1/calendar/earnings'
            
            params: dict = {
                'token': token,
                'parameters[date_from]': date_from, 
                'parameters[date_to]': temp_to,
                'pagesize': 1000
            }

            content: requests.Response = self._request(url=url, params=params)
            html: BeautifulSoup = BeautifulSoup(content.content,'html.parser')
            items: set = html.find_all('item')
            dicts: list = []
            for i in items:
                d: dict = {}
                for j in i.find_all():
                    temp: str = str(j).split('<')[1].split('>')
                    d[temp[0]] = temp[1]
                dicts.append(d)

            dfs.append(pd.DataFrame(dicts))
            
            if 'date' not in dfs[-1] or date_from >= dfs[-1]['date'].tolist()[-1]:
                finished: bool = True
            else:
                temp_to: dt.datetime = dt.datetime.strptime(dfs[-1]['date'].tolist()[-1],'%Y-%m-%d')-dt.timedelta(days=1)
                temp_to: dt.datetime = dt.datetime.strftime(temp_to, '%Y-%m-%d')

        data: pd.DataFrame = pd.concat(dfs, ignore_index=True)

        if not df:
            data.index = data['ticker']
            data: dict = data.T.to_dict()
        
        return data

    def premarketData(self) -> pd.DataFrame:

        r: requests.Response = self._request(self.PREMARKET_URL)

        html: BeautifulSoup = BeautifulSoup(r.content, 'html.parser')

        gainers = html.find('table', {'id':'bz-gainers-table'})
        columns: list = [[cel.get_text().replace(' ', '').replace('\n','') for cel in row.find_all('th')] for row in gainers.find_all('tr')][0]
        data: list = [[cel.get_text().replace(' ', '').replace('\n','') for cel in row.find_all('td')] for row in gainers.find_all('tr')][1:]
        gainers_df: pd.DataFrame = pd.DataFrame(data=data, columns=columns)
        

        losers = html.find('table', {'id':'bz-losers-table'})
        columns: list = [[cel.get_text().replace(' ', '').replace('\n','') for cel in row.find_all('th')] for row in losers.find_all('tr')][0]
        data: list = [[cel.get_text().replace(' ', '').replace('\n','') for cel in row.find_all('td')] for row in losers.find_all('tr')][1:]
        losers_df: pd.DataFrame = pd.DataFrame(data=data, columns=columns)

        earnings = html.find('div', {'id':'premarket-landing-earnings'})
        columns: list = [[cel.get_text().replace(' ', '').replace('\n','') for cel in row.find_all('th')] for row in earnings.find_all('tr')][0]
        count: int = 0
        for i,c in enumerate(columns):
            if c in columns[:i]:
                columns[i] = c+f'{count}'
                count += 1
        data: list = [[cel.get_text().replace(' ', '').replace('\n','') for cel in row.find_all('td')] for row in earnings.find_all('tr')][1:]
        earnings_df: pd.DataFrame = pd.DataFrame(data=data, columns=columns)

        return gainers_df, losers_df, earnings_df



def dfToDB(df:pd.DataFrame) -> None:

    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///earnings.db', echo=True) # :memory:', echo=True)
    conn = engine.connect()

    try:
        df.to_sql('earnings', con=engine)#, if_exists='append')
    except:
        import os 
        os.remove("earnings.db")
        df.to_sql('earnings', con=engine)#, if_exists='append')

def dfFromDB() -> pd.DataFrame:

    from sqlalchemy import create_engine

    engine = create_engine('sqlite:///earnings.db', echo=True) # :memory:', echo=True)

    columns: list = [i[1] for i in engine.execute("PRAGMA table_info(earnings)").fetchall()]
    db_data: pd.DataFrame = pd.DataFrame(engine.execute("SELECT * FROM earnings").fetchall(), columns=columns)
    db_data: pd.DataFrame = db_data[(db_data['eps_surprise'] != '') & (db_data['exchange'] != 'OTC')]

    return db_data

def downloadDailyData(df:pd.DataFrame) -> dict:
    
    import yfinance as yf

    dfs: dict = {}
    for i in df['index']:

        ticker: str = i.split('_')[0]
        earning_date: str = i.split('_')[1]
        ticker_earning: dict = df[df['index'] == i].iloc[0].to_dict()
        start_date: str = dt.datetime.strftime(dt.datetime.strptime(earning_date, '%Y-%m-%d') - dt.timedelta(days=1), '%Y-%m-%d')

        if ticker_earning['time'] > '09:00:00':
            end_date: str = dt.datetime.strftime(dt.datetime.strptime(earning_date, '%Y-%m-%d') + dt.timedelta(days=2), '%Y-%m-%d')
        else:
            end_date: str = dt.datetime.strftime(dt.datetime.strptime(earning_date, '%Y-%m-%d') + dt.timedelta(days=1), '%Y-%m-%d')

        dfs[i] = {}
        dfs[i]['data'] = pd.DataFrame()
        error: bool = False
        while (dfs[i]['data'].empty or len(dfs[i]['data']) == 1) and not error:
            try:
                dfs[i]['data'] = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1d", raise_errors=True)
                end_date = dt.datetime.strftime(dt.datetime.strptime(end_date, '%Y-%m-%d') + dt.timedelta(days=1), '%Y-%m-%d')
            except:
                error = True

        if error:
            del dfs[i]
            continue

        dfs[i]['data']['gap%'] = (dfs[i]['data']['Open'] / dfs[i]['data']['Close'].shift(1) - 1) * 100
        dfs[i]['data'].index = dfs[i]['data'].index.strftime('%Y-%m-%d')
        dfs[i]['data'] = dfs[i]['data'].tail(1)#[dfs[i]['data'].index >= earning_date]

        dfs[i] = {**dfs[i], **ticker_earning}
        dfs[i]['datetime'] = dfs[i]['date'] + ' ' + dfs[i]['time']

    return dfs

if __name__ == '__main__':

    bz = Benzinga('TSLA')
    result: dict = {}
    for k, v in bz.info().items():
        if k in ['dateUpdated', 'image', 'primarySymbol', 'primaryExchange', 'cik', 'isin', 'cusip',
                 'standardName', 'yearofEstablishment', 'shortName', 'address1', 'city', 'country', 
                 'homepage', 'phone', 'postalCode', 'province', 'totalEmployees', 'legalName', 'longDescription',
                 'currencyId', 'ipoDate', 'sicName', 'naicsName', 'msSuperSectorName', 'msSectorName', 
                 'msGroupName', 'msIndustryName']:
            result[k] = v
    # classification = bz.classification()
    # result['marketCap'] = bz.marketCap()
    for k, v in bz.shareData().items():
        if k in ['bzExchange', 'type', 'lastTradePrice', 'lastTradeTime', 'volume', 'fiftyDayAveragePrice', 
                 'hundredDayAveragePrice', 'averageVolume', 'fiftyTwoWeekHigh', 'fiftyTwoWeekLow', 
                 'marketCap', 'sharesOutstanding', 'sharesFloat']:
            result[k] = v
    result['schedule'] = bz.schedule()
    result['valuations'] = bz.valuations()
    result['balanceSheet'] = bz.balanceSheet()
    result['cashFlow'] = bz.cashFlow()
    result['incomeStatement'] = bz.incomeStatement()
    result['operationRatios'] = bz.operationRatios()
    # listFilling = bz.listFilling()
    result['earnings'] = bz.earnings(df=False)
    result['dividends'] = bz.dividends(df=False)
    result['splits'] = bz.splits(df=False)
    result['ownership'] = bz.ownership()
    result['shortInterest'] = bz.shortInterest(df=False)
    result['mergersAcquisitions'] = bz.mergersAcquisitions(df=False)
    result['news'] = bz.news(df=False)
    # data = bz.keyData()
    relatedStocks = bz.relatedStocks()
    result['relatedStocks'] = (relatedStocks['companyStandardName'] + ' (' + relatedStocks['symbol'] + ':' + relatedStocks['bzExchange'] +')').to_list()
    # percentileStats = bz.percentileStats()
    
    
    earningsHistoric = bz.earningsHistoric(df=False)
    earningsCalendar = bz.earningsCalendar(df=False)

    # Analyze earnings
    if False:
        
        import concurrent.futures

        import plotly.graph_objects as go
        import yfinance as yf
        from plotly.subplots import make_subplots

        # Get earnings and store
        earnings = BenzingaWebScrap().earningsHistoric(date_from='2000-01-01', date_to='2023-01-30', df=True)
        dfToDB(earnings)
        db_data = dfFromDB()

        # Get Price data
        analyze_data = db_data.head(1000)
        l = list(range(0, len(analyze_data), int(len(analyze_data)/10)))
        l[-1] = len(analyze_data)
        iterable = [analyze_data[l[i]:l[i+1]] for i in range(len(l[:-1]))]

        with concurrent.futures.ProcessPoolExecutor(3) as executor:
            result = list(executor.map(downloadDailyData, iterable))

        dfs = {}
        for i in result:
            dfs = {**dfs, **i}

        # Prepare data to analyze
        needed_data = {}
        for t in dfs:
            needed_data[t] = {
                'Ticker': dfs[t]['ticker'],
                'Exchange': dfs[t]['exchange'],
                'Datetime': dfs[t]['datetime'],
                'Open': dfs[t]['data'].iloc[0]['Open'],
                'High': dfs[t]['data'].iloc[0]['High'],
                'Low': dfs[t]['data'].iloc[0]['Low'],
                'Close': dfs[t]['data'].iloc[0]['Close'],
                'Gap%': dfs[t]['data'].iloc[0]['gap%'],
                'RevenuePrior': dfs[t]['revenue_prior'],
                'RevenueActual': dfs[t]['revenue'],
                'RevenueEstimate': dfs[t]['revenue_est'],
                'RevenueSurprise': dfs[t]['revenue_surprise'],
                'RevenueSurprise%': dfs[t]['revenue_surprise_percent'],
                'EPSprior': dfs[t]['eps_prior'],
                'EPSactual': dfs[t]['eps'],
                'EPSestimate': dfs[t]['eps_est'],
                'EPSsurprise': dfs[t]['eps_surprise'],
                'EPSsurprise%': dfs[t]['eps_surprise_percent'],
            }
            for i in needed_data[t]:
                if i in ['Ticker', 'Exchange', 'Datetime', 'Open', 'High', 'Low', 
                        'Close', 'Gap%']:
                    continue
                needed_data[t][i] = float(needed_data[t][i]) if needed_data[t][i] != '' else 0

        needed_df = pd.DataFrame(needed_data).T
        needed_df['Return'] = needed_df['Close'] - needed_df['Open']
        needed_df['Return%'] = (needed_df['Close'] - needed_df['Open']) / needed_df['Open'] * 100

        # Filter data
        stats = {
            'RA>RE': {
                'data': needed_df[(needed_df['RevenueActual'] > needed_df['RevenueEstimate'])],
            },
            'RA>RE>RP': {
                'data': needed_df[(needed_df['RevenueActual'] > needed_df['RevenueEstimate']) & \
                        (needed_df['RevenueActual'] > needed_df['RevenuePrior'])],
            },
            'RA>RP': {
                'data': needed_df[(needed_df['RevenueActual'] > needed_df['RevenuePrior'])],
            },
            'RA<RE': {
                'data': needed_df[(needed_df['RevenueActual'] < needed_df['RevenueEstimate'])],
            },
            'RA<RE<RP': {
                'data': needed_df[(needed_df['RevenueActual'] < needed_df['RevenueEstimate']) & \
                        (needed_df['RevenueActual'] < needed_df['RevenuePrior'])],
            },
            'RA<RP': {
                'data': needed_df[(needed_df['RevenueActual'] < needed_df['RevenuePrior'])],
            },
        }

        # Calculate stats
        for o in stats:
            if '>' in o:
                stats[o]['Winrate'] = len(stats[o]['data'][stats[o]['data']['Return%'] > 0]) \
                                    /len(stats[o]['data'])
                stats[o]['RR'] = abs(stats[o]['data']['Return%'][stats[o]['data']['Return%'] > 0].mean()) \
                                /abs(stats[o]['data']['Return%'][stats[o]['data']['Return%'] <= 0].mean())
            elif '<' in o:
                stats[o]['Winrate'] = len(stats[o]['data'][stats[o]['data']['Return%'] < 0]) \
                                    /len(stats[o]['data'])
                stats[o]['RR'] = abs(stats[o]['data']['Return%'][stats[o]['data']['Return%'] < 0].mean()) \
                                /abs(stats[o]['data']['Return%'][stats[o]['data']['Return%'] >= 0].mean())
            stats[o]['Expec'] = stats[o]['Winrate'] * stats[o]['RR'] - (1-stats[o]['Winrate'])

        # Show stats
        df = {}
        for o in stats:
            df[o] = stats[o]
            del df[o]['data']
        stats = pd.DataFrame(df)

        # Plot
        if False:
            temp_df = db_data.head(10)
            dfs = {}
            for i in temp_df['index']:
                ticker = i.split('_')[0]
                start_date = dt.datetime.strftime(dt.datetime.strptime(i.split('_')[1], '%Y-%m-%d') - dt.timedelta(days=2), '%Y-%m-%d')
                end_date = dt.datetime.strftime(dt.datetime.strptime(i.split('_')[1], '%Y-%m-%d') + dt.timedelta(days=5), '%Y-%m-%d')
                dfs[i] = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1m")
            dfs

            for t in dfs:

                ticker_earning = temp_df[temp_df['index'] == t].iloc[0]

                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0, 
                                    row_heights=[5,2], specs=[[{"secondary_y": False}],[{"secondary_y": False}]])

                fig.add_trace(go.Candlestick(x=dfs[t].index, open=dfs[t]['Open'], high=dfs[t]['High'], 
                                            low=dfs[t]['Low'], close=dfs[t]['Close'], name='Price'), 
                            secondary_y=False, row=1, col=1)

                fig.add_trace(go.Bar(x=dfs[t].index, y=dfs[t]['Volume'], name='Volume'), secondary_y=False, row=2, col=1)

                # Add figure title
                fig.update_layout(title_text=f"Precio de {t.split('_')[0]} por earnings el" \
                                    f"día {t.split('_')[1]} con una sorpresa de {ticker_earning['eps_surprise']} ({ticker_earning['eps_surprise_percent']} %)")
                fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
                fig.update_xaxes(title_text="Fecha", rangeslider_visible=False, row=2, col=1)

                # Set y-axes titles
                fig.update_yaxes(title_text="<b>Precio ($)</b>", secondary_y=False, row=1, col=1)
                fig.update_yaxes(title_text="<b>Volumen</b>", row=2, col=1)

                fig.show()


