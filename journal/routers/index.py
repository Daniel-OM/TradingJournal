
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user

from ..models import db, Setting

index_bp = Blueprint(name='index_endpoints', import_name=__name__)

@index_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@index_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        print(request.form)
        if request.form['setting_id']:
            setting: Setting = Setting.query.filter_by(id=int(request.form['setting_id'])).first()
            if setting and setting.user_id == current_user.id:
                if request.form['balance']: setting.balance = float(request.form['balance'])
                if request.form['commission']: setting.commission = float(request.form['commission'])
                if request.form['timezone']: setting.timezone = request.form['timezone']
            else:
                abort(403)
        else:
            setting = Setting(
                balance=float(request.form['balance']),
                commission=float(request.form.get('commission', 1.0)),
                timezone=request.form.get('criteria_description', 'UTC'),
                user_id=current_user.id
            )
        db.session.add(setting)

        db.session.commit()
        return redirect(url_for('index_endpoints.settings'))
    
    setting = Setting.query.filter_by(user_id=current_user.id).first()
    return render_template('settings.html', setting=setting)
