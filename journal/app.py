import os
from flask import Flask, send_from_directory, abort

from .config import DevConfig, ProdConfig
from .login import login_manager
from .models import db, migrate
from .routers import index_bp, strategy_bp, watchlist_bp, journal_bp, error_bp, user_bp

def create_app(config_class:(DevConfig | ProdConfig)) -> Flask:

    static_url_path = getattr(config_class, 'STATIC_URL_PATH', '/static')

    app = Flask(import_name=__name__,
                static_folder='templates/static',
                static_url_path=static_url_path,
                instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance"))
    
    app.config['SECRET_KEY'] = config_class.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f'{config_class.SQLALCHEMY_DATABASE_URI.split('path/')[0]}{os.path.join(app.instance_path, config_class.SQLALCHEMY_DATABASE_URI.split('path/')[1])}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config_class.SQLALCHEMY_TRACK_MODIFICATIONS
    # app.config['APPLICATION_ROOT'] = config_class.APPLICATION_ROOT
    app.config['STATIC_URL_PATH'] = config_class.STATIC_URL_PATH

    app.jinja_env.auto_reload = True
                
    app.register_blueprint(blueprint=index_bp, url_prefix='/')
    app.register_blueprint(blueprint=user_bp, url_prefix='/user')
    app.register_blueprint(blueprint=strategy_bp, url_prefix='/strategy')
    app.register_blueprint(blueprint=watchlist_bp, url_prefix='/watchlist')
    app.register_blueprint(blueprint=journal_bp, url_prefix='/journal')
    app.register_blueprint(blueprint=error_bp, url_prefix='/error')


    db.init_app(app=app)
    migrate.init_app(app=app, db=db)
    login_manager.init_app(app=app)
    # compress = Compress()
    # compress.init_app(app)
    # cors = CORS()
    # cors.init_app(app=app, supports_credentials=True)

    with app.app_context():
        db.create_all()
        
    @app.route('/media/<path:filename>')
    def serve_media(filename):
        media_folder = os.path.join(app.instance_path)
        try:
            return send_from_directory(media_folder, filename.replace('instance/', ''))
        except FileNotFoundError:
            abort(404)
    
    return app

app = create_app(DevConfig)

if __name__ == '__main__':
    # init_db()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
