from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.database import get_db
from backend.models.models import Lote, EstadoLote
from backend.schemas.schemas import LoteCrear, LoteActualizar, LoteRespuesta
from backend.models.motor_alertas import evaluar_lote
from backend.routers.auth_utils import obtener_usuario_actual
from backend.models.models import Usuario

router = APIRouter(prefix="/api/lotes", tags=["Gestión de Lotes"])


def _enriquecer_lote(lote: Lote) -> dict:
    """Agrega días para vencer y nivel de alerta al objeto lote."""
    evaluacion = evaluar_lote(lote.fecha_vencimiento, lote.producto)
    data = {c.name: getattr(lote, c.name) for c in lote.__table__.columns}
    data["dias_para_vencer"] = evaluacion["dias_para_vencer"]
    data["nivel_alerta"]     = evaluacion["nivel_alerta"]
    return data


@router.post("/", response_model=LoteRespuesta, status_code=201)
def crear_lote(
    datos: LoteCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    """Registra un nuevo lote de producto perecible."""
    if db.query(Lote).filter(Lote.codigo == datos.codigo).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un lote con el código '{datos.codigo}'."
        )
    lote = Lote(**datos.model_dump())
    lote.estado = EstadoLote.EN_STOCK
    db.add(lote)
    db.commit()
    db.refresh(lote)
    return _enriquecer_lote(lote)


@router.get("/", response_model=List[LoteRespuesta])
def listar_lotes(
    categoria: Optional[str] = Query(None),
    estado: Optional[EstadoLote] = Query(None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    """Lista todos los lotes con filtros opcionales por categoría y estado."""
    query = db.query(Lote)
    if categoria:
        query = query.filter(Lote.categoria.ilike(f"%{categoria}%"))
    if estado:
        query = query.filter(Lote.estado == estado)
    lotes = query.order_by(Lote.fecha_vencimiento.asc()).all()
    return [_enriquecer_lote(l) for l in lotes]


@router.get("/{lote_id}", response_model=LoteRespuesta)
def obtener_lote(
    lote_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    """Obtiene el detalle de un lote por su ID."""
    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail=f"Lote con ID {lote_id} no encontrado.")
    return _enriquecer_lote(lote)


@router.put("/{lote_id}", response_model=LoteRespuesta)
def actualizar_lote(
    lote_id: int,
    datos: LoteActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    """Actualiza cantidad, ubicación o estado de un lote."""
    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail=f"Lote con ID {lote_id} no encontrado.")
    for campo, valor in datos.model_dump(exclude_none=True).items():
        setattr(lote, campo, valor)
    db.commit()
    db.refresh(lote)
    return _enriquecer_lote(lote)


@router.delete("/{lote_id}", status_code=204)
def dar_de_baja_lote(
    lote_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    """Da de baja un lote (cambia estado a DADO_DE_BAJA, no elimina físicamente)."""
    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail=f"Lote con ID {lote_id} no encontrado.")
    lote.estado = EstadoLote.DADO_DE_BAJA
    db.commit()
