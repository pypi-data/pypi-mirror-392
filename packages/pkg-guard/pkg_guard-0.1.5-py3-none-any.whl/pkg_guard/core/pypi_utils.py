import requests
import json
import time
from pathlib import Path
from rapidfuzz import process, fuzz

PYPI_JSON_URL = "https://pypi.org/pypi/{name}/json"
CACHE_PATH = Path.home() / ".pkg_guard_cache.json"

POPULAR_PATH = Path(__file__).parent.parent / "popular_packages.txt"
TOP_PYPI_URL = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.json"
META_PATH = POPULAR_PATH.with_suffix(".meta.json")

def auto_refresh_popular(limit: int = 200, days: int = 30):
    """Refresh local popular_packages.txt if older than `days`."""
    try:
        # Check last refresh timestamp
        if META_PATH.exists():
            meta = json.loads(META_PATH.read_text(encoding="utf-8"))
            last_update = meta.get("last_update", 0)
            if time.time() - last_update < days * 86400:
                return  # not old enough yet

        resp = requests.get(TOP_PYPI_URL, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            top = [row["project"] for row in data["rows"][:limit]]
            POPULAR_PATH.write_text("\n".join(top), encoding="utf-8")
            META_PATH.write_text(json.dumps({"last_update": time.time()}))
            print(f"✅ Auto-refreshed popular_packages.txt with {len(top)} packages.")
    except Exception:
        pass  # silently skip if offline

def search_pypi(query: str, limit: int = 10) -> list[str]:
    """Search PyPI for packages matching the query."""
    try:
        url = f"https://pypi.org/search/?q={query}&format=json"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return [r["name"] for r in data.get("projects", [])][:limit]
    except Exception:
        pass
    return []

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
