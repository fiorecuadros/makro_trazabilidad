"""
POM base + localizador inteligente (self-healing) sobre Playwright.
Cada página del sistema hereda de BasePage y usa 'self.smart' para ubicar
elementos de forma tolerante a cambios de diseño.
"""
from __future__ import annotations

import json
import os
import urllib.request

from tests_e2e.self_healing import (
    Huella, AlmacenHuellas, ReporteSanacion, mejor_candidato,
)

# JS que recorre la página y describe los elementos "ubicables" (los que un
# test suele necesitar: inputs, botones, enlaces, selects y cualquier
# elemento con data-testid). Para cada uno arma un selector único estable.
_JS_ESCANEO = r"""
() => {
  const sel = 'input, button, a, select, textarea, [data-testid], [role]';
  const nodos = Array.from(document.querySelectorAll(sel));
  const selectorUnico = (el) => {
    if (el.getAttribute('data-testid')) return `[data-testid="${el.getAttribute('data-testid')}"]`;
    if (el.id) return `#${el.id}`;
    const tag = el.tagName.toLowerCase();
    const iguales = Array.from(document.querySelectorAll(tag));
    const idx = iguales.indexOf(el) + 1;
    return `${tag}:nth-of-type(${idx})`;
  };
  return nodos.map(el => {
    const attrs = {};
    ['type','name','placeholder','role','aria-label','data-testid'].forEach(a => {
      if (el.getAttribute(a)) attrs[a] = el.getAttribute(a);
    });
    return {
      tag: el.tagName.toLowerCase(),
      id: el.id || '',
      clases: Array.from(el.classList),
      texto: (el.textContent || '').trim().slice(0, 60),
      atributos: attrs,
      selector: selectorUnico(el),
    };
  });
}
"""


class LocalizadorInteligente:
    """Ubica elementos y se auto-corrige si el selector primario se rompe."""

    def __init__(self, page, almacen: AlmacenHuellas, reporte: ReporteSanacion,
                 umbral: float = 0.6):
        self.page = page
        self.almacen = almacen
        self.reporte = reporte
        self.umbral = umbral

    # -- utilidades internas -------------------------------------------------
    def _escanear(self) -> list:
        return self.page.evaluate(_JS_ESCANEO)

    def _huella_de_selector(self, selector: str) -> Huella | None:
        for c in self._escanear():
            if c["selector"] == selector or c.get("id") and f"#{c['id']}" == selector:
                return Huella.desde_dict(c)
        el = self.page.query_selector(selector)
        if not el:
            return None
        datos = el.evaluate(
            """el => ({tag: el.tagName.toLowerCase(), id: el.id||'',
                       clases: Array.from(el.classList),
                       texto: (el.textContent||'').trim().slice(0,60),
                       atributos: (()=>{const o={};
                         ['type','name','placeholder','role','aria-label','data-testid']
                         .forEach(a=>{if(el.getAttribute(a))o[a]=el.getAttribute(a)});return o})()})"""
        )
        return Huella.desde_dict(datos)

    # -- API pública ---------------------------------------------------------
    def aprender(self, clave: str, selector: str):
        """Guarda la huella del elemento (para reconocerlo si luego se rompe)."""
        huella = self._huella_de_selector(selector)
        if huella:
            self.almacen.guardar(clave, huella)
        return huella

    def buscar(self, clave: str, selector_primario: str, descripcion: str = ""):
        """
        Devuelve el elemento. Si el selector primario funciona, lo usa (y
        refresca la huella). Si NO existe, activa la auto-corrección.
        """
        el = self.page.query_selector(selector_primario)
        if el:
            huella = self._huella_de_selector(selector_primario)
            if huella:
                self.almacen.guardar(clave, huella)
            return el

        # --- El selector se rompió: auto-corrección ---
        huella = self.almacen.obtener(clave)
        if huella is None:
            raise LookupError(
                f"'{clave}': selector '{selector_primario}' no existe y no hay "
                f"huella previa para auto-corregir.")

        candidatos = self._escanear()
        puntaje, cand = mejor_candidato(huella, candidatos, self.umbral)

        if cand:  # corrección por heurística
            self.reporte.registrar(clave, selector_primario, cand["selector"], puntaje, "heurística")
            return self.page.query_selector(cand["selector"])

        # heurística dudosa -> intento con IA (opcional, gratis con Groq)
        sel_ia = self._corregir_con_ia(descripcion or clave, candidatos)
        if sel_ia:
            self.reporte.registrar(clave, selector_primario, sel_ia, 0.0, "IA (Groq)")
            return self.page.query_selector(sel_ia)

        raise LookupError(
            f"'{clave}': no se pudo auto-corregir '{selector_primario}' "
            f"(mejor similitud {puntaje}).")

    # -- capa de IA opcional -------------------------------------------------
    def _corregir_con_ia(self, descripcion: str, candidatos: list) -> str | None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None  # sin key -> se omite; la heurística ya cubre el 95%
        try:
            lista = [{"selector": c["selector"], "tag": c["tag"],
                      "texto": c["texto"], "atributos": c["atributos"]} for c in candidatos]
            prompt = (
                "Eres un asistente de automatización de pruebas. Dada la descripción "
                f"de un elemento: '{descripcion}', y esta lista de elementos de la "
                f"página en JSON:\n{json.dumps(lista, ensure_ascii=False)}\n"
                "Responde SOLO con el 'selector' del elemento que mejor corresponde, "
                "sin explicaciones ni comillas extra.")
            cuerpo = json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0, "max_tokens": 60,
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions", data=cuerpo,
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode("utf-8"))
            sel = data["choices"][0]["message"]["content"].strip()
            return sel if self.page.query_selector(sel) else None
        except Exception:
            return None  # ante cualquier fallo de red/IA, no rompemos la prueba


class BasePage:
    URL = "/"

    def __init__(self, page, smart: LocalizadorInteligente, base_url: str):
        self.page = page
        self.smart = smart
        self.base_url = base_url

    def ir(self):
        self.page.goto(self.base_url + self.URL)
        return self
