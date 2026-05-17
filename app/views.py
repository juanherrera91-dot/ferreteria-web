from flask import current_app, render_template

from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface

from .models import Categoria, Producto, Venta, DetalleVenta

class CategoriaView(ModelView):
    datamodel = SQLAInterface(Categoria)

    list_columns = ['nombre']


class ProductoView(ModelView):
    datamodel = SQLAInterface(Producto)

    list_columns = ['nombre', 'precio', 'stock', 'categoria']


class VentaView(ModelView):
    datamodel = SQLAInterface(Venta)


class DetalleVentaView(ModelView):
    datamodel = SQLAInterface(DetalleVenta)


@current_app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )
