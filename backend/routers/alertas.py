from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.models.models import Lote, EstadoLote, NivelAlerta
from backend.schemas.schemas import AlertaRespuesta, DashboardRespuesta
from backend.models.motor_alertas import evaluar_lote
from backend.routers.auth_utils import obtener_usuario_actual
from backend.models.models import Usuario

router = APIRouter(prefix="/api", tags=["Alertas y Dashboard"])


@router.get("/alertas", response_model=List[AlertaRespuesta])
def listar_alertas_activas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    """
    Evalúa todos los lotes activos y retorna los que tienen alerta.
    Las alertas se calculan en tiempo real al momento de la consulta.
    """
    lotes_activos = db.query(Lote).filter(
        Lote.estado.in_([EstadoLote.EN_STOCK, EstadoLote.POR_VENCER])
    ).all()

    alertas = []
    for lote in lotes_activos:
        evaluacion = evaluar_lote(lote.fecha_vencimiento, lote.producto)
        nivel = evaluacion["nivel_alerta"]
        if nivel != NivelAlerta.SIN_ALERTA:
            alertas.append({
                "id":             lote.id,
                "lote_id":        lote.id,
                "nivel":          nivel,
                "dias_restantes": evaluacion["dias_para_vencer"],
                "mensaje":        evaluacion["mensaje"],
                "leida":          0,
                "creado_en":      None,
                "producto":       lote.producto
            })

    # Ordenar: primero alertas rojas, luego amarillas
    alertas.sort(key=lambda a: (0 if a["nivel"] == NivelAlerta.ALERTA_ROJA else 1))
    return alertas


@router.get("/dashboard", response_model=DashboardRespuesta)
def obtener_dashboard(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    """
    Retorna los indicadores principales del dashboard de trazabilidad.
    Incluye conteo de alertas, lotes por estado y valorización de mermas.
    """
    todos_lotes = db.query(Lote).all()

    total        = len(todos_lotes)
    en_stock     = 0
    rojas        = 0
    amarillas    = 0
    vencidos     = 0
    merma_valor  = 0.0

    for lote in todos_lotes:
        if lote.estado == EstadoLote.EN_STOCK:
            en_stock += 1
            ev = evaluar_lote(lote.fecha_vencimiento, lote.producto)
            if ev["nivel_alerta"] == NivelAlerta.ALERTA_ROJA:
                rojas += 1
            elif ev["nivel_alerta"] == NivelAlerta.ALERTA_AMARILLA:
                amarillas += 1
        elif lote.estado in (EstadoLote.VENCIDO, EstadoLote.DADO_DE_BAJA):
            vencidos += 1
            merma_valor += lote.cantidad * lote.costo_unitario

    return DashboardRespuesta(
        total_lotes       = total,
        lotes_en_stock    = en_stock,
        alertas_rojas     = rojas,
        alertas_amarillas = amarillas,
        lotes_vencidos    = vencidos,
        merma_valorizada  = round(merma_valor, 2)
    )
