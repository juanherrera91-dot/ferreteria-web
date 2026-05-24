from flask import Flask
from flask_login import LoginManager
from .database import db
from .models import Usuario

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'FerreteriaSistema2026'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/ferreteria_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar Base de Datos
    db.init_app(app)

    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'views.login' # Apunta al login del Blueprint
    login_manager.login_message = "Por favor, inicia sesión para acceder al sistema."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar el Blueprint de las vistas
    from .views import bp
    app.register_blueprint(bp)

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    return app