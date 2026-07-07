"""
Pruebas unitarias – Motor de Alertas Preventivas
Sistema de Trazabilidad Makro Chincha – 2026
Asignatura: Calidad y Pruebas de Software – UPSJB

Técnica aplicada: Análisis de Valores Límite (BVA) + Partición de Equivalencias
Framework: pytest
Metodología: AAA (Arrange – Act – Assert)
"""
import pytest
from datetime import date, timedelta
from backend.models.motor_alertas import (
    calcular_dias_vencimiento,
    clasificar_alerta,
    generar_mensaje_alerta,
    evaluar_lote
)
from backend.models.models import NivelAlerta


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBAS: calcular_dias_vencimiento()
# ══════════════════════════════════════════════════════════════════════════════

class TestCalcularDiasVencimiento:

    def test_UT_AL_001_lote_vence_en_3_dias(self):
        """UT-AL-001: Lote que vence exactamente en 3 días debe retornar 3."""
        # Arrange
        fecha_venc = date.today() + timedelta(days=3)
        # Act
        resultado = calcular_dias_vencimiento(fecha_venc)
        # Assert
        assert resultado == 3

    def test_UT_AL_002_lote_ya_vencido(self):
        """UT-AL-002: Lote vencido ayer debe retornar valor negativo (-1)."""
        # Arrange
        fecha_venc = date.today() - timedelta(days=1)
        # Act
        resultado = calcular_dias_vencimiento(fecha_venc)
        # Assert
        assert resultado == -1

    def test_UT_AL_003_fecha_none_lanza_excepcion(self):
        """UT-AL-003: fecha_vencimiento=None debe lanzar ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            calcular_dias_vencimiento(None)

    def test_vence_hoy_retorna_cero(self):
        """Lote que vence hoy debe retornar 0."""
        assert calcular_dias_vencimiento(date.today()) == 0

    def test_vence_en_30_dias(self):
        """Lote con amplio margen de seguridad."""
        fecha_venc = date.today() + timedelta(days=30)
        assert calcular_dias_vencimiento(fecha_venc) == 30


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBAS: clasificar_alerta()  — Valores Límite críticos
# ══════════════════════════════════════════════════════════════════════════════

class TestClasificarAlerta:

    def test_UT_AL_004_2_dias_alerta_roja(self):
        """UT-AL-004: 2 días → ALERTA_ROJA (partición 1–3)."""
        assert clasificar_alerta(2) == NivelAlerta.ALERTA_ROJA

    def test_UT_AL_005_5_dias_alerta_amarilla(self):
        """UT-AL-005: 5 días → ALERTA_AMARILLA (partición 4–7)."""
        assert clasificar_alerta(5) == NivelAlerta.ALERTA_AMARILLA

    def test_UT_AL_006_15_dias_sin_alerta(self):
        """UT-AL-006: 15 días → SIN_ALERTA (partición > 7)."""
        assert clasificar_alerta(15) == NivelAlerta.SIN_ALERTA

    def test_UT_AL_007_limite_inferior_roja_es_3(self):
        """UT-AL-007: Límite superior de ROJA = 3 días."""
        assert clasificar_alerta(3) == NivelAlerta.ALERTA_ROJA

    def test_UT_AL_008_limite_inferior_amarilla_es_4(self):
        """UT-AL-008: Límite inferior de AMARILLA = 4 días."""
        assert clasificar_alerta(4) == NivelAlerta.ALERTA_AMARILLA

    def test_limite_superior_amarilla_es_7(self):
        """Límite superior de AMARILLA = 7 días."""
        assert clasificar_alerta(7) == NivelAlerta.ALERTA_AMARILLA

    def test_limite_inferior_sin_alerta_es_8(self):
        """Límite inferior de SIN_ALERTA = 8 días."""
        assert clasificar_alerta(8) == NivelAlerta.SIN_ALERTA

    def test_dias_negativos_alerta_roja(self):
        """Lote ya vencido (días negativos) → ALERTA_ROJA."""
        assert clasificar_alerta(-5) == NivelAlerta.ALERTA_ROJA

    def test_dias_cero_alerta_roja(self):
        """Lote que vence hoy (0 días) → ALERTA_ROJA."""
        assert clasificar_alerta(0) == NivelAlerta.ALERTA_ROJA


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBAS: evaluar_lote() — función integrada
# ══════════════════════════════════════════════════════════════════════════════

class TestEvaluarLote:

    def test_lote_critico_retorna_rojo_con_mensaje(self):
        """Lote a 2 días debe retornar nivel ROJO y mensaje con texto de urgencia."""
        fecha = date.today() + timedelta(days=2)
        resultado = evaluar_lote(fecha, "Pollo Fresco")
        assert resultado["nivel_alerta"] == NivelAlerta.ALERTA_ROJA
        assert resultado["dias_para_vencer"] == 2
        assert "Pollo Fresco" in resultado["mensaje"]
        assert "ROJA" in resultado["mensaje"]

    def test_lote_seguro_retorna_sin_alerta(self):
        """Lote a 20 días no debe generar alerta."""
        fecha = date.today() + timedelta(days=20)
        resultado = evaluar_lote(fecha, "Leche UHT")
        assert resultado["nivel_alerta"] == NivelAlerta.SIN_ALERTA
        assert resultado["dias_para_vencer"] == 20

    def test_lote_vencido_retorna_rojo_con_texto_vencido(self):
        """Lote ya vencido debe indicar que está vencido en el mensaje."""
        fecha = date.today() - timedelta(days=3)
        resultado = evaluar_lote(fecha, "Yogur Natural")
        assert resultado["nivel_alerta"] == NivelAlerta.ALERTA_ROJA
        assert "VENCIDO" in resultado["mensaje"] or "venció" in resultado["mensaje"]
