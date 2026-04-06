import logging
import sys
import os
from pathlib import Path

def setup_logging():
    """Logger sozlash uchun funksiya"""
    
    # Logs papkasini yaratish
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Log formatini sozlash
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s — %(message)s"
    
    # Railway uchun konsolga yozish
    if "RAILWAY_ENVIRONMENT" in os.environ:
        # Railway da faylga yozish o'rniga konsolga yozamiz
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[logging.StreamHandler(sys.stdout)]
        )
    else:
        # Lokal uchun faylga yozish
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_dir / "bot.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    return logging.getLogger(__name__)

# Import qilish uchun os qo'shish
import os
