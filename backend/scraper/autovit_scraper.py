import aiohttp
import asyncio
import re
import json
from bs4 import BeautifulSoup

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
):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0 Safari/537.36"
        )
    }

    results: list[dict] = []
    seen_links_total: set[str] = set()

    async with aiohttp.ClientSession(
        headers=headers,
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        
        async def _fetch_next_data_details(url: str) -> tuple[str | None, str | None]:
            # Returns (price, image_url)
            try:
                async with session.get(url, timeout=5) as r:
                    if r.status != 200: return None, None
                    text = await r.text()
                    s = BeautifulSoup(text, "html.parser")
                    
                    price = None
                    image = None
                    
                    # 1. Try NEXT_DATA
                    nd = s.find("script", {"id": "__NEXT_DATA__"})
                    if nd and nd.string:
                        data = json.loads(nd.string)
                        pp = data.get("props", {}).get("pageProps", {})
                        advert = pp.get("advert") or pp.get("data", {}).get("advert")
                        if advert:
                            # Price
                            p_val = advert.get("price", {}).get("value")
                            if p_val:
                                price = str(int(p_val))
                                
                            # Image
                            photos = advert.get("photos") or advert.get("images")
                            if photos and isinstance(photos, list) and len(photos) > 0:
                                first_photo = photos[0]
                                if isinstance(first_photo, dict):
                                    image = first_photo.get("large") or first_photo.get("medium") or first_photo.get("src")
                                elif isinstance(first_photo, str):
                                    image = first_photo
                    
                    # 2. Try JSON-LD fallback
                    if not price:
                        jld = s.find("script", {"id": "listing-json-ld"})
                        if jld and jld.string:
                            data = json.loads(jld.string)
                            offers = data.get("offers", {})
                            if offers:
                                p = offers.get("price")
                                if p: price = str(int(float(p)))
                    
                    # 3. Try OG Image fallback
                    if not image:
                        og = s.find("meta", attrs={"property": "og:image"})
                        if og and og.get("content"):
                            image = og.get("content")
                            
                    return price, image
                        
            except Exception:
                pass
            return None, None

        async def _scrape_pass(use_filters: bool):
            current_page = page
            while len(results) < limit and current_page <= max_pages:
                params = {"page": str(current_page)}
                if use_filters and max_price is not None:
                    params["search[filter_float_price:to]"] = str(max_price)
                if use_filters and min_year is not None:
                    params["search[filter_float_year:from]"] = str(min_year)
                if use_filters and max_km is not None:
                    params["search[filter_float_mileage:to]"] = str(max_km)

                url = BASE_URL.format(make.lower(), model.lower())
                try:
                    async with session.get(url, params=params, timeout=10) as response:
                        # response.raise_for_status() 
                        if response.status != 200:
                            break
                        html = await response.text()
                except Exception:
                    break

                soup = BeautifulSoup(html, "html.parser")

                # Collect detail links
                detail_links = []
                # (Same logic as sync: find links ending in .html)
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "/autoturisme/anunt/" in href and href.endswith(".html"):
                        if href.startswith("/"):
                            href = "https://www.autovit.ro" + href
                        detail_links.append(href)

                # 1) JSON-LD on current page
                try:
                    script = soup.find("script", {"id": "listing-json-ld", "type": "application/ld+json"})
                    if script and script.string:
                        data = json.loads(script.string)
                        items = data.get("mainEntity", {}).get("itemListElement", [])
                        for idx, elem in enumerate(items):
                            if len(results) >= limit: break
                            price_spec = elem.get("priceSpecification", {})
                            price = price_spec.get("price")
                            car = elem.get("itemOffered", {})
                            name = car.get("name")
                            if not name or price is None:
                                continue
                            
                            link = (car.get("url") or elem.get("url") or (detail_links[idx] if idx < len(detail_links) else url))
                            if link and link.startswith("/"): link = "https://www.autovit.ro" + link
                            if link in seen_links_total: continue
                            
                            seen_links_total.add(link)
                            image_url = car.get("image")
                            if isinstance(image_url, list) and len(image_url) > 0:
                                image_url = image_url[0]

                            try:
                                price = int(float(price))
                            except: pass

                            results.append({
                                "title": str(name),
                                "price": f"{price} €",
                                "link": link,
                                "image": image_url,
                                "subsource": "Autovit"
                            })
                except Exception:
                    pass

                # 2) HTML fallback
                if len(results) < limit:
                    articles = soup.find_all("article")
                    for art in articles:
                        if len(results) >= limit: break
                        try:
                            if not art.has_attr("data-id"): continue
                            a_tag = art.find("a", href=True)
                            if not a_tag: continue
                            link = a_tag["href"]
                            if "/anunt/" not in link: continue
                            if link.startswith("/"): link = "https://www.autovit.ro" + link
                            if link in seen_links_total: continue

                            h2 = art.find("h2") or art.find("h1")
                            title = h2.get_text(strip=True) if h2 else "No Title"

                            price = "0"
                            price_span = art.find(string=re.compile(r"EUR"))
                            if price_span:
                                parent = price_span.parent.parent if price_span.parent else None
                                if parent:
                                    h3 = parent.find("h3")
                                    if h3:
                                        raw_p = h3.get_text(strip=True)
                                        clean_p = raw_p.replace(" ", "")
                                        if "," in clean_p:
                                            clean_p = clean_p.replace(".", "").replace(",", ".")
                                        else:
                                            clean_p = clean_p.replace(".", "")
                                        try:
                                            price = str(int(float(clean_p)))
                                        except: pass

                            img = art.find("img")
                            image_url = img.get("src") if img else None

                            # Async Fallback
                            p_num = 0
                            try: p_num = int(float(str(price).replace("€", "").strip()))
                            except: pass

                            # Deep fetch if:
                            # 1. Price is 0 or invalid
                            # 2. Image is missing
                            # 3. Price is too low (e.g. 9000 vs 90000) - Likely monthly rate or parsing error
                            needs_enrichment = (p_num < 15000) or (not image_url)
                            
                            if needs_enrichment:
                                try:
                                    new_p, new_img = await _fetch_next_data_details(link)
                                    if new_p:
                                        try:
                                            new_p_val = int(float(str(new_p).replace("€", "")))
                                            # Update only if new price is better (higher) or we had 0
                                            if new_p_val > p_num:
                                                price = new_p
                                        except: 
                                            # Fallback: just take logic
                                            if p_num == 0: price = new_p
                                    
                                    if new_img and not image_url:
                                        image_url = new_img
                                except: pass

                            if price == "0" or price == 0: continue

                            seen_links_total.add(link)
                            results.append({
                                "title": title,
                                "price": f"{price} €",
                                "link": link,
                                "image": image_url,
                                "subsource": "Autovit"
                            })
                        except: pass

                current_page += 1

        # Pass 1
        await _scrape_pass(use_filters=True)
        # Fallback
        if len(results) < max(10, limit // 2) and (max_price is not None or min_year is not None or max_km is not None):
            await _scrape_pass(use_filters=False)

    return results[:limit]
