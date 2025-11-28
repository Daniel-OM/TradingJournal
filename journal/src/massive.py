
from random import choice
import datetime
import time

import requests
import pandas as pd
import numpy as np


class DataProvider:

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

    headers: dict = {'User-Agent': choice(USER_AGENTS)}

    def _to_numeric(self, string:str) -> (int | float):

        '''
        Converts a string to a number of type float 
        or int.

        Parameters
        ----------
        string: str
            String containing a number.

        Returns
        -------
        number: int | float
            Number in correct format.
        '''

        string: str = string.replace(',','')
        float_cond: bool = '.' in string or string == 'nan'
        number: (int | float)
        if 'k' in string or 'K' in string:
            number = float(string[:-1]) if float_cond else int(string[:-1])
            number = number * 1000
        elif 'm' in string or 'M' in string:
            number = float(string[:-1]) if float_cond else int(string[:-1])
            number = number * 1000000
        elif 'b' in string or 'B' in string:
            number = float(string[:-1]) if float_cond else int(string[:-1])
            number = number * 1000000000
        elif 't' in string or 'T' in string:
            number = float(string[:-1]) if float_cond else int(string[:-1])
            number = number * 1000000000000
        elif '%' in string:
            number = float(string[:-1]) if float_cond else int(string[:-1])
        else:
            number = float(string) if float_cond else int(string)

        return number
        
    def _random_header(self) -> dict:

        '''
        This function selects a random User-Agent from the User-Agent list. 
        User-Agents are used in order to avoid the limitations of the requests 
        to Finviz.com. The User-Agent is specified on the headers of the 
        requests and is different for every request.
        '''

        self.headers: dict = {**self.headers, **{'User-Agent': choice(self.USER_AGENTS)}}

        return self.headers

class Massive(DataProvider):

    '''
    Former Massive API.
    '''

    BASE_URL: str = 'https://api.massive.io'

    def __init__(self,api_key:str='cUlHULSDVdLm9Up1TsKxF3RU2dEKm3nq', 
                 free:bool=False) -> None:

        '''
        Python Wrapper for the Massive.io API.

        Parameters
        ----------
        api_key: str
            Personal key for the massive API.
        free: bool
            True to wait between requests not to exceed the free plan limits.
        '''

        self.api_key: str = api_key
        self.free: bool = free

    def _request(self, url:str, params:dict={}) -> (list | dict):

        '''
        Performs the request of type GET.

        Parameters
        ----------
        url: str
            URL to make the request.
        params: dict
            Dictionary containing the request parameters.

        Returns
        -------
        result: list | dict
            Contains the requested data.
        '''

        
        params = {**params, **{'apiKey': self.api_key}}

        self.r: requests.Response = requests.get(url=url, params=params)
        if self.free:
            time.sleep(12.1)

        r: (list | dict) = self.r.json()
        
        if 'status' not in r:
            result: list = [r]
        else:
            if r['status'] in ['OK', 'DELAYED']:
                result: dict = r
            else:
                raise(ValueError(r))

        while 'next_url' in result:
            self.r: requests.Response = requests.get(url=result['next_url'], params=params)
            new_result = self.r.json()
            if 'results' in new_result:
                result['results'] = result['results'] + new_result['results']
            else:
                print(result)
        
        return result
            
    def aggregates(self, symbol:str, multiplier:int, timespan:str, 
                   start:str, end:str, adjusted:bool=False, sort:str='desc',
                   limit:int=5000, version:str='/v2', df:bool=True
                   ) -> (dict | pd.DataFrame):

        '''
        Get a single ticker supported by Massive.io. 
        This response will have detailed information about the 
        ticker and the company behind it.

        Parameters
        ----------
        symbol: str
            The ticker symbol of the stock/equity.
        multiplier: int
            Number to multiply the timespan to form the timeframe.
        timespan: str
            Time unit to form the timeframe.
            Options: 'minute','hour','day','week','month','quarter','year'.
        start: str
            Date from which to start getting data. Either a date with 
            the format YYYY-MM-DD or a millisecond timestamp.
        end: str
            Date till which to get data. Either a date with the format 
            YYYY-MM-DD or a millisecond timestamp.
        adjusted: bool
            Whether or not the results are adjusted for splits. By default, 
            results are not adjusted. Set this to true to get results that 
            are adjusted for splits.
        sort: str
            Sort the results by timestamp. 'asc' will return results in 
            ascending order (oldest at the top), 'desc' will return results 
            in descending order (newest at the top). Default is 'asc'.
        limit:int
            Limits the number of base aggregates queried to create the 
            aggregate results. Max 50000 and Default 5000.
        version: str
            Name of the version of the API to call.
        df: bool
            Return data as DataFrame.

        Returns
        -------
        data: dict | pd.DataFrame
            Contains the requested data.
        '''

        params: dict = {'adjusted': adjusted, 'sort': sort, 'limit': limit}
        url: str = self.BASE_URL+version+f'/aggs/ticker/{symbol}/range/{multiplier}/{timespan}' + \
                                   f'/{start}/{end}'
        
        data: (list | dict) = self._request(url=url, params=params)
        
        if df:
            data: pd.DataFrame = pd.DataFrame(data['results']) \
                    if 'results' in data else pd.DataFrame(data)
            data.rename(columns={'v':'Volume','vw':'VWAP','o':'Open',
                                 'c':'Close','h':'High','l':'Low',
                                 't':'DateTime','n':'Trades'}, inplace=True)
            data['DateTime'] = pd.to_datetime(data['DateTime'], unit='ms')
            
            # Set session column for intraday timeframes
            if timespan in ['second', 'minute', 'hour']:
                try:
                    exchange_tz = 'America/New_York' # TODO: Get default timezone depending on the exchange it is trading on.
                    # If timestamps are naive, set NY timezone
                    if data['DateTime'].dt.tz is None:
                        data['DateTime'] = data['DateTime'].dt.tz_localize('UTC')
                    data['DateTime'] = data['DateTime'].dt.tz_convert('UTC')

                    ny_index = data['DateTime'].dt.tz_convert(exchange_tz)
                    ny_times = ny_index.dt.time
                    open_time = datetime.time(9, 30)
                    close_time = datetime.time(16, 0)
                    # premarket < 09:30, regular 09:30-16:00, postmarket >=16:00
                    data['session'] = np.where(ny_times < open_time, 'PRE',
                                               np.where(ny_times >= close_time, 'POST', 'REG'))
                except Exception as e:
                    print('Could not set session column:', e)

            data.set_index(keys='DateTime', inplace=True)
            data.sort_index(ascending=True, inplace=True)
            #data['Volume'] = data['Volume'].astype(float).astype(int)
            #data['VWAP'] = data['VWAP'].astype(float)
            #data['Open'] = data['Open'].astype(float)
            #data['Close'] = data['Close'].astype(float)
            #data['High'] = data['High'].astype(float)
            #data['Low'] = data['Low'].astype(float)
            #data['Trades'] = data['Trades'].astype(int)

        return data
            
    def groupedBy(self, date:str, adjusted:bool=False, include_otc:bool=True,
                   version:str='/v2', df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get the daily open, high, low, and close (OHLC) for the entire 
        stocks/equities markets.

        Parameters
        ----------
        date: str
            Date till which to get data. Either a date with the format 
            YYYY-MM-DD or a millisecond timestamp.
        adjusted: bool
            Whether or not the results are adjusted for splits. By default, 
            results are not adjusted. Set this to true to get results that 
            are adjusted for splits.
        inclued_otc: bool
            Include OTC securities in the response. Default is True 
            (don't include OTC securities).
        version: str
            Name of the version of the API to call.
        df: bool
            Return data as DataFrame.

        Returns
        -------
        data: dict | pd.DataFrame
            Contains the requested data.
        '''

        params: dict = {'adjusted': adjusted, 'include_otc': include_otc}
        url: str = self.BASE_URL+version+f'/aggs/grouped/locale/us/market/stocks' + \
                                   f'/{date}'
        
        data: (list | dict) = self._request(url=url, params=params)
        
        if df:
            data: pd.DataFrame = pd.DataFrame(data['results']) \
                    if 'results' in data else pd.DataFrame(data)
            data.rename(columns={'v':'Volume','vw':'VWAP','o':'Open',
                                 'c':'Close','h':'High','l':'Low',
                                 't':'DateTime','n':'Trades','T':'Symbol',
                                 'otc':'OTC'}, inplace=True)
            data['DateTime'] = pd.to_datetime(data['DateTime'], unit='ms')
            data.set_index(keys='DateTime', inplace=True)
            data['OTC'].fillna(False, inplace=True)
            #data['Volume'] = data['Volume'].astype(float).astype(int)
            #data['VWAP'] = data['VWAP'].astype(float)
            #data['Open'] = data['Open'].astype(float)
            #data['Close'] = data['Close'].astype(float)
            #data['High'] = data['High'].astype(float)
            #data['Low'] = data['Low'].astype(float)
            #data['Trades'] = data['Trades'].astype(int)
            #data['Symbol'] = data['Symbol'].astype(str)

        return data

    def dailyCandle(self, symbol:str, date:str, adjusted:bool=False,
                   version:str='/v1', df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get the open, high, low, close, premarket close and 
        afterhours close prices of a stock symbol on a certain date.

        Parameters
        ----------
        symbol: str
            The ticker symbol of the stock/equity.
        date: str
            Date till which to get data. Either a date with the format 
            YYYY-MM-DD or a millisecond timestamp.
        adjusted: bool
            Whether or not the results are adjusted for splits. By default, 
            results are not adjusted. Set this to true to get results that 
            are adjusted for splits.
        version: str
            Name of the version of the API to call.
        df: bool
            Return data as DataFrame.

        Returns
        -------
        data: dict | pd.DataFrame
            Contains the requested data.
        '''

        params: dict = {'adjusted': adjusted}
        url: str = self.BASE_URL+version+f'/open-close/{symbol}/{date}'
        
        data: (list | dict) = self._request(url=url, params=params)
        
        if df:
            data: pd.DataFrame = pd.DataFrame(data['results']) \
                    if 'results' in data else pd.DataFrame(data)
            data.rename(columns={'afterHours':'AH','close':'Close',
                                 'open':'Open','high':'High','low':'Low',
                                 'from':'DateTime','preMarket':'PM',
                                 'symbol':'Symbol','volume':'Volume'}, inplace=True)
            data['DateTime'] = pd.to_datetime(data['DateTime'])
            data.set_index(keys='DateTime', inplace=True)
        
        return data

    def prevDailyCandle(self, symbol:str, adjusted:bool=False,
                   version:str='/v2', df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get the previous day's open, high, low, and close (OHLC) 
        for the specified stock ticker.

        Parameters
        ----------
        symbol: str
            The ticker symbol of the stock/equity.
        adjusted: bool
            Whether or not the results are adjusted for splits. By default, 
            results are not adjusted. Set this to true to get results that 
            are adjusted for splits.
        version: str
            Name of the version of the API to call.
        df: bool
            Return data as DataFrame.

        Returns
        -------
        data: dict | pd.DataFrame
            Contains the requested data.
        '''

        params: dict = {'adjusted': adjusted}
        url: str = self.BASE_URL+version+f'/aggs/ticker/{symbol}/prev'
        
        data: (list | dict) = self._request(url=url, params=params)
        
        if df:
            data: pd.DataFrame = pd.DataFrame(data['results']) \
                    if 'results' in data else pd.DataFrame(data)
            data.rename(columns={'v':'Volume','vw':'VWAP','o':'Open',
                                 'c':'Close','h':'High','l':'Low',
                                 't':'DateTime','n':'Trades','T':'Symbol'}, inplace=True)
            data['DateTime'] = pd.to_datetime(data['DateTime'], unit='ms')
            data.set_index(keys='DateTime', inplace=True)
        
        return data

    def trades(self, symbol:str, date:str, order:str='asc', sort:str='timestamp',
                limit:int=5000, version:str='/v3', df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get the trades for the specified stock ticker.

        Parameters
        ----------
        symbol: str
            The ticker symbol of the stock/equity.
        date: str
            Date for which to get data. Either a date with the format 
            YYYY-MM-DD or a millisecond timestamp.
        order: str
            Sort the results by sort filed. 'asc' will return results in 
            ascending order (oldest at the top), 'desc' will return results 
            in descending order (newest at the top). Default is 'asc'.
        sort:str
            Sort field used for ordering.
        limit:int
            Limits the number of base aggregates queried to create the 
            aggregate results. Max 50000 and Default 5000.
        version: str
            Name of the version of the API to call.
        df: bool
            Return data as DataFrame.

        Returns
        -------
        data: dict | pd.DataFrame
            Contains the requested data.
        '''
        
        params: dict = {'timestamp': date, 'order': order, 'limit': limit, 'sort': sort}
        url: str = self.BASE_URL+version+f'/trades/{symbol}'
        
        data: (list | dict) = self._request(url=url, params=params)
        
        if df:
            data: pd.DataFrame = pd.DataFrame(data['results']) \
                    if 'results' in data else pd.DataFrame(data)
            data.rename(columns={'exchange':'Exchange','price':'Price',
                                 'DateTime':'sip_timestamp',
                                 'size':'Volume'}, inplace=True)
            if 'DateTime' not in data:
                raise(ValueError)
            data['DateTime'] = pd.to_datetime(data['DateTime'], unit='ms')
            data.set_index(keys='DateTime', inplace=True)
        
        return data
    
    def lastTrade(self, symbol:str, version:str='/v2', df:bool=True
                  ) -> (dict | pd.DataFrame):

        '''
        Get the last trade for the specified stock ticker.

        Parameters
        ----------
        symbol: str
            The ticker symbol of the stock/equity.
        version: str
            Name of the version of the API to call.
        df: bool
            Return data as DataFrame.

        Returns
        -------
        data: dict | pd.DataFrame
            Contains the requested data.
        '''
        
        url: str = self.BASE_URL+version+f'/last/trade/{symbol}'
        
        data: (list | dict) = self._request(url=url)
        
        if df:
            data: pd.DataFrame = pd.DataFrame(data['results']) \
                    if 'results' in data else pd.DataFrame(data)
            # data.rename(columns={'exchange':'Exchange','price':'Price',
            #                      'DateTime':'sip_timestamp',
            #                      'size':'Volume'}, inplace=True)
            # if 'DateTime' not in data:
            #     raise(ValueError)
            # data['DateTime'] = pd.to_datetime(data['DateTime'], unit='ms')
            # data.set_index(keys='DateTime', inplace=True)
        
        return data
    
    def quotes(self, symbol:str, date:str, order:str='asc', sort:str='timestamp',
                limit:int=5000, version:str='/v3', df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get NBBO quotes for a ticker symbol in a given time range.

        Parameters
        ----------
        symbol: str
            The ticker symbol of the stock/equity.
        date: str
            Date till which to get data. Either a date with the format 
            YYYY-MM-DD or a millisecond timestamp.
        order: str
            Sort the results by sort filed. 'asc' will return results in 
            ascending order (oldest at the top), 'desc' will return results 
            in descending order (newest at the top). Default is 'asc'.
        sort:str
            Sort field used for ordering.
        limit:int
            Limits the number of base aggregates queried to create the 
            aggregate results. Max 50000 and Default 5000.
        version: str
            Name of the version of the API to call.
        df: bool
            Return data as DataFrame.

        Returns
        -------
        data: dict | pd.DataFrame
            Contains the requested data.
        '''
        
        params: dict = {'timestamp': date, 'order': order, 'limit': limit, 
                        'sort': sort}
        url: str = self.BASE_URL+version+f'/quotes/{symbol}'
        
        data: (list | dict) = self._request(url=url, params=params)
        
        if df:
            data: pd.DataFrame = pd.DataFrame(data['results']) \
                    if 'results' in data else pd.DataFrame(data)
            data.rename(columns={'exchange':'Exchange','price':'Price',
                                 'DateTime':'sip_timestamp',
                                 'size':'Volume'}, inplace=True)
            if 'DateTime' not in data:
                raise(ValueError)
            data['DateTime'] = pd.to_datetime(data['DateTime'], unit='ms')
            data.set_index(keys='DateTime', inplace=True)
        
        return data
    
    def snapshot(self, symbol:str, include_otc:bool=True, version:str='/v2', 
                 df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get the most up-to-date market data for several tickers.

        Note: Snapshot data is cleared at 3:30am EST and gets populated as 
        data is received from the exchanges. This can happen as early as 4am 
        EST.

        Parameters
        ----------
        symbol: str
            A comma separated list of tickers to get snapshots for.
        inclued_otc: bool
            Include OTC securities in the response. Default is True 
            (don't include OTC securities).
        version: str
            Name of the version of the API to call.
        df: bool
            Return data as DataFrame.

        Returns
        -------
        data: dict | pd.DataFrame
            Contains the requested data.
        '''
        
        include_otc: str = 'true' if include_otc else 'false'
        params: dict = {'tickers': symbol, 'include_otc': include_otc}
        url: str = self.BASE_URL+version+f'/snapshot/locale/us/markets/stocks/tickers'
        
        data: (list | dict) = self._request(url=url, params=params)
        
        if df:
            data: pd.DataFrame = pd.DataFrame(data['results']) \
                    if 'results' in data else pd.DataFrame(data)
            # data.rename(columns={'exchange':'Exchange','price':'Price',
            #                      'DateTime':'sip_timestamp',
            #                      'size':'Volume'}, inplace=True)
            # if 'DateTime' not in data:
            #     raise(ValueError)
            # data['DateTime'] = pd.to_datetime(data['DateTime'], unit='ms')
            # data.set_index(keys='DateTime', inplace=True)
        
        return data
    
    def gainersLosers(self, direction:str, include_otc:bool=True, version:str='/v2', 
                 df:bool=True) -> (dict | pd.DataFrame):

        '''
        Get the most up-to-date market data for the current top 20 gainers or 
        losers of the day in the stocks/equities markets.

        Top gainers are those tickers whose price has increased by the highest 
        percentage since the previous day's close. Top losers are those tickers 
        whose price has decreased by the highest percentage since the previous 
        day's close.

        Note: Snapshot data is cleared at 3:30am EST and gets populated as data 
        is received from the exchanges.

        Parameters
        ----------
        direction: str
            The direction of the snapshot results to return. 
            Can be gainers or losers.
        inclued_otc: bool
            Include OTC securities in the response. Default is True 
            (don't include OTC securities).
        version: str
            Name of the version of the API to call.
        df: bool
            Return data as DataFrame.

        Returns
        -------
        data: dict | pd.DataFrame
            Contains the requested data.
        '''
        
        include_otc: str = 'true' if include_otc else 'false'
        params: dict = {'include_otc': include_otc}
        url: str = self.BASE_URL+version+f'/snapshot/locale/us/markets/stocks' + \
                                    f'/{direction}'
        
        data: (list | dict) = self._request(url=url, params=params)
        if df:
            columns: dict = {'o':'Open','h':'High','l':'Low','c':'Close',
                       't':'DateTime', 'av':' Average', 'v': 'Volume',
                       'vw': 'VWAP'}
            if 'tickers' in data:
                temp: list = []
                for d in data['tickers']:
                    tdict: dict = {
                        'ticker': d['ticker'],
                        'todaysChangePerc': d['todaysChangePerc'],
                        'todaysChange': d['todaysChange'],
                        'updated': d['updated'],
                    }
                    print(d)
                    for k in ['day','min','prevDay']:
                        for t in d[k]:
                            tdict[k+columns[t]] = d[k][t]
                    temp.append(tdict)
                data: pd.DataFrame = pd.DataFrame(temp)
                for c in [i for i in data.columns if 'DateTime' in i]:
                    data[c] = pd.to_datetime(data[c], unit='ms')
            else:
                data: pd.DataFrame = pd.DataFrame(data)
        
        return data

    def snapshotTicker(self, symbol:str, version:str='/v2', df:bool=True
                       ) -> (dict | pd.DataFrame):

        '''
        Get the most up-to-date market data for a single traded stock ticker.

        Note: Snapshot data is cleared at 3:30am EST and gets populated as 
        data is received from the exchanges. This can happen as early as 4am 
        EST.

        Parameters
        ----------
        symbol: str
            The ticker symbol of the stock/equity.
        version: str
            Name of the version of the API to call.
        df: bool
            Return data as DataFrame.

        Returns
        -------
        data: dict | pd.DataFrame
            Contains the requested data.
        '''
        
        include_otc: str = 'true' if include_otc else 'false'
        url: str = self.BASE_URL+version+f'/snapshot/locale/us/markets/stocks/tickers' + \
                                    f'/{symbol}'
        
        data: (list | dict) = self._request(url=url)
        
        if df:
            data: pd.DataFrame = pd.DataFrame(data['results']) \
                    if 'results' in data else pd.DataFrame(data)
            # data.rename(columns={'exchange':'Exchange','price':'Price',
            #                      'DateTime':'sip_timestamp',
            #                      'size':'Volume'}, inplace=True)
            # if 'DateTime' not in data:
            #     raise(ValueError)
            # data['DateTime'] = pd.to_datetime(data['DateTime'], unit='ms')
            # data.set_index(keys='DateTime', inplace=True)
        
        return data
    


if __name__ == '__main__':

    pol = Massive('cUlHULSDVdLm9Up1TsKxF3RU2dEKm3nq', free=True)
    data = pol.aggregates('AAPL',1,'minute',(datetime.datetime.now() - datetime.timedelta(days=4)).strftime('%Y-%m-%d'),datetime.datetime.now().strftime('%Y-%m-%d'))
    # data = pol.gainersLosers('gainers')
    print(data)