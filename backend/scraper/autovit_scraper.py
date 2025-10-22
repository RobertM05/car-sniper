import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.autovit.ro/autoturisme/{}/{}"

_LIST_CACHE: dict[str, tuple[float, str]] = {}
_DETAIL_CACHE: dict[str, tuple[float, str]] = {}
_CACHE_TTL_SECONDS = 300


def _get_cached(cache: dict[str, tuple[float, str]], key: str) -> str | None:
    entry = cache.get(key)
    if not entry:
        return None
    ts, text = entry
    if time.time() - ts < _CACHE_TTL_SECONDS:
        return text
    return None


def _set_cache(cache: dict[str, tuple[float, str]], key: str, text: str) -> None:
    cache[key] = (time.time(), text)


def _fetch_text(url: str, headers: dict) -> str | None:
    is_list = ("/autoturisme/" in url and "/anunt/" not in url)
    cache = _LIST_CACHE if is_list else _DETAIL_CACHE
    cached = _get_cached(cache, url)
    if cached is not None:
        return cached
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            _set_cache(cache, url, resp.text)
            return resp.text
    except Exception:
        return None
    return None


def _parse_detail_page(html: str) -> dict:
    dsoup = BeautifulSoup(html, "html.parser")
    out: dict = {}
    ogt = dsoup.find("meta", attrs={"property": "og:title"})
    if ogt and ogt.get("content"):
        title_text = ogt["content"].split(" - ")[0]
        out["title"] = title_text
        m = re.search(r"([0-9][0-9\s\.]+)\s*EUR", ogt["content"], re.IGNORECASE)
        if m:
            out["price"] = m.group(1).replace(" ", "").replace(".", "") + " €"
    y = dsoup.find(attrs={"data-testid": "year"})
    if y:
        val = y.find("p", class_=lambda c: c and "ooa-1jz96sd" in c)
        if val:
            try:
                out["year"] = int(re.sub(r"\D", "", val.get_text()))
            except Exception:
                out["year"] = val.get_text(strip=True)
    km = dsoup.find(attrs={"data-testid": "mileage"})
    if km:
        val = km.find("p", class_=lambda c: c and "ooa-1jz96sd" in c)
        if val:
            out["km"] = val.get_text(strip=True)
    cc = dsoup.find(attrs={"data-testid": "engine_capacity"})
    if cc:
        val = cc.find("p", class_=lambda c: c and "ooa-1jz96sd" in c)
        if val:
            out["cc"] = val.get_text(strip=True)
    hp = dsoup.find(attrs={"data-testid": "engine_power"})
    if hp:
        val = hp.find("p", class_=lambda c: c and "ooa-1jz96sd" in c)
        if val:
            out["hp"] = val.get_text(strip=True)
    return out


def scrape_autovit(
    make: str,
    model: str,
    page: int = 1,
    limit: int = 10,
    max_pages: int = 5,
    enrich: bool = False,
    *,
    max_price: int | None = None,
    min_year: int | None = None,
    max_km: int | None = None,
):
    """
    Scraper robust pentru Autovit:
    - Paginateaza pe mai multe pagini (max_pages)
    - Parseaza JSON-LD pentru titlu/pret; leaga link-urile de detaliu
    - Enrich pe pagina de detaliu: year, km, cc, hp (best-effort)
    - Fallback pe HTML daca JSON-LD lipseste
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0 Safari/537.36"
        )
    }

    results: list[dict] = []
    seen_links_total: set[str] = set()

    def _scrape_pass(use_filters: bool) -> None:
        nonlocal results
        current_page = page
        while len(results) < limit and current_page <= max_pages:
            # Build query params for server-side filtering
            params = {"page": str(current_page)} if use_filters else {"page": str(current_page)}
            if use_filters and max_price is not None:
                params["search[filter_float_price:to]"] = str(max_price)
            if use_filters and min_year is not None:
                params["search[filter_float_year:from]"] = str(min_year)
            if use_filters and max_km is not None:
                params["search[filter_float_mileage:to]"] = str(max_km)

            url = BASE_URL.format(make.lower(), model.lower())
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
            except Exception:
                break

            soup = BeautifulSoup(response.text, "html.parser")

            # Colecteaza link-urile de detaliu din pagina
            detail_links: list[str] = []
            seen_page = set()
            for a in soup.find_all("a", href=True):
                href: str = a["href"]
                if "/autoturisme/anunt/" in href and href.endswith(".html"):
                    if href.startswith("/"):
                        href = "https://www.autovit.ro" + href
                    if href not in seen_page:
                        seen_page.add(href)
                        detail_links.append(href)

            # 1) JSON-LD pe pagina curenta
            try:
                script = soup.find("script", {"id": "listing-json-ld", "type": "application/ld+json"})
                if script and script.string:
                    data = json.loads(script.string)
                    items = data.get("mainEntity", {}).get("itemListElement", [])
                    for idx, elem in enumerate(items):
                        if len(results) >= limit:
                            break
                        price_spec = elem.get("priceSpecification", {})
                        price = price_spec.get("price")
                        car = elem.get("itemOffered", {})
                        name = car.get("name")
                        if not name or price is None:
                            continue
                        # Prefer URL from JSON-LD if available; fallback to collected link by index
                        link = (
                            car.get("url")
                            or elem.get("url")
                            or (detail_links[idx] if idx < len(detail_links) else url)
                        )
                        if link and link.startswith("/"):
                            link = "https://www.autovit.ro" + link
                        if link in seen_links_total:
                            continue
                        seen_links_total.add(link)

                        item = {
                            "title": str(name),
                            "price": f"{price} €",
                            "link": link,
                        }
                        # Detalii suplimentare din pagina de anunt (optional, doar daca enrich=True)
                        if enrich:
                            try:
                                det = requests.get(link, headers=headers, timeout=10)
                                if det.status_code == 200:
                                    dsoup = BeautifulSoup(det.text, "html.parser")
                                    y = dsoup.find(attrs={"data-testid": "year"})
                                    if y:
                                        val = y.find("p", class_=lambda c: c and "ooa-1jz96sd" in c)
                                        if val:
                                            try:
                                                item["year"] = int(re.sub(r"\D", "", val.get_text()))
                                            except Exception:
                                                item["year"] = val.get_text(strip=True)
                                    km = dsoup.find(attrs={"data-testid": "mileage"})
                                    if km:
                                        val = km.find("p", class_=lambda c: c and "ooa-1jz96sd" in c)
                                        if val:
                                            item["km"] = val.get_text(strip=True)
                                    cc = dsoup.find(attrs={"data-testid": "engine_capacity"})
                                    if cc:
                                        val = cc.find("p", class_=lambda c: c and "ooa-1jz96sd" in c)
                                        if val:
                                            item["cc"] = val.get_text(strip=True)
                                    hp = dsoup.find(attrs={"data-testid": "engine_power"})
                                    if hp:
                                        val = hp.find("p", class_=lambda c: c and "ooa-1jz96sd" in c)
                                        if val:
                                            item["hp"] = val.get_text(strip=True)
                            except Exception:
                                pass

                        results.append(item)
            except Exception:
                pass

            # 2) Completeaza din link-urile ramase (constructie din pagina de detaliu, optional)
            if len(results) < limit and enrich:
                for link in detail_links:
                    if len(results) >= limit:
                        break
                    if link in seen_links_total:
                        continue
                    seen_links_total.add(link)
                    item = {"link": link}
                    try:
                        det = requests.get(link, headers=headers, timeout=10)
                        if det.status_code == 200:
                            dsoup = BeautifulSoup(det.text, "html.parser")
                            # Titlu: foloseste og:title sau compune din brand/model/versiune
                            ogt = dsoup.find("meta", attrs={"property": "og:title"})
                            if ogt and ogt.get("content"):
                                title_text = ogt["content"].split(" - ")[0]
                                item["title"] = title_text
                                # Price din og:title
                                m = re.search(r"([0-9][0-9\s\.]+)\s*EUR", ogt["content"], re.IGNORECASE)
                                if m:
                                    item["price"] = m.group(1).replace(" ", "").replace(".", "") + " €"
                            # Year/Km/CC/HP
                            y = dsoup.find(attrs={"data-testid": "year"})
                            if y:
                                val = y.find("p", class_=lambda c: c and "ooa-1jz96sd" in c)
                                if val:
                                    try:
                                        item["year"] = int(re.sub(r"\\D", "", val.get_text()))
                                    except Exception:
                                        item["year"] = val.get_text(strip=True)
                            km = dsoup.find(attrs={"data-testid": "mileage"})
                            if km:
                                val = km.find("p", class_=lambda c: c and "ooa-1jz96sd" in c)
                                if val:
                                    item["km"] = val.get_text(strip=True)
                            cc = dsoup.find(attrs={"data-testid": "engine_capacity"})
                            if cc:
                                val = cc.find("p", class_=lambda c: c and "ooa-1jz96sd" in c)
                                if val:
                                    item["cc"] = val.get_text(strip=True)
                            hp = dsoup.find(attrs={"data-testid": "engine_power"})
                            if hp:
                                val = hp.find("p", class_=lambda c: c and "ooa-1jz96sd" in c)
                                if val:
                                    item["hp"] = val.get_text(strip=True)
                    except Exception:
                        pass
                    # Fallback-uri minime daca lipsesc
                    item.setdefault("title", link.rsplit("/", 1)[-1])
                    item.setdefault("price", "")
                    results.append(item)

            current_page += 1

    # Pass 1: cu filtre in URL
    _scrape_pass(use_filters=True)
    # Fallback: daca am obtinut prea putine rezultate, mai facem un pass fara filtre server-side
    if len(results) < max(10, limit // 2) and (max_price is not None or min_year is not None or max_km is not None):
        _scrape_pass(use_filters=False)

    return results[:limit]
