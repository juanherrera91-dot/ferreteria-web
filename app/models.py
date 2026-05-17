from flask_sqlalchemy import SQLAlchemy
from flask_appbuilder import Model
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, Integer, String, Float, Date

class Categoria(Model):
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)

    productos = relationship("Producto", back_populates="categoria")

    def __repr__(self):
        return self.nombre


class Producto(Model):
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    precio = Column(Float)
    stock = Column(Integer)

    categoria_id = Column(Integer, ForeignKey('categoria.id'))
    categoria = relationship("Categoria", back_populates="productos")

    detalles = relationship("DetalleVenta", back_populates="producto")

    def __repr__(self):
        return self.nombre


class Venta(Model):
    id = Column(Integer, primary_key=True)
    fecha = Column(Date)

    detalles = relationship("DetalleVenta", back_populates="venta")

    def __repr__(self):
        return str(self.id)


class DetalleVenta(Model):
    id = Column(Integer, primary_key=True)

    venta_id = Column(Integer, ForeignKey('venta.id'))
    producto_id = Column(Integer, ForeignKey('producto.id'))

    cantidad = Column(Integer)
    subtotal = Column(Float)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles")