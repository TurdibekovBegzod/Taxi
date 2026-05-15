
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # user/
TRANSLATION_PATH = BASE_DIR / "translations.json"  

with open(TRANSLATION_PATH, "r", encoding="utf-8") as f:
    translations = json.load(f)

def t(lang: str, key: str) -> str:
    return translations.get(key, {}).get(lang) or translations.get(key, {}).get("uz") or key
