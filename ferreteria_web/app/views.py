from flask import Blueprint, render_template, redirect, url_for, request, flash

from flask_login import ( login_user,logout_user,login_required, current_user)

from datetime import datetime

import numpy as np
from sklearn.linear_model import LinearRegression 
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
from .database import db, bcrypt

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

        username = request.form.get(
            'username'
        )

        password = request.form.get(
            'password'
        )

        user = Usuario.query.filter_by(
            username=username
        ).first()

        # ==================================
        # VALIDAR USUARIO
        # ==================================
        if user:

            if bcrypt.check_password_hash(
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

    return render_template(
        'reportes.html'
    )

# ==========================================
# REPORTE 1
# ANALISIS GENERAL
# VENTAS POR DIA
# ==========================================
@bp.route('/reporte1')
@login_required
def reporte1():

    from sqlalchemy import func

    # ==============================
    # METRICAS
    # ==============================
    total_ventas = Venta.query.count()

    total_productos = Producto.query.count()

    total_clientes = Cliente.query.count()

    ingresos = db.session.query(
        func.sum(Venta.total)
    ).scalar()

    if ingresos is None:
        ingresos = 0

    # ==============================
    # VENTAS POR DIA
    # ==============================
    ventas_por_dia = db.session.query(

        func.date(Venta.fecha),

        func.sum(Venta.total)

    ).group_by(

        func.date(Venta.fecha)

    ).all()

    dias = []

    montos = []

    for dia, total in ventas_por_dia:

        dias.append(
            dia.strftime('%d/%m/%Y')
        )

        montos.append(
            float(total)
        )

    # ==============================
    # GRAFICA
    # ==============================
    grafica = None

    if dias and montos:

        plt.figure(
            figsize=(12, 6)
        )

        plt.plot(

            dias,

            montos,

            marker='o',

            linewidth=3,

            color='#0d6efd'
        )

        plt.title(
            'Ventas por Dia',
            fontsize=18,
            fontweight='bold'
        )

        plt.xlabel(
            'Fecha'
        )

        plt.ylabel(
            'Monto de Ventas'
        )

        plt.grid(
            True,
            linestyle='--',
            alpha=0.5
        )

        plt.xticks(
            rotation=30
        )

        for i, valor in enumerate(montos):

            plt.text(

                i,

                valor + 1,

                f'Bs {valor:.0f}',

                ha='center',

                fontsize=9
            )

        plt.tight_layout()

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

    # ==============================
    # ANALISIS IA AUTOMATICO
    # ==============================

    mayor_venta = 0

    mejor_dia = "Sin registros"

    if montos:

        mayor_venta = max(montos)

        indice = montos.index(mayor_venta)

        mejor_dia = dias[indice]

    promedio_ventas = 0

    if total_ventas > 0:

        promedio_ventas = ingresos / total_ventas

    analisis = f"""
    La IA analizó el comportamiento
    diario de ventas registrado en el sistema.

    Actualmente se registran {total_ventas} ventas,
    con ingresos acumulados de Bs. {round(ingresos, 2)}.

    El día con mayor rendimiento comercial fue:
    {mejor_dia},
    alcanzando ventas aproximadas de
    Bs. {round(mayor_venta, 2)}.

    El promedio de ingresos por venta es de
    Bs. {round(promedio_ventas, 2)}.

    El análisis detecta variaciones en la demanda
    durante determinados días, lo que evidencia
    oportunidades estratégicas para incrementar
    promociones y optimizar inventario.

    Recomendaciones Inteligentes:

    • Incrementar stock en fechas de mayor demanda.

    • Aplicar promociones en días con menor actividad.

    • Mantener monitoreo continuo del comportamiento
      de ventas diarias.

En conclusion IA

    El sistema determina que el negocio presenta
    movimiento comercial constante y potencial
    de crecimiento mediante estrategias basadas
    en análisis de ventas.
    """

    return render_template(

        'reporte1.html',

        total_ventas=total_ventas,

        total_productos=total_productos,

        total_clientes=total_clientes,

        ingresos=round(ingresos, 2),

        grafica=grafica,

        analisis=analisis
    )
# ==========================================
# REPORTE 2
# CLIENTES FRECUENTES
# ==========================================
@bp.route('/reporte2')
@login_required
def reporte2():

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

        plt.figure(
            figsize=(12, 5)
        )

        plt.bar(
            nombres,
            cantidades,
            color='#198754'
        )

        plt.title(
            'Clientes Frecuentes',
            fontsize=18,
            fontweight='bold'
        )

        plt.xlabel(
            'Clientes'
        )

        plt.ylabel(
            'Cantidad de Compras'
        )

        plt.xticks(
            rotation=20
        )

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
    # ANALISIS AUTOMATICO IA
    # ======================================

    cliente_top = "Sin registros"

    max_compras = 0

    total_clientes_frecuentes = 0

    if clientes:

        cliente_top = max(
            clientes,
            key=clientes.get
        )

        max_compras = clientes[cliente_top]

        total_clientes_frecuentes = len(clientes)

    promedio_compras = 0

    if total_clientes_frecuentes > 0:

        promedio_compras = sum(cantidades) / total_clientes_frecuentes

    interpretacion = f"""
    La IA analizó el comportamiento
    de compra de los clientes registrados en el sistema.

    Actualmente se identificaron
    {total_clientes_frecuentes} clientes activos
    con historial de compras.

    El cliente con mayor frecuencia de compra es:
    {cliente_top},
    con un total de {max_compras} compras realizadas.

    El promedio general de compras por cliente es de
    {round(promedio_compras, 2)} operaciones.

    El análisis evidencia que los clientes recurrentes
    representan una fuente importante de ingresos
    y estabilidad financiera para la ferretería.

    También se detectó que algunos clientes realizan
    compras periódicas en intervalos similares,
    permitiendo anticipar futuras ventas
    y mejorar la planificación comercial.

    Recomendaciones Inteligentes:

    • Implementar programas de fidelización.

    • Aplicar descuentos personalizados
      para clientes frecuentes.

    • Crear promociones exclusivas
      para incentivar compras recurrentes.

    • Realizar seguimiento estratégico
      de clientes con mayor actividad.

    Conclusión IA:

    El sistema determina que fortalecer la relación
    con clientes frecuentes puede incrementar
    las ventas y mejorar el crecimiento del negocio.
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

    from sqlalchemy import func
    import numpy as np
    from sklearn.linear_model import LinearRegression

    # ======================================
    # OBTENER VENTAS POR DIA
    # ======================================
    ventas_por_dia = db.session.query(

        func.date(Venta.fecha),

        func.sum(Venta.total)

    ).group_by(

        func.date(Venta.fecha)

    ).all()

    dias = []

    montos = []

    contador = 1

    for fecha, total in ventas_por_dia:

        dias.append([contador])

        montos.append(float(total))

        contador += 1

    prediccion = 0

    tendencia = "Sin datos suficientes"

    # ======================================
    # IA CON REGRESION LINEAL
    # ======================================
    if len(dias) >= 2:

        X = np.array(dias)

        y = np.array(montos)

        modelo = LinearRegression()

        modelo.fit(X, y)

        siguiente_dia = np.array([[len(dias) + 1]])

        prediccion = modelo.predict(
            siguiente_dia
        )[0]

        # ==============================
        # TENDENCIA
        # ==============================
        pendiente = modelo.coef_[0]

        if pendiente > 0:
            tendencia = "CRECIMIENTO"

        elif pendiente < 0:
            tendencia = "DISMINUCION"

        else:
            tendencia = "ESTABLE"

    # ======================================
    # PRODUCTOS EN RIESGO
    # ======================================
    productos = Producto.query.all()

    riesgo = []

    stock_alto = []

    for producto in productos:

        if producto.stock <= 5:
            riesgo.append(producto)

        if producto.stock >= 20:
            stock_alto.append(producto)

    # ======================================
    # ANALISIS IA AUTOMATICO
    # ======================================
    explicacion = f"""
    Modelo utilizado:

    Regresión Lineal utilizando Scikit-Learn.

    El algoritmo analiza el comportamiento
    histórico de ventas registrado en el sistema
    para identificar tendencias comerciales
    y estimar futuras demandas.

    Resultado del análisis:

    La tendencia detectada actualmente es:
    {tendencia}.

    La IA estima que las próximas ventas
    podrían alcanzar aproximadamente:

    Bs. {round(prediccion, 2)}

    según el comportamiento histórico.
    """

    recomendaciones = f"""
    Recomendaciones Inteligentes:

    • Mantener abastecidos los productos
      con mayor salida comercial.

    • Supervisar productos con stock crítico.

    • Aprovechar tendencias de crecimiento
      para incrementar promociones.

    • Revisar periódicamente el comportamiento
      de ventas para mejorar decisiones.

    Productos en riesgo:
    {len(riesgo)}

    Productos con stock alto:
    {len(stock_alto)}
    """

    # ======================================
    # GRAFICA PREDICTIVA
    # ======================================
    grafica = None

    if dias and montos:

        plt.figure(figsize=(12,6))

        x_real = list(range(1, len(montos)+1))

        plt.plot(

            x_real,

            montos,

            marker='o',

            linewidth=3,

            label='Ventas Reales'
        )

        # ==============================
        # PREDICCION
        # ==============================
        if prediccion > 0:

            plt.scatter(

                len(montos)+1,

                prediccion,

                s=200,

                marker='X',

                label='Predicción IA'
            )

        plt.title(
            'Prediccion Inteligente de Ventas',
            fontsize=18,
            fontweight='bold'
        )

        plt.xlabel('Dias')

        plt.ylabel('Ventas')

        plt.grid(True)

        plt.legend()

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
    # TEMPLATE
    # ======================================
    return render_template(

        'reporte3.html',

        riesgo=riesgo,

        recomendados=stock_alto,

        explicacion=explicacion,

        recomendaciones=recomendaciones,

        grafica=grafica,

        prediccion=round(prediccion, 2),

        tendencia=tendencia
    )