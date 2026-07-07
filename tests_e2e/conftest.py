"""
Fixtures de las pruebas E2E de MermaZero.

- Arranca el servidor uvicorn automáticamente si no está corriendo (para que
  solo tengas que ejecutar 'pytest', sin abrir dos terminales).
- Entrega 'smart' (el localizador con auto-corrección) a cada prueba.
- Al terminar, guarda el reporte de auto-correcciones (la evidencia).
"""
import os
import subprocess
import sys
import time
import urllib.request

import pytest

from tests_e2e.self_healing import AlmacenHuellas, ReporteSanacion
from tests_e2e.pages.base_page import LocalizadorInteligente

PROY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # carpeta makro_trazabilidad
BASE_URL = os.getenv("MZ_BASE_URL", "http://127.0.0.1:8000")
DIR_HUELLAS = os.path.join(os.path.dirname(__file__), "locators.json")
DIR_REPORTE = os.path.join(os.path.dirname(__file__), "healing_report")


def _servidor_responde(url: str) -> bool:
    try:
        urllib.request.urlopen(url, timeout=1.5)
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def servidor():
    """Levanta el servidor si no está activo; lo apaga al final si lo inició."""
    if _servidor_responde(BASE_URL):
        yield BASE_URL
        return

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
        cwd=PROY, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        if _servidor_responde(BASE_URL):
            break
        time.sleep(0.5)
    else:
        proc.terminate()
        pytest.fail("No se pudo iniciar el servidor uvicorn en el puerto 8000.")
    yield BASE_URL
    proc.terminate()


@pytest.fixture(scope="session")
def base_url(servidor):
    return servidor


@pytest.fixture(scope="session")
def reporte():
    rep = ReporteSanacion(DIR_REPORTE)
    yield rep
    ruta = rep.guardar()
    if ruta:
        print(f"\n>>> Reporte de auto-corrección guardado en: {ruta}")


@pytest.fixture
def smart(page, reporte):
    almacen = AlmacenHuellas(DIR_HUELLAS)
    return LocalizadorInteligente(page, almacen, reporte)
