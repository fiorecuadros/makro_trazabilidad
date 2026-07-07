"""
Pruebas UNITARIAS del motor de auto-corrección (sin navegador).
Demuestran que la lógica de reconocimiento funciona, con métricas exactas.
Se ejecutan con: pytest tests_e2e/test_healing_engine.py -v
"""
from tests_e2e.self_healing import Huella, puntuar, mejor_candidato


# Simulamos los elementos reales que existen en el login de MermaZero.
CANDIDATOS_LOGIN = [
    {"tag": "input", "id": "login-email", "clases": [],
     "texto": "", "atributos": {"type": "email", "data-testid": "login-email",
                                  "placeholder": "operador@makro.com"},
     "selector": "[data-testid=login-email]"},
    {"tag": "input", "id": "login-password", "clases": [],
     "texto": "", "atributos": {"type": "password", "data-testid": "login-password",
                                  "placeholder": "••••••••"},
     "selector": "[data-testid=login-password]"},
    {"tag": "button", "id": "btn-login", "clases": ["btn-login"],
     "texto": "Ingresar", "atributos": {"data-testid": "btn-login"},
     "selector": "[data-testid=btn-login]"},
    {"tag": "a", "id": "", "clases": ["nav-item"], "texto": "Centro de Mando",
     "atributos": {"data-testid": "nav-dashboard"}, "selector": "[data-testid=nav-dashboard]"},
]


def test_reconoce_input_email_por_huella():
    """El selector primario '#correo-viejo' ya no existe; la huella describe el
    input de email. El motor debe reconocerlo entre todos los candidatos."""
    huella = Huella(tag="input", id="correo-viejo",
                    atributos={"type": "email", "placeholder": "operador@makro.com",
                               "data-testid": "login-email"})
    puntaje, cand = mejor_candidato(huella, CANDIDATOS_LOGIN, umbral=0.6)
    assert cand is not None, "El motor no encontró reemplazo"
    assert cand["selector"] == "[data-testid=login-email]"
    assert puntaje >= 0.8


def test_no_confunde_email_con_password():
    """Aunque email y password son ambos <input>, el motor debe elegir email."""
    huella = Huella(tag="input", atributos={"type": "email", "data-testid": "login-email"})
    _, cand = mejor_candidato(huella, CANDIDATOS_LOGIN)
    assert cand["selector"] == "[data-testid=login-email]"


def test_reconoce_boton_por_texto_aunque_cambie_id():
    """El botón cambió de id, pero su texto 'Ingresar' y su tag lo delatan."""
    huella = Huella(tag="button", id="boton-viejo", texto="Ingresar",
                    clases=["btn-login"])
    puntaje, cand = mejor_candidato(huella, CANDIDATOS_LOGIN)
    assert cand["selector"] == "[data-testid=btn-login]"
    assert puntaje >= 0.7


def test_devuelve_none_si_no_hay_parecido():
    """Si nada se parece, no inventa: devuelve None (mejor fallar que adivinar mal)."""
    huella = Huella(tag="video", id="reproductor", texto="algo inexistente")
    _, cand = mejor_candidato(huella, CANDIDATOS_LOGIN, umbral=0.6)
    assert cand is None


def test_puntaje_exacto_es_alto():
    """Una huella idéntica a un candidato debe dar puntaje cercano a 1.0."""
    huella = Huella(tag="button", id="btn-login", texto="Ingresar",
                    clases=["btn-login"], atributos={"data-testid": "btn-login"})
    candidato = CANDIDATOS_LOGIN[2]
    assert puntuar(huella, candidato) >= 0.95
