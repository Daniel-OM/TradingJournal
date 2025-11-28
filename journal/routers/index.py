
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user

from ..models import db, Setting, Risk

index_pages = Blueprint(name='index_pages', import_name=__name__)

@index_pages.route('/')
@login_required
def index():
    return render_template('index.html')

@index_pages.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    setting = Setting.query.filter_by(user_id=current_user.id).first()
    risks = Risk.query.filter_by(user_id=current_user.id).order_by(Risk.date.desc()).all()
    return render_template('settings.html', setting=setting, risks=[r.to_dict(exclude=['user']) for r in risks])

index_bp = Blueprint(name='index_endpoints', import_name=__name__)

@index_bp.route('/settings', methods=['POST'])
@login_required
def post_settings():
    data = request.get_json() if request.is_json else request.form

    setting: Setting = Setting.query.filter_by(user_id=current_user.id).first()

    if setting:
        if data.get('balance'): setting.balance = float(data['balance'])
        if data.get('commission'): setting.commission = float(data['commission'])
        if data.get('timezone'): setting.timezone = data['timezone']
        if data.get('show_r') is not None: setting.show_r = data['show_r']
    else:
        abort(403)
        
    db.session.add(instance=setting)

    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': setting.to_dict(),
        'error': None
    })

@index_bp.route(rule='/risk', methods=['GET'])
@login_required
def get_risks() -> list[dict]:
    risks: list[Risk] = Risk.query.filter_by(user_id=current_user.id).order_by(Risk.date.desc()).all()
    
    return jsonify({
        'success': True,
        'data': [r.to_dict() for r in risks],
        'error': None
    })

@index_bp.route(rule='/risk/update', methods=['POST'])
@login_required
def post_risk():
    data = request.get_json() if request.is_json else request.form
    print(data)
    for risk in data.getlist('risk'):
        if risk['date'] and risk['risk']:
            existing_risk: Risk = Risk.query.filter_by(date=risk['date'], user_id=current_user.id).first()
            if existing_risk:
                existing_risk.risk = float(risk['risk'])
                existing_risk.date = risk['date']
            else:
                new_risk = Risk(
                    risk=float(risk['risk']),
                    date=datetime.strptime(risk['date'], '%Y-%m-%d') if isinstance(risk['date'], str) else risk['date'],
                    user_id=current_user.id
                )
                db.session.add(instance=new_risk)

    db.session.commit()
    
    return jsonify({
        'success': True,
        'error': None
    })

@index_bp.route(rule='/risk/<date>/create', methods=['GET', 'POST'])
@login_required
def create_risk(date):
    print(date, request.get_json())
    data = request.get_json()
    new_risk = None
    if date and data.get('risk'):
        new_risk = Risk(
            risk=float(data['risk']),
            date=datetime.strptime(date, '%Y-%m-%d') if isinstance(date, str) else date,
            user_id=current_user.id
        )
        db.session.add(instance=new_risk)

    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': new_risk.to_dict() if new_risk is not None else None,
        'error': None
    })


@index_bp.route(rule='/risk/<date>/update', methods=['GET', 'POST'])
@login_required
def update_risk(date):
    print(date, request.data)
    existing_risk = None
    if date and request.data.get('risk'):
        existing_risk: Risk = Risk.query.filter_by(date=date, user_id=current_user.id).first()
        if existing_risk:
            existing_risk.risk = float(request.data['risk'])

    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': existing_risk.to_dict() if existing_risk is not None else None,
        'error': None
    })

@index_bp.route(rule='/risk/<date>/delete', methods=['GET', 'POST'])
@login_required
def delete_risk(date):
    if date:
        existing_risk: Risk = Risk.query.filter_by(date=date, user_id=current_user.id).first()
        if existing_risk:
            db.session.delete(instance=existing_risk)

    db.session.commit()
    
    return jsonify({
        'success': True,
        'error': None
    })

