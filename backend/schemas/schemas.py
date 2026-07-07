from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional
from backend.models.models import EstadoLote, NivelAlerta, RolUsuario


# ── Schemas de Usuario ───────────────────────────────────────────────────────
class UsuarioCrear(BaseModel):
    nombre:   str
    email:    EmailStr
    password: str
    rol:      RolUsuario = RolUsuario.OPERADOR


class UsuarioRespuesta(BaseModel):
    id:        int
    nombre:    str
    email:     str
    rol:       RolUsuario
    creado_en: Optional[datetime]

    model_config = {"from_attributes": True}


class TokenRespuesta(BaseModel):
    access_token: str
    token_type:   str = "bearer"


# ── Schemas de Lote ──────────────────────────────────────────────────────────
class LoteCrear(BaseModel):
    codigo:            str
    producto:          str
    categoria:         str
    cantidad:          float
    unidad:            str = "kg"
    proveedor:         str
    fecha_ingreso:     date
    fecha_vencimiento: date
    ubicacion:         str
    costo_unitario:    float = 0.0

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, v):
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        return v

    @field_validator("fecha_vencimiento")
    @classmethod
    def vencimiento_futuro(cls, v, info):
        ingreso = info.data.get("fecha_ingreso")
        if ingreso and v <= ingreso:
            raise ValueError("La fecha de vencimiento debe ser posterior a la fecha de ingreso.")
        return v


class LoteActualizar(BaseModel):
    cantidad:   Optional[float] = None
    ubicacion:  Optional[str]   = None
    estado:     Optional[EstadoLote] = None


class LoteRespuesta(BaseModel):
    id:                int
    codigo:            str
    producto:          str
    categoria:         str
    cantidad:          float
    unidad:            str
    proveedor:         str
    fecha_ingreso:     date
    fecha_vencimiento: date
    ubicacion:         str
    estado:            EstadoLote
    costo_unitario:    float
    dias_para_vencer:  Optional[int] = None
    nivel_alerta:      Optional[NivelAlerta] = None

    model_config = {"from_attributes": True}


# ── Schemas de Alerta ────────────────────────────────────────────────────────
class AlertaRespuesta(BaseModel):
    id:             int
    lote_id:        int
    nivel:          NivelAlerta
    dias_restantes: int
    mensaje:        str
    leida:          int
    creado_en:      Optional[datetime]
    producto:       Optional[str] = None

    model_config = {"from_attributes": True}


# ── Schema Dashboard ─────────────────────────────────────────────────────────
class DashboardRespuesta(BaseModel):
    total_lotes:       int
    lotes_en_stock:    int
    alertas_rojas:     int
    alertas_amarillas: int
    lotes_vencidos:    int
    merma_valorizada:  float
