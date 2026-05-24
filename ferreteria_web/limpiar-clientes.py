from app import create_app
from app.database import db
from app.models import Cliente

app = create_app()
with app.app_context():
    # Opción A: Convierte todos los vacíos antiguos en nulos reales para desbloquear MySQL
    clientes_vacios = Cliente.query.filter(Cliente.ci_nit == "").all()
    for c in clientes_vacios:
        c.ci_nit = None
    db.session.commit()
    print("¡Base de datos optimizada y corregida con éxito!")
    
    # Opción B (Si solo quieres vaciar la lista de pruebas y empezar de cero):
    # Cliente.query.delete()
    # db.session.commit()