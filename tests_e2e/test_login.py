"""Pruebas E2E — Autenticación (regresión funcional)."""
import pytest
from tests_e2e.pages.login_page import LoginPage


@pytest.mark.e2e
def test_login_con_credenciales_validas(page, smart, base_url):
    """Un usuario válido inicia sesión y entra al sistema."""
    login = LoginPage(page, smart, base_url).ir()
    login.iniciar_sesion("admin@makro.com", "admin123")
    assert login.esta_autenticado(), "No se ingresó al sistema con credenciales válidas"


@pytest.mark.e2e
def test_login_con_credenciales_invalidas(page, smart, base_url):
    """Credenciales incorrectas muestran un mensaje de error y NO ingresan."""
    login = LoginPage(page, smart, base_url).ir()
    login.iniciar_sesion("admin@makro.com", "clave-incorrecta")
    assert login.texto_error() != "", "Debió mostrarse un mensaje de error"
    assert page.is_hidden("#app"), "No debió ingresar al sistema"
