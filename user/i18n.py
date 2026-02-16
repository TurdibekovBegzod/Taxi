
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # user/
TRANSLATION_PATH = BASE_DIR / "translations.json"  

print(TRANSLATION_PATH)  # path to'g'riligini tekshirish uchun

with open(TRANSLATION_PATH, "r", encoding="utf-8") as f:
    translations = json.load(f)

def t(lang: str, key: str) -> str:
    return translations.get(key, {}).get(lang, key)
