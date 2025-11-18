from pathlib import Path
from typing import Optional, List, Sequence, Dict
from .browser.manager import BrowserManager
from .session import FacebookSession
from .login import login, close_notification_dialog
from .groups import go_to_groups_section, extract_groups, enter_group_by_url, enter_group_by_id
from .posting import publish, publish_to_groups
from .utils.log import get_logger

logger = get_logger("facebook_client")

class FacebookClient:
    """Cliente de alto nivel para automatizar login, gestión de grupos y publicaciones en Facebook.

    Usa sesión persistente por `user_data_dir` para cada usuario y permite configurar `proxy`, `headless` y `locale`.

    Ejemplo rápido:
        fb = FacebookClient(email="user@example.com", password="***", user_data_dir="user_data/alice", headless=False)
        fb.start()
        fb.login()
        fb.go_to_groups()
        grupos = fb.list_groups()
        fb.publish_to_groups([g["url"] for g in grupos[:3]], text="Hola desde mi SaaS!")
        fb.stop()
    """
    def __init__(
        self,
        email: str,
        password: str,
        user_data_dir: str | Path = "user_data",
        headless: bool = False,
        locale: str = "es-ES",
        user_agent: Optional[str] = None,
        proxy: Optional[dict] = None,
        timeout: int = 30_000,
    ):
        self.email = email
        self.password = password
        self.user_data_dir = str(user_data_dir)
        self.headless = headless
        self.locale = locale
        self.user_agent = user_agent
        self.proxy = proxy
        self.timeout = timeout

        self.session: Optional[FacebookSession] = None

    def start(self) -> None:
        """ Inicia el navegador, se debe de utilizar siempre al inicio antes de cualquier otra acción y despues de instanciar la clase. """
        
        logger.info("[Client] Iniciando navegador...")
        BrowserManager.start(headless=self.headless, proxy=self.proxy)
        self.session = FacebookSession(
            user_data_dir=self.user_data_dir,
            locale=self.locale,
            user_agent=self.user_agent,
            headless=self.headless,
            proxy=self.proxy,
        )
        self.session.open()
        self.session.page.set_default_timeout(self.timeout) # type: ignore

    def stop(self) -> None:
        """ Detiene el navegador """

        if self.session:
            self.session.close()
        BrowserManager.stop()
        logger.info("[Client] Navegador detenido.")

    def login(self) -> None:
        """ Inicia sesión en facebook con las credenciales pasadas a la instancia de la clase. En caso de que haya una sesión activa se maneja. """

        assert self.session and self.session.page
        login(self.session.page, self.email, self.password, timeout=self.timeout)
        close_notification_dialog(self.session.page)

    def go_to_groups(self) -> None:
        """ Accede a la sección de grupos de Facebook """

        assert self.session and self.session.page
        go_to_groups_section(self.session.page)

    def list_groups(self) -> List[Dict[str, str]]:
        """Extrae la lista de grupos del usuario.

        Returns:
            Lista de diccionarios con `nombre` y `url` de cada grupo descubierto.
        """

        assert self.session and self.session.page
        return extract_groups(self.session.page)

    def enter_group(self, url: str) -> None:
        """Entra a un grupo usando su `url`.

        Intenta el botón "Ver grupo" y, si no existe, navega directamente a la URL.

        Args:
            page: Página Playwright activa.
            url: URL del grupo.
        """

        assert self.session and self.session.page
        enter_group_by_url(self.session.page, url)

    def publish(self, text: str, photos: Optional[Sequence[str]] = None) -> bool:
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

        assert self.session and self.session.page
        return publish(self.session.page, text, photos)

    def publish_to_groups(self, group_urls: Sequence[str], text: str, photos: Optional[Sequence[str]] = None, delay_between: Optional[float] = None) -> dict:
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

        assert self.session and self.session.page
        return publish_to_groups(self.session.page, group_urls, text, photos, delay_between)
