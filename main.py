"""
Created by  : Mapin Data
Created At  : 2026-05-20
Subject     : Nearby scraper ana orkestrasyon modülü.
              - Her ilçe için yeni browser context (session) oluşturur
              - Mahalleler 4 worker ile paralel işlenir
              - Her mahalle bitince user-agent değişir
              - İlçe bitince context kapatılır → yeni session başlar

              Kullanım:
                python3 main.py
"""

import asyncio
import os

from playwright.async_api import async_playwright, BrowserContext

from config import (
    ISTANBUL_ILCELER,
    MAX_WORKERS,
    OUTPUT_DIR,
    OUTPUT_FILE,
    BETWEEN_MAHALLE_WAIT,
    BETWEEN_ILCE_WAIT,
)
from log_config import getLogger
from progress_manager import loadProgress, saveProgress, isMahalleProcessed
from browser_manager import createFreshContext, getNextUserAgent, refreshCookies
from scraper import processMahalle

logger = getLogger(__name__)


async def main():
    """
    Ana akış:
    - Her ilçe için yeni bir browser context (session) oluşturulur
    - Mahalleler 4 worker ile paralel işlenir
    - Her mahalle bitince user-agent değişir (yeni page ile)
    - Tüm mahallelerin keyword aramaları yapılır
    - İlçe bitince context kapatılır → yeni session başlar
    """
    progress = loadProgress()
    outputFile = OUTPUT_FILE

    if progress.get("outputFile"):
        outputFile = progress["outputFile"]
        logger.info("Kaldığı yerden devam ediliyor: %s", outputFile)
    else:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        progress["outputFile"] = outputFile
        saveProgress(progress.get("processed", []), outputFile)
        logger.info("Yeni çıktı dosyası: %s", outputFile)

    semaphore = asyncio.Semaphore(MAX_WORKERS)

    async def worker(ilce: str, mahalle: str, context: BrowserContext):
        """Tek bir mahalle için semaphore kontrollü worker."""
        async with semaphore:
            await processMahalle(context, ilce, mahalle, progress, outputFile)
            await asyncio.sleep(BETWEEN_MAHALLE_WAIT / 1000)

    async with async_playwright() as playwrightInstance:
        browser = await playwrightInstance.chromium.launch(headless=True)

        ilceNames = list(ISTANBUL_ILCELER.keys())
        for ilceIndex, ilce in enumerate(ilceNames):
            mahalleler = ISTANBUL_ILCELER[ilce]

            # İşlenmemiş mahalleleri filtrele
            pendingMahalleler = [
                m for m in mahalleler
                if not isMahalleProcessed(progress, ilce, m)
            ]

            if not pendingMahalleler:
                logger.info("[%s] Tüm mahalleler zaten işlenmiş, atlanıyor.", ilce)
                continue

            # Her ilçe için yeni session (context) oluştur → cookie sıfırlanır
            logger.info("═══ İlçe: %s (%s mahalle) ═══", ilce, len(pendingMahalleler))
            context = await createFreshContext(browser, getNextUserAgent())

            # Cookie kabul et: Maps'e ilk girişte consent ekranını geç
            initialPage = await context.new_page()
            await refreshCookies(initialPage)
            await initialPage.close()

            # Mahalleleri worker'larla paralel işle
            tasks = [
                worker(ilce, mahalle, context)
                for mahalle in pendingMahalleler
            ]
            logger.info("[%s] %s worker ile %s mahalle işlenecek.", ilce, MAX_WORKERS, len(tasks))
            await asyncio.gather(*tasks, return_exceptions=True)

            # İlçe bitti → context (session) kapat
            await context.close()
            logger.info("[%s] İlçe tamamlandı, session kapatıldı.", ilce)

            # İlçeler arası bekleme (son ilçe değilse)
            isLastIlce = ilceIndex >= len(ilceNames) - 1
            if not isLastIlce:
                logger.info("İlçeler arası %s saniye bekleniyor...", BETWEEN_ILCE_WAIT)
                await asyncio.sleep(BETWEEN_ILCE_WAIT)

        await browser.close()

    logger.info("Tüm işlemler tamamlandı.")


if __name__ == "__main__":
    asyncio.run(main())
