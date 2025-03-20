from sqlalchemy.orm import Session
from . import models, schemas

# 📌 Crear un evento
def crear_evento(db: Session, evento: schemas.EventoCreate, organizador_id: int):
    nuevo_evento = models.Evento(**evento.dict(), organizador_id=organizador_id)
    db.add(nuevo_evento)
    db.commit()
    db.refresh(nuevo_evento)
    return nuevo_evento

# 📌 Obtener todos los eventos
def obtener_eventos(db: Session):
    return db.query(models.Evento).all()

# 📌 Obtener un evento por ID
def obtener_evento(db: Session, evento_id: int):
    return db.query(models.Evento).filter(models.Evento.id == evento_id).first()

# 📌 Actualizar evento
def actualizar_evento(db: Session, evento_id: int, evento_data: schemas.EventoCreate):
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if evento:
        for key, value in evento_data.dict().items():
            setattr(evento, key, value)
        db.commit()
        db.refresh(evento)
    return evento

# 📌 Eliminar evento
def eliminar_evento(db: Session, evento_id: int):
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if evento:
        db.delete(evento)
        db.commit()
    return evento

