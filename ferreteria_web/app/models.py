from .database import db
from datetime import datetime
from flask_login import UserMixin


# ==================================================
# 👤 USUARIO
# ==================================================
class Usuario(UserMixin, db.Model):

    __tablename__ = 'usuario'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

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
        back_populates='usuario',
        cascade='all, delete-orphan'
    )

    def __repr__(self):

        return f'<Usuario {self.username}>'


# ==================================================
# 👥 CLIENTE
# ==================================================
class Cliente(db.Model):

    __tablename__ = 'cliente'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    ci_nit = db.Column(
        db.String(50),
        unique=True
    )

    telefono = db.Column(
        db.String(30)
    )

    direccion = db.Column(
        db.String(200)
    )

    fecha_registro = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    ventas = db.relationship(
        'Venta',
        back_populates='cliente',
        cascade='all, delete-orphan'
    )

    def __repr__(self):

        return f'<Cliente {self.nombre}>'


# ==================================================
# 📦 CATEGORÍA
# ==================================================
class Categoria(db.Model):

    __tablename__ = 'categoria'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    productos = db.relationship(
        'Producto',
        back_populates='categoria',
        cascade='all, delete-orphan'
    )

    def __repr__(self):

        return f'<Categoria {self.nombre}>'


# ==================================================
# 🔧 PRODUCTO
# ==================================================
class Producto(db.Model):

    __tablename__ = 'producto'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    precio = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    stock = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    fecha_registro = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey('categoria.id'),
        nullable=False
    )

    categoria = db.relationship(
        'Categoria',
        back_populates='productos'
    )

    detalles = db.relationship(
        'DetalleVenta',
        back_populates='producto',
        cascade='all, delete-orphan'
    )

    def __repr__(self):

        return f'<Producto {self.nombre}>'


# ==================================================
# 💰 VENTA
# ==================================================
class Venta(db.Model):

    __tablename__ = 'venta'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    total = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id'),
        nullable=False
    )

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey('cliente.id'),
        nullable=False
    )

    usuario = db.relationship(
        'Usuario',
        back_populates='ventas'
    )

    cliente = db.relationship(
        'Cliente',
        back_populates='ventas'
    )

    detalles = db.relationship(
        'DetalleVenta',
        back_populates='venta',
        cascade='all, delete-orphan'
    )

    def __repr__(self):

        return f'<Venta {self.id}>'


# ==================================================
# 🛒 DETALLE VENTA
# ==================================================
class DetalleVenta(db.Model):

    __tablename__ = 'detalle_venta'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    venta_id = db.Column(
        db.Integer,
        db.ForeignKey('venta.id'),
        nullable=False
    )

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey('producto.id'),
        nullable=False
    )

    cantidad = db.Column(
        db.Integer,
        nullable=False
    )

    precio_unitario = db.Column(
        db.Float,
        nullable=False
    )

    subtotal = db.Column(
        db.Float,
        nullable=False
    )

    venta = db.relationship(
        'Venta',
        back_populates='detalles'
    )

    producto = db.relationship(
        'Producto',
        back_populates='detalles'
    )

    def __repr__(self):

        return f'<DetalleVenta {self.id}>'