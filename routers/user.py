
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from ..models import db, User

user_bp = Blueprint(name='user_endpoints', import_name=__name__)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user: User = User.query.filter(or_(User.username==request.form.get('username', ''), User.email==request.form.get('email', ''))).first()
        if user and check_password_hash(user.password, request.form.get('password', '')):
            login_user(user)
            return redirect(url_for('index_endpoints.index'))
        flash('Nombre de usuario o contraseña incorrectos')
    return render_template('user/login.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form.get('password', ''))
        new_user = User(username=request.form.get('username', ''), 
                        email=request.form.get('email', ''), 
                        password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user_endpoints.login'))
    return render_template('user/register.html')

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_endpoints.login'))
