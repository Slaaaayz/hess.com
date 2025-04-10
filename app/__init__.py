from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config.config import Config
from app.models.database import db, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialisation de la base de données
    db.init_app(app)
    
    # Initialisation de Flask-Migrate
    migrate = Migrate(app, db)
    
    # Initialisation de Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Création des tables de la base de données
    with app.app_context():
        db.create_all()
    
    # Enregistrement des blueprints
    from app.routes import main, auth, api
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp, url_prefix='/api')
    
    return app 