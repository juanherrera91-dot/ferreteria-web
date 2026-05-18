from flask import Blueprint, render_template, request, redirect, session
from .models import db, Producto, Categoria, Venta, DetalleVenta, Usuario
from .decorators import login_required
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from datetime import datetime

bp = Blueprint('bp', __name__)

# =========================
# 🏠 DASHBOARD
# =========================
@bp.route('/dashboard')
@login_required
def dashboard():
    productos = Producto.query.count()
    ventas = Venta.query.count()
    categorias = Categoria.query.count()

    return render_template("index.html",
                           productos=productos,
                           ventas=ventas,
                           categorias=categorias)


# =========================
# 🔧 PRODUCTOS
# =========================
@bp.route('/productos')
@login_required
def productos():
    data = Producto.query.all()
    categorias = Categoria.query.all()
    return render_template("producto.html", productos=data, categorias=categorias)


# =========================
# ➕ AGREGAR PRODUCTO (CORREGIDO)
# =========================
@bp.route('/add_producto', methods=['POST'])
@login_required
def add_producto():

    categoria_id = request.form.get('categoria')

    # 🚨 VALIDACIÓN REAL
    if not categoria_id or categoria_id.strip() == "":
        return "❌ Debes seleccionar una categoría"

    nuevo = Producto(
        nombre=request.form['nombre'],
        precio=float(request.form['precio']),
        stock=int(request.form['stock']),
        categoria_id=int(categoria_id)
    )

    db.session.add(nuevo)
    db.session.commit()

    return redirect('/productos')


# =========================
# 🗑 ELIMINAR PRODUCTO
# =========================
@bp.route('/delete_producto/<int:id>')
@login_required
def delete_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    return redirect('/productos')


# =========================
# ✏ EDITAR PRODUCTO
# =========================
@bp.route('/edit_producto/<int:id>', methods=['POST'])
@login_required
def edit_producto(id):
    producto = Producto.query.get_or_404(id)

    producto.nombre = request.form['nombre']
    producto.precio = float(request.form['precio'])
    producto.stock = int(request.form['stock'])

    db.session.commit()
    return redirect('/productos')


# =========================
# 📊 REPORTE
# =========================
@bp.route('/reporte')
@login_required
def reporte():
    productos = Producto.query.all()

    nombres = [p.nombre for p in productos]
    stock = [p.stock for p in productos]

    plt.figure(figsize=(6,4))
    plt.bar(nombres, stock)
    plt.title("📦 Stock de Productos")
    plt.xticks(rotation=45)

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    grafica = base64.b64encode(img.getvalue()).decode()

    return render_template("reporte.html", plot_url=grafica)


# =========================
# 🧾 VENTAS
# =========================
@bp.route('/ventas')
@login_required
def ventas():
    data = Venta.query.all()
    return render_template("venta.html", ventas=data)


# =========================
# 🆕 CREAR VENTA (CORREGIDO)
# =========================
@bp.route('/crear_venta')
@login_required
def crear_venta():

    usuario_id = session.get('user_id')

    if not usuario_id:
        return "❌ Usuario no autenticado"

    nueva = Venta(
        fecha=datetime.now(),
        usuario_id=int(usuario_id)
    )

    db.session.add(nueva)
    db.session.commit()

    return redirect(f'/venta_detalle/{nueva.id}')


# =========================
# 🛒 DETALLE VENTA
# =========================
@bp.route('/venta_detalle/<int:id>')
@login_required
def venta_detalle(id):
    venta = Venta.query.get_or_404(id)
    productos = Producto.query.all()

    return render_template("venta_detalle.html",
                           venta=venta,
                           productos=productos)


# =========================
# ➕ AGREGAR DETALLE VENTA
# =========================
@bp.route('/add_detalle/<int:venta_id>', methods=['POST'])
@login_required
def add_detalle(venta_id):

    producto_id = request.form.get('producto_id')
    cantidad = request.form.get('cantidad')

    if not producto_id or not cantidad:
        return "❌ Datos incompletos"

    cantidad = int(cantidad)

    producto = Producto.query.get_or_404(producto_id)

    if producto.stock < cantidad:
        return "❌ Stock insuficiente"

    subtotal = producto.precio * cantidad

    detalle = DetalleVenta(
        venta_id=venta_id,
        producto_id=int(producto_id),
        cantidad=cantidad,
        subtotal=subtotal
    )

    producto.stock -= cantidad

    db.session.add(detalle)
    db.session.commit()

    return redirect(f'/venta_detalle/{venta_id}')


# =========================
# 🗑 ELIMINAR VENTA
# =========================
@bp.route('/delete_venta/<int:id>')
@login_required
def delete_venta(id):

    venta = Venta.query.get_or_404(id)

    for d in venta.detalles:
        producto = Producto.query.get(d.producto_id)
        if producto:
            producto.stock += d.cantidad
        db.session.delete(d)

    db.session.delete(venta)
    db.session.commit()

    return redirect('/ventas')


# =========================
# 🗑 ELIMINAR DETALLE
# =========================
@bp.route('/delete_detalle/<int:id>/<int:venta_id>')
@login_required
def delete_detalle(id, venta_id):

    detalle = DetalleVenta.query.get_or_404(id)

    producto = Producto.query.get(detalle.producto_id)
    if producto:
        producto.stock += detalle.cantidad

    db.session.delete(detalle)
    db.session.commit()

    return redirect(f'/venta_detalle/{venta_id}')


# =========================
# 🏠 HOME
# =========================
@bp.route('/')
def home():
    if 'user' in session:
        return redirect('/dashboard')
    return redirect('/login')