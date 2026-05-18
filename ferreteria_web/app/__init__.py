from flask import Flask
from .models import db
from .auth import auth
from .views import bp
from .auth import bcrypt

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/ferreteria_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(bp)

    return app