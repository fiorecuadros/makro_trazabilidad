from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from backend.database.database import Base


class EstadoLote(str, enum.Enum):
    REGISTRADO  = "REGISTRADO"
    EN_STOCK    = "EN_STOCK"
    POR_VENCER  = "POR_VENCER"
    VENCIDO     = "VENCIDO"
    DADO_DE_BAJA = "DADO_DE_BAJA"


class NivelAlerta(str, enum.Enum):
    SIN_ALERTA      = "SIN_ALERTA"
    ALERTA_AMARILLA = "ALERTA_AMARILLA"
    ALERTA_ROJA     = "ALERTA_ROJA"


class RolUsuario(str, enum.Enum):
    OPERADOR       = "OPERADOR"
    ADMINISTRADOR  = "ADMINISTRADOR"


# ── Modelo Usuario ──────────────────────────────────────────────────────────
class Usuario(Base):
    __tablename__ = "usuarios"

    id              = Column(Integer, primary_key=True, index=True)
    nombre          = Column(String(100), nullable=False)
    email           = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    rol             = Column(Enum(RolUsuario), default=RolUsuario.OPERADOR)
    creado_en       = Column(DateTime(timezone=True), server_default=func.now())

    alertas = relationship("Alerta", back_populates="usuario")


# ── Modelo Lote ─────────────────────────────────────────────────────────────
class Lote(Base):
    __tablename__ = "lotes"

    id              = Column(Integer, primary_key=True, index=True)
    codigo          = Column(String(50), unique=True, index=True, nullable=False)
    producto        = Column(String(150), nullable=False)
    categoria       = Column(String(100), nullable=False)
    cantidad        = Column(Float, nullable=False)
    unidad          = Column(String(20), default="kg")
    proveedor       = Column(String(150), nullable=False)
    fecha_ingreso   = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    ubicacion       = Column(String(100), nullable=False)
    estado          = Column(Enum(EstadoLote), default=EstadoLote.REGISTRADO)
    costo_unitario  = Column(Float, default=0.0)
    creado_en       = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en  = Column(DateTime(timezone=True), onupdate=func.now())

    alertas = relationship("Alerta", back_populates="lote")


# ── Modelo Alerta ────────────────────────────────────────────────────────────
class Alerta(Base):
    __tablename__ = "alertas"

    id          = Column(Integer, primary_key=True, index=True)
    lote_id     = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    usuario_id  = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    nivel       = Column(Enum(NivelAlerta), nullable=False)
    dias_restantes = Column(Integer, nullable=False)
    mensaje     = Column(String(300), nullable=False)
    leida       = Column(Integer, default=0)  # 0=no leída, 1=leída
    creado_en   = Column(DateTime(timezone=True), server_default=func.now())

    lote    = relationship("Lote",    back_populates="alertas")
    usuario = relationship("Usuario", back_populates="alertas")
