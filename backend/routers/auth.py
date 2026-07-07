from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.models import Usuario
from backend.schemas.schemas import UsuarioCrear, UsuarioRespuesta, TokenRespuesta
from backend.routers.auth_utils import hashear_password, verificar_password, crear_token

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioRespuesta, status_code=201)
def registrar_usuario(datos: UsuarioCrear, db: Session = Depends(get_db)):
    """Registra un nuevo usuario en el sistema."""
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un usuario con el email '{datos.email}'."
        )
    nuevo = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        hashed_password=hashear_password(datos.password),
        rol=datos.rol
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.post("/login", response_model=TokenRespuesta)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Autentica al usuario y retorna un JWT válido por 8 horas."""
    usuario = db.query(Usuario).filter(Usuario.email == form.username).first()
    if not usuario or not verificar_password(form.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = crear_token({"sub": usuario.email, "rol": usuario.rol})
    return {"access_token": token, "token_type": "bearer"}
