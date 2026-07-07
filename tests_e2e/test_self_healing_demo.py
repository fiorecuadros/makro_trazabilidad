"""
Prueba E2E — DEMOSTRACIÓN DE AUTO-CORRECCIÓN (Calidad 4.0)
==========================================================
Escenario: una corrida anterior 'aprendió' cómo es el campo de correo del
login. Luego el diseño cambió y el test viejo usa un selector que YA NO EXISTE
(#correo-antiguo). En lugar de fallar, el motor reconoce el campo por su huella
y corrige la prueba solo, dejando registro en healing_report/.
"""
import pytest


@pytest.mark.e2e
@pytest.mark.healing
def test_autocorreccion_de_selector_roto(page, smart, base_url):
    page.goto(base_url)

    # 1) La corrida "aprende" el campo real (esto ocurriría normalmente la
    #    primera vez que el test corre bien).
    smart.aprender("campo_email_demo", "[data-testid=login-email]")

    # 2) Simulamos que el diseño cambió: el test intenta un selector inexistente.
    selector_roto = "#correo-antiguo-que-ya-no-existe"
    elemento = smart.buscar("campo_email_demo", selector_roto,
                            descripcion="campo de correo del login")

    # 3) El motor debió auto-corregir y devolver el campo correcto (usable).
    assert elemento is not None, "El motor no logró auto-corregir el selector roto"
    elemento.fill("admin@makro.com")
    assert elemento.input_value() == "admin@makro.com"

    # 4) Debe haber quedado registrada al menos una auto-corrección (evidencia).
    eventos = [e for e in smart.reporte.eventos if e["elemento"] == "campo_email_demo"]
    assert len(eventos) >= 1
    assert eventos[-1]["selector_roto"] == selector_roto
    assert "login-email" in eventos[-1]["selector_corregido"]


@pytest.mark.e2e
@pytest.mark.healing
def test_login_completo_con_selectores_rotos(page, smart, base_url):
    """Prueba de fuego: iniciar sesión aunque los 3 selectores estén rotos."""
    page.goto(base_url)
    # Aprendemos los 3 elementos reales
    smart.aprender("email", "[data-testid=login-email]")
    smart.aprender("password", "[data-testid=login-password]")
    smart.aprender("boton", "[data-testid=btn-login]")

    # Usamos selectores rotos a propósito -> el motor sana los 3
    smart.buscar("email", "#email-viejo", "campo correo").fill("admin@makro.com")
    smart.buscar("password", "#pass-viejo", "campo contraseña").fill("admin123")
    smart.buscar("boton", "#btn-viejo", "botón ingresar").click()

    page.wait_for_selector("#app:not(.hidden)", timeout=6000)
    assert page.is_hidden("#app") is False
    assert len(smart.reporte.eventos) >= 3
