from .login import close_notification_dialog
from playwright.sync_api import Page, TimeoutError as PWTimeoutError
from typing import List, Dict, Optional
from .exceptions import GroupNotFoundError
from .utils.log import get_logger
import time
import random

logger = get_logger("facebook_groups")

def _rand(min_s=1, max_s=3) -> float:
    """Delay aleatorio en segundos para simular interacción humana."""
    import random
    return float(random.randint(min_s, max_s))

def go_to_groups_section(page: Page) -> None:
    """Navega a la sección de Grupos del usuario."""
    logger.info("[Groups] Navegando a la sección Grupos...")
    page.locator('[aria-label="Grupos"]').first.click()
    close_notification_dialog(page)
    time.sleep(_rand())
    page.get_by_text("Tus grupos", exact=True).click(force=True)
    time.sleep(_rand())
    close_notification_dialog(page)

def extract_groups(page: Page) -> List[Dict[str, str]]:
    logger.info("[Groups] Extrayendo lista de grupos...")

    page.wait_for_load_state('domcontentloaded')

    groups_data = page.evaluate('''() => {
        const container = document.querySelector('div[role="list"]');
        if (!container) return [];
        const items = container.querySelectorAll('div[role="listitem"]');
        const groups = [];
        items.forEach(item => {
            const link = item.querySelector('a[href*="/groups/"]');
            if (link) {
            const svg = link.querySelector('svg[aria-label]');
            const nombre = svg ? svg.getAttribute('aria-label').trim() : null;
            if (nombre) {
                groups.push({
                nombre: nombre,
                url: link.href.split("?")[0]
                });
            }
            }
        });
        return groups;
        }''')

    return groups_data

def enter_group_by_url(page: Page, url: str) -> None:
    """Entra a un grupo usando su `url`.

    Intenta el botón "Ver grupo" y, si no existe, navega directamente a la URL.

    Args:
        page: Página Playwright activa.
        url: URL del grupo.
    """
    selector = f'a[aria-label="Ver grupo"][href="{url}"]'
    boton = page.locator(selector)
    if boton.count() > 0:
        boton.first.click()
        time.sleep(_rand())
        logger.info(f"[Groups] Entrando al grupo {url}")
    else:
        page.goto(url)
        try:
            page.wait_for_load_state("networkidle")
        except PWTimeoutError:
            pass
        logger.info(f"[Groups] Navegación directa al grupo {url}")

def enter_group_by_id(page: Page, group_id: str) -> None:
    """Entra a un grupo por su `group_id` numérico.

    Args:
        page: Página Playwright activa.
        group_id: Identificador del grupo en Facebook.
    """
    url = f"https://www.facebook.com/groups/{group_id}/"
    enter_group_by_url(page, url)
