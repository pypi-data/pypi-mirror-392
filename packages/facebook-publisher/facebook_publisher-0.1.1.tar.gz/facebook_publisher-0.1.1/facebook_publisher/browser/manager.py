from playwright.sync_api import sync_playwright, Browser, BrowserContext
from typing import Optional, Dict
import threading
from ..utils.log import get_logger

logger = get_logger("browser_manager")

class BrowserManager:
    _playwright = None
    _browser: Optional[Browser] = None
    _lock = threading.Lock()

    @classmethod
    def start(cls, headless: bool = False, proxy: Optional[Dict] = None) -> None:
        with cls._lock:
            if cls._playwright is None:
                cls._playwright = sync_playwright().start()
                launch_args = {"headless": headless}
                if proxy:
                    launch_args["proxy"] = proxy
                cls._browser = cls._playwright.chromium.launch(**launch_args)

    @classmethod
    def get_browser(cls) -> Browser:
        if cls._browser is None:
            raise RuntimeError("BrowserManager not started. Call start() first.")
        return cls._browser

    @classmethod
    def create_persistent_context(cls, user_data_dir: str, locale: str = "es-ES", user_agent: Optional[str] = None, proxy: Optional[Dict] = None, headless: bool = False) -> BrowserContext:
        if cls._playwright is None:
            cls._playwright = sync_playwright().start()
        logger.info(f"[BrowserManager] Attempting to launch persistent context with user_data_dir: {user_data_dir}, headless: {headless}")
        try:
            context = cls._playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False, # Changed to False for debugging
                locale=locale,
                user_agent=user_agent,
                proxy=proxy,
                viewport={"width": 1280, "height": 800},
                accept_downloads=True,
            )
            logger.info("[BrowserManager] Persistent context launched successfully.")
            return context
        except Exception as e:
            logger.error(f"[BrowserManager] Error launching persistent context: {e}")
            raise

    @classmethod
    def stop(cls) -> None:
        with cls._lock:
            if cls._browser:
                cls._browser.close()
                cls._browser = None
            if cls._playwright:
                cls._playwright.stop()
                cls._playwright = None
