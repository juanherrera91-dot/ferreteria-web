from flask import Flask

from flask_appbuilder.extensions import db
from .extensions import appbuilder


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    with app.app_context():
        appbuilder.init_app(app)
        db.create_all()
        # Registering the views and APIs
        ...
    return app
from .views import *

appbuilder.add_view(
    CategoriaView,
    "Categorias",
    icon="fa-folder",
    category="Ferreteria"
)

appbuilder.add_view(
    ProductoView,
    "Productos",
    icon="fa-box",
    category="Ferreteria"
)

appbuilder.add_view(
    VentaView,
    "Ventas",
    icon="fa-shopping-cart",
    category="Ferreteria"
)

appbuilder.add_view(
    DetalleVentaView,
    "Detalle Venta",
    icon="fa-list",
    category="Ferreteria"
)