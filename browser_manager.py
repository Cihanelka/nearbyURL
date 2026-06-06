"""
Created by  : Mapin Data
Created At  : 2026-05-20
Subject     : Browser context, cookie ve user-agent yönetimi.
              - Her ilçe için yeni context (session) oluşturur
              - Cookie consent ekranını kabul eder
              - User-agent rotasyonu yapar
"""

import random

from playwright.async_api import Page, BrowserContext

from config import (
    GOOGLE_URL,
    GOOGLE_MAPS_URL,
    PAGE_LOAD_TIMEOUT,
    USER_AGENTS,
)
from log_config import getLogger

logger = getLogger(__name__)


def getNextUserAgent() -> str:
    """Her çağrıda farklı user-agent döndürür (rastgele seçim)."""
    return random.choice(USER_AGENTS)


async def acceptCookiesIfPresent(page: Page) -> None:
    """Google cookie onayı (consent) ekranını kabul eder."""
    try:
        btn = page.locator(
            'button:has-text("Tümünü kabul et"), '
            'button:has-text("Accept all"), '
            'button:has-text("Kabul et")'
        )
        if await btn.count() > 0:
            await btn.first.click()
            await page.wait_for_timeout(2000)
            logger.info("Cookie onayı kabul edildi.")
    except Exception:
        pass


async def initGoogleCookies(page: Page) -> None:
    """
    Önce google.com'a gidip cookie consent'i kabul eder.
    Neden: Maps'e gitmeden önce Google cookie'lerini almak gerekiyor,
           aksi halde Maps sayfası düzgün yüklenmiyor.
    """
    try:
        await page.goto(GOOGLE_URL, timeout=PAGE_LOAD_TIMEOUT)
        await acceptCookiesIfPresent(page)
        await page.wait_for_timeout(1500)
        logger.info("Google cookie'leri alındı (google.com).")
    except Exception as exc:
        logger.warning("Google cookie alma başarısız: %s", exc)


async def refreshCookies(page: Page) -> None:
    """
    Düzenli cookie tazeleme: Önce google.com → cookie kabul, sonra Maps'e git.
    Neden: Uzun süren oturumlarda cookie'lerin geçerliliğini korur.
    """
    try:
        await initGoogleCookies(page)
        await page.goto(GOOGLE_MAPS_URL, timeout=PAGE_LOAD_TIMEOUT)
        await page.wait_for_timeout(2000)
        logger.info("Cookie tazelendi, Maps'e geçildi.")
    except Exception as exc:
        logger.warning("Cookie tazeleme başarısız: %s", exc)


async def createFreshContext(browser, userAgent: str = None) -> BrowserContext:
    """
    Yeni, temiz bir browser context oluşturur (yeni session, boş cookie).
    Neden: Her ilçe değişiminde session sıfırlanarak bot tespitinden kaçınılır.
    """
    selectedAgent = userAgent or getNextUserAgent()
    context = await browser.new_context(
        user_agent=selectedAgent,
        viewport={"width": 1920, "height": 1080},
        locale="tr-TR",
    )
    logger.info("Yeni context oluşturuldu (UA: ...%s)", selectedAgent[-30:])
    return context
