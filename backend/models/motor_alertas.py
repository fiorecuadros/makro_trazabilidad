from datetime import date
from backend.models.models import NivelAlerta


def calcular_dias_vencimiento(fecha_vencimiento: date) -> int:
    """
    Calcula los días que restan hasta el vencimiento del lote.
    Retorna valor negativo si el producto ya venció.
    """
    if fecha_vencimiento is None:
        raise ValueError("La fecha de vencimiento no puede ser None.")
    return (fecha_vencimiento - date.today()).days


def clasificar_alerta(dias: int) -> NivelAlerta:
    """
    Clasifica el nivel de alerta según los días restantes para vencer.

    Reglas de negocio (definidas con el área de almacén de Makro Chincha):
      - dias <= 3  → ALERTA_ROJA    (acción inmediata requerida)
      - dias <= 7  → ALERTA_AMARILLA (monitoreo prioritario)
      - dias >  7  → SIN_ALERTA
    """
    if dias <= 3:
        return NivelAlerta.ALERTA_ROJA
    elif dias <= 7:
        return NivelAlerta.ALERTA_AMARILLA
    else:
        return NivelAlerta.SIN_ALERTA


def generar_mensaje_alerta(nivel: NivelAlerta, producto: str, dias: int) -> str:
    """Genera el mensaje descriptivo de la alerta para el operador."""
    if nivel == NivelAlerta.ALERTA_ROJA:
        if dias <= 0:
            return f"⛔ VENCIDO: El lote de '{producto}' venció hace {abs(dias)} día(s). Retirar inmediatamente."
        return f"🔴 ALERTA ROJA: El lote de '{producto}' vence en {dias} día(s). Acción inmediata requerida."
    elif nivel == NivelAlerta.ALERTA_AMARILLA:
        return f"🟡 ALERTA AMARILLA: El lote de '{producto}' vence en {dias} día(s). Monitorear y priorizar rotación."
    return f"✅ El lote de '{producto}' está dentro del rango seguro ({dias} días para vencer)."


def evaluar_lote(fecha_vencimiento: date, producto: str) -> dict:
    """
    Evalúa un lote completo y retorna su nivel de alerta, días y mensaje.
    Función principal usada por el motor de alertas del sistema.
    """
    dias   = calcular_dias_vencimiento(fecha_vencimiento)
    nivel  = clasificar_alerta(dias)
    mensaje = generar_mensaje_alerta(nivel, producto, dias)
    return {
        "dias_para_vencer": dias,
        "nivel_alerta":     nivel,
        "mensaje":          mensaje
    }
