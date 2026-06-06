"""
Created by  : Mapin Data
Created At  : 2026-05-20
Subject     : Merkezi logging yapılandırması.
              Tüm modüller bu dosyadaki logger'ı kullanır.
"""

import logging
import os
import sys

from config import LOGS_DIR

os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(LOGS_DIR, "nearby_scraper.log"),
            mode="w",
            encoding="utf-8",
        ),
    ],
)


def getLogger(name: str) -> logging.Logger:
    """Modül adına göre logger döndürür."""
    return logging.getLogger(name)
