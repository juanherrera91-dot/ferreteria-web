from app import create_app
from app.extensions import db, bcrypt
from app.models import Usuario

app = create_app()

with app.app_context():

    password_encriptado = bcrypt.generate_password_hash(
        '123456'
    ).decode('utf-8')

    usuario = Usuario(
        username='admin',
        password=password_encriptado
    )

    db.session.add(usuario)
    db.session.commit()

    print("✅ Usuario creado correctamente")