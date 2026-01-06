from scraper.olx_scraper import scrape_olx
from scraper.autovit_scraper import scrape_autovit
from car_database import get_optimized_search_params, car_db_optimizer
import re
import time
import functools
import json
import asyncio

# --- Simple TTL Cache for Async ---
_SEARCH_CACHE = {}
_CACHE_TTL = 600  # 10 minutes

def ttl_cache(func):
    """Cache function results for a specific duration (Async support)."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Create a cache key from arguments
        key_parts = list(args)
        for k in sorted(kwargs.keys()):
            key_parts.append((k, kwargs[k]))
        
        # Make key hashable
        key = str(tuple(key_parts))
        
        current_time = time.time()
        
        # Check cache
        if key in _SEARCH_CACHE:
            timestamp, result = _SEARCH_CACHE[key]
            if current_time - timestamp < _CACHE_TTL:
                return result
            else:
                del _SEARCH_CACHE[key] # Expired
        
        # Execute
        result = await func(*args, **kwargs)
        
        # Store
        _SEARCH_CACHE[key] = (current_time, result)
        return result
    return wrapper

@ttl_cache
async def search_cars(
    make: str,
    model: str,
    generation: str | None = None,
    site: str = "olx",
    *,
    min_price: int | None = None,
    max_price: int,
    min_km: int | None = None,
    max_km: int | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    min_cc: int | None = None,
    min_hp: int | None = None,
    limit: int = 100,
    max_pages: int = 5,
):
    # Calculate pages based on limit
    if limit > 50:
        calculated_pages = (limit // 30) + 2
        max_pages = max(max_pages, calculated_pages)
        
    cars = []

    optimized_params = get_optimized_search_params(make, model, min_year, max_year)
    optimized_min_year = optimized_params['min_year']
    optimized_max_year = optimized_params['max_year']
    # model_info = optimized_params['model_info']
    
    normalized_model = optimized_params['normalized_model']
    query = f"{make} {normalized_model}"
    if generation:
        query += f" {generation}"

    def map_autovit_model(make_text: str, model_text: str) -> str:
        make_lc = (make_text or "").strip().lower()
        model_lc = (model_text or "").strip().lower()

        m = re.match(r"^(x)?(\d)", model_lc)
        if make_lc == "bmw" and m:
            is_x = m.group(1) == "x"
            digit = m.group(2)
            if is_x:
                return f"x{digit}"
            return f"seria-{digit}"
        return model_lc

    site_lc = (site or "").lower()
    
    # Define Tasks
    tasks = []
    
    if site_lc in ["olx", "both"]:
        tasks.append(scrape_olx(
            query,
            limit=limit,
            max_price=max_price,
            min_price=min_price,
            min_year=optimized_min_year,
            max_year=optimized_max_year,
            max_km=max_km,
        ))
        
    if site_lc in ["autovit", "both"]:
        model_for_autovit = map_autovit_model(make, model)
        tasks.append(scrape_autovit(
            make,
            model_for_autovit,
            limit=limit,
            max_pages=max_pages,
            max_price=max_price,
            min_price=min_price,
            min_year=optimized_min_year,
            max_year=optimized_max_year,
            max_km=max_km,
        ))

    # Run concurrently
    results_list = await asyncio.gather(*tasks, return_exceptions=True)
    
    for res in results_list:
        if isinstance(res, list):
            cars.extend(res)
        else:
            print(f"Scraper error: {res}")

    # Filter cars
    strict_filtered = []
    loose_filtered = []
    for car in cars:
        # price is required
        try:
            raw_price = str(car.get("price", ""))
            price_val = int(re.sub(r"\D", "", raw_price))
            
            # Currency conversion
            if "ron" in raw_price.lower() or "lei" in raw_price.lower():
                price_val = int(price_val / 5)
            
            price = price_val
        except ValueError:
            continue

        def normalize_tokens(text: str) -> set[str]:
            return set(t for t in re.split(r"[^a-z0-9]", (text or "").lower()) if t)

        def normalize(text: str) -> str:
            return re.sub(r"[^a-z0-9]+", "", (text or "").lower())

        title_norm = normalize(str(car.get("title") or car.get("name") or ""))
        link_norm = normalize(str(car.get("link") or car.get("url") or ""))
        make_norm = normalize(make or "")
        model_norm = normalize(model or "")

        title_tokens = normalize_tokens(str(car.get("title") or car.get("name") or ""))
        link_tokens = normalize_tokens(str(car.get("link") or car.get("url") or ""))
        
        searchable_tokens = title_tokens | link_tokens
        make_tokens = normalize_tokens(make or "")
        model_tokens = normalize_tokens(model or "")

        # Make check
        if make_tokens and not make_tokens.issubset(searchable_tokens):
             continue

        # Model check
        model_matches = True
        if model_tokens:
            for m_tok in model_tokens:
                token_found = False
                for s_tok in searchable_tokens:
                    if m_tok == s_tok or (len(m_tok) > 1 and m_tok in s_tok): 
                        token_found = True
                        break
                if not token_found:
                    model_matches = False
                    break

        bad_keywords = {"dezmembrari", "piese", "motor", "cutie", "bara", "usa", "capota", "far", "stop", "anvelope", "roti", "jante", "boxe", "navigatie", "volan", "interior"}
        if any(bad in title_tokens or bad in link_tokens for bad in bad_keywords):
            continue
        
        # Validations
        km_val = None
        try:
            km_raw = re.sub(r"\D", "", str(car.get("km", "")))
            km_val = int(km_raw) if km_raw else None
        except: pass
        
        year_val = None
        try:
            year_raw = re.sub(r"\D", "", str(car.get("year", "")))
            year_val = int(year_raw) if year_raw else None
        except: pass
        
        cc_val = None
        try:
            cc_raw = re.sub(r"\D", "", str(car.get("cc", "")))
            cc_val = int(cc_raw) if cc_raw else None
        except: pass
        
        hp_val = None
        try:
            hp_raw = re.sub(r"\D", "", str(car.get("hp", "")))
            hp_val = int(hp_raw) if hp_raw else None
        except: pass

        if price > max_price: continue
        if min_price is not None and price < min_price: continue
        if max_km is not None and km_val is not None and km_val > max_km: continue
        if optimized_min_year is not None and year_val is not None and year_val < optimized_min_year: continue
        if optimized_max_year is not None and year_val is not None and year_val > optimized_max_year: continue
        if min_cc is not None and cc_val is not None and cc_val < min_cc: continue
        if min_hp is not None and hp_val is not None and hp_val < min_hp: continue

        car["price"] = price
        if model_matches:
            strict_filtered.append(car)
        else:
            # Fallback logic (BMW X, Audi Q, Mercedes Classes etc)
            make_is_bmw = (make_norm == "bmw")
            model_is_x = model_norm.startswith("x") if model_norm else False
            contains_x_series = any(x in title_norm or x in link_norm for x in ["x1","x2","x3","x4","x5","x6","x7"]) if (title_norm or link_norm) else False
            if make_is_bmw and not model_is_x and contains_x_series: continue
            
            if make_is_bmw and not model_is_x and model_norm:
                import re as _re
                m_num = _re.match(r"(\d{3})", model_norm)
                model_num = m_num.group(1) if m_num else ""
                m_series = _re.match(r"(\d)", model_norm)
                series_digit = m_series.group(1) if m_series else ""
                allowed = False
                if model_num and (model_num in title_norm or model_num in link_norm or (model_num + "d") in title_norm): allowed = True
                if series_digit:
                    series_tokens = [f"seria{series_digit}", f"serie{series_digit}", f"{series_digit}series", f"series{series_digit}"]
                    if any(tok in title_norm or tok in link_norm for tok in series_tokens): allowed = True
                if not allowed: continue

            make_is_audi = (make_norm == "audi")
            model_is_q = model_norm.startswith("q") if model_norm else False
            contains_q_series = any(q in title_norm or q in link_norm for q in ["q2","q3","q4","q5","q7","q8"]) if (title_norm or link_norm) else False
            if make_is_audi and not model_is_q and contains_q_series: continue
            if make_is_audi and not model_is_q and model_norm:
                import re as _re2
                m2 = _re2.match(r"([a-z])(\d)", model_norm)
                if m2:
                    series_token = f"{m2.group(1)}{m2.group(2)}"
                    if series_token.startswith("a"):
                        if not ((series_token in title_norm) or (series_token in link_norm)): continue

            make_is_mercedes = make_norm in ("mercedes", "mercedesbenz", "mercedesbenz")
            import re as _re3
            mer_class_match = _re3.match(r"([a-z])", model_norm or "")
            requested_class = mer_class_match.group(1) if mer_class_match else ""
            is_g_requested = requested_class == "g"
            contains_g_suv = any(tok in title_norm or tok in link_norm for tok in ["gla","glb","glc","gle","gls","g55","g63","g500","g350"]) if (title_norm or link_norm) else False
            if make_is_mercedes and not is_g_requested and contains_g_suv: continue
            if make_is_mercedes and requested_class in ("c","e","s"):
                class_tokens = [f"clasa{requested_class}", f"{requested_class}class"]
                if not any(tok in title_norm or tok in link_norm for tok in class_tokens): continue
                
            loose_filtered.append(car)

    final_results = strict_filtered if strict_filtered else (loose_filtered if model else [])

    # Enhanced Validation & Repair Logic
    # Scans results for missing data (images/price) and triggers deep-fetch to correct them.
    
    ads_to_repair = []
    
    import aiohttp
    from bs4 import BeautifulSoup
    import json as _json_live

    async def repair_ad(ad):
        # 1. Image Check: Attempt to recover missing images via multiple sources
        # 2. Price Check: Validate price against page data if image is missing
        
        is_missing_image = not ad.get("image") or "no_thumbnail" in str(ad.get("image"))
        
        is_missing_image = not ad.get("image") or "no_thumbnail" in str(ad.get("image"))
        
        if is_missing_image:
             try:
                 async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as sess:
                     async with sess.get(ad.get("link"), timeout=5) as r: # Short timeout for live search
                         # Ghost check
                         if r.status == 404 or len(str(r.url)) < 30:
                             return None # Signal to remove
                             
                         if r.status == 200:
                             html = await r.text()
                             soup = BeautifulSoup(html, "html.parser")
                             
                             # Fix Price
                             nd = soup.find("script", {"id": "__NEXT_DATA__"})
                             current_price = int(ad.get("price", 0))
                             if nd and nd.string:
                                 d = _json_live.loads(nd.string)
                                 pp = d.get("props", {}).get("pageProps", {})
                                 adv = pp.get("advert") or pp.get("data", {}).get("advert")
                                 if adv:
                                     p = adv.get("price", {}).get("value")
                                     if p:
                                         new_p = int(p)
                                         if new_p > current_price: 
                                             ad["price"] = new_p

                             # Fix Image
                             if is_missing_image:
                                 # Priority 1: Open Graph (Best Quality)
                                 og = soup.find("meta", attrs={"property": "og:image"})
                                 if og and og.get("content"):
                                     ad["image"] = og.get("content")
                                 
                                 # Priority 2: JSON-LD (Schema.org)
                                 if not ad.get("image"):
                                     scripts = soup.find_all('script', type='application/ld+json')
                                     for s in scripts:
                                        try:
                                            data = _json_live.loads(s.string)
                                            if isinstance(data, dict) and 'image' in data:
                                                imgs = data['image']
                                                if isinstance(imgs, list) and imgs:
                                                    ad["image"] = imgs[0]
                                                elif isinstance(imgs, str):
                                                    ad["image"] = imgs
                                                break
                                        except: pass

                                 # Priority 3: Common Gallery Selectors
                                 if not ad.get("image"):
                                     # Try finding gallery image
                                     selectors = [
                                         "img.css-1bmvjcs", # OLX Legacy
                                         "div.swiper-zoom-container img", # OLX Mobile/New
                                         "div.css-1bnh990 img", # Autovit Desktop
                                         "img.photo-handler", # Generic Autovit
                                         ".image-gallery-slide img" # React Gallery
                                     ]
                                     for sel in selectors:
                                         gal = soup.select_one(sel)
                                         if gal:
                                             src = gal.get("src") or gal.get("data-src")
                                             if src:
                                                  ad["image"] = src
                                                  break
             except:
                 pass
        
        # Final Quality Check
        if not ad.get("image") or "no_thumbnail" in str(ad.get("image")):
            return None # Still broken -> Remove
            
        return ad

    # Collect tasks
    repair_tasks = []
    for ad in final_results:
        repair_tasks.append(repair_ad(ad))
        
    if repair_tasks:
        # Run repairs concurrently
        repaired_results = await asyncio.gather(*repair_tasks)
        # Filter out Nones (Removed ads)
        final_results = [r for r in repaired_results if r]

    # Deduplicate by Ad ID
    unique_map = {}
    unique_list = []
    
    import re as _re_dedup
    def get_ad_id(link_str):
        m = _re_dedup.search(r"-ID([a-zA-Z0-9]+)\.html", link_str)
        if m: return m.group(1)
        return link_str

    for c in final_results:
        lnk = c.get("link")
        if lnk:
            ad_id = get_ad_id(lnk)
            if ad_id not in unique_map:
                unique_map[ad_id] = True
                unique_list.append(c)
    
    final_results = unique_list
    
    # Stats update
    if final_results and make and model:
        prices = [r['price'] for r in final_results if r.get('price')]
        years = [r['year'] for r in final_results if r.get('year')]
        kms = [int(re.sub(r"\D", "", str(r.get('km', '')))) for r in final_results if r.get('km')]

        avg_price = sum(prices) / len(prices) if prices else None
        avg_year = sum(years) / len(years) if years else None
        avg_km = sum(kms) / len(kms) if kms else None
        
        car_db_optimizer.update_search_stats(
            make=make,
            model=model,
            avg_price=avg_price,
            avg_year=avg_year,
            avg_km=avg_km
        )

    return final_results

def add_alert(user_email: str, make: str, model: str, max_price: int):
    return car_db_optimizer.add_alert(user_email, make, model, max_price)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email_notification(to_email: str, car_list: list, search_details: str):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        return

    subject = f"Car Sniper: {len(car_list)} mașini regăsite pentru {search_details}"
    html_content = f"<h2>Salut! Am găsit {len(car_list)} mașini pentru căutarea ta ({search_details}):</h2><br>"
    for car in car_list:
        html_content += f"""
        <div style="border:1px solid #ddd; padding:10px; margin-bottom:10px; border-radius:5px;">
            <h3><a href='{car.get('link') or car.get('url')}'>{car.get('title')}</a></h3>
            <p><strong>Preț: {car.get('price')}</strong> | An: {car.get('year') or '?'} | Km: {car.get('km') or '?'}</p>
        </div>
        """
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email trimis cu succes către {to_email}")
    except Exception as e:
        print(f"❌ Eroare la trimiterea emailului: {e}")

async def check_alerts():
    alerts = car_db_optimizer.get_alerts()
    print(f"[Scheduler] Verific {len(alerts)} alerte...")
    
    for alert in alerts:
        try:
            results = await search_cars(
                make=alert["make"], 
                model=alert["model"], 
                max_price=alert["max_price"],
                site="both", 
                limit=10 
            )
            
            if results:
                print(f"ALERT MATCH for {alert['user_email']}: Found {len(results)} cars.")
                send_email_notification(
                    alert['user_email'], 
                    results, 
                    f"{alert['make']} {alert['model']}"
                )
        except Exception as e:
            print(f"Eroare la verificarea alertei {alert['id']}: {e}")