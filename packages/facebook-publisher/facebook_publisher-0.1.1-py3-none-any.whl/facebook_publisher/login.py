from playwright.sync_api import Page, TimeoutError as PWTimeoutError
from .utils.retry import retry
from .exceptions import LoginError
from .utils.log import get_logger
import time

logger = get_logger("facebook_login")

def login(page: Page, email: str, password: str, timeout: int = 30000) -> None:
    logger.info("[Login] Navegando a Facebook...")
    page.goto("https://www.facebook.com/")
    try:
        page.wait_for_selector("div[aria-label='Crear una publicación']", timeout=30000)
    except PWTimeoutError:
        logger.info("[Login] Timeout en networkidle, continuando...")

    try:
        # Check if already logged in
        if not page.locator("#email").is_visible():
            logger.info("[Login] Sesión existente detectada. Saltando login.")
            return

        retry(lambda: page.wait_for_selector("#email", timeout=5000), retries=3, delay=1, stage="Login", logger=logger)
        page.locator("#email").fill(email)
        page.locator("#pass").fill(password)
        page.locator('[name="login"]').click()
        page.wait_for_selector("div[aria-label='Crear una publicación']", timeout=30000)
        if page.get_by_text("Introduce el código").count() > 0 or page.get_by_text("Verifica tu identidad").count() > 0:
            raise LoginError("Se requiere verificación adicional (2FA/checkpoint)")
        logger.info("[Login] Login exitoso")
    except Exception as e:
        raise LoginError(f"Error en login: {e}")

def close_notification_dialog(page: Page) -> None:
    """
    Cierra específicamente el popup 'Solicitud de notificaciones push'.
    Muy robusto, evita errores de navegación y context destroyed.
    """
    try:
        # Ubicar el alertdialog exacto
        dlg = page.wait_for_selector('div[role="alertdialog"][aria-label="Solicitud de notificaciones push"]', timeout=30000)
        dlg = page.locator('div[role="alertdialog"][aria-label="Solicitud de notificaciones push"]')
        
        if dlg.count() == 0:
            return  # No existe popup

        # Botón Cerrar dentro del diálogo
        btn = dlg.locator("button", has_text="Cerrar")

        if btn.count() > 0:
            btn.first.click()
            logger.info("[Login] Popup de notificaciones cerrado.")
            return

        logger.info("[Login] No se encontró botón Cerrar dentro del popup de notificaciones.")

    except PWTimeoutError:
        logger.info(msg="[Login] Error cerrando popup de notificaciones")
