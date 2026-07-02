import aiohttp
import asyncio
import re
import json
from bs4 import BeautifulSoup
from logger import get_logger
from metrics import metrics
from dead_letter import dead_letter

log = get_logger("autovit_scraper")

BASE_URL = "https://www.autovit.ro/autoturisme/{}/{}"


async def scrape_autovit(
    make: str,
    model: str,
    page: int = 1,
    limit: int = 100,
    max_pages: int = 5,
    enrich: bool = False,
    *,
    min_price: int | None = None,
    max_price: int | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    max_km: int | None = None,
    sort_order: str = "price_asc",
):
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    ]
    import random

    results: list[dict] = []
    seen_links_total: set[str] = set()
    scrape_stats = {"dupes": 0, "invalid": 0}

    _enrich_sem = asyncio.Semaphore(5)

    async def _fetch_next_data_details(
        url: str, enrich_session
    ) -> tuple[str | None, str | None]:
        ua = random.choice(USER_AGENTS)
        headers_det = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "https://www.autovit.ro/",
        }
        async with _enrich_sem:
            await asyncio.sleep(random.uniform(0.1, 0.5))
            try:
                async with enrich_session.get(url, headers=headers_det, timeout=8) as r:
                    if r.status != 200:
                        return (None, None, None, None)
                    text = await r.text()
                    s = BeautifulSoup(text, "html.parser")
                    price = None
                    image = None
                    year = None
                    km = None
                    nd = s.find("script", {"id": "__NEXT_DATA__"})
                    if nd and nd.string:
                        data = json.loads(nd.string)
                        pp = data.get("props", {}).get("pageProps", {})
                        advert = pp.get("advert") or pp.get("data", {}).get("advert")
                        if advert:
                            p_val = advert.get("price", {}).get("value")
                            if p_val:
                                price = str(int(p_val))
                            photos = advert.get("photos") or advert.get("images")
                            if (
                                photos
                                and isinstance(photos, list)
                                and (len(photos) > 0)
                            ):
                                first_photo = photos[0]
                                if isinstance(first_photo, dict):
                                    image = (
                                        first_photo.get("large")
                                        or first_photo.get("medium")
                                        or first_photo.get("src")
                                    )
                                elif isinstance(first_photo, str):
                                    image = first_photo
                            # Extract year and km from advert parameters
                            for param in advert.get("parameters", []):
                                key = (param.get("key") or "").lower()
                                if key == "year":
                                    year = param.get("value")
                                elif key in ("mileage", "kilometers", "km"):
                                    km = param.get("value")
                    if not price:
                        jld = s.find("script", {"id": "listing-json-ld"})
                        if jld and jld.string:
                            data = json.loads(jld.string)
                            offers = data.get("offers", {})
                            if offers:
                                p = offers.get("price")
                                if p:
                                    price = str(int(float(p)))
                    if not image:
                        og = s.find("meta", attrs={"property": "og:image"})
                        if og and og.get("content"):
                            image = og.get("content")
                    return (price, image, year, km)
            except Exception:
                pass
            return (None, None, None, None)

    async def fetch_page(page_num: int, enrich_session=None):
        try:
            params = {"page": str(page_num)}
            if sort_order == "price_asc":
                params["search[order]"] = "filter_float_price:asc"
            elif sort_order == "price_desc":
                params["search[order]"] = "filter_float_price:desc"
            elif sort_order == "newest":
                params["search[order]"] = "created_at:desc"
            if max_price is not None:
                params["search[filter_float_price:to]"] = str(max_price)
            if min_price is not None:
                params["search[filter_float_price:from]"] = str(min_price)
            if min_year is not None:
                params["search[filter_float_year:from]"] = str(min_year)
            if max_year is not None:
                params["search[filter_float_year:to]"] = str(max_year)
            if max_km is not None:
                params["search[filter_float_mileage:to]"] = str(max_km)
                params["search[advanced_search_expanded]"] = "true"
            url = BASE_URL.format(make.lower().replace(" ", "-"), model.lower())
            ua = random.choice(USER_AGENTS)
            headers_req = {
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://www.google.com/",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            }
            page_ads = []
            seen_links = set()
            retries = 3
            for attempt in range(retries):
                try:
                    async with aiohttp.ClientSession(
                        connector=aiohttp.TCPConnector(ssl=False)
                    ) as sess:
                        await asyncio.sleep(random.uniform(2.0, 4.0))
                        async with sess.get(
                            url, params=params, headers=headers_req, timeout=15
                        ) as response:
                            if response.status in (403, 401):
                                log.warning(
                                    "Autovit blocked",
                                    extra={"status": response.status, "page": page_num},
                                )
                                return "BLOCKED"
                            if response.status == 429:
                                wait_time = 5 * (attempt + 1)
                                log.warning(
                                    "Autovit 429",
                                    extra={
                                        "page": page_num,
                                        "attempt": attempt + 1,
                                        "wait_s": wait_time,
                                    },
                                )
                                await asyncio.sleep(wait_time)
                                continue
                            if response.status != 200:
                                log.warning(
                                    "Autovit non-200",
                                    extra={"status": response.status, "page": page_num},
                                )
                                return None
                            html = await response.text()
                            break
                except Exception as e:
                    log.error(
                        "Autovit page error", extra={"page": page_num, "error": str(e)}
                    )
                    metrics.increment("errors")
                    await asyncio.sleep(3)
                    continue
            else:
                log.error(
                    "Autovit page exhausted retries",
                    extra={"page": page_num, "retries": retries},
                )
                return None
            soup = BeautifulSoup(html, "html.parser")
            detail_links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/autoturisme/anunt/" in href and href.endswith(".html"):
                    if href.startswith("/"):
                        href = "https://www.autovit.ro" + href
                    if href not in detail_links:
                        detail_links.append(href)
            _found_json = False
            script = soup.find(
                "script", {"id": "listing-json-ld", "type": "application/ld+json"}
            )
            if script and script.string:
                try:
                    data = json.loads(script.string)
                    items = data.get("mainEntity", {}).get("itemListElement", [])
                    for idx, elem in enumerate(items):
                        item = elem.get("itemOffered", {})
                        name = item.get("name")
                        if not name:
                            continue
                        price_spec = elem.get("priceSpecification", {})
                        price_raw = price_spec.get("price")
                        link = item.get("url") or elem.get("url")
                        img_url = item.get("image")
                        if isinstance(img_url, list) and img_url:
                            img_url = img_url[0]
                        if not link or link == url:
                            continue
                        if link.startswith("/"):
                            link = "https://www.autovit.ro" + link
                        fingerprint = (
                            link if "-ID" in link else f"{link}__img__{img_url}"
                        )
                        car_year_raw = item.get("productionDate") or item.get(
                            "modelDate"
                        )
                        car_year = None
                        if car_year_raw and re.match("^\\d{4}$", str(car_year_raw)):
                            car_year = str(car_year_raw)
                        car_km_dict = item.get("mileageFromOdometer", {})
                        car_km = (
                            car_km_dict.get("value")
                            if isinstance(car_km_dict, dict)
                            else None
                        )
                        if fingerprint in seen_links_total:
                            scrape_stats["dupes"] += 1
                            continue
                        seen_links_total.add(fingerprint)
                        seen_links.add(link)  # prevent HTML parser from adding duplicate with truncated title
                        if price_raw:
                            try:
                                final_price = int(float(price_raw))
                                jld_make = (
                                    item.get("manufacturer")
                                    or item.get("brand", {}).get("name")
                                    if isinstance(item.get("brand"), dict)
                                    else item.get("brand")
                                )
                                jld_model = item.get("model") or item.get("name")
                                page_ads.append(
                                    {
                                        "title": name,
                                        "price": f"{final_price} €",
                                        "link": link,
                                        "image": img_url,
                                        "subsource": "Autovit",
                                        "year": car_year,
                                        "km": f"{car_km} km" if car_km else None,
                                        "make": jld_make or make,
                                        "model": jld_model,
                                    }
                                )
                                _found_json = True
                            except Exception:
                                pass
                except Exception as e:
                    print(f"JSON-LD Parsing Error: {e}")
            if True:
                articles = soup.find_all("article")
                for art in articles:
                    try:
                        if not art.has_attr("data-id"):
                            continue
                        a = art.find("a", href=True)
                        if not a:
                            continue
                        lnk = a["href"]
                        if lnk.startswith("/"):
                            lnk = "https://www.autovit.ro" + lnk
                        if lnk in seen_links:
                            continue
                        seen_links.add(lnk)
                        h2 = art.find("h2") or art.find("h1")
                        title = h2.get_text(strip=True) if h2 else "No Title"
                        price = "0"
                        price_span = art.find(string=re.compile("EUR"))
                        if price_span:
                            parent = (
                                price_span.parent.parent if price_span.parent else None
                            )
                            if parent:
                                h3 = parent.find("h3")
                                if h3:
                                    raw_p = h3.get_text(strip=True)
                                    clean_p = raw_p.replace(" ", "")
                                    if "," in clean_p:
                                        clean_p = clean_p.replace(".", "").replace(
                                            ",", "."
                                        )
                                    else:
                                        clean_p = clean_p.replace(".", "")
                                    try:
                                        price = str(int(float(clean_p)))
                                    except Exception:
                                        pass
                        img = art.find("img")
                        image_url = img.get("src") if img else None
                        p_num = 0
                        try:
                            p_num = int(float(str(price).replace("€", "").strip()))
                        except Exception:
                            pass
                        needs_enrichment = p_num < 15000 or not image_url
                        if needs_enrichment:
                            try:
                                (new_p, new_img) = await _fetch_next_data_details(
                                    lnk, enrich_session
                                )
                                if new_p:
                                    try:
                                        new_p_val = int(
                                            float(str(new_p).replace("€", ""))
                                        )
                                        if new_p_val > p_num:
                                            price = new_p
                                    except Exception:
                                        if p_num == 0:
                                            price = new_p
                                if new_img and (not image_url):
                                    image_url = new_img
                            except Exception:
                                pass
                        if price == "0" or price == 0:
                            scrape_stats["invalid"] += 1
                            continue
                        html_year = None
                        html_km = None
                        html_make = None
                        html_model = None
                        nd = soup.find("script", {"id": "__NEXT_DATA__"})
                        if nd and nd.string:
                            try:
                                nd_data = json.loads(nd.string)
                                urql = (
                                    nd_data.get("props", {})
                                    .get("pageProps", {})
                                    .get("urqlState", {})
                                )
                                for _k, _v in urql.items():
                                    if "data" in _v:
                                        _d = json.loads(_v["data"])
                                        if "advertSearch" in _d:
                                            for edge in _d["advertSearch"].get(
                                                "edges", []
                                            ):
                                                node = edge.get("node", {})
                                                node_url = node.get("url", "")
                                                if node_url and node_url in lnk:
                                                    for param in node.get(
                                                        "parameters", []
                                                    ):
                                                        if param.get("key") == "year":
                                                            html_year = param.get(
                                                                "value"
                                                            )
                                                        elif (
                                                            param.get("key")
                                                            == "mileage"
                                                        ):
                                                            html_km = param.get("value")
                                                        elif param.get("key") == "make":
                                                            html_make = param.get(
                                                                "value"
                                                            )
                                                        elif (
                                                            param.get("key") == "model"
                                                        ):
                                                            html_model = param.get(
                                                                "value"
                                                            )
                                                    break
                                            break
                            except Exception:
                                pass

                        expected_make = make.lower().replace(" ", "-") if make else None
                        expected_model = model.lower() if model else None

                        if html_make and expected_make:
                            if (
                                html_make != expected_make
                                and html_make not in expected_make
                                and expected_make not in html_make
                            ):
                                scrape_stats["invalid"] += 1
                                continue
                        if html_model and expected_model:
                            html_model_lc = html_model.lower()
                            if html_model_lc != expected_model:
                                # For cases like 'e' and 'e-class'
                                if html_model_lc in expected_model.split(
                                    "-"
                                ) or expected_model in html_model_lc.split("-"):
                                    pass
                                elif html_model_lc.replace(
                                    "-", " "
                                ) == expected_model.replace("-", " "):
                                    pass
                                else:
                                    scrape_stats["invalid"] += 1
                                    continue

                        page_ads.append(
                            {
                                "title": title,
                                "price": f"{price} €",
                                "link": lnk,
                                "image": image_url,
                                "subsource": "Autovit",
                                "year": html_year,
                                "km": f"{html_km} km" if html_km else None,
                                "make": html_make or make,
                                "model": html_model or model,
                            }
                        )
                    except Exception as _parse_err:
                        dead_letter.save(
                            {
                                "link": lnk,
                                "title": title if "title" in dir() else "unknown",
                            },
                            error=str(_parse_err),
                            source="autovit_scraper_parse",
                        )
            return page_ads
        except Exception as e:
            print(f"Autovit fetch_page({page_num}) error: {e}")
            import traceback

            traceback.print_exc()
            return None

    current_p = page
    empty_pages = 0
    failed_pages = []
    _is_bucket_mode = (min_price is not None or max_price is not None) and not model
    _empty_page_limit = 10 if _is_bucket_mode else 2
    _shared_enrich = aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False, limit=10)
    )
    while len(results) < limit:
        if current_p > max_pages:
            break
        ads = await fetch_page(current_p, _shared_enrich)
        if ads == "BLOCKED":
            log.warning("Autovit blocked — stopping pagination")
            break
        if ads is None:
            failed_pages.append(current_p)
            current_p += 1
            continue
        if ads is None or len(ads) == 0:
            log.warning(
                "Autovit empty page",
                extra={"page": current_p, "consecutive_empty": empty_pages + 1},
            )
            empty_pages += 1
            if empty_pages >= _empty_page_limit:
                log.warning("Autovit stopping: too many empty pages")
                break
        else:
            empty_pages = 0
        enrich_tasks = []
        enrich_ads = []
        for ad in ads:
            if ad["link"] not in seen_links_total:
                seen_links_total.add(ad["link"])
                p_n = 0
                try:
                    p_n = int(ad["price"].replace("€", "").strip())
                except Exception:
                    pass
                if (
                    p_n < 15000
                    or not ad["image"]
                    or not ad.get("year")
                    or not ad.get("km")
                ):
                    enrich_tasks.append(
                        _fetch_next_data_details(ad["link"], _shared_enrich)
                    )
                    enrich_ads.append(ad)
                else:
                    results.append(ad)
        if enrich_tasks:
            enriched_data = await asyncio.gather(*enrich_tasks)
            for idx, e_data in enumerate(enriched_data):
                (price, image, year, km) = e_data
                if price:
                    enrich_ads[idx]["price"] = f"{price} EUR"
                if image:
                    enrich_ads[idx]["image"] = image
                if year and not enrich_ads[idx].get("year"):
                    enrich_ads[idx]["year"] = year
                if km and not enrich_ads[idx].get("km"):
                    enrich_ads[idx]["km"] = (
                        f"{km} km" if not str(km).endswith("km") else str(km)
                    )
            results.extend(enrich_ads)
        current_p += 1
        if len(results) >= limit:
            break
    if failed_pages:
        log.info(
            "Autovit retrying failed pages",
            extra={"count": len(failed_pages), "pages": failed_pages},
        )
        for p_idx in failed_pages:
            if len(results) >= limit:
                break
            await asyncio.sleep(random.uniform(2.0, 4.0))
            ads = await fetch_page(p_idx, _shared_enrich)
            if ads == "BLOCKED":
                log.warning("Autovit blocked during retry — stopping")
                break
            if ads:
                for ad in ads:
                    if ad["link"] not in seen_links_total:
                        seen_links_total.add(ad["link"])
                        results.append(ad)
    await _shared_enrich.close()
    log.info(
        "Autovit stats",
        extra={
            "found": len(results),
            "dupes": scrape_stats["dupes"],
            "invalid": scrape_stats["invalid"],
        },
    )
    return results[:limit]
