from .extensions import db
from datetime import datetime


# 👤 USUARIO
class Usuario(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    ventas = db.relationship(
        'Venta',
        backref='usuario'
    )


# 📁 CATEGORIA
class Categoria(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    productos = db.relationship(
        'Producto',
        back_populates='categoria'
    )


# 🔧 PRODUCTO
class Producto(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    precio = db.Column(
        db.Float,
        nullable=False
    )

    stock = db.Column(
        db.Integer,
        nullable=False
    )

    # ✅ FECHA DE REGISTRO
    fecha_registro = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # ✅ RELACION CON CATEGORIA
    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey('categoria.id')
    )

    categoria = db.relationship(
        'Categoria',
        back_populates='productos'
    )

    # ✅ RELACION CON DETALLE VENTA
    detalles = db.relationship(
        'DetalleVenta',
        back_populates='producto'
    )


# 🧾 VENTA
class Venta(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id')
    )

    detalles = db.relationship(
        'DetalleVenta',
        back_populates='venta'
    )


# 📄 DETALLE VENTA
class DetalleVenta(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    cantidad = db.Column(
        db.Integer,
        nullable=False
    )

    subtotal = db.Column(
        db.Float,
        nullable=False
    )

    venta_id = db.Column(
        db.Integer,
        db.ForeignKey('venta.id')
    )

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey('producto.id')
    )

    venta = db.relationship(
        'Venta',
        back_populates='detalles'
    )

    producto = db.relationship(
        'Producto',
        back_populates='detalles'
    )