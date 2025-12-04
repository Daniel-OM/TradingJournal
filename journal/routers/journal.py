
import os
from typing import Any
from datetime import date, datetime, timedelta, time
from collections import defaultdict
import asyncio
from copy import deepcopy

import numpy as np

from werkzeug.utils import secure_filename
from werkzeug.datastructures.file_storage import FileStorage
from sqlalchemy import desc, func, case, extract, and_, or_
from flask import Blueprint, Response, render_template, request, flash, redirect, url_for, jsonify, abort, current_app
from flask_login import login_required, current_user
from werkzeug.wrappers.response import Response

from journal.src.import_das import ImportStats

from ..models.watchlist_entry import WatchlistEntry

from ..config import UPLOAD_FOLDER
from ..models import db, AccountBalance, Trade, Transaction, Media, Strategy, StrategyCondition, Error, Watchlist, Candle, trade_scoring, trade_errors
from ..src.performance import TradePerformance
from ..src.import_das import CSVImporter
from .utils import save_uploaded_files, calculate_max_drawdown, download_candles, localToUtc

journal_pages = Blueprint(name='journal_pages', import_name=__name__)

@journal_pages.route(rule='/')
@login_required
def journal() -> str:
    return render_template(template_name_or_list='trade/journal.html')
    
@journal_pages.route(rule='/performance')
@login_required
def performance() -> str:
    # ===== OBTENER FILTROS =====
    start = request.args.get('start', type=str)
    end = request.args.get('end', type=str)
    strategy_id = request.args.get('strategy', type=int)
    asset_symbol = request.args.get('symbol', type=str)
    watchlist_id = request.args.get('watchlist', type=int)
    limit = request.args.get('limit', type=int)
    side = request.args.get('side', type=str)  # LONG or SHORT
    # Tags filter: comma separated list of tags. Mode can be 'include' or 'exclude'
    tags_param = request.args.get('tags', type=str)
    tags_mode = request.args.get('tags_mode', type=str)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # ===== CONSTRUIR QUERY BASE =====
    base_query = Trade.query.filter(Trade.user_id == current_user.id)
    
    # Filtro por watchlist
    if watchlist_id:
        base_query = base_query.join(
            WatchlistEntry,
            and_(
                Trade.symbol == WatchlistEntry.symbol,
                Trade.entry_date >= WatchlistEntry.date,
                Trade.entry_date <= WatchlistEntry.date_exit
            )
        ).filter(WatchlistEntry.watchlist_id == watchlist_id)
    
    # Filtros adicionales
    if strategy_id:
        base_query = base_query.filter(Trade.strategy_id == strategy_id)
    if asset_symbol not in ['None', '', None]:
        base_query = base_query.filter(Trade.symbol == asset_symbol)
    if side in ['LONG', 'SHORT']:
        base_query = base_query.filter(Trade.trade_type == side.upper())
    
    # Filtros de fecha
    start = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d') if not start else start
    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    base_query = base_query.filter(Trade.entry_date >= start_date)

    if end:
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        base_query = base_query.filter(or_(Trade.entry_date <= end_date, Trade.entry_date == None)) # TODO: And if it is a swing trade?
    else:
        temp = base_query.with_entities(func.max(Trade.entry_date)).scalar()
        if temp:
            end = temp.strftime('%Y-%m-%d')
        else:
            end = date.today()
    
    # Aplicar límite
    if limit:
        base_query = base_query.limit(limit)

    # Filtrar por tags (almacenados en Trade.hashtags como string, p.e. 'tag1,tag2')
    if tags_param and tags_param.strip():
        # construir lista de tags limpiadas
        tags_list = [t.strip() for t in tags_param.split(',') if t.strip()]
        if tags_list:
            conds = [Trade.hashtags.ilike(f"%{t}%") for t in tags_list]
            # modo por defecto: include -> devolver trades que contengan al menos uno de los tags
            if tags_mode and tags_mode.lower() == 'exclude':
                # excluir trades que contengan cualquiera de los tags; mantener los que no tengan tags (NULL)
                base_query = base_query.filter((Trade.hashtags == None) | ~or_(*conds))
            else:
                # include: mantener solo trades que contengan al menos uno de los tags
                base_query = base_query.filter(or_(*conds))
    
    # Get data
    all_trades = base_query.order_by(Trade.entry_date).distinct().all()

    # Calculate statistics and charts data
    stats_object = TradePerformance(data=all_trades)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    net_stats, gross_stats, net_charts, gross_charts = loop.run_until_complete(
        asyncio.gather(
            deepcopy(stats_object).getStats(gross=False),
            deepcopy(stats_object).getStats(gross=True),
            deepcopy(stats_object).getCharts(gross=False),
            deepcopy(stats_object).getCharts(gross=True)
        )
    )
    loop.close()
        
    stats = { 'net': net_stats, 'gross': gross_stats }
    charts = { 'net': net_charts, 'gross': gross_charts }
    
    strategies = Strategy.query.filter(Strategy.user_id == current_user.id).all()
    
    return render_template('trade/performance.html', stats=stats, strategies=strategies, charts=charts, 
                           start=start, end=end, strategy_id=strategy_id, asset_symbol=asset_symbol if asset_symbol else '', watchlist_id=watchlist_id, limit=limit, side=side, tags=tags_param or '', tags_mode=tags_mode or 'include')

@journal_pages.route(rule='/trade/<int:id>')
@login_required
def get_trade(id) -> str:
    trade: Trade = Trade.query.get_or_404(id)

    if trade.user_id != current_user.id:
        abort(403)

    # Scoring: obtener puntuaciones individuales del trade
    scoring_data = db.session.execute(
        db.select(
            trade_scoring.c.scoring_id,
            trade_scoring.c.value,
            StrategyCondition.name,
            StrategyCondition.description,
            StrategyCondition.score
        )
        .join(StrategyCondition, trade_scoring.c.scoring_id == StrategyCondition.id)
        .filter(trade_scoring.c.trade_id == id)
    ).fetchall()

    # Errores: obtener errores y su impacto
    errors_data = db.session.execute(
        db.select(
            Error.description,
            Error.category,
            Error.severity,
            trade_errors.c.impact_level,
            trade_errors.c.created_at
        )
        .join(Error, trade_errors.c.error_id == Error.id)
        .filter(trade_errors.c.trade_id == id)
    ).fetchall()

    today = trade.exit_date if trade.exit_date else date.today()
    one_year_ago = trade.entry_date - timedelta(days=365)
    week_ago = trade.entry_date - timedelta(days=5)
    symbol = trade.symbol
    
    daily = Candle.query.filter(Candle.symbol == trade.symbol, 
                                Candle.date >= datetime.combine(one_year_ago, time(0, 0, 0)), 
                                Candle.date <= datetime.combine(today, time(23, 59, 59)), 
                                Candle.timeframe == '1d').distinct().order_by(Candle.date.asc()).all()
    intraday = Candle.query.filter(Candle.symbol == symbol, 
                                   Candle.date >= week_ago, 
                                   Candle.date <= datetime.combine(today, time(23, 59, 59)), 
                                   Candle.timeframe == '1m').distinct().order_by(Candle.date.asc()).all()

    trade_json = trade.to_dict(exclude=['trades', 'trade', 'conditions', 'errors', 'media', 'candles'], force_dollars=False, equity=False, complete=True)
    trade_data = {
        "id": trade.id,
        "symbol": trade_json.get('symbol', None),
        "company_name": trade_json.get('company_name', None),
        "entry_date": trade_json.get('entry_date', None),
        "exit_date": trade_json.get('exit_date', None),
        "entry_time": trade_json.get('entry_time', None),
        "exit_time": trade_json.get('exit_time', None),
        "entry_price": trade_json.get('entry_price', None),
        "exit_price": trade_json.get('exit_price', None),
        "stop_loss": trade_json.get('stop_loss', None),
        "take_profit": trade_json.get('take_profit', None),
        "quantity": trade_json.get('quantity', None),
        "exit_quantity": trade_json.get('exit_quantity', None),
        "balance": trade_json.get('balance', None),
        "commission": trade_json.get('commission', None),
        "locates": trade_json.get('locates', None),
        "trade_type": trade_json.get('trade_type', None),
        "profit_loss": trade_json.get('profit_loss', None),
        "description": trade_json.get('description', None),
        "why_profitable": trade_json.get('why_profitable', None),
        "influencing_factors": trade_json.get('influencing_factors', None),
        "hashtags": trade_json.get('hashtags', None),
        "strategy": trade_json.get('strategy', None),
        "conditions": [{
            'scoring_id': s.scoring_id,
            'value': s.value,
            'name': s.name,
            'description': s.description,
            'score': s.score,
        } for s in scoring_data],
        "errors": [{
            'description': e.description,
            'category': e.category,
            'severity': e.severity,
            'impact_level': e.impact_level,
            'created_at': e.created_at,
        } for e in errors_data],
        "transactions": trade_json.get('transactions', []),
        "media": [
            {
                **m,
                **{"alt": f"Media {i + 1}"}
            }
            for i, m in enumerate(trade_json.get('media', []))
        ],
        "candles": {
            "1d": [t.to_dict() for t in daily],
            "1m": [t.to_dict() for t in intraday],
        }
    }

    return render_template('trade/detail.html', trade_data=trade_data)

@journal_pages.route(rule='/add', methods=['GET', 'POST'])
@journal_pages.route(rule='/add/<int:trade_id>', methods=['GET', 'POST'])
@login_required
def add_trade(trade_id:int=None) -> Response | str:

    if request.method == 'POST':
        symbol = request.form['symbol']

        # try:
        # Crear el trade básico primero
        if trade_id:
            trade: Trade = Trade.query.get_or_404(trade_id)
            trade.entry_date = datetime.strptime(request.form['entry_date'], '%Y-%m-%d').date()
            trade.symbol = request.form['symbol'].upper()
            trade.company_name = request.form.get('company_name', '')
            trade.entry_price = float(request.form['entry_price'])
            trade.entry_time = request.form.get('entry_time', '')
            trade.quantity = float(request.form['quantity'])
            trade.trade_type = request.form['trade_type']
            trade.description = request.form.get('description', '').replace('\n', ' ').replace('\r', ' ').replace('\t', '    ')
            trade.why_profitable = request.form.get('why_profitable', '')
            trade.influencing_factors = request.form.get('influencing_factors', '')
            trade.strategy_id = request.form.get('strategy_id') if request.form.get('strategy_id') else None
            trade.stop_loss = float(request.form['stop_loss']) if request.form.get('stop_loss') else None
            trade.take_profit = float(request.form['take_profit']) if request.form.get('take_profit') else None
            trade.hashtags = request.form.get('hashtags', '')

            # Si hay datos de salida, actualizar y recalcular PnL
            if request.form.get('exit_price'):
                trade.exit_price = float(request.form['exit_price'])
                trade.exit_time = request.form.get('exit_time', '')
                trade.exit_date = datetime.strptime(request.form['exit_date'], '%Y-%m-%d').date()

                if trade.trade_type == 'LONG':
                    trade.profit_loss = (trade.exit_price - trade.entry_price) * trade.quantity - trade.commission
                else:
                    trade.profit_loss = (trade.entry_price - trade.exit_price) * trade.quantity - trade.commission
        else:
            trade = Trade(
                symbol=symbol,
                company_name=request.form.get('company_name', ''),
                balance=request.form.get('balance', 0.0),
                trade_type=request.form['trade_type'],
                description=request.form.get('description', ''),
                why_profitable=request.form.get('why_profitable', ''),
                influencing_factors=request.form.get('influencing_factors', ''),
                strategy_id=request.form.get('strategy_id') if request.form.get('strategy_id') else None,
                stop_loss=float(request.form['stop_loss']) if request.form.get('stop_loss') else None,
                take_profit=float(request.form['take_profit']) if request.form.get('take_profit') else None,
                hashtags=request.form.get('hashtags', ''),
                user_id=current_user.id
            )
            
        db.session.add(trade)
        db.session.flush([trade])

        transaction_date: list[str] = request.form.getlist('transaction_date')
        transaction_time: list[str] = request.form.getlist('transaction_time')
        transaction_timezone: list[str] = request.form.getlist('transaction_timezone')
        transaction_price: list[str] = request.form.getlist('transaction_price')
        transaction_type: list[str] = request.form.getlist('transaction_type')
        transaction_quantity: list[str] = request.form.getlist('transaction_quantity')
        transaction_commission: list[str] = request.form.getlist('transaction_commission')
        transaction_ecn_fee: list[str] = request.form.getlist('transaction_ecn_fee')
        transaction_locates: list[str] = request.form.getlist('transaction_locates')
        trade.remove_transactions()
        for i in range(len(transaction_date)):
            trade.add_transaction(date=datetime.strptime(transaction_date[i], '%Y-%m-%d').date(), 
                                  price=float(transaction_price[i]), 
                                time=localToUtc(date=transaction_date[i], time=transaction_time[i], tz=transaction_timezone[i] if len(transaction_timezone) > 0 else 'Europe/Madrid', mode='time') if len(transaction_timezone) > 0 else transaction_time[i], 
                                quantity=float(transaction_quantity[i]), 
                                commission=float(transaction_commission[i]),
                                ecn_fee=float(transaction_ecn_fee[i]),
                                locates=float(transaction_locates[i]), type=transaction_type[i])

        error_id: list[str] = request.form.getlist('error_id')
        error_descriptions: list[str] = request.form.getlist('error_description')
        error_category: list[str] = request.form.getlist('error_category')
        error_severity: list[str] = request.form.getlist('error_severity')
        trade.remove_errors()
        for i in range(len(error_id)):
            trade.add_error(id=error_id[i], description=error_descriptions[i], user_id=current_user.id, impact_level=error_severity[i], category=error_category[i])
        
        # Guardar archivos multimedia
        images: list[FileStorage] = request.files.getlist('images')
        videos: list[FileStorage] = request.files.getlist('videos')
        
        if images and any(img.filename for img in images):
            for path in save_uploaded_files(images, 'images', trade.id):
                db.session.add(Media(
                    url=path,
                    trade_id=trade.id
                ))
        
        if videos and any(vid.filename for vid in videos):
            for path in save_uploaded_files(videos, 'videos', trade.id):
                db.session.add(Media(
                    url=path,
                    trade_id=trade.id
                ))
        
        # Guardar condiciones de estrategia cumplidas
        condition_id = request.form.getlist('condition_id')
        condition_value = request.form.getlist('condition_value')
        for i in range(len(condition_id)):
            trade.add_condition(condition_id=condition_id[i], value=condition_value[i])
    
        today = trade.entry_date or date.today()
        one_year_ago = today - timedelta(days=365)
        week_ago = today - timedelta(days=5)
        while (datetime.now() - week_ago).days >= 30:
            week_ago = week_ago + timedelta(days=1)
        # Descargar velas con Yahoo Finance
        download_candles(db=db,
                         symbol=symbol,
                         config=[
                             {'timeframe': '1d', 'start':one_year_ago, 'end':today},
                             {'timeframe': '1m', 'start': week_ago, 'end': datetime.combine(today, time(23, 59, 59)) },
                         ])
        
        db.session.commit()
        flash('Trade registrado exitosamente!', 'success')
        return redirect(url_for('journal_pages.journal'))
        
        # except Exception as e:
        #     db.session.rollback()
        #     flash(f'Error al registrar el trade: {str(e)}', 'error')
    
    # GET request - mostrar formulario
    strategies = Strategy.query.all()
    errors = Error.query.filter_by(is_active=True).all()
    
    return render_template('trade/create.html', strategies=strategies, errors=errors, json_strategies=[strat.to_dict(exclude=['trades']) for strat in strategies], date=date)

@journal_pages.route(rule='/edit/<int:trade_id>', methods=['GET', 'POST'])
@login_required
def edit_trade(trade_id) -> Response | str:
    trade: Trade = Trade.query.get_or_404(trade_id)

    if trade.user_id != current_user.id:
        abort(403)
    
    if request.method == 'POST':
        try:
            trade.entry_date = datetime.strptime(request.form['entry_date'], '%Y-%m-%d').date()
            trade.symbol = request.form['symbol'].upper()
            trade.company_name = request.form.get('company_name', '')
            trade.entry_price = float(request.form['entry_price'])
            trade.entry_time = request.form.get('entry_time', '')
            trade.quantity = float(request.form['quantity'])
            trade.trade_type = request.form['trade_type']
            trade.description = request.form.get('description', '').replace('\n', ' ').replace('\r', ' ').replace('\t', '    ')
            trade.why_profitable = request.form.get('why_profitable', '')
            trade.influencing_factors = request.form.get('influencing_factors', '')
            trade.strategy_id = request.form.get('strategy_id') if request.form.get('strategy_id') else None
            trade.stop_loss = float(request.form['stop_loss']) if request.form.get('stop_loss') else None
            trade.take_profit = float(request.form['take_profit']) if request.form.get('take_profit') else None
            trade.hashtags = request.form.get('hashtags', '')

            # Si hay datos de salida, actualizar y recalcular PnL
            if request.form.get('exit_price'):
                trade.exit_price = float(request.form['exit_price'])
                trade.exit_time = request.form.get('exit_time', '')
                trade.exit_date = datetime.strptime(request.form['exit_date'], '%Y-%m-%d').date()

                if trade.trade_type == 'LONG':
                    trade.profit_loss = (trade.exit_price - trade.entry_price) * trade.quantity - trade.commission
                else:
                    trade.profit_loss = (trade.entry_price - trade.exit_price) * trade.quantity - trade.commission
            
            error_descriptions = request.form.getlist('error_description')
            error_category = request.form.getlist('error_category')
            error_severity = request.form.getlist('error_severity')
            trade.remove_errors()
            for i in range(len(error_descriptions)):
                trade.add_error(description=error_descriptions[i], user_id=trade.user_id, impact_level=error_severity[i], category=error_category[i])
            
            # Actualizar archivos multimedia si se subieron nuevos
            images = request.files.getlist('images')
            videos = request.files.getlist('videos')
            
            if images and any(img.filename for img in images):
                for path in save_uploaded_files(images, 'images', trade.id):
                    db.session.add(Media(
                        url=path,
                        trade_id=trade.id
                    ))
            
            if videos and any(vid.filename for vid in videos):
                for path in save_uploaded_files(videos, 'videos', trade.id):
                    db.session.add(Media(
                        url=path,
                        trade_id=trade.id
                    ))

            # Actualizar condiciones estratégicas (borrar y volver a insertar)
            condition_id = request.form.getlist('condition_id')
            condition_value = request.form.getlist('condition_value')
            trade.remove_conditions()
            for i in range(len(condition_id)):
                trade.add_condition(condition_id=condition_id[i], value=condition_value[i])
        

            # Descargar velas con Yahoo Finance
            '''
            today = trade.exit_date if trade.exit_date else date.today()
            one_year_ago = trade.entry_date - timedelta(days=365)
            week_ago = trade.entry_date - timedelta(days=5)
            symbol = trade.symbol
            download_candles(db=db,
                            symbol=symbol,
                            config=[
                                {'timeframe': '1d', 'start':one_year_ago, 'end':today},
                                {'timeframe': '1m', 'start': week_ago, 'end': datetime.combine(today, time(23, 59, 59)) },
                            ])
            '''
            db.session.commit()
            flash('Trade actualizado correctamente', 'success')
            return redirect(url_for('journal_pages.journal'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el trade: {str(e)}', 'error')

    strategies = Strategy.query.all()
    errors = Error.query.filter_by(is_active=True).all()

    return render_template(template_name_or_list='trade/create.html', trade=trade.to_dict(exclude=['trades', 'trade'], force_dollars=True), strategies=strategies, errors=errors, date=date)

@journal_pages.route(rule='/delete/<int:trade_id>', methods=['POST'])
@login_required
def delete_trade(trade_id) -> Response:
    trade: Trade = Trade.query.get_or_404(trade_id)

    if trade.user_id != current_user.id:
        abort(403)

    try:
        db.session.delete(trade)
        db.session.commit()

        # Eliminar archivos multimedia del sistema
        trade_path = os.path.join(UPLOAD_FOLDER, str(trade.id))
        if os.path.exists(trade_path):
            import shutil
            shutil.rmtree(trade_path)

        flash('Trade eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el trade: {str(e)}', 'error')

    return redirect(url_for('journal_pages.journal'))


journal_bp = Blueprint(name='journal_endpoints', import_name=__name__)

@journal_bp.route(rule='/')
@login_required
def journal_api() -> str:
    # Obtener datos del calendario
    balances: list[AccountBalance] = AccountBalance.query.filter(AccountBalance.user_id==current_user.id).order_by(AccountBalance.date).all()
    calendar_data: dict = {}
    for balance in balances:
        calendar_data[balance.date.strftime('%Y-%m-%d')] = {
            'return': balance.daily_return,
            'balance': balance.balance
        }
    
    selected_date: str | None = request.args.get('date')
    trades: list[Trade] = []
    if selected_date:
        trades = Trade.query.filter(Trade.exit_date == selected_date, Trade.user_id==current_user.id).all()
    
    return render_template(template_name_or_list='trade/journal.html', calendar_data=calendar_data, 
                         trades=trades, selected_date=selected_date)

@journal_bp.route(rule='/trades/<date>/month')
@login_required
def month_trades(date:str) -> Response:
    date: datetime = datetime.strptime(date, '%Y-%m-%d')
    start = datetime(date.year, date.month, 1).date()
    end = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
    trades: list[Trade] = Trade.query.filter((start <= Trade.exit_date) & (Trade.exit_date < end) & (Trade.user_id==current_user.id)).all()
    return jsonify([t.to_dict(exclude=['strategy', 'errors', 'conditions', 'transactions'],equity=True) for t in trades])

@journal_bp.route(rule='/add', methods=['GET', 'POST'])
@login_required
def add_trade_api() -> Response | str:

    if request.method == 'POST':
        symbol = request.form['symbol']

        # try:
        # Crear el trade básico primero
        trade = Trade(
            symbol=symbol,
            company_name=request.form.get('company_name', ''),
            balance=request.form.get('balance', 0.0),
            trade_type=request.form['trade_type'],
            description=request.form.get('description', ''),
            why_profitable=request.form.get('why_profitable', ''),
            influencing_factors=request.form.get('influencing_factors', ''),
            strategy_id=request.form.get('strategy_id') if request.form.get('strategy_id') else None,
            stop_loss=float(request.form['stop_loss']) if request.form.get('stop_loss') else None,
            take_profit=float(request.form['take_profit']) if request.form.get('take_profit') else None,
            hashtags=request.form.get('hashtags', ''),
            user_id=current_user.id
        )
        
        db.session.add(trade)
        db.session.flush([trade])

        transaction_date: list[str] = request.form.getlist('transaction_date')
        transaction_time: list[str] = request.form.getlist('transaction_time')
        transaction_timezone: list[str] = request.form.getlist('transaction_timezone')
        transaction_price: list[str] = request.form.getlist('transaction_price')
        transaction_type: list[str] = request.form.getlist('transaction_type')
        transaction_quantity: list[str] = request.form.getlist('transaction_quantity')
        transaction_commission: list[str] = request.form.getlist('transaction_commission')
        transaction_ecn_fee: list[str] = request.form.getlist('transaction_ecn_fee')
        transaction_locates: list[str] = request.form.getlist('transaction_locates')
        for i in range(len(transaction_date)):
            trade.add_transaction(date=datetime.strptime(transaction_date[i], '%Y-%m-%d').date(), 
                                  price=float(transaction_price[i]), 
                                time=localToUtc(date=transaction_date[i], time=transaction_time[i], tz=transaction_timezone[i] if len(transaction_timezone) > 0 else 'Europe/Madrid', mode='time') if len(transaction_timezone) > 0 else transaction_time[i], 
                                quantity=float(transaction_quantity[i]), 
                                commission=float(transaction_commission[i]),
                                ecn_fee=float(transaction_ecn_fee[i]),
                                locates=float(transaction_locates[i]), type=transaction_type[i])

        error_id: list[str] = request.form.getlist('error_id')
        error_descriptions: list[str] = request.form.getlist('error_description')
        error_category: list[str] = request.form.getlist('error_category')
        error_severity: list[str] = request.form.getlist('error_severity')
        for i in range(len(error_id)):
            print(dict(id=error_id[i], description=error_descriptions[i], impact_level=error_severity[i], category=error_category[i]))
            trade.add_error(id=error_id[i], description=error_descriptions[i], user_id=current_user.id, impact_level=error_severity[i], category=error_category[i])
        
        # Guardar archivos multimedia
        images: list[FileStorage] = request.files.getlist('images')
        videos: list[FileStorage] = request.files.getlist('videos')
        
        if images and any(img.filename for img in images):
            for path in save_uploaded_files(images, 'images', trade.id):
                db.session.add(Media(
                    url=path,
                    trade_id=trade.id
                ))
        
        if videos and any(vid.filename for vid in videos):
            for path in save_uploaded_files(videos, 'videos', trade.id):
                db.session.add(Media(
                    url=path,
                    trade_id=trade.id
                ))
        
        # Guardar condiciones de estrategia cumplidas
        condition_id = request.form.getlist('condition_id')
        condition_value = request.form.getlist('condition_value')
        for i in range(len(condition_id)):
            trade.add_condition(condition_id=condition_id[i], value=condition_value[i])
    
        today = trade.entry_date or date.today()
        one_year_ago = today - timedelta(days=365)
        week_ago = today - timedelta(days=5)
        while (datetime.now() - week_ago).days >= 30:
            week_ago = week_ago + timedelta(days=1)
        # Descargar velas con Yahoo Finance
        download_candles(db=db,
                         symbol=symbol,
                         config=[
                             {'timeframe': '1d', 'start':one_year_ago, 'end':today},
                             {'timeframe': '1m', 'start': week_ago, 'end': datetime.combine(today, time(23, 59, 59)) },
                         ])
        
        db.session.commit()
        flash('Trade registrado exitosamente!', 'success')
        return redirect(url_for('journal_pages.journal'))
        
        # except Exception as e:
        #     db.session.rollback()
        #     flash(f'Error al registrar el trade: {str(e)}', 'error')
    
    # GET request - mostrar formulario
    strategies = Strategy.query.all()
    errors = Error.query.filter_by(is_active=True).all()
    
    return render_template('trade/create.html', strategies=strategies, errors=errors, json_strategies=[strat.to_dict(exclude=['trades']) for strat in strategies], date=date)

@journal_bp.route(rule='/edit/<int:trade_id>', methods=['GET', 'POST'])
@login_required
def edit_trade_api(trade_id) -> Response | str:
    trade: Trade = Trade.query.get_or_404(trade_id)

    if trade.user_id != current_user.id:
        abort(403)
    
    if request.method == 'POST':
        try:
            trade.entry_date = datetime.strptime(request.form['entry_date'], '%Y-%m-%d').date()
            trade.symbol = request.form['symbol'].upper()
            trade.company_name = request.form.get('company_name', '')
            trade.entry_price = float(request.form['entry_price'])
            trade.entry_time = request.form.get('entry_time', '')
            trade.quantity = float(request.form['quantity'])
            trade.trade_type = request.form['trade_type']
            trade.description = request.form.get('description', '').replace('\n', ' ').replace('\r', ' ').replace('\t', '    ')
            trade.why_profitable = request.form.get('why_profitable', '')
            trade.influencing_factors = request.form.get('influencing_factors', '')
            trade.strategy_id = request.form.get('strategy_id') if request.form.get('strategy_id') else None
            trade.stop_loss = float(request.form['stop_loss']) if request.form.get('stop_loss') else None
            trade.take_profit = float(request.form['take_profit']) if request.form.get('take_profit') else None
            trade.hashtags = request.form.get('hashtags', '')

            # Si hay datos de salida, actualizar y recalcular PnL
            if request.form.get('exit_price'):
                trade.exit_price = float(request.form['exit_price'])
                trade.exit_time = request.form.get('exit_time', '')
                trade.exit_date = datetime.strptime(request.form['exit_date'], '%Y-%m-%d').date()

                if trade.trade_type == 'LONG':
                    trade.profit_loss = (trade.exit_price - trade.entry_price) * trade.quantity - trade.commission
                else:
                    trade.profit_loss = (trade.entry_price - trade.exit_price) * trade.quantity - trade.commission
            
            error_descriptions = request.form.getlist('error_description')
            error_category = request.form.getlist('error_category')
            error_severity = request.form.getlist('error_severity')
            trade.remove_errors()
            for i in range(len(error_descriptions)):
                trade.add_error(description=error_descriptions[i], user_id=trade.user_id, impact_level=error_severity[i], category=error_category[i])
            
            # Actualizar archivos multimedia si se subieron nuevos
            images = request.files.getlist('images')
            videos = request.files.getlist('videos')
            
            if images and any(img.filename for img in images):
                for path in save_uploaded_files(images, 'images', trade.id):
                    db.session.add(Media(
                        url=path,
                        trade_id=trade.id
                    ))
            
            if videos and any(vid.filename for vid in videos):
                for path in save_uploaded_files(videos, 'videos', trade.id):
                    db.session.add(Media(
                        url=path,
                        trade_id=trade.id
                    ))

            # Actualizar condiciones estratégicas (borrar y volver a insertar)
            condition_id = request.form.getlist('condition_id')
            condition_value = request.form.getlist('condition_value')
            trade.remove_conditions()
            for i in range(len(condition_id)):
                trade.add_condition(condition_id=condition_id[i], value=condition_value[i])
        

            # Descargar velas con Yahoo Finance
            today = trade.exit_date if trade.exit_date else date.today()
            one_year_ago = trade.entry_date - timedelta(days=365)
            week_ago = trade.entry_date - timedelta(days=5)
            symbol = trade.symbol
            download_candles(db=db,
                            symbol=symbol,
                            config=[
                                {'timeframe': '1d', 'start':one_year_ago, 'end':today},
                                {'timeframe': '1m', 'start': week_ago, 'end': datetime.combine(today, time(23, 59, 59)) },
                            ])

            db.session.commit()
            flash('Trade actualizado correctamente', 'success')
            return redirect(url_for('journal_pages.journal'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el trade: {str(e)}', 'error')

    strategies = Strategy.query.all()
    errors = Error.query.filter_by(is_active=True).all()

    return render_template('trade/create.html', trade=trade, strategies=strategies, errors=errors, json_strategies=[strat.to_dict() for strat in strategies], date=date)

@journal_bp.route(rule='/delete/<int:trade_id>', methods=['POST'])
@login_required
def delete_trade_api(trade_id) -> Response:
    trade: Trade = Trade.query.get_or_404(trade_id)

    if trade.user_id != current_user.id:
        abort(403)

    try:
        db.session.delete(trade)
        db.session.commit()

        # Eliminar archivos multimedia del sistema
        trade_path = os.path.join(UPLOAD_FOLDER, str(trade.id))
        if os.path.exists(trade_path):
            import shutil
            shutil.rmtree(trade_path)

        flash('Trade eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el trade: {str(e)}', 'error')

    return redirect(url_for('journal_pages.journal'))

@journal_bp.route(rule='/complete-performance')
@login_required
def globalPerformance() -> str:
    # Obtener filtros
    start = request.args.get('start', type=str)
    end = request.args.get('end', type=str)
    strategy_id = request.args.get('strategy', type=int)
    asset_symbol = request.args.get('symbol', type=str)
    watchlist_id = request.args.get('watchlist', type=int)
    limit = request.args.get('limit', type=int)
    
    # Construir query base
    base_query = Trade.query.filter(Trade.user_id==current_user.id)
    
    if watchlist_id:
        base_query = base_query.join(
            WatchlistEntry,
            and_(
                Trade.symbol == WatchlistEntry.symbol,
                Trade.entry_date >= WatchlistEntry.date,
                Trade.entry_date <= WatchlistEntry.date_exit
            )
        ).filter(WatchlistEntry.watchlist_id == watchlist_id).distinct().all()
        
    if strategy_id:
        base_query = base_query.filter(Trade.strategy_id == strategy_id)
        
    if asset_symbol:
        base_query = base_query.filter(Trade.symbol == asset_symbol)
        
    if limit:
        base_query = base_query.limit(limit=limit)
    
    # Aplicar filtros de fecha
    if start:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        base_query = base_query.filter(Trade.entry_date >= start_date)
    if end:
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        base_query = base_query.filter(Trade.entry_date <= end_date)
    
    # ===== ESTADÍSTICAS GENERALES =====
    total_trades = base_query.count()
    winning_trades = base_query.filter(Trade.profit_loss > 0).count()
    losing_trades = base_query.filter(Trade.profit_loss < 0).count()
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # P&L y métricas básicas
    total_pnl = base_query.with_entities(func.sum(Trade.profit_loss)).scalar() or 0
    avg_win = base_query.filter(Trade.profit_loss > 0).with_entities(func.avg(Trade.profit_loss)).scalar() or 0
    avg_loss = base_query.filter(Trade.profit_loss < 0).with_entities(func.avg(Trade.profit_loss)).scalar() or 0
    avg_trade = total_pnl / total_trades if total_trades > 0 else 0
    risk_reward = avg_win / abs(avg_loss)
    
    # Profit factor
    total_wins = base_query.filter(Trade.profit_loss > 0).with_entities(func.sum(Trade.profit_loss)).scalar() or 0
    total_losses = abs(base_query.filter(Trade.profit_loss < 0).with_entities(func.sum(Trade.profit_loss)).scalar() or 0)
    profit_factor = total_wins / total_losses if total_losses > 0 else 0
    
    # Trades del mes actual
    current_month = date.today().replace(day=1)
    trades_this_month = Trade.query.filter(Trade.entry_date >= current_month, Trade.user_id==current_user.id).count()
    
    # Cambio P&L vs mes anterior
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    pnl_last_month = Trade.query.filter(
        Trade.exit_date >= last_month, Trade.exit_date < current_month, Trade.user_id==current_user.id
    ).with_entities(func.sum(Trade.profit_loss)).scalar() or 0
    
    pnl_change = ((total_pnl - pnl_last_month) / abs(pnl_last_month) * 100) if pnl_last_month != 0 else 0
    
    # ===== CÁLCULOS AVANZADOS =====
    
    # Obtener todos los trades para cálculos complejos
    all_trades = base_query.order_by(Trade.entry_date).all()
    
    # Calcular Sharpe Ratio
    if len(all_trades) > 1:
        returns = [trade.profit_loss for trade in all_trades]
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        sharpe_ratio = (avg_return / std_return) if std_return != 0 else 0
    else:
        sharpe_ratio = 0
    
    # Calcular Maximum Drawdown
    max_drawdown = calculate_max_drawdown(all_trades)
    
    # ===== MEJORES Y PEORES TRADES =====
    best_trades = base_query.order_by(desc(Trade.profit_loss)).limit(5).all()
    worst_trades = base_query.order_by(Trade.profit_loss).limit(5).all()
    
    # ===== ANÁLISIS POR ESTRATEGIA =====
    strategy_stats = []
    strategies_query = db.session.query(
        Strategy.id,
        Strategy.name,
        Strategy.description,
        func.count(Trade.id).label('total_trades'),
        func.sum(Trade.profit_loss).label('total_pnl'),
        func.avg(Trade.profit_loss).label('avg_pnl'),
        func.count(func.nullif(Trade.profit_loss > 0, False)).label('wins'),
        func.sum(case((Trade.profit_loss > 0, Trade.profit_loss), else_=0)).label('total_wins'),
        func.sum(case((Trade.profit_loss < 0, Trade.profit_loss), else_=0)).label('total_losses')
    ).filter(Strategy.user_id==current_user.id).join(Trade).group_by(Strategy.id)
    
    if strategy_id:
        strategies_query = strategies_query.filter(Strategy.id == strategy_id)
    
    for strategy in strategies_query.all():
        win_rate_strategy = (strategy.wins / strategy.total_trades * 100) if strategy.total_trades > 0 else 0
        profit_factor_strategy = abs(strategy.total_wins / strategy.total_losses) if strategy.total_losses < 0 else 0
        
        # Calcular drawdown para esta estrategia
        strategy_trades = [t for t in all_trades if t.strategy_id == strategy.id]
        strategy_drawdown = calculate_max_drawdown(strategy_trades)
        
        strategy_stats.append({
            'id': strategy.id,
            'name': strategy.name,
            'description': strategy.description,
            'total_trades': strategy.total_trades,
            'win_rate': win_rate_strategy,
            'total_pnl': strategy.total_pnl or 0,
            'avg_pnl': strategy.avg_pnl or 0,
            'profit_factor': profit_factor_strategy,
            'max_drawdown': strategy_drawdown
        })
    
    # ===== ANÁLISIS POR WATCHLIST =====
    watchlist_stats = []
    watchlists: list[Watchlist] = Watchlist.query.filter(Watchlist.user_id==current_user.id).all()
    
    for watchlist in watchlists:
        # Obtener símbolos de esta watchlist
        symbols = [entry.symbol for entry in watchlist.entries]
        if not symbols:
            continue
            
        watchlist_trades = base_query.filter(Trade.symbol.in_(symbols)).all()
        if not watchlist_trades:
            continue
            
        total_trades_wl = len(watchlist_trades)
        winning_trades_wl = len([t for t in watchlist_trades if t.profit_loss > 0])
        total_pnl_wl = sum(t.profit_loss for t in watchlist_trades)
        
        # Mejor símbolo de la watchlist
        symbol_performance = defaultdict(float)
        for trade in watchlist_trades:
            symbol_performance[trade.symbol] += trade.profit_loss
        
        best_symbol = max(symbol_performance.items(), key=lambda x: x[1]) if symbol_performance else ('', 0)
        
        watchlist_stats.append({
            'name': watchlist.name,
            'symbol_count': len(symbols),
            'total_trades': total_trades_wl,
            'win_rate': (winning_trades_wl / total_trades_wl * 100) if total_trades_wl > 0 else 0,
            'total_pnl': total_pnl_wl,
            'best_symbol': best_symbol[0],
            'best_symbol_pnl': best_symbol[1]
        })
    
    # ===== ANÁLISIS MENSUAL =====
    monthly_stats = []
    monthly_data = db.session.query(
        extract('year', Trade.exit_date).label('year'),
        extract('month', Trade.exit_date).label('month'),
        func.sum(Trade.profit_loss).label('pnl'),
        func.count(Trade.id).label('trades')
    ).filter(Trade.user_id==current_user.id).group_by(
        extract('year', Trade.exit_date),
        extract('month', Trade.exit_date)
    ).order_by(
        extract('year', Trade.exit_date),
        extract('month', Trade.exit_date)
    ).all()
    
    month_names = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                   'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    for month_data in monthly_data[-12:]:  # Últimos 12 meses
        monthly_stats.append({
            'year': int(month_data.year),
            'month': int(month_data.month),
            'month_name': month_names[int(month_data.month)],
            'pnl': month_data.pnl or 0,
            'trades': month_data.trades
        })
    
    # ===== ANÁLISIS POR SÍMBOLO =====
    symbol_data = db.session.query(
        Trade.symbol,
        func.count(Trade.id).label('trades'),
        func.sum(Trade.profit_loss).label('pnl'),
        func.count(func.nullif(Trade.profit_loss > 0, False)).label('wins')
    ).filter(Trade.user_id==current_user.id).group_by(Trade.symbol).all()
    
    symbol_stats = []
    for symbol in symbol_data:
        win_rate_symbol = (symbol.wins / symbol.trades * 100) if symbol.trades > 0 else 0
        symbol_stats.append({
            'symbol': symbol.symbol,
            'trades': symbol.trades,
            'win_rate': win_rate_symbol,
            'pnl': symbol.pnl or 0
        })
    
    # Top y worst performers
    top_symbols = sorted(symbol_stats, key=lambda x: x['pnl'], reverse=True)[:10]
    worst_symbols = sorted(symbol_stats, key=lambda x: x['pnl'])[:10]
    
    # ===== ANÁLISIS DE ERRORES =====
    error_stats = []
    errors_query = db.session.query(
        Error.id,
        Error.description,
        Error.category,
        func.count(trade_errors.c.trade_id).label('frequency'),
        func.max(Trade.exit_date).label('last_occurrence')
    ).filter(Error.user_id==current_user.id).join(trade_errors, trade_errors.c.error_id == Error.id) \
    .join(Trade, Trade.id == trade_errors.c.trade_id).group_by(Error.id).all()
    
    for error in errors_query:
        # Calcular impacto promedio y total
        error_trades = db.session.query(Trade).filter(Trade.user_id==current_user.id).join(trade_errors).filter(
            trade_errors.c.error_id == error.id
        ).all()
        
        if error_trades:
            avg_impact = sum(abs(t.profit_loss) for t in error_trades if t.profit_loss < 0) / len([t for t in error_trades if t.profit_loss < 0]) \
                        if len([t for t in error_trades if t.profit_loss < 0]) > 0 else 0.0
            total_loss = sum(t.profit_loss for t in error_trades if t.profit_loss < 0)
        else:
            avg_impact = 0
            total_loss = 0
            
        error_stats.append({
            'description': error.description,
            'category': error.category,
            'frequency': error.frequency,
            'avg_impact': avg_impact,
            'total_loss': abs(total_loss),
            'last_occurrence': error.last_occurrence
        })
    
    # Ordenar por frecuencia
    error_stats.sort(key=lambda x: x['frequency'], reverse=True)
    
    # ===== DATOS PARA GRÁFICOS =====
    # Balance histórico
    balances = AccountBalance.query.filter(AccountBalance.user_id==current_user.id).order_by(AccountBalance.date).all()
    balance_data = [{'date': b.date.strftime('%Y-%m-%d'), 'balance': float(b.balance)} for b in balances]
    
    # ===== OBTENER ESTRATEGIAS PARA FILTROS =====
    strategies = Strategy.query.filter(Strategy.user_id==current_user.id).all()
    
    # ===== COMPILAR ESTADÍSTICAS =====
    stats = {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': round(win_rate, 2),
        'total_pnl': round(total_pnl, 2),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'avg_trade': round(avg_trade, 2),
        'risk_reward': round(risk_reward, 2),
        'profit_factor': round(profit_factor, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'max_drawdown': round(max_drawdown, 2),
        'trades_this_month': trades_this_month,
        'pnl_change': round(pnl_change, 2),
        'best_trades': best_trades,
        'worst_trades': worst_trades,
        'strategy_stats': strategy_stats,
        'watchlist_stats': watchlist_stats,
        'monthly_stats': monthly_stats,
        'top_symbols': top_symbols,
        'worst_symbols': worst_symbols,
        'error_stats': error_stats,
        'balances': balance_data
    }
    
    return render_template('trade/performance-global.html', stats=stats, strategies=strategies)

@journal_bp.route(rule='/performance')
@login_required
def performance_api() -> str:
    # ===== OBTENER FILTROS =====
    start = request.args.get('start', type=str)
    end = request.args.get('end', type=str)
    strategy_id = request.args.get('strategy', type=int)
    asset_symbol = request.args.get('symbol', type=str)
    watchlist_id = request.args.get('watchlist', type=int)
    limit = request.args.get('limit', type=int)
    side = request.args.get('side', type=str)  # LONG or SHORT
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # ===== CONSTRUIR QUERY BASE =====
    base_query = Trade.query.filter(Trade.user_id == current_user.id)
    
    # Filtro por watchlist
    if watchlist_id:
        base_query = base_query.join(
            WatchlistEntry,
            and_(
                Trade.symbol == WatchlistEntry.symbol,
                Trade.entry_date >= WatchlistEntry.date,
                Trade.entry_date <= WatchlistEntry.date_exit
            )
        ).filter(WatchlistEntry.watchlist_id == watchlist_id)
    
    # Filtros adicionales
    if strategy_id:
        base_query = base_query.filter(Trade.strategy_id == strategy_id)
    if asset_symbol not in ['None', '', None]:
        base_query = base_query.filter(Trade.symbol == asset_symbol)
    if side in ['LONG', 'SHORT']:
        base_query = base_query.filter(Trade.trade_type == side.upper())
    
    # Filtros de fecha
    start = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d') if not start else start
    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    base_query = base_query.filter(Trade.entry_date >= start_date)

    if end:
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        base_query = base_query.filter(or_(Trade.entry_date <= end_date, Trade.entry_date == None)) # TODO: And if it is a swing trade?
    else:
        end = base_query.with_entities(func.max(Trade.entry_date)).scalar().strftime('%Y-%m-%d')
    
    # Aplicar límite
    if limit:
        base_query = base_query.limit(limit)
    
    # Get data
    all_trades = base_query.order_by(Trade.entry_date).distinct().all()

    # Calculate statistics and charts data
    stats_object = TradePerformance(data=all_trades, show_r=current_user.settings.show_r)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    net_stats, gross_stats, net_charts, gross_charts = loop.run_until_complete(
        asyncio.gather(
            deepcopy(stats_object).getStats(gross=False),
            deepcopy(stats_object).getStats(gross=True),
            deepcopy(stats_object).getCharts(gross=False),
            deepcopy(stats_object).getCharts(gross=True)
        )
    )
    loop.close()
        
    stats = { 'net': net_stats, 'gross': gross_stats }
    charts = { 'net': net_charts, 'gross': gross_charts }
    
    return jsonify(stats=stats, charts=charts)

@journal_bp.route(rule='/import', methods=['POST'])
@login_required
def import_trades():
    """
    Endpoint para importar CSV.
    
    Request:
        - file: Archivo CSV (multipart/form-data)
        - dry_run: true/false (opcional, default: false)
    
    Response:
        {
            "success": true,
            "stats": {...}
        }
    """
    
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authorized"}), 401
    
    # Validar archivo
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file: FileStorage = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    if not any(el in file.filename.lower().split('.')[-1] for el in ['csv', 'xls', 'xlsx']):
        return jsonify({"error": "Only CSV or XLSX files are allowed"}), 400
    
    # Guardar archivo temporalmente
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    temp_path = os.path.join(UPLOAD_FOLDER, f"{timestamp}_{filename}")
    file.save(temp_path)
    
    try:
        # Importar
        dry_run = request.form.get(key='dry_run', default='false').lower() == 'true'
        timezone = request.form.get(key='transaction_timezone', default='Europe/Madrid')

        importer = CSVImporter(current_app=current_app, trade_model=Trade, 
                               transaction_model=Transaction, user_id=current_user.id)
        
        stats, loged_trades = importer.import_from_file(file_path=temp_path, dry_run=dry_run)

        downloaded: dict[str, list] = {}
        for trade in loged_trades:
            db.session.add(instance=trade)
            db.session.flush()
            
            for transaction in trade.transactions:
                transaction.trade_id = trade.id
                transaction.time = localToUtc(date=transaction.date, time=transaction.time, tz=timezone if len(timezone) > 0 else 'Europe/Madrid', mode='time') if len(timezone) > 0 else transaction.time
            '''
            for transaction in transactions:
                trade.add_transaction(date=datetime.strptime(transaction.date, '%Y-%m-%d').date(), 
                                    price=float(transaction.price), 
                                    time=localToUtc(date=transaction.date, time=transaction.time, tz=timezone if len(timezone) > 0 else 'Europe/Madrid', mode='time') if len(timezone) > 0 else transaction.time, 
                                    quantity=float(transaction.quantity), 
                                    commission=float(transaction.commission), type=transaction.type)
            '''
            today = trade.entry_date or date.today()
            one_year_ago = today - timedelta(days=365)
            week_ago = datetime.combine(today - timedelta(days=5), time(0, 0, 0))
            while (datetime.now() - week_ago).days >= 30:
                week_ago = datetime.combine(week_ago + timedelta(days=1), time(0, 0, 0))

            # Descargar velas con Yahoo Finance solo si no se han descargado ya para este símbolo y rango
            if trade.symbol not in downloaded or [one_year_ago, today] not in downloaded[trade.symbol]['daily'] or [week_ago, datetime.combine(today, time(23, 59, 59))] not in downloaded[trade.symbol]['minute']:
                download_candles(db=db,
                                symbol=trade.symbol,
                                config=[
                                    {'timeframe': '1d', 'start':one_year_ago, 'end':today},
                                    {'timeframe': '1m', 'start': week_ago, 'end': datetime.combine(today, time(23, 59, 59)) },
                                ])
                if trade.symbol not in downloaded:
                    downloaded[trade.symbol] = {'daily': [[one_year_ago, today]], 'minute': [[week_ago, datetime.combine(today, time(23, 59, 59))]]}
                else:
                    downloaded[trade.symbol]['daily'].append([one_year_ago, today])
                    downloaded[trade.symbol]['minute'].append([week_ago, datetime.combine(today, time(23, 59, 59))])
                
        if not dry_run:
            db.session.commit()
            stats.success = True
        else:
            db.session.rollback()
            stats.success = False
            stats.errors.append("DRY RUN - Changes are not saved to the database.")
            
        # Log del resultado
        if stats.success:
            current_app.logger.info(
                f"Import successful - User: {current_user.id}, File: {filename}, Trades: {stats.trades_created}"
            )
        else:
            current_app.logger.warning(
                f"Import failed - User: {current_user.id}, File: {filename}, Errors: {len(stats.errors)}"
            )
        
        return jsonify({
            "success": stats.success,
            "message": "Importación completada" if stats.success else "Importación fallida",
            "stats": {
                "total_executions": stats.total_executions,
                "trades_created": stats.trades_created,
                "closed_trades": stats.closed_trades,
                "open_trades": stats.open_trades,
                "transactions_created": stats.transactions_created,
                "errors": stats.errors
            }
        }), 200 if stats.success else 400
    
    except FileNotFoundError as e:
        current_app.logger.error(f"File not found: {e}")
        return jsonify({"error": "Archivo no encontrado"}), 404
    
    except ValueError as e:
        current_app.logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        current_app.logger.error(f"Import error: {e}", exc_info=True)
        return jsonify({
            "error": "Error interno del servidor",
            "details": str(e) if current_app.debug else None
        }), 500
    
    finally:
        # Limpiar archivo temporal
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                current_app.logger.warning(f"Could not delete temp file: {e}")

@journal_bp.route(rule='/import/batch', methods=['POST'])
@login_required
def import_batch_trades():
    """
    POST /api/trades/import/batch
    
    Importa múltiples archivos CSV en una sola petición.
    
    Form Data:
        - files[]: Array de archivos CSV (required)
        - dry_run: bool (optional, default: false)
    
    Returns:
        JSON con estadísticas de cada archivo
    """
    
    if not current_user.is_authenticated:
        return jsonify({"error": "No autorizado"}), 401
    
    # Validar archivos
    if 'files[]' not in request.files:
        return jsonify({"error": "No se proporcionaron archivos"}), 400
    
    files = request.files.getlist('files[]')
    
    if not files or len(files) == 0:
        return jsonify({"error": "Lista de archivos vacía"}), 400
    
    # Validar que todos sean CSV
    for file in files:
        if not file.filename.lower().endswith('.csv'):
            return jsonify({
                "error": f"Archivo inválido: {file.filename}. Solo CSV permitidos"
            }), 400
    
    # Parámetros comunes
    dry_run: bool = request.form.get('dry_run', 'false').lower() == 'true'
    
    results: dict = {}
    temp_files: list[str] = []
    
    try:
        # Procesar cada archivo
        for file in files:
            filename: str = secure_filename(filename=file.filename)
            timestamp: str = datetime.now().strftime(format='%Y%m%d_%H%M%S')
            temp_path: str = os.path.join(UPLOAD_FOLDER, f"{timestamp}_{filename}")
            
            temp_files.append(temp_path)
            file.save(dst=temp_path)
            
            try:
                importer = CSVImporter(current_app=current_app, trade_model=Trade, 
                               transaction_model=Transaction, user_id=current_user.id, db=db)
                
                stats: ImportStats = importer.import_from_csv(csv_path=temp_path, dry_run=dry_run)
                
                results[filename] = {
                    "success": stats.success,
                    "stats": {
                        "total_executions": stats.total_executions,
                        "trades_created": stats.trades_created,
                        "closed_trades": stats.closed_trades,
                        "open_trades": stats.open_trades,
                        "transactions_created": stats.transactions_created,
                        "errors": stats.errors
                    }
                }
                
            except Exception as e:
                results[filename] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Resumen total
        total_success: int = sum(1 for r in results.values() if r.get('success', False))
        total_trades: int = sum(
            r.get('stats', {}).get('trades_created', 0) 
            for r in results.values()
        )
        
        return jsonify({
            "success": total_success == len(files),
            "summary": {
                "total_files": len(files),
                "successful": total_success,
                "failed": len(files) - total_success,
                "total_trades_created": total_trades
            },
            "results": results
        })
        
    finally:
        # Limpiar archivos temporales
        for temp_path in temp_files:
            if os.path.exists(path=temp_path):
                try:
                    os.remove(path=temp_path)
                except Exception as e:
                    current_app.logger.warning(f"Could not delete temp file: {e}")

def get_balance_data() -> list[dict[str, Any]]:
    """Obtener datos de balance histórico"""
    balances = AccountBalance.query.filter(AccountBalance.user_id == current_user.id).order_by(AccountBalance.date).all()
    return [{'date': b.date.strftime('%Y-%m-%d'), 'balance': float(b.balance)} for b in balances]