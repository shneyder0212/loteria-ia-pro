import os, time, json, hashlib, random
from pathlib import Path
from urllib.parse import urlparse
import requests

DEFAULT_MIN_INTERVAL = float(os.getenv("SCRAPER_MIN_INTERVAL_SECONDS", "5.0"))
CACHE_TTL = int(os.getenv("SCRAPER_CACHE_TTL_SECONDS", "21600"))
MAX_RETRIES = int(os.getenv("SCRAPER_MAX_RETRIES", "3"))

class SafeHttpClient:
    def __init__(self, cache_dir=None):
        root = cache_dir or os.getenv("SCRAPER_CACHE_DIR")
        if not root:
            db_path = os.getenv("DB_PATH", "loteria_master_ai.db")
            root = os.path.join(os.path.dirname(db_path) or ".", "http_cache")
        self.cache_dir = Path(root)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; ShneyderIA/3.0; result-history-loader)",
            "Accept-Language": "es-ES,es;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        })
        self.last_request = {}

    def _cache_paths(self, url):
        key = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{key}.body", self.cache_dir / f"{key}.json"

    def _read_cache(self, url):
        body_path, meta_path = self._cache_paths(url)
        if not body_path.exists() or not meta_path.exists():
            return None
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if time.time() - float(meta.get("saved_at", 0)) > CACHE_TTL:
                return None
            return {
                "url": url,
                "status_code": int(meta.get("status_code", 200)),
                "text": body_path.read_text(encoding="utf-8", errors="ignore"),
                "from_cache": True,
            }
        except Exception:
            return None

    def _write_cache(self, url, status, text):
        if status != 200 or not text:
            return
        body_path, meta_path = self._cache_paths(url)
        try:
            body_path.write_text(text, encoding="utf-8")
            meta_path.write_text(json.dumps({
                "saved_at": time.time(),
                "status_code": status
            }), encoding="utf-8")
        except Exception:
            pass

    def _respect_rate(self, url):
        domain = urlparse(url).netloc.lower()
        last = self.last_request.get(domain, 0.0)
        wait = DEFAULT_MIN_INTERVAL - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        self.last_request[domain] = time.time()

    def get(self, url, use_cache=True, timeout=20):
        if use_cache:
            cached = self._read_cache(url)
            if cached:
                return cached

        last_error = None
        for attempt in range(MAX_RETRIES):
            self._respect_rate(url)
            try:
                r = self.session.get(url, timeout=timeout, allow_redirects=True)
                status = r.status_code

                if status == 429:
                    retry_after = r.headers.get("Retry-After")
                    try:
                        pause = min(120, max(10, int(retry_after)))
                    except Exception:
                        pause = min(120, 15 * (2 ** attempt))
                    time.sleep(pause + random.uniform(0.5, 2.0))
                    last_error = f"HTTP 429; reintento {attempt+1}"
                    continue

                if status in (500, 502, 503, 504):
                    time.sleep(min(60, (5 * (2 ** attempt))) + random.uniform(0.3, 1.5))
                    last_error = f"HTTP {status}"
                    continue

                r.raise_for_status()
                text = r.text
                self._write_cache(url, status, text)
                return {
                    "url": str(r.url),
                    "status_code": status,
                    "text": text,
                    "from_cache": False,
                }

            except requests.RequestException as e:
                last_error = str(e)
                time.sleep(min(30, 3 * (2 ** attempt)) + random.uniform(0.2, 1.0))

        raise RuntimeError(last_error or "No se pudo obtener la URL")

CLIENT = SafeHttpClient()
