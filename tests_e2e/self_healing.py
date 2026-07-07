"""
Motor de auto-corrección de selectores (self-healing) — MermaZero
=================================================================
Calidad 4.0: cuando un selector se rompe (porque cambió el diseño), este
motor reconoce el elemento correcto por su "huella" (tag, id, clases, texto
y atributos) y corrige la prueba automáticamente, sin intervención manual.

El archivo separa a propósito DOS cosas:
  1. La LÓGICA PURA de comparación (funciones abajo) -> se puede probar sin
     navegador, con simples diccionarios. Es lo que demuestra que funciona.
  2. La integración con Playwright vive en pages/base_page.py, que usa estas
     funciones sobre los elementos reales de la página.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from difflib import SequenceMatcher
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────
#  Huella de un elemento (lo que guardamos para reconocerlo después)
# ─────────────────────────────────────────────────────────────────────────
@dataclass
class Huella:
    tag: str = ""
    id: str = ""
    clases: list = field(default_factory=list)
    texto: str = ""
    atributos: dict = field(default_factory=dict)  # type, name, placeholder, role, aria-label, data-testid

    @staticmethod
    def desde_dict(d: dict) -> "Huella":
        return Huella(
            tag=d.get("tag", ""),
            id=d.get("id", ""),
            clases=d.get("clases", d.get("classes", [])),
            texto=d.get("texto", d.get("text", "")),
            atributos=d.get("atributos", d.get("attrs", {})),
        )


def _similitud(a: str, b: str) -> float:
    """Parecido entre dos textos, de 0 (nada) a 1 (idénticos)."""
    a, b = (a or "").strip().lower(), (b or "").strip().lower()
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


# Pesos: qué tan importante es cada rasgo para reconocer un elemento.
# El data-testid pesa mucho (es un ancla estable); el texto y las clases ayudan.
PESOS = {
    "data-testid": 4.0,
    "id": 3.0,
    "name": 2.5,
    "type": 2.0,
    "placeholder": 1.5,
    "role": 1.5,
    "aria-label": 1.5,
    "clases": 2.0,
    "texto": 2.0,
    "tag": 1.0,
}


def puntuar(huella: Huella, candidato: dict) -> float:
    """Devuelve qué tan parecido es 'candidato' a la 'huella' guardada (0 a 1)."""
    c_attrs = candidato.get("atributos", candidato.get("attrs", {})) or {}
    c_clases = candidato.get("clases", candidato.get("classes", [])) or []
    total, peso_usado = 0.0, 0.0

    # tag
    if huella.tag:
        total += PESOS["tag"] * (1.0 if huella.tag == candidato.get("tag") else 0.0)
        peso_usado += PESOS["tag"]

    # id
    if huella.id:
        exacto = 1.0 if huella.id == candidato.get("id") else _similitud(huella.id, candidato.get("id", ""))
        total += PESOS["id"] * exacto
        peso_usado += PESOS["id"]

    # atributos por nombre
    for attr in ("data-testid", "name", "type", "placeholder", "role", "aria-label"):
        if huella.atributos.get(attr):
            esperado = huella.atributos.get(attr)
            real = c_attrs.get(attr, "")
            val = 1.0 if esperado == real else _similitud(esperado, real)
            total += PESOS[attr] * val
            peso_usado += PESOS[attr]

    # clases (parecido por conjunto: cuántas comparten)
    if huella.clases:
        set_h, set_c = set(huella.clases), set(c_clases)
        union = set_h | set_c
        solapamiento = len(set_h & set_c) / len(union) if union else 0.0
        total += PESOS["clases"] * solapamiento
        peso_usado += PESOS["clases"]

    # texto visible
    if huella.texto:
        total += PESOS["texto"] * _similitud(huella.texto, candidato.get("texto", candidato.get("text", "")))
        peso_usado += PESOS["texto"]

    return round(total / peso_usado, 4) if peso_usado else 0.0


def mejor_candidato(huella: Huella, candidatos: list, umbral: float = 0.6):
    """
    Elige el candidato más parecido a la huella.
    Devuelve (puntaje, candidato) si supera el umbral, o (mejor_puntaje, None).
    """
    puntuados = sorted(
        ((puntuar(huella, c), c) for c in candidatos),
        key=lambda x: -x[0],
    )
    if puntuados and puntuados[0][0] >= umbral:
        return puntuados[0]
    return (puntuados[0][0] if puntuados else 0.0, None)


# ─────────────────────────────────────────────────────────────────────────
#  Almacén de huellas (persistente en disco)
# ─────────────────────────────────────────────────────────────────────────
class AlmacenHuellas:
    def __init__(self, ruta: str):
        self.ruta = ruta
        self._datos: dict = {}
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    self._datos = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._datos = {}

    def obtener(self, clave: str) -> Optional[Huella]:
        d = self._datos.get(clave)
        return Huella.desde_dict(d) if d else None

    def guardar(self, clave: str, huella: Huella):
        self._datos[clave] = asdict(huella)
        with open(self.ruta, "w", encoding="utf-8") as f:
            json.dump(self._datos, f, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────
#  Reporte de auto-correcciones (la evidencia para la rúbrica)
# ─────────────────────────────────────────────────────────────────────────
class ReporteSanacion:
    def __init__(self, carpeta: str):
        os.makedirs(carpeta, exist_ok=True)
        self.carpeta = carpeta
        self.eventos: list = []

    def registrar(self, clave, selector_roto, selector_nuevo, puntaje, via="heurística"):
        evento = {
            "hora": datetime.now().isoformat(timespec="seconds"),
            "elemento": clave,
            "selector_roto": selector_roto,
            "selector_corregido": selector_nuevo,
            "similitud": puntaje,
            "corregido_por": via,
        }
        self.eventos.append(evento)
        print(f"  [AUTO-CORRECCIÓN] '{clave}': {selector_roto}  ->  "
              f"{selector_nuevo}  (similitud {puntaje}, vía {via})")

    def guardar(self):
        if not self.eventos:
            return None
        ts = time.strftime("%Y%m%d_%H%M%S")
        ruta_json = os.path.join(self.carpeta, f"reporte_{ts}.json")
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(self.eventos, f, indent=2, ensure_ascii=False)
        # versión legible en texto
        ruta_txt = os.path.join(self.carpeta, f"reporte_{ts}.txt")
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write("REPORTE DE AUTO-CORRECCIÓN DE PRUEBAS — MermaZero\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total de selectores auto-corregidos: {len(self.eventos)}\n\n")
            for i, e in enumerate(self.eventos, 1):
                f.write(f"{i}. Elemento: {e['elemento']}\n")
                f.write(f"   Selector roto:      {e['selector_roto']}\n")
                f.write(f"   Selector corregido: {e['selector_corregido']}\n")
                f.write(f"   Similitud: {e['similitud']}  |  Vía: {e['corregido_por']}\n")
                f.write(f"   Hora: {e['hora']}\n\n")
        return ruta_json
