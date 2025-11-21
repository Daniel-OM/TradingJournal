
import json
from datetime import date, datetime, timedelta
import asyncio
from copy import deepcopy

from sqlalchemy import func, or_
from flask import Blueprint, Response, render_template, request, flash, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user
from werkzeug.wrappers.response import Response

from ..models import db, Watchlist, WatchlistEntry, WatchlistCondition
from ..src.performance import WatchlistPerformance
from .utils import download_candles

watchlist_pages = Blueprint(name='watchlist_pages', import_name=__name__)

@watchlist_pages.route(rule='/')
@login_required
def watchlist() -> str:
    
    watchlists = Watchlist.query.filter(Watchlist.user_id == current_user.id).all()
    
    return render_template('watchlist/watchlist.html', watchlists=watchlists)

@watchlist_pages.route(rule='/<int:id>')
@login_required
def watchlist_detail(id) -> str:
    selected_date = datetime.strptime(request.args.get('date', date.today().strftime('%Y-%m-%d')), '%Y-%m-%d')
    watchlist_filter = request.args.get('watchlist', str(id))
    hashtag_filter = request.args.get('hashtag', '')
    
    query = WatchlistEntry.query.filter(
        (WatchlistEntry.date <= selected_date) & 
        ((WatchlistEntry.date_exit.is_(None)) | (selected_date <= WatchlistEntry.date_exit))
    ).join(Watchlist, Watchlist.id == WatchlistEntry.watchlist_id).filter(Watchlist.user_id == current_user.id)
    
    if watchlist_filter:
        query = query.filter(WatchlistEntry.watchlist_id == watchlist_filter)
    
    if hashtag_filter:
        query = query.filter(WatchlistEntry.hashtags.contains(hashtag_filter))
    
    entries = query.all()
    watchlists = Watchlist.query.filter(Watchlist.user_id == current_user.id).all()
    
    return render_template('watchlist/detail.html', entries=entries, watchlists=watchlists, 
                         selected_date=selected_date.strftime('%Y-%m-%d'), 
                         watchlist_filter=watchlist_filter, hashtag_filter=hashtag_filter)

@watchlist_pages.route(rule='/<int:id>/performance')
@login_required
def watchlist_performance(id) -> str:
    start = request.args.get('start', type=str)
    end = request.args.get('end', type=str)
    asset_symbol = request.args.get('symbol', type=str)
    atr = request.args.get('atr', type=int)
    limit = request.args.get('limit', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # ===== CONSTRUIR QUERY BASE =====
    watchlist = Watchlist.query.filter(Watchlist.id == id, Watchlist.user_id == current_user.id).first_or_404()
    base_query = WatchlistEntry.query.join(Watchlist, Watchlist.id == WatchlistEntry.watchlist_id) \
                                    .filter(WatchlistEntry.watchlist_id == id, Watchlist.user_id == current_user.id)
    
    # Filtros adicionales
    if asset_symbol not in ['None', '', None]:
        base_query = base_query.filter(WatchlistEntry.symbol == asset_symbol)
    if atr:
        base_query = base_query.filter(WatchlistEntry.atr == atr)
    
    # Filtros de fecha
    start = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d') if not start else start
    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    base_query = base_query.filter(WatchlistEntry.date >= start_date)

    if end:
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        base_query = base_query.filter(or_(WatchlistEntry.date_exit <= end_date, WatchlistEntry.date_exit == None))
    else:
        end = base_query.with_entities(func.max(WatchlistEntry.date_exit)).scalar()
        if end is not None: 
            end = end.strftime('%Y-%m-%d')
    
    # Aplicar límite
    if limit:
        base_query = base_query.limit(limit)
    
    # ===== OBTENER DATOS =====
    all_entries = base_query.order_by(WatchlistEntry.date).distinct().all()

    # ===== CALCULAR ESTADÍSTICAS =====
    stats_object = WatchlistPerformance(data=all_entries)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    gross_stats, gross_charts = loop.run_until_complete(
        asyncio.gather(
            deepcopy(stats_object).getStats(gross=True),
            deepcopy(stats_object).getCharts(gross=True)
        )
    )
    loop.close()

    stats = { 'net': gross_stats, 'gross': gross_stats }
    charts = { 'net': gross_charts, 'gross': gross_charts }
    
    return render_template('watchlist/performance.html', stats=stats, charts=charts, watchlist=watchlist,
                           start=start, end=end, asset_symbol=asset_symbol if asset_symbol else '', limit=limit)




@watchlist_pages.route(rule='/config', methods=['GET', 'POST'])
@login_required
def watchlist_configuration() -> Response | str:

    if request.method == 'POST':
        action = request.form.get('action')
        print(request.form)
        if action == 'add_watchlist':
            entry = Watchlist(
                name=request.form['name'],
                type=request.form['type'],
                description=request.form['description'],
                user_id=current_user.id
            )
            
            db.session.add(entry)
            db.session.flush([entry])

            # Procesar los niveles
            condition_name = request.form.getlist('condition_name')
            condition_description = request.form.getlist('condition_description')
            condition_score = request.form.getlist('condition_score')
            
            for i in range(len(condition_name)):
                entry.add_condition(name=condition_name[i], description=condition_description[i], score=float(condition_score[i]))

            db.session.commit()
            flash('Watchlist created successfully!', 'success')
        
        elif action == 'edit_watchlist':
            watchlist: Watchlist = Watchlist.query.get_or_404(request.form['watchlist_id'])
            if watchlist.user_id == current_user.id:
                watchlist.name = request.form['name']
                watchlist.type = request.form['type']
                watchlist.description = request.form['description']
                flash('Watchlist updated successfully!', 'success')
            else:
                flash('You are not authorized to update this watchlist', 'error')
        
        elif action == 'delete_watchlist':
            watchlist = Watchlist.query.get_or_404(request.form['watchlist_id'])
            if watchlist.user_id == current_user.id:
                db.session.delete(watchlist)
                flash('Watchlist deleted successfully!', 'info')
            else:
                flash('You are not authorized to delete this watchlist', 'error')
        
        elif action == 'add_scoring':
            watchlist = Watchlist.query.get_or_404(request.form['watchlist_id'])
            if watchlist.user_id != current_user.id:
                flash('You are not authorized to add coditions to this watchlist', 'error')
            else:
                criteria = WatchlistCondition(
                    watchlist_id=int(request.form['watchlist_id']),
                    name=request.form['condition_name'],
                    description=request.form['condition_description'],
                    score=float(request.form['score'])
                )
                db.session.add(criteria)
                flash('Scoring criteria added successfully!', 'success')
        
        elif action == 'edit_criteria':
            criteria: WatchlistCondition = WatchlistCondition.query.get_or_404(request.form['criteria_id'])
            watchlist = Watchlist.query.get_or_404(criteria.watchlist_id)
            if watchlist.user_id != current_user.id:
                flash('You are not authorized to add coditions to this watchlist', 'error')
            else:
                criteria.name = request.form['condition_name']
                criteria.description = request.form['condition_description']
                criteria.score = float(request.form['score'])
                flash('Scoring criteria updated successfully!', 'success')
        
        elif action == 'delete_criteria':
            criteria = WatchlistCondition.query.get_or_404(request.form['criteria_id'])
            watchlist = Watchlist.query.get_or_404(criteria.watchlist_id)
            if watchlist.user_id != current_user.id:
                flash('You are not authorized to delete coditions from this watchlist', 'error')
            else:
                db.session.delete(criteria)
                flash('Scoring criteria deleted successfully!', 'info')
        
        db.session.commit()
        return redirect(url_for('watchlist_pages.watchlist'))

    watchlists = Watchlist.query.all()
    return render_template('watchlist/create.html', date=date, watchlists=watchlists, json_watchlists=[s.to_dict() for s in watchlists])

@watchlist_pages.route(rule='/<int:id>/update', methods=['POST'])
@login_required
def update_watchlist(id) -> Response:
    """Actualizar un registro de la watchlist"""
    try:
        entry: WatchlistEntry = WatchlistEntry.query.get_or_404(id)

        if entry.watchlist.user_id != current_user.id:
            abort(403)
        
        # Actualizar campos del formulario
        entry.symbol = request.form.get('symbol', '').upper()
        entry.company_name = request.form.get('company_name', '')
        entry.score = float(request.form.get('score', 0.0))
        entry.atr = float(request.form.get('atr')) if request.form.get('atr') else None
        entry.price = float(request.form.get('price')) if request.form.get('price') else None
        entry.volume = float(request.form.get('volume')) if request.form.get('volume') else None
        entry.avg_volume = float(request.form.get('avg_volume')) if request.form.get('avg_volume') else None
        entry.market_cap = float(request.form.get('market_cap')) if request.form.get('market_cap') else None
        entry.float_shares = float(request.form.get('float_shares')) if request.form.get('float_shares') else None
        entry.per = float(request.form.get('per')) if request.form.get('per') else None
        entry.eps = float(request.form.get('eps')) if request.form.get('eps') else None
        entry.exchange = request.form['exchange'] if request.form.get('exchange') else None
        entry.sector = request.form['sector'] if request.form.get('sector') else None
        entry.industry = request.form['industry'] if request.form.get('industry') else None
        entry.country = request.form['country'] if request.form.get('country') else None
        entry.description = request.form.get('description', '')
        entry.negative_action = request.form.get('negative_action', '')
        entry.hashtags = request.form.get('hashtags', '')
        entry.risk_reward = request.form.get('risk_reward', '')
        entry.profit_target = float(request.form.get('profit_target')) if request.form.get('profit_target') else None
        entry.other_notes = request.form.get('other_notes', '')
        entry.strategy_id = int(request.form.get('strategy_id')) if request.form.get('strategy_id') else None
        
        db.session.commit()
        
        flash(f'Registro de {entry.symbol} actualizado exitosamente', 'success')
        return redirect(url_for('watchlist_pages.detail_watchlist_entry', id=entry.id))
        
    except ValueError as e:
        flash(f'Error en los datos ingresados: {str(e)}', 'error')
        return redirect(url_for('watchlist_pages.edit_watchlist_entry', id=id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar el registro: {str(e)}', 'error')
        return redirect(url_for('watchlist_pages.edit_watchlist_entry', id=id))

@watchlist_pages.route(rule='/entry/add', methods=['GET', 'POST'])
@login_required
def add_watchlist_entry() -> Response | str:

    if request.method == 'POST' and 'entry' in request.form:
        try:
            print('Data: ', request.form['entry'])
            entry_obj: WatchlistEntry = WatchlistEntry.from_dict(json.loads(request.form['entry']))
        except Exception as e:
            print("Error trying to convert watchlist entry form in watchlist: ", e)
            entry_obj = None
        watchlists = Watchlist.query.all()
        return render_template(template_name_or_list='watchlist_entry/create.html',
                               watchlist_id=getattr(entry_obj, 'watchlist_id', None),
                               date=date, watchlists=watchlists,
                               json_watchlists=[s.to_dict(exclude=['entries']) for s in watchlists],
                               entry=entry_obj)

    elif request.method == 'POST':

        entry = WatchlistEntry(
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            symbol=request.form['symbol'],
            company_name=request.form['company_name'],
            atr=float(request.form['atr']) if request.form['atr'] else None,
            volume=float(request.form['volume']) if request.form['volume'] else None,
            avg_volume=float(request.form['avg_volume']) if request.form['avg_volume'] else None,
            market_cap=float(request.form['market_cap']) if request.form['market_cap'] else None,
            float_shares=float(request.form['float_shares']) if request.form['float_shares'] else None,
            per=float(request.form['per']) if request.form['per'] else None,
            eps=float(request.form['eps']) if request.form['eps'] else None,
            exchange=request.form['exchange'] if request.form['exchange'] else None,
            sector=request.form['sector'] if request.form['sector'] else None,
            industry=request.form['industry'] if request.form['industry'] else None,
            country=request.form['country'] if request.form['country'] else None,
            price=float(request.form['price']) if request.form['price'] else None,
            score=float(request.form['score']) if request.form['score'] else None,
            description=request.form['description'],
            negative_action=request.form['negative_action'],
            watchlist_id=int(request.form['watchlist_id']) if request.form['watchlist_id'] else None,
            hashtags=request.form['hashtags'],
            risk_reward=request.form['risk_reward'],
            profit_target=float(request.form['profit_target']) if request.form['profit_target'] else None,
            other_notes=request.form['other_notes']
        )
        db.session.add(entry)
        db.session.flush([entry])  # Para obtener el ID

        # Procesar los niveles
        level_prices = request.form.getlist('level_price')
        level_impacts = request.form.getlist('level_impact')
        for i in range(len(level_prices)):
            entry.add_level(price=float(level_prices[i]), date=date.today(), impact_level=level_impacts[i])

        condition_ids = request.form.getlist('condition_id')
        condition_values = request.form.getlist('condition_value')
        for i in range(len(condition_ids)):
            if condition_ids[i] != '':
                entry.add_condition(condition_id=condition_ids[i], value=condition_values[i])

        one_year_ago = entry.date - timedelta(days=365)
        # Descargar velas con Yahoo Finance y sobreescribir las existentes
        download_candles(db=db,
                        symbol=entry.symbol,
                        config=[
                            {'timeframe': '1d', 'start':one_year_ago, 'end':entry.date},
                        ])
        
        db.session.commit()
        flash('Activo añadido a la watchlist exitosamente!', 'success')
        return redirect(url_for('watchlist_pages.watchlist_detail', id=entry.watchlist_id))
    
    watchlists = Watchlist.query.all()
    
    return render_template('watchlist_entry/create.html', 
                           watchlist_id=request.args.get('watchlist_id', None), 
                           date=date, watchlists=watchlists, 
                           json_watchlists=[s.to_dict(exclude=['entries']) for s in watchlists], 
                           entry=None)

@watchlist_pages.route(rule='/entry/<int:id>/detail')
@login_required
def detail_watchlist_entry(id) -> str | Response:
    """Vista detallada de un registro específico de la watchlist"""
    try:
        entry: WatchlistEntry = WatchlistEntry.query.get_or_404(id)

        if entry.watchlist.user_id != current_user.id:
            abort(403)
        
        # Obtener los niveles asociados si existen
        levels = entry.levels if hasattr(entry, 'levels') else []
        
        # Separar niveles por tipo si tienen esa propiedad
        resistance_levels = [level for level in levels if hasattr(level, 'level_type') and level.level_type == 'resistance']
        support_levels = [level for level in levels if hasattr(level, 'level_type') and level.level_type == 'support']
        
        # Procesar hashtags
        hashtags_list = []
        if entry.hashtags:
            hashtags_list = [tag.strip() for tag in entry.hashtags.split(',') if tag.strip()]
        
        return render_template('watchlist_entry/detail.html', 
                             entry=entry,
                             levels=levels,
                             resistance_levels=resistance_levels,
                             support_levels=support_levels,
                             hashtags_list=hashtags_list,
                             date=date)
                             
    except Exception as e:
        flash(f'Error al cargar el detalle: {str(e)}', 'error')
        return redirect(url_for('watchlist_pages.watchlist'))

@watchlist_pages.route(rule='/entry/<int:id>/remove', methods=['POST'])
@login_required
def delete_watchlist_entry(id):
    """Dar de baja un registro de la watchlist (agregar fecha de salida)"""
    try:
        entry: WatchlistEntry = WatchlistEntry.query.get_or_404(id)

        if entry.watchlist.user_id != current_user.id:
            abort(403)

        watchlist_id = entry.watchlist_id
        
        # Verificar que no esté ya dado de baja
        if entry.date_exit:
            flash(f'El activo {entry.symbol} ya está dado de baja desde {entry.date_exit.strftime("%d/%m/%Y")}', 'warning')
            return redirect(url_for('watchlist_pages.watchlist'))
        
        # Agregar fecha de salida
        entry.date_exit = date.today()
        download_candles(db=db,
                        symbol=entry.symbol,
                        config=[
                            {'timeframe': '1d', 'start': entry.date, 'end':entry.date_exit},
                        ])
        
        db.session.commit()
        
        flash(f'Activo {entry.symbol} dado de baja exitosamente', 'success')
        
        # Si la petición es AJAX, devolver JSON
        if request.headers.get('Content-Type') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({
                'success': True,
                'message': f'Activo {entry.symbol} dado de baja exitosamente',
                'exit_date': entry.date_exit.strftime("%d/%m/%Y")
            })
        
        return redirect(url_for('watchlist_pages.watchlist_detail', id=watchlist_id))
        
    except Exception as e:
        db.session.rollback()
        error_msg = f'Error al dar de baja el activo: {str(e)}'
        flash(error_msg, 'error')
        
        # Si la petición es AJAX, devolver error en JSON
        if request.headers.get('Content-Type') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({
                'success': False,
                'message': error_msg
            }), 500
        
        return redirect(url_for('watchlist_pages.watchlist'))

@watchlist_pages.route(rule='/entry/<int:id>/reactivate', methods=['POST'])
@login_required
def reactivate_watchlist_entry(id) -> Response:
    """Reactivar un registro de la watchlist (quitar fecha de salida)"""
    try:
        entry: WatchlistEntry = WatchlistEntry.query.get_or_404(id)

        if entry.watchlist.user_id != current_user.id:
            abort(403)
        
        # Verificar que esté dado de baja
        if not entry.date_exit:
            flash(f'El activo {entry.symbol} ya está activo', 'warning')
            return redirect(url_for('watchlist_pages.watchlist_detail', id=entry.id))
        
        # Quitar fecha de salida
        entry.date_exit = None
        
        db.session.commit()
        
        flash(f'Activo {entry.symbol} reactivado exitosamente', 'success')
        return redirect(url_for('watchlist_pages.watchlist_detail', id=entry.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al reactivar el activo: {str(e)}', 'error')
        return redirect(url_for('watchlist_pages.watchlist'))

@watchlist_pages.route(rule='/entry/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_watchlist_entry(id) -> Response | str:
    """Vista para editar un registro de la watchlist"""
    # try:

    if request.method == 'POST':
        
        entry: WatchlistEntry = WatchlistEntry.query.get_or_404(id)

        if entry.watchlist.user_id != current_user.id:
            abort(403)

        # Actualizar campos del formulario
        entry.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        entry.symbol = request.form.get('symbol', '').upper()
        entry.company_name = request.form.get('company_name', '')
        entry.score = float(request.form.get('score', 0.0))
        entry.atr = float(request.form.get('atr')) if request.form.get('atr') else None
        entry.price = float(request.form.get('price')) if request.form.get('price') else None
        entry.volume = float(request.form.get('volume')) if request.form.get('volume') else None
        entry.avg_volume = float(request.form.get('avg_volume')) if request.form.get('avg_volume') else None
        entry.market_cap = float(request.form.get('market_cap')) if request.form.get('market_cap') else None
        entry.float_shares = float(request.form.get('float_shares')) if request.form.get('float_shares') else None
        entry.per = float(request.form.get('per')) if request.form.get('per') else None
        entry.eps = float(request.form.get('eps')) if request.form.get('eps') else None
        entry.exchange = request.form['exchange'] if request.form.get('exchange') else None
        entry.sector = request.form['sector'] if request.form.get('sector') else None
        entry.industry = request.form['industry'] if request.form.get('industry') else None
        entry.country = request.form['country'] if request.form.get('country') else None
        entry.description = request.form.get('description', '')
        entry.negative_action = request.form.get('negative_action', '')
        entry.hashtags = request.form.get('hashtags', '')
        entry.risk_reward = request.form.get('risk_reward', '')
        entry.profit_target = float(request.form.get('profit_target')) if request.form.get('profit_target') else None
        entry.other_notes = request.form.get('other_notes', '')
        entry.watchlist_id = int(request.form.get('watchlist_id')) if request.form.get('watchlist_id') else None
        
        db.session.add(entry)
        db.session.flush([entry])  # Para obtener el ID
        
        # Procesar los niveles
        level_prices = request.form.getlist('level_price')
        level_impacts = request.form.getlist('level_impact')
        entry.remove_levels()
        for i in range(len(level_prices)):
            entry.add_level(price=float(level_prices[i]), date=date.today(), impact_level=level_impacts[i])

        condition_ids = request.form.getlist('condition_id')
        condition_values = request.form.getlist('condition_value')
        entry.remove_conditions()
        for i in range(len(condition_ids)):
            if condition_ids[i] != '':
                entry.add_condition(condition_id=condition_ids[i], value=condition_values[i])

        one_year_ago = entry.date - timedelta(days=365)
        # Descargar velas con Yahoo Finance y sobreescribir las existentes
        download_candles(db=db,
                        symbol=entry.symbol,
                        config=[
                            {'timeframe': '1d', 'start':one_year_ago, 'end':entry.date},
                        ])
        
        db.session.commit()
        
        flash(f'Registro de {entry.symbol} actualizado exitosamente', 'success')
        return redirect(url_for('watchlist_pages.detail_watchlist_entry', id=entry.id))
    

    entry = WatchlistEntry.query.get_or_404(id)
    if entry.watchlist.user_id != current_user.id:
        abort(403)
    watchlists = Watchlist.query.filter(Watchlist.user_id == current_user.id).all()
    
    return render_template('watchlist_entry/create.html', 
                            entry=entry,
                            watchlists=watchlists, 
                            json_watchlists=[s.to_dict(exclude=['entries']) for s in watchlists],
                            json_levels=[level.to_dict(exclude=['entries']) for level in entry.levels],
                            json_conditions=[condition.to_dict(exclude=['entries', 'watchlist']) for condition in entry.conditions])
                             
    # except Exception as e:
    #     flash(f'Error al cargar el registro para edición: {str(e)}', 'error')
    #     return redirect(url_for('watchlist_pages.watchlist'))

# Función auxiliar para obtener estadísticas de la watchlist
def get_watchlist_stats():
    """Obtener estadísticas generales de la watchlist"""
    try:
        total_entries = WatchlistEntry.query.count()
        active_entries = WatchlistEntry.query.filter(WatchlistEntry.date_exit.is_(None)).count()
        inactive_entries = WatchlistEntry.query.filter(WatchlistEntry.date_exit.isnot(None)).count()
        
        avg_score = db.session.query(db.func.avg(WatchlistEntry.score)).filter(
            WatchlistEntry.date_exit.is_(None)
        ).scalar()
        
        return {
            'total': total_entries,
            'active': active_entries,
            'inactive': inactive_entries,
            'avg_score': round(avg_score, 2) if avg_score else 0
        }
    except Exception:
        return {
            'total': 0,
            'active': 0,
            'inactive': 0,
            'avg_score': 0
        }


watchlist_bp = Blueprint(name='watchlist_endpoints', import_name=__name__)

@watchlist_bp.route(rule='/')
@login_required
def get_watchlists() -> Response:
    
    watchlists: list[Watchlist] = Watchlist.query.filter(Watchlist.user_id == current_user.id).all()
    complete: bool = request.args.get(key='complete', default='false').lower() == 'true'
    
    return jsonify({
        'success': True,
        'data': [watchlist.to_dict(exclude=['entries', 'conditions'] if not complete else []) for watchlist in watchlists],
        'error': None
    })