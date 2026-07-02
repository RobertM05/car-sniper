import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
import json
from logger import get_logger
from metrics import metrics
from dead_letter import dead_letter

log = get_logger("olx_scraper")

BASE_URL = "https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/q-{}/"


async def scrape_olx(
    query: str,
    page: int = 1,
    limit: int = 100,
    *,
    min_price: int | None = None,
    max_price: int | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    max_km: int | None = None,
    sort_order: str = "price_asc",
    make: str | None = None,
    model_slug: str | None = None,
    max_pages: int = 15,
    require_photos: bool = True,
):
    ads = []
    seen_links = set()
    current_page = page
    page_errors = 0
    async with aiohttp.ClientSession(
        headers={"User-Agent": "Mozilla/5.0"}, connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        empty_pages = 0
        stale_pages = 0
        while len(ads) < limit and current_page <= max_pages:
            path = "autoturisme"
            params = {
                "page": str(current_page),
                "currency": "EUR",
            }
            if make and model_slug:
                make_formatted = make.lower().replace(" ", "-")
                url = f"https://www.olx.ro/auto-masini-moto-ambarcatiuni/{path}/{make_formatted}/"
                params["search[filter_enum_model][0]"] = model_slug
            elif query:
                url = f"https://www.olx.ro/auto-masini-moto-ambarcatiuni/{path}/q-{query.lower().replace(' ', '-')}/"
            else:
                url = f"https://www.olx.ro/auto-masini-moto-ambarcatiuni/{path}/"
            if require_photos:
                params["search[photos]"] = "1"
            if sort_order == "price_asc":
                params["search[order]"] = "filter_float_price:asc"
            elif sort_order == "price_desc":
                params["search[order]"] = "filter_float_price:desc"
            elif sort_order == "newest":
                params["search[order]"] = "created_at:desc"
            if min_price is not None:
                params["search[filter_float_price:from]"] = str(min_price)
            if max_price is not None:
                params["search[filter_float_price:to]"] = str(max_price)
            if min_year is not None:
                params["search[filter_float_year:from]"] = str(min_year)
            if max_year is not None:
                params["search[filter_float_year:to]"] = str(max_year)
            try:
                log.debug("OLX request", extra={"url": url, "params": dict(params)})
                async with session.get(url, params=params, timeout=20) as response:
                    log.debug("OLX response", extra={"status": response.status})
                    if response.status != 200:
                        page_errors += 1
                        if page_errors >= 3:
                            break
                        await asyncio.sleep(2)
                        continue
                    html_text = await response.text()
                soup = BeautifulSoup(html_text, "html.parser")
                items = soup.find_all("div", attrs={"data-cy": "l-card"})
                if not items:
                    items = soup.select("div.css-1sw7q4x")
                if not items:
                    empty_pages += 1
                    if empty_pages >= 2:
                        log.warning("OLX stopping: too many empty pages")
                        break
                else:
                    empty_pages = 0
                page_ads = []
                for item in items:
                    if len(ads) + len(page_ads) >= limit:
                        break
                    title_tag = item.select_one("h4") or item.select_one(
                        "h6.css-16v5mdi"
                    )
                    price_tag = item.select_one(
                        "p[data-testid='ad-price']"
                    ) or item.select_one("p.css-10b0gli")
                    if price_tag:
                        price_text = price_tag.get_text(strip=True)
                        if (
                            "rata" in price_text.lower()
                            or "/luna" in price_text.lower()
                            or "/lună" in price_text.lower()
                        ):
                            price_tag = None
                    link_tag = item.select_one("a.css-1tqlkj0") or item.select_one("a")
                    img_tag = item.select_one("img.css-8wsg1m") or item.select_one(
                        "img"
                    )
                    if title_tag and price_tag and link_tag:
                        image_src = None
                        if img_tag:
                            image_src = img_tag.get("src")
                            srcset = img_tag.get("srcset")
                            data_src = img_tag.get("data-src")
                            if srcset:
                                try:
                                    candidates = srcset.split(",")
                                    best_candidate = candidates[-1].strip()
                                    image_src = best_candidate.split(" ")[0]
                                except Exception:
                                    pass
                            elif data_src:
                                image_src = data_src
                        link_href = link_tag["href"]
                        if not link_href.startswith("http"):
                            link_href = "https://www.olx.ro" + link_href
                        if link_href in seen_links:
                            continue
                        if "reason=extended_search_no_results" in link_href:
                            continue
                        seen_links.add(link_href)
                        is_autovit = "autovit.ro" in link_href
                        car_year = None
                        car_km = None
                        spans = item.find_all("span")
                        for sp in spans:
                            t = sp.get_text(strip=True)
                            if "km" in t.lower() and len(t) > 6:
                                m = re.search(
                                    "(\\d{4})\\s*-\\s*([\\d\\s]+)\\s*km",
                                    t,
                                    re.IGNORECASE,
                                )
                                if not m:
                                    m = re.search(
                                        "(\\d{4})\\s+([\\d\\s]+)\\s*km",
                                        t,
                                        re.IGNORECASE,
                                    )
                                if m:
                                    car_year = m.group(1)
                                    car_km = m.group(2).replace(" ", "") + " km"
                                    break
                        title_text = title_tag.get_text(strip=True)
                        # Extract model: strip known brand prefix from title
                        olx_make = make or query
                        olx_model = None
                        if olx_make and title_text.lower().startswith(olx_make.lower()):
                            remainder = title_text[len(olx_make) :].strip()
                            # Take everything before the first year-like number or engine spec
                            olx_model = remainder.split()[0] if remainder else None
                            # Try to get multi-word model (e.g., "Seria 3")
                            parts = remainder.split()
                            if len(parts) >= 2 and parts[1].isdigit():
                                olx_model = f"{parts[0]} {parts[1]}"
                        page_ads.append(
                            {
                                "title": title_text,
                                "price": price_tag.get_text(strip=True),
                                "link": link_href,
                                "image": image_src,
                                "subsource": "Autovit" if is_autovit else "OLX",
                                "year": car_year,
                                "km": car_km,
                                "make": olx_make,
                                "model": olx_model,
                            }
                        )

                async def enrich_ad_data_async(ad_item):
                    needs_img = (
                        not ad_item["image"]
                        or "no_thumbnail" in ad_item["image"]
                        or "/app/static" in ad_item["image"]
                    )
                    try:
                        p_val = int(re.sub("\\D", "", ad_item["price"]))
                        needs_price = p_val == 0 or (
                            p_val < 20000 and "autovit" in ad_item["link"]
                        )
                    except Exception:
                        needs_price = True
                    if not needs_img and (not needs_price):
                        return (None, None)
                    new_img = None
                    new_price = None
                    try:
                        async with session.get(ad_item["link"], timeout=15) as r_det:
                            if r_det.status == 200:
                                t_det = await r_det.text()
                                s = BeautifulSoup(t_det, "html.parser")
                                if needs_img:
                                    og = s.find("meta", attrs={"property": "og:image"})
                                    if og and og.get("content"):
                                        new_img = og.get("content")
                                    elif not new_img:
                                        gal = s.find("img", {"class": "css-1bmvjcs"})
                                        if gal:
                                            new_img = gal.get("src")
                                if needs_price:
                                    nd = s.find("script", {"id": "__NEXT_DATA__"})
                                    if nd and nd.string:
                                        data = json.loads(nd.string)
                                        pp = data.get("props", {}).get("pageProps", {})
                                        advert = pp.get("advert") or pp.get(
                                            "data", {}
                                        ).get("advert")
                                        if advert:
                                            val = advert.get("price", {}).get("value")
                                            if val:
                                                new_price = f"{int(val)} €"
                    except Exception as _enrich_err:
                        dead_letter.save(
                            ad_item, error=str(_enrich_err), source="olx_scraper_enrich"
                        )
                    return (new_img, new_price)

                if page_ads:
                    enrich_tasks = [enrich_ad_data_async(ad) for ad in page_ads]
                    results_enrich = await asyncio.gather(*enrich_tasks)
                    for i, (res_img, res_price) in enumerate(results_enrich):
                        if res_img:
                            page_ads[i]["image"] = res_img
                        if res_price:
                            page_ads[i]["price"] = res_price
                ads_before = len(ads)
                ads.extend(page_ads)
                if len(ads) == ads_before:
                    stale_pages += 1
                    if stale_pages >= 2:
                        log.warning("OLX stopping: no new unique ads for 2 pages")
                        break
                else:
                    stale_pages = 0
                if len(page_ads) == 0:
                    break
                current_page += 1
            except Exception as e:
                import traceback

                page_errors += 1
                log.error(
                    "OLX page error",
                    extra={
                        "page": current_page,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                        "error_count": page_errors,
                    },
                )
                metrics.increment("errors")
                if page_errors >= 3:
                    log.error("OLX stopping: too many page errors")
                    break
                await asyncio.sleep(2 * page_errors)  # backoff
                continue
    return ads
