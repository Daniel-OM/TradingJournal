
import requests

from ..config import GROQ_API_KEY 

class LLMResponse:

    def __init__(self, prompt:str='', context:str='', response:str='',
                 model:str=None, temperature:float=None, max_tokens:int=None) -> None:
        self.prompt: str = prompt
        self.context: str = context
        self.response: str = response
        self.model: str = model
        self.temperature: float = temperature
        self.max_tokens: int = max_tokens

    def setResponse(self, response:str) -> None:
        self.response: str = response

    def to_dict(self) -> dict:
        return self.__dict__

class LLM:

    _API_URL = "https://api.groq.com/openai/v1/chat/completions"
    horizon: dict[str, str] = {
        'position': 'long-term investment (6+ months)',
        'swing': 'swing trading (days to weeks)',
        'intraday': 'intraday trading (minutes to hours)'
    }
    
    def __init__(self, api_key:str) -> None:
        self.api_key: str = api_key

    def createStockPrompt(self, symbol:str, data:dict, trade_type:str, file_urls:list[str]=[]) -> str:
        """
        Create a prompt for financial analysis
        trade_type: 'position', 'swing', 'intraday'
        """
        
        prompt: str = f"""You are an expert financial analyst. Analyze the stock {symbol} for {self.horizon[trade_type]}.

        CURRENT DATA:
        {data}

        ATTACHED FILE URLS FOR RESEARCH:
        {'\n'.join(file_urls)}
        
        Provide a structured analysis with statistical rigor:

        1. TECHNICAL ANALYSIS (2-3 lines):
        - Current trend and key levels
        - Current trend strength based in multiple factors and timeframes
        - Key support/resistance levels with historical test count
        - Volume profile analysis (institutional participation)
        - Multi-timeframe alignment (daily, weekly confirmation)

        2. EDGE IDENTIFICATION:
        - Specific setup type
        - Historical win rate for similar setups (if known from pattern recognition)
        - Why THIS specific entry has positive expectancy
        - Market regime fit (trending/ranging/volatile) and sector regime

        3. RISK-REWARD ANALYSIS:
        - Action: BUY / HOLD / SELL (only if clear edge exists)
        - Confidence: High (>70%) / Medium (50-70%) / Low (<50%) - with reasoning
        - Reward:Risk ratio (minimum 2:1 required)
        - Position size recommendation

        4. EXECUTION PLAN:
        - Entry: Exact price level with contingency ($X or break of $Y)
        - Stop Loss: Technical invalidation level ($Z, max -2% risk)
        - Target 1: Conservative profit target ($A, 2R minimum or time based)
        - Target 2: Extended target if momentum continues ($B, 3-5R)
        - Time stop: Exit if thesis doesn't play out within [timeframe]
   
        5. RISK FACTORS & INVALIDATION:
        - Primary risk that would invalidate thesis
        - Maximum acceptable loss per trade
        - Catalysts to monitor (earnings, economic data, sector news, etc...)
        - Correlated positions that affect overall portfolio risk
   
        6. EXPECTED VALUE CALCULATION:
        If possible, provide: E = (Win% × Avg Win) - (Loss% × Avg Loss)
        Example: E = (60% × 4%) - (40% × 2%) = 1.6% per trade

        Be brutally honest: If setup lacks statistical edge, recommend HOLD/PASS. Quality > Quantity. Maximum 400 words, focus on actionable insights with numerical precision."""
        
        return prompt

    def createFilePrompt(self, file_url:str=None, file_content:str=None) -> str:

        if file_url is None and file_content is None:
            raise ValueError('You must pass file_url or file_content')

        prompt = f'''You are an expert financial analyst. Analyze the file and its possible repercussions over the stock price.'''
        if file_url is not None:
            prompt += f'''This is the link to the file: {file_url}'''
        elif file_content is not None:
            prompt += f'''This is the content of the file: {file_url}'''
        else:
            raise ValueError('You must pass file_url or file_content')

        return prompt
        
    def getSystemPrompt(self, trade_type: str) -> str:
        """
        Generate optimized system prompt based on trade type
        Focuses on mathematical expectancy and risk-adjusted returns
        """
        
        base_context = """You are an elite quantitative trading analyst with expertise in:
        - Technical analysis with focus on high-probability setups
        - Risk management and position sizing
        - Statistical edge identification and mathematical expectancy
        - Market microstructure and liquidity analysis

        Your analysis methodology prioritizes:
        1. MATHEMATICAL EXPECTANCY: Only recommend trades with positive expected value (E = (Win% × Avg Win) - (Loss% × Avg Loss) > 0)
        2. RISK-ADJUSTED RETURNS: Sharpe ratio > 1.5, maximum drawdown < 15%
        3. ASYMMETRIC RISK/REWARD: Minimum 2:1 reward-to-risk ratio
        4. STATISTICAL SIGNIFICANCE: Base decisions on repeatable patterns with sample size > 100 occurrences
        5. LIQUIDITY & EXECUTION: Consider bid-ask spread, slippage, and order flow

        Core principles:
        - Never recommend trades without clear edge and statistical backing
        - Always quantify confidence levels with probabilistic reasoning
        - Prioritize capital preservation over aggressive gains
        - Account for transaction costs, slippage, and market impact
        - Distinguish between noise and signal using multi-timeframe confirmation"""

        trade_specific: dict[str, str] = {
            'position': """
            POSITION TRADING FOCUS (6+ months):
            - Fundamental valuation metrics (P/E, PEG, DCF models)
            - Macro trends and sector rotation analysis
            - Long-term support/resistance zones tested multiple times
            - Institutional accumulation patterns (volume profile, dark pool activity)
            - Risk: Maximum 2-3% portfolio allocation per position
            - Expected win rate: 55-65% with 3:1+ reward/risk minimum""",

            'swing': """
            SWING TRADING FOCUS (days to weeks):
            - Mean reversion setups at key support/resistance with RSI divergence
            - Momentum continuation after pullbacks (20-50 EMA bounces)
            - Volume confirmation on breakouts (2x average volume minimum)
            - Market regime identification (trending vs ranging)
            - Risk: Maximum 1-2% capital per trade
            - Expected win rate: 50-60% with 2.5:1+ reward/risk minimum""",

            'intraday': """
            INTRADAY TRADING FOCUS (minutes to hours):
            - Opening range breakouts with volume spike confirmation
            - VWAP mean reversion plays with Level 2 order flow
            - High relative volume (RVOL > 2) for momentum scalps
            - News catalyst fading after initial volatility spike
            - Time-of-day edge awareness (avoid lunch chop 12-2pm ET)
            - Risk: Maximum 0.5-1% capital per trade
            - Expected win rate: 45-55% with 3:1+ reward/risk minimum
            - Minimum liquidity: 1M shares average daily volume"""
        }
        
        return base_context + trade_specific.get(trade_type, trade_specific['swing'])

    def callGroq(self, prompt:str, context:str, model:str="llama-3.3-70b-versatile", temperature:float=0.3, max_tokens:int=500) -> LLMResponse:
        
        """FREE option - Groq with Llama"""

        headers: dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Available models by need:
        # - llama-3.3-70b-versatile: BEST quality (recommended for analysis)
        # - llama-3.1-8b-instant: FASTER and higher daily limit (14.4K/day)
        # - meta-llama/llama-4-scout-17b-16e-instruct: Speed/quality balance
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response: requests.Response = requests.post(self._API_URL, json=data, headers=headers)
        response.raise_for_status()
        print(response.json(), '\n')
        return LLMResponse(prompt=prompt, 
                           context=context, 
                           response=response.json()['choices'][0]['message']['content'],
                           model=model,
                           temperature=temperature,
                           max_tokens=max_tokens)



if __name__ == "__main__":

    # from ..config import GROQ_API_KEY
    from .edgar import SECFiling
    
    # Initialize LLM with your Groq API key
    llm = LLM(api_key=GROQ_API_KEY)
    
    # Prepare stock data
    stock_data = {
        "52W_High_High_Pct": -46.05,
        "52W_High_Low": 6.64,
        "52W_Low_High_Pct": 615.86,
        "52W_Low_Low": 0.5,
        "52_week_high": 7.69,
        "52_week_low": 0.5001,
        "ATR_14": 0.82,
        "Avg_Volume": 104000000,
        "Beta": 2.25,
        "Book_per_sh": -8.84,
        "CIK": 1655210,
        "Cash_per_sh": 1.36,
        "Change_Pct": -1.1,
        "Company": "Beyond Meat Inc",
        "Country": "USA",
        "Current_Ratio": 3.29,
        "Debt_per_Eq": None,
        "Description": "Beyond Meat, Inc. engages in the provision of plant-based meats. Its products include ready-to-cook meat under The Beyond Burger and Beyond Sausage brands, and frozen meat, namely, Beyond Chicken Strips and Beyond Beef Crumbles. The company was founded by Ethan Walden Brown and Brent Taylor in 2009 and is headquartered in El Segundo, CA.",
        "Dividend_Est": None,
        "Dividend_Ex_Date": "nan",
        "Dividend_Gr_3_per_5Y_High": 0,
        "Dividend_Gr_3_per_5Y_Low": 0,
        "Dividend_TTM": None,
        "EPS_Q_per_Q_Pct": 28.03,
        "EPS_Y_per_Y_TTM_Pct": 56.19,
        "EPS_next_5Y_Pct": 19.81,
        "EPS_next_Q": -0.43,
        "EPS_next_Y_Pct": 26.99,
        "EPS_past_3_per_5Y_High_Pct": -52.51,
        "EPS_past_3_per_5Y_Low_Pct": 5.56,
        "EPS_per_Sales_Surpr_High_Pct": -8.41,
        "EPS_per_Sales_Surpr_Low_Pct": -11.69,
        "EPS_this_Y_Pct": 21.06,
        "EPS_ttm": -2.13,
        "EV_per_EBITDA": None,
        "EV_per_Sales": 4.83,
        "Earnings": "Nov 04 After Market Close",
        "Employees": 754,
        "Enterprise_Value": 1450000000,
        "Exchange": "NASD",
        "Forward_P_per_E": None,
        "Gross_Margin_Pct": 9.01,
        "IPO": "May 02, 2019",
        "Income": -153600000,
        "Index": [
            "RUT"
        ],
        "Industry": "Packaged Foods",
        "Insider_Own_Pct": 18.05,
        "Insider_Trans_Pct": -0.03,
        "Inst_Own_Pct": 72.45,
        "Inst_Trans_Pct": -1.29,
        "LT_Debt_per_Eq": None,
        "Market_Cap": 274770000,
        "Oper_Margin_Pct": -55.44,
        "Option": True,
        "PEG": None,
        "P_per_B": None,
        "P_per_C": 2.63,
        "P_per_E": None,
        "P_per_FCF": None,
        "P_per_S": 0.91,
        "Payout": None,
        "Perf_10Y": None,
        "Perf_3Y_Pct": -73.34,
        "Perf_5Y_Pct": -98.06,
        "Perf_Half_Y_Pct": 38.22,
        "Perf_Month_Pct": 25.61,
        "Perf_Quarter_Pct": -7.01,
        "Perf_Week_Pct": 434.25,
        "Perf_YTD_Pct": -4.79,
        "Perf_Year_Pct": -43.97,
        "Prev_Close": 3.62,
        "Price": 3.58,
        "Profit_Margin_Pct": -50.97,
        "Quick_Ratio": 2.07,
        "ROA_Pct": -21.9,
        "ROE": None,
        "ROIC_Pct": -25.53,
        "RSI_14": 66.31,
        "Recom": 4.25,
        "Rel_Volume": 30.69,
        "SMA200_Pct": 17.15,
        "SMA20_Pct": 81.21,
        "SMA50_Pct": 52.39,
        "Sales": 301350000,
        "Sales_Q_per_Q_Pct": -19.56,
        "Sales_Y_per_Y_TTM_Pct": -5.17,
        "Sales_past_3_per_5Y_High_Pct": 1.85,
        "Sales_past_3_per_5Y_Low_Pct": -11.1,
        "Sector": "Consumer Defensive",
        "Short": True,
        "Short_Float_Pct": 62.94,
        "Short_Interest": 39590000,
        "Short_Ratio": 0.38,
        "Shs_Float": 62900000,
        "Shs_Outstand": 76600000,
        "Symbol": "BYND",
        "Target_Price": 2.33,
        "Trades": "",
        "Volatility_High_Pct": 35.2,
        "Volatility_Low_Pct": 88.52,
        "Volume": 2227938304,
        "Web": "http://www.beyondmeat.com",
        "address": "888 North Douglas Street, El Segundo, USA",
        "address1": "888 North Douglas Street",
        "address2": "Suite 100",
        "askPrice": 2.97,
        "askSize": 132,
        "askTime": 1761215083000,
        "audit_risk": 4,
        "author": "Benzinga",
        "averageVolume": 102573427,
        "avgAnalystPriceTarget": 2.2666666666666666,
        "avgAnalystRating": 2,
        "avg_volume": 102573427,
        "bidPrice": 2.96,
        "bidSize": 218,
        "bidTime": 1761215084000,
        "board_risk": 4,
        "bzExchange": "NASDAQ",
        "candles": [
            {
                "close": 6.190000057220459,
                "date": "Wed, 23 Oct 2024 13:30:00 GMT",
                "gap": None,
                "high": 6.389999866485596,
                "high_spike": 0,
                "low": 6.059999942779541,
                "low_spike": -0.05164318162772508,
                "open": 6.389999866485596,
                "ret": -0.031298875343346966,
                "session": "REG",
                "volume": 2193400
            },
            {
                "close": 6.449999809265137,
                "date": "Thu, 24 Oct 2024 13:30:00 GMT",
                "gap": 0.001615468812962817,
                "high": 6.489999771118164,
                "high_spike": 0.04677418883459605,
                "low": 6.15500020980835,
                "low_spike": -0.007258000135667908,
                "open": 6.199999809265137,
                "ret": 0.040322581885632536,
                "session": "REG",
                "volume": 1515500
            },
            {
                "close": 6.320000171661377,
                "date": "Fri, 25 Oct 2024 13:30:00 GMT",
                "gap": 0.007751967785028402,
                "high": 6.5,
                "high_spike": 0,
                "low": 6.230000019073486,
                "low_spike": -0.04153845860407901,
                "open": 6.5,
                "ret": -0.02769228128286505,
                "session": "REG",
                "volume": 1581800
            },
            {
                "close": 6.579999923706055,
                "date": "Mon, 28 Oct 2024 13:30:00 GMT",
                "gap": 0.009493661574342616,
                "high": 6.636000156402588,
                "high_spike": 0.040125397706846755,
                "low": 6.320000171661377,
                "low_spike": -0.009404379577318989,
                "open": 6.380000114440918,
                "ret": 0.031347931924396555,
                "session": "REG",
                "volume": 2272000
            },
            {
                "close": 6.289999961853027,
                "date": "Tue, 29 Oct 2024 13:30:00 GMT",
                "gap": -0.021276575700436062,
                "high": 6.531000137329102,
                "high_spike": 0.014130447096287524,
                "low": 6.215000152587891,
                "low_spike": -0.034937873079721626,
                "open": 6.440000057220459,
                "ret": -0.023291940067493244,
                "session": "REG",
                "volume": 2406600
            },
            {
                "close": 6.179999828338623,
                "date": "Wed, 30 Oct 2024 13:30:00 GMT",
                "gap": -0.0015897857083184697,
                "high": 6.559999942779541,
                "high_spike": 0.04458594325106491,
                "low": 6.150000095367432,
                "low_spike": -0.020700654474163693,
                "open": 6.28000020980835,
                "ret": -0.01592362709057593,
                "session": "REG",
                "volume": 1908900
            },
            {
                "close": 6.090000152587891,
                "date": "Thu, 31 Oct 2024 13:30:00 GMT",
                "gap": 0.00323624295826086,
                "high": 6.25,
                "high_spike": 0.00806454714081517,
                "low": 5.965000152587891,
                "low_spike": -0.03790317159785517,
                "open": 6.199999809265137,
                "ret": -0.0177418806550389,
                "session": "REG",
                "volume": 2300200
            },
            {
                "close": 6.090000152587891,
                "date": "Fri, 01 Nov 2024 13:30:00 GMT",
                "gap": 0.014778271509974905,
                "high": 6.28000020980835,
                "high_spike": 0.016181291949422194,
                "low": 6.03000020980835,
                "low_spike": -0.024271783607896613,
                "open": 6.179999828338623,
                "ret": -0.014563054733114367,
                "session": "REG",
                "volume": 2272000
            },
            {
                "close": 6.039999961853027,
                "date": "Mon, 04 Nov 2024 14:30:00 GMT",
                "gap": -0.004926142702246339,
                "high": 6.21999979019165,
                "high_spike": 0.026402615333808388,
                "low": 5.880000114440918,
                "low_spike": -0.029702942250534492,
                "open": 6.059999942779541,
                "ret": -0.003300326916726104,
                "session": "REG",
                "volume": 2944600
            },
            {
                "close": 6.380000114440918,
                "date": "Tue, 05 Nov 2024 14:30:00 GMT",
                "gap": 0.018211942749856824,
                "high": 6.389999866485596,
                "high_spike": 0.03902435242219715,
                "low": 6.070000171661377,
                "low_spike": -0.013008117474065717,
                "open": 6.150000095367432,
                "ret": 0.03739837650518685,
                "session": "REG",
                "volume": 2230600
            },
            {
                "close": 6.579999923706055,
                "date": "Wed, 06 Nov 2024 14:30:00 GMT",
                "gap": 0.018808759154637977,
                "high": 6.599999904632568,
                "high_spike": 0.015384600712702756,
                "low": 6.119999885559082,
                "low_spike": -0.05846155606783354,
                "open": 6.5,
                "ret": 0.012307680570162294,
                "session": "REG",
                "volume": 3686100
            },
            {
                "close": 5.840000152587891,
                "date": "Thu, 07 Nov 2024 14:30:00 GMT",
                "gap": -0.07142854037100543,
                "high": 6.28000020980835,
                "high_spike": 0.02782325246794448,
                "low": 5.829999923706055,
                "low_spike": -0.04582654724874724,
                "open": 6.110000133514404,
                "ret": -0.04418984861318043,
                "session": "REG",
                "volume": 7835500
            },
            {
                "close": 5.369999885559082,
                "date": "Fri, 08 Nov 2024 14:30:00 GMT",
                "gap": 0.010273962536277104,
                "high": 5.920000076293945,
                "high_spike": 0.0033898272208872093,
                "low": 5.329999923706055,
                "low_spike": -0.09661019702506957,
                "open": 5.900000095367432,
                "ret": -0.08983054258329515,
                "session": "REG",
                "volume": 5475800
            },
            {
                "close": 5.269999980926514,
                "date": "Mon, 11 Nov 2024 14:30:00 GMT",
                "gap": 0.003724391313358666,
                "high": 5.440000057220459,
                "high_spike": 0.009276473464453927,
                "low": 5.099999904632568,
                "low_spike": -0.05380333377301438,
                "open": 5.389999866485596,
                "ret": -0.022263430154280228,
                "session": "REG",
                "volume": 5266000
            },
            {
                "close": 5.050000190734863,
                "date": "Tue, 12 Nov 2024 14:30:00 GMT",
                "gap": -0.013282765069207891,
                "high": 5.25,
                "high_spike": 0.00961542164785767,
                "low": 5,
                "low_spike": -0.03846150319251662,
                "open": 5.199999809265137,
                "ret": -0.028846081544659063,
                "session": "REG",
                "volume": 3700300
            },
            {
                "close": 5.269999980926514,
                "date": "Wed, 13 Nov 2024 14:30:00 GMT",
                "gap": 0.005940540958044194,
                "high": 5.324999809265137,
                "high_spike": 0.04822832465326998,
                "low": 5.019999980926514,
                "low_spike": -0.011811012535560939,
                "open": 5.079999923706055,
                "ret": 0.03740158662873494,
                "session": "REG",
                "volume": 2983300
            },
            {
                "close": 5.300000190734863,
                "date": "Thu, 14 Nov 2024 14:30:00 GMT",
                "gap": 0.020872890685488255,
                "high": 5.5,
                "high_spike": 0.022304810967750832,
                "low": 5.269999980926514,
                "low_spike": -0.020446121036158282,
                "open": 5.380000114440918,
                "ret": -0.01486987397850048,
                "session": "REG",
                "volume": 2883500
            },
            {
                "close": 5.139999866485596,
                "date": "Fri, 15 Nov 2024 14:30:00 GMT",
                "gap": 0.0018867456009075134,
                "high": 5.320000171661377,
                "high_spike": 0.0018832822955929807,
                "low": 5.019999980926514,
                "low_spike": -0.05461392937439957,
                "open": 5.309999942779541,
                "ret": -0.03201508062633951,
                "session": "REG",
                "volume": 2920000
            },
            {
                "close": 4.940000057220459,
                "date": "Mon, 18 Nov 2024 14:30:00 GMT",
                "gap": -0.0077820939478694395,
                "high": 5.170000076293945,
                "high_spike": 0.013725524111832366,
                "low": 4.829999923706055,
                "low_spike": -0.052941173720662205,
                "open": 5.099999904632568,
                "ret": -0.03137251968706389,
                "session": "REG",
                "volume": 4129300
            },
            {
                "close": 4.880000114440918,
                "date": "Tue, 19 Nov 2024 14:30:00 GMT",
                "gap": -0.008097158176053498,
                "high": 4.920000076293945,
                "high_spike": 0.004081628681073202,
                "low": 4.789999961853027,
                "low_spike": -0.022449006402755156,
                "open": 4.900000095367432,
                "ret": -0.004081628681073313,
                "session": "REG",
                "volume": 2713700
            },
            {
                "close": 5.150000095367432,
                "date": "Wed, 20 Nov 2024 14:30:00 GMT",
                "gap": 0.004098356651125901,
                "high": 5.230000019073486,
                "high_spike": 0.06734692189456148,
                "low": 4.900000095367432,
                "low_spike": 0,
                "open": 4.900000095367432,
                "ret": 0.051020407170268234,
                "session": "REG",
                "volume": 3407900
            },
            {
                "close": 5.010000228881836,
                "date": "Thu, 21 Nov 2024 14:30:00 GMT",
                "gap": 0,
                "high": 5.210000038146973,
                "high_spike": 0.011650474110381559,
                "low": 5.000999927520752,
                "low_spike": -0.028932070890777206,
                "open": 5.150000095367432,
                "ret": -0.02718443959089034,
                "session": "REG",
                "volume": 2061000
            },
            {
                "close": 4.889999866485596,
                "date": "Fri, 22 Nov 2024 14:30:00 GMT",
                "gap": 0.0019959584007662734,
                "high": 5.059999942779541,
                "high_spike": 0.007968119921316186,
                "low": 4.849999904632568,
                "low_spike": -0.033864557159334785,
                "open": 5.019999980926514,
                "ret": -0.0258964372380186,
                "session": "REG",
                "volume": 3805300
            },
            {
                "close": 5.25,
                "date": "Mon, 25 Nov 2024 14:30:00 GMT",
                "gap": 0.0020450366369892947,
                "high": 5.330999851226807,
                "high_spike": 0.08795913213692619,
                "low": 4.840000152587891,
                "low_spike": -0.012244886043219938,
                "open": 4.900000095367432,
                "ret": 0.07142855057563491,
                "session": "REG",
                "volume": 6210300
            },
            {
                "close": 5.170000076293945,
                "date": "Tue, 26 Nov 2024 14:30:00 GMT",
                "gap": -0.009523845854259694,
                "high": 5.199999809265137,
                "high_spike": 0,
                "low": 4.96999979019165,
                "low_spike": -0.04423077452112256,
                "open": 5.199999809265137,
                "ret": -0.005769179629149024,
                "session": "REG",
                "volume": 3994700
            },
            {
                "close": 5.050000190734863,
                "date": "Wed, 27 Nov 2024 14:30:00 GMT",
                "gap": 0,
                "high": 5.239999771118164,
                "high_spike": 0.01353959260952231,
                "low": 5.039999961853027,
                "low_spike": -0.025145089462765946,
                "open": 5.170000076293945,
                "ret": -0.023210809243372932,
                "session": "REG",
                "volume": 1909800
            },
            {
                "close": 4.980000019073486,
                "date": "Fri, 29 Nov 2024 14:30:00 GMT",
                "gap": 0.005940540958044194,
                "high": 5.079999923706055,
                "high_spike": 0,
                "low": 4.960000038146973,
                "low_spike": -0.023622025071121988,
                "open": 5.079999923706055,
                "ret": -0.0196850208926016,
                "session": "REG",
                "volume": 2186000
            },
            {
                "close": 4.960000038146973,
                "date": "Mon, 02 Dec 2024 14:30:00 GMT",
                "gap": 0.004016060411629274,
                "high": 5.010000228881836,
                "high_spike": 0.002000045776367143,
                "low": 4.829999923706055,
                "low_spike": -0.03400001525878904,
                "open": 5,
                "ret": -0.007999992370605447,
                "session": "REG",
                "volume": 4693500
            },
            {
                "close": 4.860000133514404,
                "date": "Tue, 03 Dec 2024 14:30:00 GMT",
                "gap": -0.014112937726413533,
                "high": 4.945000171661377,
                "high_spike": 0.011247506478013314,
                "low": 4.829999923706055,
                "low_spike": -0.012269927283794058,
                "open": 4.889999866485596,
                "ret": -0.006134914885540077,
                "session": "REG",
                "volume": 3562700
            },
            {
                "close": 4.659999847412109,
                "date": "Wed, 04 Dec 2024 14:30:00 GMT",
                "gap": 0.002057562092585119,
                "high": 4.869999885559082,
                "high_spike": 0,
                "low": 4.619999885559082,
                "low_spike": -0.051334703465049425,
                "open": 4.869999885559082,
                "ret": -0.0431211587436956,
                "session": "REG",
                "volume": 5492800
            },
            {
                "close": 4.489999771118164,
                "date": "Thu, 05 Dec 2024 14:30:00 GMT",
                "gap": 0.0036481113564195145,
                "high": 4.677000045776367,
                "high_spike": 0,
                "low": 4.460000038146973,
                "low_spike": -0.04639726438005054,
                "open": 4.677000045776367,
                "ret": -0.03998295335213353,
                "session": "REG",
                "volume": 3974000
            },
            {
                "close": 4.550000190734863,
                "date": "Fri, 06 Dec 2024 14:30:00 GMT",
                "gap": 0.010022289217787472,
                "high": 4.625,
                "high_spike": 0.019845679297927354,
                "low": 4.489999771118164,
                "low_spike": -0.009922839648963677,
                "open": 4.534999847412109,
                "ret": 0.003307683313664045,
                "session": "REG",
                "volume": 3141600
            },
            {
                "close": 4.480000019073486,
                "date": "Mon, 09 Dec 2024 14:30:00 GMT",
                "gap": 0.015384547668098714,
                "high": 4.710000038146973,
                "high_spike": 0.019480552990749578,
                "low": 4.440000057220459,
                "low_spike": -0.03896100276999048,
                "open": 4.619999885559082,
                "ret": -0.030303002154437042,
                "session": "REG",
                "volume": 3549800
            },
            {
                "close": 4.159999847412109,
                "date": "Tue, 10 Dec 2024 14:30:00 GMT",
                "gap": -0.006696475375139399,
                "high": 4.480000019073486,
                "high_spike": 0.006741620470609444,
                "low": 4.119999885559082,
                "low_spike": -0.07415728940459221,
                "open": 4.449999809265137,
                "ret": -0.0651685335467278,
                "session": "REG",
                "volume": 5401200
            },
            {
                "close": 4,
                "date": "Wed, 11 Dec 2024 14:30:00 GMT",
                "gap": 0,
                "high": 4.170000076293945,
                "high_spike": 0.0024039012616927646,
                "low": 3.9010000228881836,
                "low_spike": -0.06225957548653438,
                "open": 4.159999847412109,
                "ret": -0.03846150319251662,
                "session": "REG",
                "volume": 4885800
            },
            {
                "close": 3.9100000858306885,
                "date": "Thu, 12 Dec 2024 14:30:00 GMT",
                "gap": -0.007499992847442627,
                "high": 4.050000190734863,
                "high_spike": 0.020151174193477006,
                "low": 3.859999895095825,
                "low_spike": -0.027707841995384563,
                "open": 3.9700000286102295,
                "ret": -0.015113335603814892,
                "session": "REG",
                "volume": 3233100
            },
            {
                "close": 3.8399999141693115,
                "date": "Fri, 13 Dec 2024 14:30:00 GMT",
                "gap": 0,
                "high": 3.9149999618530273,
                "high_spike": 0.00127874064260447,
                "low": 3.690000057220459,
                "low_spike": -0.056265990736798166,
                "open": 3.9100000858306885,
                "ret": -0.01790285680940218,
                "session": "REG",
                "volume": 4427400
            },
            {
                "close": 3.7100000381469727,
                "date": "Mon, 16 Dec 2024 14:30:00 GMT",
                "gap": -0.015624985448084439,
                "high": 3.7799999713897705,
                "high_spike": 0,
                "low": 3.6500000953674316,
                "low_spike": -0.03439150185351525,
                "open": 3.7799999713897705,
                "ret": -0.01851850099804664,
                "session": "REG",
                "volume": 3481900
            },
            {
                "close": 3.799999952316284,
                "date": "Tue, 17 Dec 2024 14:30:00 GMT",
                "gap": -0.016172491148951362,
                "high": 3.9000000953674316,
                "high_spike": 0.0684931488953382,
                "low": 3.549999952316284,
                "low_spike": -0.02739729875022945,
                "open": 3.6500000953674316,
                "ret": 0.04109585014510864,
                "session": "REG",
                "volume": 3768500
            },
            {
                "close": 3.6500000953674316,
                "date": "Wed, 18 Dec 2024 14:30:00 GMT",
                "gap": -0.013157882353605488,
                "high": 3.819999933242798,
                "high_spike": 0.018666648864746005,
                "low": 3.619999885559082,
                "low_spike": -0.034666697184244755,
                "open": 3.75,
                "ret": -0.026666641235351562,
                "session": "REG",
                "volume": 4780300
            },
            {
                "close": 3.4100000858306885,
                "date": "Thu, 19 Dec 2024 14:30:00 GMT",
                "gap": 0.0027397233430073165,
                "high": 3.6600000858306885,
                "high_spike": 0,
                "low": 3.4000000953674316,
                "low_spike": -0.07103824709453421,
                "open": 3.6600000858306885,
                "ret": -0.06830600932711695,
                "session": "REG",
                "volume": 5317200
            },
            {
                "close": 3.549999952316284,
                "date": "Fri, 20 Dec 2024 14:30:00 GMT",
                "gap": -0.011730263714014644,
                "high": 3.630000114440918,
                "high_spike": 0.07715140584899505,
                "low": 3.299999952316284,
                "low_spike": -0.020771494249230527,
                "open": 3.369999885559082,
                "ret": 0.05341248453109082,
                "session": "REG",
                "volume": 4691000
            },
            {
                "close": 3.5399999618530273,
                "date": "Mon, 23 Dec 2024 14:30:00 GMT",
                "gap": 0.0028168987598808926,
                "high": 3.6500000953674316,
                "high_spike": 0.02528094214451615,
                "low": 3.4200000762939453,
                "low_spike": -0.039325805824673155,
                "open": 3.559999942779541,
                "ret": -0.005617972260667625,
                "session": "REG",
                "volume": 3885300
            },
            {
                "close": 3.549999952316284,
                "date": "Tue, 24 Dec 2024 14:30:00 GMT",
                "gap": -0.00847456828052251,
                "high": 3.640000104904175,
                "high_spike": 0.03703706974191756,
                "low": 3.440000057220459,
                "low_spike": -0.019943000978059566,
                "open": 3.509999990463257,
                "ret": 0.011396000558891117,
                "session": "REG",
                "volume": 1796100
            },
            {
                "close": 3.8299999237060547,
                "date": "Thu, 26 Dec 2024 14:30:00 GMT",
                "gap": 0,
                "high": 3.880000114440918,
                "high_spike": 0.09295779339639632,
                "low": 3.515000104904175,
                "low_spike": -0.009859112079500965,
                "open": 3.549999952316284,
                "ret": 0.07887323243682798,
                "session": "REG",
                "volume": 4661800
            },
            {
                "close": 4.079999923706055,
                "date": "Fri, 27 Dec 2024 14:30:00 GMT",
                "gap": 0.010443854477762526,
                "high": 4.199999809265137,
                "high_spike": 0.08527130063684263,
                "low": 3.8320000171661377,
                "low_spike": -0.009819087730400411,
                "open": 3.869999885559082,
                "ret": 0.054263577353216075,
                "session": "REG",
                "volume": 7499500
            },
            {
                "close": 3.859999895095825,
                "date": "Mon, 30 Dec 2024 14:30:00 GMT",
                "gap": -0.024509781005518705,
                "high": 3.994999885559082,
                "high_spike": 0.0037688106567113078,
                "low": 3.759999990463257,
                "low_spike": -0.055276388833144785,
                "open": 3.9800000190734863,
                "ret": -0.030150784774517714,
                "session": "REG",
                "volume": 4787800
            },
            {
                "close": 3.759999990463257,
                "date": "Tue, 31 Dec 2024 14:30:00 GMT",
                "gap": 0.005181404116229027,
                "high": 3.930000066757202,
                "high_spike": 0.01288658526843589,
                "low": 3.630000114440918,
                "low_spike": -0.0644329877902654,
                "open": 3.880000114440918,
                "ret": -0.03092786609233189,
                "session": "REG",
                "volume": 4096800
            },
            {
                "close": 3.8499999046325684,
                "date": "Thu, 02 Jan 2025 14:30:00 GMT",
                "gap": 0.02127657550770312,
                "high": 4,
                "high_spike": 0.04166668994973155,
                "low": 3.7899999618530273,
                "low_spike": -0.013020821206737088,
                "open": 3.8399999141693115,
                "ret": 0.002604164241347462,
                "session": "REG",
                "volume": 3317400
            },
            {
                "close": 4.010000228881836,
                "date": "Fri, 03 Jan 2025 14:30:00 GMT",
                "gap": 0.020779263404233417,
                "high": 4.079999923706055,
                "high_spike": 0.038167901883173094,
                "low": 3.8299999237060547,
                "low_spike": -0.025445328588419525,
                "open": 3.930000066757202,
                "ret": 0.020356275003996283,
                "session": "REG",
                "volume": 3051800
            },
            {
                "close": 3.9100000858306885,
                "date": "Mon, 06 Jan 2025 14:30:00 GMT",
                "gap": 0.009975052261825157,
                "high": 4.159999847412109,
                "high_spike": 0.027160407776990025,
                "low": 3.859999895095825,
                "low_spike": -0.04691365103480727,
                "open": 4.050000190734863,
                "ret": -0.0345679255088559,
                "session": "REG",
                "volume": 4257400
            },
            {
                "close": 3.759999990463257,
                "date": "Tue, 07 Jan 2025 14:30:00 GMT",
                "gap": 0.012787711309131922,
                "high": 4.019999980926514,
                "high_spike": 0.015151500555948827,
                "low": 3.7200000286102295,
                "low_spike": -0.06060606243050637,
                "open": 3.9600000381469727,
                "ret": -0.05050506205987393,
                "session": "REG",
                "volume": 2869900
            },
            {
                "close": 3.5999999046325684,
                "date": "Wed, 08 Jan 2025 14:30:00 GMT",
                "gap": -0.013297859692314451,
                "high": 3.7899999618530273,
                "high_spike": 0.021563321531935076,
                "low": 3.5999999046325684,
                "low_spike": -0.029649631370178064,
                "open": 3.7100000381469727,
                "ret": -0.029649631370178064,
                "session": "REG",
                "volume": 2947500
            },
            {
                "close": 3.5999999046325684,
                "date": "Fri, 10 Jan 2025 14:30:00 GMT",
                "gap": -0.013333294479934255,
                "high": 3.619999885559082,
                "high_spike": 0.019144098791207043,
                "low": 3.430000066757202,
                "low_spike": -0.03434684049743564,
                "open": 3.552000045776367,
                "ret": 0.013513473602928983,
                "session": "REG",
                "volume": 2963700
            },
            {
                "close": 3.630000114440918,
                "date": "Mon, 13 Jan 2025 14:30:00 GMT",
                "gap": -0.011111100809073515,
                "high": 3.7100000381469727,
                "high_spike": 0.042134858926518914,
                "low": 3.505000114440918,
                "low_spike": -0.01544939023107983,
                "open": 3.559999942779541,
                "ret": 0.019662969883848636,
                "session": "REG",
                "volume": 4029500
            },
            {
                "close": 3.630000114440918,
                "date": "Tue, 14 Jan 2025 14:30:00 GMT",
                "gap": 0.008264454667762822,
                "high": 3.680000066757202,
                "high_spike": 0.005464475534834312,
                "low": 3.5,
                "low_spike": -0.0437158694203621,
                "open": 3.6600000858306885,
                "ret": -0.00819671330225158,
                "session": "REG",
                "volume": 1913500
            },
            {
                "close": 3.9700000286102295,
                "date": "Wed, 15 Jan 2025 14:30:00 GMT",
                "gap": 0.011019272890350207,
                "high": 4.046999931335449,
                "high_spike": 0.10272475400660142,
                "low": 3.6600000858306885,
                "low_spike": -0.0027247929851148545,
                "open": 3.6700000762939453,
                "ret": 0.08174385451763566,
                "session": "REG",
                "volume": 4722800
            },
            {
                "close": 4.179999828338623,
                "date": "Thu, 16 Jan 2025 14:30:00 GMT",
                "gap": -0.005037778534604964,
                "high": 4.179999828338623,
                "high_spike": 0.0582277918679468,
                "low": 3.8499999046325684,
                "low_spike": -0.025316491606066638,
                "open": 3.950000047683716,
                "ret": 0.0582277918679468,
                "session": "REG",
                "volume": 4693300
            },
            {
                "close": 4.079999923706055,
                "date": "Fri, 17 Jan 2025 14:30:00 GMT",
                "gap": 0,
                "high": 4.21999979019165,
                "high_spike": 0.009569369257348859,
                "low": 4,
                "low_spike": -0.043062161658070086,
                "open": 4.179999828338623,
                "ret": -0.023923423143372258,
                "session": "REG",
                "volume": 5989000
            },
            {
                "close": 4,
                "date": "Tue, 21 Jan 2025 14:30:00 GMT",
                "gap": -0.00980391240220746,
                "high": 4.144999980926514,
                "high_spike": 0.025990103976467838,
                "low": 3.990000009536743,
                "low_spike": -0.012376225937722696,
                "open": 4.039999961853027,
                "ret": -0.009900980750178201,
                "session": "REG",
                "volume": 3760800
            },
            {
                "close": 3.9000000953674316,
                "date": "Wed, 22 Jan 2025 14:30:00 GMT",
                "gap": -0.007499992847442627,
                "high": 3.990000009536743,
                "high_spike": 0.005037778534604964,
                "low": 3.819999933242798,
                "low_spike": -0.03778339906459449,
                "open": 3.9700000286102295,
                "ret": -0.017632224871117375,
                "session": "REG",
                "volume": 3419800
            },
            {
                "close": 4.059999942779541,
                "date": "Thu, 23 Jan 2025 14:30:00 GMT",
                "gap": 0,
                "high": 4.150000095367432,
                "high_spike": 0.0641025625350522,
                "low": 3.872999906539917,
                "low_spike": -0.006923125171095945,
                "open": 3.9000000953674316,
                "ret": 0.0410256008973342,
                "session": "REG",
                "volume": 3223400
            },
            {
                "close": 4.070000171661377,
                "date": "Fri, 24 Jan 2025 14:30:00 GMT",
                "gap": 0,
                "high": 4.099999904632568,
                "high_spike": 0.00985220749181659,
                "low": 3.9100000858306885,
                "low_spike": -0.0369457780943121,
                "open": 4.059999942779541,
                "ret": 0.002463110596742979,
                "session": "REG",
                "volume": 2190900
            },
            {
                "close": 4.130000114440918,
                "date": "Mon, 27 Jan 2025 14:30:00 GMT",
                "gap": -0.019656058661043696,
                "high": 4.465000152587891,
                "high_spike": 0.11904765461549394,
                "low": 3.990000009536743,
                "low_spike": 0,
                "open": 3.990000009536743,
                "ret": 0.035087745506153345,
                "session": "REG",
                "volume": 5925500
            },
            {
                "close": 3.9800000190734863,
                "date": "Tue, 28 Jan 2025 14:30:00 GMT",
                "gap": -0.012106583377572533,
                "high": 4.159999847412109,
                "high_spike": 0.01960782480441492,
                "low": 3.9100000858306885,
                "low_spike": -0.04166662770938179,
                "open": 4.079999923706055,
                "ret": -0.024509781005518705,
                "session": "REG",
                "volume": 2784100
            },
            {
                "close": 4.03000020980835,
                "date": "Wed, 29 Jan 2025 14:30:00 GMT",
                "gap": -0.0075376812175881325,
                "high": 4.210000038146973,
                "high_spike": 0.06582278160116006,
                "low": 3.930000066757202,
                "low_spike": -0.005063286249386678,
                "open": 3.950000047683716,
                "ret": 0.02025320535667996,
                "session": "REG",
                "volume": 1926300
            },
            {
                "close": 4.070000171661377,
                "date": "Thu, 30 Jan 2025 14:30:00 GMT",
                "gap": 0.00992554833016479,
                "high": 4.179999828338623,
                "high_spike": 0.027026941532620086,
                "low": 4.033999919891357,
                "low_spike": -0.008845270332095367,
                "open": 4.070000171661377,
                "ret": 0,
                "session": "REG",
                "volume": 1787600
            },
            {
                "close": 3.9600000381469727,
                "date": "Fri, 31 Jan 2025 14:30:00 GMT",
                "gap": 0,
                "high": 4.0980000495910645,
                "high_spike": 0.006879576596739545,
                "low": 3.930000066757202,
                "low_spike": -0.0343980587222007,
                "open": 4.070000171661377,
                "ret": -0.02702705869162214,
                "session": "REG",
                "volume": 2303100
            },
            {
                "close": 3.7899999618530273,
                "date": "Mon, 03 Feb 2025 14:30:00 GMT",
                "gap": -0.0353535615039251,
                "high": 3.944999933242798,
                "high_spike": 0.03272251366085421,
                "low": 3.75,
                "low_spike": -0.018324590174370714,
                "open": 3.819999933242798,
                "ret": -0.007853395789016004,
                "session": "REG",
                "volume": 2892600
            },
            {
                "close": 3.8399999141693115,
                "date": "Tue, 04 Feb 2025 14:30:00 GMT",
                "gap": -0.002638519937706696,
                "high": 3.869999885559082,
                "high_spike": 0.023809501283202916,
                "low": 3.75,
                "low_spike": -0.007936500427734305,
                "open": 3.7799999713897705,
                "ret": 0.01587300085546861,
                "session": "REG",
                "volume": 1754100
            },
            {
                "close": 3.869999885559082,
                "date": "Wed, 05 Feb 2025 14:30:00 GMT",
                "gap": -0.002604164241347462,
                "high": 3.9800000190734863,
                "high_spike": 0.039164516541892125,
                "low": 3.8299999237060547,
                "low_spike": 0,
                "open": 3.8299999237060547,
                "ret": 0.010443854477762526,
                "session": "REG",
                "volume": 1401300
            },
            {
                "close": 3.930000066757202,
                "date": "Thu, 06 Feb 2025 14:30:00 GMT",
                "gap": 0.007751992427776466,
                "high": 4.034999847412109,
                "high_spike": 0.03461532019064184,
                "low": 3.8499999046325684,
                "low_spike": -0.01282056141338439,
                "open": 3.9000000953674316,
                "ret": 0.007692300168250066,
                "session": "REG",
                "volume": 2111300
            },
            {
                "close": 3.9200000762939453,
                "date": "Fri, 07 Feb 2025 14:30:00 GMT",
                "gap": -0.007633580376634641,
                "high": 3.944999933242798,
                "high_spike": 0.011538419685891421,
                "low": 3.8499999046325684,
                "low_spike": -0.01282056141338439,
                "open": 3.9000000953674316,
                "ret": 0.0051282001121668586,
                "session": "REG",
                "volume": 1480800
            },
            {
                "close": 3.9600000381469727,
                "date": "Mon, 10 Feb 2025 14:30:00 GMT",
                "gap": 0,
                "high": 3.9700000286102295,
                "high_spike": 0.012755089628354144,
                "low": 3.799999952316284,
                "low_spike": -0.03061227592911475,
                "open": 3.9200000762939453,
                "ret": 0.010204071702683226,
                "session": "REG",
                "volume": 2645700
            },
            {
                "close": 3.819999933242798,
                "date": "Tue, 11 Feb 2025 14:30:00 GMT",
                "gap": -0.002525250092658138,
                "high": 3.9800000190734863,
                "high_spike": 0.007594929374080017,
                "low": 3.809999942779541,
                "low_spike": -0.035443064104839994,
                "open": 3.950000047683716,
                "ret": -0.032911420980146655,
                "session": "REG",
                "volume": 2070200
            },
            {
                "close": 3.819999933242798,
                "date": "Wed, 12 Feb 2025 14:30:00 GMT",
                "gap": -0.005235597192677299,
                "high": 3.819999933242798,
                "high_spike": 0.005263152941442195,
                "low": 3.5899999141693115,
                "low_spike": -0.05526316862687519,
                "open": 3.799999952316284,
                "ret": 0.005263152941442195,
                "session": "REG",
                "volume": 3649900
            },
            {
                "close": 3.859999895095825,
                "date": "Thu, 13 Feb 2025 14:30:00 GMT",
                "gap": 0,
                "high": 3.869999885559082,
                "high_spike": 0.013088992981693304,
                "low": 3.75,
                "low_spike": -0.018324590174370714,
                "open": 3.819999933242798,
                "ret": 0.010471194385354599,
                "session": "REG",
                "volume": 2307400
            },
            {
                "close": 3.950000047683716,
                "date": "Fri, 14 Feb 2025 14:30:00 GMT",
                "gap": 0.012953417640862996,
                "high": 3.990000009536743,
                "high_spike": 0.02046033809461112,
                "low": 3.8399999141693115,
                "low_spike": -0.01790285680940218,
                "open": 3.9100000858306885,
                "ret": 0.01023016904730567,
                "session": "REG",
                "volume": 3189900
            },
            {
                "close": 4.400000095367432,
                "date": "Tue, 18 Feb 2025 14:30:00 GMT",
                "gap": 0,
                "high": 4.409999847412109,
                "high_spike": 0.11645564409502684,
                "low": 3.9100000858306885,
                "low_spike": -0.010126572498773356,
                "open": 3.950000047683716,
                "ret": 0.11392406132946675,
                "session": "REG",
                "volume": 8272600
            },
            {
                "close": 4.320000171661377,
                "date": "Wed, 19 Feb 2025 14:30:00 GMT",
                "gap": 0.022727250560256484,
                "high": 4.739999771118164,
                "high_spike": 0.053333282470703125,
                "low": 4.28000020980835,
                "low_spike": -0.04888884226481116,
                "open": 4.5,
                "ret": -0.039999961853027344,
                "session": "REG",
                "volume": 9462000
            },
            {
                "close": 4.079999923706055,
                "date": "Thu, 20 Feb 2025 14:30:00 GMT",
                "gap": -0.016203742796254694,
                "high": 4.260000228881836,
                "high_spike": 0.0023529950310201553,
                "low": 4,
                "low_spike": -0.05882352941176472,
                "open": 4.25,
                "ret": -0.04000001795151653,
                "session": "REG",
                "volume": 4029300
            },
            {
                "close": 4.019999980926514,
                "date": "Fri, 21 Feb 2025 14:30:00 GMT",
                "gap": 0.022058861340894076,
                "high": 4.329999923706055,
                "high_spike": 0.03836926726253398,
                "low": 4.010000228881836,
                "low_spike": -0.03836926726253398,
                "open": 4.170000076293945,
                "ret": -0.03597124523334372,
                "session": "REG",
                "volume": 4335400
            },
            {
                "close": 3.859999895095825,
                "date": "Mon, 24 Feb 2025 14:30:00 GMT",
                "gap": 0.009950239314132636,
                "high": 4.090000152587891,
                "high_spike": 0.0073892143426512735,
                "low": 3.8499999046325684,
                "low_spike": -0.0517241480558257,
                "open": 4.059999942779541,
                "ret": -0.049261096182871555,
                "session": "REG",
                "volume": 2933400
            },
            {
                "close": 3.7200000286102295,
                "date": "Tue, 25 Feb 2025 14:30:00 GMT",
                "gap": 0.005181404116229027,
                "high": 3.9149999618530273,
                "high_spike": 0.009020578963862436,
                "low": 3.7100000381469727,
                "low_spike": -0.04381445136076789,
                "open": 3.880000114440918,
                "ret": -0.04123713430708065,
                "session": "REG",
                "volume": 3182800
            },
            {
                "close": 3.559999942779541,
                "date": "Wed, 26 Feb 2025 14:30:00 GMT",
                "gap": 0.009408625150942429,
                "high": 3.755000114440918,
                "high_spike": 0,
                "low": 3.509999990463257,
                "low_spike": -0.06524636924388993,
                "open": 3.755000114440918,
                "ret": -0.05193080312073717,
                "session": "REG",
                "volume": 5169000
            },
            {
                "close": 3.180000066757202,
                "date": "Thu, 27 Feb 2025 14:30:00 GMT",
                "gap": -0.03370783356400553,
                "high": 3.6500000953674316,
                "high_spike": 0.061046521701704215,
                "low": 3.0999999046325684,
                "low_spike": -0.09883725201522608,
                "open": 3.440000057220459,
                "ret": -0.07558139131931829,
                "session": "REG",
                "volume": 8602500
            },
            {
                "close": 3.1600000858306885,
                "date": "Fri, 28 Feb 2025 14:30:00 GMT",
                "gap": -0.012578604092237433,
                "high": 3.325000047683716,
                "high_spike": 0.05891717726079082,
                "low": 3.0999999046325684,
                "low_spike": -0.01273891685835693,
                "open": 3.140000104904175,
                "ret": 0.0063694204644377805,
                "session": "REG",
                "volume": 4189400
            },
            {
                "close": 3.0799999237060547,
                "date": "Mon, 03 Mar 2025 14:30:00 GMT",
                "gap": -0.003164553858114205,
                "high": 3.180000066757202,
                "high_spike": 0.009523800152860362,
                "low": 2.984999895095825,
                "low_spike": -0.05238101437338527,
                "open": 3.1500000953674316,
                "ret": -0.022222276045109735,
                "session": "REG",
                "volume": 4366400
            },
            {
                "close": 3.2300000190734863,
                "date": "Tue, 04 Mar 2025 14:30:00 GMT",
                "gap": -0.0487012534624881,
                "high": 3.259999990463257,
                "high_spike": 0.11262795774311507,
                "low": 2.859999895095825,
                "low_spike": -0.023890843026106223,
                "open": 2.930000066757202,
                "ret": 0.10238905989115255,
                "session": "REG",
                "volume": 4655000
            },
            {
                "close": 3.2100000381469727,
                "date": "Wed, 05 Mar 2025 14:30:00 GMT",
                "gap": 0.003095972261363933,
                "high": 3.259999990463257,
                "high_spike": 0.006172833601125083,
                "low": 3.1050000190734863,
                "low_spike": -0.04166666360058413,
                "open": 3.240000009536743,
                "ret": -0.009259250401687513,
                "session": "REG",
                "volume": 2753200
            },
            {
                "close": 3.1500000953674316,
                "date": "Thu, 06 Mar 2025 14:30:00 GMT",
                "gap": -0.024922094316309096,
                "high": 3.2300000190734863,
                "high_spike": 0.03194885015217652,
                "low": 3.0850000381469727,
                "low_spike": -0.014377020654513073,
                "open": 3.130000114440918,
                "ret": 0.006389770030435393,
                "session": "REG",
                "volume": 2699600
            },
            {
                "close": 3.359999895095825,
                "date": "Fri, 07 Mar 2025 14:30:00 GMT",
                "gap": 0.004761862232212533,
                "high": 3.380000114440918,
                "high_spike": 0.06793053876121169,
                "low": 3.0999999046325684,
                "low_spike": -0.02053714312919075,
                "open": 3.1649999618530273,
                "ret": 0.06161135405784668,
                "session": "REG",
                "volume": 2412200
            },
            {
                "close": 3.259999990463257,
                "date": "Mon, 10 Mar 2025 13:30:00 GMT",
                "gap": -0.008928563192385108,
                "high": 3.5,
                "high_spike": 0.051051075131781865,
                "low": 3.259999990463257,
                "low_spike": -0.02102100145542729,
                "open": 3.3299999237060547,
                "ret": -0.02102100145542729,
                "session": "REG",
                "volume": 3804600
            },
            {
                "close": 3.109999895095825,
                "date": "Tue, 11 Mar 2025 13:30:00 GMT",
                "gap": 0.046012299327067296,
                "high": 3.4100000858306885,
                "high_spike": 0,
                "low": 3.0299999713897705,
                "low_spike": -0.11143698090211296,
                "open": 3.4100000858306885,
                "ret": -0.08797659330902396,
                "session": "REG",
                "volume": 2875900
            },
            {
                "close": 3.3299999237060547,
                "date": "Wed, 12 Mar 2025 13:30:00 GMT",
                "gap": 0,
                "high": 3.369999885559082,
                "high_spike": 0.08360128592713201,
                "low": 3.069999933242798,
                "low_spike": -0.012861724502339578,
                "open": 3.109999895095825,
                "ret": 0.07073956142479254,
                "session": "REG",
                "volume": 2269400
            },
            {
                "close": 3.2899999618530273,
                "date": "Thu, 13 Mar 2025 13:30:00 GMT",
                "gap": -0.012012000831672753,
                "high": 3.369999885559082,
                "high_spike": 0.02431608651478423,
                "low": 3.184999942779541,
                "low_spike": -0.03191489978448114,
                "open": 3.2899999618530273,
                "ret": 0,
                "session": "REG",
                "volume": 1849600
            },
            {
                "close": 3.390000104904175,
                "date": "Fri, 14 Mar 2025 13:30:00 GMT",
                "gap": 0.0075988132696971356,
                "high": 3.5,
                "high_spike": 0.05580691993551845,
                "low": 3.25,
                "low_spike": -0.019607860059875803,
                "open": 3.315000057220459,
                "ret": 0.02262444838284594,
                "session": "REG",
                "volume": 2359800
            },
            {
                "close": 3.5199999809265137,
                "date": "Mon, 17 Mar 2025 13:30:00 GMT",
                "gap": 0.005899699205784925,
                "high": 3.575000047683716,
                "high_spike": 0.04838708436948114,
                "low": 3.3499999046325684,
                "low_spike": -0.017595360612286837,
                "open": 3.4100000858306885,
                "ret": 0.03225803294049734,
                "session": "REG",
                "volume": 3087000
            },
            {
                "close": 3.5299999713897705,
                "date": "Tue, 18 Mar 2025 13:30:00 GMT",
                "gap": 0.007102299858777528,
                "high": 3.6080000400543213,
                "high_spike": 0.017771498562628496,
                "low": 3.4489998817443848,
                "low_spike": -0.027080449219601177,
                "open": 3.5450000762939453,
                "ret": -0.004231341207714845,
                "session": "REG",
                "volume": 1547200
            },
            {
                "close": 3.490000009536743,
                "date": "Wed, 19 Mar 2025 13:30:00 GMT",
                "gap": -0.008498575533404162,
                "high": 3.575000047683716,
                "high_spike": 0.021428585052490234,
                "low": 3.430000066757202,
                "low_spike": -0.019999980926513672,
                "open": 3.5,
                "ret": -0.0028571401323590484,
                "session": "REG",
                "volume": 1276800
            },
            {
                "close": 3.4700000286102295,
                "date": "Thu, 20 Mar 2025 13:30:00 GMT",
                "gap": -0.011461307089892236,
                "high": 3.5450000762939453,
                "high_spike": 0.02753623979628972,
                "low": 3.421999931335449,
                "low_spike": -0.008115975640946904,
                "open": 3.450000047683716,
                "ret": 0.005797095840604838,
                "session": "REG",
                "volume": 2212800
            },
            {
                "close": 3.549999952316284,
                "date": "Fri, 21 Mar 2025 13:30:00 GMT",
                "gap": 0.03170025769131812,
                "high": 3.6500000953674316,
                "high_spike": 0.01955312099250328,
                "low": 3.4600000381469727,
                "low_spike": -0.03351952182022866,
                "open": 3.5799999237060547,
                "ret": -0.00837988045505711,
                "session": "REG",
                "volume": 6494500
            },
            {
                "close": 3.3499999046325684,
                "date": "Mon, 24 Mar 2025 13:30:00 GMT",
                "gap": 0.04225354855837682,
                "high": 3.700000047683716,
                "high_spike": 0,
                "low": 3.2809998989105225,
                "low_spike": -0.11324328199279265,
                "open": 3.700000047683716,
                "ret": -0.09459463203797946,
                "session": "REG",
                "volume": 4031900
            },
            {
                "close": 3.3399999141693115,
                "date": "Tue, 25 Mar 2025 13:30:00 GMT",
                "gap": -0.020895503055387565,
                "high": 3.440000057220459,
                "high_spike": 0.04878051439826536,
                "low": 3.240000009536743,
                "low_spike": -0.012195110427418387,
                "open": 3.2799999713897705,
                "ret": 0.018292665641127526,
                "session": "REG",
                "volume": 2185500
            },
            {
                "close": 3.240000009536743,
                "date": "Wed, 26 Mar 2025 13:30:00 GMT",
                "gap": -0.002994009197675007,
                "high": 3.375,
                "high_spike": 0.013513536734218068,
                "low": 3.2049999237060547,
                "low_spike": -0.037537538397563686,
                "open": 3.3299999237060547,
                "ret": -0.027027001871263723,
                "session": "REG",
                "volume": 1349400
            },
            {
                "close": 3.309999942779541,
                "date": "Thu, 27 Mar 2025 13:30:00 GMT",
                "gap": -0.012345667202249944,
                "high": 3.3949999809265137,
                "high_spike": 0.06093747823033513,
                "low": 3.200000047683716,
                "low_spike": 0,
                "open": 3.200000047683716,
                "ret": 0.034374966705218446,
                "session": "REG",
                "volume": 1350300
            },
            {
                "close": 3.140000104904175,
                "date": "Fri, 28 Mar 2025 13:30:00 GMT",
                "gap": -0.015105726036447331,
                "high": 3.299999952316284,
                "high_spike": 0.01226992698467555,
                "low": 3.0299999713897705,
                "low_spike": -0.0705521532964184,
                "open": 3.259999990463257,
                "ret": -0.03680978095402687,
                "session": "REG",
                "volume": 2616200
            },
            {
                "close": 3.049999952316284,
                "date": "Mon, 31 Mar 2025 13:30:00 GMT",
                "gap": -0.031847178251670494,
                "high": 3.1500000953674316,
                "high_spike": 0.036184254899580326,
                "low": 3.0399999618530273,
                "low_spike": 0,
                "open": 3.0399999618530273,
                "ret": 0.0032894705884014552,
                "session": "REG",
                "volume": 1403400
            },
            {
                "close": 3.069999933242798,
                "date": "Tue, 01 Apr 2025 13:30:00 GMT",
                "gap": 0.00655737089809616,
                "high": 3.0799999237060547,
                "high_spike": 0.003257325954627577,
                "low": 2.940000057220459,
                "low_spike": -0.04234523741015905,
                "open": 3.069999933242798,
                "ret": 0,
                "session": "REG",
                "volume": 1778900
            },
            {
                "close": 3.0899999141693115,
                "date": "Wed, 02 Apr 2025 13:30:00 GMT",
                "gap": -0.006514651909255265,
                "high": 3.140000104904175,
                "high_spike": 0.02950824721146006,
                "low": 3.0250000953674316,
                "low_spike": -0.008196674537606752,
                "open": 3.049999952316284,
                "ret": 0.013114741796192542,
                "session": "REG",
                "volume": 1184600
            },
            {
                "close": 2.869999885559082,
                "date": "Thu, 03 Apr 2025 13:30:00 GMT",
                "gap": -0.048543644373911676,
                "high": 3,
                "high_spike": 0.020408143405366452,
                "low": 2.809999942779541,
                "low_spike": -0.044217725139714115,
                "open": 2.940000057220459,
                "ret": -0.02380958173434755,
                "session": "REG",
                "volume": 2205900
            },
            {
                "close": 2.869999885559082,
                "date": "Fri, 04 Apr 2025 13:30:00 GMT",
                "gap": -0.04181180848225219,
                "high": 2.9700000286102295,
                "high_spike": 0.08000001040371973,
                "low": 2.619999885559082,
                "low_spike": -0.047272768887606564,
                "open": 2.75,
                "ret": 0.043636322021484375,
                "session": "REG",
                "volume": 3577000
            },
            {
                "close": 2.9000000953674316,
                "date": "Mon, 07 Apr 2025 13:30:00 GMT",
                "gap": -0.059233395349857276,
                "high": 2.990000009536743,
                "high_spike": 0.10740739138201616,
                "low": 2.619999885559082,
                "low_spike": -0.029629689152511185,
                "open": 2.700000047683716,
                "ret": 0.07407409042651403,
                "session": "REG",
                "volume": 2733200
            },
            {
                "close": 2.6700000762939453,
                "date": "Tue, 08 Apr 2025 13:30:00 GMT",
                "gap": 0.018965457424115817,
                "high": 2.9800000190734863,
                "high_spike": 0.008460269378307572,
                "low": 2.630000114440918,
                "low_spike": -0.1099830178193486,
                "open": 2.9549999237060547,
                "ret": -0.09644665136054309,
                "session": "REG",
                "volume": 2336700
            },
            {
                "close": 2.890000104904175,
                "date": "Wed, 09 Apr 2025 13:30:00 GMT",
                "gap": -0.018726662661472826,
                "high": 2.9000000953674316,
                "high_spike": 0.10687031375522382,
                "low": 2.5899999141693115,
                "low_spike": -0.011450371259603576,
                "open": 2.619999885559082,
                "ret": 0.103053523335356,
                "session": "REG",
                "volume": 2396500
            },
            {
                "close": 2.680000066757202,
                "date": "Thu, 10 Apr 2025 13:30:00 GMT",
                "gap": -0.02768171599332392,
                "high": 2.809999942779541,
                "high_spike": 0,
                "low": 2.6500000953674316,
                "low_spike": -0.056939448637085666,
                "open": 2.809999942779541,
                "ret": -0.04626330201763207,
                "session": "REG",
                "volume": 1940600
            },
            {
                "close": 2.7100000381469727,
                "date": "Fri, 11 Apr 2025 13:30:00 GMT",
                "gap": 0,
                "high": 2.73799991607666,
                "high_spike": 0.021641734281610647,
                "low": 2.5999999046325684,
                "low_spike": -0.0298508060193573,
                "open": 2.680000066757202,
                "ret": 0.011194018896451219,
                "session": "REG",
                "volume": 1875100
            },
            {
                "close": 2.700000047683716,
                "date": "Mon, 14 Apr 2025 13:30:00 GMT",
                "gap": 0.018450166646666544,
                "high": 2.7899999618530273,
                "high_spike": 0.01086955488892416,
                "low": 2.6500000953674316,
                "low_spike": -0.03985503459272188,
                "open": 2.759999990463257,
                "ret": -0.02173910977784832,
                "session": "REG",
                "volume": 1763700
            },
            {
                "close": 2.549999952316284,
                "date": "Tue, 15 Apr 2025 13:30:00 GMT",
                "gap": -0.0037037001061669406,
                "high": 2.7249999046325684,
                "high_spike": 0.013011095415467855,
                "low": 2.549999952316284,
                "low_spike": -0.05204464755619187,
                "open": 2.690000057220459,
                "ret": -0.05204464755619187,
                "session": "REG",
                "volume": 1984900
            },
            {
                "close": 2.559999942779541,
                "date": "Wed, 16 Apr 2025 13:30:00 GMT",
                "gap": -0.007843129921765946,
                "high": 2.5950000286102295,
                "high_spike": 0.025691722512057424,
                "low": 2.5,
                "low_spike": -0.011857696335581758,
                "open": 2.5299999713897705,
                "ret": 0.011857696335581869,
                "session": "REG",
                "volume": 1600700
            },
            {
                "close": 2.759999990463257,
                "date": "Thu, 17 Apr 2025 13:30:00 GMT",
                "gap": 0.011718739086063357,
                "high": 2.8450000286102295,
                "high_spike": 0.09845564590402844,
                "low": 2.569999933242798,
                "low_spike": -0.00772200061362871,
                "open": 2.5899999141693115,
                "ret": 0.0656370972693523,
                "session": "REG",
                "volume": 4413900
            },
            {
                "close": 2.6700000762939453,
                "date": "Mon, 21 Apr 2025 13:30:00 GMT",
                "gap": -0.007246369925949403,
                "high": 2.759999990463257,
                "high_spike": 0.007299263086460783,
                "low": 2.575000047683716,
                "low_spike": -0.0602189639703411,
                "open": 2.740000009536743,
                "ret": -0.02554742080261263,
                "session": "REG",
                "volume": 1885100
            },
            {
                "close": 2.615000009536743,
                "date": "Tue, 22 Apr 2025 13:30:00 GMT",
                "gap": 0.00749062934645095,
                "high": 2.757999897003174,
                "high_spike": 0.025278750310874676,
                "low": 2.569999933242798,
                "low_spike": -0.04460971056694163,
                "open": 2.690000057220459,
                "ret": -0.027881058025408523,
                "session": "REG",
                "volume": 1710000
            },
            {
                "close": 2.5899999141693115,
                "date": "Wed, 23 Apr 2025 13:30:00 GMT",
                "gap": 0.028680706466613914,
                "high": 2.696000099182129,
                "high_spike": 0.002230498823063032,
                "low": 2.569999933242798,
                "low_spike": -0.04460971056694163,
                "open": 2.690000057220459,
                "ret": -0.03717477357769139,
                "session": "REG",
                "volume": 2296300
            },
            {
                "close": 2.549999952316284,
                "date": "Thu, 24 Apr 2025 13:30:00 GMT",
                "gap": -0.003861000306814355,
                "high": 2.5910000801086426,
                "high_spike": 0.004263626638711937,
                "low": 2.509999990463257,
                "low_spike": -0.027131757873173123,
                "open": 2.5799999237060547,
                "ret": -0.011627896231359958,
                "session": "REG",
                "volume": 1424400
            },
            {
                "close": 2.5399999618530273,
                "date": "Fri, 25 Apr 2025 13:30:00 GMT",
                "gap": -0.0019607357316996366,
                "high": 2.559999942779541,
                "high_spike": 0.005893856988577584,
                "low": 2.505000114440918,
                "low_spike": -0.015717076877764025,
                "open": 2.5450000762939453,
                "ret": -0.001964681450304373,
                "session": "REG",
                "volume": 1220000
            },
            {
                "close": 2.4600000381469727,
                "date": "Mon, 28 Apr 2025 13:30:00 GMT",
                "gap": -0.007874008357040663,
                "high": 2.5450000762939453,
                "high_spike": 0.009920672839941913,
                "low": 2.4100000858306885,
                "low_spike": -0.04365075235253857,
                "open": 2.5199999809265137,
                "ret": -0.023809501283202916,
                "session": "REG",
                "volume": 2369700
            },
            {
                "close": 2.509999990463257,
                "date": "Tue, 29 Apr 2025 13:30:00 GMT",
                "gap": 0.01016254331755384,
                "high": 2.5299999713897705,
                "high_spike": 0.018108683377715096,
                "low": 2.430000066757202,
                "low_spike": -0.022132728635991472,
                "open": 2.484999895095825,
                "ret": 0.010060400974973627,
                "session": "REG",
                "volume": 2168500
            },
            {
                "close": 2.4800000190734863,
                "date": "Wed, 30 Apr 2025 13:30:00 GMT",
                "gap": -0.01593623984263237,
                "high": 2.5450000762939453,
                "high_spike": 0.030364391423070236,
                "low": 2.4489998817443848,
                "low_spike": -0.008502083652873749,
                "open": 2.4700000286102295,
                "ret": 0.004048579088026694,
                "session": "REG",
                "volume": 1604600
            },
            {
                "close": 2.509999990463257,
                "date": "Thu, 01 May 2025 13:30:00 GMT",
                "gap": 0.004032254188043316,
                "high": 2.549999952316284,
                "high_spike": 0.0240963624697752,
                "low": 2.4700000286102295,
                "low_spike": -0.008032120823258437,
                "open": 2.490000009536743,
                "ret": 0.008032120823258326,
                "session": "REG",
                "volume": 1333300
            },
            {
                "close": 2.515000104904175,
                "date": "Fri, 02 May 2025 13:30:00 GMT",
                "gap": 0.007968119921316186,
                "high": 2.5899999141693115,
                "high_spike": 0.023715392671163515,
                "low": 2.509999990463257,
                "low_spike": -0.007905130890387913,
                "open": 2.5299999713897705,
                "ret": -0.005928801049494115,
                "session": "REG",
                "volume": 1218800
            },
            {
                "close": 2.559999942779541,
                "date": "Mon, 05 May 2025 13:30:00 GMT",
                "gap": 0.0019880221923607166,
                "high": 2.5999999046325684,
                "high_spike": 0.03174600171093722,
                "low": 2.490000009536743,
                "low_spike": -0.011904750641601458,
                "open": 2.5199999809265137,
                "ret": 0.01587300085546861,
                "session": "REG",
                "volume": 1653500
            },
            {
                "close": 2.5199999809265137,
                "date": "Tue, 06 May 2025 13:30:00 GMT",
                "gap": 0.003906246362021193,
                "high": 2.5999999046325684,
                "high_spike": 0.01167314092180427,
                "low": 2.509999990463257,
                "low_spike": -0.02334628184360832,
                "open": 2.569999933242798,
                "ret": -0.0194552348696736,
                "session": "REG",
                "volume": 1315200
            },
            {
                "close": 2.5399999618530273,
                "date": "Wed, 07 May 2025 13:30:00 GMT",
                "gap": 0,
                "high": 2.569999933242798,
                "high_spike": 0.019841251069335764,
                "low": 2.4800000190734863,
                "low_spike": -0.01587300085546861,
                "open": 2.5199999809265137,
                "ret": 0.007936500427734305,
                "session": "REG",
                "volume": 1996000
            },
            {
                "close": 2.3399999141693115,
                "date": "Thu, 08 May 2025 13:30:00 GMT",
                "gap": -0.025590574093174,
                "high": 2.490000009536743,
                "high_spike": 0.00606064867966194,
                "low": 2.2249999046325684,
                "low_spike": -0.10101010490225226,
                "open": 2.4749999046325684,
                "ret": -0.05454545279398648,
                "session": "REG",
                "volume": 3306800
            },
            {
                "close": 2.2799999713897705,
                "date": "Fri, 09 May 2025 13:30:00 GMT",
                "gap": 0.0021368011215048277,
                "high": 2.3450000286102295,
                "high_spike": 0,
                "low": 2.25,
                "low_spike": -0.04051173878515113,
                "open": 2.3450000286102295,
                "ret": -0.027718574169477317,
                "session": "REG",
                "volume": 1770700
            },
            {
                "close": 2.309999942779541,
                "date": "Mon, 12 May 2025 13:30:00 GMT",
                "gap": 0.026315764707210976,
                "high": 2.390000104904175,
                "high_spike": 0.02136760366190571,
                "low": 2.2839999198913574,
                "low_spike": -0.023931622364111838,
                "open": 2.3399999141693115,
                "ret": -0.012820501064172207,
                "session": "REG",
                "volume": 2131700
            },
            {
                "close": 2.509999990463257,
                "date": "Tue, 13 May 2025 13:30:00 GMT",
                "gap": -0.00432900030777672,
                "high": 2.559999942779541,
                "high_spike": 0.11304347645808255,
                "low": 2.299999952316284,
                "low_spike": 0,
                "open": 2.299999952316284,
                "ret": 0.091304366304654,
                "session": "REG",
                "volume": 3954000
            },
            {
                "close": 2.4700000286102295,
                "date": "Wed, 14 May 2025 13:30:00 GMT",
                "gap": -0.01593623984263237,
                "high": 2.494999885559082,
                "high_spike": 0.010121399457197144,
                "low": 2.4000000953674316,
                "low_spike": -0.02834005361618719,
                "open": 2.4700000286102295,
                "ret": 0,
                "session": "REG",
                "volume": 1596800
            },
            {
                "close": 2.4700000286102295,
                "date": "Thu, 15 May 2025 13:30:00 GMT",
                "gap": -0.012145737264080192,
                "high": 2.5,
                "high_spike": 0.02459013990675496,
                "low": 2.359999895095825,
                "low_spike": -0.032786950921536606,
                "open": 2.440000057220459,
                "ret": 0.01229506995337748,
                "session": "REG",
                "volume": 1276500
            },
            {
                "close": 2.7699999809265137,
                "date": "Fri, 16 May 2025 13:30:00 GMT",
                "gap": 0.004048579088026694,
                "high": 2.8299999237060547,
                "high_spike": 0.14112899271804302,
                "low": 2.4539999961853027,
                "low_spike": -0.010483880116217481,
                "open": 2.4800000190734863,
                "ret": 0.11693546758978246,
                "session": "REG",
                "volume": 3844300
            },
            {
                "close": 2.7899999618530273,
                "date": "Mon, 19 May 2025 13:30:00 GMT",
                "gap": -0.03610104885239751,
                "high": 2.809999942779541,
                "high_spike": 0.05243440542515665,
                "low": 2.630000114440918,
                "low_spike": -0.0149812586929019,
                "open": 2.6700000762939453,
                "ret": 0.0449437760787057,
                "session": "REG",
                "volume": 1744400
            },
            {
                "close": 2.9700000286102295,
                "date": "Tue, 20 May 2025 13:30:00 GMT",
                "gap": 0,
                "high": 2.9700000286102295,
                "high_spike": 0.06451615384168385,
                "low": 2.7799999713897705,
                "low_spike": -0.00358422602149977,
                "open": 2.7899999618530273,
                "ret": 0.06451615384168385,
                "session": "REG",
                "volume": 2487900
            },
            {
                "close": 2.9600000381469727,
                "date": "Wed, 21 May 2025 13:30:00 GMT",
                "gap": -0.02020200074126499,
                "high": 3.0999999046325684,
                "high_spike": 0.06529203202674227,
                "low": 2.9000000953674316,
                "low_spike": -0.0034364227382496226,
                "open": 2.9100000858306885,
                "ret": 0.017182113691248002,
                "session": "REG",
                "volume": 2738800
            },
            {
                "close": 2.930000066757202,
                "date": "Thu, 22 May 2025 13:30:00 GMT",
                "gap": 0.0050675223960423565,
                "high": 3.130000114440918,
                "high_spike": 0.05210091253011084,
                "low": 2.9010000228881836,
                "low_spike": -0.02487391062741029,
                "open": 2.9749999046325684,
                "ret": -0.015125996409376063,
                "session": "REG",
                "volume": 2119600
            },
            {
                "close": 2.8499999046325684,
                "date": "Fri, 23 May 2025 13:30:00 GMT",
                "gap": -0.027303808976760324,
                "high": 2.934999942779541,
                "high_spike": 0.02982457578640907,
                "low": 2.7850000858306885,
                "low_spike": -0.022806954728744055,
                "open": 2.8499999046325684,
                "ret": 0,
                "session": "REG",
                "volume": 1575900
            },
            {
                "close": 3.130000114440918,
                "date": "Tue, 27 May 2025 13:30:00 GMT",
                "gap": 0,
                "high": 3.1700000762939453,
                "high_spike": 0.11228076574361578,
                "low": 2.8499999046325684,
                "low_spike": 0,
                "open": 2.8499999046325684,
                "ret": 0.09824569093957503,
                "session": "REG",
                "volume": 3046300
            },
            {
                "close": 3.0299999713897705,
                "date": "Wed, 28 May 2025 13:30:00 GMT",
                "gap": -0.006389846202502492,
                "high": 3.1500000953674316,
                "high_spike": 0.012861801164264719,
                "low": 2.9700000286102295,
                "low_spike": -0.045016035758188355,
                "open": 3.109999895095825,
                "ret": -0.025723449004679044,
                "session": "REG",
                "volume": 2155200
            },
            {
                "close": 2.9800000190734863,
                "date": "Thu, 29 May 2025 13:30:00 GMT",
                "gap": -0.003300326916726104,
                "high": 3.0799999237060547,
                "high_spike": 0.01986753084718007,
                "low": 2.9649999141693115,
                "low_spike": -0.018211942749856713,
                "open": 3.0199999809265137,
                "ret": -0.013245020564786825,
                "session": "REG",
                "volume": 1225200
            },
            {
                "close": 2.930000066757202,
                "date": "Fri, 30 May 2025 13:30:00 GMT",
                "gap": -0.010067104428777118,
                "high": 3.009999990463257,
                "high_spike": 0.020338963325323256,
                "low": 2.9100000858306885,
                "low_spike": -0.013559308883548837,
                "open": 2.950000047683716,
                "ret": -0.006779654441774419,
                "session": "REG",
                "volume": 1237700
            },
            {
                "close": 3.109999895095825,
                "date": "Mon, 02 Jun 2025 13:30:00 GMT",
                "gap": -0.003412965950654212,
                "high": 3.1600000858306885,
                "high_spike": 0.08219178194041366,
                "low": 2.880000114440918,
                "low_spike": -0.01369861671503625,
                "open": 2.9200000762939453,
                "ret": 0.0650684293964221,
                "session": "REG",
                "volume": 1930600
            },
            {
                "close": 3.180000066757202,
                "date": "Tue, 03 Jun 2025 13:30:00 GMT",
                "gap": -0.0032154311255848667,
                "high": 3.2950000762939453,
                "high_spike": 0.0629032831162264,
                "low": 3.0799999237060547,
                "low_spike": -0.0064516069489635175,
                "open": 3.0999999046325684,
                "ret": 0.025806504705075506,
                "session": "REG",
                "volume": 2345700
            },
            {
                "close": 3.25,
                "date": "Wed, 04 Jun 2025 13:30:00 GMT",
                "gap": 0,
                "high": 3.259999990463257,
                "high_spike": 0.025157208184474866,
                "low": 3.119999885559082,
                "low_spike": -0.018867981112750454,
                "open": 3.180000066757202,
                "ret": 0.02201255716141537,
                "session": "REG",
                "volume": 1147200
            },
            {
                "close": 3.0399999618530273,
                "date": "Thu, 05 Jun 2025 13:30:00 GMT",
                "gap": 0.0030769201425404624,
                "high": 3.2699999809265137,
                "high_spike": 0.0030674817461688875,
                "low": 3.0199999809265137,
                "low_spike": -0.07361963504258728,
                "open": 3.259999990463257,
                "ret": -0.06748467155024951,
                "session": "REG",
                "volume": 1667600
            },
            {
                "close": 3.319999933242798,
                "date": "Fri, 06 Jun 2025 13:30:00 GMT",
                "gap": -0.003289470588401344,
                "high": 3.359999895095825,
                "high_spike": 0.10891086693796015,
                "low": 3.0299999713897705,
                "low_spike": 0,
                "open": 3.0299999713897705,
                "ret": 0.09570955927105596,
                "session": "REG",
                "volume": 2667800
            },
            {
                "close": 3.430000066757202,
                "date": "Mon, 09 Jun 2025 13:30:00 GMT",
                "gap": 0,
                "high": 3.4600000381469727,
                "high_spike": 0.04216870714434928,
                "low": 3.2699999809265137,
                "low_spike": -0.015060226904115348,
                "open": 3.319999933242798,
                "ret": 0.03313257100188016,
                "session": "REG",
                "volume": 2061800
            },
            {
                "close": 3.4100000858306885,
                "date": "Tue, 10 Jun 2025 13:30:00 GMT",
                "gap": -0.002915449057909525,
                "high": 3.4800000190734863,
                "high_spike": 0.017543842526623443,
                "low": 3.3529999256134033,
                "low_spike": -0.019590686896459375,
                "open": 3.4200000762939453,
                "ret": -0.0029239737544372035,
                "session": "REG",
                "volume": 1656400
            },
            {
                "close": 3.380000114440918,
                "date": "Wed, 11 Jun 2025 13:30:00 GMT",
                "gap": 0.008797645347408345,
                "high": 3.4649999141693115,
                "high_spike": 0.007267400154944426,
                "low": 3.3299999237060547,
                "low_spike": -0.03197678246647617,
                "open": 3.440000057220459,
                "ret": -0.01744184354113687,
                "session": "REG",
                "volume": 982200
            },
            {
                "close": 3.2699999809265137,
                "date": "Thu, 12 Jun 2025 13:30:00 GMT",
                "gap": -0.020710109257779052,
                "high": 3.359999895095825,
                "high_spike": 0.015105726036447331,
                "low": 3.2100000381469727,
                "low_spike": -0.030211452072894662,
                "open": 3.309999942779541,
                "ret": -0.012084580829157865,
                "session": "REG",
                "volume": 1288600
            },
            {
                "close": 3.1600000858306885,
                "date": "Fri, 13 Jun 2025 13:30:00 GMT",
                "gap": -0.018348606461624728,
                "high": 3.2899999618530273,
                "high_spike": 0.024922094316309096,
                "low": 3.1600000858306885,
                "low_spike": -0.01557630894769324,
                "open": 3.2100000381469727,
                "ret": -0.01557630894769324,
                "session": "REG",
                "volume": 1106500
            },
            {
                "close": 3.299999952316284,
                "date": "Mon, 16 Jun 2025 13:30:00 GMT",
                "gap": 0.003164553858114205,
                "high": 3.4200000762939453,
                "high_spike": 0.07886435141423576,
                "low": 3.1649999618530273,
                "low_spike": -0.0015773231295197476,
                "open": 3.1700000762939453,
                "ret": 0.041009423625731234,
                "session": "REG",
                "volume": 2403400
            },
            {
                "close": 3.2899999618530273,
                "date": "Tue, 17 Jun 2025 13:30:00 GMT",
                "gap": -0.012121200736670112,
                "high": 3.299999952316284,
                "high_spike": 0.01226992698467555,
                "low": 3.2249999046325684,
                "low_spike": -0.010736222678857987,
                "open": 3.259999990463257,
                "ret": 0.009202445238506662,
                "session": "REG",
                "volume": 1612200
            },
            {
                "close": 3.390000104904175,
                "date": "Wed, 18 Jun 2025 13:30:00 GMT",
                "gap": -0.007598740802043036,
                "high": 3.390000104904175,
                "high_spike": 0.03828483797358673,
                "low": 3.2300000190734863,
                "low_spike": -0.010719780920716349,
                "open": 3.265000104904175,
                "ret": 0.03828483797358673,
                "session": "REG",
                "volume": 1322300
            },
            {
                "close": 3.430000066757202,
                "date": "Fri, 20 Jun 2025 13:30:00 GMT",
                "gap": 0,
                "high": 3.609999895095825,
                "high_spike": 0.06489669126363329,
                "low": 3.3299999237060547,
                "low_spike": -0.01769916794731663,
                "open": 3.390000104904175,
                "ret": 0.011799398411569628,
                "session": "REG",
                "volume": 5191400
            },
            {
                "close": 3.440000057220459,
                "date": "Mon, 23 Jun 2025 13:30:00 GMT",
                "gap": -0.014577245289547514,
                "high": 3.4549999237060547,
                "high_spike": 0.022189291930702293,
                "low": 3.2300000190734863,
                "low_spike": -0.044378724937482183,
                "open": 3.380000114440918,
                "ret": 0.017751461759777376,
                "session": "REG",
                "volume": 2357300
            },
            {
                "close": 3.4000000953674316,
                "date": "Tue, 24 Jun 2025 13:30:00 GMT",
                "gap": 0.00872092177056838,
                "high": 3.5,
                "high_spike": 0.008645524824904882,
                "low": 3.380000114440918,
                "low_spike": -0.025936574474714758,
                "open": 3.4700000286102295,
                "ret": -0.020172891258111503,
                "session": "REG",
                "volume": 1190700
            },
            {
                "close": 3.319999933242798,
                "date": "Wed, 25 Jun 2025 13:30:00 GMT",
                "gap": 0.02941173583166079,
                "high": 3.5,
                "high_spike": 0,
                "low": 3.2799999713897705,
                "low_spike": -0.06285715103149414,
                "open": 3.5,
                "ret": -0.051428590502057725,
                "session": "REG",
                "volume": 1092400
            },
            {
                "close": 3.4100000858306885,
                "date": "Thu, 26 Jun 2025 13:30:00 GMT",
                "gap": -0.009036136142469231,
                "high": 3.450000047683716,
                "high_spike": 0.04863224549722234,
                "low": 3.2799999713897705,
                "low_spike": -0.0030395108143480565,
                "open": 3.2899999618530273,
                "ret": 0.03647420223983033,
                "session": "REG",
                "volume": 1243800
            },
            {
                "close": 3.4200000762939453,
                "date": "Fri, 27 Jun 2025 13:30:00 GMT",
                "gap": 0,
                "high": 3.430000066757202,
                "high_spike": 0.005865096898272304,
                "low": 3.3299999237060547,
                "low_spike": -0.02346045751055914,
                "open": 3.4100000858306885,
                "ret": 0.002932548449136041,
                "session": "REG",
                "volume": 3546900
            },
            {
                "close": 3.490000009536743,
                "date": "Mon, 30 Jun 2025 13:30:00 GMT",
                "gap": -0.005847947508874518,
                "high": 3.5299999713897705,
                "high_spike": 0.038235256581159005,
                "low": 3.3499999046325684,
                "low_spike": -0.014705938038939936,
                "open": 3.4000000953674316,
                "ret": 0.026470562248494645,
                "session": "REG",
                "volume": 1614300
            },
            {
                "close": 3.450000047683716,
                "date": "Tue, 01 Jul 2025 13:30:00 GMT",
                "gap": -0.005730653544946063,
                "high": 3.549999952316284,
                "high_spike": 0.02305473286641302,
                "low": 3.4100000858306885,
                "low_spike": -0.017291049649809875,
                "open": 3.4700000286102295,
                "ret": -0.005763683216603255,
                "session": "REG",
                "volume": 1218400
            },
            {
                "close": 3.5799999237060547,
                "date": "Wed, 02 Jul 2025 13:30:00 GMT",
                "gap": -0.002898547920302419,
                "high": 3.5850000381469727,
                "high_spike": 0.04215115654494328,
                "low": 3.424999952316284,
                "low_spike": -0.004360495539146858,
                "open": 3.440000057220459,
                "ret": 0.040697634929319326,
                "session": "REG",
                "volume": 1479900
            },
            {
                "close": 3.569999933242798,
                "date": "Thu, 03 Jul 2025 13:30:00 GMT",
                "gap": 0.0027932934850189994,
                "high": 3.619999885559082,
                "high_spike": 0.008356538191369944,
                "low": 3.549999952316284,
                "low_spike": -0.011142050921826518,
                "open": 3.5899999141693115,
                "ret": -0.005571025460913259,
                "session": "REG",
                "volume": 836500
            },
            {
                "close": 3.509999990463257,
                "date": "Mon, 07 Jul 2025 13:30:00 GMT",
                "gap": -0.0014005255226425817,
                "high": 3.6700000762939453,
                "high_spike": 0.02945302030523722,
                "low": 3.5,
                "low_spike": -0.01823283483230509,
                "open": 3.565000057220459,
                "ret": -0.015427788464072112,
                "session": "REG",
                "volume": 1531600
            },
            {
                "close": 3.5799999237060547,
                "date": "Tue, 08 Jul 2025 13:30:00 GMT",
                "gap": -0.0028490001397227793,
                "high": 3.5999999046325684,
                "high_spike": 0.028571401323590928,
                "low": 3.450000047683716,
                "low_spike": -0.014285700661795464,
                "open": 3.5,
                "ret": 0.02285712105887283,
                "session": "REG",
                "volume": 1040800
            },
            {
                "close": 3.509999990463257,
                "date": "Wed, 09 Jul 2025 13:30:00 GMT",
                "gap": 0.005586586970037999,
                "high": 3.5999999046325684,
                "high_spike": 0,
                "low": 3.4800000190734863,
                "low_spike": -0.033333302427220435,
                "open": 3.5999999046325684,
                "ret": -0.024999976820415326,
                "session": "REG",
                "volume": 1024200
            },
            {
                "close": 3.5899999141693115,
                "date": "Thu, 10 Jul 2025 13:30:00 GMT",
                "gap": 0.005698000279445559,
                "high": 3.619999885559082,
                "high_spike": 0.025495726600212487,
                "low": 3.505000114440918,
                "low_spike": -0.007082112507499572,
                "open": 3.5299999713897705,
                "ret": 0.016997151066808325,
                "session": "REG",
                "volume": 1022000
            },
            {
                "close": 3.509999990463257,
                "date": "Fri, 11 Jul 2025 13:30:00 GMT",
                "gap": -0.008356538191369944,
                "high": 3.578000068664551,
                "high_spike": 0.005056215217507987,
                "low": 3.494999885559082,
                "low_spike": -0.0182584433329257,
                "open": 3.559999942779541,
                "ret": -0.014044930651669008,
                "session": "REG",
                "volume": 910900
            },
            {
                "close": 3.4600000381469727,
                "date": "Mon, 14 Jul 2025 13:30:00 GMT",
                "gap": -0.0028490001397227793,
                "high": 3.5299999713897705,
                "high_spike": 0.008571420397077256,
                "low": 3.4149999618530273,
                "low_spike": -0.024285725184849283,
                "open": 3.5,
                "ret": -0.011428560529436416,
                "session": "REG",
                "volume": 676400
            },
            {
                "close": 3.259999990463257,
                "date": "Tue, 15 Jul 2025 13:30:00 GMT",
                "gap": 0.0028901706222559387,
                "high": 3.505000114440918,
                "high_spike": 0.010086479983317576,
                "low": 3.259999990463257,
                "low_spike": -0.060518742482858046,
                "open": 3.4700000286102295,
                "ret": -0.060518742482858046,
                "session": "REG",
                "volume": 1283400
            },
            {
                "close": 3.3399999141693115,
                "date": "Wed, 16 Jul 2025 13:30:00 GMT",
                "gap": 0.015337408730844437,
                "high": 3.3499999046325684,
                "high_spike": 0.012084580829157865,
                "low": 3.2300000190734863,
                "low_spike": -0.02416916165831573,
                "open": 3.309999942779541,
                "ret": 0.009063435621868399,
                "session": "REG",
                "volume": 1057000
            },
            {
                "close": 3.5,
                "date": "Thu, 17 Jul 2025 13:30:00 GMT",
                "gap": 0,
                "high": 3.555000066757202,
                "high_spike": 0.0643713048242287,
                "low": 3.3399999141693115,
                "low_spike": 0,
                "open": 3.3399999141693115,
                "ret": 0.04790421854561089,
                "session": "REG",
                "volume": 1577300
            },
            {
                "close": 3.5,
                "date": "Fri, 18 Jul 2025 13:30:00 GMT",
                "gap": 0.011428560529436416,
                "high": 3.565000057220459,
                "high_spike": 0.007062173908709557,
                "low": 3.450000047683716,
                "low_spike": -0.02542370484156753,
                "open": 3.5399999618530273,
                "ret": -0.011299424374029976,
                "session": "REG",
                "volume": 1086500
            },
            {
                "close": 4.099999904632568,
                "date": "Mon, 21 Jul 2025 13:30:00 GMT",
                "gap": -0.0014286041259765625,
                "high": 4.559999942779541,
                "high_spike": 0.3047210563928515,
                "low": 3.494999885559082,
                "low_spike": 0,
                "open": 3.494999885559082,
                "ret": 0.17310444603253727,
                "session": "REG",
                "volume": 14632500
            },
            {
                "close": 4.21999979019165,
                "date": "Tue, 22 Jul 2025 13:30:00 GMT",
                "gap": 0.012195168755581687,
                "high": 4.539999961853027,
                "high_spike": 0.09397586928273705,
                "low": 3.9489998817443848,
                "low_spike": -0.04843378530217857,
                "open": 4.150000095367432,
                "ret": 0.01686739595557074,
                "session": "REG",
                "volume": 9681900
            },
            {
                "close": 4.28000020980835,
                "date": "Wed, 23 Jul 2025 13:30:00 GMT",
                "gap": 0.10900475379551655,
                "high": 4.820000171661377,
                "high_spike": 0.029914604371353848,
                "low": 4.179999828338623,
                "low_spike": -0.10683761075638709,
                "open": 4.679999828338623,
                "ret": -0.08547000709448127,
                "session": "REG",
                "volume": 13175900
            },
            {
                "close": 3.8499999046325684,
                "date": "Thu, 24 Jul 2025 13:30:00 GMT",
                "gap": -0.021028072003744236,
                "high": 4.210000038146973,
                "high_spike": 0.004773265072407051,
                "low": 3.7799999713897705,
                "low_spike": -0.0978520477879593,
                "open": 4.190000057220459,
                "ret": -0.08114562003453485,
                "session": "REG",
                "volume": 5107000
            },
            {
                "close": 3.640000104904175,
                "date": "Fri, 25 Jul 2025 13:30:00 GMT",
                "gap": 0,
                "high": 3.859999895095825,
                "high_spike": 0.002597400184666032,
                "low": 3.609999895095825,
                "low_spike": -0.06233766635888993,
                "open": 3.8499999046325684,
                "ret": -0.054545403877986676,
                "session": "REG",
                "volume": 3029900
            },
            {
                "close": 3.390000104904175,
                "date": "Mon, 28 Jul 2025 13:30:00 GMT",
                "gap": 0.002747250048093175,
                "high": 3.6500000953674316,
                "high_spike": 0,
                "low": 3.3499999046325684,
                "low_spike": -0.0821918309305314,
                "open": 3.6500000953674316,
                "ret": -0.0712328722383454,
                "session": "REG",
                "volume": 3269700
            },
            {
                "close": 3.259999990463257,
                "date": "Tue, 29 Jul 2025 13:30:00 GMT",
                "gap": 0.005899699205784925,
                "high": 3.4200000762939453,
                "high_spike": 0.002932548449136041,
                "low": 3.2249999046325684,
                "low_spike": -0.05425225118522348,
                "open": 3.4100000858306885,
                "ret": -0.04398829665451198,
                "session": "REG",
                "volume": 1869700
            },
            {
                "close": 3.240000009536743,
                "date": "Wed, 30 Jul 2025 13:30:00 GMT",
                "gap": 0,
                "high": 3.450000047683716,
                "high_spike": 0.058282226311742846,
                "low": 3.2200000286102295,
                "low_spike": -0.012269926984675661,
                "open": 3.259999990463257,
                "ret": -0.006134963492337775,
                "session": "REG",
                "volume": 2440100
            },
            {
                "close": 3.0399999618530273,
                "date": "Thu, 31 Jul 2025 13:30:00 GMT",
                "gap": 0,
                "high": 3.244999885559082,
                "high_spike": 0.001543171607290672,
                "low": 3.0350000858306885,
                "low_spike": -0.06327158120452159,
                "open": 3.240000009536743,
                "ret": -0.061728409597230804,
                "session": "REG",
                "volume": 2485700
            },
            {
                "close": 2.869999885559082,
                "date": "Fri, 01 Aug 2025 13:30:00 GMT",
                "gap": -0.013157882353605488,
                "high": 3,
                "high_spike": 0,
                "low": 2.8499999046325684,
                "low_spike": -0.05000003178914392,
                "open": 3,
                "ret": -0.04333337148030603,
                "session": "REG",
                "volume": 1948600
            },
            {
                "close": 3.0299999713897705,
                "date": "Mon, 04 Aug 2025 13:30:00 GMT",
                "gap": 0.013937352566762984,
                "high": 3.0399999618530273,
                "high_spike": 0.04467349559724476,
                "low": 2.875,
                "low_spike": -0.012027520549263926,
                "open": 2.9100000858306885,
                "ret": 0.04123707285899503,
                "session": "REG",
                "volume": 2018300
            },
            {
                "close": 3.0999999046325684,
                "date": "Tue, 05 Aug 2025 13:30:00 GMT",
                "gap": 0,
                "high": 3.109999895095825,
                "high_spike": 0.026402615333808388,
                "low": 2.9800000190734863,
                "low_spike": -0.016501634583630298,
                "open": 3.0299999713897705,
                "ret": 0.023102288417082395,
                "session": "REG",
                "volume": 1586700
            },
            {
                "close": 2.9200000762939453,
                "date": "Wed, 06 Aug 2025 13:30:00 GMT",
                "gap": -0.02258062432137231,
                "high": 3.065000057220459,
                "high_spike": 0.011551183551541389,
                "low": 2.9100000858306885,
                "low_spike": -0.03960392300071269,
                "open": 3.0299999713897705,
                "ret": -0.03630359608398659,
                "session": "REG",
                "volume": 2731900
            },
            {
                "close": 2.799999952316284,
                "date": "Thu, 07 Aug 2025 13:30:00 GMT",
                "gap": -0.017123352543991444,
                "high": 2.950000047683716,
                "high_spike": 0.02787462206084701,
                "low": 2.734999895095825,
                "low_spike": -0.04703832607887315,
                "open": 2.869999885559082,
                "ret": -0.0243902216146471,
                "session": "REG",
                "volume": 2704400
            },
            {
                "close": 2.6600000858306885,
                "date": "Fri, 08 Aug 2025 13:30:00 GMT",
                "gap": 0.002857191270712267,
                "high": 2.808000087738037,
                "high_spike": 0,
                "low": 2.6600000858306885,
                "low_spike": -0.05270655173895267,
                "open": 2.808000087738037,
                "ret": -0.05270655173895267,
                "session": "REG",
                "volume": 1659400
            },
            {
                "close": 2.700000047683716,
                "date": "Mon, 11 Aug 2025 13:30:00 GMT",
                "gap": 0,
                "high": 2.7200000286102295,
                "high_spike": 0.02255636873816247,
                "low": 2.609999895095825,
                "low_spike": -0.01879706357951072,
                "open": 2.6600000858306885,
                "ret": 0.015037579158775127,
                "session": "REG",
                "volume": 2586700
            },
            {
                "close": 2.7200000286102295,
                "date": "Tue, 12 Aug 2025 13:30:00 GMT",
                "gap": 0.0037037001061668295,
                "high": 2.809999942779541,
                "high_spike": 0.036900333293332865,
                "low": 2.7100000381469727,
                "low_spike": 0,
                "open": 2.7100000381469727,
                "ret": 0.0036900333293332643,
                "session": "REG",
                "volume": 3051600
            },
            {
                "close": 2.819999933242798,
                "date": "Wed, 13 Aug 2025 13:30:00 GMT",
                "gap": 0.0036764670434088487,
                "high": 2.890000104904175,
                "high_spike": 0.058608089638398475,
                "low": 2.7300000190734863,
                "low_spike": 0,
                "open": 2.7300000190734863,
                "ret": 0.03296700129689234,
                "session": "REG",
                "volume": 1875000
            },
            {
                "close": 2.7899999618530273,
                "date": "Thu, 14 Aug 2025 13:30:00 GMT",
                "gap": -0.024822671950315622,
                "high": 2.8450000286102295,
                "high_spike": 0.03454546494917432,
                "low": 2.7200000286102295,
                "low_spike": -0.010909080505371094,
                "open": 2.75,
                "ret": 0.014545440673828125,
                "session": "REG",
                "volume": 1833800
            },
            {
                "close": 2.5799999237060547,
                "date": "Fri, 15 Aug 2025 13:30:00 GMT",
                "gap": -0.01792113010749863,
                "high": 2.75,
                "high_spike": 0.0036496315432303916,
                "low": 2.569999933242798,
                "low_spike": -0.062043823248996044,
                "open": 2.740000009536743,
                "ret": -0.05839419170576576,
                "session": "REG",
                "volume": 4063400
            },
            {
                "close": 2.5299999713897705,
                "date": "Mon, 18 Aug 2025 13:30:00 GMT",
                "gap": 0.015503861641813277,
                "high": 2.6449999809265137,
                "high_spike": 0.009542021549400426,
                "low": 2.5299999713897705,
                "low_spike": -0.03435111377881084,
                "open": 2.619999885559082,
                "ret": -0.03435111377881084,
                "session": "REG",
                "volume": 1959600
            },
            {
                "close": 2.4600000381469727,
                "date": "Tue, 19 Aug 2025 13:30:00 GMT",
                "gap": 0.003952565445193956,
                "high": 2.5999999046325684,
                "high_spike": 0.023622025071121877,
                "low": 2.440000057220459,
                "low_spike": -0.0393700417852032,
                "open": 2.5399999618530273,
                "ret": -0.03149603342816265,
                "session": "REG",
                "volume": 2134100
            },
            {
                "close": 2.4100000858306885,
                "date": "Wed, 20 Aug 2025 13:30:00 GMT",
                "gap": -0.012195110131936526,
                "high": 2.4649999141693115,
                "high_spike": 0.014403228992012407,
                "low": 2.359999895095825,
                "low_spike": -0.02880665421330264,
                "open": 2.430000066757202,
                "ret": -0.008230444599618192,
                "session": "REG",
                "volume": 1937400
            },
            {
                "close": 2.390000104904175,
                "date": "Thu, 21 Aug 2025 13:30:00 GMT",
                "gap": -0.004149373488428698,
                "high": 2.4100000858306885,
                "high_spike": 0.004166662527455456,
                "low": 2.3499999046325684,
                "low_spike": -0.02083341197834765,
                "open": 2.4000000953674316,
                "ret": -0.004166662527455345,
                "session": "REG",
                "volume": 1366100
            },
            {
                "close": 2.450000047683716,
                "date": "Fri, 22 Aug 2025 13:30:00 GMT",
                "gap": 0.0041840962444885665,
                "high": 2.494999885559082,
                "high_spike": 0.03958324434029081,
                "low": 2.3949999809265137,
                "low_spike": -0.0020833809342630794,
                "open": 2.4000000953674316,
                "ret": 0.020833312637276835,
                "session": "REG",
                "volume": 2125400
            },
            {
                "close": 2.5899999141693115,
                "date": "Mon, 25 Aug 2025 13:30:00 GMT",
                "gap": 0.024489772086439876,
                "high": 2.700000047683716,
                "high_spike": 0.07569723423998576,
                "low": 2.450000047683716,
                "low_spike": -0.023904359763948557,
                "open": 2.509999990463257,
                "ret": 0.03187247968526474,
                "session": "REG",
                "volume": 5885900
            },
            {
                "close": 2.490000009536743,
                "date": "Tue, 26 Aug 2025 13:30:00 GMT",
                "gap": 0.00772200061362871,
                "high": 2.6600000858306885,
                "high_spike": 0.01915716197108419,
                "low": 2.4700000286102295,
                "low_spike": -0.053639797744304385,
                "open": 2.609999895095825,
                "ret": -0.04597696949511809,
                "session": "REG",
                "volume": 2703500
            },
            {
                "close": 2.5899999141693115,
                "date": "Wed, 27 Aug 2025 13:30:00 GMT",
                "gap": 0,
                "high": 2.630000114440918,
                "high_spike": 0.056224941513241866,
                "low": 2.4800000190734863,
                "low_spike": -0.004016060411629163,
                "open": 2.490000009536743,
                "ret": 0.040160604116292076,
                "session": "REG",
                "volume": 1904500
            },
            {
                "close": 2.5399999618530273,
                "date": "Thu, 28 Aug 2025 13:30:00 GMT",
                "gap": 0.003861000306814244,
                "high": 2.609999895095825,
                "high_spike": 0.003846150319251729,
                "low": 2.490000009536743,
                "low_spike": -0.04230765351176824,
                "open": 2.5999999046325684,
                "ret": -0.02307690191550993,
                "session": "REG",
                "volume": 1217900
            },
            {
                "close": 2.5,
                "date": "Fri, 29 Aug 2025 13:30:00 GMT",
                "gap": 0.003937004178520276,
                "high": 2.559999942779541,
                "high_spike": 0.003921564960883028,
                "low": 2.4800000190734863,
                "low_spike": -0.027450954726180976,
                "open": 2.549999952316284,
                "ret": -0.01960782480441492,
                "session": "REG",
                "volume": 1373400
            },
            {
                "close": 2.369999885559082,
                "date": "Tue, 02 Sep 2025 13:30:00 GMT",
                "gap": -0.003999996185302779,
                "high": 2.490000009536743,
                "high_spike": 0,
                "low": 2.359999895095825,
                "low_spike": -0.05220888110161259,
                "open": 2.490000009536743,
                "ret": -0.04819282068998332,
                "session": "REG",
                "volume": 1990700
            },
            {
                "close": 2.319999933242798,
                "date": "Wed, 03 Sep 2025 13:30:00 GMT",
                "gap": 0.00843891152356524,
                "high": 2.430000066757202,
                "high_spike": 0.016736384977954266,
                "low": 2.309999942779541,
                "low_spike": -0.03347286971263186,
                "open": 2.390000104904175,
                "ret": -0.029288773468143292,
                "session": "REG",
                "volume": 1547800
            },
            {
                "close": 2.3499999046325684,
                "date": "Thu, 04 Sep 2025 13:30:00 GMT",
                "gap": -0.004310340840949611,
                "high": 2.380000114440918,
                "high_spike": 0.030303105365945715,
                "low": 2.2899999618530273,
                "low_spike": -0.00865800061555344,
                "open": 2.309999942779541,
                "ret": 0.01731600123110688,
                "session": "REG",
                "volume": 1228900
            },
            {
                "close": 2.4600000381469727,
                "date": "Fri, 05 Sep 2025 13:30:00 GMT",
                "gap": 0,
                "high": 2.4700000286102295,
                "high_spike": 0.05106388461595435,
                "low": 2.3499999046325684,
                "low_spike": 0,
                "open": 2.3499999046325684,
                "ret": 0.04680856935251798,
                "session": "REG",
                "volume": 1592800
            },
            {
                "close": 2.5299999713897705,
                "date": "Mon, 08 Sep 2025 13:30:00 GMT",
                "gap": 0.00406503671064562,
                "high": 2.559000015258789,
                "high_spike": 0.03603238284115995,
                "low": 2.4000000953674316,
                "low_spike": -0.02834005361618719,
                "open": 2.4700000286102295,
                "ret": 0.024291474528160384,
                "session": "REG",
                "volume": 2069900
            },
            {
                "close": 2.5799999237060547,
                "date": "Tue, 09 Sep 2025 13:30:00 GMT",
                "gap": -0.011857696335581758,
                "high": 2.5999999046325684,
                "high_spike": 0.039999961853027344,
                "low": 2.4700000286102295,
                "low_spike": -0.011999988555908225,
                "open": 2.5,
                "ret": 0.031999969482421786,
                "session": "REG",
                "volume": 1227900
            },
            {
                "close": 2.490000009536743,
                "date": "Wed, 10 Sep 2025 13:30:00 GMT",
                "gap": -0.003875965410453319,
                "high": 2.5850000381469727,
                "high_spike": 0.005836616845840803,
                "low": 2.4800000190734863,
                "low_spike": -0.03501942276541248,
                "open": 2.569999933242798,
                "ret": -0.031128375791477758,
                "session": "REG",
                "volume": 1199800
            },
            {
                "close": 2.5999999046325684,
                "date": "Thu, 11 Sep 2025 13:30:00 GMT",
                "gap": 0.008032120823258326,
                "high": 2.619999885559082,
                "high_spike": 0.04382465956723891,
                "low": 2.494999885559082,
                "low_spike": -0.005976137434728135,
                "open": 2.509999990463257,
                "ret": 0.035856539645922725,
                "session": "REG",
                "volume": 2340600
            },
            {
                "close": 2.680000066757202,
                "date": "Fri, 12 Sep 2025 13:30:00 GMT",
                "gap": 0,
                "high": 2.690000057220459,
                "high_spike": 0.03461544457272181,
                "low": 2.5299999713897705,
                "low_spike": -0.026923052234761657,
                "open": 2.5999999046325684,
                "ret": 0.03076929425347008,
                "session": "REG",
                "volume": 1685000
            },
            {
                "close": 2.799999952316284,
                "date": "Mon, 15 Sep 2025 13:30:00 GMT",
                "gap": -0.026119466387206858,
                "high": 2.819999933242798,
                "high_spike": 0.08045978796457476,
                "low": 2.5899999141693115,
                "low_spike": -0.007662828249186293,
                "open": 2.609999895095825,
                "ret": 0.07279695971538858,
                "session": "REG",
                "volume": 3262000
            },
            {
                "close": 2.7100000381469727,
                "date": "Tue, 16 Sep 2025 13:30:00 GMT",
                "gap": 0.003571425226269964,
                "high": 2.8299999237060547,
                "high_spike": 0.007117431079635805,
                "low": 2.700000047683716,
                "low_spike": -0.039145870937996374,
                "open": 2.809999942779541,
                "ret": -0.03558715539817858,
                "session": "REG",
                "volume": 1857700
            },
            {
                "close": 2.7300000190734863,
                "date": "Wed, 17 Sep 2025 13:30:00 GMT",
                "gap": -0.0036900333293332643,
                "high": 2.8350000381469727,
                "high_spike": 0.04999999558484114,
                "low": 2.621000051498413,
                "low_spike": -0.029259257329671384,
                "open": 2.700000047683716,
                "ret": 0.01111110031850071,
                "session": "REG",
                "volume": 3122600
            },
            {
                "close": 2.7699999809265137,
                "date": "Thu, 18 Sep 2025 13:30:00 GMT",
                "gap": 0.010989000432297447,
                "high": 2.930000066757202,
                "high_spike": 0.061594230754113743,
                "low": 2.734999895095825,
                "low_spike": -0.009058005599208552,
                "open": 2.759999990463257,
                "ret": 0.003623184962974646,
                "session": "REG",
                "volume": 3905200
            },
            {
                "close": 2.8299999237060547,
                "date": "Fri, 19 Sep 2025 13:30:00 GMT",
                "gap": 0.010830314655719375,
                "high": 2.9200000762939453,
                "high_spike": 0.04285718786473258,
                "low": 2.7699999809265137,
                "low_spike": -0.01071427567880967,
                "open": 2.799999952316284,
                "ret": 0.01071427567880967,
                "session": "REG",
                "volume": 2134200
            },
            {
                "close": 2.8399999141693115,
                "date": "Mon, 22 Sep 2025 13:30:00 GMT",
                "gap": 0,
                "high": 2.8399999141693115,
                "high_spike": 0.0035335656299810836,
                "low": 2.7149999141693115,
                "low_spike": -0.04063604686820754,
                "open": 2.8299999237060547,
                "ret": 0.0035335656299810836,
                "session": "REG",
                "volume": 1708800
            },
            {
                "close": 2.8499999046325684,
                "date": "Tue, 23 Sep 2025 13:30:00 GMT",
                "gap": 0,
                "high": 2.9800000190734863,
                "high_spike": 0.04929581307579878,
                "low": 2.8299999237060547,
                "low_spike": -0.003521123508970825,
                "open": 2.8399999141693115,
                "ret": 0.003521123508970936,
                "session": "REG",
                "volume": 2292200
            },
            {
                "close": 2.9000000953674316,
                "date": "Wed, 24 Sep 2025 13:30:00 GMT",
                "gap": -0.010526306103030625,
                "high": 2.990000009536743,
                "high_spike": 0.06028371642493524,
                "low": 2.759999990463257,
                "low_spike": -0.02127657595741339,
                "open": 2.819999933242798,
                "ret": 0.028368852488815266,
                "session": "REG",
                "volume": 2181300
            },
            {
                "close": 2.8299999237060547,
                "date": "Thu, 25 Sep 2025 13:30:00 GMT",
                "gap": -0.02068971697413624,
                "high": 2.890000104904175,
                "high_spike": 0.0176057014950608,
                "low": 2.7300000190734863,
                "low_spike": -0.03873235859867963,
                "open": 2.8399999141693115,
                "ret": -0.003521123508970825,
                "session": "REG",
                "volume": 2471500
            },
            {
                "close": 2.8499999046325684,
                "date": "Fri, 26 Sep 2025 13:30:00 GMT",
                "gap": 0,
                "high": 2.890000104904175,
                "high_spike": 0.021201478026736664,
                "low": 2.7799999713897705,
                "low_spike": -0.01766782814990553,
                "open": 2.8299999237060547,
                "ret": 0.007067131259962167,
                "session": "REG",
                "volume": 1256700
            },
            {
                "close": 1.8200000524520874,
                "date": "Mon, 29 Sep 2025 13:30:00 GMT",
                "gap": -0.5543859566934806,
                "high": 2.2200000286102295,
                "high_spike": 0.7480315448435317,
                "low": 1.2300000190734863,
                "low_spike": -0.03149603342816265,
                "open": 1.2699999809265137,
                "ret": 0.4330709289651544,
                "session": "REG",
                "volume": 65310400
            },
            {
                "close": 1.8899999856948853,
                "date": "Tue, 30 Sep 2025 13:30:00 GMT",
                "gap": -0.0054945655957939765,
                "high": 1.9299999475479126,
                "high_spike": 0.06629834727181949,
                "low": 1.659999966621399,
                "low_spike": -0.08287291762440252,
                "open": 1.809999942779541,
                "ret": 0.04419892013504234,
                "session": "REG",
                "volume": 13954100
            },
            {
                "close": 2.309999942779541,
                "date": "Wed, 01 Oct 2025 13:30:00 GMT",
                "gap": 0.03968256521237001,
                "high": 2.430000066757202,
                "high_spike": 0.23664123434088946,
                "low": 1.9500000476837158,
                "low_spike": -0.007633580376634641,
                "open": 1.965000033378601,
                "ret": 0.17557246999520437,
                "session": "REG",
                "volume": 20834000
            },
            {
                "close": 2.3299999237060547,
                "date": "Thu, 02 Oct 2025 13:30:00 GMT",
                "gap": 0.012987000923330161,
                "high": 2.490000009536743,
                "high_spike": 0.0641026072091464,
                "low": 2.299999952316284,
                "low_spike": -0.017094001418896276,
                "open": 2.3399999141693115,
                "ret": -0.004273500354724069,
                "session": "REG",
                "volume": 9679900
            },
            {
                "close": 2.569999933242798,
                "date": "Fri, 03 Oct 2025 13:30:00 GMT",
                "gap": 0.008583683082144411,
                "high": 2.6500000953674316,
                "high_spike": 0.12765966081252644,
                "low": 2.3499999046325684,
                "low_spike": 0,
                "open": 2.3499999046325684,
                "ret": 0.09361703725031734,
                "session": "REG",
                "volume": 9492500
            },
            {
                "close": 2.3499999046325684,
                "date": "Mon, 06 Oct 2025 13:30:00 GMT",
                "gap": 0.01167314092180427,
                "high": 2.630000114440918,
                "high_spike": 0.011538542657211881,
                "low": 2.2850000858306885,
                "low_spike": -0.1211537809061557,
                "open": 2.5999999046325684,
                "ret": -0.09615384968074836,
                "session": "REG",
                "volume": 8276700
            },
            {
                "close": 2.180000066757202,
                "date": "Tue, 07 Oct 2025 13:30:00 GMT",
                "gap": 0.017021362508463866,
                "high": 2.390000104904175,
                "high_spike": 0,
                "low": 2.109999895095825,
                "low_spike": -0.1171548943591264,
                "open": 2.390000104904175,
                "ret": -0.08786612089098311,
                "session": "REG",
                "volume": 6539200
            },
            {
                "close": 2.0799999237060547,
                "date": "Wed, 08 Oct 2025 13:30:00 GMT",
                "gap": 0.009174302896359121,
                "high": 2.2200000286102295,
                "high_spike": 0.009090900224102638,
                "low": 2.0399999618530273,
                "low_spike": -0.07272731016490008,
                "open": 2.200000047683716,
                "ret": -0.05454550971669481,
                "session": "REG",
                "volume": 6829300
            },
            {
                "close": 1.9700000286102295,
                "date": "Thu, 09 Oct 2025 13:30:00 GMT",
                "gap": -0.0096153757981291,
                "high": 2.069999933242798,
                "high_spike": 0.004854364437391068,
                "low": 1.9500000476837158,
                "low_spike": -0.053398008811302855,
                "open": 2.059999942779541,
                "ret": -0.0436892799365205,
                "session": "REG",
                "volume": 8919800
            },
            {
                "close": 2.009999990463257,
                "date": "Fri, 10 Oct 2025 13:30:00 GMT",
                "gap": 0.020304548869091166,
                "high": 2.2799999713897705,
                "high_spike": 0.13432834935699933,
                "low": 1.9950000047683716,
                "low_spike": -0.007462679485599422,
                "open": 2.009999990463257,
                "ret": 0,
                "session": "REG",
                "volume": 14533500
            },
            {
                "close": 1.034999966621399,
                "date": "Mon, 13 Oct 2025 13:30:00 GMT",
                "gap": -0.5781094557164769,
                "high": 1.1200000047683716,
                "high_spike": 0.3207547382003011,
                "low": 0.8450000286102295,
                "low_spike": -0.0035376903438857354,
                "open": 0.8479999899864197,
                "ret": 0.22051884297542745,
                "session": "REG",
                "volume": 128357700
            },
            {
                "close": 0.781000018119812,
                "date": "Tue, 14 Oct 2025 13:30:00 GMT",
                "gap": -0.11207723748645071,
                "high": 0.9259999990463257,
                "high_spike": 0.007616941520386611,
                "low": 0.7699999809265137,
                "low_spike": -0.1621328007008831,
                "open": 0.9190000295639038,
                "ret": -0.15016322851434227,
                "session": "REG",
                "volume": 113067200
            },
            {
                "close": 0.6700000166893005,
                "date": "Wed, 15 Oct 2025 13:30:00 GMT",
                "gap": 0.007682435618208583,
                "high": 0.8180000185966492,
                "high_spike": 0.03939011194539943,
                "low": 0.6510000228881836,
                "low_spike": -0.17280810356575893,
                "open": 0.7870000004768372,
                "ret": -0.1486657988775696,
                "session": "REG",
                "volume": 120425700
            },
            {
                "close": 0.5199999809265137,
                "date": "Thu, 16 Oct 2025 13:30:00 GMT",
                "gap": 0.034328360200645225,
                "high": 0.6930000185966492,
                "high_spike": 0,
                "low": 0.5,
                "low_spike": -0.2784992978607438,
                "open": 0.6930000185966492,
                "ret": -0.24963929729824108,
                "session": "REG",
                "volume": 174262400
            },
            {
                "close": 0.6460000276565552,
                "date": "Fri, 17 Oct 2025 13:30:00 GMT",
                "gap": 0.16923077452112256,
                "high": 0.753000020980835,
                "high_spike": 0.23848691643693232,
                "low": 0.550000011920929,
                "low_spike": -0.09539468814760621,
                "open": 0.6079999804496765,
                "ret": 0.06250007965259119,
                "session": "REG",
                "volume": 438222600
            },
            {
                "close": 1.4700000286102295,
                "date": "Mon, 20 Oct 2025 13:30:00 GMT",
                "gap": 0.5789472712976336,
                "high": 1.5299999713897705,
                "high_spike": 0.5,
                "low": 0.8809999823570251,
                "low_spike": -0.1362745109497241,
                "open": 1.0199999809265137,
                "ret": 0.44117652558675524,
                "session": "REG",
                "volume": 1202828700
            },
            {
                "close": 3.619999885559082,
                "date": "Tue, 21 Oct 2025 13:30:00 GMT",
                "gap": 0.571428501918783,
                "high": 3.859999895095825,
                "high_spike": 0.6709956669744435,
                "low": 1.9299999475479126,
                "low_spike": -0.16450216651277827,
                "open": 2.309999942779541,
                "ret": 0.5670995563762935,
                "session": "REG",
                "volume": 2071569300
            },
            {
                "close": 3.5799999237060547,
                "date": "Wed, 22 Oct 2025 13:30:00 GMT",
                "gap": 0.7044199644611411,
                "high": 7.690000057220459,
                "high_spike": 0.24635331639080182,
                "low": 2.619999885559082,
                "low_spike": -0.5753646915458706,
                "open": 6.170000076293945,
                "ret": -0.41977311516397786,
                "session": "REG",
                "volume": 2180713900
            }
        ],
        "canonical": "https://www.benzinga.com/quote/BYND",
        "cashAndCashEquivalents": 103497000,
        "change": -0.039999961853027344,
        "changePercent": -17.18,
        "change_percent": -1.1,
        "city": "El Segundo",
        "classificationStandard": "MS",
        "closeDate": "2025-10-23T17:00:00.000-04:00",
        "companyStandardName": "Beyond Meat Inc",
        "company_name": "Beyond Meat Inc",
        "company_officers": [
            {
                "age": 43,
                "birth": 1981,
                "exercised_value": 0,
                "name": "Mr. Lubi  Kutua",
                "pay": 405417,
                "title": "CFO & Treasurer",
                "unexercised_value": 0,
                "year": 2024
            },
            {
                "age": 56,
                "birth": 1968,
                "exercised_value": 0,
                "name": "Ms. Teri L. Witteman Esq., J.D.",
                "pay": 432105,
                "title": "Chief Legal Officer & Secretary",
                "unexercised_value": 0,
                "year": 2024
            },
            {
                "age": 49,
                "birth": 1975,
                "exercised_value": 0,
                "name": "Dr. Dariush  Ajami Ph.D.",
                "pay": 455880,
                "title": "Chief Innovation Officer",
                "unexercised_value": 0,
                "year": 2024
            },
            {
                "age": 47,
                "birth": 1977,
                "exercised_value": 0,
                "name": "Mr. Yi  Luo",
                "pay": None,
                "title": "VP, Corporate Controller & Principal Accounting Officer",
                "unexercised_value": 0,
                "year": 2024
            },
            {
                "age": None,
                "birth": None,
                "exercised_value": 0,
                "name": "Paul  Sheppard",
                "pay": None,
                "title": "Vice President of Financial Planning & Analysis and Investor Relations",
                "unexercised_value": 0,
                "year": 2024
            },
            {
                "age": None,
                "birth": None,
                "exercised_value": 0,
                "name": "Ms. Shira  Zackai",
                "pay": None,
                "title": "Head of Communications & VP",
                "unexercised_value": 0,
                "year": 2024
            }
        ],
        "compensation_as_of_epoch_date": "Tue, 31 Dec 2024 01:00:00 GMT",
        "compensation_risk": 9,
        "country": "USA",
        "currency": "USD",
        "currentRatio": 3.294654,
        "current_price": 2.965,
        "dataId": "current_ratio",
        "dataValue": 4.281384,
        "dateCreated": "2019-01-01T01:01:01",
        "dateUpdated": "2025-10-22T16:59:44.340-04:00",
        "day_range_high": 0,
        "day_range_low": 0,
        "description": "Beyond Meat, Inc., a plant-based meat company, engages in the development, manufacture, marketing, and sale of plant-based meat products under the Beyond brand name in the United States and internationally. The company sells a range of plant-based meat products that replicates beef, pork, and poultry meats. It sells its products through grocery, mass merchandiser, club stores, and natural retailer channels, as well as various food-away-from-home channels, including restaurants, foodservice outlets, and schools. The company was formerly known as Savage River, Inc. and changed its name to Beyond Meat, Inc. in September 2018. The company was incorporated in 2008 and is headquartered in El Segundo, California.",
        "dividend_yield": 0,
        "dxSymbol": "BYND",
        "ebitdaMargin": -0.40745,
        "employees": 754,
        "eps": -2.13,
        "ethPrice": 2.965,
        "ethTime": 1761215084804,
        "ethVolume": 30375943,
        "exchange": "NASDAQ",
        "executive_team": [],
        "fiftyDayAveragePrice": 2.3492,
        "fiftyTwoWeekHigh": 7.69,
        "fiftyTwoWeekLow": 0.5001,
        "full_time_employees": 754,
        "governance_epoch_date": "Wed, 01 Oct 2025 02:00:00 GMT",
        "grossMargin": 0.127734,
        "groupCode": 20525040,
        "groupName": "INDUSTRY",
        "hundredDayAveragePrice": 2.8508,
        "image": "https://image-util.benzinga.com/api/v2/logos/file/image/1655210/mark_composite_light__bc98b537f73f9f17de3bc34a9d21f584.png?height=60&max_width=&width=60&x-bz-cred=sb~Um8hL4rxuMuGG8BZOW-1uf0KJd_liVZQ_414v89C-_MblxMXm5gTmjh-M_HfKGdA35JQq5HjVBZjKe_pMCFDvcCyZ9fFlaLttuQq-Y9XiguAOczpgFAOeMQ3Yh_GHl4XEHVpBHrukprO2s0da1hR5hRAyfag&x-bz-exp=1761302385&x-bz-security-isin=US08862E1091&x-bz-security-symbol=BYND&x-bz-signature=d2aea1ccb7dbd15cdc8fdac83b5ba341b91aa45ee6fe9e004f67790d96b0307c",
        "industry": "Packaged Foods",
        "industry_disp": "Packaged Foods",
        "industry_key": "packaged-foods",
        "insiders": [
            {
                "#Shares": 492,
                "#Shares Total": 41701,
                "Cost": 2.86,
                "Date": "Thu, 25 Sep 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Director",
                "SEC Form 4": "Fri, 26 Sep 2025 18:57:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000162826425000005/xslF345X05/wk-form4_1758927427.xml",
                "Transaction": "Sale",
                "Value ($)": 1407
            },
            {
                "#Shares": 492,
                "#Shares Total": None,
                "Cost": 2.86,
                "Date": "Thu, 25 Sep 2025 00:00:00 GMT",
                "Insider Trading": "Chelsea A Grayson",
                "Relationship": "Officer",
                "SEC Form 4": "Thu, 25 Sep 2025 10:53:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1655210/000162828025042716/xsl144X01/primary_doc.xml",
                "Transaction": "Proposed Sale",
                "Value ($)": 1407
            },
            {
                "#Shares": 492,
                "#Shares Total": 42193,
                "Cost": 2.6,
                "Date": "Tue, 26 Aug 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Director",
                "SEC Form 4": "Wed, 27 Aug 2025 19:09:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000165521025000166/xslF345X05/wk-form4_1756336181.xml",
                "Transaction": "Sale",
                "Value ($)": 1279
            },
            {
                "#Shares": 492,
                "#Shares Total": None,
                "Cost": 2.56,
                "Date": "Tue, 26 Aug 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Officer",
                "SEC Form 4": "Tue, 26 Aug 2025 10:31:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000200731725000965/xsl144X01/primary_doc.xml",
                "Transaction": "Proposed Sale",
                "Value ($)": 1259
            },
            {
                "#Shares": 492,
                "#Shares Total": 42685,
                "Cost": 3.85,
                "Date": "Fri, 25 Jul 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Director",
                "SEC Form 4": "Mon, 28 Jul 2025 18:48:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000165521025000146/xslF345X05/wk-form4_1753742932.xml",
                "Transaction": "Sale",
                "Value ($)": 1894
            },
            {
                "#Shares": 492,
                "#Shares Total": None,
                "Cost": 3.85,
                "Date": "Fri, 25 Jul 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Officer",
                "SEC Form 4": "Fri, 25 Jul 2025 13:45:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000200731725000754/xsl144X01/primary_doc.xml",
                "Transaction": "Proposed Sale",
                "Value ($)": 1894
            },
            {
                "#Shares": 492,
                "#Shares Total": 43177,
                "Cost": 3.5,
                "Date": "Wed, 25 Jun 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Director",
                "SEC Form 4": "Thu, 26 Jun 2025 18:44:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000165521025000131/xslF345X05/wk-form4_1750977877.xml",
                "Transaction": "Sale",
                "Value ($)": 1722
            },
            {
                "#Shares": 492,
                "#Shares Total": None,
                "Cost": 3.46,
                "Date": "Wed, 25 Jun 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Officer",
                "SEC Form 4": "Wed, 25 Jun 2025 15:36:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000200731725000636/xsl144X01/primary_doc.xml",
                "Transaction": "Proposed Sale",
                "Value ($)": 1702
            },
            {
                "#Shares": 1125,
                "#Shares Total": 43669,
                "Cost": 3.11,
                "Date": "Wed, 28 May 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Director",
                "SEC Form 4": "Thu, 29 May 2025 18:36:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000165521025000109/xslF345X05/wk-form4_1748558206.xml",
                "Transaction": "Sale",
                "Value ($)": 3499
            },
            {
                "#Shares": 1125,
                "#Shares Total": None,
                "Cost": 3.11,
                "Date": "Wed, 28 May 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Officer",
                "SEC Form 4": "Wed, 28 May 2025 13:41:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000200731725000450/xsl144X01/primary_doc.xml",
                "Transaction": "Proposed Sale",
                "Value ($)": 3499
            },
            {
                "#Shares": 1125,
                "#Shares Total": 44794,
                "Cost": 2.54,
                "Date": "Fri, 25 Apr 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Director",
                "SEC Form 4": "Mon, 28 Apr 2025 20:07:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000165521025000087/xslF345X05/wk-form4_1745885230.xml",
                "Transaction": "Sale",
                "Value ($)": 2858
            },
            {
                "#Shares": 1125,
                "#Shares Total": None,
                "Cost": 2.5,
                "Date": "Fri, 25 Apr 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Officer",
                "SEC Form 4": "Mon, 28 Apr 2025 16:29:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000200731725000265/xsl144X01/primary_doc.xml",
                "Transaction": "Proposed Sale",
                "Value ($)": 2817
            },
            {
                "#Shares": 18849,
                "#Shares Total": None,
                "Cost": 2.69,
                "Date": "Thu, 10 Apr 2025 00:00:00 GMT",
                "Insider Trading": "Oghoghomeh Akerho",
                "Relationship": "Former Officer Subject to Rule",
                "SEC Form 4": "Thu, 10 Apr 2025 13:22:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1655210/000197185725000187/xsl144X01/primary_doc.xml",
                "Transaction": "Proposed Sale",
                "Value ($)": 50774
            },
            {
                "#Shares": 1110,
                "#Shares Total": 45919,
                "Cost": 3.28,
                "Date": "Tue, 25 Mar 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Director",
                "SEC Form 4": "Thu, 27 Mar 2025 20:00:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000165521025000066/xslF345X05/wk-form4_1743120002.xml",
                "Transaction": "Sale",
                "Value ($)": 3641
            },
            {
                "#Shares": 1110,
                "#Shares Total": None,
                "Cost": 3.28,
                "Date": "Tue, 25 Mar 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Officer",
                "SEC Form 4": "Tue, 25 Mar 2025 13:09:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000197185725000128/xsl144X01/primary_doc.xml",
                "Transaction": "Proposed Sale",
                "Value ($)": 3641
            },
            {
                "#Shares": 3330,
                "#Shares Total": 47029,
                "Cost": 3.29,
                "Date": "Thu, 13 Mar 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Director",
                "SEC Form 4": "Fri, 14 Mar 2025 19:48:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000165521025000059/xslF345X05/wk-form4_1741996077.xml",
                "Transaction": "Sale",
                "Value ($)": 10956
            },
            {
                "#Shares": 3330,
                "#Shares Total": None,
                "Cost": 3.29,
                "Date": "Thu, 13 Mar 2025 00:00:00 GMT",
                "Insider Trading": "GRAYSON CHELSEA A",
                "Relationship": "Officer",
                "SEC Form 4": "Thu, 13 Mar 2025 14:44:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1628264/000200269825000068/xsl144X01/primary_doc.xml",
                "Transaction": "Proposed Sale",
                "Value ($)": 10956
            },
            {
                "#Shares": 492877,
                "#Shares Total": 2016288,
                "Cost": 0.93,
                "Date": "Fri, 13 Dec 2024 00:00:00 GMT",
                "Insider Trading": "Brown Ethan",
                "Relationship": "President, Chief Exec. Officer",
                "SEC Form 4": "Mon, 16 Dec 2024 20:04:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1655210/000165521024000282/xslF345X05/wk-form4_1734397446.xml",
                "Transaction": "Option Exercise",
                "Value ($)": 458376
            },
            {
                "#Shares": 473129,
                "#Shares Total": 1686804,
                "Cost": 0.93,
                "Date": "Thu, 12 Dec 2024 00:00:00 GMT",
                "Insider Trading": "Brown Ethan",
                "Relationship": "President, Chief Exec. Officer",
                "SEC Form 4": "Mon, 16 Dec 2024 20:04:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1655210/000165521024000282/xslF345X05/wk-form4_1734397446.xml",
                "Transaction": "Option Exercise",
                "Value ($)": 440010
            },
            {
                "#Shares": 313000,
                "#Shares Total": 1703288,
                "Cost": 3.75,
                "Date": "Fri, 13 Dec 2024 00:00:00 GMT",
                "Insider Trading": "Brown Ethan",
                "Relationship": "President, Chief Exec. Officer",
                "SEC Form 4": "Mon, 16 Dec 2024 20:04:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1655210/000165521024000282/xslF345X05/wk-form4_1734397446.xml",
                "Transaction": "Sale",
                "Value ($)": 1173093
            },
            {
                "#Shares": 162772,
                "#Shares Total": 1524032,
                "Cost": 3.92,
                "Date": "Thu, 12 Dec 2024 00:00:00 GMT",
                "Insider Trading": "Brown Ethan",
                "Relationship": "President, Chief Exec. Officer",
                "SEC Form 4": "Mon, 16 Dec 2024 20:04:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1655210/000165521024000282/xslF345X05/wk-form4_1734397446.xml",
                "Transaction": "Sale",
                "Value ($)": 637301
            },
            {
                "#Shares": 313000,
                "#Shares Total": None,
                "Cost": 3.75,
                "Date": "Fri, 13 Dec 2024 00:00:00 GMT",
                "Insider Trading": "Brown Ethan",
                "Relationship": "Officer",
                "SEC Form 4": "Fri, 13 Dec 2024 16:19:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1655210/000197185724000840/xsl144X01/primary_doc.xml",
                "Transaction": "Proposed Sale",
                "Value ($)": 1173093
            },
            {
                "#Shares": 162772,
                "#Shares Total": None,
                "Cost": 3.91,
                "Date": "Thu, 12 Dec 2024 00:00:00 GMT",
                "Insider Trading": "Brown Ethan",
                "Relationship": "Officer",
                "SEC Form 4": "Thu, 12 Dec 2024 16:19:00 GMT",
                "SEC URL": "http://www.sec.gov/Archives/edgar/data/1655210/000197185724000827/xsl144X01/primary_doc.xml",
                "Transaction": "Proposed Sale",
                "Value ($)": 636863
            }
        ],
        "insiders_pct": 0.04765,
        "institutional_pct": 0.3195,
        "isoExchange": "XNAS",
        "issuerName": "Beyond Meat Inc",
        "issuerShortName": "Beyond Meat",
        "language": "en",
        "lastTradePrice": 2.965,
        "lastTradeTime": 1761215084804,
        "last_trade_time": 1761215084804,
        "last_updated": "2025-10-23T12:40:04.095722",
        "longTermDebt": 1194111000,
        "long_business_summary": "Beyond Meat, Inc., a plant-based meat company, engages in the development, manufacture, marketing, and sale of plant-based meat products under the Beyond brand name in the United States and internationally. The company sells a range of plant-based meat products that replicates beef, pork, and poultry meats. It sells its products through grocery, mass merchandiser, club stores, and natural retailer channels, as well as various food-away-from-home channels, including restaurants, foodservice outlets, and schools. The company was formerly known as Savage River, Inc. and changed its name to Beyond Meat, Inc. in September 2018. The company was incorporated in 2008 and is headquartered in El Segundo, California.",
        "marketCap": 1178905943,
        "market_cap": 1178905943,
        "max_age": 86400,
        "mean": 2.05,
        "median": 1.3,
        "name": "Beyond Meat",
        "news": [
            {
                "Date": "2025-10-23 05:14:00",
                "Header": "Tesla shares dip after earnings, and other early market movers",
                "Source": "(MarketWatch)",
                "URL": "https://www.marketwatch.com/livecoverage/stock-market-today-sp500-nasdaq-dow-to-open-near-records-treasury-4-resla-falls/card/tesla-shares-dip-after-earnings-and-other-early-market-movers-moB8As1r9oBIyaKPdA91?mod=mw_FV"
            },
            {
                "Date": "2025-10-23 04:32:00",
                "Header": "Beyond Meat Stocks Wild Ride Triggers a Short-Seller Frenzy",
                "Source": "(Bloomberg)",
                "URL": "https://finance.yahoo.com/news/beyond-meat-stock-wild-ride-083221485.html"
            },
            {
                "Date": "2025-10-22 16:49:00",
                "Header": "Hot-Money Retail Traders Turn Momentum Chasers Into Bagholders",
                "Source": "(Bloomberg)",
                "URL": "https://finance.yahoo.com/news/hot-money-retail-traders-turn-204939598.html"
            },
            {
                "Date": "2025-10-22 15:35:00",
                "Header": "Beyond Meat Goes Meme: Traders Pile Into Struggling Faux Meat Shares",
                "Source": "(The Wall Street Journal)",
                "URL": "https://www.wsj.com/finance/stocks/beyond-meat-goes-meme-traders-pile-into-struggling-faux-meat-shares-0d845d68?mod=wsj_FV"
            },
            {
                "Date": "2025-10-22 14:27:00",
                "Header": "Beyond Meat Explodes 1,100% in Meme-Fueled Frenzy -- What's Really Driving the Surge?",
                "Source": "(GuruFocus.com)",
                "URL": "https://finance.yahoo.com/news/beyond-meat-explodes-1-100-182715341.html"
            },
            {
                "Date": "2025-10-22 14:01:00",
                "Header": "Beyond Meat Soars After MEME ETF Inclusion Sparks Short Squeeze",
                "Source": "(Benzinga)",
                "URL": "https://finance.yahoo.com/news/beyond-meat-soars-meme-etf-180109997.html"
            },
            {
                "Date": "2025-10-22 12:48:00",
                "Header": "Beyond Meat Stock Goes On a Wild Ride",
                "Source": "(The Wall Street Journal)",
                "URL": "https://www.wsj.com/livecoverage/stock-market-today-tesla-earnings-10-22-2025/card/beyond-meat-stock-goes-on-a-wild-ride-QIrRiAHyuXGJHi6gCCXR?mod=wsj_FV"
            },
            {
                "Date": "2025-10-22 12:47:00",
                "Header": "Beyond Meat Stock is Up 729% This Week and Still Climbing. Amid Rumors of a Short Squeeze, Could It Be Headed to the Moon?",
                "Source": "(Motley Fool)",
                "URL": "/news/200742/beyond-meat-stock-is-up-729-this-week-and-still-climbing-amid-rumors-of-a-short-squeeze-could-it-be-headed-to-the-moon"
            },
            {
                "Date": "2025-10-22 12:14:00",
                "Header": "From Beyond Meat to Krispy Kreme, meme stocks surge as investors pile back into speculative trades",
                "Source": "(Yahoo Finance)",
                "URL": "https://finance.yahoo.com/news/from-beyond-meat-to-krispy-kreme-meme-stocks-surge-as-investors-pile-back-into-speculative-trades-161416350.html"
            },
            {
                "Date": "2025-10-22 12:11:00",
                "Header": "Krispy Kreme Takes a Meme Stock Ride. Don't Bite.",
                "Source": "(Barrons.com)",
                "URL": "https://www.barrons.com/articles/krispy-kreme-meme-stock-price-d302efc2?mod=bar_FV"
            },
            {
                "Date": "2025-10-22 11:50:00",
                "Header": "Why Is Beyond Meat (BYND) Stock Rocketing Higher Today",
                "Source": "(StockStory)",
                "URL": "/news/200640/why-is-beyond-meat-bynd-stock-rocketing-higher-today"
            },
            {
                "Date": "2025-10-22 11:38:00",
                "Header": "Forget GameStop: Meme Stock Traders Are Now Pumping Beyond MeatHere's Why",
                "Source": "(decrypt)",
                "URL": "https://finance.yahoo.com/m/1877ddf8-420f-350f-8a35-e2c54c707231/forget-gamestop%3A-meme-stock.html"
            },
            {
                "Date": "2025-10-22 11:37:00",
                "Header": "Beyond Meat shares surge in meme-stock style rally",
                "Source": "(Investing.com)",
                "URL": "https://finance.yahoo.com/news/beyond-meat-shares-surge-meme-153716358.html"
            },
            {
                "Date": "2025-10-22 11:14:00",
                "Header": "Beyond Meat and Gold Are Wall Street's Odd Couple. It Must Be FOMO.",
                "Source": "(Barrons.com)",
                "URL": "https://www.barrons.com/articles/beyond-meat-gold-stocks-fomo-rally-be74d3a2?mod=bar_FV"
            },
            {
                "Date": "2025-10-22 11:05:00",
                "Header": "Is Beyond Meat the Next Meme Stock? Whats Behind the Rally.",
                "Source": "(Barrons.com)",
                "URL": "https://finance.yahoo.com/m/fe293fcc-8308-3d7b-bd96-df96cf656407/is-beyond-meat-the-next-meme.html"
            },
            {
                "Date": "2025-10-22 10:39:00",
                "Header": "Beyond Meat, Krispy Kreme Revive Meme Stock Craze",
                "Source": "(Schaeffer's Research)",
                "URL": "/news/200412/beyond-meat-krispy-kreme-revive-meme-stock-craze"
            },
            {
                "Date": "2025-10-22 10:12:00",
                "Header": "Beyond Meat, Inc. (BYND) Has 70% Upside Potential If It Follows Opendoor Technologies' (OPEN) Path",
                "Source": "(Insider Monkey)",
                "URL": "/news/200315/beyond-meat-inc-bynd-has-70-upside-potential-if-it-follows-opendoor-technologies-open-path"
            },
            {
                "Date": "2025-10-22 10:03:00",
                "Header": "Beyond Meat fuels meme rally: What to know when trading meme stocks",
                "Source": "(Yahoo Finance Video)",
                "URL": "https://finance.yahoo.com/video/beyond-meat-fuels-meme-rally-140303800.html"
            },
            {
                "Date": "2025-10-22 10:01:00",
                "Header": "Beyond Meat stock soars 1,300% as meme traders fuel GameStop-like rally",
                "Source": "(Quartz)",
                "URL": "https://qz.com/beyond-meat-meme-stock-jumps-1300-percent"
            },
            {
                "Date": "2025-10-22 09:43:00",
                "Header": "BYND Stock Rallies as Walmart Deal Boosts Retail Comeback",
                "Source": "(Zacks)",
                "URL": "/news/200455/bynd-stock-rallies-as-walmart-deal-boosts-retail-comeback"
            },
            {
                "Date": "2025-10-22 09:34:00",
                "Header": "Beyond Meat's stock is up 1,200% in four days as blistering meme-stock rally rocks on",
                "Source": "(MarketWatch)",
                "URL": "https://www.marketwatch.com/story/beyond-meats-stock-is-up-1-200-in-four-days-as-blistering-meme-stock-rally-rocks-on-161f55c5?mod=mw_FV"
            },
            {
                "Date": "2025-10-22 09:28:00",
                "Header": "AT&T adds mobile subscribers in Q3, Beyond Meat rallies by 1,300%",
                "Source": "(Yahoo Finance Video)",
                "URL": "https://finance.yahoo.com/video/t-adds-mobile-subscribers-q3-132824277.html"
            },
            {
                "Date": "2025-10-22 09:19:00",
                "Header": "Beyond Meat Surges on Expanded Distribution at Walmart",
                "Source": "(Bloomberg)",
                "URL": "https://finance.yahoo.com/news/beyond-meat-surges-expanded-distribution-154010369.html"
            },
            {
                "Date": "2025-10-22 08:41:00",
                "Header": "Anthropic & Google talks, Beyond Meat soars",
                "Source": "(Yahoo Finance Video)",
                "URL": "https://finance.yahoo.com/video/anthropic-google-deal-amazon-beyond-124125344.html"
            },
            {
                "Date": "2025-10-22 07:41:00",
                "Header": "TD Cowen Lowers Beyond Meat (BYND) PT to $0.8, Cites Share Dilution, Operational Challenges",
                "Source": "(Insider Monkey)",
                "URL": "/news/199973/td-cowen-lowers-beyond-meat-bynd-pt-to-08-cites-share-dilution-operational-challenges"
            },
            {
                "Date": "2025-10-22 05:35:00",
                "Header": "Netflix shares retreat after earnings, and other early market movers",
                "Source": "(MarketWatch)",
                "URL": "https://www.marketwatch.com/livecoverage/stock-market-today-dow-sp500-nasdaq-hold-near-record-highs-tesla-ibm-earnings-due/card/netflix-shares-retreat-after-earnings-and-other-early-market-movers-64ndeW0y12V3OdqkKIDT?mod=mw_FV"
            },
            {
                "Date": "2025-10-22 05:31:00",
                "Header": "Why Beyond Meat stock is up about 600% in 3 days",
                "Source": "(Yahoo Finance)",
                "URL": "https://finance.yahoo.com/news/why-beyond-meat-stock-is-up-about-600-in-3-days-093158667.html"
            },
            {
                "Date": "2025-10-21 16:05:00",
                "Header": "Why Is Beyond Meat (BYND) Stock Rocketing Higher Today",
                "Source": "(StockStory)",
                "URL": "/news/199411/why-is-beyond-meat-bynd-stock-rocketing-higher-today"
            },
            {
                "Date": "2025-10-21 16:05:00",
                "Header": "Beyond Meat to Report Third Quarter 2025 Financial Results on November 4, 2025",
                "Source": "(GlobeNewswire)",
                "URL": "/news/199313/beyond-meat-to-report-third-quarter-2025-financial-results-on-november-4-2025"
            },
            {
                "Date": "2025-10-21 15:00:00",
                "Header": "Why Beyond Meat Stock Was Skyrocketing Again Today",
                "Source": "(Motley Fool)",
                "URL": "/news/199261/why-beyond-meat-stock-was-skyrocketing-again-today"
            },
            {
                "Date": "2025-10-21 14:38:00",
                "Header": "Meme Stock Madness: Will Beyond Meats 388% Pop End in Tears?",
                "Source": "(24/7 Wall St.)",
                "URL": "https://finance.yahoo.com/m/8eeef87a-ace1-323a-b1ce-160bbe72c5fb/meme-stock-madness%3A-will.html"
            },
            {
                "Date": "2025-10-21 13:14:00",
                "Header": "Netflix & Comcast's reported WBD interest, Beyond Meat skyrockets",
                "Source": "(Yahoo Finance Video)",
                "URL": "https://finance.yahoo.com/video/netflix-comcasts-reported-wbd-interest-171442417.html"
            },
            {
                "Date": "2025-10-21 12:25:00",
                "Header": "Is Beyond Meat the Next Meme Stock? What's Behind Rally.",
                "Source": "(Barrons.com)",
                "URL": "https://www.barrons.com/articles/beyond-meat-meme-stock-price-0961d3c6?mod=bar_FV"
            },
            {
                "Date": "2025-10-21 12:19:00",
                "Header": "Shares of Beyond Meat soar nearly 300% in torrid meme-stock rally. Here's what's going on.",
                "Source": "(MarketWatch)",
                "URL": "https://www.marketwatch.com/story/shares-of-beyond-meat-soar-nearly-300-in-torrid-meme-stock-rally-heres-whats-going-on-5e061ee1?mod=mw_FV"
            },
            {
                "Date": "2025-10-21 09:52:00",
                "Header": "Beyond Meat stock soars after expanding Walmart distribution",
                "Source": "(Investing.com)",
                "URL": "https://finance.yahoo.com/news/beyond-meat-stock-soars-expanding-135259078.html"
            },
            {
                "Date": "2025-10-21 09:15:00",
                "Header": "Beyond Meat Expands Distribution at Walmart",
                "Source": "(GlobeNewswire)",
                "URL": "/news/198716/beyond-meat-expands-distribution-at-walmart"
            },
            {
                "Date": "2025-10-21 08:05:00",
                "Header": "Beyond Meat, Tesla, and the aspiring Nvidia rival: Trending Stocks",
                "Source": "(Yahoo Finance Video)",
                "URL": "https://finance.yahoo.com/video/beyond-meat-tesla-aspiring-nvidia-120524013.html"
            },
            {
                "Date": "2025-10-20 15:45:00",
                "Header": "Retail Traders Sending Beyond Meat 80% Higher Today",
                "Source": "(24/7 Wall St.)",
                "URL": "https://finance.yahoo.com/m/19e60684-8613-326d-b6b5-11c1668101b4/retail-traders-sending-beyond.html"
            },
            {
                "Date": "2025-10-20 15:11:00",
                "Header": "Up Over 100% in 24 Hours, Is Beyond Meat Stock the Next AMC?",
                "Source": "(Motley Fool)",
                "URL": "/news/197862/up-over-100-in-24-hours-is-beyond-meat-stock-the-next-amc"
            },
            {
                "Date": "2025-10-20 14:05:00",
                "Header": "Meme Stock Beyond Meat Soaring As Traders Buy Up Shares",
                "Source": "(24/7 Wall St.)",
                "URL": "https://finance.yahoo.com/m/b555e7a3-d9a5-3381-b4c6-4278bf4df1c2/meme-stock-beyond-meat.html"
            },
            {
                "Date": "2025-10-20 08:16:00",
                "Header": "Beyond Meat, Tesla, TKMS, Kering: Trending Stocks",
                "Source": "(Yahoo Finance Video)",
                "URL": "https://finance.yahoo.com/video/beyond-meat-tesla-tkms-kering-121647244.html"
            },
            {
                "Date": "2025-10-16 16:30:00",
                "Header": "Beyond Meat Announces Release at 5:00 p.m., New York City time, of Lock-up Restrictions on Shares that were Exchanged for Existing Convertible Notes in its Exchange Offer",
                "Source": "(GlobeNewswire)",
                "URL": "/news/195452/beyond-meat-announces-release-at-5-00-pm-new-york-city-time-of-lock-up-restrictions-on-shares-that-were-exchanged-for-existing-convertible-notes-in-its-exchange-offer"
            },
            {
                "Date": "2025-10-16 11:19:00",
                "Header": "3 AgTech & Food Innovation Stocks Poised for Long-Term Gains",
                "Source": "(Zacks)",
                "URL": "/news/195070/3-agtech-food-innovation-stocks-poised-for-long-term-gains"
            },
            {
                "Date": "2025-10-15 14:01:00",
                "Header": "Why Beyond Meat (BYND) Stock Is Up Today",
                "Source": "(StockStory)",
                "URL": "/news/193856/why-beyond-meat-bynd-stock-is-up-today"
            },
            {
                "Date": "2025-10-14 14:10:00",
                "Header": "Beyond Meat Stock Trades Below $1 for First Time. Why Its Ailing.",
                "Source": "(Barrons.com)",
                "URL": "https://finance.yahoo.com/m/0d7e96b8-fb8e-34bf-942b-52b64a714392/beyond-meat-stock-trades.html"
            },
            {
                "Date": "2025-10-14 13:05:00",
                "Header": "Why Beyond Meat (BYND) Stock Is Nosediving",
                "Source": "(StockStory)",
                "URL": "/news/192511/why-beyond-meat-bynd-stock-is-nosediving"
            },
            {
                "Date": "2025-10-14 09:46:00",
                "Header": "Beyond Meat Stock Trades Below $1 for First Time. Why the Plant-Based Meat Maker Is Ailing.",
                "Source": "(Barrons.com)",
                "URL": "https://www.barrons.com/articles/beyond-meat-stock-plant-based-meat-0dfb2288?mod=bar_FV"
            },
            {
                "Date": "2025-10-13 16:16:00",
                "Header": "Beyond Meat Debt Deal Rattles Investors",
                "Source": "(The Wall Street Journal)",
                "URL": "https://www.wsj.com/business/retail/beyond-meat-corporate-restructure-stock-reaction-326cadec?mod=wsj_FV"
            },
            {
                "Date": "2025-10-13 16:11:00",
                "Header": "Beyond Meat Plummets After Debt Swap Massively Dilutes Shareholders",
                "Source": "(Bloomberg)",
                "URL": "https://finance.yahoo.com/news/beyond-meat-plummets-debt-swap-145207491.html"
            },
            {
                "Date": "2025-10-13 14:08:00",
                "Header": "Oklo & other nuclear stocks climb, Public Storage upgraded",
                "Source": "(Yahoo Finance Video)",
                "URL": "https://finance.yahoo.com/video/oklo-other-nuclear-stocks-climb-180748887.html"
            },
            {
                "Date": "2025-10-13 12:21:00",
                "Header": "Why Beyond Meat (BYND) Stock Is Falling Today",
                "Source": "(StockStory)",
                "URL": "/news/191023/why-beyond-meat-bynd-stock-is-falling-today"
            },
            {
                "Date": "2025-10-13 10:53:00",
                "Header": "Taylor Swift on Disney+, Beyond Meat nosedives on debt swap",
                "Source": "(Yahoo Finance Video)",
                "URL": "https://finance.yahoo.com/video/taylor-swift-disney-beyond-meat-145344436.html"
            },
            {
                "Date": "2025-10-13 07:00:00",
                "Header": "Beyond Meat Announces Early Tender Results and Early Settlement for Exchange Offer and Consent Solicitation with Respect to Existing Convertible Notes",
                "Source": "(GlobeNewswire)",
                "URL": "/news/190468/beyond-meat-announces-early-tender-results-and-early-settlement-for-exchange-offer-and-consent-solicitation-with-respect-to-existing-convertible-notes"
            },
            {
                "Date": "2025-10-02 00:34:00",
                "Header": "3 of Wall Street's Favorite Stocks We Steer Clear Of",
                "Source": "(StockStory)",
                "URL": "/news/181922/3-of-wall-streets-favorite-stocks-we-steer-clear-of"
            },
            {
                "Date": "2025-09-30 09:00:00",
                "Header": "Stocks making big moves yesterday: Beyond Meat, The Trade Desk, Guardant Health, PayPal, and Tilray",
                "Source": "(StockStory)",
                "URL": "/news/179484/stocks-making-big-moves-yesterday-beyond-meat-the-trade-desk-guardant-health-paypal-and-tilray"
            },
            {
                "Date": "2025-09-30 08:45:00",
                "Header": "Beyond Meat launches exchange offer, consent solicitation to eliminate debt",
                "Source": "(TipRanks)",
                "URL": "https://finance.yahoo.com/news/beyond-meat-launches-exchange-offer-124552870.html"
            },
            {
                "Date": "2025-09-29 15:10:00",
                "Header": "Why Beyond Meat (BYND) Stock Is Trading Lower Today",
                "Source": "(StockStory)",
                "URL": "/news/178734/why-beyond-meat-bynd-stock-is-trading-lower-today"
            },
            {
                "Date": "2025-09-29 10:46:00",
                "Header": "Movie tariffs, Beyond Meat, Kroger & DoorDash: Trending Tickers",
                "Source": "(Yahoo Finance Video)",
                "URL": "https://finance.yahoo.com/video/movie-tariffs-beyond-meat-kroger-144641390.html"
            },
            {
                "Date": "2025-09-29 08:15:00",
                "Header": "Beyond Meat Launches Exchange Offer and Consent Solicitation Intended to Eliminate Over $800 Million of Debt with Existing Noteholder Support",
                "Source": "(GlobeNewswire)",
                "URL": "/news/178203/beyond-meat-launches-exchange-offer-and-consent-solicitation-intended-to-eliminate-over-800-million-of-debt-with-existing-noteholder-support"
            },
            {
                "Date": "2025-09-29 00:33:00",
                "Header": "1 Consumer Stock to Target This Week and 2 We Brush Off",
                "Source": "(StockStory)",
                "URL": "/news/178114/1-consumer-stock-to-target-this-week-and-2-we-brush-off"
            },
            {
                "Date": "2025-09-28 19:20:00",
                "Header": "Beyond Meat, Inc. (BYND) Cuts Jobs as Revenue Slumps 20% in Q2",
                "Source": "(Insider Monkey)",
                "URL": "/news/177803/beyond-meat-inc-bynd-cuts-jobs-as-revenue-slumps-20-in-q2"
            },
            {
                "Date": "2025-09-23 00:02:00",
                "Header": "3 Reasons BYND is Risky and 1 Stock to Buy Instead",
                "Source": "(StockStory)",
                "URL": "/news/173182/3-reasons-bynd-is-risky-and-1-stock-to-buy-instead"
            },
            {
                "Date": "2025-09-15 10:40:00",
                "Header": "Micron, The RealReal, Beyond Meat: Top Analyst Calls",
                "Source": "(Yahoo Finance Video)",
                "URL": "https://finance.yahoo.com/video/micron-realreal-beyond-meat-top-144037089.html"
            },
            {
                "Date": "2025-09-15 09:40:00",
                "Header": "Broadcom initiated, Beyond Meat downgraded: Wall Street's top analyst calls",
                "Source": "(The Fly)",
                "URL": "https://finance.yahoo.com/news/broadcom-initiated-beyond-meat-downgraded-134059715.html"
            },
            {
                "Date": "2025-09-15 09:31:00",
                "Header": "Argus downgrades Beyond Meat on weak demand and balance sheet concerns",
                "Source": "(Investing.com)",
                "URL": "https://finance.yahoo.com/news/argus-downgrades-beyond-meat-weak-133121297.html"
            },
            {
                "Date": "2025-09-10 23:35:00",
                "Header": "Q2 Earnings Outperformers: Beyond Meat (NASDAQ:BYND) And The Rest Of The Perishable Food Stocks",
                "Source": "(StockStory)",
                "URL": "/news/163269/q2-earnings-outperformers-beyond-meat-nasdaq-bynd-and-the-rest-of-the-perishable-food-stocks"
            },
            {
                "Date": "2025-09-10 16:41:00",
                "Header": "Beyond Meat, BellRing Brands, Calavo, e.l.f. Beauty, and Tilray Shares Plummet, What You Need To Know",
                "Source": "(StockStory)",
                "URL": "/news/163072/beyond-meat-bellring-brands-calavo-elf-beauty-and-tilray-shares-plummet-what-you-need-to-know"
            },
            {
                "Date": "2025-09-02 15:30:00",
                "Header": "Why Beyond Meat (BYND) Shares Are Trading Lower Today",
                "Source": "(StockStory)",
                "URL": "/news/155964/why-beyond-meat-bynd-shares-are-trading-lower-today"
            },
            {
                "Date": "2025-08-26 10:53:00",
                "Header": "Best Natural and Organic Food Stocks for Investors in 2025",
                "Source": "(Zacks)",
                "URL": "/news/150037/best-natural-and-organic-food-stocks-for-investors-in-2025"
            },
            {
                "Date": "2025-08-15 11:50:00",
                "Header": "Why Beyond Meat (BYND) Stock Is Trading Lower Today",
                "Source": "(StockStory)",
                "URL": "/news/142045/why-beyond-meat-bynd-stock-is-trading-lower-today"
            },
            {
                "Date": "2025-08-15 10:34:00",
                "Header": "Beyond Meat's stock falls as company denies reports about bankruptcy",
                "Source": "(MarketWatch)",
                "URL": "https://www.marketwatch.com/livecoverage/stock-market-today-dow-set-for-300-point-rise-as-s-p-500-eyes-record-ahead-of-retail-sales/card/beyond-meat-s-stock-falls-as-company-denies-reports-about-bankruptcy-0BUH8SuJh29chlyROgre?mod=mw_FV"
            },
            {
                "Date": "2025-08-13 01:36:00",
                "Header": "5 Insightful Analyst Questions From Beyond Meat's Q2 Earnings Call",
                "Source": "(StockStory)",
                "URL": "/news/137800/5-insightful-analyst-questions-from-beyond-meats-q2-earnings-call"
            },
            {
                "Date": "2025-08-12 13:50:00",
                "Header": "Beyond Meat (BYND) Stock Trades Up, Here Is Why",
                "Source": "(StockStory)",
                "URL": "/news/137223/beyond-meat-bynd-stock-trades-up-here-is-why"
            },
            {
                "Date": "2025-08-12 03:16:00",
                "Header": "BYND Q2 Deep Dive: Category Headwinds Prompt Operational Reset and Brand Refocus",
                "Source": "(StockStory)",
                "URL": "/news/136207/bynd-q2-deep-dive-category-headwinds-prompt-operational-reset-and-brand-refocus"
            },
            {
                "Date": "2025-08-06 18:50:00",
                "Header": "Beyond Meat (BYND) Reports Q2 Loss, Lags Revenue Estimates",
                "Source": "(Zacks)",
                "URL": "/news/131043/beyond-meat-bynd-reports-q2-loss-lags-revenue-estimates"
            },
            {
                "Date": "2025-08-06 17:50:00",
                "Header": "Beyond Meat: Q2 Earnings Snapshot",
                "Source": "(Associated Press Finance)",
                "URL": "https://finance.yahoo.com/news/beyond-meat-q2-earnings-snapshot-215023589.html"
            },
            {
                "Date": "2025-08-06 17:13:00",
                "Header": "Beyond Meat (NASDAQ:BYND) Misses Q2 Sales Targets",
                "Source": "(StockStory)",
                "URL": "/news/130725/beyond-meat-nasdaq-bynd-misses-q2-sales-targets"
            },
            {
                "Date": "2025-08-06 16:58:00",
                "Header": "Beyond Meat Reports Second Quarter 2025 Financial Results",
                "Source": "(GlobeNewswire)",
                "URL": "/news/130700/beyond-meat-reports-second-quarter-2025-financial-results"
            },
            {
                "Date": "2025-08-05 05:52:00",
                "Header": "Big Foods stake in the future  in-house venture-capital funds investments",
                "Source": "(Just Food)",
                "URL": "https://finance.yahoo.com/m/fa0bb8a5-5a1e-3ee0-842b-17773e34ea9b/big-food%E2%80%99s-stake-in-the.html"
            },
            {
                "Date": "2025-08-04 23:20:00",
                "Header": "What To Expect From Beyond Meat's (BYND) Q2 Earnings",
                "Source": "(StockStory)",
                "URL": "/news/127378/what-to-expect-from-beyond-meats-bynd-q2-earnings"
            },
            {
                "Date": "2025-08-04 08:40:00",
                "Header": "Tyson Foods (TSN) Q3 Earnings and Revenues Surpass Estimates",
                "Source": "(Zacks)",
                "URL": "/news/126249/tyson-foods-tsn-q3-earnings-and-revenues-surpass-estimates"
            },
            {
                "Date": "2025-08-01 00:41:00",
                "Header": "3 Unpopular Stocks We Keep Off Our Radar",
                "Source": "(StockStory)",
                "URL": "/news/124361/3-unpopular-stocks-we-keep-off-our-radar"
            },
            {
                "Date": "2025-07-28 16:05:00",
                "Header": "Beyond Meat to Report Second Quarter 2025 Financial Results on August 6, 2025",
                "Source": "(GlobeNewswire)",
                "URL": "/news/117821/beyond-meat-to-report-second-quarter-2025-financial-results-on-august-6-2025"
            },
            {
                "Date": "2025-07-28 12:01:00",
                "Header": "Why Beyond Meat (BYND) Shares Are Falling Today",
                "Source": "(StockStory)",
                "URL": "/news/117600/why-beyond-meat-bynd-shares-are-falling-today"
            },
            {
                "Date": "2025-07-25 16:29:00",
                "Header": "Meme-Stock Roar Fades on Wall Street as Retail Finds New Thrills",
                "Source": "(Bloomberg)",
                "URL": "https://finance.yahoo.com/news/meme-stock-roar-fades-wall-202930652.html"
            },
            {
                "Date": "2025-07-24 03:57:00",
                "Header": "Zacks Investment Ideas feature highlights: OpenDoor Technologies, Krispy Kreme, Beyond, Kohls and Beyond Meat",
                "Source": "(Zacks)",
                "URL": "/news/113364/zacks-investment-ideas-feature-highlights-opendoor-technologies-krispy-kreme-beyond-kohls-and-beyond-meat"
            },
            {
                "Date": "2025-07-23 13:31:00",
                "Header": "Why Are Beyond Meat (BYND) Shares Soaring Today",
                "Source": "(StockStory)",
                "URL": "/news/112727/why-are-beyond-meat-bynd-shares-soaring-today"
            },
            {
                "Date": "2025-07-23 11:44:00",
                "Header": "Low-Quality Momentum Stocks Soar: Are Markets too Frothy?",
                "Source": "(Zacks)",
                "URL": "/news/112625/low-quality-momentum-stocks-soar-are-markets-too-frothy"
            },
            {
                "Date": "2025-07-23 10:11:00",
                "Header": "Krispy Kreme and GoPro trading explodes as meme stock craze continues",
                "Source": "(Quartz)",
                "URL": "https://qz.com/meme-stocks-krispy-kreme-gopro-beyond-meat-opendoor-kohls-reddit"
            },
            {
                "Date": "2025-07-23 09:25:00",
                "Header": "USJapan trade deal, meme stocks, Big Tech earnings: 3 things",
                "Source": "(Yahoo Finance Video)",
                "URL": "https://finance.yahoo.com/video/us-japan-trade-deal-meme-132511187.html"
            },
            {
                "Date": "2025-07-22 10:11:00",
                "Header": "Here's what's fueling the latest meme stock surge",
                "Source": "(Yahoo Finance Video)",
                "URL": "https://finance.yahoo.com/video/heres-whats-fueling-latest-meme-141145393.html"
            },
            {
                "Date": "2025-07-22 05:00:00",
                "Header": "Eyeing alternatives  meat companies with stakes in meat-free and cell-based meat",
                "Source": "(Just Food)",
                "URL": "https://finance.yahoo.com/m/51775d56-3264-30e6-be44-6f586ff1f4c5/eyeing-alternatives%C2%A0%E2%80%93-meat.html"
            },
            {
                "Date": "2025-07-22 00:05:00",
                "Header": "Beyond Meat (BYND): Buy, Sell, or Hold Post Q1 Earnings?",
                "Source": "(StockStory)",
                "URL": "/news/110483/beyond-meat-bynd-buy-sell-or-hold-post-q1-earnings"
            },
            {
                "Date": "2025-07-17 15:50:00",
                "Header": "Why Beyond Meat (BYND) Stock Is Trading Up Today",
                "Source": "(StockStory)",
                "URL": "/news/107170/why-beyond-meat-bynd-stock-is-trading-up-today"
            },
            {
                "Date": "2025-07-15 23:37:00",
                "Header": "Reflecting On Perishable Food Stocks' Q1 Earnings: Beyond Meat (NASDAQ:BYND)",
                "Source": "(StockStory)",
                "URL": "/news/104985/reflecting-on-perishable-food-stocks-q1-earnings-beyond-meat-nasdaq-bynd"
            },
            {
                "Date": "2025-07-15 10:33:00",
                "Header": "Sprouts Farmers Chases Growth in Booming Health & Wellness Market",
                "Source": "(Zacks)",
                "URL": "/news/104253/sprouts-farmers-chases-growth-in-booming-health-wellness-market"
            },
            {
                "Date": "2025-07-15 10:27:00",
                "Header": "Natural and Organic Food Stocks Showing Strong Potential for 2025",
                "Source": "(Zacks)",
                "URL": "/news/104249/natural-and-organic-food-stocks-showing-strong-potential-for-2025"
            },
            {
                "Date": "2025-07-11 04:50:00",
                "Header": "Zacks Industry Outlook Highlights Tyson Foods and Beyond Meat",
                "Source": "(Zacks)",
                "URL": "/news/101018/zacks-industry-outlook-highlights-tyson-foods-and-beyond-meat"
            },
            {
                "Date": "2025-07-10 09:06:00",
                "Header": "2 Meat Stocks to Keep an Eye On Despite Market Challenges",
                "Source": "(Zacks)",
                "URL": "/news/100282/2-meat-stocks-to-keep-an-eye-on-despite-market-challenges"
            },
            {
                "Date": "2025-07-09 09:53:00",
                "Header": "Top Ag Tech & Food Innovation Stocks to Strengthen Your Portfolio",
                "Source": "(Zacks)",
                "URL": "/news/99303/top-ag-tech-food-innovation-stocks-to-strengthen-your-portfolio"
            }
        ],
        "operationRatiosAsOf1Y": "2024-12-31",
        "otcMarket": "",
        "otcTier": "",
        "overall_risk": 6,
        "pageType": "ticker",
        "pe_ratio": None,
        "percentile": 86,
        "phone": "866 756 4112",
        "previousCloseDate": "2025-10-22T17:00:00.000-04:00",
        "previousClosePrice": 3.58,
        "previous_close": 3.62,
        "primary": True,
        "psRatio": 0.852734,
        "revenueGrowth": -0.1956,
        "revenueGrowth1Y": -0.049287,
        "sec_filings": [
            {
                "date": "2025-10-17",
                "epoch_date": 1760659200,
                "title": "Proxy Statements",
                "type": "DEF 14A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001193125-25-242542_1655210"
            },
            {
                "date": "2025-10-15",
                "epoch_date": 1760486400,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001193125-25-240364_1655210"
            },
            {
                "date": "2025-10-14",
                "epoch_date": 1760400000,
                "title": "Additional Forms",
                "type": "D",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000194_1655210"
            },
            {
                "date": "2025-10-06",
                "epoch_date": 1759708800,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000193_1655210"
            },
            {
                "date": "2025-09-29",
                "epoch_date": 1759104000,
                "title": "Proxy Statements",
                "type": "DEFA14A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001193125-25-221795_1655210"
            },
            {
                "date": "2025-09-18",
                "epoch_date": 1758153600,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000189_1655210"
            },
            {
                "date": "2025-08-08",
                "epoch_date": 1754611200,
                "title": "Periodic Financial Reports",
                "type": "10-Q",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000159_1655210"
            },
            {
                "date": "2025-08-06",
                "epoch_date": 1754438400,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000149_1655210"
            },
            {
                "date": "2025-07-28",
                "epoch_date": 1753660800,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000144_1655210"
            },
            {
                "date": "2025-06-26",
                "epoch_date": 1750896000,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000129_1655210"
            },
            {
                "date": "2025-05-23",
                "epoch_date": 1747958400,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000102_1655210"
            },
            {
                "date": "2025-05-15",
                "epoch_date": 1747267200,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000099_1655210"
            },
            {
                "date": "2025-05-08",
                "epoch_date": 1746662400,
                "title": "Offering Registrations",
                "type": "S-8",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000096_1655210"
            },
            {
                "date": "2025-05-07",
                "epoch_date": 1746576000,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001193125-25-115042_1655210"
            },
            {
                "date": "2025-04-08",
                "epoch_date": 1744070400,
                "title": "Proxy Statements",
                "type": "DEFA14A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000075_1655210"
            },
            {
                "date": "2025-03-17",
                "epoch_date": 1742169600,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000061_1655210"
            },
            {
                "date": "2025-03-05",
                "epoch_date": 1741132800,
                "title": "Periodic Financial Reports",
                "type": "10-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000034_1655210"
            },
            {
                "date": "2025-02-26",
                "epoch_date": 1740528000,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000020_1655210"
            },
            {
                "date": "2025-02-10",
                "epoch_date": 1739145600,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-25-000011_1655210"
            },
            {
                "date": "2024-11-06",
                "epoch_date": 1730851200,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-24-000261_1655210"
            },
            {
                "date": "2024-08-08",
                "epoch_date": 1723075200,
                "title": "Periodic Financial Reports",
                "type": "10-Q",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-24-000210_1655210"
            },
            {
                "date": "2024-08-07",
                "epoch_date": 1722988800,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-24-000207_1655210"
            },
            {
                "date": "2024-05-24",
                "epoch_date": 1716508800,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-24-000142_1655210"
            },
            {
                "date": "2024-05-09",
                "epoch_date": 1715212800,
                "title": "Periodic Financial Reports",
                "type": "10-Q",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-24-000117_1655210"
            },
            {
                "date": "2024-05-08",
                "epoch_date": 1715126400,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-24-000114_1655210"
            },
            {
                "date": "2024-04-22",
                "epoch_date": 1713744000,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-24-000101_1655210"
            },
            {
                "date": "2024-04-10",
                "epoch_date": 1712707200,
                "title": "Proxy Statements",
                "type": "DEF 14A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-24-000085_1655210"
            },
            {
                "date": "2024-03-01",
                "epoch_date": 1709251200,
                "title": "Periodic Financial Reports",
                "type": "10-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-24-000025_1655210"
            },
            {
                "date": "2024-02-27",
                "epoch_date": 1708992000,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-24-000017_1655210"
            },
            {
                "date": "2024-02-13",
                "epoch_date": 1707782400,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-24-000013_1655210"
            },
            {
                "date": "2024-01-26",
                "epoch_date": 1706227200,
                "title": "Tender Offer/Acquisition Reports",
                "type": "SC 13G/A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001086364-24-004825_1655210"
            },
            {
                "date": "2024-01-08",
                "epoch_date": 1704672000,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-24-000004_1655210"
            },
            {
                "date": "2023-11-24",
                "epoch_date": 1700784000,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000260_1655210"
            },
            {
                "date": "2023-11-09",
                "epoch_date": 1699488000,
                "title": "Periodic Financial Reports",
                "type": "10-Q",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000257_1655210"
            },
            {
                "date": "2023-11-08",
                "epoch_date": 1699401600,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000255_1655210"
            },
            {
                "date": "2023-11-02",
                "epoch_date": 1698883200,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000251_1655210"
            },
            {
                "date": "2023-09-29",
                "epoch_date": 1695945600,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000237_1655210"
            },
            {
                "date": "2023-08-09",
                "epoch_date": 1691539200,
                "title": "Periodic Financial Reports",
                "type": "10-Q",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000197_1655210"
            },
            {
                "date": "2023-08-07",
                "epoch_date": 1691366400,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000194_1655210"
            },
            {
                "date": "2023-05-26",
                "epoch_date": 1685059200,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000118_1655210"
            },
            {
                "date": "2023-05-12",
                "epoch_date": 1683849600,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000098_1655210"
            },
            {
                "date": "2023-05-10",
                "epoch_date": 1683676800,
                "title": "Periodic Financial Reports",
                "type": "10-Q",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000092_1655210"
            },
            {
                "date": "2023-04-13",
                "epoch_date": 1681344000,
                "title": "Proxy Statements",
                "type": "DEFA14A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000080_1655210"
            },
            {
                "date": "2023-04-12",
                "epoch_date": 1681257600,
                "title": "Annual Report to Shareholders",
                "type": "ARS",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000074_1655210"
            },
            {
                "date": "2023-04-11",
                "epoch_date": 1681171200,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000066_1655210"
            },
            {
                "date": "2023-03-01",
                "epoch_date": 1677628800,
                "title": "Periodic Financial Reports",
                "type": "10-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000017_1655210"
            },
            {
                "date": "2023-02-23",
                "epoch_date": 1677110400,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-23-000011_1655210"
            },
            {
                "date": "2023-02-14",
                "epoch_date": 1676332800,
                "title": "Tender Offer/Acquisition Reports",
                "type": "SC 13G/A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001104659-23-021030_1655210"
            },
            {
                "date": "2023-02-09",
                "epoch_date": 1675900800,
                "title": "Tender Offer/Acquisition Reports",
                "type": "SC 13G/A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001104659-23-015451_1655210"
            },
            {
                "date": "2023-02-03",
                "epoch_date": 1675382400,
                "title": "Tender Offer/Acquisition Reports",
                "type": "SC 13G",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001306550-23-006962_1655210"
            },
            {
                "date": "2022-12-21",
                "epoch_date": 1671580800,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000276_1655210"
            },
            {
                "date": "2022-12-06",
                "epoch_date": 1670284800,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000246_1655210"
            },
            {
                "date": "2022-11-16",
                "epoch_date": 1668556800,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000232_1655210"
            },
            {
                "date": "2022-11-10",
                "epoch_date": 1668038400,
                "title": "Periodic Financial Reports",
                "type": "10-Q",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000227_1655210"
            },
            {
                "date": "2022-11-09",
                "epoch_date": 1667952000,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000223_1655210"
            },
            {
                "date": "2022-10-18",
                "epoch_date": 1666051200,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000213_1655210"
            },
            {
                "date": "2022-10-14",
                "epoch_date": 1665705600,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000206_1655210"
            },
            {
                "date": "2022-10-06",
                "epoch_date": 1665014400,
                "title": "Tender Offer/Acquisition Reports",
                "type": "SC 13G/A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001088875-22-000117_1655210"
            },
            {
                "date": "2022-09-23",
                "epoch_date": 1663891200,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000194_1655210"
            },
            {
                "date": "2022-09-20",
                "epoch_date": 1663632000,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000189_1655210"
            },
            {
                "date": "2022-09-02",
                "epoch_date": 1662076800,
                "title": "Tender Offer/Acquisition Reports",
                "type": "SC 13G/A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001088875-22-000115_1655210"
            },
            {
                "date": "2022-08-11",
                "epoch_date": 1660176000,
                "title": "Periodic Financial Reports",
                "type": "10-Q",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000163_1655210"
            },
            {
                "date": "2022-08-04",
                "epoch_date": 1659571200,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000157_1655210"
            },
            {
                "date": "2022-05-26",
                "epoch_date": 1653523200,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000102_1655210"
            },
            {
                "date": "2022-05-12",
                "epoch_date": 1652313600,
                "title": "Periodic Financial Reports",
                "type": "10-Q",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000084_1655210"
            },
            {
                "date": "2022-05-11",
                "epoch_date": 1652227200,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000081_1655210"
            },
            {
                "date": "2022-04-12",
                "epoch_date": 1649721600,
                "title": "Proxy Statements",
                "type": "DEF 14A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000073_1655210"
            },
            {
                "date": "2022-04-08",
                "epoch_date": 1649376000,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000068_1655210"
            },
            {
                "date": "2022-03-03",
                "epoch_date": 1646265600,
                "title": "Offering Registrations",
                "type": "S-8",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000035_1655210"
            },
            {
                "date": "2022-03-02",
                "epoch_date": 1646179200,
                "title": "Periodic Financial Reports",
                "type": "10-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000019_1655210"
            },
            {
                "date": "2022-02-24",
                "epoch_date": 1645660800,
                "title": "Corporate Changes & Voting Matters",
                "type": "8-K",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000015_1655210"
            },
            {
                "date": "2022-02-14",
                "epoch_date": 1644796800,
                "title": "Tender Offer/Acquisition Reports",
                "type": "SC 13G",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001104659-22-022354_1655210"
            },
            {
                "date": "2022-02-09",
                "epoch_date": 1644364800,
                "title": "Tender Offer/Acquisition Reports",
                "type": "SC 13G/A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001104659-22-016633_1655210"
            },
            {
                "date": "2022-02-04",
                "epoch_date": 1643932800,
                "title": "Tender Offer/Acquisition Reports",
                "type": "SC 13G/A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001193125-22-028315_1655210"
            },
            {
                "date": "2022-01-27",
                "epoch_date": 1643241600,
                "title": "Tender Offer/Acquisition Reports",
                "type": "SC 13G/A",
                "url": "https://finance.yahoo.com/sec-filing/BYND/0001655210-22-000010_1655210"
            }
        ],
        "sector": "Consumer Defensive",
        "sector_disp": "Consumer Defensive",
        "sector_key": "consumer-defensive",
        "shareFloat": 393961721,
        "share_holder_rights_risk": 5,
        "sharesFloat": 393961721,
        "sharesOutstanding": 397607401,
        "sharesShort": 39586789,
        "sharesShortPercentOfFloat": 10.05,
        "shares_float": 393961721,
        "shares_outstanding": 397607401,
        "shortDescription": "Ordinary Shares",
        "size": 0,
        "sources": {
            "EDGAR": "https://www.sec.gov/edgar/browse/?CIK=1655210",
            "google": "https://www.google.com/finance/quote/BYND:NASDAQ",
            "marketwatch": "https://www.marketwatch.com/investing/stock/bynd",
            "reuters": "https://www.reuters.com/companies/BYND.OQ",
            "yahoo": "https://finance.yahoo.com/quote/BYND"
        },
        "state": "CA",
        "stats": {
            "avg_gap": 0.4266062531988394,
            "day1": {
                "avg_high_spike": 0.3371501008347063,
                "avg_high_time": "12:16:24",
                "avg_low_spike": -0.21567473358247327,
                "avg_low_time": "12:56:24",
                "avg_return": 0.11310660787143616,
                "avg_return_series": [
                    {
                        "09:30": -0.014875025244592083
                    },
                    {
                        "09:31": -0.03384453308806856
                    },
                    {
                        "09:32": -0.0806002945825729
                    },
                    {
                        "09:33": -0.0357132672486013
                    },
                    {
                        "09:34": -0.046427272202956976
                    },
                    {
                        "09:35": -0.04434809904399617
                    },
                    {
                        "09:36": -0.03820059751183555
                    },
                    {
                        "09:37": -0.06116884331149212
                    },
                    {
                        "09:38": -0.04301768243425186
                    },
                    {
                        "09:39": -0.0335530608982591
                    },
                    {
                        "09:40": -0.053472876711645724
                    },
                    {
                        "09:41": -0.04168460345961977
                    },
                    {
                        "09:42": -0.05676630731496518
                    },
                    {
                        "09:43": -0.07089922483519336
                    },
                    {
                        "09:44": -0.06549878564460074
                    },
                    {
                        "09:45": -0.06773382133855474
                    },
                    {
                        "09:46": -0.06945543324833856
                    },
                    {
                        "09:47": -0.0644118020931713
                    },
                    {
                        "09:48": -0.06634976219633426
                    },
                    {
                        "09:49": -0.06454281401888476
                    },
                    {
                        "09:50": -0.051797579785406556
                    },
                    {
                        "09:51": -0.04523728399080555
                    },
                    {
                        "09:52": -0.05982999541319259
                    },
                    {
                        "09:53": -0.044052832894114616
                    },
                    {
                        "09:54": -0.04085934644257525
                    },
                    {
                        "09:55": -0.03054013782216005
                    },
                    {
                        "09:56": -0.035202166896191246
                    },
                    {
                        "09:57": -0.047975094254709555
                    },
                    {
                        "09:58": -0.05836337315325785
                    },
                    {
                        "09:59": -0.07235213837277725
                    },
                    {
                        "10:00": -0.03433493961105409
                    },
                    {
                        "10:01": -0.05785159454196237
                    },
                    {
                        "10:02": -0.05512408200537855
                    },
                    {
                        "10:03": -0.037605811988986784
                    },
                    {
                        "10:04": -0.03218838022609061
                    },
                    {
                        "10:05": -0.04918137218127033
                    },
                    {
                        "10:06": -0.03532936676197107
                    },
                    {
                        "10:07": -0.0382001007699658
                    },
                    {
                        "10:08": -0.0342646764872305
                    },
                    {
                        "10:09": -0.03433228758213516
                    },
                    {
                        "10:10": -0.039739655824064385
                    },
                    {
                        "10:11": -0.04568698875323851
                    },
                    {
                        "10:12": -0.031763458125472654
                    },
                    {
                        "10:13": -0.02679125846049596
                    },
                    {
                        "10:14": -0.022060064830841043
                    },
                    {
                        "10:15": -0.039040605770477445
                    },
                    {
                        "10:16": -0.030740113340397345
                    },
                    {
                        "10:17": -0.03800900650951766
                    },
                    {
                        "10:18": -0.030711098818705956
                    },
                    {
                        "10:19": -0.027553537969889297
                    },
                    {
                        "10:20": -0.0353621311737464
                    },
                    {
                        "10:21": -0.03788456674399565
                    },
                    {
                        "10:22": -0.031164199700212114
                    },
                    {
                        "10:23": -0.025713204728130566
                    },
                    {
                        "10:24": -0.041631813008217416
                    },
                    {
                        "10:25": -0.028279871279512814
                    },
                    {
                        "10:26": -0.0276420882608865
                    },
                    {
                        "10:27": -0.029286726683529562
                    },
                    {
                        "10:28": -0.045209328347230654
                    },
                    {
                        "10:29": -0.03913550489925022
                    },
                    {
                        "10:30": -0.038949250690171716
                    },
                    {
                        "10:31": -0.04906779339287723
                    },
                    {
                        "10:32": -0.054368390888056645
                    },
                    {
                        "10:33": -0.04785359637880704
                    },
                    {
                        "10:34": -0.03545590696817502
                    },
                    {
                        "10:35": -0.03424997055751704
                    },
                    {
                        "10:36": -0.03983520093589432
                    },
                    {
                        "10:37": -0.03723083906425793
                    },
                    {
                        "10:38": -0.04357796101599906
                    },
                    {
                        "10:39": -0.03480789832757514
                    },
                    {
                        "10:40": -0.03277966335018236
                    },
                    {
                        "10:41": -0.04444286482557236
                    },
                    {
                        "10:42": -0.03053692971728834
                    },
                    {
                        "10:43": -0.030778505842558413
                    },
                    {
                        "10:44": -0.0278281161124184
                    },
                    {
                        "10:45": -0.0268392514255964
                    },
                    {
                        "10:46": -0.02400864300947734
                    },
                    {
                        "10:47": -0.03454903431817244
                    },
                    {
                        "10:48": -0.030081328058301438
                    },
                    {
                        "10:49": -0.03548927849882649
                    },
                    {
                        "10:50": -0.014409806930652903
                    },
                    {
                        "10:51": -0.017281866467856233
                    },
                    {
                        "10:52": -0.02977137840009203
                    },
                    {
                        "10:53": -0.019539431852844097
                    },
                    {
                        "10:54": -0.030538376531281747
                    },
                    {
                        "10:55": -0.03376309435589799
                    },
                    {
                        "10:56": -0.04822355987393915
                    },
                    {
                        "10:57": -0.03005077683437054
                    },
                    {
                        "10:58": -0.03552796959059459
                    },
                    {
                        "10:59": -0.0688882842653263
                    },
                    {
                        "11:00": -0.03436989990983945
                    },
                    {
                        "11:01": -0.017527072074044758
                    },
                    {
                        "11:02": -0.011414264411425656
                    },
                    {
                        "11:03": -0.022482335018799444
                    },
                    {
                        "11:04": -0.006358350869442808
                    },
                    {
                        "11:05": -0.008686909666569532
                    },
                    {
                        "11:06": -0.0235969074892036
                    },
                    {
                        "11:07": -0.04866433406549195
                    },
                    {
                        "11:08": -0.0478718078976593
                    },
                    {
                        "11:09": -0.0473507394068053
                    },
                    {
                        "11:10": -0.027225504729118066
                    },
                    {
                        "11:11": -0.03273055711254882
                    },
                    {
                        "11:12": -0.03024284052295605
                    },
                    {
                        "11:13": -0.024911880393745506
                    },
                    {
                        "11:14": -0.027543459663077363
                    },
                    {
                        "11:15": -0.04674459178668036
                    },
                    {
                        "11:16": -0.03453544004064566
                    },
                    {
                        "11:17": -0.053951086789880365
                    },
                    {
                        "11:18": -0.03564288105283695
                    },
                    {
                        "11:19": -0.03757191710203915
                    },
                    {
                        "11:20": -0.02925004822867361
                    },
                    {
                        "11:21": -0.02836367235328994
                    },
                    {
                        "11:22": -0.031540523019998656
                    },
                    {
                        "11:23": -0.0307875174073833
                    },
                    {
                        "11:24": -0.03702848337088796
                    },
                    {
                        "11:25": -0.04064833757569494
                    },
                    {
                        "11:26": -0.040078156864883495
                    },
                    {
                        "11:27": -0.05151165493717669
                    },
                    {
                        "11:28": -0.027746485051566426
                    },
                    {
                        "11:29": -0.038248077055758146
                    },
                    {
                        "11:30": -0.03802845934743666
                    },
                    {
                        "11:31": -0.04236167769729432
                    },
                    {
                        "11:32": -0.031103289685682056
                    },
                    {
                        "11:33": -0.03796296866639437
                    },
                    {
                        "11:34": -0.044340415867861215
                    },
                    {
                        "11:35": -0.04512221869377371
                    },
                    {
                        "11:36": -0.04525895158385651
                    },
                    {
                        "11:37": -0.045448633510159264
                    },
                    {
                        "11:38": -0.05902920449654667
                    },
                    {
                        "11:39": -0.056882011695182366
                    },
                    {
                        "11:40": -0.04686887313220933
                    },
                    {
                        "11:41": -0.0658345210584699
                    },
                    {
                        "11:42": -0.05958634075044622
                    },
                    {
                        "11:43": -0.038623308488844155
                    },
                    {
                        "11:44": -0.04479495360503005
                    },
                    {
                        "11:45": -0.06207370349734001
                    },
                    {
                        "11:46": -0.045535801977836354
                    },
                    {
                        "11:47": -0.0745955112213893
                    },
                    {
                        "11:48": -0.056843503519445934
                    },
                    {
                        "11:49": -0.05241371718760466
                    },
                    {
                        "11:50": -0.05405971810080856
                    },
                    {
                        "11:51": -0.045555610473203376
                    },
                    {
                        "11:52": -0.043228380714204005
                    },
                    {
                        "11:53": -0.041883669382004426
                    },
                    {
                        "11:54": -0.049949496634771495
                    },
                    {
                        "11:55": -0.0445762652423078
                    },
                    {
                        "11:56": -0.04356752788327356
                    },
                    {
                        "11:57": -0.04272776826285381
                    },
                    {
                        "11:58": -0.048180296870851236
                    },
                    {
                        "11:59": -0.045186902756678804
                    },
                    {
                        "12:00": -0.03510266230624215
                    },
                    {
                        "12:01": -0.03339421003331202
                    },
                    {
                        "12:02": -0.031647371381447485
                    },
                    {
                        "12:03": -0.04249974076832415
                    },
                    {
                        "12:04": -0.03931014900193639
                    },
                    {
                        "12:05": -0.035324279968621794
                    },
                    {
                        "12:06": -0.030368303483450453
                    },
                    {
                        "12:07": -0.0319212309529461
                    },
                    {
                        "12:08": 0.004094108829881371
                    },
                    {
                        "12:09": -0.021435704493171514
                    },
                    {
                        "12:10": -0.024807216183772306
                    },
                    {
                        "12:11": -0.022926196089640926
                    },
                    {
                        "12:12": -0.014725060329764283
                    },
                    {
                        "12:13": -0.011550848970114203
                    },
                    {
                        "12:14": -0.01610708317619245
                    },
                    {
                        "12:15": -0.019471906994077682
                    },
                    {
                        "12:16": -0.017593948012911496
                    },
                    {
                        "12:17": -0.008156097068038859
                    },
                    {
                        "12:18": -0.005597464497649219
                    },
                    {
                        "12:19": -0.00778298700507356
                    },
                    {
                        "12:20": -0.011596199638792392
                    },
                    {
                        "12:21": -0.010787397080055428
                    },
                    {
                        "12:22": -0.007319123925869952
                    },
                    {
                        "12:23": -0.009081612137136963
                    },
                    {
                        "12:24": -0.0006940913120684789
                    },
                    {
                        "12:25": 0.0002412480087518043
                    },
                    {
                        "12:26": 0.004230274440768911
                    },
                    {
                        "12:27": 0.008044443017518966
                    },
                    {
                        "12:28": 0.007424735742777444
                    },
                    {
                        "12:29": -0.007487038429830117
                    },
                    {
                        "12:30": -0.006722812393435018
                    },
                    {
                        "12:31": 0.0066673186048470615
                    },
                    {
                        "12:32": 0.011000442461179283
                    },
                    {
                        "12:33": 0.017734086870641354
                    },
                    {
                        "12:34": 0.01307162946970546
                    },
                    {
                        "12:35": 0.007391665807661841
                    },
                    {
                        "12:36": 0.008590663331419468
                    },
                    {
                        "12:37": 0.000666294168995063
                    },
                    {
                        "12:38": 0.008753330813886896
                    },
                    {
                        "12:39": 0.006729254099610005
                    },
                    {
                        "12:40": 0.006649602460181159
                    },
                    {
                        "12:41": 0.008722665760920267
                    },
                    {
                        "12:42": 0.0041778176403559405
                    },
                    {
                        "12:43": 0.007575536792350479
                    },
                    {
                        "12:44": 0.0006454565856527817
                    },
                    {
                        "12:45": 0.008639120646401955
                    },
                    {
                        "12:46": 0.00785083883573281
                    },
                    {
                        "12:47": 0.014570185745848074
                    },
                    {
                        "12:48": 0.011996438166905276
                    },
                    {
                        "12:49": 0.010332820465778391
                    },
                    {
                        "12:50": 0.013497896950365806
                    },
                    {
                        "12:51": 0.0017269906903272236
                    },
                    {
                        "12:52": -0.004402369090545299
                    },
                    {
                        "12:53": -0.0014262300795682581
                    },
                    {
                        "12:54": -0.006335462124846836
                    },
                    {
                        "12:55": -0.009232120731763294
                    },
                    {
                        "12:56": -0.009679617472174652
                    },
                    {
                        "12:57": -0.013470804162298044
                    },
                    {
                        "12:58": -0.020647349489555843
                    },
                    {
                        "12:59": -0.017205807318234245
                    },
                    {
                        "13:00": -0.007829373436409926
                    },
                    {
                        "13:01": -0.00821265146599819
                    },
                    {
                        "13:02": -0.009743135022911287
                    },
                    {
                        "13:03": -0.00873570909817869
                    },
                    {
                        "13:04": -0.001733258605799448
                    },
                    {
                        "13:05": -0.0001470428071703056
                    },
                    {
                        "13:06": -0.007293044871322896
                    },
                    {
                        "13:07": -0.006723239157160865
                    },
                    {
                        "13:08": -0.008165039559385589
                    },
                    {
                        "13:09": -0.008647340377356993
                    },
                    {
                        "13:10": -0.010084636553385406
                    },
                    {
                        "13:11": -0.01350066745571179
                    },
                    {
                        "13:12": -0.004600200019718348
                    },
                    {
                        "13:13": -0.011861852580439258
                    },
                    {
                        "13:14": -0.004825292265668501
                    },
                    {
                        "13:15": 0.030318735588038548
                    },
                    {
                        "13:16": 0.02284425554407301
                    },
                    {
                        "13:17": 0.016986711682344845
                    },
                    {
                        "13:18": 0.01892709275729898
                    },
                    {
                        "13:19": 0.024259581820587916
                    },
                    {
                        "13:20": 0.02014145301365613
                    },
                    {
                        "13:21": 0.013778300741800953
                    },
                    {
                        "13:22": 0.017415458589998267
                    },
                    {
                        "13:23": 0.01839789177278215
                    },
                    {
                        "13:24": 0.008630078804547225
                    },
                    {
                        "13:25": 0.014711399611575037
                    },
                    {
                        "13:26": 0.012777265518041037
                    },
                    {
                        "13:27": 0.012520712269647105
                    },
                    {
                        "13:28": 0.006286514413346223
                    },
                    {
                        "13:29": -0.007008400797852454
                    },
                    {
                        "13:30": -0.04182515343934869
                    },
                    {
                        "13:31": -0.03916105236512597
                    },
                    {
                        "13:32": -0.03229988292905499
                    },
                    {
                        "13:33": -0.02323976770719822
                    },
                    {
                        "13:34": -0.03885965767846431
                    },
                    {
                        "13:35": 0.03561500766663481
                    },
                    {
                        "13:36": 0.041776755383743175
                    },
                    {
                        "13:37": 0.0527366829474199
                    },
                    {
                        "13:38": 0.05335688106686318
                    },
                    {
                        "13:39": -0.03514203623481678
                    },
                    {
                        "13:40": -0.01935501212167794
                    },
                    {
                        "13:41": -0.02961311119501473
                    },
                    {
                        "13:42": 0.024478115899362912
                    },
                    {
                        "13:43": 0.023785732413630606
                    },
                    {
                        "13:44": 0.018033164356164644
                    },
                    {
                        "13:45": 0.007142332039512422
                    },
                    {
                        "13:46": -0.06229706787650857
                    },
                    {
                        "13:47": -0.0560267726490842
                    },
                    {
                        "13:48": -0.05693640568356133
                    },
                    {
                        "13:49": -0.062144591000061866
                    },
                    {
                        "13:50": -0.05353175210763332
                    },
                    {
                        "13:51": -0.05192868727961786
                    },
                    {
                        "13:52": -0.049739776033750946
                    },
                    {
                        "13:53": -0.042730643936977564
                    },
                    {
                        "13:54": -0.042149849650874184
                    },
                    {
                        "13:55": -0.04347210587722965
                    },
                    {
                        "13:56": -0.03991757960634797
                    },
                    {
                        "13:57": -0.04096796739604756
                    },
                    {
                        "13:58": -0.04077791578625274
                    },
                    {
                        "13:59": -0.03978779925855225
                    },
                    {
                        "14:00": -0.03494960898321953
                    },
                    {
                        "14:01": -0.03646283764928393
                    },
                    {
                        "14:02": -0.03333617242757227
                    },
                    {
                        "14:03": -0.04042768123294536
                    },
                    {
                        "14:04": -0.03705402991278759
                    },
                    {
                        "14:05": -0.04981557163898211
                    },
                    {
                        "14:06": -0.05321978557895359
                    },
                    {
                        "14:07": -0.043120998287158915
                    },
                    {
                        "14:08": -0.0426817902884884
                    },
                    {
                        "14:09": -0.038258673228329876
                    },
                    {
                        "14:10": -0.030445375844734522
                    },
                    {
                        "14:11": -0.019921511500658594
                    },
                    {
                        "14:12": 0.020686302639162185
                    },
                    {
                        "14:13": 0.020757208160610996
                    },
                    {
                        "14:14": 0.02958246815740112
                    },
                    {
                        "14:15": 0.03376388891277496
                    },
                    {
                        "14:16": -0.011775625564328407
                    },
                    {
                        "14:17": -0.022705834641130317
                    },
                    {
                        "14:18": -0.013895719381036797
                    },
                    {
                        "14:19": -0.00662693782645365
                    },
                    {
                        "14:20": -0.002036863565002478
                    },
                    {
                        "14:21": -0.00206958032818112
                    },
                    {
                        "14:22": -0.012515106172080338
                    },
                    {
                        "14:23": -0.004029014122183328
                    },
                    {
                        "14:24": 0.003079037553245079
                    },
                    {
                        "14:25": -0.001721356581296063
                    },
                    {
                        "14:26": 0.012805386830946985
                    },
                    {
                        "14:27": -0.0055707860429468955
                    },
                    {
                        "14:28": -0.01163673888479646
                    },
                    {
                        "14:29": -0.0008061827756849383
                    },
                    {
                        "14:30": -0.00005021211201168274
                    },
                    {
                        "14:31": -0.002690468804644075
                    },
                    {
                        "14:32": -0.004640929610162092
                    },
                    {
                        "14:33": -0.008921807470271936
                    },
                    {
                        "14:34": -0.00501371519736753
                    },
                    {
                        "14:35": -0.01448180015389151
                    },
                    {
                        "14:36": -0.0060873130507260505
                    },
                    {
                        "14:37": -0.004540892236453087
                    },
                    {
                        "14:38": 0.0012662268761515216
                    },
                    {
                        "14:39": 0.014379133973723568
                    },
                    {
                        "14:40": 0.017075807699462552
                    },
                    {
                        "14:41": 0.004107724848729455
                    },
                    {
                        "14:42": -0.013573967203887437
                    },
                    {
                        "14:43": -0.005967596644462692
                    },
                    {
                        "14:44": -0.0039048381725847793
                    },
                    {
                        "14:45": -0.009066813418698971
                    },
                    {
                        "14:46": -0.0023631471822552095
                    },
                    {
                        "14:47": -0.009623634042043073
                    },
                    {
                        "14:48": -0.011023151408494924
                    },
                    {
                        "14:49": -0.015086909106292557
                    },
                    {
                        "14:50": -0.015358611848907211
                    },
                    {
                        "14:51": -0.015425210126879096
                    },
                    {
                        "14:52": -0.01595847224744591
                    },
                    {
                        "14:53": -0.01947909512005559
                    },
                    {
                        "14:54": -0.02532225313255394
                    },
                    {
                        "14:55": -0.02542384587215485
                    },
                    {
                        "14:56": -0.021967575473572552
                    },
                    {
                        "14:57": -0.02423618559494136
                    },
                    {
                        "14:58": -0.020243743618463948
                    },
                    {
                        "14:59": -0.01362855289830942
                    },
                    {
                        "15:00": -0.011306693679019486
                    },
                    {
                        "15:01": -0.013163578828675849
                    },
                    {
                        "15:02": -0.009865474780550044
                    },
                    {
                        "15:03": -0.010144516621156608
                    },
                    {
                        "15:04": -0.025466246265466452
                    },
                    {
                        "15:05": 0.04486210461607262
                    },
                    {
                        "15:06": 0.04744170952814333
                    },
                    {
                        "15:07": 0.05301362512292221
                    },
                    {
                        "15:08": 0.06514777030599928
                    },
                    {
                        "15:09": -0.00867580061433495
                    },
                    {
                        "15:10": -0.010546017104035577
                    },
                    {
                        "15:11": -0.015708211890860933
                    },
                    {
                        "15:12": 0.0004268986070014691
                    },
                    {
                        "15:13": -0.0015259362054202085
                    },
                    {
                        "15:14": 0.003893977781652236
                    },
                    {
                        "15:15": 0.003625062680444935
                    },
                    {
                        "15:16": 0.002184222757545107
                    },
                    {
                        "15:17": 0.0012621032804016608
                    },
                    {
                        "15:18": -0.001803726009605411
                    },
                    {
                        "15:19": 0.0002643742743527744
                    },
                    {
                        "15:20": -0.007068780182162393
                    },
                    {
                        "15:21": -0.01635585977913403
                    },
                    {
                        "15:22": -0.01420172810185607
                    },
                    {
                        "15:23": 0.08578355744153104
                    },
                    {
                        "15:24": 0.07659455436019943
                    },
                    {
                        "15:25": 0.08302108189942287
                    },
                    {
                        "15:26": 0.08402848806156998
                    },
                    {
                        "15:27": -0.005084210164260727
                    },
                    {
                        "15:28": -0.014508206862009442
                    },
                    {
                        "15:29": -0.0133218361953245
                    },
                    {
                        "15:30": 0.09797810896947359
                    },
                    {
                        "15:31": 0.10016230244355598
                    },
                    {
                        "15:32": 0.10531735141936144
                    },
                    {
                        "15:33": 0.10801396129116775
                    },
                    {
                        "15:34": -0.019668709351426127
                    },
                    {
                        "15:35": -0.021643685876198072
                    },
                    {
                        "15:36": 0.10167912395779047
                    },
                    {
                        "15:37": 0.09880731416599109
                    },
                    {
                        "15:38": 0.09539193837096543
                    },
                    {
                        "15:39": 0.09549638494404614
                    },
                    {
                        "15:40": -0.027067404334843025
                    },
                    {
                        "15:41": -0.04567574990999377
                    },
                    {
                        "15:42": 0.08640900570416618
                    },
                    {
                        "15:43": 0.08232351294090226
                    },
                    {
                        "15:44": 0.08730182263199435
                    },
                    {
                        "15:45": 0.07298505692652218
                    },
                    {
                        "15:46": -0.03246246146171141
                    },
                    {
                        "15:47": -0.02487389651091354
                    },
                    {
                        "15:48": -0.029864692062219332
                    },
                    {
                        "15:49": 0.08874747301169908
                    },
                    {
                        "15:50": 0.096322166745296
                    },
                    {
                        "15:51": 0.08841184014312342
                    },
                    {
                        "15:52": 0.08402880758730996
                    },
                    {
                        "15:53": -0.02623927302709981
                    },
                    {
                        "15:54": -0.02859390078101489
                    },
                    {
                        "15:55": -0.02587941544996102
                    },
                    {
                        "15:56": -0.02821005316298535
                    },
                    {
                        "15:57": -0.030715198290751998
                    },
                    {
                        "15:58": -0.027974391297413147
                    },
                    {
                        "15:59": -0.023127375877895685
                    }
                ],
                "avg_volume": 1181302080,
                "expected_return": 0.31520385677481977,
                "median_high_spike": 0.24635331639080182,
                "median_high_time": "12:07:00",
                "median_low_spike": -0.1362745109497241,
                "median_low_time": "12:00:00",
                "median_return": 0.06250007965259119,
                "median_return_series": [
                    {
                        "09:30": -0.017730819719953328
                    },
                    {
                        "09:31": -0.02964743589743596
                    },
                    {
                        "09:32": -0.024038461538461675
                    },
                    {
                        "09:33": -0.02183493589743596
                    },
                    {
                        "09:34": -0.03092147435897441
                    },
                    {
                        "09:35": -0.03630608974358979
                    },
                    {
                        "09:36": -0.02914157963905567
                    },
                    {
                        "09:37": -0.0674038461538462
                    },
                    {
                        "09:38": -0.041538461538461524
                    },
                    {
                        "09:39": -0.026730769230769225
                    },
                    {
                        "09:40": -0.05769230769230771
                    },
                    {
                        "09:41": -0.03027702488890116
                    },
                    {
                        "09:42": -0.04179192520947134
                    },
                    {
                        "09:43": -0.07913461538461541
                    },
                    {
                        "09:44": -0.057214874867575594
                    },
                    {
                        "09:45": -0.02083333333333337
                    },
                    {
                        "09:46": -0.05843998940605094
                    },
                    {
                        "09:47": -0.06300480769230771
                    },
                    {
                        "09:48": -0.05429192520947135
                    },
                    {
                        "09:49": -0.0513701923076923
                    },
                    {
                        "09:50": -0.02083333333333337
                    },
                    {
                        "09:51": -0.015625
                    },
                    {
                        "09:52": -0.04286858974358976
                    },
                    {
                        "09:53": -0.02604166666666663
                    },
                    {
                        "09:54": -0.02083333333333337
                    },
                    {
                        "09:55": -0.0016097299230907192
                    },
                    {
                        "09:56": -0.00520833333333337
                    },
                    {
                        "09:57": -0.02183493589743596
                    },
                    {
                        "09:58": -0.033160952354745976
                    },
                    {
                        "09:59": -0.039423076923077005
                    },
                    {
                        "10:00": -0.00520833333333337
                    },
                    {
                        "10:01": -0.02697916666666672
                    },
                    {
                        "10:02": -0.022192689487225414
                    },
                    {
                        "10:03": -0.013414416025755771
                    },
                    {
                        "10:04": -0.019230769230769273
                    },
                    {
                        "10:05": -0.022435897435897523
                    },
                    {
                        "10:06": -0.02083333333333337
                    },
                    {
                        "10:07": -0.027524038461538503
                    },
                    {
                        "10:08": -0.02964743589743596
                    },
                    {
                        "10:09": -0.030949519230769273
                    },
                    {
                        "10:10": -0.02834535256410259
                    },
                    {
                        "10:11": -0.024639423076923128
                    },
                    {
                        "10:12": -0.019631410256410242
                    },
                    {
                        "10:13": -0.0028044871794871695
                    },
                    {
                        "10:14": -0.0003577177606869375
                    },
                    {
                        "10:15": -0.02083333333333337
                    },
                    {
                        "10:16": -0.009615384615384581
                    },
                    {
                        "10:17": -0.017427884615384637
                    },
                    {
                        "10:18": -0.010416666666666685
                    },
                    {
                        "10:19": -0.0006009615384615641
                    },
                    {
                        "10:20": -0.015224358974358976
                    },
                    {
                        "10:21": -0.015224358974358976
                    },
                    {
                        "10:22": -0.0078125
                    },
                    {
                        "10:23": -0.010910391700947986
                    },
                    {
                        "10:24": -0.014559066282120059
                    },
                    {
                        "10:25": 0.0018028846153845812
                    },
                    {
                        "10:26": -0.014308710427472726
                    },
                    {
                        "10:27": -0.014308710427472726
                    },
                    {
                        "10:28": -0.01676615691885769
                    },
                    {
                        "10:29": -0.01652644230769229
                    },
                    {
                        "10:30": -0.015224358974358976
                    },
                    {
                        "10:31": -0.02834535256410259
                    },
                    {
                        "10:32": -0.040364583333333315
                    },
                    {
                        "10:33": -0.027139423076923075
                    },
                    {
                        "10:34": -0.015625
                    },
                    {
                        "10:35": -0.015625
                    },
                    {
                        "10:36": -0.015625
                    },
                    {
                        "10:37": -0.015625
                    },
                    {
                        "10:38": -0.020032051282051322
                    },
                    {
                        "10:39": -0.02083333333333337
                    },
                    {
                        "10:40": -0.0234375
                    },
                    {
                        "10:41": -0.015224358974358976
                    },
                    {
                        "10:42": -0.014423076923077094
                    },
                    {
                        "10:43": -0.01822916666666663
                    },
                    {
                        "10:44": -0.009615384615384581
                    },
                    {
                        "10:45": -0.009615384615384581
                    },
                    {
                        "10:46": 0.0026041666666667407
                    },
                    {
                        "10:47": -0.002403846153846201
                    },
                    {
                        "10:48": -0.00390625
                    },
                    {
                        "10:49": -0.0016204428247779679
                    },
                    {
                        "10:50": 0.0019674476837774346
                    },
                    {
                        "10:51": 0.0019674476837774346
                    },
                    {
                        "10:52": -0.0016204428247779679
                    },
                    {
                        "10:53": 0.007337526205450806
                    },
                    {
                        "10:54": 0.002096436058700246
                    },
                    {
                        "10:55": 0
                    },
                    {
                        "10:56": -0.00520833333333337
                    },
                    {
                        "10:57": 0.003577177606868265
                    },
                    {
                        "10:58": -0.01041666666666663
                    },
                    {
                        "10:59": -0.028846153846153855
                    },
                    {
                        "11:00": -0.016276158111250272
                    },
                    {
                        "11:01": 0.0014308710427470839
                    },
                    {
                        "11:02": -0.008227508495796898
                    },
                    {
                        "11:03": -0.01041666666666663
                    },
                    {
                        "11:04": 0.016771488469601747
                    },
                    {
                        "11:05": 0.018867924528302105
                    },
                    {
                        "11:06": 0.01041666666666674
                    },
                    {
                        "11:07": -0.03747093543194424
                    },
                    {
                        "11:08": -0.00520833333333337
                    },
                    {
                        "11:09": -0.02083333333333337
                    },
                    {
                        "11:10": -0.00520833333333337
                    },
                    {
                        "11:11": -0.00520833333333337
                    },
                    {
                        "11:12": 0.005208333333333259
                    },
                    {
                        "11:13": 0.01178426362683449
                    },
                    {
                        "11:14": 0
                    },
                    {
                        "11:15": -0.019932052256602883
                    },
                    {
                        "11:16": 0
                    },
                    {
                        "11:17": -0.02013233694032085
                    },
                    {
                        "11:18": -0.0078125
                    },
                    {
                        "11:19": -0.01041666666666663
                    },
                    {
                        "11:20": -0.00520833333333337
                    },
                    {
                        "11:21": -0.01041666666666663
                    },
                    {
                        "11:22": -0.015625
                    },
                    {
                        "11:23": -0.015625
                    },
                    {
                        "11:24": 0.008672366352201255
                    },
                    {
                        "11:25": 0.009615384615384581
                    },
                    {
                        "11:26": -0.0026041666666666297
                    },
                    {
                        "11:27": -0.014319423329159975
                    },
                    {
                        "11:28": 0.015625
                    },
                    {
                        "11:29": 0.019230769230769162
                    },
                    {
                        "11:30": 0.016771488469601747
                    },
                    {
                        "11:31": -0.00031128324367463156
                    },
                    {
                        "11:32": 0.009615384615384581
                    },
                    {
                        "11:33": 0
                    },
                    {
                        "11:34": 0
                    },
                    {
                        "11:35": -0.009615384615384581
                    },
                    {
                        "11:36": -0.009615384615384581
                    },
                    {
                        "11:37": -0.009615384615384581
                    },
                    {
                        "11:38": -0.022561155978702063
                    },
                    {
                        "11:39": -0.015349617517163683
                    },
                    {
                        "11:40": -0.019230769230769273
                    },
                    {
                        "11:41": -0.021856469188118344
                    },
                    {
                        "11:42": -0.016902164192452163
                    },
                    {
                        "11:43": 0.023857039187228035
                    },
                    {
                        "11:44": 0.016771488469601747
                    },
                    {
                        "11:45": -0.007376209017239288
                    },
                    {
                        "11:46": 0.024947589098532674
                    },
                    {
                        "11:47": -0.031167879696765433
                    },
                    {
                        "11:48": -0.014423076923077094
                    },
                    {
                        "11:49": -0.009615384615384581
                    },
                    {
                        "11:50": -0.019230769230769273
                    },
                    {
                        "11:51": -0.009615384615384581
                    },
                    {
                        "11:52": -0.019230769230769273
                    },
                    {
                        "11:53": -0.03846153846153855
                    },
                    {
                        "11:54": -0.03804319785919685
                    },
                    {
                        "11:55": -0.009615384615384581
                    },
                    {
                        "11:56": 0
                    },
                    {
                        "11:57": -0.009615384615384581
                    },
                    {
                        "11:58": -0.009615384615384581
                    },
                    {
                        "11:59": -0.024038461538461675
                    },
                    {
                        "12:00": -0.009615384615384581
                    },
                    {
                        "12:01": 0.009326923076923066
                    },
                    {
                        "12:02": 0.018942307692307647
                    },
                    {
                        "12:03": -0.009615384615384581
                    },
                    {
                        "12:04": -0.009807692307692295
                    },
                    {
                        "12:05": -0.014423076923077094
                    },
                    {
                        "12:06": -0.019230769230769273
                    },
                    {
                        "12:07": -0.014423076923077094
                    },
                    {
                        "12:08": -0.017170452512967338
                    },
                    {
                        "12:09": -0.007512072974423356
                    },
                    {
                        "12:10": -0.00017885888034341324
                    },
                    {
                        "12:11": 0.0014308710427470839
                    },
                    {
                        "12:12": 0.0012520121624037817
                    },
                    {
                        "12:13": 0.0012520121624037817
                    },
                    {
                        "12:14": -0.015918440350563445
                    },
                    {
                        "12:15": -0.0005365766410303507
                    },
                    {
                        "12:16": -0.0003577177606869375
                    },
                    {
                        "12:17": -0.00214630656412107
                    },
                    {
                        "12:18": -0.003756036487211567
                    },
                    {
                        "12:19": 0.0016097299230906081
                    },
                    {
                        "12:20": 0.010552673940261048
                    },
                    {
                        "12:21": 0.015024145948846268
                    },
                    {
                        "12:22": 0.03291003398318715
                    },
                    {
                        "12:23": 0.025219102128420712
                    },
                    {
                        "12:24": 0.03201573958146997
                    },
                    {
                        "12:25": 0.050617063137184726
                    },
                    {
                        "12:26": 0.052410901467505155
                    },
                    {
                        "12:27": 0.05448637316561844
                    },
                    {
                        "12:28": 0.05243186582809245
                    },
                    {
                        "12:29": 0.028301886792452935
                    },
                    {
                        "12:30": 0.03563941299790363
                    },
                    {
                        "12:31": 0.04423480083857445
                    },
                    {
                        "12:32": 0.05660377358490587
                    },
                    {
                        "12:33": 0.06079664570230614
                    },
                    {
                        "12:34": 0.05031446540880502
                    },
                    {
                        "12:35": 0.044025157232704615
                    },
                    {
                        "12:36": 0.04192872117400426
                    },
                    {
                        "12:37": 0.023060796645702375
                    },
                    {
                        "12:38": 0.033542976939203495
                    },
                    {
                        "12:39": 0.02515723270440251
                    },
                    {
                        "12:40": 0.024109014675052443
                    },
                    {
                        "12:41": 0.029350104821803003
                    },
                    {
                        "12:42": 0.027253668763102867
                    },
                    {
                        "12:43": 0.03773584905660399
                    },
                    {
                        "12:44": 0.027253668763102867
                    },
                    {
                        "12:45": 0.029350104821803003
                    },
                    {
                        "12:46": 0.033542976939203495
                    },
                    {
                        "12:47": 0.048218029350104885
                    },
                    {
                        "12:48": 0.052410901467505155
                    },
                    {
                        "12:49": 0.04088050314465419
                    },
                    {
                        "12:50": 0.052410901467505155
                    },
                    {
                        "12:51": 0.02515723270440251
                    },
                    {
                        "12:52": 0.027253668763102867
                    },
                    {
                        "12:53": 0.033542976939203495
                    },
                    {
                        "12:54": 0.03352201257861642
                    },
                    {
                        "12:55": 0.03773584905660399
                    },
                    {
                        "12:56": 0.044025157232704615
                    },
                    {
                        "12:57": -0.002096436058700135
                    },
                    {
                        "12:58": 0.01048218029350112
                    },
                    {
                        "12:59": 0.004192872117400492
                    },
                    {
                        "13:00": 0.012578616352201255
                    },
                    {
                        "13:01": 0.012788259958071535
                    },
                    {
                        "13:02": 0.012578616352201255
                    },
                    {
                        "13:03": 0.01465408805031454
                    },
                    {
                        "13:04": 0.02096436058700224
                    },
                    {
                        "13:05": 0.014675052410901612
                    },
                    {
                        "13:06": -0.028942307692307656
                    },
                    {
                        "13:07": -0.03144654088050303
                    },
                    {
                        "13:08": -0.02935010482180289
                    },
                    {
                        "13:09": -0.027253668763102756
                    },
                    {
                        "13:10": -0.012578616352201144
                    },
                    {
                        "13:11": -0.020964360587002018
                    },
                    {
                        "13:12": -0.018888888888888844
                    },
                    {
                        "13:13": -0.039423076923077005
                    },
                    {
                        "13:14": -0.03146750524108999
                    },
                    {
                        "13:15": -0.012578616352201144
                    },
                    {
                        "13:16": -0.008385744234800652
                    },
                    {
                        "13:17": -0.012578616352201144
                    },
                    {
                        "13:18": -0.008385744234800652
                    },
                    {
                        "13:19": -0.00006289308176088415
                    },
                    {
                        "13:20": -0.020964360587002018
                    },
                    {
                        "13:21": -0.02100628930817594
                    },
                    {
                        "13:22": -0.016771488469601525
                    },
                    {
                        "13:23": -0.01467505241090139
                    },
                    {
                        "13:24": -0.016771488469601525
                    },
                    {
                        "13:25": -0.0000961538461538014
                    },
                    {
                        "13:26": -0.012578616352201144
                    },
                    {
                        "13:27": 0
                    },
                    {
                        "13:28": -0.009615384615384581
                    },
                    {
                        "13:29": -0.019230769230769273
                    },
                    {
                        "13:30": -0.0033983187265247405
                    },
                    {
                        "13:31": -0.01467505241090139
                    },
                    {
                        "13:32": -0.008385744234800652
                    },
                    {
                        "13:33": -0.026205450733752578
                    },
                    {
                        "13:34": -0.02444444444444427
                    },
                    {
                        "13:35": 0.009222803794808054
                    },
                    {
                        "13:36": 0.021999023587999156
                    },
                    {
                        "13:37": 0.020767837048685955
                    },
                    {
                        "13:38": 0.020688121108085267
                    },
                    {
                        "13:39": -0.022012578616352085
                    },
                    {
                        "13:40": -0.0251572327044024
                    },
                    {
                        "13:41": -0.04402515723270439
                    },
                    {
                        "13:42": 0.011706632439751397
                    },
                    {
                        "13:43": -0.003406099275302832
                    },
                    {
                        "13:44": -0.008288639236388673
                    },
                    {
                        "13:45": -0.014257002587641787
                    },
                    {
                        "13:46": -0.06943396226415088
                    },
                    {
                        "13:47": -0.07113207547169809
                    },
                    {
                        "13:48": -0.07547169811320742
                    },
                    {
                        "13:49": -0.08343815513626829
                    },
                    {
                        "13:50": -0.08071278825995798
                    },
                    {
                        "13:51": -0.07756813417190755
                    },
                    {
                        "13:52": -0.07127882599580715
                    },
                    {
                        "13:53": -0.06918238993710679
                    },
                    {
                        "13:54": -0.06918238993710679
                    },
                    {
                        "13:55": -0.06813417190775672
                    },
                    {
                        "13:56": -0.054711538461538534
                    },
                    {
                        "13:57": -0.04461538461538461
                    },
                    {
                        "13:58": -0.03903846153846158
                    },
                    {
                        "13:59": -0.0459615384615385
                    },
                    {
                        "14:00": -0.03846153846153855
                    },
                    {
                        "14:01": -0.03163461538461532
                    },
                    {
                        "14:02": -0.04346153846153844
                    },
                    {
                        "14:03": -0.048942307692307785
                    },
                    {
                        "14:04": -0.05555555555555547
                    },
                    {
                        "14:05": -0.05761006289308179
                    },
                    {
                        "14:06": -0.06079664570230592
                    },
                    {
                        "14:07": -0.06289308176100628
                    },
                    {
                        "14:08": -0.06603773584905648
                    },
                    {
                        "14:09": -0.05555555555555547
                    },
                    {
                        "14:10": -0.04503144654088043
                    },
                    {
                        "14:11": -0.04402515723270439
                    },
                    {
                        "14:12": 0.024305555555555636
                    },
                    {
                        "14:13": 0.020603052935010635
                    },
                    {
                        "14:14": 0.03052935010482194
                    },
                    {
                        "14:15": 0.020399305555555636
                    },
                    {
                        "14:16": -0.04926624737945484
                    },
                    {
                        "14:17": -0.04612159329140453
                    },
                    {
                        "14:18": -0.04926624737945484
                    },
                    {
                        "14:19": -0.046436058700209615
                    },
                    {
                        "14:20": -0.04088050314465397
                    },
                    {
                        "14:21": -0.04402515723270439
                    },
                    {
                        "14:22": -0.041907756813417074
                    },
                    {
                        "14:23": -0.041928721174004036
                    },
                    {
                        "14:24": -0.04538784067085955
                    },
                    {
                        "14:25": -0.04117400419287209
                    },
                    {
                        "14:26": -0.041928721174004036
                    },
                    {
                        "14:27": -0.04278825995807123
                    },
                    {
                        "14:28": -0.04402515723270439
                    },
                    {
                        "14:29": -0.03878406708595383
                    },
                    {
                        "14:30": -0.03878406708595383
                    },
                    {
                        "14:31": -0.037735849056603765
                    },
                    {
                        "14:32": -0.0429769392033541
                    },
                    {
                        "14:33": -0.047169811320754595
                    },
                    {
                        "14:34": -0.04245283018867918
                    },
                    {
                        "14:35": -0.041928721174004036
                    },
                    {
                        "14:36": -0.04081761006289297
                    },
                    {
                        "14:37": -0.0429769392033541
                    },
                    {
                        "14:38": -0.03878406708595383
                    },
                    {
                        "14:39": -0.03878406708595383
                    },
                    {
                        "14:40": -0.03668763102725359
                    },
                    {
                        "14:41": -0.037735849056603765
                    },
                    {
                        "14:42": -0.03563941299790352
                    },
                    {
                        "14:43": -0.020964360587002018
                    },
                    {
                        "14:44": -0.015723270440251458
                    },
                    {
                        "14:45": -0.01467505241090139
                    },
                    {
                        "14:46": -0.017819706498951815
                    },
                    {
                        "14:47": -0.012578616352201144
                    },
                    {
                        "14:48": -0.012578616352201144
                    },
                    {
                        "14:49": -0.01991614255765195
                    },
                    {
                        "14:50": -0.02492662473794549
                    },
                    {
                        "14:51": -0.02410901467505222
                    },
                    {
                        "14:52": -0.03144654088050303
                    },
                    {
                        "14:53": -0.03215932914046116
                    },
                    {
                        "14:54": -0.032243186582809114
                    },
                    {
                        "14:55": -0.03878406708595383
                    },
                    {
                        "14:56": -0.028301886792452824
                    },
                    {
                        "14:57": -0.03039832285115296
                    },
                    {
                        "14:58": -0.03144654088050303
                    },
                    {
                        "14:59": -0.03144654088050303
                    },
                    {
                        "15:00": -0.024465408805031452
                    },
                    {
                        "15:01": -0.02406708595387841
                    },
                    {
                        "15:02": -0.022012578616352085
                    },
                    {
                        "15:03": -0.02410901467505222
                    },
                    {
                        "15:04": -0.03138364779874203
                    },
                    {
                        "15:05": 0.04634599906443038
                    },
                    {
                        "15:06": 0.049302149402198514
                    },
                    {
                        "15:07": 0.06019342556030971
                    },
                    {
                        "15:08": 0.0778191255176588
                    },
                    {
                        "15:09": 0.04807692307692313
                    },
                    {
                        "15:10": 0.03846153846153855
                    },
                    {
                        "15:11": 0.024038461538461453
                    },
                    {
                        "15:12": 0.043269230769230616
                    },
                    {
                        "15:13": 0.05288461538461542
                    },
                    {
                        "15:14": 0.04807692307692313
                    },
                    {
                        "15:15": 0.04413461538461538
                    },
                    {
                        "15:16": 0.0575961538461538
                    },
                    {
                        "15:17": 0.07211538461538458
                    },
                    {
                        "15:18": 0.08653846153846145
                    },
                    {
                        "15:19": 0.10576923076923062
                    },
                    {
                        "15:20": 0.07596153846153841
                    },
                    {
                        "15:21": 0.07528846153846147
                    },
                    {
                        "15:22": 0.05288461538461542
                    },
                    {
                        "15:23": 0.09489750010318776
                    },
                    {
                        "15:24": 0.08408861081683483
                    },
                    {
                        "15:25": 0.10140478172337397
                    },
                    {
                        "15:26": 0.10602376071433484
                    },
                    {
                        "15:27": 0.0672115384615386
                    },
                    {
                        "15:28": 0.06028846153846157
                    },
                    {
                        "15:29": 0.05288461538461542
                    },
                    {
                        "15:30": 0.11199231594733294
                    },
                    {
                        "15:31": 0.11161227522254169
                    },
                    {
                        "15:32": 0.1216739127443831
                    },
                    {
                        "15:33": 0.12839525748799585
                    },
                    {
                        "15:34": 0.03846153846153855
                    },
                    {
                        "15:35": 0.03846153846153855
                    },
                    {
                        "15:36": 0.12332663759063334
                    },
                    {
                        "15:37": 0.11513621794871798
                    },
                    {
                        "15:38": 0.11077724358974372
                    },
                    {
                        "15:39": 0.11072516025641033
                    },
                    {
                        "15:40": 0.024038461538461453
                    },
                    {
                        "15:41": -0.019326923076923075
                    },
                    {
                        "15:42": 0.09469497681713734
                    },
                    {
                        "15:43": 0.08839342948717954
                    },
                    {
                        "15:44": 0.09037949038977477
                    },
                    {
                        "15:45": 0.06359491731216377
                    },
                    {
                        "15:46": -0.028846153846153855
                    },
                    {
                        "15:47": -0.028846153846153855
                    },
                    {
                        "15:48": -0.043653846153846154
                    },
                    {
                        "15:49": 0.07463789675715082
                    },
                    {
                        "15:50": 0.08549368490568632
                    },
                    {
                        "15:51": 0.0842647180220959
                    },
                    {
                        "15:52": 0.08147021999642279
                    },
                    {
                        "15:53": -0.004807692307692402
                    },
                    {
                        "15:54": 0.004807692307692291
                    },
                    {
                        "15:55": -0.004807692307692402
                    },
                    {
                        "15:56": -0.014423076923077094
                    },
                    {
                        "15:57": 0.004807692307692291
                    },
                    {
                        "15:58": 0.004807692307692291
                    },
                    {
                        "15:59": 0.019230769230769162
                    }
                ],
                "median_volume": 1202828700,
                "n_instances": 5,
                "winrate": 0.6
            },
            "day2": {
                "avg_high_spike": 0.3555305621094131,
                "avg_high_time": "11:42:30",
                "avg_low_spike": -0.24349835419908306,
                "avg_low_time": "13:50:00",
                "avg_return": 0.126839336691134,
                "avg_return_series": [
                    {
                        "09:30": -0.019833366992789443
                    },
                    {
                        "09:31": -0.04582485613699153
                    },
                    {
                        "09:32": -0.0806002945825729
                    },
                    {
                        "09:33": -0.0357132672486013
                    },
                    {
                        "09:34": -0.0618434099771615
                    },
                    {
                        "09:35": -0.05843198670576152
                    },
                    {
                        "09:36": -0.04550874397869731
                    },
                    {
                        "09:37": -0.06116884331149212
                    },
                    {
                        "09:38": -0.04301768243425186
                    },
                    {
                        "09:39": -0.04543622655057892
                    },
                    {
                        "09:40": -0.053472876711645724
                    },
                    {
                        "09:41": -0.05462555725099483
                    },
                    {
                        "09:42": -0.07026302371620348
                    },
                    {
                        "09:43": -0.07089922483519336
                    },
                    {
                        "09:44": -0.08309872069134032
                    },
                    {
                        "09:45": -0.11025956427210808
                    },
                    {
                        "09:46": -0.08730109754759692
                    },
                    {
                        "09:47": -0.08867765086916198
                    },
                    {
                        "09:48": -0.08304096355802892
                    },
                    {
                        "09:49": -0.08325496289979957
                    },
                    {
                        "09:50": -0.08489155421915051
                    },
                    {
                        "09:51": -0.07871067453549951
                    },
                    {
                        "09:52": -0.08030990385862032
                    },
                    {
                        "09:53": -0.07847530767236137
                    },
                    {
                        "09:54": -0.074311975785138
                    },
                    {
                        "09:55": -0.05944820931693747
                    },
                    {
                        "09:56": -0.06599949261486604
                    },
                    {
                        "09:57": -0.07095491253528015
                    },
                    {
                        "09:58": -0.0743002728909234
                    },
                    {
                        "09:59": -0.07235213837277725
                    },
                    {
                        "10:00": -0.06614722022758786
                    },
                    {
                        "10:01": -0.0767181220018152
                    },
                    {
                        "10:02": -0.06992159840030321
                    },
                    {
                        "10:03": -0.06589181352162683
                    },
                    {
                        "10:04": -0.05730647059410188
                    },
                    {
                        "10:05": -0.06396543298526973
                    },
                    {
                        "10:06": -0.068384171578454
                    },
                    {
                        "10:07": -0.05141042470753676
                    },
                    {
                        "10:08": -0.05477079157067496
                    },
                    {
                        "10:09": -0.054860939697214506
                    },
                    {
                        "10:10": -0.062070764019786805
                    },
                    {
                        "10:11": -0.04251224362714301
                    },
                    {
                        "10:12": -0.05003820971586433
                    },
                    {
                        "10:13": -0.03203234860724652
                    },
                    {
                        "10:14": -0.04293684364060679
                    },
                    {
                        "10:15": -0.039040605770477445
                    },
                    {
                        "10:16": -0.04436626554114889
                    },
                    {
                        "10:17": -0.04867077660525007
                    },
                    {
                        "10:18": -0.04583981589524181
                    },
                    {
                        "10:19": -0.04162973476348627
                    },
                    {
                        "10:20": -0.05274000438819578
                    },
                    {
                        "10:21": -0.04523529149768943
                    },
                    {
                        "10:22": -0.04386376428656916
                    },
                    {
                        "10:23": -0.04760428821470245
                    },
                    {
                        "10:24": -0.05014331760065427
                    },
                    {
                        "10:25": -0.04469461523501783
                    },
                    {
                        "10:26": -0.048288697154654
                    },
                    {
                        "10:27": -0.05102976119239244
                    },
                    {
                        "10:28": -0.05604611096151354
                    },
                    {
                        "10:29": -0.05846998137510099
                    },
                    {
                        "10:30": -0.056824018390529495
                    },
                    {
                        "10:31": -0.05646323286665689
                    },
                    {
                        "10:32": -0.06538864113205928
                    },
                    {
                        "10:33": -0.06904588531849327
                    },
                    {
                        "10:34": -0.06849933055081829
                    },
                    {
                        "10:35": -0.062192825588938516
                    },
                    {
                        "10:36": -0.07646371884630343
                    },
                    {
                        "10:37": -0.0635812781515451
                    },
                    {
                        "10:38": -0.06858612831483313
                    },
                    {
                        "10:39": -0.07071789386550187
                    },
                    {
                        "10:40": -0.05776735616702436
                    },
                    {
                        "10:41": -0.06188041667913313
                    },
                    {
                        "10:42": -0.054159074164361526
                    },
                    {
                        "10:43": -0.065042146002254
                    },
                    {
                        "10:44": -0.05936639813900609
                    },
                    {
                        "10:45": -0.05724133331338699
                    },
                    {
                        "10:46": -0.051049785452133754
                    },
                    {
                        "10:47": -0.046721194985489066
                    },
                    {
                        "10:48": -0.04500012154803579
                    },
                    {
                        "10:49": -0.0479748538930278
                    },
                    {
                        "10:50": -0.03515434107251503
                    },
                    {
                        "10:51": -0.03714585888958699
                    },
                    {
                        "10:52": -0.040350987094715185
                    },
                    {
                        "10:53": -0.030944259940759333
                    },
                    {
                        "10:54": -0.036831349805387104
                    },
                    {
                        "10:55": -0.06025946454038633
                    },
                    {
                        "10:56": -0.044908928646713114
                    },
                    {
                        "10:57": -0.0533734566516072
                    },
                    {
                        "10:58": -0.06632751648066704
                    },
                    {
                        "10:59": -0.0688882842653263
                    },
                    {
                        "11:00": -0.04833096272164242
                    },
                    {
                        "11:01": -0.037725082029341106
                    },
                    {
                        "11:02": -0.020600362723138393
                    },
                    {
                        "11:03": -0.022482335018799444
                    },
                    {
                        "11:04": -0.01374334290757869
                    },
                    {
                        "11:05": -0.01236112357757635
                    },
                    {
                        "11:06": -0.023974903815554338
                    },
                    {
                        "11:07": -0.039905155132693104
                    },
                    {
                        "11:08": -0.06409212343795194
                    },
                    {
                        "11:09": -0.06259474513558523
                    },
                    {
                        "11:10": -0.035713462037120225
                    },
                    {
                        "11:11": -0.04367953330540849
                    },
                    {
                        "11:12": -0.04084497077860553
                    },
                    {
                        "11:13": -0.04020396072066142
                    },
                    {
                        "11:14": -0.038644795500104766
                    },
                    {
                        "11:15": -0.04730197643339414
                    },
                    {
                        "11:16": -0.05379903060766537
                    },
                    {
                        "11:17": -0.06024933553740438
                    },
                    {
                        "11:18": -0.05640319727433204
                    },
                    {
                        "11:19": -0.06377500772920837
                    },
                    {
                        "11:20": -0.03698323172597531
                    },
                    {
                        "11:21": -0.035661237464402584
                    },
                    {
                        "11:22": -0.05132178813990366
                    },
                    {
                        "11:23": -0.052099695568919614
                    },
                    {
                        "11:24": -0.05775705539598478
                    },
                    {
                        "11:25": -0.06321245848667086
                    },
                    {
                        "11:26": -0.05010239253283669
                    },
                    {
                        "11:27": -0.06087203547457339
                    },
                    {
                        "11:28": -0.045183612332824676
                    },
                    {
                        "11:29": -0.043367871675193764
                    },
                    {
                        "11:30": -0.04264989890263374
                    },
                    {
                        "11:31": -0.049864458357019616
                    },
                    {
                        "11:32": -0.05130511424268721
                    },
                    {
                        "11:33": -0.062260955529625295
                    },
                    {
                        "11:34": -0.07001166861143526
                    },
                    {
                        "11:35": -0.07477261167459533
                    },
                    {
                        "11:36": -0.05493386851868473
                    },
                    {
                        "11:37": -0.07384276920084971
                    },
                    {
                        "11:38": -0.07328021995831213
                    },
                    {
                        "11:39": -0.07041729622315973
                    },
                    {
                        "11:40": -0.07243717524858136
                    },
                    {
                        "11:41": -0.0812212024653682
                    },
                    {
                        "11:42": -0.06818034487229352
                    },
                    {
                        "11:43": -0.057787052827892905
                    },
                    {
                        "11:44": -0.06886140344972029
                    },
                    {
                        "11:45": -0.07143720890803744
                    },
                    {
                        "11:46": -0.07288113724082224
                    },
                    {
                        "11:47": -0.0850923515742652
                    },
                    {
                        "11:48": -0.08626918588995607
                    },
                    {
                        "11:49": -0.07769381613459787
                    },
                    {
                        "11:50": -0.08113596300950443
                    },
                    {
                        "11:51": -0.04956212532605472
                    },
                    {
                        "11:52": -0.06162649036591561
                    },
                    {
                        "11:53": -0.05884872817121941
                    },
                    {
                        "11:54": -0.03577201192428736
                    },
                    {
                        "11:55": -0.057970621528089405
                    },
                    {
                        "11:56": -0.06251620640477114
                    },
                    {
                        "11:57": -0.06434581600494671
                    },
                    {
                        "11:58": -0.05492695175545961
                    },
                    {
                        "11:59": -0.06972275828022627
                    },
                    {
                        "12:00": -0.03819134907779895
                    },
                    {
                        "12:01": -0.05018750966151057
                    },
                    {
                        "12:02": -0.05311883533295433
                    },
                    {
                        "12:03": -0.0627900011469148
                    },
                    {
                        "12:04": -0.04797318182838167
                    },
                    {
                        "12:05": -0.04533540925478649
                    },
                    {
                        "12:06": -0.04611039485601909
                    },
                    {
                        "12:07": -0.048221859759746355
                    },
                    {
                        "12:08": -0.006998773299823531
                    },
                    {
                        "12:09": -0.05768057051531387
                    },
                    {
                        "12:10": -0.06568825640277653
                    },
                    {
                        "12:11": -0.04689381093976522
                    },
                    {
                        "12:12": -0.03846537381205925
                    },
                    {
                        "12:13": -0.04693639734115237
                    },
                    {
                        "12:14": -0.04949147262613577
                    },
                    {
                        "12:15": -0.04144269549854074
                    },
                    {
                        "12:16": -0.054361240139026025
                    },
                    {
                        "12:17": -0.032777982907796155
                    },
                    {
                        "12:18": -0.027546291101935794
                    },
                    {
                        "12:19": -0.028386836143727973
                    },
                    {
                        "12:20": -0.03553587511525813
                    },
                    {
                        "12:21": -0.042553780330909806
                    },
                    {
                        "12:22": -0.03170144895458493
                    },
                    {
                        "12:23": -0.04519857209107503
                    },
                    {
                        "12:24": -0.021862232356325145
                    },
                    {
                        "12:25": -0.03394057485364362
                    },
                    {
                        "12:26": -0.02328471624398548
                    },
                    {
                        "12:27": -0.03301442245359983
                    },
                    {
                        "12:28": -0.03544971526593458
                    },
                    {
                        "12:29": -0.04033482432257226
                    },
                    {
                        "12:30": -0.04079152080902367
                    },
                    {
                        "12:31": -0.026586292248850524
                    },
                    {
                        "12:32": -0.02426246521856205
                    },
                    {
                        "12:33": -0.013721913053885038
                    },
                    {
                        "12:34": -0.012288745582621413
                    },
                    {
                        "12:35": -0.015446045804399816
                    },
                    {
                        "12:36": -0.01921370575651497
                    },
                    {
                        "12:37": -0.01919486793593414
                    },
                    {
                        "12:38": -0.012065794185515927
                    },
                    {
                        "12:39": -0.011067123755280017
                    },
                    {
                        "12:40": -0.008713612513021773
                    },
                    {
                        "12:41": -0.010789078373493466
                    },
                    {
                        "12:42": -0.014337758808067674
                    },
                    {
                        "12:43": -0.014369967868819333
                    },
                    {
                        "12:44": -0.020452369489708994
                    },
                    {
                        "12:45": -0.010945556453141029
                    },
                    {
                        "12:46": -0.02122867611126067
                    },
                    {
                        "12:47": -0.01611384126699178
                    },
                    {
                        "12:48": -0.02114522870977072
                    },
                    {
                        "12:49": -0.014827931613958492
                    },
                    {
                        "12:50": -0.0139924665150745
                    },
                    {
                        "12:51": -0.019695670067971682
                    },
                    {
                        "12:52": -0.03198256066181974
                    },
                    {
                        "12:53": -0.028503026291095107
                    },
                    {
                        "12:54": -0.03682972420665681
                    },
                    {
                        "12:55": -0.03716667873647159
                    },
                    {
                        "12:56": -0.04659417218817741
                    },
                    {
                        "12:57": -0.04767108874145598
                    },
                    {
                        "12:58": -0.05164688621131891
                    },
                    {
                        "12:59": -0.05427953804266524
                    },
                    {
                        "13:00": -0.03865546792763827
                    },
                    {
                        "13:01": -0.0367306881987454
                    },
                    {
                        "13:02": -0.03885664862655819
                    },
                    {
                        "13:03": -0.03722193974345375
                    },
                    {
                        "13:04": -0.033176475168161246
                    },
                    {
                        "13:05": -0.03256178380157374
                    },
                    {
                        "13:06": -0.03198172540865074
                    },
                    {
                        "13:07": -0.030104680589611688
                    },
                    {
                        "13:08": -0.03296907596973231
                    },
                    {
                        "13:09": -0.03535391005581351
                    },
                    {
                        "13:10": -0.042901625876392534
                    },
                    {
                        "13:11": -0.04168600838743782
                    },
                    {
                        "13:12": -0.02531396707629202
                    },
                    {
                        "13:13": -0.031429953425285984
                    },
                    {
                        "13:14": -0.02857513572580664
                    },
                    {
                        "13:15": 0.009821984401732042
                    },
                    {
                        "13:16": -0.00011053147006143127
                    },
                    {
                        "13:17": -0.006843045480385085
                    },
                    {
                        "13:18": -0.004660922204497181
                    },
                    {
                        "13:19": -0.0013742097677701681
                    },
                    {
                        "13:20": 0.004844455913592394
                    },
                    {
                        "13:21": -0.0054392108523526606
                    },
                    {
                        "13:22": -0.0020826894687381303
                    },
                    {
                        "13:23": -0.005453633419283899
                    },
                    {
                        "13:24": -0.01394960680768731
                    },
                    {
                        "13:25": -0.0035589701203761295
                    },
                    {
                        "13:26": -0.00724286045537507
                    },
                    {
                        "13:27": -0.004152891222611199
                    },
                    {
                        "13:28": -0.015649621268786922
                    },
                    {
                        "13:29": -0.0337869256699479
                    },
                    {
                        "13:30": -0.06006749273431741
                    },
                    {
                        "13:31": -0.052742875075138806
                    },
                    {
                        "13:32": -0.05524426639640506
                    },
                    {
                        "13:33": -0.04621757769894433
                    },
                    {
                        "13:34": -0.06350518993113072
                    },
                    {
                        "13:35": 0.027359897047397053
                    },
                    {
                        "13:36": 0.027438811188811196
                    },
                    {
                        "13:37": 0.041707337801087783
                    },
                    {
                        "13:38": 0.04181041181041182
                    },
                    {
                        "13:39": -0.06934859866164564
                    },
                    {
                        "13:40": -0.0496175977671201
                    },
                    {
                        "13:41": -0.049446710472408756
                    },
                    {
                        "13:42": 0.010062281468531498
                    },
                    {
                        "13:43": 0.017668026418026377
                    },
                    {
                        "13:44": 0.015583964646464684
                    },
                    {
                        "13:45": 0.004979603729603747
                    },
                    {
                        "13:46": -0.07686581164848377
                    },
                    {
                        "13:47": -0.06990428538424823
                    },
                    {
                        "13:48": -0.08042930367595258
                    },
                    {
                        "13:49": -0.08291322932221418
                    },
                    {
                        "13:50": -0.08239893174576296
                    },
                    {
                        "13:51": -0.09234279631541151
                    },
                    {
                        "13:52": -0.08918396983704738
                    },
                    {
                        "13:53": -0.0891294575064667
                    },
                    {
                        "13:54": -0.08650235943437151
                    },
                    {
                        "13:55": -0.08021695793145989
                    },
                    {
                        "13:56": -0.0817954820850095
                    },
                    {
                        "13:57": -0.07763447080195185
                    },
                    {
                        "13:58": -0.07508380163326556
                    },
                    {
                        "13:59": -0.07496048456356946
                    },
                    {
                        "14:00": -0.06799348991270299
                    },
                    {
                        "14:01": -0.07130444438267877
                    },
                    {
                        "14:02": -0.06927451228638143
                    },
                    {
                        "14:03": -0.07688420641372434
                    },
                    {
                        "14:04": -0.07237362542346312
                    },
                    {
                        "14:05": -0.08416196008022514
                    },
                    {
                        "14:06": -0.08676662445634878
                    },
                    {
                        "14:07": -0.07668498939557133
                    },
                    {
                        "14:08": -0.07411935016255136
                    },
                    {
                        "14:09": -0.07299376020833503
                    },
                    {
                        "14:10": -0.06926012313241015
                    },
                    {
                        "14:11": -0.05570850158811433
                    },
                    {
                        "14:12": -0.011290792540792535
                    },
                    {
                        "14:13": -0.008640977078477033
                    },
                    {
                        "14:14": -0.0006920163170162456
                    },
                    {
                        "14:15": -0.011306575369075348
                    },
                    {
                        "14:16": -0.06791994315121866
                    },
                    {
                        "14:17": -0.07818557873354762
                    },
                    {
                        "14:18": -0.07436991941960217
                    },
                    {
                        "14:19": -0.06955555301976321
                    },
                    {
                        "14:20": -0.07141076321456646
                    },
                    {
                        "14:21": -0.07896153544408724
                    },
                    {
                        "14:22": -0.08738616112713618
                    },
                    {
                        "14:23": -0.08552316165820761
                    },
                    {
                        "14:24": -0.08326147039463846
                    },
                    {
                        "14:25": -0.08362731850753297
                    },
                    {
                        "14:26": -0.07474090878066411
                    },
                    {
                        "14:27": -0.07869049947402842
                    },
                    {
                        "14:28": -0.07587780036474606
                    },
                    {
                        "14:29": -0.060068880124397206
                    },
                    {
                        "14:30": -0.05632605422096379
                    },
                    {
                        "14:31": -0.061613928950158214
                    },
                    {
                        "14:32": -0.06808799946042873
                    },
                    {
                        "14:33": -0.06628059036815967
                    },
                    {
                        "14:34": -0.06112384333869167
                    },
                    {
                        "14:35": -0.06667122562324393
                    },
                    {
                        "14:36": -0.05951812323712846
                    },
                    {
                        "14:37": -0.06643570011158623
                    },
                    {
                        "14:38": -0.06124561449586974
                    },
                    {
                        "14:39": -0.05580196469650048
                    },
                    {
                        "14:40": -0.05020241827892058
                    },
                    {
                        "14:41": -0.056558430265766874
                    },
                    {
                        "14:42": -0.0701772731862653
                    },
                    {
                        "14:43": -0.06608004184652375
                    },
                    {
                        "14:44": -0.06338099525061669
                    },
                    {
                        "14:45": -0.07125810153782913
                    },
                    {
                        "14:46": -0.0686885060437423
                    },
                    {
                        "14:47": -0.07531835066795323
                    },
                    {
                        "14:48": -0.07274039226526102
                    },
                    {
                        "14:49": -0.07409552802251715
                    },
                    {
                        "14:50": -0.06856599433603155
                    },
                    {
                        "14:51": -0.06661757411625235
                    },
                    {
                        "14:52": -0.06097548503616185
                    },
                    {
                        "14:53": -0.06432149336466725
                    },
                    {
                        "14:54": -0.06979571918867791
                    },
                    {
                        "14:55": -0.06685588933382838
                    },
                    {
                        "14:56": -0.0650673965796213
                    },
                    {
                        "14:57": -0.06684247357562703
                    },
                    {
                        "14:58": -0.05749191259319253
                    },
                    {
                        "14:59": -0.054556755537830515
                    },
                    {
                        "15:00": -0.053475583634568474
                    },
                    {
                        "15:01": -0.056490007221483285
                    },
                    {
                        "15:02": -0.053174628573002314
                    },
                    {
                        "15:03": -0.053713409685049535
                    },
                    {
                        "15:04": -0.07059763787967191
                    },
                    {
                        "15:05": 0.008551136363636283
                    },
                    {
                        "15:06": 0.013232930264180376
                    },
                    {
                        "15:07": 0.022739291958041957
                    },
                    {
                        "15:08": 0.03079836829836835
                    },
                    {
                        "15:09": -0.05006257492628918
                    },
                    {
                        "15:10": -0.049789840152433124
                    },
                    {
                        "15:11": -0.05682932917554051
                    },
                    {
                        "15:12": -0.043333936398587874
                    },
                    {
                        "15:13": -0.04347757918982034
                    },
                    {
                        "15:14": -0.04481437128726001
                    },
                    {
                        "15:15": -0.04635322126944433
                    },
                    {
                        "15:16": -0.046372379534846714
                    },
                    {
                        "15:17": -0.0482693788793373
                    },
                    {
                        "15:18": -0.0539423814286161
                    },
                    {
                        "15:19": -0.04918998200239086
                    },
                    {
                        "15:20": -0.06074930422249378
                    },
                    {
                        "15:21": -0.06953483864200757
                    },
                    {
                        "15:22": -0.06856772788301738
                    },
                    {
                        "15:23": 0.05094624125874122
                    },
                    {
                        "15:24": 0.04238296425796432
                    },
                    {
                        "15:25": 0.04829181235431231
                    },
                    {
                        "15:26": 0.051262383449883465
                    },
                    {
                        "15:27": -0.05263199925439202
                    },
                    {
                        "15:28": -0.06630866137703212
                    },
                    {
                        "15:29": -0.06728130852155428
                    },
                    {
                        "15:30": 0.056201680264180265
                    },
                    {
                        "15:31": 0.05262359168609169
                    },
                    {
                        "15:32": 0.059274354118104146
                    },
                    {
                        "15:33": 0.061329885392385375
                    },
                    {
                        "15:34": -0.08686527594464072
                    },
                    {
                        "15:35": -0.09142976093881319
                    },
                    {
                        "15:36": 0.04906189296814297
                    },
                    {
                        "15:37": 0.04397581585081589
                    },
                    {
                        "15:38": 0.04198669386169396
                    },
                    {
                        "15:39": 0.0419597416472417
                    },
                    {
                        "15:40": -0.0946278286267894
                    },
                    {
                        "15:41": -0.12027870327115509
                    },
                    {
                        "15:42": 0.03187208624708626
                    },
                    {
                        "15:43": 0.026683420745920783
                    },
                    {
                        "15:44": 0.0343141754079254
                    },
                    {
                        "15:45": 0.031827651515151545
                    },
                    {
                        "15:46": -0.10209325288553336
                    },
                    {
                        "15:47": -0.09215569138902713
                    },
                    {
                        "15:48": -0.09500261009532088
                    },
                    {
                        "15:49": 0.04578331390831384
                    },
                    {
                        "15:50": 0.0538028117715618
                    },
                    {
                        "15:51": 0.046974553224553205
                    },
                    {
                        "15:52": 0.04504613442113444
                    },
                    {
                        "15:53": -0.08325121775407107
                    },
                    {
                        "15:54": -0.08385641126789392
                    },
                    {
                        "15:55": -0.08385903390051219
                    },
                    {
                        "15:56": -0.08264026441457706
                    },
                    {
                        "15:57": -0.08518469372784931
                    },
                    {
                        "15:58": -0.08185089885197458
                    },
                    {
                        "15:59": -0.07320881712107788
                    }
                ],
                "avg_volume": 1365054725,
                "expected_return": 0.37729870429039036,
                "median_high_spike": 0.3731766581954009,
                "median_high_time": "12:00:00",
                "median_low_spike": -0.15038833873125118,
                "median_low_time": "13:47:00",
                "median_return": 0.1800154527761102,
                "median_return_series": [
                    {
                        "09:30": -0.019836639439906656
                    },
                    {
                        "09:31": -0.03846153846153855
                    },
                    {
                        "09:32": -0.024038461538461675
                    },
                    {
                        "09:33": -0.02183493589743596
                    },
                    {
                        "09:34": -0.05663461538461545
                    },
                    {
                        "09:35": -0.0674038461538462
                    },
                    {
                        "09:36": -0.04200700116686107
                    },
                    {
                        "09:37": -0.0674038461538462
                    },
                    {
                        "09:38": -0.041538461538461524
                    },
                    {
                        "09:39": -0.05346153846153845
                    },
                    {
                        "09:40": -0.05769230769230771
                    },
                    {
                        "09:41": -0.05769230769230771
                    },
                    {
                        "09:42": -0.0673076923076924
                    },
                    {
                        "09:43": -0.07913461538461541
                    },
                    {
                        "09:44": -0.10173076923076918
                    },
                    {
                        "09:45": -0.09932692307692315
                    },
                    {
                        "09:46": -0.10096153846153844
                    },
                    {
                        "09:47": -0.11038461538461541
                    },
                    {
                        "09:48": -0.09230769230769242
                    },
                    {
                        "09:49": -0.0871153846153846
                    },
                    {
                        "09:50": -0.07048076923076929
                    },
                    {
                        "09:51": -0.06298076923076923
                    },
                    {
                        "09:52": -0.06490384615384615
                    },
                    {
                        "09:53": -0.05769230769230771
                    },
                    {
                        "09:54": -0.04807692307692313
                    },
                    {
                        "09:55": -0.033653846153846256
                    },
                    {
                        "09:56": -0.028846153846153855
                    },
                    {
                        "09:57": -0.03846153846153855
                    },
                    {
                        "09:58": -0.05576923076923079
                    },
                    {
                        "09:59": -0.039423076923077005
                    },
                    {
                        "10:00": -0.024038461538461675
                    },
                    {
                        "10:01": -0.04875000000000007
                    },
                    {
                        "10:02": -0.033653846153846256
                    },
                    {
                        "10:03": -0.019230769230769273
                    },
                    {
                        "10:04": -0.02083333333333337
                    },
                    {
                        "10:05": -0.024038461538461675
                    },
                    {
                        "10:06": -0.03846153846153855
                    },
                    {
                        "10:07": -0.039423076923077005
                    },
                    {
                        "10:08": -0.03846153846153855
                    },
                    {
                        "10:09": -0.03846153846153855
                    },
                    {
                        "10:10": -0.03846153846153855
                    },
                    {
                        "10:11": -0.024639423076923128
                    },
                    {
                        "10:12": -0.028846153846153855
                    },
                    {
                        "10:13": -0.005208333333333315
                    },
                    {
                        "10:14": -0.015625
                    },
                    {
                        "10:15": -0.02083333333333337
                    },
                    {
                        "10:16": -0.015224358974358976
                    },
                    {
                        "10:17": -0.02360139860139865
                    },
                    {
                        "10:18": -0.02083333333333337
                    },
                    {
                        "10:19": -0.015625
                    },
                    {
                        "10:20": -0.02083333333333337
                    },
                    {
                        "10:21": -0.024402680652680697
                    },
                    {
                        "10:22": -0.02063301282051283
                    },
                    {
                        "10:23": -0.015625
                    },
                    {
                        "10:24": -0.01302083333333326
                    },
                    {
                        "10:25": -0.015625
                    },
                    {
                        "10:26": -0.015625
                    },
                    {
                        "10:27": -0.02604166666666663
                    },
                    {
                        "10:28": -0.02083333333333337
                    },
                    {
                        "10:29": -0.0234375
                    },
                    {
                        "10:30": -0.02083333333333337
                    },
                    {
                        "10:31": -0.033216783216783285
                    },
                    {
                        "10:32": -0.047567016317016264
                    },
                    {
                        "10:33": -0.03865384615384615
                    },
                    {
                        "10:34": -0.028846153846153855
                    },
                    {
                        "10:35": -0.03430944055944063
                    },
                    {
                        "10:36": -0.03990384615384612
                    },
                    {
                        "10:37": -0.02950174825174834
                    },
                    {
                        "10:38": -0.02083333333333337
                    },
                    {
                        "10:39": -0.03846153846153855
                    },
                    {
                        "10:40": -0.030949519230769273
                    },
                    {
                        "10:41": -0.02083333333333337
                    },
                    {
                        "10:42": -0.023510343822843782
                    },
                    {
                        "10:43": -0.024038461538461675
                    },
                    {
                        "10:44": -0.015625
                    },
                    {
                        "10:45": -0.01041666666666663
                    },
                    {
                        "10:46": -0.019230769230769273
                    },
                    {
                        "10:47": -0.004807692307692402
                    },
                    {
                        "10:48": -0.0078125
                    },
                    {
                        "10:49": -0.00520833333333337
                    },
                    {
                        "10:50": -0.00520833333333337
                    },
                    {
                        "10:51": -0.00520833333333337
                    },
                    {
                        "10:52": -0.00520833333333337
                    },
                    {
                        "10:53": 0
                    },
                    {
                        "10:54": -0.010489510489510467
                    },
                    {
                        "10:55": -0.01041666666666663
                    },
                    {
                        "10:56": -0.020086684149184186
                    },
                    {
                        "10:57": -0.00520833333333337
                    },
                    {
                        "10:58": -0.024038461538461675
                    },
                    {
                        "10:59": -0.028846153846153855
                    },
                    {
                        "11:00": -0.026114510489510412
                    },
                    {
                        "11:01": -0.05208333333333326
                    },
                    {
                        "11:02": -0.028718677156177097
                    },
                    {
                        "11:03": -0.01041666666666663
                    },
                    {
                        "11:04": 0.03125
                    },
                    {
                        "11:05": 0.02083333333333326
                    },
                    {
                        "11:06": 0.004042832167832244
                    },
                    {
                        "11:07": 0
                    },
                    {
                        "11:08": -0.00520833333333337
                    },
                    {
                        "11:09": -0.02083333333333337
                    },
                    {
                        "11:10": -0.00520833333333337
                    },
                    {
                        "11:11": -0.00520833333333337
                    },
                    {
                        "11:12": 0.005208333333333259
                    },
                    {
                        "11:13": 0.0026041666666667407
                    },
                    {
                        "11:14": 0
                    },
                    {
                        "11:15": 0.005208333333333259
                    },
                    {
                        "11:16": 0
                    },
                    {
                        "11:17": -0.00520833333333337
                    },
                    {
                        "11:18": -0.0078125
                    },
                    {
                        "11:19": -0.01041666666666663
                    },
                    {
                        "11:20": -0.003769667832167811
                    },
                    {
                        "11:21": -0.004042832167832133
                    },
                    {
                        "11:22": -0.015625
                    },
                    {
                        "11:23": -0.015625
                    },
                    {
                        "11:24": -0.0078125
                    },
                    {
                        "11:25": 0
                    },
                    {
                        "11:26": -0.0013020833333333148
                    },
                    {
                        "11:27": -0.00520833333333337
                    },
                    {
                        "11:28": 0.015625
                    },
                    {
                        "11:29": 0.009615384615384581
                    },
                    {
                        "11:30": 0.010780885780885763
                    },
                    {
                        "11:31": 0.019230769230769162
                    },
                    {
                        "11:32": 0.009615384615384581
                    },
                    {
                        "11:33": 0
                    },
                    {
                        "11:34": 0
                    },
                    {
                        "11:35": -0.009615384615384581
                    },
                    {
                        "11:36": -0.004807692307692291
                    },
                    {
                        "11:37": -0.009615384615384581
                    },
                    {
                        "11:38": -0.028846153846153855
                    },
                    {
                        "11:39": -0.014423076923077094
                    },
                    {
                        "11:40": -0.019230769230769273
                    },
                    {
                        "11:41": -0.024038461538461675
                    },
                    {
                        "11:42": 0
                    },
                    {
                        "11:43": 0.028846153846153966
                    },
                    {
                        "11:44": 0.019230769230769162
                    },
                    {
                        "11:45": 0.019230769230769162
                    },
                    {
                        "11:46": 0.03125
                    },
                    {
                        "11:47": -0.019230769230769273
                    },
                    {
                        "11:48": -0.014423076923077094
                    },
                    {
                        "11:49": -0.009615384615384581
                    },
                    {
                        "11:50": -0.019230769230769273
                    },
                    {
                        "11:51": -0.003642191142191109
                    },
                    {
                        "11:52": -0.019230769230769273
                    },
                    {
                        "11:53": -0.03846153846153855
                    },
                    {
                        "11:54": -0.009688228438228585
                    },
                    {
                        "11:55": -0.009615384615384581
                    },
                    {
                        "11:56": 0
                    },
                    {
                        "11:57": -0.009615384615384581
                    },
                    {
                        "11:58": -0.003642191142191109
                    },
                    {
                        "11:59": -0.024038461538461675
                    },
                    {
                        "12:00": 0.006847319347319303
                    },
                    {
                        "12:01": 0.009326923076923066
                    },
                    {
                        "12:02": 0.018942307692307647
                    },
                    {
                        "12:03": -0.009615384615384581
                    },
                    {
                        "12:04": -0.0049038461538461475
                    },
                    {
                        "12:05": -0.006046037296037365
                    },
                    {
                        "12:06": -0.008449883449883455
                    },
                    {
                        "12:07": -0.007211538461538547
                    },
                    {
                        "12:08": -0.028653846153846252
                    },
                    {
                        "12:09": -0.009711538461538494
                    },
                    {
                        "12:10": -0.03846153846153855
                    },
                    {
                        "12:11": -0.017992424242424254
                    },
                    {
                        "12:12": -0.006130536130536213
                    },
                    {
                        "12:13": -0.019230769230769273
                    },
                    {
                        "12:14": -0.024038461538461675
                    },
                    {
                        "12:15": -0.013209498834498845
                    },
                    {
                        "12:16": -0.019230769230769273
                    },
                    {
                        "12:17": -0.010828962703962663
                    },
                    {
                        "12:18": -0.009615384615384637
                    },
                    {
                        "12:19": -0.012150349650349723
                    },
                    {
                        "12:20": -0.010780885780885763
                    },
                    {
                        "12:21": -0.019230769230769273
                    },
                    {
                        "12:22": -0.012674825174825266
                    },
                    {
                        "12:23": -0.028846153846153855
                    },
                    {
                        "12:24": -0.002717074592074653
                    },
                    {
                        "12:25": -0.009615384615384581
                    },
                    {
                        "12:26": -0.003642191142191109
                    },
                    {
                        "12:27": -0.009711538461538494
                    },
                    {
                        "12:28": -0.009615384615384581
                    },
                    {
                        "12:29": -0.010000000000000009
                    },
                    {
                        "12:30": 0
                    },
                    {
                        "12:31": 0.009711538461538494
                    },
                    {
                        "12:32": 0.009423076923076978
                    },
                    {
                        "12:33": 0.027788461538461373
                    },
                    {
                        "12:34": 0.011946386946386833
                    },
                    {
                        "12:35": 0.0022829254079253514
                    },
                    {
                        "12:36": 0
                    },
                    {
                        "12:37": -0.003642191142191109
                    },
                    {
                        "12:38": 0.004807692307692291
                    },
                    {
                        "12:39": 0.005925116550116627
                    },
                    {
                        "12:40": 0.0010693473193473246
                    },
                    {
                        "12:41": -0.001165501165501126
                    },
                    {
                        "12:42": -0.007138694638694654
                    },
                    {
                        "12:43": -0.0011771561771562467
                    },
                    {
                        "12:44": -0.007138694638694654
                    },
                    {
                        "12:45": -0.004807692307692402
                    },
                    {
                        "12:46": -0.009615384615384581
                    },
                    {
                        "12:47": -0.019230769230769273
                    },
                    {
                        "12:48": -0.028846153846153855
                    },
                    {
                        "12:49": -0.028846153846153855
                    },
                    {
                        "12:50": -0.019326923076923075
                    },
                    {
                        "12:51": -0.01787150349650357
                    },
                    {
                        "12:52": -0.03846153846153855
                    },
                    {
                        "12:53": -0.0203962703962704
                    },
                    {
                        "12:54": -0.027498543123543107
                    },
                    {
                        "12:55": -0.026729312354312362
                    },
                    {
                        "12:56": -0.032797202797202774
                    },
                    {
                        "12:57": -0.03422785547785551
                    },
                    {
                        "12:58": -0.031091200466200564
                    },
                    {
                        "12:59": -0.03980769230769232
                    },
                    {
                        "13:00": -0.03140297202797199
                    },
                    {
                        "13:01": -0.020192307692307843
                    },
                    {
                        "13:02": -0.024912587412587395
                    },
                    {
                        "13:03": -0.02972027972027974
                    },
                    {
                        "13:04": -0.025104895104895053
                    },
                    {
                        "13:05": -0.033653846153846256
                    },
                    {
                        "13:06": -0.028942307692307656
                    },
                    {
                        "13:07": -0.0214889277389278
                    },
                    {
                        "13:08": -0.027462121212121215
                    },
                    {
                        "13:09": -0.033085664335664344
                    },
                    {
                        "13:10": -0.03846153846153855
                    },
                    {
                        "13:11": -0.04173076923076924
                    },
                    {
                        "13:12": -0.02373543123543126
                    },
                    {
                        "13:13": -0.039423076923077005
                    },
                    {
                        "13:14": -0.02742569930069927
                    },
                    {
                        "13:15": -0.024985431235431343
                    },
                    {
                        "13:16": -0.030731351981352018
                    },
                    {
                        "13:17": -0.030701296620046725
                    },
                    {
                        "13:18": -0.03190850815850821
                    },
                    {
                        "13:19": -0.03220862470862479
                    },
                    {
                        "13:20": -0.04384615384615398
                    },
                    {
                        "13:21": -0.02615093240093247
                    },
                    {
                        "13:22": -0.02141608391608385
                    },
                    {
                        "13:23": -0.02622231934731928
                    },
                    {
                        "13:24": -0.03826923076923083
                    },
                    {
                        "13:25": -0.0000961538461538014
                    },
                    {
                        "13:26": -0.019230769230769273
                    },
                    {
                        "13:27": 0
                    },
                    {
                        "13:28": -0.009615384615384581
                    },
                    {
                        "13:29": -0.019230769230769273
                    },
                    {
                        "13:30": -0.02483828671328675
                    },
                    {
                        "13:31": -0.03142045454545461
                    },
                    {
                        "13:32": -0.031978438228438266
                    },
                    {
                        "13:33": -0.032759324009323965
                    },
                    {
                        "13:34": -0.06908362470862478
                    },
                    {
                        "13:35": -0.04193473193473196
                    },
                    {
                        "13:36": -0.0407925407925408
                    },
                    {
                        "13:37": -0.044289044289044344
                    },
                    {
                        "13:38": -0.04662004662004671
                    },
                    {
                        "13:39": -0.06062689393939397
                    },
                    {
                        "13:40": -0.05090617715617718
                    },
                    {
                        "13:41": -0.06664554195804201
                    },
                    {
                        "13:42": -0.04431235431235436
                    },
                    {
                        "13:43": -0.04895104895104896
                    },
                    {
                        "13:44": -0.04195804195804187
                    },
                    {
                        "13:45": -0.04214452214452202
                    },
                    {
                        "13:46": -0.09033216783216785
                    },
                    {
                        "13:47": -0.08494026806526811
                    },
                    {
                        "13:48": -0.07989849941724936
                    },
                    {
                        "13:49": -0.06859994172494177
                    },
                    {
                        "13:50": -0.07692890442890443
                    },
                    {
                        "13:51": -0.08048878205128202
                    },
                    {
                        "13:52": -0.08221736596736595
                    },
                    {
                        "13:53": -0.0729390005827506
                    },
                    {
                        "13:54": -0.05865384615384617
                    },
                    {
                        "13:55": -0.05818618881118881
                    },
                    {
                        "13:56": -0.047752039627039666
                    },
                    {
                        "13:57": -0.042121212121212115
                    },
                    {
                        "13:58": -0.0393327505827506
                    },
                    {
                        "13:59": -0.04512529137529142
                    },
                    {
                        "14:00": -0.03962703962703967
                    },
                    {
                        "14:01": -0.03621357808857806
                    },
                    {
                        "14:02": -0.04364219114219109
                    },
                    {
                        "14:03": -0.045834790209790255
                    },
                    {
                        "14:04": -0.054184149184149155
                    },
                    {
                        "14:05": -0.05832750582750579
                    },
                    {
                        "14:06": -0.05760984848484846
                    },
                    {
                        "14:07": -0.05724067599067595
                    },
                    {
                        "14:08": -0.06201194638694646
                    },
                    {
                        "14:09": -0.06666375291375298
                    },
                    {
                        "14:10": -0.0641343677156177
                    },
                    {
                        "14:11": -0.06526369463869458
                    },
                    {
                        "14:12": -0.044289044289044344
                    },
                    {
                        "14:13": -0.04585081585081585
                    },
                    {
                        "14:14": -0.04895104895104896
                    },
                    {
                        "14:15": -0.04585081585081585
                    },
                    {
                        "14:16": -0.06651952214452217
                    },
                    {
                        "14:17": -0.0728868006993007
                    },
                    {
                        "14:18": -0.07313519813519814
                    },
                    {
                        "14:19": -0.06235504079254078
                    },
                    {
                        "14:20": -0.06773310023310031
                    },
                    {
                        "14:21": -0.07310533216783222
                    },
                    {
                        "14:22": -0.07892191142191146
                    },
                    {
                        "14:23": -0.08533216783216785
                    },
                    {
                        "14:24": -0.08296474358974365
                    },
                    {
                        "14:25": -0.08131774475524478
                    },
                    {
                        "14:26": -0.07619172494172494
                    },
                    {
                        "14:27": -0.07630681818181811
                    },
                    {
                        "14:28": -0.07440850815850814
                    },
                    {
                        "14:29": -0.0592832167832168
                    },
                    {
                        "14:30": -0.06360139860139863
                    },
                    {
                        "14:31": -0.07172057109557117
                    },
                    {
                        "14:32": -0.07347100815850821
                    },
                    {
                        "14:33": -0.07126602564102563
                    },
                    {
                        "14:34": -0.06769085081585086
                    },
                    {
                        "14:35": -0.07440365675990679
                    },
                    {
                        "14:36": -0.06906177156177151
                    },
                    {
                        "14:37": -0.07228292540792541
                    },
                    {
                        "14:38": -0.06991258741258743
                    },
                    {
                        "14:39": -0.0689481351981352
                    },
                    {
                        "14:40": -0.05909673659673659
                    },
                    {
                        "14:41": -0.06697552447552452
                    },
                    {
                        "14:42": -0.06818084207459207
                    },
                    {
                        "14:43": -0.05255827505827504
                    },
                    {
                        "14:44": -0.05981789044289043
                    },
                    {
                        "14:45": -0.06520250582750581
                    },
                    {
                        "14:46": -0.06352564102564096
                    },
                    {
                        "14:47": -0.059294871794871806
                    },
                    {
                        "14:48": -0.05515515734265736
                    },
                    {
                        "14:49": -0.05773892773892775
                    },
                    {
                        "14:50": -0.059187791375291454
                    },
                    {
                        "14:51": -0.05891025641025649
                    },
                    {
                        "14:52": -0.06187281468531469
                    },
                    {
                        "14:53": -0.06421037296037296
                    },
                    {
                        "14:54": -0.064564393939394
                    },
                    {
                        "14:55": -0.06338068181818185
                    },
                    {
                        "14:56": -0.06648747086247092
                    },
                    {
                        "14:57": -0.06220862470862476
                    },
                    {
                        "14:58": -0.06151806526806536
                    },
                    {
                        "14:59": -0.0639918414918415
                    },
                    {
                        "15:00": -0.06555798368298371
                    },
                    {
                        "15:01": -0.06633595571095574
                    },
                    {
                        "15:02": -0.07129079254079257
                    },
                    {
                        "15:03": -0.06024184149184153
                    },
                    {
                        "15:04": -0.05299242424242434
                    },
                    {
                        "15:05": -0.024038461538461675
                    },
                    {
                        "15:06": -0.01586538461538456
                    },
                    {
                        "15:07": 0.007884615384615268
                    },
                    {
                        "15:08": 0.023461538461538423
                    },
                    {
                        "15:09": -0.013840326340326337
                    },
                    {
                        "15:10": -0.020396270396270344
                    },
                    {
                        "15:11": -0.031873543123543124
                    },
                    {
                        "15:12": -0.02323717948717957
                    },
                    {
                        "15:13": -0.018231351981352006
                    },
                    {
                        "15:14": -0.019469696969696915
                    },
                    {
                        "15:15": -0.02313082750582751
                    },
                    {
                        "15:16": -0.017064393939393963
                    },
                    {
                        "15:17": -0.01039918414918417
                    },
                    {
                        "15:18": -0.002185314685314743
                    },
                    {
                        "15:19": 0.006264568764568712
                    },
                    {
                        "15:20": -0.01056235431235436
                    },
                    {
                        "15:21": -0.010724067599067633
                    },
                    {
                        "15:22": -0.023091491841491785
                    },
                    {
                        "15:23": 0.043846153846153646
                    },
                    {
                        "15:24": 0.028846153846153966
                    },
                    {
                        "15:25": 0.043269230769230616
                    },
                    {
                        "15:26": 0.05769230769230771
                    },
                    {
                        "15:27": -0.013597027972027942
                    },
                    {
                        "15:28": -0.017058566433566458
                    },
                    {
                        "15:29": -0.020305944055944047
                    },
                    {
                        "15:30": 0.04807692307692313
                    },
                    {
                        "15:31": 0.03846153846153855
                    },
                    {
                        "15:32": 0.05769230769230771
                    },
                    {
                        "15:33": 0.0657692307692308
                    },
                    {
                        "15:34": -0.030885780885780867
                    },
                    {
                        "15:35": -0.030874125874125802
                    },
                    {
                        "15:36": 0.03846153846153855
                    },
                    {
                        "15:37": 0.047980769230769216
                    },
                    {
                        "15:38": 0.028846153846153966
                    },
                    {
                        "15:39": 0.028846153846153966
                    },
                    {
                        "15:40": -0.03576631701631705
                    },
                    {
                        "15:41": -0.058031759906759905
                    },
                    {
                        "15:42": -0.020769230769230873
                    },
                    {
                        "15:43": -0.028942307692307656
                    },
                    {
                        "15:44": -0.026538461538461622
                    },
                    {
                        "15:45": -0.02913461538461537
                    },
                    {
                        "15:46": -0.06336247086247088
                    },
                    {
                        "15:47": -0.06337412587412589
                    },
                    {
                        "15:48": -0.07037004662004664
                    },
                    {
                        "15:49": -0.024038461538461675
                    },
                    {
                        "15:50": -0.009615384615384581
                    },
                    {
                        "15:51": -0.0019230769230769162
                    },
                    {
                        "15:52": 0
                    },
                    {
                        "15:53": -0.05077214452214457
                    },
                    {
                        "15:54": -0.04557983682983685
                    },
                    {
                        "15:55": -0.05077214452214457
                    },
                    {
                        "15:56": -0.05383158508158514
                    },
                    {
                        "15:57": -0.04421620046620045
                    },
                    {
                        "15:58": -0.0447989510489511
                    },
                    {
                        "15:59": -0.03738927738927744
                    }
                ],
                "median_volume": 1637199000,
                "n_instances": 4,
                "winrate": 0.5
            },
            "day3": {
                "avg_high_spike": 0.3066487945166371,
                "avg_high_time": "11:36:40",
                "avg_low_spike": -0.26740150813917957,
                "avg_low_time": "14:34:00",
                "avg_return": 0.03092701244477632,
                "avg_return_series": [
                    {
                        "09:30": -0.017730819719953328
                    },
                    {
                        "09:31": -0.04950651497471803
                    },
                    {
                        "09:32": -0.1088812111046285
                    },
                    {
                        "09:33": -0.052195765266433325
                    },
                    {
                        "09:34": -0.06444780727343452
                    },
                    {
                        "09:35": -0.05394605698171917
                    },
                    {
                        "09:36": -0.021003500583430534
                    },
                    {
                        "09:37": -0.05805134189031508
                    },
                    {
                        "09:38": -0.043757292882147025
                    },
                    {
                        "09:39": -0.04142357059509916
                    },
                    {
                        "09:40": -0.051363161221314735
                    },
                    {
                        "09:41": -0.053092182030338386
                    },
                    {
                        "09:42": -0.07174068942045903
                    },
                    {
                        "09:43": -0.06678152956048233
                    },
                    {
                        "09:44": -0.07378269642162588
                    },
                    {
                        "09:45": -0.11572588486970053
                    },
                    {
                        "09:46": -0.08047087709062617
                    },
                    {
                        "09:47": -0.07782416861143526
                    },
                    {
                        "09:48": -0.07840759918319717
                    },
                    {
                        "09:49": -0.08132475204200706
                    },
                    {
                        "09:50": -0.09209694671334112
                    },
                    {
                        "09:51": -0.08657562718786466
                    },
                    {
                        "09:52": -0.08801293271100741
                    },
                    {
                        "09:53": -0.08886680766238819
                    },
                    {
                        "09:54": -0.08742950213924544
                    },
                    {
                        "09:55": -0.07234539089848308
                    },
                    {
                        "09:56": -0.08457616199922213
                    },
                    {
                        "09:57": -0.058134399714767304
                    },
                    {
                        "09:58": -0.08356579395176972
                    },
                    {
                        "09:59": -0.08881666909762737
                    },
                    {
                        "10:00": -0.08720159957215096
                    },
                    {
                        "10:01": -0.09070218300272276
                    },
                    {
                        "10:02": -0.08805547452353168
                    },
                    {
                        "10:03": -0.08922233566705562
                    },
                    {
                        "10:04": -0.07634432127576818
                    },
                    {
                        "10:05": -0.05682980545490527
                    },
                    {
                        "10:06": -0.08334548813691173
                    },
                    {
                        "10:07": -0.05740409859976664
                    },
                    {
                        "10:08": -0.06292541812524316
                    },
                    {
                        "10:09": -0.06306064031505249
                    },
                    {
                        "10:10": -0.05012744418173006
                    },
                    {
                        "10:11": -0.06819756417736289
                    },
                    {
                        "10:12": -0.06063423765071957
                    },
                    {
                        "10:13": -0.06646854336833918
                    },
                    {
                        "10:14": -0.04732280855288747
                    },
                    {
                        "10:15": -0.06817629327110075
                    },
                    {
                        "10:16": -0.0536188901854013
                    },
                    {
                        "10:17": -0.0737401546091015
                    },
                    {
                        "10:18": -0.06875972384286272
                    },
                    {
                        "10:19": -0.06965614060676784
                    },
                    {
                        "10:20": -0.07430231427460138
                    },
                    {
                        "10:21": -0.07167687670167255
                    },
                    {
                        "10:22": -0.07490701575262548
                    },
                    {
                        "10:23": -0.07140643232205368
                    },
                    {
                        "10:24": -0.0800226687086737
                    },
                    {
                        "10:25": -0.07665730746791133
                    },
                    {
                        "10:26": -0.0772407380396733
                    },
                    {
                        "10:27": -0.07894848794243481
                    },
                    {
                        "10:28": -0.07926147413457801
                    },
                    {
                        "10:29": -0.0828972797549592
                    },
                    {
                        "10:30": -0.08042833527810195
                    },
                    {
                        "10:31": -0.07970968251653049
                    },
                    {
                        "10:32": -0.08321026594710229
                    },
                    {
                        "10:33": -0.08424190490081684
                    },
                    {
                        "10:34": -0.0883259189031505
                    },
                    {
                        "10:35": -0.0900762106184364
                    },
                    {
                        "10:36": -0.09474365519253208
                    },
                    {
                        "10:37": -0.09766080805134186
                    },
                    {
                        "10:38": -0.09326380785686506
                    },
                    {
                        "10:39": -0.08684607156748353
                    },
                    {
                        "10:40": -0.08581443261376898
                    },
                    {
                        "10:41": -0.08801293271100741
                    },
                    {
                        "10:42": -0.09061709937767404
                    },
                    {
                        "10:43": -0.08554398823415016
                    },
                    {
                        "10:44": -0.08424190490081684
                    },
                    {
                        "10:45": -0.08105430766238819
                    },
                    {
                        "10:46": -0.06695929356281599
                    },
                    {
                        "10:47": -0.0676779463243874
                    },
                    {
                        "10:48": -0.06750018232205368
                    },
                    {
                        "10:49": -0.07436612699338785
                    },
                    {
                        "10:50": -0.07436612699338785
                    },
                    {
                        "10:51": -0.07494955756514976
                    },
                    {
                        "10:52": -0.07494955756514976
                    },
                    {
                        "10:53": -0.07526254375729285
                    },
                    {
                        "10:54": -0.07759626604434072
                    },
                    {
                        "10:55": -0.0903891968105795
                    },
                    {
                        "10:56": -0.08195072442629331
                    },
                    {
                        "10:57": -0.08486787728510309
                    },
                    {
                        "10:58": -0.08747204395176972
                    },
                    {
                        "10:59": -0.08890934947491252
                    },
                    {
                        "11:00": -0.07362573952383873
                    },
                    {
                        "11:01": -0.10947223842862697
                    },
                    {
                        "11:02": -0.1028265995721509
                    },
                    {
                        "11:03": -0.09622350252819917
                    },
                    {
                        "11:04": -0.07830732205367563
                    },
                    {
                        "11:05": -0.08584937767405681
                    },
                    {
                        "11:06": -0.07140546207018905
                    },
                    {
                        "11:07": -0.10793465577596267
                    },
                    {
                        "11:08": -0.12979203131077405
                    },
                    {
                        "11:09": -0.1323536561649164
                    },
                    {
                        "11:10": -0.06833829334616197
                    },
                    {
                        "11:11": -0.10878853072734346
                    },
                    {
                        "11:12": -0.11174822539867757
                    },
                    {
                        "11:13": -0.10838286415791515
                    },
                    {
                        "11:14": -0.11085180863477245
                    },
                    {
                        "11:15": -0.06943423014459527
                    },
                    {
                        "11:16": -0.1143523920653442
                    },
                    {
                        "11:17": -0.12162400330610657
                    },
                    {
                        "11:18": -0.1182586420653442
                    },
                    {
                        "11:19": -0.11489328082458183
                    },
                    {
                        "11:20": -0.10645480844029565
                    },
                    {
                        "11:21": -0.1061418222481525
                    },
                    {
                        "11:22": -0.10582883605600935
                    },
                    {
                        "11:23": -0.10699569719953328
                    },
                    {
                        "11:24": -0.11067404463243874
                    },
                    {
                        "11:25": -0.10443407234539087
                    },
                    {
                        "11:26": -0.10982016968105796
                    },
                    {
                        "11:27": -0.11053882244262936
                    },
                    {
                        "11:28": -0.09662157234539087
                    },
                    {
                        "11:29": -0.09635112796577211
                    },
                    {
                        "11:30": -0.09608068358615324
                    },
                    {
                        "11:31": -0.08441207215091401
                    },
                    {
                        "11:32": -0.0817653636717231
                    },
                    {
                        "11:33": -0.09339143329443794
                    },
                    {
                        "11:34": -0.1050175029171529
                    },
                    {
                        "11:35": -0.1073512252042007
                    },
                    {
                        "11:36": -0.10506004472967717
                    },
                    {
                        "11:37": -0.10595646149358229
                    },
                    {
                        "11:38": -0.09549725301439127
                    },
                    {
                        "11:39": -0.09841440587320105
                    },
                    {
                        "11:40": -0.0990403782574874
                    },
                    {
                        "11:41": -0.10981257292882146
                    },
                    {
                        "11:42": -0.10227051730844028
                    },
                    {
                        "11:43": -0.10110365616491634
                    },
                    {
                        "11:44": -0.11290748978996501
                    },
                    {
                        "11:45": -0.11677119797744073
                    },
                    {
                        "11:46": -0.12614862893815637
                    },
                    {
                        "11:47": -0.11802314274601317
                    },
                    {
                        "11:48": -0.12219224037339554
                    },
                    {
                        "11:49": -0.11173303189420453
                    },
                    {
                        "11:50": -0.11208855989887201
                    },
                    {
                        "11:51": -0.09548205950991834
                    },
                    {
                        "11:52": -0.08282435093348878
                    },
                    {
                        "11:53": -0.06904232302605984
                    },
                    {
                        "11:54": -0.06185579541034614
                    },
                    {
                        "11:55": -0.08214823998444182
                    },
                    {
                        "11:56": -0.09377430960715671
                    },
                    {
                        "11:57": -0.09171103169972777
                    },
                    {
                        "11:58": -0.10621171236872812
                    },
                    {
                        "11:59": -0.09256490665110856
                    },
                    {
                        "12:00": -0.058118257282646524
                    },
                    {
                        "12:01": -0.07994472603072739
                    },
                    {
                        "12:02": -0.08914940684558531
                    },
                    {
                        "12:03": -0.0893773094126799
                    },
                    {
                        "12:04": -0.0910425175029172
                    },
                    {
                        "12:05": -0.08462478121353562
                    },
                    {
                        "12:06": -0.08377090626215472
                    },
                    {
                        "12:07": -0.08923218105795416
                    },
                    {
                        "12:08": 0.008692859628651592
                    },
                    {
                        "12:09": -0.08166508654220156
                    },
                    {
                        "12:10": -0.07930161537339553
                    },
                    {
                        "12:11": -0.07579519763710618
                    },
                    {
                        "12:12": -0.07080021149358229
                    },
                    {
                        "12:13": -0.06078921139634391
                    },
                    {
                        "12:14": -0.03868917842910469
                    },
                    {
                        "12:15": -0.06967589216258263
                    },
                    {
                        "12:16": -0.0719264755931544
                    },
                    {
                        "12:17": -0.03384431786389345
                    },
                    {
                        "12:18": -0.04547719758848695
                    },
                    {
                        "12:19": -0.04462332263710622
                    },
                    {
                        "12:20": -0.0602908644496305
                    },
                    {
                        "12:21": -0.05421528588098007
                    },
                    {
                        "12:22": -0.031187136208861266
                    },
                    {
                        "12:23": -0.053374781213535616
                    },
                    {
                        "12:24": -0.04100739012057564
                    },
                    {
                        "12:25": -0.04610316997277314
                    },
                    {
                        "12:26": -0.042927241345779854
                    },
                    {
                        "12:27": -0.0446658644496305
                    },
                    {
                        "12:28": -0.04836688059120958
                    },
                    {
                        "12:29": -0.05550223648385838
                    },
                    {
                        "12:30": -0.061187281213535505
                    },
                    {
                        "12:31": -0.044735207604045035
                    },
                    {
                        "12:32": -0.041105236289381564
                    },
                    {
                        "12:33": -0.03447710035005824
                    },
                    {
                        "12:34": -0.03652387811162966
                    },
                    {
                        "12:35": -0.033175017016724984
                    },
                    {
                        "12:36": -0.028820558634772453
                    },
                    {
                        "12:37": -0.03474754472967717
                    },
                    {
                        "12:38": -0.028939280678724144
                    },
                    {
                        "12:39": -0.015197470777293201
                    },
                    {
                        "12:40": -0.01849657234539087
                    },
                    {
                        "12:41": -0.020412655581485806
                    },
                    {
                        "12:42": -0.021536822977440695
                    },
                    {
                        "12:43": -0.01574360742628648
                    },
                    {
                        "12:44": -0.015589643595569913
                    },
                    {
                        "12:45": -0.014014488525865343
                    },
                    {
                        "12:46": -0.011067407555255223
                    },
                    {
                        "12:47": -0.007072005909366889
                    },
                    {
                        "12:48": -0.017294766141579154
                    },
                    {
                        "12:49": -0.007818820497860812
                    },
                    {
                        "12:50": -0.011325238234150214
                    },
                    {
                        "12:51": -0.021519836639439793
                    },
                    {
                        "12:52": -0.028743071761960337
                    },
                    {
                        "12:53": -0.01745915303622721
                    },
                    {
                        "12:54": -0.046160905289770515
                    },
                    {
                        "12:55": -0.04760404511863081
                    },
                    {
                        "12:56": -0.06039114157915204
                    },
                    {
                        "12:57": -0.061114322005056454
                    },
                    {
                        "12:58": -0.07220257195643726
                    },
                    {
                        "12:59": -0.0615154609101517
                    },
                    {
                        "13:00": -0.02358776535855389
                    },
                    {
                        "13:01": -0.04499987845196418
                    },
                    {
                        "13:02": -0.05280070984052898
                    },
                    {
                        "13:03": -0.044723599766627764
                    },
                    {
                        "13:04": -0.021358352610425253
                    },
                    {
                        "13:05": -0.016080677188888132
                    },
                    {
                        "13:06": -0.03350143426682228
                    },
                    {
                        "13:07": -0.021427657381249632
                    },
                    {
                        "13:08": -0.0384760307273434
                    },
                    {
                        "13:09": -0.03762215577596267
                    },
                    {
                        "13:10": -0.045121669583819524
                    },
                    {
                        "13:11": -0.04166362796577211
                    },
                    {
                        "13:12": -0.011787984400908816
                    },
                    {
                        "13:13": -0.027433391676390473
                    },
                    {
                        "13:14": -0.029724572150914008
                    },
                    {
                        "13:15": 0.04462940003889543
                    },
                    {
                        "13:16": 0.030510289041229155
                    },
                    {
                        "13:17": 0.015799610790394936
                    },
                    {
                        "13:18": 0.022586663749513847
                    },
                    {
                        "13:19": 0.029460205173084453
                    },
                    {
                        "13:20": 0.023845805441257806
                    },
                    {
                        "13:21": 0.015272510696227148
                    },
                    {
                        "13:22": 0.01725070497860759
                    },
                    {
                        "13:23": 0.015315052508751481
                    },
                    {
                        "13:24": -0.0017897948269155473
                    },
                    {
                        "13:25": -0.005290378257487294
                    },
                    {
                        "13:26": -0.0012489060676779684
                    },
                    {
                        "13:27": -0.006229336833916799
                    },
                    {
                        "13:28": -0.01866673959548809
                    },
                    {
                        "13:29": -0.04106500388953721
                    },
                    {
                        "13:30": -0.06178551846847761
                    },
                    {
                        "13:31": -0.04542949531549597
                    },
                    {
                        "13:32": -0.052340063042914574
                    },
                    {
                        "13:33": -0.03890669460992028
                    },
                    {
                        "13:34": -0.036837135014705126
                    },
                    {
                        "13:35": 0.11428125000000011
                    },
                    {
                        "13:36": 0.11412280701754396
                    },
                    {
                        "13:37": 0.11822779605263167
                    },
                    {
                        "13:38": 0.11853070175438607
                    },
                    {
                        "13:39": -0.04897669348400169
                    },
                    {
                        "13:40": -0.02977197716432271
                    },
                    {
                        "13:41": -0.019305603535043254
                    },
                    {
                        "13:42": 0.08571518640350884
                    },
                    {
                        "13:43": 0.10356359649122804
                    },
                    {
                        "13:44": 0.09184484649122815
                    },
                    {
                        "13:45": 0.08212719298245608
                    },
                    {
                        "13:46": -0.039196128204603276
                    },
                    {
                        "13:47": -0.03851746496004697
                    },
                    {
                        "13:48": -0.05748217721959511
                    },
                    {
                        "13:49": -0.0668352218059735
                    },
                    {
                        "13:50": -0.06166702533999324
                    },
                    {
                        "13:51": -0.07164875091267642
                    },
                    {
                        "13:52": -0.06629336492729287
                    },
                    {
                        "13:53": -0.07284485523415692
                    },
                    {
                        "13:54": -0.07856724847659786
                    },
                    {
                        "13:55": -0.07031427417483815
                    },
                    {
                        "13:56": -0.07854173916900375
                    },
                    {
                        "13:57": -0.07718620562004001
                    },
                    {
                        "13:58": -0.0752056912628712
                    },
                    {
                        "13:59": -0.07161817113281062
                    },
                    {
                        "14:00": -0.0655557496059284
                    },
                    {
                        "14:01": -0.0718074001003091
                    },
                    {
                        "14:02": -0.06502560825196013
                    },
                    {
                        "14:03": -0.07432416946440383
                    },
                    {
                        "14:04": -0.06457715549448295
                    },
                    {
                        "14:05": -0.07858532885354193
                    },
                    {
                        "14:06": -0.08223840730277658
                    },
                    {
                        "14:07": -0.06891076327048655
                    },
                    {
                        "14:08": -0.06230906402894624
                    },
                    {
                        "14:09": -0.058584266054576305
                    },
                    {
                        "14:10": -0.05606426990999469
                    },
                    {
                        "14:11": -0.037347819726777066
                    },
                    {
                        "14:12": 0.04155701754385971
                    },
                    {
                        "14:13": 0.036965460526315885
                    },
                    {
                        "14:14": 0.05019736842105277
                    },
                    {
                        "14:15": 0.035137609649122825
                    },
                    {
                        "14:16": -0.051915330491241675
                    },
                    {
                        "14:17": -0.062498343108354226
                    },
                    {
                        "14:18": -0.05829783064477604
                    },
                    {
                        "14:19": -0.05905667507693776
                    },
                    {
                        "14:20": -0.05795368763946033
                    },
                    {
                        "14:21": -0.06487849248022814
                    },
                    {
                        "14:22": -0.07179501073034585
                    },
                    {
                        "14:23": -0.06537084049827017
                    },
                    {
                        "14:24": -0.06607388585232044
                    },
                    {
                        "14:25": -0.06957196326093336
                    },
                    {
                        "14:26": -0.06114076350078812
                    },
                    {
                        "14:27": -0.06675120823012408
                    },
                    {
                        "14:28": -0.06340683364381387
                    },
                    {
                        "14:29": -0.05285039739810434
                    },
                    {
                        "14:30": -0.04366538550772107
                    },
                    {
                        "14:31": -0.04574169997509333
                    },
                    {
                        "14:32": -0.05410157278893457
                    },
                    {
                        "14:33": -0.05315291041440632
                    },
                    {
                        "14:34": -0.04923964496031985
                    },
                    {
                        "14:35": -0.05201182790333473
                    },
                    {
                        "14:36": -0.04559701836270954
                    },
                    {
                        "14:37": -0.05317301829788398
                    },
                    {
                        "14:38": -0.04689453298259257
                    },
                    {
                        "14:39": -0.03854245928780523
                    },
                    {
                        "14:40": -0.03735452278108723
                    },
                    {
                        "14:41": -0.039541592458392096
                    },
                    {
                        "14:42": -0.059887732689853736
                    },
                    {
                        "14:43": -0.06400646891440968
                    },
                    {
                        "14:44": -0.05557676845994793
                    },
                    {
                        "14:45": -0.06163018413034723
                    },
                    {
                        "14:46": -0.059321966672808014
                    },
                    {
                        "14:47": -0.07054367583437397
                    },
                    {
                        "14:48": -0.07027848830068173
                    },
                    {
                        "14:49": -0.07038913816898329
                    },
                    {
                        "14:50": -0.061699640303110925
                    },
                    {
                        "14:51": -0.0596201033200953
                    },
                    {
                        "14:52": -0.05041175271414633
                    },
                    {
                        "14:53": -0.06443261376896153
                    },
                    {
                        "14:54": -0.06029873137969385
                    },
                    {
                        "14:55": -0.05697511719789553
                    },
                    {
                        "14:56": -0.052808741180303875
                    },
                    {
                        "14:57": -0.0555368465407002
                    },
                    {
                        "14:58": -0.042661383805195574
                    },
                    {
                        "14:59": -0.0366600604243007
                    },
                    {
                        "15:00": -0.034174403092523176
                    },
                    {
                        "15:01": -0.03723639003186685
                    },
                    {
                        "15:02": -0.02907406412277295
                    },
                    {
                        "15:03": -0.03715840630480327
                    },
                    {
                        "15:04": -0.06494225188847262
                    },
                    {
                        "15:05": 0.05001370614035083
                    },
                    {
                        "15:06": 0.05257812500000014
                    },
                    {
                        "15:07": 0.05408854166666677
                    },
                    {
                        "15:08": 0.060416666666666785
                    },
                    {
                        "15:09": -0.06542672444676449
                    },
                    {
                        "15:10": -0.06079771186888849
                    },
                    {
                        "15:11": -0.06305849787099016
                    },
                    {
                        "15:12": -0.06343069330999618
                    },
                    {
                        "15:13": -0.05425446742342047
                    },
                    {
                        "15:14": -0.07015904560482311
                    },
                    {
                        "15:15": -0.05514690125011094
                    },
                    {
                        "15:16": -0.05878691008686628
                    },
                    {
                        "15:17": -0.06575971573966026
                    },
                    {
                        "15:18": -0.0783698075532081
                    },
                    {
                        "15:19": -0.07765775868833887
                    },
                    {
                        "15:20": -0.0822908360884221
                    },
                    {
                        "15:21": -0.09374795031628076
                    },
                    {
                        "15:22": -0.08436264261636195
                    },
                    {
                        "15:23": 0.0910224780701755
                    },
                    {
                        "15:24": 0.08320942982456148
                    },
                    {
                        "15:25": 0.08449835526315796
                    },
                    {
                        "15:26": 0.08189418859649134
                    },
                    {
                        "15:27": -0.07032184000696022
                    },
                    {
                        "15:28": -0.085916363862788
                    },
                    {
                        "15:29": -0.08527637848267104
                    },
                    {
                        "15:30": 0.09490186403508771
                    },
                    {
                        "15:31": 0.0942571271929824
                    },
                    {
                        "15:32": 0.09624314692982472
                    },
                    {
                        "15:33": 0.09405975877192979
                    },
                    {
                        "15:34": -0.10479125084443897
                    },
                    {
                        "15:35": -0.15198539600350058
                    },
                    {
                        "15:36": 0.09098273026315795
                    },
                    {
                        "15:37": 0.07668530701754395
                    },
                    {
                        "15:38": 0.08214364035087729
                    },
                    {
                        "15:39": 0.08264418859649131
                    },
                    {
                        "15:40": -0.11192271805291132
                    },
                    {
                        "15:41": -0.13046446617808613
                    },
                    {
                        "15:42": 0.08900767543859656
                    },
                    {
                        "15:43": 0.08575932017543864
                    },
                    {
                        "15:44": 0.09542077850877195
                    },
                    {
                        "15:45": 0.09357182017543864
                    },
                    {
                        "15:46": -0.10572479520222178
                    },
                    {
                        "15:47": -0.0925458905675312
                    },
                    {
                        "15:48": -0.09161643150320375
                    },
                    {
                        "15:49": 0.10866776315789473
                    },
                    {
                        "15:50": 0.1141433662280702
                    },
                    {
                        "15:51": 0.0987390350877193
                    },
                    {
                        "15:52": 0.09620065789473686
                    },
                    {
                        "15:53": -0.09075001855206855
                    },
                    {
                        "15:54": -0.09501848169870415
                    },
                    {
                        "15:55": -0.09156044008065671
                    },
                    {
                        "15:56": -0.08862385723522141
                    },
                    {
                        "15:57": -0.09796177378247246
                    },
                    {
                        "15:58": -0.093715932857718
                    },
                    {
                        "15:59": -0.08672065895455043
                    }
                ],
                "avg_volume": 1418437700,
                "expected_return": 0.3471393584727527,
                "median_high_spike": 0.24635331639080182,
                "median_high_time": "12:00:00",
                "median_low_spike": -0.16450216651277827,
                "median_low_time": "15:46:00",
                "median_return": -0.054545403877986676,
                "median_return_series": [
                    {
                        "09:30": -0.017730819719953328
                    },
                    {
                        "09:31": -0.04950651497471803
                    },
                    {
                        "09:32": -0.1088812111046285
                    },
                    {
                        "09:33": -0.052195765266433325
                    },
                    {
                        "09:34": -0.06444780727343452
                    },
                    {
                        "09:35": -0.05394605698171917
                    },
                    {
                        "09:36": -0.021003500583430534
                    },
                    {
                        "09:37": -0.05805134189031508
                    },
                    {
                        "09:38": -0.043757292882147025
                    },
                    {
                        "09:39": -0.04142357059509916
                    },
                    {
                        "09:40": -0.051363161221314735
                    },
                    {
                        "09:41": -0.053092182030338386
                    },
                    {
                        "09:42": -0.07174068942045903
                    },
                    {
                        "09:43": -0.06678152956048233
                    },
                    {
                        "09:44": -0.07378269642162588
                    },
                    {
                        "09:45": -0.11572588486970053
                    },
                    {
                        "09:46": -0.08047087709062617
                    },
                    {
                        "09:47": -0.07782416861143526
                    },
                    {
                        "09:48": -0.07840759918319717
                    },
                    {
                        "09:49": -0.08132475204200706
                    },
                    {
                        "09:50": -0.09209694671334112
                    },
                    {
                        "09:51": -0.08657562718786466
                    },
                    {
                        "09:52": -0.08801293271100741
                    },
                    {
                        "09:53": -0.08886680766238819
                    },
                    {
                        "09:54": -0.08742950213924544
                    },
                    {
                        "09:55": -0.07234539089848308
                    },
                    {
                        "09:56": -0.08457616199922213
                    },
                    {
                        "09:57": -0.00520833333333337
                    },
                    {
                        "09:58": -0.08356579395176972
                    },
                    {
                        "09:59": -0.08881666909762737
                    },
                    {
                        "10:00": -0.08720159957215096
                    },
                    {
                        "10:01": -0.09070218300272276
                    },
                    {
                        "10:02": -0.08805547452353168
                    },
                    {
                        "10:03": -0.08922233566705562
                    },
                    {
                        "10:04": -0.07634432127576818
                    },
                    {
                        "10:05": -0.02083333333333337
                    },
                    {
                        "10:06": -0.08334548813691173
                    },
                    {
                        "10:07": -0.05740409859976664
                    },
                    {
                        "10:08": -0.06292541812524316
                    },
                    {
                        "10:09": -0.06306064031505249
                    },
                    {
                        "10:10": -0.01822916666666663
                    },
                    {
                        "10:11": -0.06819756417736289
                    },
                    {
                        "10:12": -0.06063423765071957
                    },
                    {
                        "10:13": -0.06646854336833918
                    },
                    {
                        "10:14": -0.015625
                    },
                    {
                        "10:15": -0.06817629327110075
                    },
                    {
                        "10:16": -0.02083333333333337
                    },
                    {
                        "10:17": -0.0737401546091015
                    },
                    {
                        "10:18": -0.06875972384286272
                    },
                    {
                        "10:19": -0.06965614060676784
                    },
                    {
                        "10:20": -0.07430231427460138
                    },
                    {
                        "10:21": -0.07167687670167255
                    },
                    {
                        "10:22": -0.07490701575262548
                    },
                    {
                        "10:23": -0.07140643232205368
                    },
                    {
                        "10:24": -0.0800226687086737
                    },
                    {
                        "10:25": -0.07665730746791133
                    },
                    {
                        "10:26": -0.0772407380396733
                    },
                    {
                        "10:27": -0.07894848794243481
                    },
                    {
                        "10:28": -0.07926147413457801
                    },
                    {
                        "10:29": -0.0828972797549592
                    },
                    {
                        "10:30": -0.08042833527810195
                    },
                    {
                        "10:31": -0.07970968251653049
                    },
                    {
                        "10:32": -0.08321026594710229
                    },
                    {
                        "10:33": -0.08424190490081684
                    },
                    {
                        "10:34": -0.0883259189031505
                    },
                    {
                        "10:35": -0.0900762106184364
                    },
                    {
                        "10:36": -0.09474365519253208
                    },
                    {
                        "10:37": -0.09766080805134186
                    },
                    {
                        "10:38": -0.09326380785686506
                    },
                    {
                        "10:39": -0.08684607156748353
                    },
                    {
                        "10:40": -0.08581443261376898
                    },
                    {
                        "10:41": -0.08801293271100741
                    },
                    {
                        "10:42": -0.09061709937767404
                    },
                    {
                        "10:43": -0.08554398823415016
                    },
                    {
                        "10:44": -0.08424190490081684
                    },
                    {
                        "10:45": -0.08105430766238819
                    },
                    {
                        "10:46": -0.06695929356281599
                    },
                    {
                        "10:47": -0.0676779463243874
                    },
                    {
                        "10:48": -0.06750018232205368
                    },
                    {
                        "10:49": -0.07436612699338785
                    },
                    {
                        "10:50": -0.07436612699338785
                    },
                    {
                        "10:51": -0.07494955756514976
                    },
                    {
                        "10:52": -0.07494955756514976
                    },
                    {
                        "10:53": -0.07526254375729285
                    },
                    {
                        "10:54": -0.07759626604434072
                    },
                    {
                        "10:55": -0.0903891968105795
                    },
                    {
                        "10:56": -0.08195072442629331
                    },
                    {
                        "10:57": -0.08486787728510309
                    },
                    {
                        "10:58": -0.08747204395176972
                    },
                    {
                        "10:59": -0.08890934947491252
                    },
                    {
                        "11:00": -0.03124999999999989
                    },
                    {
                        "11:01": -0.10947223842862697
                    },
                    {
                        "11:02": -0.1028265995721509
                    },
                    {
                        "11:03": -0.09622350252819917
                    },
                    {
                        "11:04": -0.07830732205367563
                    },
                    {
                        "11:05": -0.08584937767405681
                    },
                    {
                        "11:06": -0.0052631578947368585
                    },
                    {
                        "11:07": -0.10793465577596267
                    },
                    {
                        "11:08": -0.12979203131077405
                    },
                    {
                        "11:09": -0.1323536561649164
                    },
                    {
                        "11:10": -0.00520833333333337
                    },
                    {
                        "11:11": -0.10878853072734346
                    },
                    {
                        "11:12": -0.11174822539867757
                    },
                    {
                        "11:13": -0.10838286415791515
                    },
                    {
                        "11:14": -0.11085180863477245
                    },
                    {
                        "11:15": 0.005208333333333259
                    },
                    {
                        "11:16": -0.1143523920653442
                    },
                    {
                        "11:17": -0.12162400330610657
                    },
                    {
                        "11:18": -0.1182586420653442
                    },
                    {
                        "11:19": -0.11489328082458183
                    },
                    {
                        "11:20": -0.10645480844029565
                    },
                    {
                        "11:21": -0.1061418222481525
                    },
                    {
                        "11:22": -0.10582883605600935
                    },
                    {
                        "11:23": -0.10699569719953328
                    },
                    {
                        "11:24": -0.11067404463243874
                    },
                    {
                        "11:25": -0.10443407234539087
                    },
                    {
                        "11:26": -0.10982016968105796
                    },
                    {
                        "11:27": -0.11053882244262936
                    },
                    {
                        "11:28": -0.09662157234539087
                    },
                    {
                        "11:29": -0.09635112796577211
                    },
                    {
                        "11:30": -0.09608068358615324
                    },
                    {
                        "11:31": -0.08441207215091401
                    },
                    {
                        "11:32": -0.0817653636717231
                    },
                    {
                        "11:33": -0.09339143329443794
                    },
                    {
                        "11:34": -0.1050175029171529
                    },
                    {
                        "11:35": -0.1073512252042007
                    },
                    {
                        "11:36": -0.10506004472967717
                    },
                    {
                        "11:37": -0.10595646149358229
                    },
                    {
                        "11:38": -0.09549725301439127
                    },
                    {
                        "11:39": -0.09841440587320105
                    },
                    {
                        "11:40": -0.0990403782574874
                    },
                    {
                        "11:41": -0.10981257292882146
                    },
                    {
                        "11:42": -0.10227051730844028
                    },
                    {
                        "11:43": -0.10110365616491634
                    },
                    {
                        "11:44": -0.11290748978996501
                    },
                    {
                        "11:45": -0.11677119797744073
                    },
                    {
                        "11:46": -0.12614862893815637
                    },
                    {
                        "11:47": -0.11802314274601317
                    },
                    {
                        "11:48": -0.12219224037339554
                    },
                    {
                        "11:49": -0.11173303189420453
                    },
                    {
                        "11:50": -0.11208855989887201
                    },
                    {
                        "11:51": -0.09548205950991834
                    },
                    {
                        "11:52": -0.08282435093348878
                    },
                    {
                        "11:53": -0.06904232302605984
                    },
                    {
                        "11:54": -0.06185579541034614
                    },
                    {
                        "11:55": -0.08214823998444182
                    },
                    {
                        "11:56": -0.09377430960715671
                    },
                    {
                        "11:57": -0.09171103169972777
                    },
                    {
                        "11:58": -0.10621171236872812
                    },
                    {
                        "11:59": -0.09256490665110856
                    },
                    {
                        "12:00": -0.007894736842105177
                    },
                    {
                        "12:01": -0.07994472603072739
                    },
                    {
                        "12:02": -0.08914940684558531
                    },
                    {
                        "12:03": -0.0893773094126799
                    },
                    {
                        "12:04": -0.0910425175029172
                    },
                    {
                        "12:05": -0.08462478121353562
                    },
                    {
                        "12:06": -0.08377090626215472
                    },
                    {
                        "12:07": -0.08923218105795416
                    },
                    {
                        "12:08": 0.018421052631579116
                    },
                    {
                        "12:09": -0.08166508654220156
                    },
                    {
                        "12:10": -0.07930161537339553
                    },
                    {
                        "12:11": -0.07579519763710618
                    },
                    {
                        "12:12": -0.07080021149358229
                    },
                    {
                        "12:13": -0.06078921139634391
                    },
                    {
                        "12:14": 0.00836842105263158
                    },
                    {
                        "12:15": -0.06967589216258263
                    },
                    {
                        "12:16": -0.0719264755931544
                    },
                    {
                        "12:17": 0.00792105263157894
                    },
                    {
                        "12:18": -0.04547719758848695
                    },
                    {
                        "12:19": -0.04462332263710622
                    },
                    {
                        "12:20": -0.0602908644496305
                    },
                    {
                        "12:21": -0.05421528588098007
                    },
                    {
                        "12:22": 0.007894736842105399
                    },
                    {
                        "12:23": -0.053374781213535616
                    },
                    {
                        "12:24": -0.04100739012057564
                    },
                    {
                        "12:25": -0.04610316997277314
                    },
                    {
                        "12:26": -0.042927241345779854
                    },
                    {
                        "12:27": -0.0446658644496305
                    },
                    {
                        "12:28": -0.04836688059120958
                    },
                    {
                        "12:29": -0.05550223648385838
                    },
                    {
                        "12:30": -0.061187281213535505
                    },
                    {
                        "12:31": -0.044735207604045035
                    },
                    {
                        "12:32": -0.041105236289381564
                    },
                    {
                        "12:33": -0.03447710035005824
                    },
                    {
                        "12:34": -0.03652387811162966
                    },
                    {
                        "12:35": -0.033175017016724984
                    },
                    {
                        "12:36": -0.028820558634772453
                    },
                    {
                        "12:37": -0.03474754472967717
                    },
                    {
                        "12:38": -0.028939280678724144
                    },
                    {
                        "12:39": 0.010526315789473717
                    },
                    {
                        "12:40": -0.01849657234539087
                    },
                    {
                        "12:41": -0.020412655581485806
                    },
                    {
                        "12:42": -0.021536822977440695
                    },
                    {
                        "12:43": 0.007894736842105399
                    },
                    {
                        "12:44": 0.020763157894736928
                    },
                    {
                        "12:45": -0.014014488525865343
                    },
                    {
                        "12:46": 0.020868421052631758
                    },
                    {
                        "12:47": 0.007894736842105399
                    },
                    {
                        "12:48": -0.017294766141579154
                    },
                    {
                        "12:49": -0.007818820497860812
                    },
                    {
                        "12:50": -0.011325238234150214
                    },
                    {
                        "12:51": -0.021519836639439793
                    },
                    {
                        "12:52": -0.028743071761960337
                    },
                    {
                        "12:53": 0.020842105263157995
                    },
                    {
                        "12:54": -0.046160905289770515
                    },
                    {
                        "12:55": -0.04760404511863081
                    },
                    {
                        "12:56": -0.06039114157915204
                    },
                    {
                        "12:57": -0.061114322005056454
                    },
                    {
                        "12:58": -0.07220257195643726
                    },
                    {
                        "12:59": -0.0615154609101517
                    },
                    {
                        "13:00": 0.021052631578947434
                    },
                    {
                        "13:01": -0.04499987845196418
                    },
                    {
                        "13:02": -0.05280070984052898
                    },
                    {
                        "13:03": -0.044723599766627764
                    },
                    {
                        "13:04": 0.018421052631579116
                    },
                    {
                        "13:05": 0.015789473684210575
                    },
                    {
                        "13:06": -0.03350143426682228
                    },
                    {
                        "13:07": 0.013157894736842257
                    },
                    {
                        "13:08": -0.0384760307273434
                    },
                    {
                        "13:09": -0.03762215577596267
                    },
                    {
                        "13:10": -0.045121669583819524
                    },
                    {
                        "13:11": -0.04166362796577211
                    },
                    {
                        "13:12": 0.018421052631579116
                    },
                    {
                        "13:13": -0.027433391676390473
                    },
                    {
                        "13:14": -0.029724572150914008
                    },
                    {
                        "13:15": 0.04462940003889543
                    },
                    {
                        "13:16": 0.030510289041229155
                    },
                    {
                        "13:17": 0.013368421052631696
                    },
                    {
                        "13:18": 0.022586663749513847
                    },
                    {
                        "13:19": 0.029460205173084453
                    },
                    {
                        "13:20": 0.013157894736842257
                    },
                    {
                        "13:21": 0.015272510696227148
                    },
                    {
                        "13:22": 0.01725070497860759
                    },
                    {
                        "13:23": 0.015315052508751481
                    },
                    {
                        "13:24": -0.0017897948269155473
                    },
                    {
                        "13:25": -0.005290378257487294
                    },
                    {
                        "13:26": -0.0012489060676779684
                    },
                    {
                        "13:27": -0.006229336833916799
                    },
                    {
                        "13:28": -0.01866673959548809
                    },
                    {
                        "13:29": -0.04106500388953721
                    },
                    {
                        "13:30": 0.005236842105263317
                    },
                    {
                        "13:31": 0.011842105263158098
                    },
                    {
                        "13:32": 0
                    },
                    {
                        "13:33": 0.0026315789473685403
                    },
                    {
                        "13:34": 0.005342105263157926
                    },
                    {
                        "13:35": 0.11428125000000011
                    },
                    {
                        "13:36": 0.11412280701754396
                    },
                    {
                        "13:37": 0.11822779605263167
                    },
                    {
                        "13:38": 0.11853070175438607
                    },
                    {
                        "13:39": 0.009210526315789558
                    },
                    {
                        "13:40": 0.0073421052631579276
                    },
                    {
                        "13:41": 0.00657894736842124
                    },
                    {
                        "13:42": 0.08571518640350884
                    },
                    {
                        "13:43": 0.10356359649122804
                    },
                    {
                        "13:44": 0.09184484649122815
                    },
                    {
                        "13:45": 0.08212719298245608
                    },
                    {
                        "13:46": 0.009210526315789558
                    },
                    {
                        "13:47": -0.005815789473684219
                    },
                    {
                        "13:48": -0.010526315789473717
                    },
                    {
                        "13:49": -0.0060526315789473095
                    },
                    {
                        "13:50": -0.009263157894736751
                    },
                    {
                        "13:51": -0.0065526315789472545
                    },
                    {
                        "13:52": -0.006578947368421018
                    },
                    {
                        "13:53": -0.007894736842105177
                    },
                    {
                        "13:54": -0.006999999999999895
                    },
                    {
                        "13:55": -0.006447368421052535
                    },
                    {
                        "13:56": -0.003947368421052588
                    },
                    {
                        "13:57": -0.0052631578947368585
                    },
                    {
                        "13:58": -0.003947368421052588
                    },
                    {
                        "13:59": -0.0052631578947368585
                    },
                    {
                        "14:00": -0.003947368421052588
                    },
                    {
                        "14:01": -0.002631578947368318
                    },
                    {
                        "14:02": -0.0052631578947368585
                    },
                    {
                        "14:03": -0.007105263157894615
                    },
                    {
                        "14:04": -0.012605263157894675
                    },
                    {
                        "14:05": -0.015763157894736812
                    },
                    {
                        "14:06": -0.01486842105263153
                    },
                    {
                        "14:07": -0.014473684210526194
                    },
                    {
                        "14:08": -0.014473684210526194
                    },
                    {
                        "14:09": -0.017105263157894735
                    },
                    {
                        "14:10": -0.019421052631578894
                    },
                    {
                        "14:11": -0.019736842105263053
                    },
                    {
                        "14:12": 0.04155701754385971
                    },
                    {
                        "14:13": 0.036965460526315885
                    },
                    {
                        "14:14": 0.05019736842105277
                    },
                    {
                        "14:15": 0.035137609649122825
                    },
                    {
                        "14:16": -0.017105263157894735
                    },
                    {
                        "14:17": -0.020526315789473615
                    },
                    {
                        "14:18": -0.023684210526315752
                    },
                    {
                        "14:19": -0.02365789473684199
                    },
                    {
                        "14:20": -0.023684210526315752
                    },
                    {
                        "14:21": -0.02499999999999991
                    },
                    {
                        "14:22": -0.023684210526315752
                    },
                    {
                        "14:23": -0.024684210526315753
                    },
                    {
                        "14:24": -0.031105263157894747
                    },
                    {
                        "14:25": -0.03684210526315779
                    },
                    {
                        "14:26": -0.03684210526315779
                    },
                    {
                        "14:27": -0.03810526315789475
                    },
                    {
                        "14:28": -0.03552631578947363
                    },
                    {
                        "14:29": -0.03684210526315779
                    },
                    {
                        "14:30": -0.03289473684210531
                    },
                    {
                        "14:31": -0.03421052631578947
                    },
                    {
                        "14:32": -0.0368947368421052
                    },
                    {
                        "14:33": -0.03686842105263155
                    },
                    {
                        "14:34": -0.03860526315789459
                    },
                    {
                        "14:35": -0.03815789473684206
                    },
                    {
                        "14:36": -0.03684210526315779
                    },
                    {
                        "14:37": -0.038342105263157844
                    },
                    {
                        "14:38": -0.03552631578947363
                    },
                    {
                        "14:39": -0.030315789473684185
                    },
                    {
                        "14:40": -0.029447368421052555
                    },
                    {
                        "14:41": -0.026342105263157833
                    },
                    {
                        "14:42": -0.03531578947368419
                    },
                    {
                        "14:43": -0.03281578947368413
                    },
                    {
                        "14:44": -0.032842105263157895
                    },
                    {
                        "14:45": -0.03026315789473677
                    },
                    {
                        "14:46": -0.03026315789473677
                    },
                    {
                        "14:47": -0.02894736842105261
                    },
                    {
                        "14:48": -0.030184210526315813
                    },
                    {
                        "14:49": -0.03026315789473677
                    },
                    {
                        "14:50": -0.029210526315789465
                    },
                    {
                        "14:51": -0.030210526315789465
                    },
                    {
                        "14:52": -0.031078947368420984
                    },
                    {
                        "14:53": -0.06443261376896153
                    },
                    {
                        "14:54": -0.030842105263157893
                    },
                    {
                        "14:55": -0.03026315789473677
                    },
                    {
                        "14:56": -0.031131578947368288
                    },
                    {
                        "14:57": -0.02365789473684199
                    },
                    {
                        "14:58": -0.021052631578947323
                    },
                    {
                        "14:59": -0.019736842105263053
                    },
                    {
                        "15:00": -0.019736842105263053
                    },
                    {
                        "15:01": -0.018421052631578894
                    },
                    {
                        "15:02": -0.017105263157894735
                    },
                    {
                        "15:03": -0.017105263157894735
                    },
                    {
                        "15:04": -0.018421052631578894
                    },
                    {
                        "15:05": 0.05001370614035083
                    },
                    {
                        "15:06": 0.05257812500000014
                    },
                    {
                        "15:07": 0.05408854166666677
                    },
                    {
                        "15:08": 0.060416666666666785
                    },
                    {
                        "15:09": -0.023710526315789404
                    },
                    {
                        "15:10": -0.024026315789473673
                    },
                    {
                        "15:11": -0.025605263157894687
                    },
                    {
                        "15:12": -0.06343069330999618
                    },
                    {
                        "15:13": -0.02531578947368407
                    },
                    {
                        "15:14": -0.07015904560482311
                    },
                    {
                        "15:15": -0.02628947368421053
                    },
                    {
                        "15:16": -0.02499999999999991
                    },
                    {
                        "15:17": -0.02499999999999991
                    },
                    {
                        "15:18": -0.023710526315789404
                    },
                    {
                        "15:19": -0.023684210526315752
                    },
                    {
                        "15:20": -0.02499999999999991
                    },
                    {
                        "15:21": -0.02455263157894727
                    },
                    {
                        "15:22": -0.02499999999999991
                    },
                    {
                        "15:23": 0.0910224780701755
                    },
                    {
                        "15:24": 0.08320942982456148
                    },
                    {
                        "15:25": 0.08449835526315796
                    },
                    {
                        "15:26": 0.08189418859649134
                    },
                    {
                        "15:27": -0.02763157894736845
                    },
                    {
                        "15:28": -0.02663157894736845
                    },
                    {
                        "15:29": -0.02731578947368407
                    },
                    {
                        "15:30": 0.09490186403508771
                    },
                    {
                        "15:31": 0.0942571271929824
                    },
                    {
                        "15:32": 0.09624314692982472
                    },
                    {
                        "15:33": 0.09405975877192979
                    },
                    {
                        "15:34": -0.028684210526315757
                    },
                    {
                        "15:35": -0.15198539600350058
                    },
                    {
                        "15:36": 0.09098273026315795
                    },
                    {
                        "15:37": 0.07668530701754395
                    },
                    {
                        "15:38": 0.08214364035087729
                    },
                    {
                        "15:39": 0.08264418859649131
                    },
                    {
                        "15:40": -0.028789473684210476
                    },
                    {
                        "15:41": -0.026342105263157833
                    },
                    {
                        "15:42": 0.08900767543859656
                    },
                    {
                        "15:43": 0.08575932017543864
                    },
                    {
                        "15:44": 0.09542077850877195
                    },
                    {
                        "15:45": 0.09357182017543864
                    },
                    {
                        "15:46": -0.03552631578947363
                    },
                    {
                        "15:47": -0.03576315789473683
                    },
                    {
                        "15:48": -0.03557894736842104
                    },
                    {
                        "15:49": 0.10866776315789473
                    },
                    {
                        "15:50": 0.1141433662280702
                    },
                    {
                        "15:51": 0.0987390350877193
                    },
                    {
                        "15:52": 0.09620065789473686
                    },
                    {
                        "15:53": -0.04078947368421049
                    },
                    {
                        "15:54": -0.04078947368421049
                    },
                    {
                        "15:55": -0.04078947368421049
                    },
                    {
                        "15:56": -0.042973684210526275
                    },
                    {
                        "15:57": -0.04157894736842105
                    },
                    {
                        "15:58": -0.04334210526315785
                    },
                    {
                        "15:59": -0.042105263157894646
                    }
                ],
                "median_volume": 2071569300,
                "n_instances": 3,
                "winrate": 0.3333333333333333
            },
            "median_gap": 0.571428501918783,
            "quantity": 5
        },
        "structuredData": {
            "keywords": [
                "\"symbol: BYND\"",
                "\"section: overview\""
            ]
        },
        "symbol": "BYND",
        "tangibleBookValuePerShare": -1.7027,
        "title": "Beyond Meat Stock Price, Quotes and Forecasts | NASDAQ:BYND | Benzinga",
        "totalAssets": 691741000,
        "twoHundredDayAveragePrice": 3.0517,
        "type": "STOCK",
        "volume": 30375943,
        "website": "http://www.beyondmeat.com",
        "zip": "90245"
    }
    
    # Create prompt
    filtered_data = {k: v for k, v in stock_data.items() if k in ['volume', 'avg_volume', 'shares_float', 'market_cap', 'pe', 'eps', 'Perf_Month_Pct', 'Perf_Quarter_Pct', 'Perf_Half_Y_Pct', 'insiders_pct', 'institutional_pct', 'description', 'Quick_Ratio']}
    filtered_data['last_candle'] = stock_data['candles'][-1]
    context: str = llm.getSystemPrompt(trade_type='position')
    
    # Get analysis
    try:
        prompt: str = llm.createStockPrompt(
            symbol="BYND",
            data=filtered_data,
            trade_type="position",
            file_urls=["https://www.sec.gov/Archives/edgar/data/1655210/000119312525242542/d940803ddef14a.htm"]
        )
        analysis: LLMResponse = llm.callGroq(prompt=prompt, context=context, model="llama-3.3-70b-versatile")
        print(analysis.response)
    except requests.exceptions.RequestException as e:
        print(f"Error calling Groq API for stock analysis: {e}")
        
    try:
        sec = SECFiling(cik='1655210', accn='000119312525242542')
        prompt: str = llm.createFilePrompt(file_content=sec.getFilingContent(file='d940803ddef14a.htm', html=False))
        analysis: LLMResponse = llm.callGroq(prompt=prompt, context=context, model="llama-3.3-70b-versatile")
        print(analysis.response)
    except requests.exceptions.RequestException as e:
        print(f"Error calling Groq API for file analysis: {e}")
