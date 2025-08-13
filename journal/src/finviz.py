
import datetime as dt
from random import choice

import certifi
import numpy as np
import pandas as pd
import urllib3
import requests
from bs4 import BeautifulSoup

import locale

# Guardar locale actual
locale_actual = locale.getlocale(locale.LC_TIME)

# Establecer locale en inglés
try:
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')  # Unix/Mac
except:
    locale.setlocale(locale.LC_TIME, 'English_United States.1252')  # Windows

class FinvizError(Exception):
    
    '''
    Class to raise custom errors.
    '''

    def __init__(self, message=''):
        self.message = message
        super().__init__(self.message)

class FinvizBase:

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

    # URLs and endpoints used
    BASE_URL: str = 'https://finviz.com'
    SCREENER_EP: str = '/screener.ashx?v=111&ft=4&o=-change&f='
    TICKER_EP: str = '/quote.ashx?ty=c&p=d&b=1&t='
    GROUPS_EP: str = '/groups.ashx?v=140&o=-change'

    def __init__(self, random_headers:bool=True) -> None:
        self.random_headers: bool = random_headers

    def _toNumeric(self, string:str) -> (int | float):

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
        if '(' in string and ')' in string:
            string = '-'+string.replace('(','').replace(')', '')
        if '-' == string:
            return 0

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
        
    def _randomHeader(self) -> dict:

        '''
        This function selects a random User-Agent from the User-Agent list. 
        User-Agents are used in order to avoid the limitations of the requests 
        to Finviz.com. The User-Agent is specified on the headers of the 
        requests and is different for every request.
        '''

        self.header: dict = {'User-Agent': choice(self.USER_AGENTS)}

        return self.header

    def _request_old(self, url:str) -> BeautifulSoup:

        '''
        Makes a request with the correct header and certifications.

        Parameters
        ----------
        url: str
            String with the url from which to get the HTML.

        Returns
        -------
        soup: bs4.BeautifulSoup
            Contains the HTML of the url.
        '''

        content: urllib3.PoolManager = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                               ca_certs=certifi.where()) \
                              .urlopen('GET', url, headers=self._randomHeader() if self.random_headers else {'User-Agent': self.USER_AGENTS[0]})
        soup: BeautifulSoup = BeautifulSoup(content.data,'html.parser')

        return soup
    
    def _request(self, url: str) -> BeautifulSoup:

        try:
            response = requests.get(url, headers=self._randomHeader() if self.random_headers else {'User-Agent': self.USER_AGENTS[0]}, 
                                    timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error connecting to {url}: {e}")
            raise

class FinvizScraper(FinvizBase):

    '''
    Class used for webscraping Finviz.
    '''

    def __init__(self, random_headers = True):
        super().__init__(random_headers)

    def _getTable(self, soup:BeautifulSoup=None) -> pd.DataFrame:

        '''
        Extraction of screener table.

        Parameters
        ----------
        soup: bs4.BeautifulSoup
            HTML of a webpage.

        Returns
        -------
        table: pd.DataFrame
            Contains the screener table.
        '''
        
        soup: BeautifulSoup = self.soup if soup == None else soup
        
        table = soup.find('table', {'class':'screener_table'})
        if table:
            cols: list = [col.get_text().replace('\n', '') for col in table.find_all('th')]
            rows: list = [[a.get_text() for a in row.find_all('a')] \
                            for row in table.find_all('tr')[1:]]
            return pd.DataFrame(data=rows, columns=cols)
        else:
            return pd.DataFrame()
    
    def _getPages(self, filters:list=None) -> pd.DataFrame:

        filters: list = self.filters if filters == None else filters
        complete_data: list = []
        
        # Defining the url and connecting to obtain html 
        self.tempurl: str = f"{self.BASE_URL}{self.SCREENER_EP}{','.join(self.filters)}"
        self.soup: BeautifulSoup = self._request(self.tempurl)
        complete_data.append(self._getTable())
        page = self.soup.find('td', {'id': 'screener_pagination'})
        
        if page:
            n = float(page.find('a', {'class': 'is-selected'}).get_text()) - 1
            if n > 0:
                for i in range(1,n):
                    self.tempurl: str = f"{self.BASE_URL}{self.SCREENER_EP}\
                                        {','.join(self.filters)}&r={i*2}1"
                    self.soup: BeautifulSoup = self._request(self.tempurl)
                    complete_data.append(self._getTable())
                    
            return pd.concat(complete_data)
        else:
            return pd.DataFrame()
        
    def screener(self,exchange:list=['nyse','nasd','amex'],
                  filters:list=['cap_smallunder','sh_avgvol_o500','sh_outstanding_u50',
                                'sh_price_u10','sh_relvol_o3'],
                  minpctchange:float=None, justsymbols:bool=False) -> pd.DataFrame:
      
        '''
        Function to get data from Finviz Screener based on some filters.

        Parameters
        ----------
        exchange: list
            List of selected exchanges. The options are: 'nyse', 'nasd' and 
            'amex'.
        filters: list
            List of filters used by Finviz in their url.
        minpctchange: float
            Minimum percentage change of the symbol in case you want to 
            filter it.
        justsymbols: bool
            True to return just the symbol names. False if you want all 
            the default data offered from the symbol by Finviz.

        Returns
        -------
        screener_df: pd.DataFrame
            DataFrame containing the screener.
        '''

        # Variables
        self.minpctchange = minpctchange
        self.justsymbols = justsymbols
        
        minpctchange = self.minpctchange if minpctchange == None else minpctchange
        
        # Getting data
        if len(exchange) == 0:
            self.filters: list = filters
            self.screener_df: pd.DataFrame = self._getPages(filters=filters)

        else:
            temp_data: list = []
            for ex in exchange:
                self.filters: list = ['exch_'+ex]+filters
                temp: pd.DataFrame = self._getPages(filters=['exch_'+ex]+filters)
                temp['Exchange'] = ex
                temp_data.append(temp.copy())
                            
            self.screener_df: pd.DataFrame = pd.concat(temp_data, ignore_index=True)

        self.screener_df.drop(columns=['No.'], inplace=True)
        self.screener_df.drop_duplicates(inplace=True)
        self.screener_df['Market Cap'] = self.screener_df['Market Cap'].apply(lambda x: self._toNumeric('nan' if x == '-' else x))
        self.screener_df['P/E'] = self.screener_df['P/E'].apply(lambda x: self._toNumeric('nan' if x == '-' else x))
        self.screener_df['Price'] = self.screener_df['Price'].astype(float)
        self.screener_df['Change'] = self.screener_df['Change'].apply(lambda x: self._toNumeric(x.replace('%', ''))/100)
        self.screener_df['Volume'] = self.screener_df['Volume'].str.replace(',','').astype(float)
        self.screener_df: pd.DateFrame = self.screener_df[self.screener_df['Change'] >= minpctchange/100]
        
        return self.screener_df

    def symbolInfo(self, symbols:list=None, df:bool=True) -> dict:

        '''
        Gets info of a list of symbols from finviz.

        Parameters
        ----------
        symbols: list
            List of symbols to look for.
        df: bool
            True to return data in dataframe format.

        Returns
        -------
        df: dict
            Contains the data of the .csv file.
        '''

        if symbols is None:
            if self.screener_df is None:
                raise FinvizError('There where no symbols selected for retrieveing their info.')
            else:
                symbols = self.screener_df
                
        if isinstance(symbols,pd.DataFrame):
            symbol_list: list = symbols['Ticker'].tolist()
        elif isinstance(symbols,str):
            symbol_list: list = [symbols]
        elif isinstance(symbols,list):
            symbol_list: list = symbols

        final_data: dict = {} 
        for symbol in symbol_list:

            final_data[symbol] = FinvizTicker(symbol=symbol).info(df=df)

        return final_data

    def hotSectors(self, column:str='%Week', df:bool=True) -> (dict | pd.DataFrame):

        '''
        Function for extracting the sectors sorted.

        Parameters
        ----------
        column: str
            Column to sort by the sectors. Choose from: %Week, %Month, 
            %Quart, %Half, %Year, %YTD, %Change
        df: bool
            True to return data in dataframe format.

        Returns
        -------
        df: dict | pd.DataFrame
            Contains the data.
        '''
        url: str = self.BASE_URL + self.GROUPS_EP + '&g=sector'
        soup: BeautifulSoup = self._request(url)
        table = soup.find('table', {'class': 'groups_table'})

        # Columns
        columns: list = []
        columns_temp: list = [j.get_text().replace('\n', '') for j in table.find_all('th')]
        for c in columns_temp:
            if 'Perf' in c:
                c: str = c.replace('Perf ','%')
            elif 'Change' in c:
                c: str = '%'+c
            columns.append(c)

        # Rows
        rows: list = []
        rows_temp: set = table.find_all('tr')[1:]
        for r in rows_temp:
            data: list = []
            data_temp = r.find_all('td')
            for d in data_temp:
                d: str = d.get_text()
                if d[0].isnumeric() or d[1].isnumeric():
                    d = self._toNumeric(d)
                data.append(d)                
            rows.append(data)

        # Dataframe
        data_df: pd.DataFrame = pd.DataFrame(rows,columns=columns)
        data_df.sort_values(column,ascending=False,inplace=True)
        data_df.reset_index()
        if 'No.' in data_df.columns:
            data_df.drop(columns=['No.'], inplace=True)

        return data_df if df else data_df.to_dict('records')

    def hotIndustry(self,column:str='%Week', df:bool=True) -> (dict | pd.DataFrame):

        '''
        Function for extracting the industries sorted.

        Parameters
        ----------
        column: str
            Column to sort by the industries. Choose from: %Week, %Month, 
            %Quart, %Half, %Year, %YTD, %Change
        df: bool
            True to return data in dataframe format.

        Returns
        -------
        df: dict | pd.DataFrame
            Contains the data.
        '''
        url: str = self.BASE_URL + self.GROUPS_EP + '&g=industry'
        soup: BeautifulSoup = self._request(url)
        table = soup.find('table', {'class': 'groups_table'})

        # Columns
        columns: list = []
        columns_temp: list = [j.get_text().replace('\n', '') for j in table.find_all('th')]
        for c in columns_temp:
            if 'Perf' in c:
                c = c.replace('Perf ','%')
            elif 'Change' in c:
                c = '%'+c
            columns.append(c)

        # Rows
        rows: list = []
        rows_temp: set = table.find_all('tr')[1:]
        for r in rows_temp:
            data: list = []
            data_temp = r.find_all('td')
            for d in data_temp:
                d: str = d.get_text()
                if d[0].isnumeric() or d[1].isnumeric():
                    d = self._toNumeric(d)
                data.append(d)                
            rows.append(data)

        # Dataframe
        data_df = pd.DataFrame(rows,columns=columns)
        data_df.sort_values(column,ascending=False,inplace=True)
        data_df.reset_index()
        if 'No.' in data_df.columns:
            data_df.drop(columns=['No.'], inplace=True)

        return data_df if df else data_df.to_dict('records')

class FinvizTicker(FinvizBase):

    symbol = None

    def __init__(self, symbol:str, random_headers = True):
        super().__init__(random_headers)
        self._newSymbol(symbol=symbol)
      
    def _newSymbol(self, symbol:str=None) -> BeautifulSoup:
        
        if (symbol is not None and symbol is not self.symbol):
            
            self.url: str = self.BASE_URL + self.TICKER_EP + symbol
            self.symbol: str = symbol
                
            self.soup: BeautifulSoup = self._request(self.url)
            if len(self.soup) <= 0:
                raise(FinvizError(f"There was an error. Could not get the page soup"))

        elif self.symbol == None:
            raise(FinvizError(f"There is no symbol. Please enter a valid symbol."))
        
        return self.soup

    def company(self, symbol:str=None) -> dict:

        '''
        Gets company info from a symbol in finviz.

        Parameters
        ----------
        symbol: str
            Ticker for which to extract the company data. If it is not None the 
            HTML will be overwritten with one for this symbol.

        Returns
        -------
        company_info: dict
            Contains the data for the company.
        '''

        if symbol != None:
            soup: BeautifulSoup = self._newSymbol(symbol)
        elif self.soup == None and symbol == None:
            raise(FinvizError('Soup or symbol must be entered!'))
        else:
            soup = self.soup


        # Get company info
        sources: dict = self.sources()
        header = soup.find('div', {'class': 'quote-header_left'})
        details = soup.find('div', {'class': 'quote-links'}).find('div').find_all('a')
                        
        company_info: dict = {
            'Symbol': header.find('h1')['data-ticker'],
            'Exchange': details[3].get_text(),
            'Company': header.find('a').get_text().replace('\n', '') \
                            .replace('\r', '').replace('  ', ''),
            'Web': header.find('a')['href'],
            'Sector': details[0].get_text(),
            'Industry': details[1].get_text(),
            'Country': details[2].get_text(),
            'Description': soup.find_all('td', {'class':'fullview-profile'})[0] \
                              .get_text(),
            'CIK': int(sources['EDGAR'].split('=')[-1].zfill(10)) \
                    if 'EDGAR' in sources else float('nan'),
        }

        return company_info

    def data(self, symbol:str=None) -> dict:

        '''
        Gets key data from a symbol in finviz.

        Parameters
        ----------
        symbol: str
            Ticker for which to extract the key metrics. If is not None the 
            HTML will be overwritten with one for this symbol.

        Returns
        -------
        main_data: dict
            Contains the key data for the symbol.
        '''

        if symbol != None:
            soup: BeautifulSoup = self._newSymbol(symbol)
        elif self.soup == None and symbol == None:
            raise(FinvizError('Soup or symbol must be entered!'))
        else:
            soup = self.soup

        main_data: dict = {
            group['keys'][i]: (group['values'][i] if group['values'][i] != '-' else 'nan') for group in 
                [{'keys': [v.get_text() for v in row.find_all('td') if 'w-[7%]' in v.get('class', [])], 
                'values':[v.get_text() for v in row.find_all('td') if 'w-[8%]' in v.get('class', [])]} \
                for row in soup.find('table', {'class': 'snapshot-table2'}).find_all('tr')] \
            for i in  range(len(group['keys']))
        }
        
        data: dict = {}
        for key in main_data:
            if ' / ' in main_data[key]:
                data[key.split('/')[0].strip()] = main_data[key].split('/')[0].strip()
                data[key.split('/')[1].strip()] = main_data[key].split('/')[1].strip()
            elif ' - ' in main_data[key]:
                data[key+' Low'] = main_data[key].split(' - ')[0]
                data[key+' High'] = main_data[key].split(' - ')[1]
            elif ' ' in main_data[key] and key not in ['Earnings', 'Index', 'IPO'] and 'date' not in key.lower():
                data[key+' Low'] = main_data[key].split(' ')[0]
                data[key+' High'] = main_data[key].split(' ')[1]
            else:
                data[key] = main_data[key]
        
        main_data: dict = {}
        for key in data:
            if '%' in data[key]:
                main_data[key+' Pct'] = self._toNumeric(data[key].replace('%',''))
            elif data[key] == 'Yes':
                main_data[key] = True
            elif data[key] == 'No':
                main_data[key] = False
            elif key == 'Earnings':
                main_data[key] = data[key].replace('AMC', 'After Market Close') \
                                          .replace('BMC', 'Before Market Close') 
            elif key == 'Index':
                main_data[key] = data[key].split(', ')
            elif key == 'IPO' or 'date' in key.lower():
                main_data[key] = data[key]
            elif data[key].strip() == '':
                main_data[key] = ''
            else:
                main_data[key] = self._toNumeric(data[key].strip())
        
        return main_data

    def news(self, symbol:str=None, df:bool=False) -> (list | pd.DataFrame):

        '''
        Gets news from a symbol in finviz.

        Parameters
        ----------
        symbol: str
            Ticker for which to extract the news. If is not None the 
            HTML will be overwritten with one for this symbol.
        df: bool
            True to return data in DataFrame.

        Returns
        -------
        news: list | pd.DataFrame
            Contains the news for the symbol.
        '''

        if symbol != None:
            soup: BeautifulSoup = self._newSymbol(symbol)
        elif self.soup == None and symbol == None:
            raise(FinvizError('Soup or symbol must be entered!'))
        else:
            soup = self.soup
        
        table = soup.find('table', {'class': 'news-table'})
        news: list = [
            {'Date':row.find('td').get_text().replace('\n', '') \
                    .replace('\r', '').replace('  ', ''), 
            'Header':row.find('a').get_text(), 'Source':row.find('span').get_text(), 
            'URL':row.find('a')['href']} \
            for row in table.find_all('tr')
        ]
        
        prev_date = None
        news_data: list = []
        for p in news:
            temp_date: str = p['Date']
            if 'Today' in temp_date:
                temp_date = dt.datetime.today().strftime('%b-%d-%y') + ' ' + temp_date.split(' ')[-1]
            elif '-' not in temp_date:
                temp_date = prev_date + ' ' + temp_date
            temp_date: dt.datetime = dt.datetime.strptime(temp_date,'%b-%d-%y %I:%M%p')

            news_data.append({
                'Date': temp_date.strftime('%Y-%m-%d %H:%M:%S'),
                'Header': p['Header'],
                'Source': p['Source'],
                'URL': p['URL'],
            })
            prev_date: str = temp_date.strftime('%b-%d-%y')

        if df:
            news: pd.DataFrame = pd.DataFrame(news_data)
            # Set timezone awareness
            if 'Date' in news:
                news['Date'] = pd.to_datetime(news['Date'], 
                                              format='%Y-%m-%d %H:%M:%S')
                news.set_index('Date', drop=True, inplace=True)
                news.index = news.index.tz_localize(
                                        tz=dt.datetime.now(dt.timezone.utc) \
                                            .astimezone().tzinfo)
        else:
            news: list = news_data
        
        return news

    def insiders(self, symbol:str=None, df:bool=False) -> (list | pd.DataFrame):

        '''
        Gets insiders transactions from a symbol in finviz.

        Parameters
        ----------
        symbol: str
            Ticker for which to extract the insiders transactions. If is not 
            None the HTML will be overwritten with one for this symbol.
        df: bool
            True to return data in DataFrame.

        Returns
        -------
        insiders: list | pd.DataFrame
            Contains the insiders transactions for the symbol.
        '''

        if symbol != None:
            soup: BeautifulSoup = self._newSymbol(symbol)
        elif self.soup == None and symbol == None:
            raise(FinvizError('Soup or symbol must be entered!'))
        else:
            soup = self.soup
        
        table = soup.find_all('table', {'class':'body-table'})
        
        if len(table) > 0:
            insiders = table[0]

            head: list = [j.get_text() for j in insiders.find_all('th')]
            urls: list = [i.find_all('a')[-1]['href'] for i in insiders.find_all('tr')[1:]]
            insiders: list = [[j.get_text() for j in i.find_all('td')] \
                                for i in insiders.find_all('tr')[1:]]

            insiders: pd.DataFrame = pd.DataFrame(data=insiders, columns=head)
            insiders['Date'] = pd.to_datetime(insiders['Date'].str.strip(), errors='coerce')
            insiders['Cost'] = insiders['Cost'].astype(float)
            insiders['#Shares'] = insiders['#Shares'].str.replace(',','').astype(int)
            insiders['Value ($)'] = insiders['Value ($)'].str.replace(',','').astype(float)
            insiders['#Shares Total'] = insiders['#Shares Total'].str.replace(',','').apply(lambda x: 'nan' if x == '' else x).astype(float)
            insiders['SEC Form 4'] = insiders['SEC Form 4'].apply(lambda x: 
                    f'{dt.datetime.today().year-1} {x.strip()}' \
                    if pd.to_datetime(f'{dt.datetime.today().year} {x.strip()}', errors='coerce') > dt.datetime.today() \
                    else f'{dt.datetime.today().year} {x.strip()}')
            insiders['SEC Form 4'] = pd.to_datetime(insiders['SEC Form 4'], errors='coerce')
            insiders['SEC URL'] = urls

            return insiders if df else insiders.to_dict('records')
        else:
            return pd.DataFrame() if df else []

    def sources(self, symbol:str=None) -> dict:

        '''
        Gets other source for a symbol in finviz.

        Parameters
        ----------
        symbol: str
            Ticker for which to extract the sources. If is not None the HTML 
            will be overwritten with one for this symbol.

        Returns
        -------
        main_data: dict
            Contains the sources for the symbol.
        '''

        if symbol != None:
            soup: BeautifulSoup = self._newSymbol(symbol)
        elif self.soup == None and symbol == None:
            raise(FinvizError('Soup or symbol must be entered!'))
        else:
            soup = self.soup

        references = soup.find_all('table')[-1].find_all('a')
        references: dict = {i.get_text().split(' ')[-1]: i['href'] for i in references}

        return references

    def info(self, symbol:str=None, df:bool=True) -> dict:

        '''
        Gets info of a list of symbols from finviz.

        Parameters
        ----------
        symbols: list
            List of symbols to look for.
        df: bool
            True to return data in dataframe format.

        Returns
        -------
        df: dict
            Contains the data of the .csv file.
        '''

        if symbol != None:
            soup: BeautifulSoup = self._newSymbol(symbol)
        elif self.soup == None and symbol == None:
            raise(FinvizError('Soup or symbol must be entered!'))
        
        return {
            **self.company(),
            **self.data(),
            **{ 
                'news': self.news(df=df),
                'insiders': self.insiders(df=df),
                'sources': self.sources(),
            }
        }



if __name__ == '__main__':

    if True:
        fv = FinvizTicker('AAPL')
        info = fv.info()
    else:
        fv = FinvizScraper()
        if False:
            stock_filters = ['sh_avgvol_o100','ta_gap_u20']
            screen = fv.screener(exchange=['nasd','nyse','amex'],filters=stock_filters,minpctchange=-10.,justsymbols=False)
        else:
            stock_filters = ['cap_largeunder','sh_avgvol_o1000','ta_highlow20d_b0to10h',
                            'ta_perf_4w30o','ta_sma20_pa10','ta_sma50_pa']
            screen = fv.screener(exchange=['nasd','nyse','amex'],filters=stock_filters,minpctchange=-10.,justsymbols=False)
            symbol = 'AAPL' #screen['Ticker'].iloc[0]
            #data = fv.symbolInfo([symbol])
            #sectors = fv.hotSectors()
            industries = fv.hotIndustry()
            #print(data)