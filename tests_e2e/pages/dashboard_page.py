"""Página del Centro de Mando (dashboard) — Page Object."""
from tests_e2e.pages.base_page import BasePage


class DashboardPage(BasePage):
    S_TITULO = "#topbar-title"
    S_TOTAL = "#d-total"
    S_ROJAS = "#d-rojas"
    S_HERO_TITULO = "#hero-title"
    S_NAV_LOTES = "[data-testid=nav-lotes]"
    S_NAV_ALERTAS = "[data-testid=nav-alertas]"
    S_SECCION_LOTES = "#sec-lotes"

    def cargado(self) -> bool:
        # Esperamos a que el KPI 'Total Lotes' deje de ser el placeholder '–'
        # y muestre un número real (la data llega tras la animación del login).
        self.page.wait_for_function(
            "() => { const el = document.querySelector('#d-total');"
            " return el && /\\d/.test(el.textContent); }",
            timeout=15000,
        )
        return "Centro de Mando" in (self.page.text_content(self.S_TITULO) or "")

    def total_lotes(self) -> str:
        return (self.page.text_content(self.S_TOTAL) or "").strip()

    def resumen_hero(self) -> str:
        # Esperamos a que el panel-resumen deje de decir 'Cargando…'
        self.page.wait_for_function(
            "() => { const el = document.querySelector('#hero-title');"
            " return el && el.textContent && !el.textContent.includes('Cargando'); }",
            timeout=15000,
        )
        return (self.page.text_content(self.S_HERO_TITULO) or "").strip()

    def ir_a_inventario(self):
        self.smart.buscar("nav_inventario", self.S_NAV_LOTES,
                           "menú Control de Inventario").click()
        self.page.wait_for_selector(f"{self.S_SECCION_LOTES}.active", timeout=4000)
        return self
