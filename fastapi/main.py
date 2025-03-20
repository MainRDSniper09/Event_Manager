from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from backend.apps.eventos.routes import router as eventos_router
from .database import engine, Base, SessionLocal
from .routes.routes import router
from .models import Rol

app = FastAPI()

#Configurar la carpeta frontend
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Configurar Jinja2 para renderizar plantillas desde la carpeta frontend
templates = Jinja2Templates(directory="frontend")

# Configurar Jinja2 y archivos estáticos
templates = Jinja2Templates(directory="backend/templates")
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Crear tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

# Incluir rutas de la API
app.include_router(router)
# Registrar el router de eventos
app.include_router(eventos_router, prefix="/eventos")

# 📌 Montar la carpeta frontend para servir archivos estáticos
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# 📌 Servir la página principal
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
