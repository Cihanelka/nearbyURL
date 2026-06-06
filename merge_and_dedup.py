"""
Created by  : Cascade
Created At  : 2026-05-19
Subject     : output/ klasöründeki tüm JSON dosyalarını tek listeye birleştirir,
              href bazında global duplicate temizler ve düz kayıt formatında
              dedup_output/merged_flat.json olarak kaydeder.

              Her çıktı kaydı: {mahalle, ilce, keyword_category, name, rating, category, address, href}

              Kullanım:
                python3 merge_and_dedup.py
"""

import json
import logging
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Logging ayarı
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).parent / "output"
DEDUP_OUTPUT_DIR = Path(__file__).parent / "dedup_output"
OUTPUT_FILE = DEDUP_OUTPUT_DIR / "merged_flat.json"


# ---------------------------------------------------------------------------
# Yardımcı fonksiyonlar
# ---------------------------------------------------------------------------

def flattenEntry(entry: dict, seenHrefs: set) -> tuple[list[dict], int]:
    """
    Tek bir entry (mahalle/ilce bazlı kayıt) içindeki keywords'ü düz kayıt listesine dönüştürür.
    Daha önce görülen href'leri atlar (global duplicate temizliği).

    Returns:
        (düz kayıt listesi, atlanan duplicate sayısı)
    """
    mahalle = entry.get("mahalle", "")
    ilce = entry.get("ilce", "")
    keywords = entry.get("keywords", {})

    flatRecords = []
    duplicateCount = 0

    for keywordCategory, items in keywords.items():
        for item in items:
            href = item.get("href", "").strip()

            # href yoksa veya daha önce görüldüyse atla
            if not href:
                continue
            if href in seenHrefs:
                duplicateCount += 1
                continue

            seenHrefs.add(href)

            flatRecords.append({
                "mahalle": mahalle,
                "ilce": ilce,
                "keywordCategory": keywordCategory,
                "name": item.get("name", ""),
                "rating": item.get("rating", ""),
                "reviewCount": item.get("reviewCount", ""),
                "priceRange": item.get("priceRange", ""),
                "googleCategory": item.get("googleCategory", ""),
                "address": item.get("address", ""),
                "href": href,
            })

    return flatRecords, duplicateCount


def collectJsonFiles(directory: Path) -> list[Path]:
    """
    Verilen dizindeki tüm .json dosyalarını tarihe göre sıralı döndürür.
    """
    jsonFiles = sorted(directory.glob("*.json"))
    return jsonFiles


def mergeAndFlatten(inputFiles: list[Path]) -> tuple[list[dict], dict]:
    """
    Tüm dosyaları okuyup düz kayıt listesine dönüştürür; global href dedup uygular.

    Returns:
        (düz kayıt listesi, istatistik dict'i)
    """
    seenHrefs: set = set()
    allRecords: list[dict] = []
    totalDuplicates = 0
    totalEntries = 0

    for filePath in inputFiles:
        logger.info(f"İşleniyor: {filePath.name}")
        try:
            with open(filePath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as error:
            logger.warning(f"  Atlandı (JSON parse hatası): {filePath.name} – {error}")
            continue

        if not isinstance(data, list):
            logger.warning(f"  Atlandı (list bekleniyor): {filePath.name}")
            continue

        fileDuplicates = 0
        fileRecords = 0

        for entry in data:
            totalEntries += 1
            flatRecords, duplicateCount = flattenEntry(entry, seenHrefs)
            allRecords.extend(flatRecords)
            fileDuplicates += duplicateCount
            fileRecords += len(flatRecords)

        totalDuplicates += fileDuplicates
        logger.info(f"  → {fileRecords} kayıt eklendi, {fileDuplicates} duplicate atlandı.")

    stats = {
        "processedFiles": len(inputFiles),
        "totalEntries": totalEntries,
        "totalUniqueRecords": len(allRecords),
        "totalDuplicatesRemoved": totalDuplicates,
        "outputFile": str(OUTPUT_FILE),
        "generatedAt": datetime.now().isoformat(),
    }

    return allRecords, stats


# ---------------------------------------------------------------------------
# Ana akış
# ---------------------------------------------------------------------------

def main():
    inputFiles = collectJsonFiles(OUTPUT_DIR)

    if not inputFiles:
        logger.error(f"output/ klasöründe JSON dosyası bulunamadı: {OUTPUT_DIR}")
        return

    logger.info(f"{len(inputFiles)} JSON dosyası bulundu.")
    for f in inputFiles:
        logger.info(f"  - {f.name}")

    allRecords, stats = mergeAndFlatten(inputFiles)

    DEDUP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(allRecords, f, ensure_ascii=False, indent=2)

    logger.info(f"Kaydedildi: {OUTPUT_FILE}")

    # Özet rapor
    print("\n" + "=" * 60)
    print("ÖZET RAPOR")
    print("=" * 60)
    print(f"  İşlenen dosya sayısı      : {stats['processedFiles']}")
    print(f"  Toplam entry sayısı       : {stats['totalEntries']}")
    print(f"  Benzersiz kayıt sayısı    : {stats['totalUniqueRecords']}")
    print(f"  Kaldırılan duplicate      : {stats['totalDuplicatesRemoved']} href")
    print(f"  Çıktı dosyası             : {stats['outputFile']}")
    print(f"  Oluşturulma zamanı        : {stats['generatedAt']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
