from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 📌 Tabla intermedia para la relación Many-to-Many entre Usuario y Evento
usuarios_eventos = Table(
    "usuarios_eventos",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id"), primary_key=True),
    Column("evento_id", Integer, ForeignKey("eventos.id"), primary_key=True)
)


class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)

    # Relación con Usuario
    usuarios = relationship("Usuario", back_populates="rol")

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id"))

    # Relación con Rol
    rol = relationship("Rol", back_populates="usuarios")

    # Relación con eventos (organizados y registrados)
    eventos_organizados = relationship("Evento", back_populates="organizador")
    eventos_registrados = relationship("Evento", secondary=usuarios_eventos, back_populates="participantes")

    # 📌 Métodos de hashing de contraseña
    def verificar_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)
    lugar = Column(String, nullable=False)
    organizador_id = Column(Integer, ForeignKey("usuarios.id"))

    # Relación con Usuario (organizador y participantes)
    organizador = relationship("Usuario", back_populates="eventos_organizados")
    participantes = relationship("Usuario", secondary=usuarios_eventos, back_populates="eventos_registrados")
