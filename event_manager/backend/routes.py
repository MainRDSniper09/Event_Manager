from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models, schemas
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .auth import crear_token, autenticar_usuario, obtener_usuario_actual
from passlib.context import CryptContext

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependencia para obtener la sesión de la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📌 Función para verificar el rol del usuario
def verificar_rol(usuario: models.Usuario = Depends(obtener_usuario_actual), rol_requerido: str = "admin"):
    if usuario.rol.nombre != rol_requerido:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta ruta")
    return usuario

def verificar_organizador(evento_id: int, usuario: models.Usuario, db: Session):
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    if evento.organizador_id != usuario.id and usuario.rol.nombre != "admin":
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este evento")
    
    return evento

# 📌 Ruta para crear un usuario (con hashing)
@router.post("/usuarios/", response_model=schemas.UsuarioResponse)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Si no se especifica un rol, asignar "usuario"
    rol_usuario = db.query(models.Rol).filter(models.Rol.nombre == "usuario").first()
    if usuario.rol_id is None:
        usuario.rol_id = rol_usuario.id if rol_usuario else None

    if usuario.rol_id is None:
        raise HTTPException(status_code=400, detail="No se encontró el rol 'usuario' en la base de datos")

    hashed_password = pwd_context.hash(usuario.password)  
    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        password=hashed_password,  # Guardar la contraseña hasheada
        rol_id=usuario.rol_id
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

# 📌 Ruta para obtener todos los usuarios
@router.get("/usuarios/", response_model=list[schemas.UsuarioResponse])
def obtener_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()

# 📌 Ruta protegida para crear un evento (Solo Admins)
@router.post("/eventos/", response_model=schemas.EventoResponse)
def crear_evento(evento: schemas.EventoCreate, 
                usuario: models.Usuario = Depends(lambda u: verificar_rol(u, "admin")), 
                db: Session = Depends(get_db)):
    nuevo_evento = models.Evento(
        nombre=evento.nombre, 
        descripcion=evento.descripcion,
        fecha=evento.fecha, 
        lugar=evento.lugar, 
        organizador_id=usuario.id
    )
    db.add(nuevo_evento)
    db.commit()
    db.refresh(nuevo_evento)
    return nuevo_evento

# 📌 Ruta para obtener todos los eventos
@router.get("/eventos/", response_model=list[schemas.EventoResponse])
def obtener_eventos(db: Session = Depends(get_db)):
    eventos = db.query(models.Evento).all()
    
    eventos_respuesta = []
    for evento in eventos:
        eventos_respuesta.append({
            "id": evento.id,
            "nombre": evento.nombre,
            "descripcion": evento.descripcion,
            "fecha": evento.fecha,
            "lugar": evento.lugar,
            "organizador_id": evento.organizador_id,
            "organizador_nombre": evento.organizador.nombre  # 📌 Agregamos el nombre
        })
    
    return eventos_respuesta

# 📌 Ruta para crear un rol
@router.post("/roles/", response_model=schemas.RolResponse)
def crear_rol(rol: schemas.RolCreate, db: Session = Depends(get_db)):
    nuevo_rol = models.Rol(nombre=rol.nombre)
    db.add(nuevo_rol)
    db.commit()
    db.refresh(nuevo_rol)
    return nuevo_rol

# 📌 Ruta para obtener todos los roles
@router.get("/roles/", response_model=list[schemas.RolResponse])
def obtener_roles(db: Session = Depends(get_db)):
    return db.query(models.Rol).all()

# 📌 Ruta para iniciar sesión y obtener un token
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    # 📌 Agregar el rol del usuario en el token
    access_token = crear_token(data={"sub": usuario.email, "rol": usuario.rol.nombre})  

    return {"access_token": access_token, "token_type": "bearer"}

@router.put("/eventos/{evento_id}/", response_model=schemas.EventoResponse)
def actualizar_evento(evento_id: int, evento_data: schemas.EventoCreate, 
                    usuario: models.Usuario = Depends(obtener_usuario_actual), 
                    db: Session = Depends(get_db)):
    
    evento = verificar_organizador(evento_id, usuario, db)
    
    evento.nombre = evento_data.nombre
    evento.descripcion = evento_data.descripcion
    evento.fecha = evento_data.fecha
    evento.lugar = evento_data.lugar
    
    db.commit()
    db.refresh(evento)
    return evento

@router.delete("/eventos/{evento_id}/")
def eliminar_evento(evento_id: int, usuario: models.Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    
    evento = verificar_organizador(evento_id, usuario, db)
    
    db.delete(evento)
    db.commit()
    return {"mensaje": "Evento eliminado exitosamente"}

@router.get("/usuarios/{usuario_id}/eventos", response_model=list[schemas.EventoResponse])
def obtener_eventos_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario.eventos_registrados


