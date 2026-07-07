"""Página de Login — Page Object."""
from tests_e2e.pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "/"

    # Selectores primarios (anclados en data-testid; si cambian, el motor sana)
    S_EMAIL = "[data-testid=login-email]"
    S_PASSWORD = "[data-testid=login-password]"
    S_BOTON = "[data-testid=btn-login]"
    S_ERROR = "#login-error"
    S_APP = "#app"

    def iniciar_sesion(self, email: str, password: str):
        self.smart.buscar("campo_email", self.S_EMAIL, "campo de correo del login").fill(email)
        self.smart.buscar("campo_password", self.S_PASSWORD, "campo de contraseña").fill(password)
        self.smart.buscar("boton_ingresar", self.S_BOTON, "botón Ingresar").click()
        return self

    def esta_autenticado(self) -> bool:
        """El login desaparece y aparece la app (sidebar + dashboard)."""
        self.page.wait_for_selector(f"{self.S_APP}:not(.hidden)", timeout=6000)
        return not self.page.is_hidden(self.S_APP)

    def texto_error(self) -> str:
        # El login tiene ~2s de animación (efecto agua) antes de mostrar el
        # resultado. Esperamos a que aparezca el mensaje de error.
        try:
            self.page.wait_for_function(
                "() => { const e = document.querySelector('#login-error');"
                " return e && e.textContent.trim().length > 0; }",
                timeout=7000,
            )
        except Exception:
            pass
        return (self.page.text_content(self.S_ERROR) or "").strip()
