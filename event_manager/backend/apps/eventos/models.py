from django.db import models

# Create your models here.
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from fastapi.database import Base

class Evento(Base):
    __tablename__ = "eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    descripcion = Column(String)
    fecha = Column(DateTime)
    lugar = Column(String)
    organizador_id = Column(Integer, ForeignKey("usuarios.id"))

    organizador = relationship("Usuario", back_populates="eventos")
