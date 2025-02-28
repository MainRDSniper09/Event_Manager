from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RolBase(BaseModel):
    nombre: str

class RolCreate(RolBase):
    pass

class RolResponse(RolBase):
    id: int

    class Config:
        from_attributes = True

class UsuarioBase(BaseModel):
    nombre: str
    email: str

class UsuarioCreate(UsuarioBase):
    password: str
    rol_id: Optional[int] = None  # Permitir asignar rol al crearlo

class UsuarioResponse(UsuarioBase):
    id: int
    rol_id: int
    eventos_organizados: list["EventoResponse"] = []  # Error aqui
    eventos_registrados: list["EventoResponse"] = []

    class Config:
        from_attributes = True

class EventoBase(BaseModel):
    nombre: str
    descripcion: str
    fecha: datetime
    lugar: str

class EventoCreate(EventoBase):
    organizador_id: int

class EventoResponse(EventoBase):
    id: int
    organizador_id: int
    organizador_nombre: str  # 📌 Nuevo campo para mostrar el organizador


    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class UsuarioLogin(BaseModel):
    email: str
    password: str


