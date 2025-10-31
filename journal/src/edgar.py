
import time
from random import choice
from itertools import chain

from curl_cffi import requests
from requests.adapters import HTTPAdapter, Retry
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

import pandas as pd

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
        
def randomHeader(headers: dict[str, str]) -> dict[str, str]:

    '''
    This function selects a random User-Agent from the User-Agent list. 
    User-Agents are used in order to avoid the limitations of the requests 
    to Finviz.com. The User-Agent is specified on the headers of the 
    requests and is different for every request.
    '''

    return {**{k.lower(): v for k, v in headers.items()}, **{'user-agent': choice(USER_AGENTS)}}

class EdgarAPIError(Exception):
    """SEC EDGAR API error."""
    
class Edgar:
    _BASE_URL_SEC_API = "https://data.sec.gov"
    _BASE_URL_XBRL = f"{_BASE_URL_SEC_API}/api/xbrl"

    # SEC API endpoints as documented here:
    # https://www.sec.gov/edgar/sec-api-documentation
    BASE_URL_SUBMISSIONS = f"{_BASE_URL_SEC_API}/submissions"
    BASE_URL_XBRL_COMPANY_CONCEPTS = f"{_BASE_URL_XBRL}/companyconcept"
    BASE_URL_XBRL_COMPANY_FACTS = f"{_BASE_URL_XBRL}/companyfacts"
    BASE_URL_XBRL_FRAMES = f"{_BASE_URL_XBRL}/frames"

    MAX_REQUESTS_PER_SECOND = 10
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 1 / MAX_REQUESTS_PER_SECOND

    def __init__(self, random_headers:bool=True) -> None:
        self.random_headers: bool = random_headers
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
                "Accept-Encoding": "gzip, deflate",
                "Host": "data.sec.gov",
            }
        )
        retries = Retry(
            total= self.MAX_RETRIES,
            backoff_factor= self.BACKOFF_FACTOR,
            status_forcelist= [408, 425, 429, 500, 502, 503, 504],
        )
        # self._session.mount("http://", HTTPAdapter(max_retries=retries))
        # self._session.mount("https://", HTTPAdapter(max_retries=retries))
    
    def validate_cik(self, cik: str) -> str:
        cik = str(cik).strip().zfill(10)

        if not self.is_cik(cik):
            raise ValueError(
                "Invalid CIK. Please enter an valid SEC CIK at most 10 digits long."
            )

        return cik

    def is_cik(self, cik: str) -> bool:
        try:
            int(cik)
            return 1 <= len(cik) <= 10
        except ValueError:
            return False

    def merge_submission_dicts(self, to_merge: list[dict[str, list[str]]]) -> dict[str, list[str]]:
        """Merge dictionaries with same keys."""
        return {k: list(chain.from_iterable(d[k] for d in to_merge)) for k in to_merge[0].keys()}

    def _get(self, url: str) -> dict:
        """Make a rate-limited GET request.

        SEC limits users to a maximum of 10 requests per second.
        Source: https://www.sec.gov/developer
        """
        if self.random_headers:
            self._session.headers.update(randomHeader(headers={"Accept-Encoding": "gzip, deflate", "Host": "data.sec.gov"}))
            
        resp = self._session.get(url)
        try:
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise EdgarAPIError(
                f"An error occurred with the SEC EDGAR API: {e}"
            ) from None
        return resp.json()
    
    def get_submissions(self, cik: str, *, handle_pagination: bool = True) -> dict:
        """Get submissions for a specified CIK. Requests data from the
        data.sec.gov/submissions API endpoint. Full API documentation:
        https://www.sec.gov/edgar/sec-api-documentation.

        :param cik: CIK to obtain submissions for.
        :param handle_pagination: whether to automatically handle API pagination,
            defaults to True. By default, 1000 submissions are included and the
            response specified the next set of filenames to request to get the next
            batch of submissions (each page contains 1000 submissions). If this is
            set to True, requests to the paginated resources will be completed
            automatically and the results will be concatenated to the recent filings key.
            If a raw response is preferred for manual pagination handling, set this
            value to false.
        :return: JSON response from the data.sec.gov/submissions/ API endpoint
            for the specified CIK.
        """
        cik = self.validate_cik(cik)
        api_endpoint = f"{self.BASE_URL_SUBMISSIONS}/CIK{cik}.json"
        submissions = self._get(api_endpoint)

        filings = submissions["filings"]
        paginated_submissions = filings["files"]

        # Handle pagination for a large number of requests
        if handle_pagination and paginated_submissions:
            to_merge = [filings["recent"]]
            for submission in paginated_submissions:
                filename = submission["name"]
                api_endpoint = f"{self.BASE_URL_SUBMISSIONS}/{filename}"
                resp = self._get(api_endpoint)
                to_merge.append(resp)

            # Merge all paginated submissions from files key into recent
            # and clear files list.
            filings["recent"] = self.merge_submission_dicts(to_merge)
            filings["files"] = []

        return submissions

    def get_company_concept(
        self,
        cik: str,
        taxonomy: str,
        tag: str,
    ) -> dict:
        """Get company concepts for a specified CIK. Requests data from the
        data.sec.gov/api/xbrl/companyconcept/ API endpoint. Returns all
        the XBRL disclosures for a single company (CIK) and concept (taxonomy and
        tag), with a separate array of facts for each unit of measure that the
        company has chosen to disclose (e.g. net profits reported in U.S. dollars
        and in Canadian dollars). Full API documentation:
        https://www.sec.gov/edgar/sec-api-documentation.

        :param cik: CIK to obtain company concepts for.
        :param taxonomy: reporting taxonomy (e.g. us-gaap, ifrs-full, dei, srt).
            More info: https://www.sec.gov/info/edgar/edgartaxonomies.shtml.
        :param tag: reporting tag (e.g. AccountsPayableCurrent).
        :return: JSON response from the data.sec.gov/api/xbrl/companyconcept/
            API endpoint for the specified CIK.
        """
        cik = self.validate_cik(cik)
        api_endpoint = (
            f"{self.BASE_URL_XBRL_COMPANY_CONCEPTS}/CIK{cik}/{taxonomy}/{tag}.json"
        )
        return self._get(api_endpoint)

    def get_company_facts(self, cik: str) -> dict:
        """Get all company concepts for a specified CIK. Requests data from the
        data.sec.gov/api/xbrl/companyfacts/ API endpoint. Full API documentation:
        https://www.sec.gov/edgar/sec-api-documentation.

        :param cik: CIK to obtain company concepts for.
        :return: JSON response from the data.sec.gov/api/xbrl/companyfacts/
            API endpoint for the specified CIK.
        """
        cik = self.validate_cik(cik)
        api_endpoint = f"{self.BASE_URL_XBRL_COMPANY_FACTS}/CIK{cik}.json"
        return self._get(api_endpoint)

    def get_frames(
        self,
        taxonomy: str,
        tag: str,
        unit: str,
        year: str,
        quarter: int | str | None = None,
        instantaneous: bool = True,
    ) -> dict:
        """Get all aggregated company facts for a specified taxonomy and tag in the specified
        calendar period. Requests data from the data.sec.gov/api/xbrl/frames/ API endpoint.
        Supports for annual, quarterly and instantaneous data. Example:
        us-gaap / AccountsPayableCurrent / USD / CY2019Q1I.
        Full API documentation: https://www.sec.gov/edgar/sec-api-documentation.

        :param taxonomy: reporting taxonomy (e.g. us-gaap, ifrs-full, dei, srt).
            More info: https://www.sec.gov/info/edgar/edgartaxonomies.shtml.
        :param tag: reporting tag (e.g. AccountsPayableCurrent).
        :param unit: unit of measure specified in the XBRL (e.g. USD).
        :param year: calendar period year.
        :param quarter: calendar period quarter, optional. Defaults to whole year.
        :param instantaneous: whether to request instantaneous data, defaults to True.
        :return: JSON response from the data.sec.gov/api/xbrl/frames/ API endpoint.
        """
        _quarter = (
            f"Q{quarter}" if quarter is not None and 1 <= int(quarter) <= 4 else ""
        )
        _instantaneous = "I" if instantaneous else ""
        period = f"CY{year}{_quarter}{_instantaneous}"
        api_endpoint = f"{self.BASE_URL_XBRL_FRAMES}/{taxonomy}/{tag}/{unit}/{period}.json"
        return self._get(api_endpoint)



class SECFiling:

    _BASE_URL: str = 'https://www.sec.gov'
    _FILING_URL: str = f'{_BASE_URL}/Archives/edgar/data'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'es-ES,es;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'cookie': 'nmstat=e9944893-37c0-c0bd-5494-034742740747; ak_bmsc=11A60AE9460B60E0456BB8AB0CE1A21D~000000000000000000000000000000~YAAQ3W1lX8ENmS+aAQAA2dbYNR3Uqngyym65VHsOafxp556qNljJ0gNw9ECZ3NORDA+b+cyF62OqJIhBoVzEKQaQAZ3pQLiy91AGcTtmOa1A0YFmA51IVz0AZYXbYL//44/xkjNjRTdbNMi8rHjjgnybN1WT9Ex0J08tajf3lQu2YV378fZnaOrR8t6nWKbtxoO8T9xYe5JFpC6WSdz+35FblR/7vwe1qykMZZYlnSJEI/uDGhKq4V//AKZb5XepbN4jgwcTeWOaxx9t/PH2tLk0dnuP7cZ7Wbde7DyJZvlMSoxmJ6QYu3zXwsU5nHmHE741sKoQBytdBKvE9JbKjIUOMVMviBf3GuFqalV8J5iBExRkG4PHR2b/C9Y+iW4c5jVUPuqQeKVC9E1dQyb+s+V/a5Phfongux3MoXpkwZzCt4efwVJaCaeofYpQcNsjtE67Ib6y7NozqqAtiV0su85aefmpEiid3MG458/LFQxwguk8; bm_sv=A3341AE43E782748A6DD4F54EBD64156~YAAQ3W1lX/fFpy+aAQAA+bgZNh2b9VLy15F0I9kIikJ+GW7B1RtkYYnY9JmXU6Ouka75Bhn7gay8xQGpDcO73h2hWfI+NeCf6JeMqG/4xwyi18k3uxyZJyQX6zFgad7kB+ow993TsIjjXaJhzBvkKZ0VUHP2SHVjsFC6l8/JpF0wdoOa675B8C293W1P/kF3rkY/FGFXJFcbT7jSaVmeo3gx6/NQ1+Ja+S6fXaGCE061mTNCUIvrFxdz4UeY~1',
        'priority': 'u=0, i',
        'referer': 'http://127.0.0.1:5000/',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    }

    def __init__(self, cik:str=None, accn:str=None, random_headers:bool=True) -> None:

        self.edgar_api = Edgar()
        self.session: requests.Session = requests.Session()
        # Declara explícitamente tu empresa y un contacto
        self.session.headers.update({
            "User-Agent": "onemade.es (dcaronm@gmail.com)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov"
        })
        
        self.cik: str = cik
        if accn is None:
            if cik is None:
                self.accn: str = None
            else:
                df = self.getApiCikFilings(cik=cik, df=True)
                self.accn: str = df[df['form'] == '10-Q'].iloc[0]['accessionNumber'].replace('-', '')
        else:
            self.accn: str = accn.replace('-', '')
        self.random_headers: bool = random_headers
        self.file: str = None
        self.filing: BeautifulSoup = None

    def _get(self, url: str, params:dict=None, accn_needed:bool=True) -> requests.Response:

        if accn_needed and self._FILING_URL in url:
            if self.cik == None:
                raise ValueError('You must pass the CIK value to the object constructor or define it after creating the object.')
            if self.accn == None:
                raise ValueError('You must pass the ACCN value to the object constructor or define it after creating the object.')
        
        #self.r: requests.Response = requests.get(url=url, params=params, headers=randomHeader(headers=self.headers) if self.random_headers else self.headers)

        time.sleep(0.6)   # <= ~1.6 req/s; sé más conservador si vas a hacer muchas peticiones
        self.r = self.session.get(url=url, params=params, timeout=30)
        self.r.raise_for_status()
        return self.r

    def _toNumeric(self, val:str) -> float | str:
        try:
            return float(val.replace(',','').replace('(','-').replace(')',''))
        except:
            return val

    def getMainFiling(self, doc_type:str='10-Q') -> str:
        r: requests.Response = self._get(f'{self._FILING_URL}/{self.cik}/{self.accn}/FilingSummary.xml')
        html = BeautifulSoup(r.content)
        self.file: str = html.find('file', {'doctype': doc_type}).get_text()
        return self.file

    def getFilingContent(self, file:str=None, html:bool=True) -> BeautifulSoup:

        file = file or self.file
        if file is None:
            file = self.getMainFiling()

        r: requests.Response = self._get(f'{self._FILING_URL}/{self.cik}/{self.accn}/{file}')
        self.filing = BeautifulSoup(r.content)

        return self.filing if html else r.content

    def getElement(self, tag:str, attrs:dict=None, last:bool=False, numeric:bool=True) -> str | float | BeautifulSoup | None:
        
        if self.filing is None:
            self.getFilingContent(html=True)

        element = self.filing.find_all(tag, attrs=attrs)[-1] if last else self.filing.find(tag, attrs=attrs)

        if element is None:
            print(f'Element not found: tag={tag}, attrs={attrs}, last={last}')
            return None
        else:
            return self._toNumeric(val=element.get_text()) if numeric else element.get_text()

    def getLastFilings(self, cik:str=None, type:str=None, company:str=None, limit:int=100, df:bool=True) -> list[dict] | pd.DataFrame:

        cik = cik or self.cik
        if cik is None:
            raise EdgarAPIError('The CIK must be passed')
        
        params: dict = {
            'action': 'getcurrent',
            'CIK': cik,
            'type': type,
            'company': company,
            'dateb': None,
            'owner': 'include',
            'start': 0,
            'count': limit,
            'output': None
        }
        next_button = {'value': 'next'}
        
        data: list = []
        while 'next' in next_button['value'].lower():
            params['start'] = len(data)
            r: requests.Response = self._get(url=f'{self._BASE_URL}/cgi-bin/browse-edgar', params=params)
            html = BeautifulSoup(markup=r.content)
            
            if params['output'] == 'atom':
                data = data + [{'type': entry.find('category')['term'], 
                    'title': entry.find('title').get_text(), 
                    'updated': pd.to_datetime(entry.find('updated').get_text()).to_pydatetime(), 
                    'url': entry.find('link')['href']} for entry in html.find_all(name='entry')]
                next_button = {'value': 'previous'}
            
            else:
                table = [table for table in html.find_all(name='table') if len(table.attrs) == 1][-1]
                data = data + pd.DataFrame(data=[[(td.find('a')['href'] if td.find('a') else td.get_text()) for td in tr.find_all('td')] for tr in table.find_all('tr', {'valign': 'top'})],
                                        columns=[th.get_text() for th in table.find_all('th')]).to_dict('records')

                next_button = html.find_all('input', {'type': 'button'})[-1]

        return pd.DataFrame(data=data) if df else data

    def getCikFilings(self, cik:str=None, df:bool=True) -> pd.DataFrame | list[dict]:

        cik = cik or self.cik
        if cik is None:
            raise EdgarAPIError('The CIK must be passed')
        
        r: requests.Response = self._get(url=f'{self._BASE_URL}/Archives/edgar/data/{cik}', accn_needed=False)
        html = BeautifulSoup(markup=r.content, features="html.parser")
        table = html.find(name='div', attrs={'id': 'main-content'}).find('table')
        columns: list[str] = [h.get_text().lower() for h in table.find_all('th')]
        values: list[list] = [[v.get_text() for v in row] for row in table.find_all('tr')[1:]]
        data = pd.DataFrame(data=values, columns=columns)
        
        return data if df else data.to_dict('records')

    def getApiCikFilings(self, cik:str=None, df:bool=True) -> list[dict] | pd.DataFrame:
        
        cik = cik or self.cik
        if cik is None:
            raise EdgarAPIError('The CIK must be passed')
        
        data = pd.DataFrame(data=self.edgar_api.get_submissions(cik=cik)['filings']['recent'])
        
        return data if df else data.to_dict('records')
    
if __name__ == "__main__":

    if False:
        jtai = SECFiling(cik='1861622', accn='000149315225011977', random_headers=True)
        aapl = SECFiling(cik='320193', accn='000032019325000073', random_headers=True)
        adil = SECFiling(cik='1655210', accn='000165521025000201', random_headers=True)

        floatingShares = jtai.getElement('ix:nonfraction', {'name': 'dei:EntityCommonStockSharesOutstanding'}, last=False, numeric=True)
        cash = jtai.getElement('ix:nonfraction', {'name': 'us-gaap:CashAndCashEquivalentsAtCarryingValue'}, last=False, numeric=True)
        totalCurrentAssets = jtai.getElement('ix:nonfraction', {'name': 'us-gaap:AssetsCurrent'}, last=False, numeric=True)
        totalAssets = jtai.getElement('ix:nonfraction', {'name': 'us-gaap:Assets'}, last=False, numeric=True)
        totalCurrentLiabilities = jtai.getElement('ix:nonfraction', {'name': 'us-gaap:LiabilitiesCurrent'}, last=False, numeric=True)
        warrantsOutstanding = jtai.getElement('ix:nonfraction', {'name': 'us-gaap:ClassOfWarrantOrRightOutstanding'}, last=False, numeric=True)
        if warrantsOutstanding:
            warrantsPrice = jtai.getElement('ix:nonfraction', {'name': 'us-gaap:ClassOfWarrantOrRightExercisePriceOfWarrantsOrRights1'}, last=True, numeric=True)
        else:
            warrantsOutstanding = 0
            warrantsPrice = 0
        quickRatio = totalCurrentAssets / totalCurrentLiabilities
        netWorkingCash = totalAssets - totalCurrentLiabilities
        print(f'QuickRatio: {quickRatio}')
        print(f'Net Working Cash: {netWorkingCash}')
        print(f'There are {warrantsOutstanding} warrants at {warrantsPrice}')




    edgar = Edgar(True)
    data = edgar.get_company_facts('1861622')

    float_amount = data['facts']['dei']['EntityPublicFloat']['units']['USD'][-1]['val']
    outstanding = data['facts']['dei']['EntityCommonStockSharesOutstanding']['units']['shares'][-1]['val']
    shares_outstanding = data['facts']['us-gaap']['CommonStockSharesOutstanding']['units']['shares'][-1]['val']
    cash = data['facts']['us-gaap']['CashAndCashEquivalentsAtCarryingValue']['units']['USD'][-1]['val']
    totalCurrentAssets = data['facts']['us-gaap']['AssetsCurrent']['units']['USD'][-1]['val']
    totalAssets = data['facts']['us-gaap']['Assets']['units']['USD'][-1]['val']
    totalCurrentLiabilities = data['facts']['us-gaap']['LiabilitiesCurrent']['units']['USD'][-1]['val']

    warrant_info = data['facts']['us-gaap']['ClassOfWarrantOrRightOutstanding']['units']['shares'][-1]
    if warrant_info:
        warrants = data['facts']['us-gaap']['ClassOfWarrantOrRightOutstanding']['units']['shares'][-1]['val']
        warrant_price = data['facts']['us-gaap'].get('ClassOfWarrantOrRightExercisePriceOfWarrantsOrRights1', None)
        if warrant_price:
            warrant_price = warrant_price['units']['shares'][-1]['val']
        if False:
            doc = SECFiling(cik=data['cik'], accn=warrant_info['accn'], random_headers=True)
            warrant_price = doc.getElement('ix:nonfraction', {'name': 'us-gaap:ClassOfWarrantOrRightExercisePriceOfWarrantsOrRights1'}, last=True, numeric=True)
    
    quickRatio = totalCurrentAssets / totalCurrentLiabilities
    netWorkingCash = totalAssets - totalCurrentLiabilities
    print(f'QuickRatio: {quickRatio}')
    print(f'Net Working Cash: {netWorkingCash}')
    print(f'There are {warrants} warrants at {warrant_price}')