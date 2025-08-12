# routes/diary.py - Router adaptado para la página de errores
import csv
import io
from datetime import date, timedelta
from sqlalchemy import func, desc, and_, or_
from flask import Blueprint, render_template, request, jsonify, Response, abort
from flask_login import login_required, current_user

from ..models import db, Trade, Error, trade_errors

class SimplePagination:
    def __init__(self, page, per_page, total):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = (total + per_page - 1) // per_page
        
    @property
    def has_prev(self):
        return self.page > 1
        
    @property
    def has_next(self):
        return self.page < self.pages
        
    @property
    def prev_num(self):
        return self.page - 1 if self.has_prev else None
        
    @property
    def next_num(self):
        return self.page + 1 if self.has_next else None
        
    def iter_pages(self):
        # Mostrar páginas alrededor de la actual
        start = max(1, self.page - 2)
        end = min(self.pages + 1, self.page + 3)
        return range(start, end)

class ErrorAnalytics:
    @staticmethod
    def get_error_statistics(period_days=None, min_count=1, severity='all'):
        """Obtener estadísticas de errores con filtros"""
        query = Error.query.filter(Error.is_active == True, Error.user_id == current_user.id)
        if severity != 'all':
            query = query.filter(Error.severity == severity)
        
        # Filtrar por período si se especifica
        if period_days:
            cutoff_date = date.today() - timedelta(days=period_days)
            query = query.join(trade_errors).join(Trade).filter(Trade.entry_date >= cutoff_date)
        
        errors = query.all()
        
        # Filtrar por mínimo de ocurrencias
        filtered_errors = [error for error in errors if error.occurrence_count >= min_count]
        
        return {
            'errors': filtered_errors,
            'total_errors': len(filtered_errors),
            'total_occurrences': sum(error.occurrence_count for error in filtered_errors),
            'avg_per_error': sum(error.occurrence_count for error in filtered_errors) / len(filtered_errors) if filtered_errors else 0,
            'days_since_last': min((error.days_since_last_occurrence or 999 for error in filtered_errors), default=0)
        }
    
    @staticmethod
    def get_error_trends(error_id, days=30):
        """Obtener tendencia de un error específico"""
        from datetime import timedelta
        
        cutoff_date = date.today() - timedelta(days=days)
        
        # Contar ocurrencias por día
        daily_counts = db.session.query(
            Trade.entry_date,
            func.count(trade_errors.c.trade_id).label('count')
        ).join(trade_errors).filter(
            trade_errors.c.error_id == error_id,
            Trade.entry_date >= cutoff_date,
            Trade.user_id == current_user.id
        ).group_by(Trade.entry_date).all()
        
        return daily_counts
    
    @staticmethod
    def get_most_costly_errors(limit=10):
        """Obtener los errores más costosos"""
        error_costs = []
        
        for error in Error.query.filter(Error.user_id == current_user.id).all():
            if error.trades:
                total_loss = sum(trade.profit_loss for trade in error.trades if trade.profit_loss < 0)
                error_costs.append({
                    'error': error,
                    'total_loss': total_loss,
                    'avg_loss': total_loss / len(error.trades),
                    'occurrences': len(error.trades)
                })
        
        return sorted(error_costs, key=lambda x: x['total_loss'])[:limit]



error_bp = Blueprint(name='error_endpoints', import_name=__name__)

@error_bp.route('/errors')
@login_required
def errors():
    # Obtener parámetros de filtro
    period = request.args.get('period', 'all')
    sort_by = request.args.get('sort', 'frequency')
    min_count = request.args.get('min_count', 1, type=int)
    severity = request.args.get('severity', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Convertir período a días
    period_days = None
    if period != 'all':
        period_days = int(period)
    
    # Obtener estadísticas usando la clase auxiliar
    stats = ErrorAnalytics.get_error_statistics(period_days, min_count, severity)
    errors_list = stats['errors']
    
    # Aplicar ordenamiento
    if sort_by == 'frequency':
        errors_list.sort(key=lambda x: x.occurrence_count, reverse=True)
    elif sort_by == 'recent':
        errors_list.sort(key=lambda x: x.last_occurrence or date.min, reverse=True)
    elif sort_by == 'alphabetical':
        errors_list.sort(key=lambda x: x.description.lower())
    
    # Paginación
    total_items = len(errors_list)
    start_idx = max(0, (page - 1) * per_page)
    end_idx = min(total_items, start_idx + per_page)
    paginated_errors = errors_list[start_idx:end_idx]
    
    # Crear objeto de paginación simple
    pagination = SimplePagination(page, per_page, total_items)
    
    # Enriquecer datos de errores con información adicional
    enriched_errors = []
    for error in paginated_errors:
        enriched_errors.append({
            "id": error.id,
            "description": error.description,
            "category": error.category,
            "severity": error.severity,
            "count": error.occurrence_count,
            "frequency": error.occurrence_count / stats["total_occurrences"],
            "last_occurrence": error.last_occurrence.strftime('%Y-%m-%d'),
            "days_ago": error.days_since_last_occurrence or 0,
            "trades": [e.to_dict() for e in error.trades],
            "average_impact": error.average_impact
        })
    
    return render_template('errors.html',
                         errors=enriched_errors,
                         total_errors=stats['total_errors'],
                         total_occurrences=stats['total_occurrences'],
                         avg_per_error=stats['avg_per_error'],
                         days_since_last=stats['days_since_last'],
                         pagination=pagination,
                         period=period,
                         sort=sort_by,
                         min_count=min_count,
                         severity=severity)

@error_bp.route('/api/error-details')
@login_required
def error_details():
    error_description = request.args.get('error')
    if not error_description:
        return jsonify({'error': 'Error description required'}), 400
    
    error = Error.query.filter_by(description=error_description, user_id=current_user.id).first()
    if not error:
        return jsonify({'error': 'Error not found'}), 404
    
    # Calcular tendencia (últimos 30 días)
    trend_data = ErrorAnalytics.get_error_trends(error.id, days=30)
    
    # Determinar si la tendencia está aumentando o disminuyendo
    if len(trend_data) >= 2:
        recent_count = sum(day.count for day in trend_data[-7:])  # Última semana
        previous_count = sum(day.count for day in trend_data[-14:-7])  # Semana anterior
        trend = 'increasing' if recent_count > previous_count else 'decreasing'
    else:
        trend = 'stable'
    
    # Generar recomendaciones basadas en el tipo de error
    recommendations = generate_recommendations(error)
    
    return jsonify({
        'total_count': error.occurrence_count,
        'last_date': error.last_occurrence.strftime('%d/%m/%Y') if error.last_occurrence else 'N/A',
        'trend': trend,
        'avg_impact': f'${error.average_impact:.2f}',
        'recommendations': recommendations,
        'trend_data': [{'date': day.date.strftime('%Y-%m-%d'), 'count': day.count} for day in trend_data]
    })

@error_bp.route('/api/error-trades')
@login_required
def error_trades():
    error_description = request.args.get('error')
    if not error_description:
        return jsonify({'error': 'Error description required'}), 400
    
    error = Error.query.filter_by(description=error_description, user_id=current_user.id).first()
    if not error:
        return jsonify({'error': 'Error not found'}), 404
    
    # Obtener trades relacionados con niveles de impacto
    trades_data = []
    for trade in sorted(error.trades, key=lambda t: t.date, reverse=True):
        # Obtener nivel de impacto de la tabla de asociación
        impact_query = db.session.execute(
            db.select(trade_errors.c.impact_level).where(
                and_(trade_errors.c.trade_id == trade.id,
                     trade_errors.c.error_id == error.id)
            )
        ).first()
        
        impact_level = impact_query[0] if impact_query else 'medium'
        
        trades_data.append({
            'id': trade.id,
            'date': trade.date.strftime('%d/%m/%Y'),
            'symbol': trade.symbol,
            'strategy': trade.strategy.name if trade.strategy else 'N/A',
            'pnl': float(trade.profit_loss or 0),
            'impact_level': impact_level
        })
    
    return jsonify({'trades': trades_data})

@error_bp.route('/api/export-errors')
@login_required
def export_errors():
    """Exportar datos de errores a CSV"""
    period = request.args.get('period', 'all')
    min_count = request.args.get('min_count', 1, type=int)
    
    period_days = None if period == 'all' else int(period)
    stats = ErrorAnalytics.get_error_statistics(period_days, min_count)
    
    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'Descripción del Error',
        'Categoría',
        'Severidad',
        'Número de Ocurrencias',
        'Última Ocurrencia',
        'Días desde la última',
        'Impacto Promedio ($)',
        'Trades Afectados'
    ])
    
    # Datos
    for error in stats['errors']:
        writer.writerow([
            error.description,
            error.category or 'N/A',
            error.severity,
            error.occurrence_count,
            error.last_occurrence.strftime('%d/%m/%Y') if error.last_occurrence else 'N/A',
            error.days_since_last_occurrence or 'N/A',
            f'{error.average_impact:.2f}',
            ', '.join([f"{t.symbol} ({t.date.strftime('%d/%m')})" for t in error.recent_examples])
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=trading_errors_{date.today().strftime("%Y%m%d")}.csv'}
    )

# Ruta para gestionar errores (agregar, editar, eliminar)
@error_bp.route('/manage-errors')
@login_required
def manage_errors():
    """Página para gestionar errores únicos"""
    errors = Error.query.filter_by(is_active=True, user_id=current_user.id).order_by(Error.description).all()
    return render_template('manage_errors.html', errors=errors)

@error_bp.route('/api/create-error', methods=['POST'])
@login_required
def create_error():
    """Crear un nuevo error único"""
    data = request.get_json()
    
    # Verificar que no existe ya
    existing = Error.query.filter_by(description=data['description'], user_id=current_user.id).first()
    if existing:
        return jsonify({'error': 'Error already exists'}), 400
    
    error = Error(
        description=data['description'],
        category=data.get('category', 'general'),
        severity=data.get('severity', 'medium'),
        user_id=current_user.id
    )
    
    db.session.add(error)
    db.session.commit()
    
    return jsonify({'success': True, 'error_id': error.id})

@error_bp.route('/api/update-error/<int:error_id>', methods=['PUT'])
@login_required
def update_error(error_id):
    """Actualizar un error existente"""
    error: Error = Error.query.get_or_404(error_id)
    if error.user_id == current_user.id:
        data = request.get_json()
        
        error.description = data.get('description', error.description)
        error.category = data.get('category', error.category)
        error.severity = data.get('severity', error.severity)
    else:
        abort(403)
    
    db.session.commit()
    return jsonify({'success': True})

@error_bp.route('/api/delete-error/<int:error_id>', methods=['DELETE'])
@login_required
def delete_error(error_id):
    """Desactivar un error (soft delete)"""
    error: Error = Error.query.get_or_404(error_id)
    if error.user_id == current_user.id:
        error.is_active = False
    else:
        abort(403)
    db.session.commit()
    return jsonify({'success': True})

def generate_recommendations(error):
    """Generar recomendaciones basadas en el tipo de error"""
    recommendations = []
    
    error_text = error.description.lower()
    
    if 'stop' in error_text or 'pérdida' in error_text:
        recommendations = [
            'Establecer stop-loss antes de entrar al trade',
            'Usar órdenes automáticas para evitar decisiones emocionales',
            'Revisar el sizing de posición para reducir el impacto'
        ]
    elif 'fomo' in error_text or 'miedo' in error_text:
        recommendations = [
            'Esperar confirmaciones técnicas antes de entrar',
            'Mantener un diario emocional',
            'Usar alertas en lugar de monitoreo constante'
        ]
    elif 'tamaño' in error_text or 'size' in error_text:
        recommendations = [
            'Calcular el tamaño de posición antes del trade',
            'No arriesgar más del 1-2% del capital por trade',
            'Usar calculadoras de riesgo'
        ]
    else:
        recommendations = [
            'Revisar el plan de trading antes de operar',
            'Documentar las lecciones aprendidas',
            'Practicar la disciplina y paciencia'
        ]
    
    return recommendations