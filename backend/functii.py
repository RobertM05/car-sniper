from scraper.olx_scraper import scrape_olx
from scraper.autovit_scraper import scrape_autovit
from car_database import get_optimized_search_params, car_db_optimizer
import re
import time
import functools
import json
import asyncio
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)
_SEARCH_CACHE = {}
_CACHE_TTL = 600

def ttl_cache(func):

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        key_parts = list(args)
        for k in sorted(kwargs.keys()):
            key_parts.append((k, kwargs[k]))
        key = str(tuple(key_parts))
        current_time = time.time()
        if key in _SEARCH_CACHE:
            (timestamp, result) = _SEARCH_CACHE[key]
            if current_time - timestamp < _CACHE_TTL:
                return result
            else:
                del _SEARCH_CACHE[key]
        result = await func(*args, **kwargs)
        _SEARCH_CACHE[key] = (current_time, result)
        return result
    return wrapper

@ttl_cache
async def search_cars(make: str, model: str, site: str='olx', sort: str='price_asc', *, min_price: int | None=None, max_price: int, min_km: int | None=None, max_km: int | None=None, min_year: int | None=None, max_year: int | None=None, min_cc: int | None=None, min_hp: int | None=None, limit: int=100, max_pages: int=5):
    if limit > 50:
        calculated_pages = limit // 30 + 2
        max_pages = max(max_pages, calculated_pages)
    cars = []
    optimized_params = get_optimized_search_params(make, model, min_year, max_year)
    optimized_min_year = optimized_params['min_year']
    optimized_max_year = optimized_params['max_year']
    normalized_model = optimized_params['normalized_model']
    search_model = normalized_model
    if 'mercedes' in make.lower():
        if 'class' in normalized_model.lower() or 'clasa' in normalized_model.lower():
            letter = re.search('([a-zA-Z])[- ]?([cC]las)', normalized_model)
            if not letter:
                letter = re.search('([cC]las)[a-z]*[- ]?([a-zA-Z])', normalized_model)
                if letter:
                    search_model = letter.group(2)
            else:
                search_model = letter.group(1)
        query = f'{search_model}'
    else:
        query = f'{make} {search_model}'

    def map_autovit_model(make_text: str, model_text: str) -> str:
        make_lc = (make_text or '').strip().lower()
        model_lc = (model_text or '').strip().lower()
        m = re.match('^(x)?(\\d)', model_lc)
        if make_lc == 'bmw' and m:
            is_x = m.group(1) == 'x'
            digit = m.group(2)
            if is_x:
                return f'x{digit}'
            return f'seria-{digit}'
        if 'mercedes' in make_lc:
            if 'class' in model_lc or 'clasa' in model_lc:
                letter_match = re.search('([a-z])-?clas(?:s|a)', model_lc)
                if not letter_match:
                    letter_match = re.search('clas(?:s|a)\\s+([a-z])', model_lc)
                if letter_match:
                    return f'clasa-{letter_match.group(1)}'
            pass
        return model_lc
    site_lc = (site or '').lower()

    def get_olx_model_slug(make_text: str, model_text: str) -> str | None:
        make_lc = (make_text or '').strip().lower()
        model_lc = (model_text or '').strip().lower()
        if 'mercedes' in make_lc:
            if 'class' in model_lc or 'clasa' in model_lc:
                return None
            if model_lc in ['glc', 'gle', 'gls', 'gla', 'glb', 'cla', 'cls']:
                return model_lc
        if make_lc == 'bmw':
            m = re.match('seria[- ]?(\\d)', model_lc)
            if m:
                return f'seria-{m.group(1)}'
            m = re.match('x(\\d)', model_lc)
            if m:
                return f'x{m.group(1)}'
        if make_lc == 'audi':
            m = re.match('([aq])[\\- ]?(\\d+)', model_lc)
            if m:
                return f'{m.group(1)}{m.group(2)}'
        if make_lc in ['volkswagen', 'vw']:
            return None
        if make_lc == 'ford':
            ford_models = {'focus', 'fiesta', 'mondeo', 'kuga', 'puma', 'mustang', 'ranger', 'transit', 'ecosport', 's-max', 'c-max', 'galaxy'}
            if model_lc in ford_models:
                return model_lc
            if model_lc == 'f-150' or model_lc == 'f 150':
                return 'f150'
        if make_lc == 'opel':
            opel_models = {'astra', 'corsa', 'insignia', 'mokka', 'crossland', 'grandland', 'zafira', 'meriva', 'vectra', 'adam'}
            if model_lc in opel_models:
                return model_lc
        if make_lc in ['skoda', 'škoda']:
            skoda_models = {'octavia', 'fabia', 'superb', 'kodiaq', 'karoq', 'kamiq', 'scala', 'rapid', 'yeti', 'roomster', 'enyaq'}
            if model_lc in skoda_models:
                return model_lc
        if make_lc == 'toyota':
            toyota_models = {'corolla', 'yaris', 'rav4', 'camry', 'chr', 'aygo', 'land-cruiser', 'hilux', 'auris', 'avensis', 'prius', 'supra'}
            if model_lc in toyota_models or model_lc.replace('-', '') in [m.replace('-', '') for m in toyota_models]:
                return model_lc.replace(' ', '-')
        if make_lc == 'dacia':
            dacia_models = {'logan', 'sandero', 'duster', 'spring', 'jogger', 'dokker', 'lodgy'}
            if model_lc in dacia_models:
                return model_lc
        if make_lc == 'renault':
            renault_models = {'clio', 'megane', 'captur', 'kadjar', 'scenic', 'laguna', 'talisman', 'koleos', 'zoe', 'twingo', 'arkana'}
            if model_lc in renault_models:
                return model_lc
        if make_lc == 'peugeot':
            if re.match('^\\d{3,4}$', model_lc):
                return model_lc
        return None

    def get_autovit_model_slug(make_text: str, model_text: str) -> str:
        make_lc = (make_text or '').strip().lower()
        model_lc = (model_text or '').strip().lower()
        if 'mercedes' in make_lc:
            if 'class' in model_lc or 'clasa' in model_lc:
                letter = re.search('([a-z])[- ]?clas', model_lc)
                if letter:
                    return f'{letter.group(1)}_classe'
            return model_lc.replace('-', '_')
        if make_lc == 'bmw':
            m = re.match('seria[- ]?(\\d)', model_lc)
            if m:
                return f'seria-{m.group(1)}'
            m = re.match('x(\\d)', model_lc)
            if m:
                return f'x{m.group(1)}'
        if make_lc == 'audi':
            m = re.match('([aq])[\\- ]?(\\d+)', model_lc)
            if m:
                return f'{m.group(1)}{m.group(2)}'
        if make_lc in ['volkswagen', 'vw']:
            vw_models = {'golf', 'passat', 'polo', 'tiguan', 'touareg', 'touran', 'arteon', 't-roc', 't-cross', 'jetta', 'scirocco'}
            if model_lc in vw_models:
                return model_lc
        if make_lc == 'ford':
            ford_models = {'focus', 'fiesta', 'mondeo', 'kuga', 'puma', 'mustang', 'ranger', 'ecosport', 's-max', 'c-max', 'galaxy'}
            if model_lc in ford_models:
                return model_lc.replace('-', '_')
            if model_lc == 'f-150' or model_lc == 'f 150':
                return 'f150'
        if make_lc == 'opel':
            opel_models = {'astra', 'corsa', 'insignia', 'mokka', 'crossland', 'grandland', 'zafira', 'meriva', 'vectra'}
            if model_lc in opel_models:
                return model_lc
        if make_lc in ['skoda', 'škoda']:
            skoda_models = {'octavia', 'fabia', 'superb', 'kodiaq', 'karoq', 'kamiq', 'scala', 'rapid', 'enyaq'}
            if model_lc in skoda_models:
                return model_lc
        if make_lc == 'toyota':
            toyota_models = {'corolla', 'yaris', 'rav4', 'camry', 'c-hr', 'aygo', 'land-cruiser', 'hilux', 'auris', 'avensis', 'prius'}
            if model_lc in toyota_models or model_lc.replace('-', '') in [m.replace('-', '') for m in toyota_models]:
                return model_lc.replace(' ', '-')
        if make_lc == 'dacia':
            dacia_models = {'logan', 'sandero', 'duster', 'spring', 'jogger', 'dokker', 'lodgy'}
            if model_lc in dacia_models:
                return model_lc
        if make_lc == 'renault':
            renault_models = {'clio', 'megane', 'captur', 'kadjar', 'scenic', 'talisman', 'koleos', 'zoe', 'twingo', 'arkana'}
            if model_lc in renault_models:
                return model_lc
        if make_lc == 'peugeot':
            if re.match('^\\d{3,4}$', model_lc):
                return model_lc
        if make_lc == 'hyundai':
            hyundai_models = {'tucson', 'i30', 'i20', 'i10', 'santa-fe', 'kona', 'ioniq', 'elantra'}
            if model_lc in hyundai_models or model_lc.replace(' ', '-') in hyundai_models:
                return model_lc.replace(' ', '-')
        if make_lc == 'kia':
            kia_models = {'sportage', 'ceed', 'rio', 'picanto', 'stonic', 'sorento', 'niro', 'optima', 'xceed'}
            if model_lc in kia_models:
                return model_lc
        return model_lc.replace(' ', '-')
    tasks = []
    olx_model_slug = get_olx_model_slug(make, model)
    autovit_model_slug = get_autovit_model_slug(make, model)
    if site_lc in ['olx', 'both']:
        tasks.append(scrape_olx(query, limit=limit, max_price=max_price, min_price=min_price, min_year=optimized_min_year, max_year=optimized_max_year, max_km=max_km, sort_order=sort, make=make, model_slug=olx_model_slug, max_pages=max_pages))
    if site_lc in ['autovit', 'both']:
        tasks.append(scrape_autovit(make=make, model=autovit_model_slug, limit=limit, max_pages=max_pages, max_price=max_price, min_price=min_price, min_year=optimized_min_year, max_year=optimized_max_year, max_km=max_km, sort_order=sort))
    results_list = await asyncio.gather(*tasks, return_exceptions=True)
    cars = []
    for res in results_list:
        if isinstance(res, list):
            cars.extend(res)
        else:
            print(f'Scraper error: {res}')
    strict_filtered = []
    loose_filtered = []
    filter_stats = {'price_parse': 0, 'make_fail': 0, 'bad_keyword': 0, 'price_over': 0, 'price_under': 0, 'passed': 0}
    skipped_ads = []
    for car in cars:
        try:
            raw_price = str(car.get('price', ''))
            price_val = int(re.sub('\\D', '', raw_price))
            if 'ron' in raw_price.lower() or 'lei' in raw_price.lower():
                price_val = int(price_val / 5)
            price = price_val
        except ValueError:
            filter_stats['price_parse'] += 1
            skipped_ads.append(('price_parse', car.get('link', ''), car.get('title', '')[:50]))
            continue

        def normalize_tokens(text: str) -> set[str]:
            return set((t for t in re.split('[^a-z0-9]', (text or '').lower()) if t))

        def normalize(text: str) -> str:
            return re.sub('[^a-z0-9]+', '', (text or '').lower())
        title_norm = normalize(str(car.get('title') or car.get('name') or ''))
        link_norm = normalize(str(car.get('link') or car.get('url') or ''))
        make_norm = normalize(make or '')
        model_norm = normalize(model or '')
        title_tokens = normalize_tokens(str(car.get('title') or car.get('name') or ''))
        link_tokens = normalize_tokens(str(car.get('link') or car.get('url') or ''))
        searchable_tokens = title_tokens | link_tokens
        make_tokens = normalize_tokens(make or '')
        model_tokens = normalize_tokens(model or '')
        model_matches = True
        bad_keywords = {'dezmembrari', 'dezmembrez', 'piese', 'piesa'}
        if any((bad in title_tokens or bad in link_tokens for bad in bad_keywords)):
            filter_stats['bad_keyword'] += 1
            skipped_ads.append(('bad_keyword', car.get('link', ''), car.get('title', '')[:50]))
            continue
        km_val = None
        try:
            km_raw = re.sub('\\D', '', str(car.get('km', '')))
            km_val = int(km_raw) if km_raw else None
        except:
            pass
        year_val = None
        try:
            year_raw = re.sub('\\D', '', str(car.get('year', '')))
            year_val = int(year_raw) if year_raw else None
        except:
            pass
        cc_val = None
        try:
            cc_raw = re.sub('\\D', '', str(car.get('cc', '')))
            cc_val = int(cc_raw) if cc_raw else None
        except:
            pass
        hp_val = None
        try:
            hp_raw = re.sub('\\D', '', str(car.get('hp', '')))
            hp_val = int(hp_raw) if hp_raw else None
        except:
            pass
        if price > max_price:
            continue
        if min_price is not None and price < min_price:
            continue
        if max_km is not None and km_val is not None and (km_val > max_km):
            continue
        if optimized_min_year is not None and year_val is not None and (year_val < optimized_min_year):
            continue
        if optimized_max_year is not None and year_val is not None and (year_val > optimized_max_year):
            continue
        if min_cc is not None and cc_val is not None and (cc_val < min_cc):
            continue
        if min_hp is not None and hp_val is not None and (hp_val < min_hp):
            continue
        car['price'] = price
        if model_matches:
            strict_filtered.append(car)
        else:
            make_is_bmw = make_norm == 'bmw'
            model_is_x = model_norm.startswith('x') if model_norm else False
            contains_x_series = any((x in title_norm or x in link_norm for x in ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7'])) if title_norm or link_norm else False
            if make_is_bmw and (not model_is_x) and contains_x_series:
                continue
            if make_is_bmw and (not model_is_x) and model_norm:
                import re as _re
                m_num = _re.match('(\\d{3})', model_norm)
                model_num = m_num.group(1) if m_num else ''
                m_series = _re.match('(\\d)', model_norm)
                series_digit = m_series.group(1) if m_series else ''
                allowed = False
                if model_num and (model_num in title_norm or model_num in link_norm or model_num + 'd' in title_norm):
                    allowed = True
                if series_digit:
                    series_tokens = [f'seria{series_digit}', f'serie{series_digit}', f'{series_digit}series', f'series{series_digit}']
                    if any((tok in title_norm or tok in link_norm for tok in series_tokens)):
                        allowed = True
                if not allowed:
                    continue
            make_is_audi = make_norm == 'audi'
            model_is_q = model_norm.startswith('q') if model_norm else False
            contains_q_series = any((q in title_norm or q in link_norm for q in ['q2', 'q3', 'q4', 'q5', 'q7', 'q8'])) if title_norm or link_norm else False
            if make_is_audi and (not model_is_q) and contains_q_series:
                continue
            if make_is_audi and (not model_is_q) and model_norm:
                import re as _re2
                m2 = _re2.match('([a-z])(\\d)', model_norm)
                if m2:
                    series_token = f'{m2.group(1)}{m2.group(2)}'
                    if series_token.startswith('a'):
                        if not (series_token in title_norm or series_token in link_norm):
                            continue
            make_is_mercedes = make_norm in ('mercedes', 'mercedesbenz', 'mercedesbenz')
            import re as _re3
            mer_class_match = _re3.match('([a-z])', model_norm or '')
            requested_class = mer_class_match.group(1) if mer_class_match else ''
            is_g_requested = requested_class == 'g'
            contains_g_suv = any((tok in title_norm or tok in link_norm for tok in ['gla', 'glb', 'glc', 'gle', 'gls', 'g55', 'g63', 'g500', 'g350'])) if title_norm or link_norm else False
            if make_is_mercedes and (not is_g_requested) and contains_g_suv:
                continue
            if make_is_mercedes and requested_class in ('c', 'e', 's'):
                class_tokens = [f'clasa{requested_class}', f'{requested_class}class']
                if not any((tok in title_norm or tok in link_norm for tok in class_tokens)):
                    continue
            loose_filtered.append(car)
    filter_stats['passed'] = len(strict_filtered) + len(loose_filtered)
    print(f'Filter Stats: {filter_stats}')
    if skipped_ads:
        print(f'\n🚫 SKIPPED ADS ({len(skipped_ads)} total):')
        for (reason, link, title) in skipped_ads:
            print(f'  [{reason}] {title} → {link[:60]}...')
    print(f'📋 strict_filtered: {len(strict_filtered)}, loose_filtered: {len(loose_filtered)}')
    final_results = strict_filtered if strict_filtered else loose_filtered if model else []
    print(f'📋 final_results before repair: {len(final_results)}')
    ads_to_repair = []
    import aiohttp
    from bs4 import BeautifulSoup
    import json as _json_live

    async def repair_ad(ad):
        is_missing_image = not ad.get('image') or 'no_thumbnail' in str(ad.get('image'))
        is_missing_image = not ad.get('image') or 'no_thumbnail' in str(ad.get('image'))
        if is_missing_image:
            try:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as sess:
                    async with sess.get(ad.get('link'), timeout=5) as r:
                        if r.status == 404 or len(str(r.url)) < 30:
                            return None
                        if r.status == 200:
                            html = await r.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            nd = soup.find('script', {'id': '__NEXT_DATA__'})
                            current_price = int(ad.get('price', 0))
                            if nd and nd.string:
                                d = _json_live.loads(nd.string)
                                pp = d.get('props', {}).get('pageProps', {})
                                adv = pp.get('advert') or pp.get('data', {}).get('advert')
                                if adv:
                                    p = adv.get('price', {}).get('value')
                                    if p:
                                        new_p = int(p)
                                        if new_p > current_price:
                                            ad['price'] = new_p
                            if is_missing_image:
                                og = soup.find('meta', attrs={'property': 'og:image'})
                                if og and og.get('content'):
                                    ad['image'] = og.get('content')
                                if not ad.get('image'):
                                    scripts = soup.find_all('script', type='application/ld+json')
                                    for s in scripts:
                                        try:
                                            data = _json_live.loads(s.string)
                                            if isinstance(data, dict) and 'image' in data:
                                                imgs = data['image']
                                                if isinstance(imgs, list) and imgs:
                                                    ad['image'] = imgs[0]
                                                elif isinstance(imgs, str):
                                                    ad['image'] = imgs
                                                break
                                        except:
                                            pass
                                if not ad.get('image'):
                                    selectors = ['img.css-1bmvjcs', 'div.swiper-zoom-container img', 'div.css-1bnh990 img', 'img.photo-handler', '.image-gallery-slide img']
                                    for sel in selectors:
                                        gal = soup.select_one(sel)
                                        if gal:
                                            src = gal.get('src') or gal.get('data-src')
                                            if src:
                                                ad['image'] = src
                                                break
            except:
                pass
        return ad
    repair_tasks = []
    for ad in final_results:
        repair_tasks.append(repair_ad(ad))
    if repair_tasks:
        repaired_results = await asyncio.gather(*repair_tasks)
        final_results = [r for r in repaired_results if r]
    unique_map = {}
    unique_list = []
    import re as _re_dedup

    def get_ad_id(link_str):
        m_auto = _re_dedup.search('-ID([a-zA-Z0-9]+)\\.html', link_str)
        if m_auto:
            return 'autovit_' + m_auto.group(1)
        if 'olx.ro' in link_str:
            m_olx = _re_dedup.search('-([a-zA-Z0-9]+)\\.html', link_str)
            if m_olx:
                return 'olx_' + m_olx.group(1)
        return link_str
    removed_duplicates = []
    for c in final_results:
        lnk = c.get('link')
        if lnk:
            ad_id = get_ad_id(lnk)
            if ad_id not in unique_map:
                unique_map[ad_id] = True
                unique_list.append(c)
            else:
                removed_duplicates.append((c.get('title', '?')[:40], c.get('subsource', '?'), lnk[:60]))
    print(f'After deduplication: {len(unique_list)} (removed {len(removed_duplicates)} duplicates)')
    if removed_duplicates:
        print(f'\nREMOVED DUPLICATES ({len(removed_duplicates)} total):')
        for (title, source, link) in removed_duplicates[:15]:
            print(f'  [{source}] {title} → {link}...')
        if len(removed_duplicates) > 15:
            print(f'  ... and {len(removed_duplicates) - 15} more')
    final_results = unique_list
    if final_results and make and model:
        prices = []
        for r in final_results:
            p = r.get('price')
            if p:
                try:
                    p_val = int(re.sub('[^\\d]', '', str(p)))
                    if p_val > 0:
                        prices.append(p_val)
                except:
                    pass
        years = []
        for r in final_results:
            y = r.get('year')
            if y:
                try:
                    years.append(int(float(str(y).strip())))
                except:
                    pass
        kms = [int(re.sub('\\D', '', str(r.get('km', '')))) for r in final_results if r.get('km')]
        avg_price = sum(prices) / len(prices) if prices else None
        avg_year = sum(years) / len(years) if years else None
        avg_km = sum(kms) / len(kms) if kms else None
        car_db_optimizer.update_search_stats(make=make, model=model, avg_price=avg_price, avg_year=avg_year, avg_km=avg_km)
    return final_results[:limit]

def add_alert(user_email: str, make: str, model: str, max_price: int):
    return car_db_optimizer.add_alert(user_email, make, model, max_price)
import os
import resend

def send_email_notification(to_email: str, car_list: list, search_details: str):
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    
    if not resend.api_key:
        print("Eroare: RESEND_API_KEY nu este setat pentru trimiterea mașinilor găsite.")
        return

    subject = f'CarSniper: {len(car_list)} oferte noi pentru {search_details}'
    
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #0a0a0a; color: #ffffff; border-radius: 10px;">
        <h2 style="color: #38bdf8; text-align: center;">Vânătoare încheiată cu succes!</h2>
        <p style="font-size: 16px; line-height: 1.5; text-align: center;">Am găsit <strong>{len(car_list)}</strong> mașini noi pentru căutarea ta ({search_details}):</p>
        <div style="margin-top: 30px;">
    """
    
    for car in car_list:
        link = car.get('link') or car.get('url')
        html_content += f"""
        <div style="background-color: #121212; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #38bdf8; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; font-size: 18px;">
                <a href="{link}" style="color: #38bdf8; text-decoration: none;">{car.get('title')}</a>
            </h3>
            <ul style="list-style-type: none; padding: 0; margin: 0; font-size: 14px; color: #e4e4e7;">
                <li><strong>Preț:</strong> <span style="color: #4ade80; font-weight: bold;">{car.get('price')}</span></li>
                <li><strong>An:</strong> {car.get('year') or '?'}</li>
                <li><strong>Km:</strong> {car.get('km') or '?'}</li>
            </ul>
        </div>
        """
        
    html_content += """
        </div>
        <p style="font-size: 12px; color: #a1a1aa; text-align: center; margin-top: 30px; border-top: 1px solid #27272a; padding-top: 20px;">
            Aceasta este o notificare generată automat de algoritmul CarSniper.
        </p>
    </div>
    """

    params = {
        "from": "CarSniper Alerts <onboarding@resend.dev>",
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }

    try:
        email = resend.Emails.send(params)
        print(f"Notificare cu {len(car_list)} mașini trimisă către {to_email} (ID: {email['id']})")
    except Exception as e:
        print(f"Eroare la trimiterea emailului cu mașini via Resend: {e}")

async def check_alerts():
    alerts = car_db_optimizer.get_alerts()
    active_alerts = [a for a in alerts if a.get('active', 1) == 1]
    print(f'[Scheduler] Verific {len(active_alerts)} alerte active (din {len(alerts)} totale)...')
    
    for alert in active_alerts:
        try:
            results = await search_cars(
                make=alert['make'], 
                model=alert['model'], 
                min_price=alert.get('min_price'),
                max_price=alert.get('max_price'), 
                min_year=alert.get('min_year'),
                max_year=alert.get('max_year'),
                max_km=alert.get('max_km'),
                site='both', 
                limit=5
            )
            
            if results:
                print(f"ALERT MATCH for {alert['user_email']}: Found {len(results)} cars. Deactivating alert...")
                send_email_notification(alert['user_email'], results, f"{alert['make']} {alert['model']}")
                car_db_optimizer.deactivate_alert(alert['id'])
                
        except Exception as e:
            print(f"Eroare la verificarea alertei {alert['id']}: {e}")