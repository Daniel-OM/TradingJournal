
from datetime import date, datetime, timedelta, time

import numpy as np
import pandas as pd

from flask import Blueprint, Response, render_template, request, flash, redirect, url_for, jsonify, abort
from flask_login import login_required

from ..src.yahoofinance import YahooTicker, YahooFinance
from ..src.benzinga import Benzinga
from ..src.finviz import FinvizScraper, FinvizTicker
from ..src.edgar import SECFiling
from .utils import getPrice

def handle_error(e, symbol=None):
    """Maneja errores y retorna una respuesta JSON consistente"""
    error_msg = f"Error processing {symbol if symbol else 'request'}: {str(e)}"
    return jsonify({
        'success': False,
        'error': error_msg,
        'data': None
    }), 500

def clean_data(data):
    """Limpia valores NaN y los convierte a None para JSON"""
    try:
        if isinstance(data, dict):
            return {k: clean_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [clean_data(item) for item in data]
        elif pd.isna(data) or (isinstance(data, float) and np.isnan(data)):
            return None
        elif isinstance(data, (np.int64, np.int32)):
            return int(data)
        elif isinstance(data, (np.float64, np.float32)):
            return float(data)
        else:
            return data
    except Exception as e:
        print(data)
        raise e

asset_pages = Blueprint(name='asset_pages', import_name=__name__)

@asset_pages.route('/')
@login_required
def asset() -> str:
    symbol = request.args.get('symbol', None)
    return render_template(template_name_or_list='asset/asset.html', symbol=symbol)

asset_bp = Blueprint(name='asset_endpoints', import_name=__name__)

def gapStats(data: pd.DataFrame) -> dict[str, float]:

    return {
        'avg_return': data['ret'].mean(),
        'median_return': data['ret'].median(),
        'avg_gain': data[data['ret'] > 0]['ret'].mean(),
        'avg_loss': data[data['ret'] < 0]['ret'].mean(),
        'avg_high_spike': data['high_spike'].mean(),
        'median_high_spike': data['high_spike'].median(),
        'avg_low_spike': data['low_spike'].mean(),
        'median_low_spike': data['low_spike'].median(),
        'winrate': len(data[data['ret'] > 0]) / len(data),
        'avg_volume': data['volume'].mean(),
        'median_volume': data['volume'].median()
    }
            
@asset_bp.route('<string:symbol>')
@login_required
def api_asset(symbol:str) -> str:
    
    """
    Endpoint principal que obtiene información general de una acción
    Combina datos de Benzinga y Finviz
    """
    # try:
    symbol = symbol.upper()
    
    # Obtener datos de Benzinga
    try:
        benzinga = Benzinga(symbol=symbol, random_headers=True)
        benzinga_info = benzinga.info()
        benzinga_key_data = benzinga.keyData()
        share_data = benzinga.shareData()
    except Exception as e:
        print(f'Benzinga failed to found {symbol}: ', e)
        benzinga_info = {}
        benzinga_key_data = {}
        share_data = {}

    # Obtener datos de Edgar# %%
    doc = SECFiling(cik='1861622')
    warrants = doc.getElement('ix:nonfraction', {'name': 'us-gaap:ClassOfWarrantOrRightOutstanding'}, last=False, numeric=True)
    warrants_price = doc.getElement('ix:nonfraction', {'name': 'us-gaap:ClassOfWarrantOrRightExercisePriceOfWarrantsOrRights1'}, last=True, numeric=True)
    
    # Obtener datos de Finviz
    finviz = FinvizTicker(symbol=symbol, random_headers=True)
    finviz_info = finviz.info(df=False)
    finviz_data = finviz_info if isinstance(finviz_info, dict) else {}

    # candles = getPrice(symbol=symbol, start=(datetime.now() - timedelta(days=365)), end=datetime.now(), timeframe='1d')
    yahoo = YahooTicker(ticker=symbol)
    yahoo_info: dict = yahoo.getTicker()

    candles = getPrice(symbol=symbol, start=(datetime.now() - timedelta(days=365)), end=datetime.now(), timeframe='1d', free=True, yahoo=True) # TODO: This should be free=None but as we don't pay this is set this way so it does not give any error 
    yahoo_candles = yahoo.getPrice(start=(datetime.now() - timedelta(days=365)).timestamp(),
                                    end=datetime.now().timestamp(), 
                                    timeframe='1d', df=True)

    candles['gap'] = candles['open'] / candles['close'].shift(1) - 1
    candles['ret'] = candles['close'] / candles['open'] - 1
    candles['high_spike'] = candles['high'] / candles['open'] - 1
    candles['low_spike'] = candles['low'] / candles['open'] - 1
    
    candles['gap'] = candles['gap'].astype(float)
    candles['ret'] = candles['ret'].astype(float)
    candles['high_spike'] = candles['high_spike'].astype(float)
    candles['low_spike'] = candles['low_spike'].astype(float)
    day1 = candles[candles['gap'] > 0.1]
    day2 = candles[candles['gap'].shift(1) > 0.1]
    day3 = candles[candles['gap'].shift(2) > 0.1]

    df = candles.sort_values('date').reset_index(drop=True)
    df['date_plus_3'] = df['date'].shift(-3).ffill()
    
    mapping = df.set_index('date')['date_plus_3'].reindex(day1['date'].tolist()).to_dict()
    print('Mapping: ',mapping)
    windows = [getPrice(symbol=symbol, start=start, end=end, timeframe='1m') for start, end in reversed(list(mapping.items()))]

    def _secondsToTimeStr(sec: float) -> str:
        if np.isnan(sec):
            return None
        sec = int(round(sec))
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def compute_gap_stats(list_of_dfs: list[pd.DataFrame],
                        tz_ny: str = 'America/New_York',
                        session_only: bool = False) -> dict[str, dict]:
        """
        Calcula:
        - serie temporal de retorno medio a lo largo del día (alineado por time-of-day HH:MM)
        - hora media del high máximo del día
        - hora media del low mínimo del día
        para day0 (día del gap), day1 (día siguiente) y day2 (segundo día siguiente).

        Asume que cada DataFrame de entrada contiene al menos 1..3 fechas contiguas (o menos) y
        que tiene columna 'session' con valores como 'PRE','REG','POST' si quieres filtrar por sesión REG.
        """
        # contenedores por día
        returns_lists = {0: [], 1: [], 2: []}
        high_seconds = {0: [], 1: [], 2: []}
        low_seconds = {0: [], 1: [], 2: []}

        for df in list_of_dfs:
            if not isinstance(df.index, pd.DatetimeIndex):
                raise ValueError("Each input must have a DatetimeIndex")

            # Garantizar tz-aware; si no lo es asumimos UTC
            idx = df.index
            if idx.tz is None:
                df = df.tz_localize('UTC')
                idx = df.index

            # Convertir a hora de NY para agrupar por fecha local (pero conservar timestamps originales en df)
            df_ny = df.tz_convert(tz_ny)

            # Obtener fechas locales ordenadas (puede haber menos de 3 días)
            unique_dates = sorted({d.date() for d in df_ny.index})
            # si no hay fechas suficientes, seguir pero solo procesar las disponibles
            for day_offset in range(0, 3):
                if day_offset >= len(unique_dates):
                    continue
                day_date = unique_dates[day_offset]
                mask_day = df_ny.index.date == day_date
                day_df_ny = df_ny.loc[mask_day].copy()
                if day_df_ny.empty:
                    continue

                # filtrar REG si se pide
                if session_only and 'session' in day_df_ny.columns:
                    day_reg = day_df_ny[day_df_ny['session'] == 'REG']
                    if day_reg.empty:
                        # fallback a todo el día si no hay datos REG
                        day_reg = day_df_ny
                else:
                    day_reg = day_df_ny

                # calcular retorno intradía relativo al open del día (primer registro usado como open)
                open_price = None
                if 'open' in day_reg.columns and not day_reg['open'].isna().all():
                    open_price = float(day_reg['open'].iloc[0])
                elif 'close' in day_reg.columns and not day_reg['close'].isna().all():
                    # fallback si falta open
                    open_price = float(day_reg['close'].iloc[0])
                else:
                    # no hay precios válidos; saltar
                    continue

                # return series indexado por time-of-day 'HH:MM'
                times = day_reg.index.time
                time_labels = [t.strftime("%H:%M") for t in times]
                returns = (day_reg['close'].astype(float) / open_price) - 1.0
                series = pd.Series(returns.values, index=time_labels)
                returns_lists[day_offset].append(series)

                # hora del max high y min low (usar day_reg)
                if 'high' in day_reg.columns and not day_reg['high'].isna().all():
                    idx_max = day_reg['high'].idxmax()
                    tmax = idx_max.tz_convert(tz_ny).timetz()  # time with tz info
                    seconds_max = tmax.hour * 3600 + tmax.minute * 60 + tmax.second
                    high_seconds[day_offset].append(seconds_max)
                if 'low' in day_reg.columns and not day_reg['low'].isna().all():
                    idx_min = day_reg['low'].idxmin()
                    tmin = idx_min.tz_convert(tz_ny).timetz()
                    seconds_min = tmin.hour * 3600 + tmin.minute * 60 + tmin.second
                    low_seconds[day_offset].append(seconds_min)

        # Agregar resultados
        results: dict[str, dict] = {}
        for day in (0, 1, 2):
            # mean return series: concatenar por columnas y hacer mean (ignorar NaN)
            if len(returns_lists[day]) == 0:
                median_series = pd.Series(dtype=float)
                avg_series = pd.Series(dtype=float)
            else:
                all_returns_df = pd.concat(returns_lists[day], axis=1).sort_index()
                
                avg_series = all_returns_df.mean(axis=1, skipna=True)
                # opcional: asegurar orden por hora
                avg_series.index = pd.to_datetime(avg_series.index, format="%H:%M").time
                avg_series = avg_series.sort_index()
                # devolver index como string HH:MM
                avg_series.index = [t.strftime("%H:%M") for t in avg_series.index]
                
                median_series = all_returns_df.median(axis=1, skipna=True)
                # opcional: asegurar orden por hora
                median_series.index = pd.to_datetime(median_series.index, format="%H:%M").time
                median_series = median_series.sort_index()
                # devolver index como string HH:MM
                median_series.index = [t.strftime("%H:%M") for t in median_series.index]

            results[f"day{day+1}"] = {
                "avg_return_series": [{k: (None if (isinstance(v, float) and np.isnan(v)) else v)} for k, v in avg_series.items()],
                "median_return_series": [{k: (None if (isinstance(v, float) and np.isnan(v)) else v)} for k, v in median_series.items()],
                "avg_high_time": _secondsToTimeStr(float(np.nan) if len(high_seconds[day]) == 0 else float(np.mean(high_seconds[day]))),
                "avg_low_time": _secondsToTimeStr(float(np.nan) if len(low_seconds[day]) == 0 else float(np.mean(low_seconds[day]))),
                "median_high_time": _secondsToTimeStr(float(np.nan) if len(high_seconds[day]) == 0 else float(np.median(high_seconds[day]))),
                "median_low_time": _secondsToTimeStr(float(np.nan) if len(low_seconds[day]) == 0 else float(np.median(low_seconds[day]))),
                "n_instances": len(returns_lists[day])
            }

        return results
    print(windows)
    intraday_stats: dict[str, dict] = compute_gap_stats(list_of_dfs=[w for w in windows if isinstance(w, pd.DataFrame) and not w.empty])
    
    # TODO: Add intraday stats (like HOD time and LOD time or the average intrday return line chart)
    stats = {
        'quantity': len(day1),
        'avg_gap': day1['gap'].mean(),
        'median_gap': day1['gap'].median(),
        'day1': {
            **gapStats(data=day1),
            **intraday_stats['day1']
        } if len(day1) > 0 else {},
        'day2': {
            **gapStats(data=day2),
            **intraday_stats['day2']
        } if len(day2) > 0 else {},
        'day3': {
            **gapStats(data=day3),
            **intraday_stats['day3']
        } if len(day3) > 0 else {}
    }
    
    # Combinar y estructurar los datos
    overview_data = {
        **benzinga_info,
        **benzinga_key_data,
        **share_data,
        **yahoo_info,
        **finviz_data,
        **{
            'cik': finviz_data.get('CIK', None),
            'symbol': symbol,
            'company_name': finviz_data.get('Company', benzinga_info.get('shortName', symbol)),
            'description': yahoo_info.get('long_business_summary', finviz_data.get('Description', benzinga_info.get('longDescription', ''))),
            'sector': finviz_data.get('Sector', yahoo_info.get('sector', benzinga_info.get('msSectorName', share_data.get('sector', '')))),
            'industry': finviz_data.get('Industry', yahoo_info.get('industry',benzinga_info.get('msIndustryName', share_data.get('industry', '')))),
            'country': finviz_data.get('Country', yahoo_info.get('country', benzinga_info.get('country', ''))),
            'exchange': finviz_data.get('Exchange', share_data.get('bzExchange', '')),
            'website': finviz_data.get('Web', benzinga_info.get('homepage', '')),
            'employees': finviz_data.get('Employees', yahoo_info.get('full_time_employees', benzinga_info.get('totalEmployees', ''))),
            'address': yahoo_info.get('address1', '') + ', ' + yahoo_info.get('city', '') + ', ' + finviz_data.get('Country', yahoo_info.get('country', benzinga_info.get('country', ''))),
            'ipo': finviz_data.get('IPO', None),
            'insiders_pct': yahoo_info.get('insiders_pct', finviz_data.get('Insider Own Pct', '')),
            'institutional_pct': yahoo_info.get('institutional_pct', finviz_data.get('Inst Own Pct', '')),

            # Datos de precio
            'current_price': share_data.get('lastTradePrice', 0),
            'previous_close': finviz_data.get('Prev Close', 0),
            'change': finviz_data.get('Change', 0),
            'change_percent': finviz_data.get('Change Pct', 0),
            'volume': share_data.get('volume', 0),
            'avg_volume': share_data.get('averageVolume', 0),
            
            # Métricas clave
            'market_cap': share_data.get('marketCap', benzinga_key_data.get('marketCap', 0)),
            'shares_outstanding': share_data.get('sharesOutstanding', benzinga_key_data.get('sharesOutstanding', 0)),
            'shares_float': share_data.get('sharesFloat', benzinga_key_data.get('marketCshareFloatap', 0)),
            'shares_short': benzinga_key_data.get('sharesShort', None),
            'short_pct': finviz_data.get('Short Float Pct', benzinga_key_data.get('sharesShortPercentOfFloat', None)),
            'pe_ratio': finviz_data.get('P/E', benzinga_key_data.get('peRatio', 0)),
            'eps': finviz_data.get('EPS (ttm)', benzinga_key_data.get('eps', 0)),
            'dividend_yield': finviz_data.get('Dividend %', 0),
            'current_ratio': finviz_data.get('Current Ratio', benzinga_key_data.get('currentRatio', None)),

            'warrants': warrants,
            'warrants_price': warrants_price,
            
            # Rangos de precio
            'day_range_low': finviz_data.get('Range Low', 0),
            'day_range_high': finviz_data.get('Range High', 0),
            '52_week_low': share_data.get('fiftyTwoWeekLow', 0),
            '52_week_high': share_data.get('fiftyTwoWeekHigh', 0),
            
            # Timestamps
            'last_updated': datetime.now().isoformat(),
            'last_trade_time': share_data.get('lastTradeTime', ''),
            'candles': candles.to_dict(orient='records'),
            'stats': stats
        }
    }
    
    # Limpiar datos
    overview_data = clean_data({k.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_per_').replace('-', '_').replace('.', ''): v for k, v in overview_data.items()})
    #print(overview_data)
    return jsonify({
        'success': True,
        'data': overview_data,
        'error': None
    })
        
    # except Exception as e:
    #     return handle_error(e, symbol)

@asset_bp.route(rule="/search", methods=['POST'])
@login_required
def search_yahoo() -> dict:
    
    try:
        params = request.values if request.method == 'GET' else (request.json if request.is_json else request.form)
        try:
            response = YahooFinance().search(text=params.get('q', None))
        except:
            response = YahooFinance(verify=False).search(text=params.get('q', None))
        
        if 'quotes' in response:
            return {'executed': True, 'description': 'success', 'data': response['quotes']}
        else:
            return {'executed': True, 'description': 'success', 'data': []}
        
    except Exception as e:
        return {'executed': False, 'description': 'error', 'data': str(e)}
    
@asset_bp.route('<symbol>/fundamentals')
@login_required
def get_stock_fundamentals(symbol):
    """
    Obtiene datos fundamentales detallados de la acción
    """
    try:
        symbol = symbol.upper()
        
        benzinga = Benzinga(symbol)
        finviz = FinvizTicker(symbol)
        
        # Datos fundamentales de Benzinga
        valuation = benzinga.valuations()
        balance_sheet = benzinga.balanceSheet()
        income_statement = benzinga.incomeStatement()
        cash_flow = benzinga.cashFlow()
        operation_ratios = benzinga.operationRatios()
        
        # Datos de Finviz
        finviz_data = finviz.data()
        
        fundamentals_data = {
            'valuation_metrics': {
                'market_cap': valuation.get('marketCapitalization', 0),
                'enterprise_value': valuation.get('enterpriseValue', 0),
                'pe_ratio': finviz_data.get('P/E', 0),
                'peg_ratio': finviz_data.get('PEG', 0),
                'price_to_book': finviz_data.get('P/B', 0),
                'price_to_sales': finviz_data.get('P/S', 0),
                'ev_to_revenue': valuation.get('evToRevenue', 0),
                'ev_to_ebitda': valuation.get('evToEbitda', 0)
            },
            
            'profitability': {
                'revenue': income_statement.get('totalRevenue', 0),
                'gross_profit': income_statement.get('grossProfit', 0),
                'operating_income': income_statement.get('operatingIncome', 0),
                'net_income': income_statement.get('netIncome', 0),
                'ebitda': income_statement.get('ebitda', 0),
                'earnings_per_share': income_statement.get('earningsPerShare', 0),
                'gross_margin': finviz_data.get('Gross Margin', 0),
                'operating_margin': finviz_data.get('Oper. Margin', 0),
                'profit_margin': finviz_data.get('Profit Margin', 0),
                'roe': finviz_data.get('ROE', 0),
                'roa': finviz_data.get('ROA', 0),
                'roi': finviz_data.get('ROI', 0)
            },
            
            'balance_sheet': {
                'total_assets': balance_sheet.get('totalAssets', 0),
                'total_liabilities': balance_sheet.get('totalLiabilities', 0),
                'shareholders_equity': balance_sheet.get('shareholdersEquity', 0),
                'cash_and_equivalents': balance_sheet.get('cashAndCashEquivalents', 0),
                'total_debt': balance_sheet.get('totalDebt', 0),
                'book_value_per_share': finviz_data.get('Book/sh', 0),
                'debt_to_equity': finviz_data.get('Debt/Eq', 0),
                'current_ratio': finviz_data.get('Current Ratio', 0),
                'quick_ratio': finviz_data.get('Quick Ratio', 0)
            },
            
            'cash_flow': {
                'operating_cash_flow': cash_flow.get('operatingCashFlow', 0),
                'investing_cash_flow': cash_flow.get('investingCashFlow', 0),
                'financing_cash_flow': cash_flow.get('financingCashFlow', 0),
                'free_cash_flow': cash_flow.get('freeCashFlow', 0),
                'capex': cash_flow.get('capitalExpenditures', 0)
            },
            
            'growth_metrics': {
                'revenue_growth': operation_ratios.get('revenueGrowth', 0),
                'earnings_growth': operation_ratios.get('earningsGrowth', 0),
                'revenue_growth_3y': finviz_data.get('Sales growth past 5 years', 0),
                'eps_growth_3y': finviz_data.get('EPS growth past 5 years', 0),
                'eps_growth_next_y': finviz_data.get('EPS growth next year', 0),
                'eps_growth_next_5y': finviz_data.get('EPS growth next 5 years', 0)
            }
        }
        
        fundamentals_data = clean_data(fundamentals_data)
        
        return jsonify({
            'success': True,
            'data': fundamentals_data,
            'error': None
        })
        
    except Exception as e:
        return handle_error(e, symbol)

@asset_bp.route('<symbol>/news')
@login_required
def get_stock_news(symbol):
    """
    Obtiene noticias relacionadas con la acción
    """
    try:
        symbol = symbol.upper()
        
        benzinga = Benzinga(symbol)
        finviz = FinvizTicker(symbol)
        
        # Noticias de Benzinga
        benzinga_news = benzinga.news(df=False)
        
        # Noticias de Finviz
        finviz_news = finviz.news(df=False)
        
        # Combinar y formatear noticias
        combined_news = []
        
        # Procesar noticias de Benzinga
        if benzinga_news:
            for article in benzinga_news[:10]:  # Limitar a 10 artículos
                combined_news.append({
                    'title': article.get('title', ''),
                    'summary': article.get('summary', ''),
                    'url': article.get('url', ''),
                    'source': 'Benzinga',
                    'date': article.get('created', ''),
                    'author': article.get('author', ''),
                    'image': article.get('image', '')
                })
        
        # Procesar noticias de Finviz
        if finviz_news:
            for article in finviz_news[:10]:  # Limitar a 10 artículos
                combined_news.append({
                    'title': article.get('Header', ''),
                    'summary': '',
                    'url': article.get('URL', ''),
                    'source': article.get('Source', 'Finviz'),
                    'date': article.get('Date', ''),
                    'author': '',
                    'image': ''
                })
        
        # Ordenar por fecha (más recientes primero)
        combined_news = sorted(combined_news, key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': combined_news[:20],  # Máximo 20 noticias
            'error': None
        })
        
    except Exception as e:
        return handle_error(e, symbol)

@asset_bp.route('<symbol>/earnings')
@login_required
def get_stock_earnings(symbol):
    """
    Obtiene datos de ganancias y dividendos
    """
    try:
        symbol = symbol.upper()
        
        benzinga = Benzinga(symbol)
        
        # Datos de ganancias
        earnings = benzinga.earnings(df=False)
        dividends = benzinga.dividends(df=False)
        splits = benzinga.splits(df=False)
        
        earnings_data = {
            'earnings_history': earnings if earnings else [],
            'dividend_history': dividends if dividends else [],
            'stock_splits': splits if splits else [],
            'next_earnings_date': None,  # Se puede obtener del calendario
            'dividend_yield': 0,
            'payout_ratio': 0
        }
        
        earnings_data = clean_data(earnings_data)
        
        return jsonify({
            'success': True,
            'data': earnings_data,
            'error': None
        })
        
    except Exception as e:
        return handle_error(e, symbol)

@asset_bp.route('<symbol>/ownership')
@login_required
def get_stock_ownership(symbol):
    """
    Obtiene datos de propiedad institucional e insider
    """
    try:
        symbol = symbol.upper()
        
        benzinga = Benzinga(symbol)
        finviz = FinvizTicker(symbol)
        
        # Datos de propiedad
        ownership = benzinga.ownership()
        short_interest = benzinga.shortInterest(df=False)
        insider_trading = finviz.insiders(df=False)
        
        ownership_data = {
            'institutional_ownership': ownership.get('institutionalSharesOwned', 0),
            'insider_ownership': finviz.data().get('Insider Own', 0),
            'insider_transactions': insider_trading if insider_trading else [],
            'short_interest': short_interest if short_interest else {},
            'float_short': finviz.data().get('Short Float', 0),
            'shares_outstanding': ownership.get('totalSharesOutstanding', 0)
        }
        
        ownership_data = clean_data(ownership_data)
        
        return jsonify({
            'success': True,
            'data': ownership_data,
            'error': None
        })
        
    except Exception as e:
        return handle_error(e, symbol)
