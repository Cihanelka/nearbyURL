"""
Created by  : Mapin Data
Created At  : 2026-05-20
Subject     : İlerleme takip sistemi.
              Hangi ilçe/mahalle'nin işlendiğini JSON dosyasına kaydeder,
              yeniden başlatıldığında kaldığı yerden devam etmeyi sağlar.
"""

import json
import os
from datetime import datetime

from config import OUTPUT_DIR, OUTPUT_FILE, PROGRESS_FILE
from log_config import getLogger

logger = getLogger(__name__)


def loadProgress() -> dict:
    """Kaydedilmiş ilerleme durumunu yükler."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.warning("İlerleme dosyası okunamadı: %s", exc)
    return {"processed": [], "outputFile": None}


def saveProgress(processedItems: list, outputFile: str) -> None:
    """İlerleme durumunu JSON dosyasına kaydeder."""
    progressData = {
        "processed": processedItems,
        "outputFile": outputFile,
        "lastUpdated": datetime.now().isoformat(),
    }
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progressData, f, ensure_ascii=False, indent=2)


def isMahalleProcessed(progress: dict, ilce: str, mahalle: str) -> bool:
    """Bir mahallenin daha önce işlenip işlenmediğini kontrol eder."""
    itemKey = f"{ilce}|{mahalle}"
    return itemKey in progress.get("processed", [])


def markMahalleProcessed(progress: dict, ilce: str, mahalle: str) -> None:
    """Bir mahalleyi işlenmiş olarak işaretler ve kaydeder."""
    itemKey = f"{ilce}|{mahalle}"
    if itemKey not in progress.get("processed", []):
        progress["processed"].append(itemKey)
        saveProgress(progress["processed"], progress.get("outputFile", OUTPUT_FILE))
