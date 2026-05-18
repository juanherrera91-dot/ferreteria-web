from flask_appbuilder import Model
from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime


class Categoria(Model):
    __tablename__ = "categoria"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    imagen = Column(String(255), nullable=True)
    estado = Column(Boolean, nullable=True)

    creado_en = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    

    actualizado_en = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    productos = relationship(
        "Producto",
        back_populates="categorias"
    )

    def __repr__(self):
        return self.nombre


class Producto(Model):
    __tablename__ = "producto"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=True)
    categoria_id = Column(Integer, ForeignKey("categoria.id"), nullable=False)
    imagen = Column(String(255), nullable=True)
    estado = Column(Boolean, nullable=True)

    creado_en = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    actualizado_en = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    categorias = relationship(
        "Categoria",
        back_populates="productos"
    )

    def __repr__(self):
        return self.nombre