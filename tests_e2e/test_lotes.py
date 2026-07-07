"""
Pruebas E2E — Flujos funcionales de negocio (regresión completa).
Prueban que el sistema HACE su trabajo: registrar un lote y descargar reportes.
"""
import time
import pytest
from tests_e2e.pages.login_page import LoginPage
from tests_e2e.pages.lotes_page import LotesPage


@pytest.fixture
def sesion(page, smart, base_url):
    LoginPage(page, smart, base_url).ir().iniciar_sesion("admin@makro.com", "admin123")
    page.wait_for_selector("#app:not(.hidden)", timeout=8000)
    return LotesPage(page, smart, base_url)


@pytest.mark.e2e
def test_registrar_producto_y_aparece_en_inventario(sesion):
    """Flujo completo: registrar un lote nuevo y verificar que queda listado."""
    codigo = f"LOT-E2E-{int(time.time())}"  # código único por corrida
    sesion.ir_a_ingreso().registrar(
        codigo=codigo,
        producto="Yogurt Griego Bandeja 1kg",
        categoria="Lácteos",
        cantidad=25,
        proveedor="Lácteos del Sur S.A.C.",
        ubicacion="Pasillo B - Estante 4",
        dias_para_vencer=15,
    )
    mensaje = sesion.mensaje_resultado()
    assert "registrado" in mensaje.lower(), f"No confirmó el registro: {mensaje}"

    sesion.esperar_en_inventario()
    assert sesion.codigo_en_tabla(codigo), "El lote registrado no aparece en el inventario"


@pytest.mark.e2e
def test_descargar_reporte_excel(sesion):
    """El reporte de inventario se genera y descarga como archivo Excel."""
    descarga = sesion.ir_a_reportes().descargar_inventario()
    assert descarga.suggested_filename.endswith(".xlsx"), "No se descargó un Excel"
    assert "Inventario" in descarga.suggested_filename
