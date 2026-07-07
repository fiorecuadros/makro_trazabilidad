"""Pruebas E2E — Centro de Mando (regresión funcional)."""
import pytest
from tests_e2e.pages.login_page import LoginPage
from tests_e2e.pages.dashboard_page import DashboardPage


@pytest.fixture
def dashboard(page, smart, base_url):
    LoginPage(page, smart, base_url).ir().iniciar_sesion("admin@makro.com", "admin123")
    return DashboardPage(page, smart, base_url)


@pytest.mark.e2e
def test_dashboard_carga_kpis(dashboard):
    """El Centro de Mando carga y muestra el total de lotes (un número)."""
    assert dashboard.cargado()
    assert dashboard.total_lotes().isdigit(), "El KPI 'Total Lotes' no muestra un número"


@pytest.mark.e2e
def test_hero_muestra_estado(dashboard):
    """El panel-resumen deja de decir 'Cargando…' y muestra el estado real."""
    resumen = dashboard.resumen_hero()
    assert resumen and "Cargando" not in resumen


@pytest.mark.e2e
def test_navegacion_a_inventario(dashboard):
    """Al hacer clic en el menú, se muestra la sección de inventario."""
    dashboard.ir_a_inventario()
    assert dashboard.page.is_visible("#sec-lotes.active")
