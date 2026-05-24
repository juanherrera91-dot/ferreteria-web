import sys
import os

# Asegura que Python reconozca la carpeta raíz del proyecto
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.database import db
from app.models import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    username_admin = "admin"
    password_plana = "admin123"  # Contraseña que usarás para entrar

    # Buscamos al usuario que ya existe
    usuario = Usuario.query.filter_by(username=username_admin).first()
    
    if usuario:
        # Encriptamos la nueva contraseña de forma segura
        usuario.password = generate_password_hash(password_plana)
        db.session.commit()
        
        print("==================================================")
        print(f" ¡Contraseña de '{username_admin}' actualizada con éxito!")
        print(f" Tu nueva contraseña es: {password_plana}")
        print("==================================================")
    else:
        print("El usuario no existía (ejecuta el script anterior).")