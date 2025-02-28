from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .database import engine, Base, SessionLocal
from .routes import router
from .models import Rol

app = FastAPI()

# Crear tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

# Incluir rutas de la API
app.include_router(router)

# 📌 Montar la carpeta frontend para servir archivos estáticos
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# 📌 Servir la página principal
@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")

# 📌 Servir la página de eventos
@app.get("/eventos.html")
def serve_eventos():
    return FileResponse("frontend/eventos.html")

# 🚀 Crear roles si no existen
def crear_roles():
    db = SessionLocal()
    if not db.query(Rol).filter(Rol.nombre == "admin").first():
        db.add(Rol(nombre="admin"))
    if not db.query(Rol).filter(Rol.nombre == "usuario").first():
        db.add(Rol(nombre="usuario"))
    db.commit()
    db.close()

# Ejecutar la creación de roles
crear_roles()
