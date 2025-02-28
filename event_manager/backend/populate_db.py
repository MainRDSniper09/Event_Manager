from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend.models import Base, Usuario, Rol, Evento
from datetime import datetime

# 🔥 1. Eliminar y recrear la base de datos
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# 🔥 2. Crear una sesión
db = SessionLocal()

# 🔥 3. Insertar Roles
rol_admin = Rol(nombre="Administrador")
rol_usuario = Rol(nombre="Usuario")
db.add_all([rol_admin, rol_usuario])
db.commit()

# 🔥 4. Insertar Usuarios con contraseñas encriptadas
usuario1 = Usuario(nombre="Juan", email="juan@example.com", rol_id=rol_admin.id)
usuario1.set_password("1234")

usuario2 = Usuario(nombre="Ana", email="ana@example.com", rol_id=rol_usuario.id)
usuario2.set_password("5678")

db.add_all([usuario1, usuario2])
db.commit()

# 🔥 5. Insertar Eventos con fechas en formato datetime
evento1 = Evento(
    nombre="Conferencia Python", 
    descripcion="Charla sobre FastAPI", 
    fecha=datetime.strptime("2024-10-01 10:00:00", "%Y-%m-%d %H:%M:%S"),  # Convertir a datetime
    lugar="Auditorio 1", 
    organizador_id=usuario1.id
)

evento2 = Evento(
    nombre="Hackathon IA", 
    descripcion="Competencia de IA en 24 horas", 
    fecha=datetime.strptime("2024-11-05 08:00:00", "%Y-%m-%d %H:%M:%S"),  # Convertir a datetime
    lugar="Coworking Space", 
    organizador_id=usuario2.id
)

db.add_all([evento1, evento2])
db.commit()

# 🔥 6. Relacionar Usuarios con Eventos (asistentes)
evento1.participantes.append(usuario2)  # Ana asiste a la conferencia de Juan
evento2.participantes.append(usuario1)  # Juan asiste al hackathon de Ana

db.commit()

print("✅ Base de datos poblada con éxito.")

# Cerrar sesión
db.close()
