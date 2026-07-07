"""Página de Control de Inventario / Ingreso de Producto — Page Object."""
from datetime import date, timedelta
from tests_e2e.pages.base_page import BasePage


class LotesPage(BasePage):
    S_NAV_NUEVO = "[data-testid=nav-nuevo-lote]"
    S_NAV_LOTES = "[data-testid=nav-lotes]"
    S_NAV_REPORTES = "[data-testid=nav-reportes]"
    S_BTN_REGISTRAR = "[data-testid=btn-registrar]"
    S_RESULTADO_OK = ".form-result.ok"
    S_TABLA_LOTES = "#tabla-lotes"

    def ir_a_ingreso(self):
        self.smart.buscar("nav_nuevo_lote", self.S_NAV_NUEVO, "menú Ingreso de Producto").click()
        self.page.wait_for_selector("#sec-nuevo-lote.active", timeout=4000)
        return self

    def registrar(self, codigo, producto, categoria, cantidad, proveedor,
                  ubicacion, dias_para_vencer=15):
        venc = (date.today() + timedelta(days=dias_para_vencer)).isoformat()
        self.page.fill("#f-codigo", codigo)
        self.page.fill("#f-producto", producto)
        self.page.select_option("#f-categoria", label=categoria)
        self.page.fill("#f-cantidad", str(cantidad))
        self.page.fill("#f-proveedor", proveedor)
        self.page.fill("#f-ingreso", date.today().isoformat())
        self.page.fill("#f-vencimiento", venc)
        self.page.fill("#f-ubicacion", ubicacion)
        self.smart.buscar("boton_registrar", self.S_BTN_REGISTRAR, "botón Registrar Lote").click()
        return self

    def mensaje_resultado(self) -> str:
        self.page.wait_for_selector(self.S_RESULTADO_OK, timeout=8000)
        return (self.page.text_content(self.S_RESULTADO_OK) or "").strip()

    def esperar_en_inventario(self):
        # tras registrar, el sistema navega solo al inventario (~1.8s)
        self.page.wait_for_selector("#sec-lotes.active", timeout=6000)
        return self

    def codigo_en_tabla(self, codigo: str) -> bool:
        self.page.wait_for_selector(f"{self.S_TABLA_LOTES}", timeout=6000)
        return codigo in (self.page.text_content(self.S_TABLA_LOTES) or "")

    def ir_a_reportes(self):
        self.smart.buscar("nav_reportes", self.S_NAV_REPORTES, "menú Análisis y Reportes").click()
        self.page.wait_for_selector("#sec-reportes.active", timeout=4000)
        return self

    def descargar_inventario(self):
        """Hace clic en la tarjeta de exportar inventario y captura la descarga."""
        with self.page.expect_download(timeout=15000) as info:
            self.page.locator(".reporte-card").first.click()
        return info.value
