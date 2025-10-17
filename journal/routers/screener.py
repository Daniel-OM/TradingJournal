
import numpy as np
import pandas as pd

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

from ..models import Watchlist, Candle
from ..src.yahoofinance import YahooTicker
from ..src.benzinga import Benzinga
from ..src.finviz import FinvizScraper, FinvizTicker, FinvizScreenerConfig

def handle_error(e):
    """Maneja errores y retorna una respuesta JSON consistente"""
    error_msg = f"Error processing request: {str(e)}"
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

screener_pages = Blueprint(name='screener_pages', import_name=__name__)

@screener_pages.route('/')
@login_required
def screeners() -> str:
    return render_template(template_name_or_list='asset/screener.html')

screener_bp = Blueprint(name='screener_endpoints', import_name=__name__)

@screener_bp.route('/top-gainers')
@login_required
def get_top_gainers() -> str:

    # try:
    fv = FinvizScraper(random_headers=True)
    config = FinvizScreenerConfig(exchange=['nasd','nyse','amex'], filters=None, signal='ta_topgainers', minpctchange=None, justsymbols=False)
    data = fv.screener(
                exchange=config.exchange,
                filters=config.filters,
                signal=config.signal,
                minpctchange=config.minpctchange,
                justsymbols=config.justsymbols,
                df=True
            )
    data.columns = [c.lower().replace(' ', '_').replace('/', '_') for c in data.columns]
    
    return jsonify({
        'success': True,
        'data': {
            'config': config.to_dict(),
            'name': 'Top Gainers',
            'data': data.to_json(orient='records')
        },
        'error': None
    })
    # except Exception as e:
    #     return handle_error(e)
    
@screener_bp.route('/new-highs')
@login_required
def get_new_highs() -> str:

    try:
        fv = FinvizScraper(random_headers=True)
        config = FinvizScreenerConfig(exchange=['nasd','nyse','amex'], filters=None, signal='ta_newhigh', minpctchange=None, justsymbols=False)
        data = fv.screener(
                    exchange=config.exchange,
                    filters=config.filters,
                    signal=config.signal,
                    minpctchange=config.minpctchange,
                    justsymbols=config.justsymbols,
                    df=True
                )
        data.columns = [c.lower().replace(' ', '_').replace('/', '_') for c in data.columns]
        
        return jsonify({
            'success': True,
            'data': {
                'config': config.to_dict(),
                'name': 'New Highs',
            '   data': data.to_json(orient='records')
            },
            'error': None
        })
    except Exception as e:
        return handle_error(e)
    
@screener_bp.route('/overbought')
@login_required
def get_overbought() -> str:

    try:
        fv = FinvizScraper(random_headers=True)
        config = FinvizScreenerConfig(exchange=['nasd','nyse','amex'], filters=None, signal='ta_overbought', minpctchange=None, justsymbols=False)
        data = fv.screener(
                    exchange=config.exchange,
                    filters=config.filters,
                    signal=config.signal,
                    minpctchange=config.minpctchange,
                    justsymbols=config.justsymbols,
                    df=True
                )
        data.columns = [c.lower().replace(' ', '_').replace('/', '_') for c in data.columns]
        
        return jsonify({
            'success': True,
            'data': {
                'config': config.to_dict(),
                'name': 'Overbought',
                'data': data.to_json(orient='records')
            },
            'error': None
        })
    except Exception as e:
        return handle_error(e)
    
@screener_bp.route('/unusual-volume')
@login_required
def get_unusual_volume() -> str:

    try:
        fv = FinvizScraper(random_headers=True)
        config = FinvizScreenerConfig(exchange=['nasd','nyse','amex'], filters=None, signal='ta_unusualvolume', minpctchange=None, justsymbols=False)
        data = fv.screener(
                    exchange=config.exchange,
                    filters=config.filters,
                    signal=config.signal,
                    minpctchange=config.minpctchange,
                    justsymbols=config.justsymbols,
                    df=True
                )
        data.columns = [c.lower().replace(' ', '_').replace('/', '_') for c in data.columns]
        
        return jsonify({
            'success': True,
            'data': {
                'config': config.to_dict(),
                'name': 'Unusual Volume',
                'data': data.to_json(orient='records')
            },
            'error': None
        })
    except Exception as e:
        return handle_error(e)
    
@screener_bp.route('/top-losers')
@login_required
def get_top_losers() -> str:

    try:
        fv = FinvizScraper(random_headers=True)
        config = FinvizScreenerConfig(exchange=['nasd','nyse','amex'], filters=None, signal='ta_toplosers', minpctchange=None, justsymbols=False)
        data = fv.screener(
                    exchange=config.exchange,
                    filters=config.filters,
                    signal=config.signal,
                    minpctchange=config.minpctchange,
                    justsymbols=config.justsymbols,
                    df=True
                )
        data.columns = [c.lower().replace(' ', '_').replace('/', '_') for c in data.columns]
        
        return jsonify({
            'success': True,
            'data': {
                'config': config.to_dict(),
                'name': 'Top Losers',
                'data': data.to_json(orient='records')
            },
            'error': None
        })
    except Exception as e:
        return handle_error(e)
        
@screener_bp.route('/new-lows')
@login_required
def get_new_lows() -> str:

    try:
        fv = FinvizScraper(random_headers=True)
        config = FinvizScreenerConfig(exchange=['nasd','nyse','amex'], filters=None, signal='ta_newlow', minpctchange=None, justsymbols=False)
        data = fv.screener(
                    exchange=config.exchange,
                    filters=config.filters,
                    signal=config.signal,
                    minpctchange=config.minpctchange,
                    justsymbols=config.justsymbols,
                    df=True
                )
        data.columns = [c.lower().replace(' ', '_').replace('/', '_') for c in data.columns]
        return jsonify({
            'success': True,
            'data': {
                'config': config.to_dict(),
                'name': 'New Lows',
                'data': data.to_json(orient='records')
            },
            'error': None
        })
    except Exception as e:
        return handle_error(e)
    
@screener_bp.route('/oversold')
@login_required
def get_oversold() -> str:

    try:
        fv = FinvizScraper(random_headers=True)
        config = FinvizScreenerConfig(exchange=['nasd','nyse','amex'], filters=None, signal='ta_oversold', minpctchange=None, justsymbols=False)
        data = fv.screener(
                    exchange=config.exchange,
                    filters=config.filters,
                    signal=config.signal,
                    minpctchange=config.minpctchange,
                    justsymbols=config.justsymbols,
                    df=True
                )
        data.columns = [c.lower().replace(' ', '_').replace('/', '_') for c in data.columns]
        return jsonify({
            'success': True,
            'data': {
                'config': config.to_dict(),
                'name': 'Oversold',
                'data': data.to_json(orient='records')
            },
            'error': None
        })
    except Exception as e:
        return handle_error(e)

@screener_bp.route('/screener')
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
        results: pd.DataFrame = scraper.screener(
            exchange=exchange,
            filters=filters,
            signal=None,
            minpctchange=None,
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

@screener_bp.route('/sectors/hot')
@login_required
def get_hot_sectors():
    """
    Obtiene sectores con mejor rendimiento
    """
    try:
        scraper = FinvizScraper()
        hot_sectors = scraper.hotSectors(column='%Week', df=False)
        
        return jsonify({
            'success': True,
            'data': hot_sectors[:20],  # Top 20 sectores
            'error': None
        })
        
    except Exception as e:
        return handle_error(e)

@screener_bp.route('/industries/hot')
@login_required
def get_hot_industries():
    """
    Obtiene industrias con mejor rendimiento
    """
    try:
        scraper = FinvizScraper()
        hot_industries = scraper.hotIndustry(column='%Week', df=False)
        
        return jsonify({
            'success': True,
            'data': hot_industries[:20],  # Top 20 industrias
            'error': None
        })
        
    except Exception as e:
        return handle_error(e)

@screener_bp.route('/earnings/calendar')
@login_required
def get_earnings_calendar():
    """
    Obtiene el calendario de earnings
    """
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
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

@screener_bp.route('/premarket')
@login_required
def get_premarket_data():
    """
    Obtiene datos pre-mercado
    """
    try:
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