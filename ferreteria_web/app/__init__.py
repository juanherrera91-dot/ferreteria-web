from flask import Flask
from flask_login import LoginManager

from .database import db, bcrypt
from .models import Usuario
from .extensions import bcrypt

def create_app():

    app = Flask(__name__)

    # ======================================
    # CONFIGURACION
    # ======================================
    app.config['SECRET_KEY'] = 'FerreteriaSistema2026'

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'mysql+pymysql://root:@localhost/ferreteria_db'
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ======================================
    # INICIALIZAR BASE DE DATOS
    # ======================================
    db.init_app(app)
    bcrypt.init_app(app)

    # ======================================
    # INICIALIZAR BCRYPT
    # ======================================
    bcrypt.init_app(app)

    # ======================================
    # CONFIGURAR LOGIN
    # ======================================
    login_manager = LoginManager()

    login_manager.init_app(app)

    login_manager.login_view = 'views.login'

    login_manager.login_message = (
        "Por favor, inicia sesión para acceder al sistema."
    )

    login_manager.login_message_category = "warning"

    # ======================================
    # CARGAR USUARIO
    # ======================================
    @login_manager.user_loader
    def load_user(user_id):

        return Usuario.query.get(
            int(user_id)
        )

    # ======================================
    # REGISTRAR BLUEPRINT
    # ======================================
    from .views import bp

    app.register_blueprint(bp)

    # ======================================
    # CREAR TABLAS
    # ======================================
    with app.app_context():

        db.create_all()

    return app