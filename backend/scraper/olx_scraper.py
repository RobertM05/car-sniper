import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
import json

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
): 

    ads = []
    current_page = page
    
    # We will use a single session for all requests
    async with aiohttp.ClientSession(
        headers={"User-Agent": "Mozilla/5.0"}, 
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        while len(ads) < limit:
            # Construct URL/Params for current page
            url = BASE_URL.format(query.replace(" ", "-"))
            params = {"page": str(current_page)}
            if min_price is not None:
                params["search[filter_float_price:from]"] = str(min_price)
            if max_price is not None:
                params["search[filter_float_price:to]"] = str(max_price)
            if min_year is not None:
                params["search[filter_float_year:from]"] = str(min_year)
            if max_year is not None:
                params["search[filter_float_year:to]"] = str(max_year)

            try:
                async with session.get(url, params=params, timeout=10) as response:
                    # response.raise_for_status() # aiohttp doesn't raise automatically unless configured
                    if response.status != 200:
                        break
                    
                    html_text = await response.text()
                
                soup = BeautifulSoup(html_text, "html.parser")
                
                # Find cards
                items = soup.find_all("div", attrs={"data-cy": "l-card"})
                if not items:
                    items = soup.select("div.css-1sw7q4x") 
                
                if not items:
                    # No more items found on this page
                    break
                    
                page_ads = []
                for item in items:
                    if len(ads) + len(page_ads) >= limit:
                        break
                        
                    # Title
                    title_tag = item.select_one("h4") or item.select_one("h6.css-16v5mdi")            
                    
                    # Price
                    price_tag = item.select_one("p[data-testid='ad-price']") or item.select_one("p.css-10b0gli")
                    
                    # Validation: Reject if it looks like a monthly rate
                    if price_tag:
                        price_text = price_tag.get_text(strip=True)
                        if "rata" in price_text.lower() or "/luna" in price_text.lower() or "/lună" in price_text.lower():
                             price_tag = None
                    
                    # Link
                    link_tag = item.select_one("a.css-1tqlkj0") or item.select_one("a")
                    
                    # Image
                    img_tag = item.select_one("img.css-8wsg1m") or item.select_one("img")

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
                                except: 
                                    pass
                            elif data_src:
                                image_src = data_src
                        
                        link_href = link_tag["href"]
                        if not link_href.startswith("http"):
                             link_href = "https://www.olx.ro" + link_href

                        is_autovit = "autovit.ro" in link_href

                        # Add to page list for parallel processing
                        page_ads.append({
                            "title": title_tag.get_text(strip=True),
                            "price": price_tag.get_text(strip=True),
                            "link": link_href,
                            "image": image_src,
                            "subsource": "Autovit" if is_autovit else "OLX"
                        })

                # Process image/price fallbacks in parallel for this request using asyncio.gather
                async def enrich_ad_data_async(ad_item):
                    # Check 1: Image needs fixing?
                    needs_img = not ad_item["image"] or "no_thumbnail" in ad_item["image"] or "/app/static" in ad_item["image"]
                    
                    # Check 2: Price needs fixing? (0 EUR or likely monthly rate)
                    try:
                        p_val = int(re.sub(r"\D", "", ad_item["price"]))
                        # Fix if price is 0 OR (small price on autovit link = monthly rate)
                        needs_price = p_val == 0 or (p_val < 20000 and "autovit" in ad_item["link"])
                    except:
                        needs_price = True 
                    
                    if not needs_img and not needs_price:
                        return None, None
                        
                    new_img = None
                    new_price = None
                    
                    try:
                        async with session.get(ad_item["link"], timeout=5) as r_det:
                            if r_det.status == 200:
                                t_det = await r_det.text()
                                s = BeautifulSoup(t_det, "html.parser")
                                
                                # --- Image Fix ---
                                if needs_img:
                                    og = s.find("meta", attrs={"property": "og:image"})
                                    if og and og.get("content"):
                                        new_img = og.get("content")
                                    elif not new_img:
                                        gal = s.find("img", {"class": "css-1bmvjcs"})
                                        if gal:
                                            new_img = gal.get("src")
                                
                                # --- Price Fix ---
                                if needs_price:
                                    nd = s.find("script", {"id": "__NEXT_DATA__"})
                                    if nd and nd.string:
                                        data = json.loads(nd.string)
                                        pp = data.get("props", {}).get("pageProps", {})
                                        advert = pp.get("advert") or pp.get("data", {}).get("advert")
                                        if advert:
                                            val = advert.get("price", {}).get("value")
                                            if val:
                                                new_price = f"{int(val)} €"
                    except:
                        pass
                    
                    return new_img, new_price

                # Run parallel enrichment
                if page_ads:
                    enrich_tasks = [enrich_ad_data_async(ad) for ad in page_ads]
                    results_enrich = await asyncio.gather(*enrich_tasks)
                    
                    for i, (res_img, res_price) in enumerate(results_enrich):
                        if res_img:
                            page_ads[i]["image"] = res_img
                        if res_price:
                            page_ads[i]["price"] = res_price
                
                ads.extend(page_ads)
                
                # Next page
                current_page += 1
                
            except Exception as e:
                print(f"Error scraping OLX page {current_page}: {e}")
                break

    return ads
