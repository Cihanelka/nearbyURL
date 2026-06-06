"""
Created by  : Mapin Data
Created At  : 2026-05-20
Subject     : Keyword arama, sonuç toplama (scroll + kart parse) ve JSON kaydetme.
              - Yakınında ekranında keyword ile arama yapar
              - Feed'i scroll ederek tüm kartları toplar
              - Sonuçları thread-safe olarak JSON dosyasına yazar
"""

import asyncio
import json
import os
import random
from typing import Dict, List, Optional

import aiofiles
from playwright.async_api import Page, BrowserContext, TimeoutError as PlaywrightTimeout

from config import (
    KEYWORDS,
    RESULTS_LOAD_WAIT,
    SCROLL_WAIT_MIN,
    SCROLL_WAIT_MAX,
    BETWEEN_KEYWORD_WAIT,
)
from maps_navigator import navigateToNearby
from progress_manager import isMahalleProcessed, markMahalleProcessed
from log_config import getLogger

logger = getLogger(__name__)

# Dosya yazma kilidi (tüm worker'lar arasında paylaşılır)
_FILE_LOCK = asyncio.Lock()


async def scrollFeedToBottom(page: Page, maxScrolls: int = 30) -> int:
    """
    Sol paneldeki sonuç listesini scroll ederek aşağıya çeker.
    Dönen değer: toplam kart sayısı.
    """
    feedSelector = '[role="feed"]'
    try:
        await page.wait_for_selector(feedSelector, timeout=10000)
    except PlaywrightTimeout:
        logger.warning("Feed (rol=feed) bulunamadı, scroll atlanıyor.")
        return 0

    previousCount = 0
    noNewCount = 0
    scrollCount = 0

    while scrollCount < maxScrolls:
        cards = await page.locator(f"{feedSelector} a.hfpxzc").count()
        if cards > previousCount:
            previousCount = cards
            noNewCount = 0
        else:
            noNewCount += 1
            if noNewCount >= 3:
                logger.info("Yeni kart yüklenmiyor, scroll durduruluyor (%s kart).", cards)
                break
        await page.locator(feedSelector).evaluate("(el) => el.scrollTop += 5000")
        await page.wait_for_timeout(random.randint(SCROLL_WAIT_MIN, SCROLL_WAIT_MAX))
        scrollCount += 1

    return previousCount


async def _parseCardData(card, cardLink=None) -> Optional[Dict[str, str]]:
    """
    Tek bir Maps kart elementinden veri çeker.
    Parametreler:
      card      : Kart container div (a.hfpxzc'nin parent'ı)
      cardLink  : a.hfpxzc elementi (href ve aria-label burada)
    Görseldeki kart yapısı:
      - İsim (aria-label veya fontHeadlineSmall)
      - Puan + Yorum sayısı + Fiyat aralığı
      - Google Kategori + Adres
    Dönen değer: dict veya None (geçersiz kart ise).
    """
    # ── Href (place URL) — a.hfpxzc'den al ──
    href = ""
    name = ""
    try:
        if cardLink:
            href = await cardLink.get_attribute("href") or ""
            name = await cardLink.get_attribute("aria-label") or ""
    except Exception:
        pass

    # aria-label'dan isim gelemediyse DOM'dan dene
    if not name:
        try:
            nameEl = card.locator("div.fontHeadlineSmall, div.qBF1Pd").first
            name = await nameEl.inner_text() if await nameEl.is_visible(timeout=500) else ""
        except Exception:
            pass

    if not name or name.strip() in ["Reklam", "Ad", ""]:
        return None

    # ── Puan (sayısal değer, ör: "4,5") ──
    rating = ""
    try:
        ratingEl = card.locator("span.MW4etd").first
        if await ratingEl.is_visible(timeout=500):
            rating = await ratingEl.inner_text()
    except Exception:
        pass

    # ── Yorum sayısı (ör: "(1.215)") ──
    reviewCount = ""
    try:
        reviewEl = card.locator("span.UY7F9").first
        if await reviewEl.is_visible(timeout=500):
            reviewCount = await reviewEl.inner_text()
    except Exception:
        pass

    # ── Fiyat aralığı (ör: "₺400–600") ──
    priceRange = ""
    try:
        priceEl = card.locator("span.wcldff").first
        if await priceEl.is_visible(timeout=500):
            priceRange = await priceEl.inner_text()
    except Exception:
        pass

    # ── Google Kategori + Adres (W4Efsd satırlarından çekiyoruz) ──
    # Neden: Maps kartlarında puan satırının altındaki ilk W4Efsd bloğu
    #        "Kategori · Adres" formatındadır.
    googleCategory = ""
    address = ""
    try:
        infoBlocks = card.locator("div.W4Efsd")
        blockCount = await infoBlocks.count()

        # İlk W4Efsd bloğu genelde puan/yorum satırıdır,
        # ikinci blok kategori + adres satırıdır.
        if blockCount >= 2:
            categoryBlock = infoBlocks.nth(1)
            categoryText = await categoryBlock.inner_text() if await categoryBlock.is_visible(timeout=500) else ""

            if categoryText:
                parts = [p.strip() for p in categoryText.split("·")]
                if parts:
                    googleCategory = parts[0].strip()
                    address = ", ".join(parts[1:]).strip() if len(parts) > 1 else ""
    except Exception:
        pass

    return {
        "name": name.strip(),
        "rating": rating.strip() if rating else "",
        "reviewCount": reviewCount.strip() if reviewCount else "",
        "priceRange": priceRange.strip() if priceRange else "",
        "googleCategory": googleCategory.strip() if googleCategory else "",
        "address": address.strip() if address else "",
        "href": href,
    }


async def scrapeKeywordResults(page: Page, keyword: str) -> List[dict]:
    """
    Yakınında ekranındaki arama kutusuna keyword yazar ve sonuçları toplar.
    Dönen değer: Bulunan mekanların listesi.
    """
    results = []
    try:
        # Yakınında ekranındaki arama kutusu: combobox veya searchboxinput
        searchBoxSelector = 'input[role="combobox"], input[id="searchboxinput"]'
        await page.wait_for_selector(searchBoxSelector, state="visible", timeout=15000)
        searchBox = page.locator(searchBoxSelector).first
        await searchBox.fill("")
        await searchBox.fill(keyword)
        await searchBox.press("Enter")
        await page.wait_for_timeout(RESULTS_LOAD_WAIT)

        # Kartların (a.hfpxzc) yüklenmesini bekle
        try:
            await page.wait_for_selector('a.hfpxzc', timeout=8000)
        except PlaywrightTimeout:
            logger.info("Keyword '%s' için sonuç bulunamadı (kart yok).", keyword)
            return results

        cardCount = await scrollFeedToBottom(page, maxScrolls=25)
        logger.info("Keyword '%s' scroll sonrası %s kart bulundu.", keyword, cardCount)

        # Her a.hfpxzc kartının parent div'ini al (kart bilgileri orada)
        cardLinks = await page.locator('a.hfpxzc').all()
        logger.info("'%s' için toplam %s kart yüklendi.", keyword, len(cardLinks))

        for cardLink in cardLinks:
            try:
                # a.hfpxzc'nin parent div'i = kart container
                cardContainer = cardLink.locator('..')
                parsedCard = await _parseCardData(cardContainer, cardLink)
                if not parsedCard:
                    continue
                results.append(parsedCard)
            except Exception as exc:
                logger.debug("Kart işlenirken hata: %s", exc)
                continue

        logger.info("'%s' için %s kart çekildi.", keyword, len(results))
    except Exception as exc:
        logger.error("Keyword '%s' işlenirken hata: %s", keyword, exc)

    return results


async def appendResult(outputFile: str, result: dict) -> None:
    """Sonucu JSON dosyasına thread-safe olarak ekler."""
    async with _FILE_LOCK:
        if not os.path.exists(outputFile):
            async with aiofiles.open(outputFile, "w", encoding="utf-8") as f:
                await f.write("[\n")
                await f.write(json.dumps(result, ensure_ascii=False, indent=2))
                await f.write("\n]")
        else:
            async with aiofiles.open(outputFile, "r+", encoding="utf-8") as f:
                content = await f.read()
                if content.strip().endswith("]"):
                    content = content.strip()[:-1].rstrip()
                    if content.endswith(","):
                        content = content[:-1]
                    await f.seek(0)
                    await f.write(content)
                    await f.write(",\n")
                    await f.write(json.dumps(result, ensure_ascii=False, indent=2))
                    await f.write("\n]")
                    await f.truncate()


async def processMahalle(
    context: BrowserContext,
    ilce: str,
    mahalle: str,
    progress: dict,
    outputFile: str,
) -> bool:
    """
    Belirli bir ilçe ve mahalle için:
    1. Maps'e git → mahalle araması yap
    2. Kart açıksa Yakınında'ya bas / Liste gelirse ilk karta tıkla → Yakınında'ya bas
    3. Tüm keyword'lerle arama yap ve sonuçları topla
    4. JSON'a kaydet, ilerlemeyi işaretle
    """
    if isMahalleProcessed(progress, ilce, mahalle):
        logger.info("[%s > %s] Daha önce işlenmiş, atlanıyor.", ilce, mahalle)
        return True

    page = await context.new_page()
    try:
        logger.info("═══ [%s > %s] İşleniyor ═══", ilce, mahalle)

        # Navigasyon: Maps → arama → kart/liste → Yakınında
        isNearbyReady = await navigateToNearby(page, ilce, mahalle)

        if not isNearbyReady:
            errorMsg = "Yakınında ekranına ulaşılamadı"
            logger.error("[%s > %s] %s", ilce, mahalle, errorMsg)
            await appendResult(outputFile, {
                "mahalle": mahalle,
                "ilce": ilce,
                "searchTerm": f"{mahalle} Mahallesi {ilce}/İstanbul",
                "keywords": {},
                "error": errorMsg,
            })
            markMahalleProcessed(progress, ilce, mahalle)
            return False

        # Tüm keyword'ler ile arama yap — her keyword bittiğinde çıktıya kaydet
        for keyword in KEYWORDS:
            logger.info("  ─── Keyword: %s ───", keyword)
            try:
                keywordResults = await scrapeKeywordResults(page, keyword)
            except Exception as exc:
                logger.error("  Keyword '%s' hatası: %s", keyword, exc)
                keywordResults = []

            await appendResult(outputFile, {
                "mahalle": mahalle,
                "ilce": ilce,
                "searchTerm": f"{mahalle} Mahallesi {ilce}/İstanbul",
                "keyword": keyword,
                "results": keywordResults,
            })
            await page.wait_for_timeout(BETWEEN_KEYWORD_WAIT)
        markMahalleProcessed(progress, ilce, mahalle)
        logger.info("[%s > %s] Tamamlandı.", ilce, mahalle)
        return True

    except Exception as exc:
        errorMsg = str(exc)
        logger.error("[%s > %s] Kritik hata: %s", ilce, mahalle, errorMsg)
        await appendResult(outputFile, {
            "mahalle": mahalle,
            "ilce": ilce,
            "searchTerm": f"{mahalle} Mahallesi {ilce}/İstanbul",
            "keywords": {},
            "error": errorMsg,
        })
        markMahalleProcessed(progress, ilce, mahalle)
        return False
    finally:
        await page.close()
