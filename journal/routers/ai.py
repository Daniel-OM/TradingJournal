
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_login import login_required

from ..src.edgar import SECFiling
from ..src.ai import LLM, LLMResponse
from ..config import GROQ_API_KEY

ai_bp = Blueprint(name='ai_endpoints', import_name=__name__)

@ai_bp.route('/asset')
@login_required
def asset_analysis():
    """
    Endpoint stock analysis with AI
    
    Body JSON:
    {
        "symbol": "AAPL",
        "data": {
            "rsi": 65,
            "media_50": 170.20,
            "media_200": 165.80,
            "volumen": "alto"
        },
        "trade_type": "swing",  # position, swing, intraday
        "model": "llama-3.3-70b-versatile"
    }
    """
    
    try:
        r = request.json
    
        symbol = r.get('symbol')
        data = r.get('data', {})
        trade_type = r.get('trade_type', 'intraday')
        model = r.get('model', 'llama-3.3-70b-versatile')
        
        if not symbol:
            return jsonify({
                'error': 'The symbol must be passed'
            }), 400
        
        if trade_type not in ['position', 'swing', 'intraday']:
            return jsonify({
                'error': 'trade_type must be: position, swing or intraday'
            }), 400
        
        llm = LLM(api_key=GROQ_API_KEY)
        prompt: str = llm.createStockPrompt(
            symbol=symbol, 
            data=data, 
            trade_type=trade_type
        )
        context: str = llm.getSystemPrompt(trade_type=trade_type)

        analysis = None
        try:
            response: LLMResponse = llm.callGroq(prompt=prompt, context=context, model=model)
            analysis: str = response.response
        except Exception as e:
            return jsonify({
                'error': f'Somethign went wrong: {e}'
            }), 400
        
        return jsonify({
            'request': {
                'symbol': symbol,
                'data': data,
                'trade_type': trade_type,
                'model': model,
            },
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Error interno: {str(e)}'
        }), 500
        
@ai_bp.route('/file')
@login_required
def file_analysis():
    """
    Endpoint SEC file analysis with AI
    
    Body JSON:
    {
        "cik": "1655210",
        "accn": "000119312525242542",
        "trade_type": "swing",  # position, swing, intraday
        "model": "llama-3.3-70b-versatile"
    }
    """
    
    try:
        r = request.json
    
        cik = r.get('cik')
        accn = r.get('accn')
        trade_type = r.get('trade_type', 'intraday')
        model = r.get('model', 'llama-3.3-70b-versatile')
        
        if not cik:
            return jsonify({
                'error': 'The cik must be passed'
            }), 400
        if not accn:
            return jsonify({
                'error': 'The accn must be passed'
            }), 400
        
        if trade_type not in ['position', 'swing', 'intraday']:
            return jsonify({
                'error': 'trade_type must be: position, swing or intraday'
            }), 400
        
        sec = SECFiling(cik=cik, accn=accn)
        llm = LLM(api_key=GROQ_API_KEY)
        prompt: str = llm.createFilePrompt(file_content=sec.getFilingContent(html=False))
        context: str = llm.getSystemPrompt(trade_type=trade_type)

        analysis = None
        try:
            response: LLMResponse = llm.callGroq(prompt=prompt, context=context, model=model)
            analysis: str = response.response
        except Exception as e:
            return jsonify({
                'error': f'Somethign went wrong: {e}'
            }), 400
        
        return jsonify({
            'request': {
                'cik': cik,
                'accn': accn,
                'trade_type': trade_type,
                'model': model,
            },
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Error interno: {str(e)}'
        }), 500

@ai_bp.route('/models', methods=['GET'])
def models_available():
    """Muestra qué modelos están configurados"""
    return jsonify({
        'models': {
            'llama-3.3-70b-versatile': 'MEJOR calidad (1K req/día)',
            'llama-3.1-8b-instant': 'MÁS rápido (14.4K req/día)',
            'llama-4-scout-17b-16e': 'Balance (1K req/día)'
        },
    })