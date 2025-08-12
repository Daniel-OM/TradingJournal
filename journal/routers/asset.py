
import os
from datetime import date, datetime, timedelta, time
from collections import defaultdict

import numpy as np
import pandas as pd

from sqlalchemy import desc, func, case, extract, and_
from flask import Blueprint, Response, render_template, request, flash, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user

from ..models import Watchlist, Candle
from ..src.yahoofinance import YahooTicker
from ..src.benzinga import Benzinga
from ..src.finviz import FinvizScraper, FinvizTicker

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

asset_bp = Blueprint(name='asset_endpoints', import_name=__name__)

@asset_bp.route('/')
@login_required
def asset() -> str:

    return render_template(template_name_or_list='asset/asset.html')

@asset_bp.route('/api/<string:symbol>')
@login_required
def api_asset(symbol:str) -> str:
    import json
    """
    Endpoint principal que obtiene información general de una acción
    Combina datos de Benzinga y Finviz
    """
    # try:
    symbol = symbol.upper()
    
    # Obtener datos de Benzinga
    benzinga = Benzinga(symbol=symbol, random_headers=True)
    benzinga_info = benzinga.info()
    benzinga_key_data = benzinga.keyData()
    share_data = benzinga.shareData()
    
    # Obtener datos de Finviz
    finviz = FinvizTicker(symbol=symbol, random_headers=True)
    finviz_info = finviz.info(df=False)
    finviz_data = finviz_info if isinstance(finviz_info, dict) else {}

    yahoo = YahooTicker(ticker=symbol)
    finviz_candles = yahoo.getPrice(start=(datetime.now() - timedelta(days=365)).timestamp(),
                                    end=datetime.now().timestamp(), 
                                    timeframe='1d', df=False)
    
    # Combinar y estructurar los datos
    overview_data = {
        **finviz_data,
        **benzinga_info,
        **benzinga_key_data,
        **share_data,
        **{
            'symbol': symbol,
            'company_name': benzinga_info.get('shortName', finviz_data.get('Company', symbol)),
            'description': finviz_data.get('Description', benzinga_info.get('longDescription', '')),
            'sector': benzinga_info.get('msSectorName', finviz_data.get('Sector', '')),
            'industry': benzinga_info.get('msIndustryName', finviz_data.get('Industry', '')),
            'country': benzinga_info.get('country', finviz_data.get('Country', '')),
            'exchange': share_data.get('bzExchange', finviz_data.get('Exchange', '')),
            'website': benzinga_info.get('homepage', ''),
            
            # Datos de precio
            'current_price': share_data.get('lastTradePrice', 0),
            'previous_close': finviz_data.get('Prev Close', 0),
            'change': finviz_data.get('Change', 0),
            'change_percent': finviz_data.get('Change Pct', 0),
            'volume': share_data.get('volume', 0),
            'avg_volume': share_data.get('averageVolume', 0),
            
            # Métricas clave
            'market_cap': share_data.get('marketCap', benzinga_key_data.get('marketCap', 0)),
            'shares_outstanding': share_data.get('sharesOutstanding', 0),
            'shares_float': share_data.get('sharesFloat', 0),
            'pe_ratio': finviz_data.get('P/E', benzinga_key_data.get('peRatio', 0)),
            'eps': finviz_data.get('EPS (ttm)', benzinga_key_data.get('eps', 0)),
            'dividend_yield': finviz_data.get('Dividend %', 0),
            
            # Rangos de precio
            'day_range_low': finviz_data.get('Range Low', 0),
            'day_range_high': finviz_data.get('Range High', 0),
            '52_week_low': share_data.get('fiftyTwoWeekLow', 0),
            '52_week_high': share_data.get('fiftyTwoWeekHigh', 0),
            
            # Timestamps
            'last_updated': datetime.now().isoformat(),
            'last_trade_time': share_data.get('lastTradeTime', ''),
            'candles': finviz_candles,
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

@asset_bp.route('/api/stock/<symbol>/fundamentals')
@login_required
def get_stock_fundamentals(symbol):
    """
    Obtiene datos fundamentales detallados de la acción
    """
    try:
        symbol = symbol.upper()
        logger.info(f"Fetching fundamentals for {symbol}")
        
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

@asset_bp.route('/api/stock/<symbol>/news')
@login_required
def get_stock_news(symbol):
    """
    Obtiene noticias relacionadas con la acción
    """
    try:
        symbol = symbol.upper()
        logger.info(f"Fetching news for {symbol}")
        
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

@asset_bp.route('/api/stock/<symbol>/earnings')
@login_required
def get_stock_earnings(symbol):
    """
    Obtiene datos de ganancias y dividendos
    """
    try:
        symbol = symbol.upper()
        logger.info(f"Fetching earnings for {symbol}")
        
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

@asset_bp.route('/api/stock/<symbol>/ownership')
@login_required
def get_stock_ownership(symbol):
    """
    Obtiene datos de propiedad institucional e insider
    """
    try:
        symbol = symbol.upper()
        logger.info(f"Fetching ownership data for {symbol}")
        
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

@asset_bp.route('/api/screener')
@login_required
def stock_screener():
    """
    Endpoint para el screener de acciones usando Finviz
    """
    try:
        # Obtener parámetros de filtro
        exchange = request.args.getlist('exchange') or ['nyse', 'nasd']
        min_price = float(request.args.get('min_price', 1))
        max_price = float(request.args.get('max_price', 1000))
        min_volume = int(request.args.get('min_volume', 100000))
        min_market_cap = request.args.get('min_market_cap', 'small')
        
        logger.info(f"Running screener with filters")
        
        # Configurar filtros para Finviz
        filters = []
        
        # Filtros de precio
        if min_price > 1:
            filters.append(f'sh_price_o{min_price}')
        if max_price < 1000:
            filters.append(f'sh_price_u{max_price}')
            
        # Filtro de volumen
        if min_volume > 0:
            volume_filter = 'sh_avgvol_o'
            if min_volume >= 1000000:
                filters.append(f'{volume_filter}{min_volume//1000000}M')
            elif min_volume >= 1000:
                filters.append(f'{volume_filter}{min_volume//1000}k')
                
        # Filtro de market cap
        if min_market_cap:
            cap_filters = {
                'micro': 'cap_micro',
                'small': 'cap_small',
                'mid': 'cap_mid',
                'large': 'cap_large'
            }
            if min_market_cap in cap_filters:
                filters.append(cap_filters[min_market_cap])
        
        scraper = FinvizScraper()
        results = scraper.screener(
            exchange=exchange,
            filters=filters,
            minpctchange=-100,  # Sin límite de cambio
            justsymbols=False
        )
        
        # Convertir DataFrame a formato JSON
        if not results.empty:
            screener_results = results.to_dict('records')
        else:
            screener_results = []
        
        return jsonify({
            'success': True,
            'data': {
                'results': screener_results[:100],  # Limitar a 100 resultados
                'total_found': len(screener_results),
                'filters_applied': {
                    'exchange': exchange,
                    'min_price': min_price,
                    'max_price': max_price,
                    'min_volume': min_volume,
                    'min_market_cap': min_market_cap
                }
            },
            'error': None
        })
        
    except Exception as e:
        return handle_error(e)

@asset_bp.route('/api/sectors/hot')
@login_required
def get_hot_sectors():
    """
    Obtiene sectores con mejor rendimiento
    """
    try:
        logger.info("Fetching hot sectors")
        
        scraper = FinvizScraper()
        hot_sectors = scraper.hotSectors(column='%Week', df=False)
        
        return jsonify({
            'success': True,
            'data': hot_sectors[:20],  # Top 20 sectores
            'error': None
        })
        
    except Exception as e:
        return handle_error(e)

@asset_bp.route('/api/industries/hot')
@login_required
def get_hot_industries():
    """
    Obtiene industrias con mejor rendimiento
    """
    try:
        logger.info("Fetching hot industries")
        
        scraper = FinvizScraper()
        hot_industries = scraper.hotIndustry(column='%Week', df=False)
        
        return jsonify({
            'success': True,
            'data': hot_industries[:20],  # Top 20 industrias
            'error': None
        })
        
    except Exception as e:
        return handle_error(e)

@asset_bp.route('/api/earnings/calendar')
@login_required
def get_earnings_calendar():
    """
    Obtiene el calendario de earnings
    """
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        logger.info(f"Fetching earnings calendar from {date_from} to {date_to}")
        
        benzinga = Benzinga()
        
        if date_from and date_to:
            earnings_calendar = benzinga.earningsHistoric(
                date_from=date_from,
                date_to=date_to,
                df=False
            )
        else:
            earnings_calendar = benzinga.earningsCalendar(df=False)
        
        return jsonify({
            'success': True,
            'data': earnings_calendar,
            'error': None
        })
        
    except Exception as e:
        return handle_error(e)

@asset_bp.route('/api/premarket')
@login_required
def get_premarket_data():
    """
    Obtiene datos pre-mercado
    """
    try:
        logger.info("Fetching premarket data")
        
        benzinga = Benzinga()
        gainers, losers, earnings = benzinga.premarketData()
        
        premarket_data = {
            'gainers': gainers.to_dict('records') if not gainers.empty else [],
            'losers': losers.to_dict('records') if not losers.empty else [],
            'earnings_today': earnings.to_dict('records') if not earnings.empty else []
        }
        
        return jsonify({
            'success': True,
            'data': premarket_data,
            'error': None
        })
        
    except Exception as e:
        return handle_error(e)