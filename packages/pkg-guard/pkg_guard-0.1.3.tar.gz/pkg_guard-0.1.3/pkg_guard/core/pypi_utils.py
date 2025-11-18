import requests
import json
import time
from pathlib import Path
from rapidfuzz import process, fuzz

PYPI_JSON_URL = "https://pypi.org/pypi/{name}/json"
CACHE_PATH = Path.home() / ".pkg_guard_cache.json"

def _load_cache():
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}

def _save_cache(data):
    CACHE_PATH.write_text(json.dumps(data, indent=2))

def cache_get(name: str):
    data = _load_cache()
    entry = data.get(name)
    if entry and (time.time() - entry["time"]) < 86400:  # 1 day cache
        return entry["exists"]
    return None

def cache_set(name: str, exists: bool):
    data = _load_cache()
    data[name] = {"exists": exists, "time": time.time()}
    _save_cache(data)

def pypi_exists(name: str) -> bool:
    """Check if a package exists on PyPI with caching and error resilience."""
    cached = cache_get(name)
    if cached is not None:
        return cached

    try:
        r = requests.get(PYPI_JSON_URL.format(name=name), timeout=5)
        exists = r.status_code == 200
        cache_set(name, exists)
        return exists
    except requests.RequestException:
        return False

def load_popular(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def suggest_names(name: str, population: list[str], limit: int = 5):
    if not population:
        return []
    return process.extract(name, population, scorer=fuzz.WRatio, limit=limit)
