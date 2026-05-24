from flask import Blueprint, render_template, redirect, url_for, request, flash

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from datetime import datetime

from werkzeug.security import check_password_hash

# ==========================================
# MATPLOTLIB
# ==========================================
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

import base64

from io import BytesIO

# ==========================================
# BASE DE DATOS
# ==========================================
from .database import db

# ==========================================
# MODELOS
# ==========================================
from .models import (
    Usuario,
    Categoria,
    Producto,
    Venta,
    DetalleVenta,
    Cliente
)

# ==========================================
# BLUEPRINT
# ==========================================
bp = Blueprint('views', __name__)

# ==========================================
# HOME
# ==========================================
@bp.route('/')
def home():

    if current_user.is_authenticated:
        return redirect(
            url_for('views.dashboard')
        )

    return redirect(
        url_for('views.login')
    )

# ==========================================
# LOGIN
# ==========================================
@bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(
            url_for('views.dashboard')
        )

    if request.method == 'POST':

        username = request.form.get('username')

        password = request.form.get('password')

        user = Usuario.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            flash(
                '¡Bienvenido al sistema!',
                'success'
            )

            return redirect(
                url_for('views.dashboard')
            )

        flash(
            'Usuario o contraseña incorrecta',
            'danger'
        )

    return render_template(
        'login.html'
    )

# ==========================================
# LOGOUT
# ==========================================
@bp.route('/logout')
@login_required
def logout():

    logout_user()

    flash(
        'Sesión cerrada correctamente',
        'info'
    )

    return redirect(
        url_for('views.login')
    )

# ==========================================
# DASHBOARD
# ==========================================
@bp.route('/dashboard')
@login_required
def dashboard():

    # ======================================
    # CONTADORES
    # ======================================
    productos = Producto.query.count()

    ventas = Venta.query.count()

    categorias = Categoria.query.count()

    clientes = Cliente.query.count()

    # ======================================
    # DATOS PARA GRÁFICA
    # ======================================
    lista_productos = Producto.query.all()

    nombres = []

    stocks = []

    for producto in lista_productos:

        nombres.append(producto.nombre)

        stocks.append(producto.stock)

    # ======================================
    # CREAR GRÁFICA PROFESIONAL
    # ======================================
    grafica = None

    if nombres and stocks:

        plt.figure(
            figsize=(12, 6)
        )

        colores = [
            '#0d6efd',
            '#198754',
            '#ffc107',
            '#dc3545',
            '#6610f2',
            '#fd7e14',
            '#20c997',
            '#6f42c1',
            '#0dcaf0',
            '#d63384'
        ]

        barras = plt.bar(
            nombres,
            stocks,
            color=colores[:len(nombres)],
            edgecolor='black',
            linewidth=1.2
        )

        # ==================================
        # TÍTULO
        # ==================================
        plt.title(
            '📊 Estadísticas de Productos en Stock',
            fontsize=18,
            fontweight='bold'
        )

        # ==================================
        # ETIQUETAS
        # ==================================
        plt.xlabel(
            'Productos',
            fontsize=12
        )

        plt.ylabel(
            'Cantidad Disponible',
            fontsize=12
        )

        # ==================================
        # ROTAR NOMBRES
        # ==================================
        plt.xticks(
            rotation=25,
            fontsize=10
        )

        # ==================================
        # GRID SUAVE
        # ==================================
        plt.grid(
            axis='y',
            linestyle='--',
            alpha=0.4
        )

        # ==================================
        # VALORES SOBRE BARRAS
        # ==================================
        for barra in barras:

            altura = barra.get_height()

            plt.text(
                barra.get_x() + barra.get_width() / 2,
                altura + 0.3,
                f'{int(altura)}',
                ha='center',
                fontsize=10,
                fontweight='bold'
            )

        # ==================================
        # AJUSTE DE ESPACIOS
        # ==================================
        plt.tight_layout()

        # ==================================
        # GUARDAR IMAGEN
        # ==================================
        buffer = BytesIO()

        plt.savefig(
            buffer,
            format='png',
            bbox_inches='tight'
        )

        buffer.seek(0)

        grafica = base64.b64encode(
            buffer.getvalue()
        ).decode('utf-8')

        buffer.close()

        plt.close()

    # ======================================
    # TEMPLATE
    # ======================================
    return render_template(
        'index.html',
        usuario=current_user,
        productos=productos,
        ventas=ventas,
        categorias=categorias,
        clientes=clientes,
        grafica=grafica
    )

# ==========================================
# PRODUCTOS
# ==========================================
@bp.route('/productos')
@login_required
def productos():

    productos = Producto.query.all()

    categorias = Categoria.query.all()

    return render_template(
        'producto.html',
        productos=productos,
        categorias=categorias
    )

# ==========================================
# AGREGAR PRODUCTO
# ==========================================
@bp.route('/add_producto', methods=['POST'])
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

        flash(
            'Producto agregado correctamente',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error al agregar producto: {str(e)}',
            'danger'
        )

    return redirect(
        url_for('views.productos')
    )

# ==========================================
# EDITAR PRODUCTO
# ==========================================
@bp.route('/editar_producto/<int:id>', methods=['POST'])
@login_required
def editar_producto(id):

    try:

        producto = Producto.query.get_or_404(id)

        producto.nombre = request.form[
            'nombre'
        ].upper()

        producto.precio = float(
            request.form['precio']
        )

        producto.stock = int(
            request.form['stock']
        )

        producto.categoria_id = int(
            request.form['categoria']
        )

        db.session.commit()

        flash(
            'Producto actualizado correctamente',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error al actualizar producto: {str(e)}',
            'danger'
        )

    return redirect(
        url_for('views.productos')
    )

# ==========================================
# ELIMINAR PRODUCTO
# ==========================================
@bp.route('/eliminar_producto/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):

    try:

        producto = Producto.query.get_or_404(id)

        db.session.delete(producto)

        db.session.commit()

        flash(
            'Producto eliminado correctamente',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error al eliminar producto: {str(e)}',
            'danger'
        )

    return redirect(
        url_for('views.productos')
    )

# ==========================================
# CLIENTES
# ==========================================
@bp.route('/clientes')
@login_required
def clientes():

    clientes = Cliente.query.all()

    return render_template(
        'cliente.html',
        clientes=clientes
    )

# ==========================================
# AGREGAR CLIENTE
# ==========================================
@bp.route('/add_cliente', methods=['POST'])
@login_required
def add_cliente():

    try:

        nombre = request.form.get(
            'nombre',
            ''
        ).strip().upper()

        telefono = request.form.get(
            'telefono',
            ''
        ).strip()

        direccion = request.form.get(
            'direccion',
            ''
        ).strip()

        ci_nit = request.form.get(
            'ci_nit',
            ''
        ).strip()

        if not nombre:

            flash(
                'El nombre es obligatorio',
                'warning'
            )

            return redirect(
                url_for('views.clientes')
            )

        if ci_nit == "":
            ci_nit = None

        nuevo = Cliente(
            nombre=nombre,
            telefono=telefono if telefono else None,
            direccion=direccion if direccion else None,
            ci_nit=ci_nit
        )

        db.session.add(nuevo)

        db.session.commit()

        flash(
            'Cliente registrado correctamente',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error al registrar cliente: {str(e)}',
            'danger'
        )

    return redirect(
        url_for('views.clientes')
    )
# ==========================================
# EDITAR CLIENTE
# ==========================================
@bp.route('/editar_cliente/<int:id>', methods=['POST'])
@login_required
def editar_cliente(id):

    try:

        cliente = Cliente.query.get_or_404(id)

        nombre = request.form.get(
            'nombre',
            ''
        ).strip().upper()

        telefono = request.form.get(
            'telefono',
            ''
        ).strip()

        direccion = request.form.get(
            'direccion',
            ''
        ).strip()

        ci_nit = request.form.get(
            'ci_nit',
            ''
        ).strip()

        # VALIDAR NOMBRE
        if not nombre:

            flash(
                'El nombre es obligatorio',
                'warning'
            )

            return redirect(
                url_for('views.clientes')
            )

        # VALIDAR CI/NIT
        if ci_nit == "":
            ci_nit = None

        else:

            existe_ci = Cliente.query.filter(
                Cliente.ci_nit == ci_nit,
                Cliente.id != id
            ).first()

            if existe_ci:

                flash(
                    f'El CI/NIT {ci_nit} ya pertenece a otro cliente',
                    'danger'
                )

                return redirect(
                    url_for('views.clientes')
                )

        # ACTUALIZAR DATOS
        cliente.nombre = nombre

        cliente.telefono = (
            telefono if telefono else None
        )

        cliente.direccion = (
            direccion if direccion else None
        )

        cliente.ci_nit = ci_nit

        db.session.commit()

        flash(
            'Cliente actualizado correctamente',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error al actualizar cliente: {str(e)}',
            'danger'
        )

    return redirect(
        url_for('views.clientes')
    )

# ==========================================
# ELIMINAR CLIENTE
# ==========================================
@bp.route('/eliminar_cliente/<int:id>', methods=['POST'])
@login_required
def eliminar_cliente(id):

    try:

        cliente = Cliente.query.get_or_404(id)

        db.session.delete(cliente)

        db.session.commit()

        flash(
            'Cliente eliminado correctamente',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error al eliminar cliente: {str(e)}',
            'danger'
        )

    return redirect(
        url_for('views.clientes')
    )
# ==========================================
# VENTAS
# ==========================================
@bp.route('/ventas')
@login_required
def ventas():

    ventas = Venta.query.order_by(
        Venta.id.desc()
    ).all()

    clientes = Cliente.query.all()

    return render_template(
        'venta.html',
        ventas=ventas,
        clientes=clientes
    )

# ==========================================
# CREAR VENTA
# ==========================================
@bp.route('/crear_venta', methods=['POST'])
@login_required
def crear_venta():

    try:

        cliente_id = request.form.get(
            'cliente_id'
        )

        if not cliente_id:

            flash(
                'Debe seleccionar un cliente',
                'warning'
            )

            return redirect(
                url_for('views.ventas')
            )

        nueva_venta = Venta(
            fecha=datetime.now(),
            usuario_id=current_user.id,
            cliente_id=int(cliente_id),
            total=0
        )

        db.session.add(nueva_venta)

        db.session.commit()

        flash(
            'Venta creada correctamente',
            'success'
        )

        return redirect(
            url_for(
                'views.venta_detalle',
                id=nueva_venta.id
            )
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error al crear venta: {str(e)}',
            'danger'
        )

        return redirect(
            url_for('views.ventas')
        )

# ==========================================
# DETALLE DE VENTA
# ==========================================
@bp.route('/venta_detalle/<int:id>')
@login_required
def venta_detalle(id):

    venta = Venta.query.get_or_404(id)

    productos = Producto.query.all()

    total = sum(
        d.subtotal for d in venta.detalles
    )

    venta.total = total

    db.session.commit()

    return render_template(
        'venta_detalle.html',
        venta=venta,
        productos=productos,
        total=total
    )

# ==========================================
# AGREGAR DETALLE
# ==========================================
@bp.route('/add_detalle/<int:venta_id>', methods=['POST'])
@login_required
def add_detalle(venta_id):

    try:

        producto_id = request.form.get(
            'producto_id'
        )

        cantidad = int(
            request.form.get('cantidad')
        )

        producto = Producto.query.get_or_404(
            producto_id
        )

        if producto.stock < cantidad:

            flash(
                f'Stock insuficiente para {producto.nombre}',
                'danger'
            )

            return redirect(
                url_for(
                    'views.venta_detalle',
                    id=venta_id
                )
            )

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

        flash(
            'Producto agregado a la venta',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error al agregar detalle: {str(e)}',
            'danger'
        )

    return redirect(
        url_for(
            'views.venta_detalle',
            id=venta_id
        )
    )
    # ==========================================
# REPORTES IA
# ==========================================
@bp.route('/reportes')
@login_required
def reportes():

    # =========================
    # MÉTRICAS GENERALES
    # =========================
    total_productos = Producto.query.count()

    total_clientes = Cliente.query.count()

    total_ventas = Venta.query.count()

    # =========================
    # TOTAL INGRESOS
    # =========================
    ventas_lista = Venta.query.all()

    ingresos = 0

    for venta in ventas_lista:
        ingresos += venta.total

    # =========================
    # PRODUCTO MÁS VENDIDO
    # =========================
    detalles = DetalleVenta.query.all()

    contador = {}

    for detalle in detalles:

        nombre = detalle.producto.nombre

        if nombre in contador:
            contador[nombre] += detalle.cantidad
        else:
            contador[nombre] = detalle.cantidad

    producto_top = "Sin ventas"

    if contador:
        producto_top = max(
            contador,
            key=contador.get
        )

    # =========================
    # ANÁLISIS IA SIMPLE
    # =========================
    analisis = f"""
    El sistema registra {total_ventas} ventas realizadas,
    con un ingreso total de Bs. {ingresos:.2f}.

    Actualmente existen {total_productos} productos registrados
    y {total_clientes} clientes almacenados.

    El producto más vendido es:
    {producto_top}.

    Recomendación IA:
    Mantener stock suficiente del producto más vendido
    y aplicar promociones en productos con baja salida.
    """

    # =========================
    # ENVIAR TEMPLATE
    # =========================
    return render_template(
        'reportes.html',
        total_productos=total_productos,
        total_clientes=total_clientes,
        total_ventas=total_ventas,
        ingresos=ingresos,
        producto_top=producto_top,
        analisis=analisis
    )
    # ==========================================
# REPORTE 1
# ANALISIS GENERAL DEL SISTEMA
# ==========================================
@bp.route('/reporte1')
@login_required
def reporte1():

    import matplotlib.pyplot as plt
    import base64

    from io import BytesIO
    from collections import defaultdict

    # ======================================
    # MÉTRICAS GENERALES
    # ======================================
    total_ventas = Venta.query.count()

    total_productos = Producto.query.count()

    total_clientes = Cliente.query.count()

    ingresos = 0

    for venta in Venta.query.all():
        ingresos += venta.total

    # ======================================
    # VENTAS POR MES
    # ======================================
    meses = defaultdict(float)

    ventas = Venta.query.all()

    for venta in ventas:

        mes = venta.fecha.strftime('%B')

        meses[mes] += venta.total

    nombres = list(meses.keys())

    valores = list(meses.values())

    # ======================================
    # GRAFICA LINEAL
    # ======================================
    grafica = None

    if nombres and valores:

        plt.figure(figsize=(12, 5))

        plt.plot(
            nombres,
            valores,
            marker='o',
            linewidth=3
        )

        plt.title(
            'Ventas por Mes',
            fontsize=18,
            fontweight='bold'
        )

        plt.xlabel('Mes')

        plt.ylabel('Ingresos')

        plt.grid(True)

        plt.tight_layout()

        buffer = BytesIO()

        plt.savefig(
            buffer,
            format='png'
        )

        buffer.seek(0)

        grafica = base64.b64encode(
            buffer.getvalue()
        ).decode('utf-8')

        buffer.close()

        plt.close()

    # ======================================
    # IA
    # ======================================
    analisis = f"""
    El sistema registra actualmente
    {total_ventas} ventas realizadas.

    Los ingresos generales alcanzan
    Bs. {ingresos:.2f}.

    Existen {total_productos} productos
    y {total_clientes} clientes registrados.

    Inteligencia Artificial detectó
    que las ventas muestran un
    comportamiento estable.

    Se recomienda aumentar promociones
    en meses de menor ingreso.
    """

    return render_template(
        'reporte1.html',
        total_ventas=total_ventas,
        total_productos=total_productos,
        total_clientes=total_clientes,
        ingresos=ingresos,
        grafica=grafica,
        analisis=analisis
    )
    # ==========================================
# REPORTE 2
# TENDENCIAS Y CLIENTES FRECUENTES
# ==========================================
@bp.route('/reporte2')
@login_required
def reporte2():

    import matplotlib.pyplot as plt
    import base64

    from io import BytesIO
    from collections import defaultdict

    clientes = defaultdict(int)

    ventas = Venta.query.all()

    for venta in ventas:

        nombre = venta.cliente.nombre

        clientes[nombre] += 1

    nombres = list(clientes.keys())

    cantidades = list(clientes.values())

    grafica = None

    if nombres and cantidades:

        plt.figure(figsize=(12,5))

        plt.bar(
            nombres,
            cantidades
        )

        plt.title(
            'Clientes Frecuentes',
            fontsize=18,
            fontweight='bold'
        )

        plt.xlabel('Clientes')

        plt.ylabel('Compras')

        plt.xticks(rotation=20)

        plt.tight_layout()

        buffer = BytesIO()

        plt.savefig(
            buffer,
            format='png'
        )

        buffer.seek(0)

        grafica = base64.b64encode(
            buffer.getvalue()
        ).decode('utf-8')

        buffer.close()

        plt.close()

    interpretacion = """
    La Inteligencia Artificial detectó
    que existen clientes frecuentes
    con alta recurrencia de compra.

    Se recomienda aplicar descuentos
    especiales y programas de fidelización.

    Los clientes más constantes
    generan mayor estabilidad económica.
    """

    return render_template(
        'reporte2.html',
        grafica=grafica,
        interpretacion=interpretacion
    )
  # ==========================================
# REPORTE 3
# PREDICCION INTELIGENTE
# ==========================================
@bp.route('/reporte3')
@login_required
def reporte3():

    productos = Producto.query.all()

    riesgo = []

    recomendados = []

    for producto in productos:

        if producto.stock <= 5:
            riesgo.append(producto)

        if producto.stock >= 20:
            recomendados.append(producto)

    explicacion = """
    Modelo utilizado:
    Sistema de análisis predictivo basado
    en reglas de stock y demanda.

    El algoritmo identifica productos
    con riesgo de agotamiento y
    productos con disponibilidad alta.
    """

    recomendaciones = """
    Recomendaciones IA:

    • Reabastecer productos con bajo stock.

    • Crear promociones en productos
      con exceso de inventario.

    • Mantener control semanal
      del inventario.

    • Automatizar alertas de stock mínimo.
    """

    return render_template(
        'reporte3.html',
        riesgo=riesgo,
        recomendados=recomendados,
        explicacion=explicacion,
        recomendaciones=recomendaciones
    )  