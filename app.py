import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this-in-prod')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///blog.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Store the app context for database creation command usage if needed
    
    from models import User, Post, SiteSettings, Category
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()
        
        # Initialize default categories if they don't exist
        default_categories = ['World', 'Business', 'Tech']
        for cat_name in default_categories:
            if not Category.query.filter_by(name=cat_name).first():
                db.session.add(Category(name=cat_name))
        db.session.commit()
    
    @app.context_processor
    def inject_global_data():
        settings = SiteSettings.query.first()
        categories = Category.query.order_by(Category.name).all()
        return dict(social_links=settings, nav_categories=categories)

    return app

app = create_app()
