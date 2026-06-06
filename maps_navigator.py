"""
Created by  : Mapin Data
Created At  : 2026-05-20
Subject     : Google Maps sayfa navigasyonu.
              - Mahalle arama → kart/liste algılama → Yakınında butonuna tıklama
              - Kart detayı açıksa direkt Yakınında'ya basar
              - Liste gelirse ilk karta tıklar, sonra Yakınında'ya basar
"""

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from config import GOOGLE_MAPS_SEARCH_URL, PAGE_LOAD_TIMEOUT
from browser_manager import acceptCookiesIfPresent
from log_config import getLogger

logger = getLogger(__name__)


async def isCardDetailOpen(page: Page) -> bool:
    """
    Arama sonrasında direkt kart detayı mı açıldı yoksa liste mi geldi kontrol eder.
    Neden: Tek sonuç varsa Maps direkt kart detayını açar, "Yakınında" butonu oradadır.
    """
    nearbyPatterns = [
        'button[aria-label*="Yakınında" i]',
        'button[data-value="Yakınında"]',
        'button:has-text("Yakınında")',
        'button[aria-label*="Nearby" i]',
        'button:has-text("Nearby")',
    ]
    for pattern in nearbyPatterns:
        try:
            btn = page.locator(pattern).first
            if await btn.is_visible(timeout=2000):
                return True
        except Exception:
            continue
    return False


async def clickFirstCardInList(page: Page) -> bool:
    """
    Liste görünümünde ilk kartı tıklar.
    Neden: Liste geldiğinde kart detayına girmek için ilk sonuca tıklanmalıdır.
    """
    cardSelectors = [
        '[role="feed"] > div > div a[href*="maps/place"]',
        '[role="feed"] > div > div div.fontHeadlineSmall',
        '[role="feed"] > div > div div.qBF1Pd',
        '[role="feed"] > div > div h3',
    ]
    for selector in cardSelectors:
        try:
            firstCard = page.locator(selector).first
            if await firstCard.is_visible(timeout=3000):
                await firstCard.click()
                await page.wait_for_timeout(3000)
                logger.info("Liste görünümünde ilk kart tıklandı: %s", selector)
                return True
        except Exception:
            continue
    logger.warning("Liste görünümünde tıklanacak kart bulunamadı.")
    return False


async def clickNearbyButton(page: Page) -> bool:
    """
    'Yakınında' butonunu bulur ve tıklar.
    Dönen değer: True (başarılı) veya False (başarısız).
    """
    nearbyPatterns = [
        'button[data-value="Yakınında"]',
        'button[aria-label*="Yakınında" i]',
        'button[aria-label*="Yakın" i]',
        'button[aria-label*="Nearby" i]',
        'button:has-text("Yakınında")',
        'button:has-text("Nearby")',
        'button[data-tooltip*="Yakınında" i]',
    ]
    for pattern in nearbyPatterns:
        try:
            btn = page.locator(pattern).first
            if await btn.is_visible(timeout=3000):
                await btn.click()
                logger.info("'Yakınında' butonu tıklandı: %s", pattern)
                await page.wait_for_timeout(3000)
                return True
        except Exception:
            continue
    logger.error("'Yakınında' butonu bulunamadı!")
    return False


async def navigateToNearby(page: Page, ilce: str, mahalle: str) -> bool:
    """
    Maps'e gidip mahalle araması yapar, kart açıksa direkt Yakınında'ya basar,
    liste gelirse ilk karta tıklayıp sonra Yakınında'ya basar.
    Dönen değer: Yakınında arama ekranına ulaşıldıysa True.
    """
    searchQuery = f"{mahalle} Mahallesi {ilce}/İstanbul"
    # URL encode ile doğrudan Maps search URL'ine git
    # Neden: Arama kutusunu bulmak yerine URL ile arama yapmak daha güvenilir
    encodedQuery = searchQuery.replace(" ", "+")
    searchUrl = f"{GOOGLE_MAPS_SEARCH_URL}{encodedQuery}"

    # 1) Maps search URL'ine git
    await page.goto(searchUrl, timeout=PAGE_LOAD_TIMEOUT)
    await acceptCookiesIfPresent(page)
    logger.info("[%s > %s] Arama URL'i açıldı: '%s'", ilce, mahalle, searchQuery)
    await page.wait_for_timeout(4000)

    # 2) Durumu kontrol et: kart mı açıldı, liste mi geldi?
    isCardOpen = await isCardDetailOpen(page)

    if isCardOpen:
        # Kart detayı açık → direkt Yakınında butonuna bas
        logger.info("[%s > %s] Kart detayı açık, Yakınında'ya basılıyor.", ilce, mahalle)
        return await clickNearbyButton(page)

    # Feed (liste) geldi mi kontrol et
    hasFeed = False
    try:
        await page.wait_for_selector('[role="feed"]', timeout=5000)
        hasFeed = True
    except PlaywrightTimeout:
        pass

    if hasFeed:
        # Liste geldi → ilk karta tıkla → kart detayına gir → Yakınında
        logger.info("[%s > %s] Liste görünümü geldi, ilk karta tıklanıyor.", ilce, mahalle)
        if not await clickFirstCardInList(page):
            logger.error("[%s > %s] İlk kart tıklanamadı.", ilce, mahalle)
            return False
        return await clickNearbyButton(page)

    # Ne kart ne liste geldi, son şans olarak Yakınında dene
    logger.warning("[%s > %s] Ne kart ne liste algılandı, Yakınında denenecek.", ilce, mahalle)
    return await clickNearbyButton(page)
