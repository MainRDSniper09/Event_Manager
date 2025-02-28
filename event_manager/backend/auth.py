from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from .database import SessionLocal
from .models import Usuario
from .schemas import TokenData

# Configuración de seguridad
SECRET_KEY = "clave_super_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Configuración de seguridad para OAuth2 y Hashing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependencia para obtener la sesión de la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para hashear contraseñas
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Función para verificar contraseñas
def verificar_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Error al verificar la contraseña: {e}")
        return False

# Genera un JWT Token
def crear_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Autenticación de usuario
def autenticar_usuario(db: Session, email: str, password: str):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        print("Usuario no encontrado")
        return False
    print(f"Contraseña almacenada en BD: {usuario.password}")  # Depuración
    if not verificar_password(password, usuario.password):
        print("Contraseña incorrecta")
        return False
    return usuario

# Obtiene el usuario autenticado
def obtener_usuario_actual(db: Session = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="No autenticado")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario