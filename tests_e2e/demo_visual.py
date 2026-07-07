"""
MODO DEMOSTRACIÓN VISUAL — MermaZero (para grabar evidencia del LRPD III)
=========================================================================
Abre el navegador y recorre el sistema DESPACIO y de forma HUMANA:
escribe letra por letra, hace pausas, muestra carteles de cada paso y
demuestra la auto-corrección de selectores en vivo.

Cómo usarlo (desde la carpeta makro_trazabilidad):
    py tests_e2e/demo_visual.py

No necesitas arrancar el servidor: el script lo levanta y lo apaga solo.
Para grabar: inicia tu grabador de pantalla y luego ejecuta el comando.
"""
import os
import sys

# Permite ejecutar el script directamente (py tests_e2e/demo_visual.py)
# agregando la carpeta del proyecto a la ruta de búsqueda de Python.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess
import time
import urllib.request
from datetime import date, timedelta

from playwright.sync_api import sync_playwright

from tests_e2e.self_healing import AlmacenHuellas, ReporteSanacion
from tests_e2e.pages.base_page import LocalizadorInteligente

# ── Ritmo de la demo (súbelo si quieres MÁS lento) ───────────────────────
DELAY_TIPEO = 110      # ms entre cada letra al escribir
SLOW_MO     = 600      # ms entre cada acción del navegador
PAUSA_CORTA = 1.2      # segundos
PAUSA_LARGA = 2.5      # segundos

PROY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "http://127.0.0.1:8000"


def _responde(url):
    try:
        urllib.request.urlopen(url, timeout=1.5)
        return True
    except Exception:
        return False


def _arrancar_servidor():
    if _responde(BASE_URL):
        return None
    print("→ Levantando el servidor…")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
        cwd=PROY, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        if _responde(BASE_URL):
            print("→ Servidor listo.\n")
            return proc
        time.sleep(0.5)
    proc.terminate()
    raise RuntimeError("No se pudo iniciar el servidor.")


def narrar(page, titulo, detalle=""):
    """Muestra un cartel arriba explicando el paso actual (para el video)."""
    page.evaluate(
        """([t, d]) => {
          let b = document.getElementById('__demo_banner');
          if (!b) {
            b = document.createElement('div');
            b.id = '__demo_banner';
            b.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;'
              + 'background:#0A1628;color:#fff;padding:14px 22px;font-family:Inter,'
              + 'system-ui,sans-serif;font-size:16px;font-weight:600;'
              + 'border-bottom:3px solid #F5A800;box-shadow:0 4px 20px rgba(0,0,0,.4)';
            document.body.appendChild(b);
          }
          b.innerHTML = '<span style="color:#F5A800">▶ </span>' + t
            + (d ? ' <span style="opacity:.65;font-weight:400">— ' + d + '</span>' : '');
        }""",
        [titulo, detalle],
    )
    print(f"  ▶ {titulo}" + (f" — {detalle}" if detalle else ""))


def tipear(page, selector, texto):
    """Escribe letra por letra, como una persona."""
    page.locator(selector).click()
    page.locator(selector).fill("")
    page.locator(selector).press_sequentially(texto, delay=DELAY_TIPEO)


def demo():
    proc = _arrancar_servidor()
    almacen = AlmacenHuellas(os.path.join(os.path.dirname(__file__), "locators.json"))
    reporte = ReporteSanacion(os.path.join(os.path.dirname(__file__), "healing_report"))

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False, slow_mo=SLOW_MO)
        page = navegador.new_page(viewport={"width": 1366, "height": 768})
        smart = LocalizadorInteligente(page, almacen, reporte)

        # ── 1. LOGIN ──────────────────────────────────────────────────────
        page.goto(BASE_URL)
        time.sleep(PAUSA_CORTA)
        narrar(page, "Paso 1: Inicio de sesión", "escribiendo credenciales del operador")
        time.sleep(PAUSA_CORTA)
        tipear(page, "[data-testid=login-email]", "admin@makro.com")
        tipear(page, "[data-testid=login-password]", "admin123")
        time.sleep(PAUSA_CORTA)
        narrar(page, "Paso 1: Inicio de sesión", "presionando “Ingresar”")
        page.locator("[data-testid=btn-login]").click()
        page.wait_for_selector("#app:not(.hidden)", timeout=8000)
        time.sleep(PAUSA_LARGA)

        # ── 2. CENTRO DE MANDO ────────────────────────────────────────────
        page.wait_for_function(
            "() => /\\d/.test(document.querySelector('#d-total').textContent)", timeout=15000)
        narrar(page, "Paso 2: Centro de Mando", "los indicadores cargan con datos reales")
        time.sleep(PAUSA_LARGA)
        # Bajamos a mostrar los gráficos (distribución y por categoría)
        page.mouse.wheel(0, 520)
        narrar(page, "Paso 2: Centro de Mando", "gráficos de distribución por alerta y por categoría")
        time.sleep(PAUSA_LARGA)
        page.mouse.wheel(0, -520)
        time.sleep(PAUSA_CORTA)

        # ── 3. CONTROL DE INVENTARIO ──────────────────────────────────────
        narrar(page, "Paso 3: Control de Inventario", "listado de lotes con su estado y alertas")
        page.locator("[data-testid=nav-lotes]").click()
        time.sleep(PAUSA_CORTA)
        page.mouse.wheel(0, 350)
        time.sleep(PAUSA_LARGA)
        page.mouse.wheel(0, -350)
        time.sleep(PAUSA_CORTA)

        # ── 4. REGISTRAR UN PRODUCTO NUEVO (escribiendo el formulario) ────
        narrar(page, "Paso 4: Ingreso de Producto",
               "registramos un lote nuevo escribiendo el formulario")
        page.locator("[data-testid=nav-nuevo-lote]").click()
        page.wait_for_selector("#sec-nuevo-lote.active", timeout=4000)
        time.sleep(PAUSA_CORTA)

        codigo = f"LOT-DEMO-{int(time.time())}"
        venc = (date.today() + timedelta(days=15)).isoformat()
        for sel, val in [("#f-codigo", codigo),
                         ("#f-producto", "Yogurt Griego Bandeja 1kg"),
                         ("#f-proveedor", "Lácteos del Sur S.A.C."),
                         ("#f-ubicacion", "Pasillo B - Estante 4")]:
            page.locator(sel).click()
            page.locator(sel).press_sequentially(val, delay=DELAY_TIPEO)
        page.select_option("#f-categoria", label="Lácteos")
        page.locator("#f-cantidad").press_sequentially("25", delay=DELAY_TIPEO)
        page.fill("#f-ingreso", date.today().isoformat())
        page.fill("#f-vencimiento", venc)
        time.sleep(PAUSA_CORTA)
        narrar(page, "Paso 4: Ingreso de Producto", "presionando “Registrar Lote”")
        page.locator("[data-testid=btn-registrar]").click()
        page.wait_for_selector(".form-result.ok", timeout=8000)
        time.sleep(PAUSA_LARGA)

        page.wait_for_selector("#sec-lotes.active", timeout=6000)
        narrar(page, "Paso 4: Registro exitoso",
               f"el lote {codigo} ya aparece en el inventario ✓")
        time.sleep(PAUSA_LARGA)

        # ── 5. DESCARGAR REPORTE EN EXCEL ─────────────────────────────────
        narrar(page, "Paso 5: Análisis y Reportes", "descargando el inventario en Excel")
        page.locator("[data-testid=nav-reportes]").click()
        page.wait_for_selector("#sec-reportes.active", timeout=4000)
        time.sleep(PAUSA_CORTA)
        with page.expect_download(timeout=15000) as info:
            page.locator(".reporte-card").first.click()
        descarga = info.value

        # Guardamos el Excel en una carpeta visible y lo ABRIMOS para que se vea
        carpeta_desc = os.path.join(PROY, "reportes_descargados")
        os.makedirs(carpeta_desc, exist_ok=True)
        ruta_excel = os.path.join(carpeta_desc, descarga.suggested_filename)
        descarga.save_as(ruta_excel)
        narrar(page, "Paso 5: Reporte generado",
               f"{descarga.suggested_filename} — abriendo el Excel…")
        time.sleep(PAUSA_CORTA)
        try:
            os.startfile(ruta_excel)   # abre el Excel en pantalla (Windows)
            time.sleep(6)              # tiempo para que se vea la hoja abierta
            page.bring_to_front()      # volvemos al navegador para continuar
        except Exception:
            time.sleep(PAUSA_LARGA)
        print(f"  Excel guardado en: {ruta_excel}")

        # ── 6. CENTRO DE ALERTAS ──────────────────────────────────────────
        narrar(page, "Paso 6: Centro de Alertas", "lotes próximos a vencer clasificados por urgencia")
        page.locator("[data-testid=nav-alertas]").click()
        time.sleep(PAUSA_CORTA)
        page.mouse.wheel(0, 320)
        time.sleep(PAUSA_LARGA)
        page.mouse.wheel(0, -320)
        time.sleep(PAUSA_CORTA)

        # ── 7. AUTO-CORRECCIÓN EN VIVO (lo que pidió el docente) ──────────
        narrar(page, "Paso 7: Auto-corrección de pruebas",
               "volvemos al login y ROMPEMOS un selector a propósito")
        page.goto(BASE_URL)
        time.sleep(PAUSA_CORTA)

        smart.aprender("campo_email", "[data-testid=login-email]")
        selector_roto = "#correo-antiguo-que-ya-no-existe"
        print("\n  ── DEMOSTRACIÓN DE AUTO-CORRECCIÓN ──")
        print(f"  El test intenta usar el selector viejo: {selector_roto}")
        elemento = smart.buscar("campo_email", selector_roto, "campo de correo del login")
        elemento.fill("")
        elemento.press_sequentially("admin@makro.com", delay=DELAY_TIPEO)
        narrar(page, "Paso 7: Auto-corrección de pruebas",
               "el motor reconoció el campo solo y siguió sin fallar ✓")
        time.sleep(PAUSA_LARGA)

        # ── CIERRE ────────────────────────────────────────────────────────
        narrar(page, "Demostración completa", "sistema y auto-corrección funcionando")
        ruta = reporte.guardar()
        if ruta:
            print(f"\n  Reporte de auto-corrección guardado en:\n  {ruta}")
        print("\n  (La ventana se cerrará en 6 segundos…)")
        time.sleep(6)
        navegador.close()

    if proc:
        proc.terminate()
    print("\n✓ Demostración finalizada.")


if __name__ == "__main__":
    demo()
