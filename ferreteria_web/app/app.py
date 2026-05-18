from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from datetime import datetime

from werkzeug.security import check_password_hash

from ferreteria_web.app.database import db

from ferreteria_web.app.models import (
    Usuario,
    Categoria,
    Producto,
    Venta,
    DetalleVenta,
    Cliente
)

# ==========================================
# APP
# ==========================================

app = Flask(__name__)

app.config['SECRET_KEY'] = 'FerreteriaSistema2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/ferreteria_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ==========================================
# LOGIN
# ==========================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ==========================================
# DB INIT
# ==========================================

with app.app_context():
    db.create_all()

# ==========================================
# HOME
# ==========================================

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ==========================================
# LOGIN
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        user = Usuario.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            login_user(user)
            flash('Bienvenido', 'success')
            return redirect(url_for('dashboard'))

        flash('Usuario o contraseña incorrecta', 'danger')

    return render_template('login.html')

# ==========================================
# LOGOUT
# ==========================================

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

# ==========================================
# DASHBOARD
# ==========================================

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', usuario=current_user)

# ==========================================
# PRODUCTOS
# ==========================================

@app.route('/productos')
@login_required
def productos():
    productos = Producto.query.all()
    categorias = Categoria.query.all()

    return render_template(
        'producto.html',
        productos=productos,
        categorias=categorias
    )

@app.route('/add_producto', methods=['POST'])
@login_required
def add_producto():

    try:
        nuevo = Producto(
            nombre=request.form['nombre'].upper(),
            precio=float(request.form['precio']),
            stock=int(request.form['stock']),
            categoria_id=int(request.form['categoria'])
        )

        db.session.add(nuevo)
        db.session.commit()

        flash('Producto agregado', 'success')

    except Exception as e:
        db.session.rollback()
        flash(str(e), 'danger')

    return redirect(url_for('productos'))

# ==========================================
# CLIENTES
# ==========================================

@app.route('/clientes')
@login_required
def clientes():
    clientes = Cliente.query.all()
    return render_template('cliente.html', clientes=clientes)

@app.route('/add_cliente', methods=['POST'])
@login_required
def add_cliente():

    try:
        nuevo = Cliente(
            nombre=request.form['nombre'].upper(),
            telefono=request.form['telefono'],
            direccion=request.form['direccion'],
            ci_nit=request.form['ci_nit']
        )

        db.session.add(nuevo)
        db.session.commit()

        flash('Cliente agregado', 'success')

    except Exception as e:
        db.session.rollback()
        flash(str(e), 'danger')

    return redirect(url_for('clientes'))

# ==========================================
# VENTAS
# ==========================================

@app.route('/ventas')
@login_required
def ventas():
    ventas = Venta.query.order_by(Venta.id.desc()).all()
    clientes = Cliente.query.all()

    return render_template(
        'venta.html',
        ventas=ventas,
        clientes=clientes
    )

@app.route('/crear_venta', methods=['POST'])
@login_required
def crear_venta():

    try:
        cliente_id = request.form.get('cliente_id')

        nueva_venta = Venta(
            fecha=datetime.now(),
            usuario_id=current_user.id,
            cliente_id=int(cliente_id),
            total=0
        )

        db.session.add(nueva_venta)
        db.session.commit()

        flash('Venta creada', 'success')

        return redirect(url_for('venta_detalle', id=nueva_venta.id))

    except Exception as e:
        db.session.rollback()
        flash(str(e), 'danger')
        return redirect(url_for('ventas'))

# ==========================================
# DETALLE VENTA (CORREGIDO)
# ==========================================

@app.route('/venta_detalle/<int:id>')
@login_required
def venta_detalle(id):

    venta = Venta.query.get_or_404(id)
    productos = Producto.query.all()

    total = sum(d.subtotal for d in venta.detalles)

    return render_template(
        'venta_detalle.html',
        venta=venta,
        productos=productos,
        total=total
    )

# ==========================================
# AGREGAR DETALLE (CORREGIDO)
# ==========================================

@app.route('/add_detalle/<int:venta_id>', methods=['POST'])
@login_required
def add_detalle(venta_id):

    try:
        producto_id = request.form.get('producto_id')
        cantidad = int(request.form.get('cantidad'))

        producto = Producto.query.get_or_404(producto_id)

        if producto.stock < cantidad:
            flash('Stock insuficiente', 'danger')
            return redirect(url_for('venta_detalle', id=venta_id))

        subtotal = producto.precio * cantidad

        detalle = DetalleVenta(
            venta_id=venta_id,
            producto_id=producto.id,
            cantidad=cantidad,
            precio_unitario=producto.precio,
            subtotal=subtotal
        )

        producto.stock -= cantidad

        db.session.add(detalle)
        db.session.commit()

        flash('Producto agregado', 'success')

    except Exception as e:
        db.session.rollback()
        flash(str(e), 'danger')

    return redirect(url_for('venta_detalle', id=venta_id))

# ==========================================
# RUN
# ==========================================

if __name__ == '__main__':
    app.run(debug=True)