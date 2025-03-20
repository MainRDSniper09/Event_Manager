from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.database import SessionLocal # type: ignore
from . import crud, schemas, models
from fastapi.auth import crear_token, autenticar_usuario, obtener_usuario_actual
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📌 Obtener todos los eventos
@router.get("/", response_model=List[schemas.EventoResponse])
def listar_eventos(db: Session = Depends(get_db)):
    return crud.obtener_eventos(db)

# Obtener un evento por ID
@router.get("/{evento_id}", response_model=schemas.EventoResponse)
def ver_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = crud.obtener_evento(db, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return evento

# 📌 Crear un evento (solo admin)
@router.post("/", response_model=schemas.EventoResponse)
def crear_evento(evento: schemas.EventoCreate, usuario: models.Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    if usuario.rol.nombre != "admin":
        raise HTTPException(status_code=403, detail="No tienes permiso para crear eventos")
    return crud.crear_evento(db, evento, organizador_id=usuario.id)

# 📌 Actualizar un evento
@router.put("/{evento_id}", response_model=schemas.EventoResponse)
def actualizar_evento(evento_id: int, evento_data: schemas.EventoCreate, usuario: models.Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    evento = crud.obtener_evento(db, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    if evento.organizador_id != usuario.id and usuario.rol.nombre != "admin":
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este evento")
    return crud.actualizar_evento(db, evento_id, evento_data)

# 📌 Eliminar un evento
@router.delete("/{evento_id}/")
def eliminar_evento(evento_id: int, usuario: models.Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    evento = crud.obtener_evento(db, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    if evento.organizador_id != usuario.id and usuario.rol.nombre != "admin":
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este evento")
    crud.eliminar_evento(db, evento_id)
    return {"mensaje": "Evento eliminado exitosamente"}

