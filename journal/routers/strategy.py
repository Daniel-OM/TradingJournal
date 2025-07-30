
from datetime import date, datetime, timezone
from sqlalchemy import desc
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user

from ..models import db, Strategy, StrategyCondition

strategy_bp = Blueprint(name='strategy_endpoints', import_name=__name__)

@strategy_bp.route('/', methods=['GET', 'POST'])
@login_required
def strategies():

    if request.method == 'POST':
        action = request.form.get('action')
        print(request.form)
        if action == 'add_strategy':
            entry = Strategy(
                name=request.form['name'],
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
            flash('Strategy created successfully!', 'success')
        
        elif action == 'edit_strategy':
            strategy: Strategy = Strategy.query.get_or_404(request.form['strategy_id'])
            if strategy.user_id == current_user.id:
                strategy.name = request.form['name']
                strategy.description = request.form['description']
                flash('Strategy updated successfully!', 'success')
            else:
                flash('You are not authorized to update this strategy', 'error')
        
        elif action == 'delete_strategy':
            strategy = Strategy.query.get_or_404(request.form['strategy_id'])
            if strategy.user_id == current_user.id:
                db.session.delete(strategy)
                flash('Strategy deleted successfully!', 'info')
            else:
                flash('You are not authorized to delete this strategy', 'error')
        
        elif action == 'add_scoring':
            strategy: Strategy = Strategy.query.get_or_404(request.form['strategy_id'])
            if strategy.user_id != current_user.id:
                flash('You are not authorized to add coditions to this strategy', 'error')
            else:
                criteria = StrategyCondition(
                    strategy_id=int(request.form['strategy_id']),
                    name=request.form['condition_name'],
                    description=request.form['condition_description'],
                    score=float(request.form['score'])
                )
                db.session.add(criteria)
                flash('Scoring criteria added successfully!', 'success')
        
        elif action == 'edit_criteria':
            criteria: StrategyCondition = StrategyCondition.query.get_or_404(request.form['criteria_id'])
            strategy: Strategy = Strategy.query.get_or_404(criteria.strategy_id)
            if strategy.user_id != current_user.id:
                flash('You are not authorized to add coditions to this strategy', 'error')
            else:
                criteria.name = request.form['condition_name']
                criteria.description = request.form['condition_description']
                criteria.score = float(request.form['score'])
                flash('Scoring criteria updated successfully!', 'success')
        
        elif action == 'delete_criteria':
            criteria = StrategyCondition.query.get_or_404(request.form['criteria_id'])
            strategy: Strategy = Strategy.query.get_or_404(criteria.strategy_id)
            if strategy.user_id != current_user.id:
                flash('You are not authorized to delete coditions from this strategy', 'error')
            else:
                db.session.delete(criteria)
                flash('Scoring criteria deleted successfully!', 'info')
        
        db.session.commit()
        return redirect(url_for('strategy_endpoints.strategies'))

    strategies = Strategy.query.all()
    return render_template('strategy/create.html', date=date, strategies=strategies, json_strategies=[s.to_dict() for s in strategies])
