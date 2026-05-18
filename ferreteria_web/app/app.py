from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from database import db
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

app = Flask(__name__)

# ==========================================
# CONFIGURACION
# ==========================================

app.config['SECRET_KEY'] = 'FerreteriaSistema2026'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/ferreteria_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# ==========================================
# BASE DE DATOS
# ==========================================



db.init_app(app)

# ==========================================
# LOGIN MANAGER
# ==========================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'


# ==========================================
# IMPORTAR MODELOS
# ==========================================

from models import Usuario, Categoria, Producto, Venta, DetalleVenta


# ==========================================
# CREAR TABLAS
# ==========================================

with app.app_context():
    db.create_all()


# ==========================================
# CARGAR USUARIO
# ==========================================

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# ==========================================
# RUTA PRINCIPAL
# ==========================================

@app.route('/')
@login_required
def index():
    return render_template('index.html')


# ==========================================
# LOGIN
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = Usuario.query.filter_by(username=username).first()

        if user and user.password == password:

            login_user(user)

            return redirect(url_for('index'))

        else:
            flash('Usuario o contraseña incorrectos')

    return render_template('login.html')


# ==========================================
# LOGOUT
# ==========================================

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('login'))


# ==========================================
# EJECUTAR APP
# ==========================================

if __name__ == '__main__':
    app.run(debug=True)