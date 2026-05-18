from .extensions import appbuilder
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface

from .models import Categoria, Producto

from flask import request
from wtforms import FileField

import os
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = "app/static/uploads"


class CategoriaModelView(ModelView):

    datamodel = SQLAInterface(Categoria)

    label_columns = {
        "nombre": "Nombre",
        "descripcion": "Descripcion",
        "imagen": "Imagen",
        "estado": "Estado",
        "creado_en": "Creado en",
        "actualizado_en": "Actualizado en"
    }

    list_columns = [
        "nombre",
        "descripcion",
        "estado",
        "creado_en",
        "actualizado_en"
    ]

    add_columns = [
        "nombre",
        "descripcion",
        "estado"
    ]

    edit_columns = [
        "nombre",
        "descripcion",
        "estado"
    ]


class ProductoModelView(ModelView):

    datamodel = SQLAInterface(Producto)

    label_columns = {
        "nombre": "Nombre",
        "descripcion": "Descripcion",
        "precio": "Precio",
        "categorias": "Categoria",
        "imagen": "Imagen",
        "estado": "Estado",
        "creado_en": "Creado en",
        "actualizado_en": "Actualizado en"
    }

    # CAMPO PARA SUBIR IMAGEN
    add_form_extra_fields = {
        "archivo_imagen": FileField("Seleccionar Imagen")
    }

    edit_form_extra_fields = {
        "archivo_imagen": FileField("Seleccionar Imagen")
    }

    list_columns = [
        "nombre",
        "precio",
        "categorias",
        "estado",
        "creado_en",
        "actualizado_en"
    ]

    add_columns = [
        "nombre",
        "descripcion",
        "precio",
        "categorias",
        "archivo_imagen",
        "estado"
    ]

    edit_columns = [
        "nombre",
        "descripcion",
        "precio",
        "categorias",
        "archivo_imagen",
        "estado"
    ]

    show_columns = [
        "nombre",
        "descripcion",
        "precio",
        "imagen",
        "estado",
        "creado_en",
        "actualizado_en"
    ]

    # GUARDAR IMAGEN AL CREAR
    def pre_add(self, item):

        imagen = request.files.get("archivo_imagen")

        if imagen and imagen.filename != "":

            nombre_imagen = secure_filename(imagen.filename)

            ruta = os.path.join(
                UPLOAD_FOLDER,
                nombre_imagen
            )

            imagen.save(ruta)

            item.imagen = nombre_imagen

    # GUARDAR IMAGEN AL EDITAR
    def pre_update(self, item):

        imagen = request.files.get("archivo_imagen")

        if imagen and imagen.filename != "":

            nombre_imagen = secure_filename(imagen.filename)

            ruta = os.path.join(
                UPLOAD_FOLDER,
                nombre_imagen
            )

            imagen.save(ruta)

            item.imagen = nombre_imagen


appbuilder.add_view(
    CategoriaModelView,
    "Categorias",
    icon="fa-info",
    category="Configuraciones",
    category_icon="fa-info"
)

appbuilder.add_view(
    ProductoModelView,
    "Productos",
    icon="fa-info",
    category="Configuraciones",
    category_icon="fa-info"
)