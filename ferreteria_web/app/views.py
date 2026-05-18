from flask import Blueprint, render_template, request, redirect, session, flash
from .models import db, Producto, Categoria, Venta, DetalleVenta, Usuario, Cliente
from .decorators import login_required
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from datetime import datetime

bp = Blueprint('bp', __name__)


# =========================
# 🏠 HOME
# =========================
@bp.route('/')
def home():

    # VALIDAR SESIÓN
    if 'user_id' in session:
        return redirect('/dashboard')

    return redirect('/login')


# =========================
# 🏠 DASHBOARD
# =========================
@bp.route('/dashboard')
@login_required
def dashboard():

    productos = Producto.query.count()
    ventas = Venta.query.count()
    categorias = Categoria.query.count()
    clientes = Cliente.query.count()

    total_ventas = db.session.query(
        db.func.sum(Venta.total)
    ).scalar()

    if not total_ventas:
        total_ventas = 0

    datos = Producto.query.all()

    nombres = [p.nombre for p in datos]
    stock = [p.stock for p in datos]

    plt.figure(figsize=(8, 4))
    plt.bar(nombres, stock)
    plt.title("📦 Stock de Productos")
    plt.xticks(rotation=45)

    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)

    grafica = base64.b64encode(img.getvalue()).decode()

    plt.close()

    return render_template(
        "index.html",
        productos=productos,
        ventas=ventas,
        categorias=categorias,
        clientes=clientes,
        total_ventas=total_ventas,
        grafica=grafica
    )


# =========================
# 🔧 PRODUCTOS
# =========================
@bp.route('/productos')
@login_required
def productos():

    data = Producto.query.all()
    categorias = Categoria.query.all()

    return render_template(
        "producto.html",
        productos=data,
        categorias=categorias
    )


# =========================
# ➕ AGREGAR PRODUCTO
# =========================
@bp.route('/add_producto', methods=['POST'])
@login_required
def add_producto():

    categoria_id = request.form.get('categoria')

    if not categoria_id:
        flash("Debes seleccionar una categoría")
        return redirect('/productos')

    nuevo = Producto(
        nombre=request.form['nombre'].upper(),
        precio=float(request.form['precio']),
        stock=int(request.form['stock']),
        categoria_id=int(categoria_id)
    )

    db.session.add(nuevo)
    db.session.commit()

    flash("Producto agregado correctamente")

    return redirect('/productos')


# =========================
# ✏ EDITAR PRODUCTO
# =========================
@bp.route('/edit_producto/<int:id>', methods=['POST'])
@login_required
def edit_producto(id):

    producto = Producto.query.get_or_404(id)

    producto.nombre = request.form['nombre'].upper()
    producto.precio = float(request.form['precio'])
    producto.stock = int(request.form['stock'])

    categoria = request.form.get('categoria')

    if categoria:
        producto.categoria_id = int(categoria)

    db.session.commit()

    flash("Producto actualizado")

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

    flash("Producto eliminado")

    return redirect('/productos')


# =========================
# 👥 CLIENTES
# =========================
@bp.route('/clientes')
@login_required
def clientes():

    data = Cliente.query.all()

    return render_template(
        "cliente.html",
        clientes=data
    )


# =========================
# ➕ AGREGAR CLIENTE
# =========================
@bp.route('/add_cliente', methods=['POST'])
@login_required
def add_cliente():

    nuevo = Cliente(
        nombre=request.form['nombre'].upper(),
        telefono=request.form['telefono'],
        direccion=request.form['direccion'],
        ci_nit=request.form['ci_nit']
    )

    db.session.add(nuevo)
    db.session.commit()

    flash("Cliente agregado")

    return redirect('/clientes')


# =========================
# 🗑 ELIMINAR CLIENTE
# =========================
@bp.route('/delete_cliente/<int:id>')
@login_required
def delete_cliente(id):

    cliente = Cliente.query.get_or_404(id)

    db.session.delete(cliente)
    db.session.commit()

    flash("Cliente eliminado")

    return redirect('/clientes')


# =========================
# 🧾 VENTAS
# =========================
@bp.route('/ventas')
@login_required
def ventas():

    data = Venta.query.order_by(
        Venta.id.desc()
    ).all()

    clientes = Cliente.query.order_by(
        Cliente.nombre.asc()
    ).all()

    return render_template(
        "venta.html",
        ventas=data,
        clientes=clientes
    )


# =========================
# 🆕 CREAR VENTA
# =========================
@bp.route('/crear_venta', methods=['POST'])
@login_required
def crear_venta():

    usuario_id = session.get('user_id')
    cliente_id = request.form.get('cliente_id')

    # VALIDAR LOGIN
    if not usuario_id:
        flash("Usuario no autenticado")
        return redirect('/login')

    # VALIDAR CLIENTE
    if not cliente_id:
        flash("Debes seleccionar un cliente")
        return redirect('/ventas')

    nueva = Venta(
        fecha=datetime.now(),
        usuario_id=int(usuario_id),
        cliente_id=int(cliente_id),
        total=0
    )

    db.session.add(nueva)
    db.session.commit()

    flash("Venta creada correctamente")

    return redirect(f'/venta_detalle/{nueva.id}')


# =========================
# 🛒 DETALLE VENTA
# =========================
@bp.route('/venta_detalle/<int:id>')
@login_required
def venta_detalle(id):

    venta = Venta.query.get_or_404(id)

    productos = Producto.query.all()

    total = 0

    for d in venta.detalles:
        total += d.subtotal

    venta.total = total

    db.session.commit()

    return render_template(
        "venta_detalle.html",
        venta=venta,
        productos=productos,
        total=total
    )


# =========================
# ➕ AGREGAR DETALLE
# =========================
@bp.route('/add_detalle/<int:venta_id>', methods=['POST'])
@login_required
def add_detalle(venta_id):

    producto_id = request.form.get('producto_id')
    cantidad = request.form.get('cantidad')

    if not producto_id or not cantidad:
        flash("Datos incompletos")
        return redirect(f'/venta_detalle/{venta_id}')

    cantidad = int(cantidad)

    if cantidad <= 0:
        flash("Cantidad inválida")
        return redirect(f'/venta_detalle/{venta_id}')

    producto = Producto.query.get_or_404(producto_id)

    if producto.stock < cantidad:
        flash("Stock insuficiente")
        return redirect(f'/venta_detalle/{venta_id}')

    subtotal = producto.precio * cantidad

    detalle = DetalleVenta(
        venta_id=venta_id,
        producto_id=int(producto_id),
        cantidad=cantidad,
        precio_unitario=producto.precio,
        subtotal=subtotal
    )

    producto.stock -= cantidad

    db.session.add(detalle)

    venta = Venta.query.get(venta_id)

    if venta.total:
        venta.total += subtotal
    else:
        venta.total = subtotal

    db.session.commit()

    flash("Producto agregado a la venta")

    return redirect(f'/venta_detalle/{venta_id}')


# =========================
# 📊 REPORTES
# =========================
@bp.route('/reporte')
@login_required
def reporte():

    ventas = Venta.query.all()

    fechas = []
    totales = []

    for v in ventas:
        fechas.append(v.fecha.strftime('%d/%m'))
        totales.append(v.total)

    plt.figure(figsize=(8, 4))
    plt.plot(fechas, totales, marker='o')
    plt.title("📈 Reporte de Ventas")
    plt.xticks(rotation=45)

    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)

    grafica = base64.b64encode(img.getvalue()).decode()

    plt.close()

    total_general = db.session.query(
        db.func.sum(Venta.total)
    ).scalar()

    if not total_general:
        total_general = 0

    return render_template(
        "reporte.html",
        plot_url=grafica,
        total_general=total_general,
        ventas=ventas
    )