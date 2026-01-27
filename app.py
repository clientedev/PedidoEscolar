import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///escola_aquisicoes.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure file uploads
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.template_filter('dict_replace')
def dict_replace_filter(d, key, value):
    new_dict = d.to_dict() if hasattr(d, 'to_dict') else dict(d)
    if value is None:
        new_dict.pop(key, None)
    else:
        new_dict[key] = value
    return new_dict

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    # Import models to ensure they're registered
    import models
    import routes
    
    # Run automatic migrations
    try:
        import run_deploy_migrations
        run_deploy_migrations.run_migrations()
    except Exception as e:
        app.logger.error(f"Migration error: {e}")
    
    # Create all tables
    db.create_all()
    
    # Create default admin user if it doesn't exist
    from models import User
    from werkzeug.security import generate_password_hash
    
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User()
        admin_user.username = 'admin'
        admin_user.email = 'admin@senaimorvanfigueiredo.edu.br'
        admin_user.password_hash = generate_password_hash('admin123')
        admin_user.is_admin = True
        admin_user.full_name = 'Administrador'
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created: username=admin, password=admin123")

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
