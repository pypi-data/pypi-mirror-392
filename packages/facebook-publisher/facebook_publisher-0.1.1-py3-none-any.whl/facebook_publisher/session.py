from pathlib import Path
from typing import Optional
from playwright.sync_api import BrowserContext, Page
from .browser.manager import BrowserManager
from .utils.log import get_logger

logger = get_logger("facebook_session")

class FacebookSession:
    def __init__(
        self,
        user_data_dir: str | Path,
        locale: str = "es-ES",
        user_agent: Optional[str] = None,
        headless: bool = False,
        proxy: Optional[dict] = None,
    ):
        self.user_data_dir = str(user_data_dir)
        self.locale = locale
        self.user_agent = user_agent
        self.headless = headless
        self.proxy = proxy
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    def open(self) -> None:
        logger.info(f"[Session] Abriendo sesión con data dir: {self.user_data_dir}")
        self.context = BrowserManager.create_persistent_context(
            user_data_dir=self.user_data_dir,
            locale=self.locale,
            user_agent=self.user_agent,
            proxy=self.proxy,
            headless=self.headless,
        )
        self.page = self.context.new_page()

    def close(self) -> None:
        if self.context:
            self.context.close()
            logger.info("[Session] Sesión cerrada")
