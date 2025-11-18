from playwright.sync_api import Page, TimeoutError as PWTimeoutError
from typing import Optional, Sequence, Dict
from .exceptions import PublishError
from .utils.log import get_logger
import time
import random

logger = get_logger("facebook_posting")

def _rand(min_s=1, max_s=3) -> float:
    """Delay aleatorio en segundos para simular interacción humana."""
    return float(random.randint(min_s, max_s))

def _rand_ms(min_ms=50, max_ms=100) -> int:
    """Delay aleatorio en milisegundos para tipeo en el editor."""
    return random.randint(min_ms, max_ms)

def _open_create_post(page: Page) -> None:
    """Abre el compositor de publicaciones en el contexto actual."""
    selector_post = 'div[role="button"] >> text=Escribe algo...'
    try:
        page.wait_for_selector(selector_post, timeout=8000)
        page.locator(selector_post).first.click()
        time.sleep(_rand())
    except PWTimeoutError:
        group_url = page.url
        group_id = group_url.rstrip('/').split('/')[-1]
        selector_buy_sell = f'a[href="/groups/{group_id}/buy_sell_discussion/"]'
        page.wait_for_selector(selector_buy_sell, timeout=8000)
        page.locator(selector_buy_sell).click()
        time.sleep(_rand())
        page.wait_for_selector(selector_post, timeout=8000)
        page.locator(selector_post).first.click()


def _find_file_input(page: Page):
    """Encuentra el input de archivos para adjuntar multimedia."""
    inp = page.locator('input[type="file"][multiple]')
    inp.wait_for(state="attached", timeout=5000)
    return inp

def publish(page: Page, text: str, photos: Optional[Sequence[str]] = None) -> bool:
    """Publica texto y multimedia en el contexto actual.

    Args:
        page: Página Playwright activa.
        text: Texto de la publicación.
        photos: Rutas de archivos a adjuntar.
    Returns:
        True si se confirma la publicación.
    Raises:
        PublishError: Si no se confirma el envío de la publicación.
    """
    logger.info("[Post] Iniciando publicación...")
    _open_create_post(page)

    if photos:
        try:
            foto_btn = page.get_by_role("button", name="Foto/video").first
            foto_btn.click()
        except Exception:
            page.locator('div[aria-label="Foto/video"][role="button"]').first.click()

        inp = _find_file_input(page)
        inp.set_input_files(list(photos))
        time.sleep(_rand(1, 2))

    editor = page.locator('div[role="textbox"][contenteditable="true"][aria-placeholder="Crea una publicación pública..."]')
    editor.wait_for(state="visible", timeout=8000)
    editor.click()
    editor.type(text, delay=_rand_ms())

    pub_btn = page.locator('div[aria-label="Publicar"][role="button"]').first
    pub_btn.click()
    time.sleep(_rand())
    try:
        page.wait_for_selector('div[aria-label="Publicar"][role="button"]', state="detached", timeout=10000)
        logger.info("[Post] Publicación enviada.")
        time.sleep(_rand())
        return True
    except PWTimeoutError:
        raise PublishError("No se confirmó la publicación")

def publish_to_groups(page: Page, group_urls: Sequence[str], text: str, photos: Optional[Sequence[str]] = None, delay_between: Optional[float] = None) -> Dict[str, dict]:
    """Publica en múltiples grupos y devuelve resultados por grupo.

    Args:
        page: Página Playwright activa.
        group_urls: URLs de grupos destino.
        text: Texto de la publicación.
        photos: Rutas de archivos a adjuntar.
        delay_between: Delay entre publicaciones en segundos.
    Returns:
        Diccionario `{url: {"ok": bool, "error"? : str}}`.
    """
    logger.info(f"[MultiPost] Publicando en {len(group_urls)} grupos...")
    results: Dict[str, dict] = {}
    for url in group_urls:
        try:
            from .groups import enter_group_by_url
            enter_group_by_url(page, url)
            page.wait_for_load_state('networkidle')
            _click_conversation_button(page)
            ok = publish(page, text, photos)
            page.go_back()
            time.sleep(delay_between or _rand())
            results[url] = {"ok": ok}
        except Exception as e:
            logger.info(f"[MultiPost] Error publicando en {url}: {e}")
            results[url] = {"ok": False, "error": str(e)}
    return results

def _click_conversation_button(page: Page) -> None:
    """Hace clic en el botón 'Conversación' para navegar a la sección de discusión, si no está ya en ella."""
    if "/buy_sell_discussion/" in page.url:
        logger.info("[Post] Ya en la sección 'Conversación'. No se requiere hacer clic.")
        return

    logger.info("[Post] Buscando y haciendo clic en el botón 'Conversación'...")
    try:
        # Intentar localizar el botón por su rol y texto
        conversation_button = page.get_by_role("menuitemradio", name="Conversación").first
        conversation_button.wait_for(state="visible", timeout=5000)
        conversation_button.click()
        logger.info("[Post] Botón 'Conversación' clicado exitosamente.")
        time.sleep(_rand())
    except PWTimeoutError:
        logger.warning("[Post] Botón 'Conversación' no encontrado o no visible en el tiempo esperado.")
        # Si falla, intentar con un selector más genérico que contenga el texto y el href
        try:
            conversation_button = page.locator('a[href*="/buy_sell_discussion/"] >> span:has-text("Conversación")').first
            conversation_button.wait_for(state="visible", timeout=5000)
            conversation_button.click()
            logger.info("[Post] Botón 'Conversación' clicado exitosamente con selector alternativo.")
            time.sleep(_rand())
        except PWTimeoutError:
            raise PublishError("No se pudo encontrar ni hacer clic en el botón 'Conversación'.")
