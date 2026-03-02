import aiohttp
import asyncio
import re
import json
from bs4 import BeautifulSoup
BASE_URL = 'https://www.autovit.ro/autoturisme/{}/{}'

async def scrape_autovit(make: str, model: str, page: int=1, limit: int=100, max_pages: int=5, enrich: bool=False, *, min_price: int | None=None, max_price: int | None=None, min_year: int | None=None, max_year: int | None=None, max_km: int | None=None, sort_order: str='price_asc'):
    USER_AGENTS = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15']
    import random
    results: list[dict] = []
    seen_links_total: set[str] = set()
    scrape_stats = {'dupes': 0, 'invalid': 0}

    async def _fetch_next_data_details(url: str) -> tuple[str | None, str | None]:
        ua = random.choice(USER_AGENTS)
        headers_det = {'User-Agent': ua, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Referer': 'https://www.autovit.ro/'}
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as sess:
                async with sess.get(url, headers=headers_det, timeout=8) as r:
                    if r.status != 200:
                        return (None, None)
                    text = await r.text()
                    s = BeautifulSoup(text, 'html.parser')
                    price = None
                    image = None
                    nd = s.find('script', {'id': '__NEXT_DATA__'})
                    if nd and nd.string:
                        data = json.loads(nd.string)
                        pp = data.get('props', {}).get('pageProps', {})
                        advert = pp.get('advert') or pp.get('data', {}).get('advert')
                        if advert:
                            p_val = advert.get('price', {}).get('value')
                            if p_val:
                                price = str(int(p_val))
                            photos = advert.get('photos') or advert.get('images')
                            if photos and isinstance(photos, list) and (len(photos) > 0):
                                first_photo = photos[0]
                                if isinstance(first_photo, dict):
                                    image = first_photo.get('large') or first_photo.get('medium') or first_photo.get('src')
                                elif isinstance(first_photo, str):
                                    image = first_photo
                    if not price:
                        jld = s.find('script', {'id': 'listing-json-ld'})
                        if jld and jld.string:
                            data = json.loads(jld.string)
                            offers = data.get('offers', {})
                            if offers:
                                p = offers.get('price')
                                if p:
                                    price = str(int(float(p)))
                    if not image:
                        og = s.find('meta', attrs={'property': 'og:image'})
                        if og and og.get('content'):
                            image = og.get('content')
                    return (price, image)
        except:
            pass
        return (None, None)

    async def fetch_page(page_num: int):
        try:
            params = {'page': str(page_num)}
            if sort_order == 'price_asc':
                params['search[order]'] = 'filter_float_price:asc'
            elif sort_order == 'price_desc':
                params['search[order]'] = 'filter_float_price:desc'
            elif sort_order == 'newest':
                params['search[order]'] = 'created_at:desc'
            if max_price is not None:
                params['search[filter_float_price:to]'] = str(max_price)
            if min_price is not None:
                params['search[filter_float_price:from]'] = str(min_price)
            if min_year is not None:
                params['search[filter_float_year:from]'] = str(min_year)
            if max_year is not None:
                params['search[filter_float_year:to]'] = str(max_year)
            if max_km is not None:
                params['search[filter_float_mileage:to]'] = str(max_km)
                params['search[advanced_search_expanded]'] = 'true'
            url = BASE_URL.format(make.lower().replace(' ', '-'), model.lower())
            ua = random.choice(USER_AGENTS)
            headers_req = {'User-Agent': ua, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1', 'Referer': 'https://www.google.com/', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
            page_ads = []
            retries = 3
            for attempt in range(retries):
                try:
                    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as sess:
                        await asyncio.sleep(random.uniform(2.0, 4.0))
                        async with sess.get(url, params=params, headers=headers_req, timeout=15) as response:
                            if response.status == 429:
                                wait_time = 5 * (attempt + 1)
                                print(f'Autovit 429 on Page {page_num}, attempt {attempt + 1}. Waiting {wait_time}s...')
                                await asyncio.sleep(wait_time)
                                continue
                            if response.status != 200:
                                print(f'Autovit non-200 ({response.status}) on Page {page_num}')
                                return None
                            html = await response.text()
                            break
                except Exception as e:
                    print(f'Autovit error on Page {page_num}: {e}')
                    await asyncio.sleep(3)
                    continue
            else:
                print(f' Autovit Page {page_num} failed after {retries} retries')
                return None
            soup = BeautifulSoup(html, 'html.parser')
            detail_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/autoturisme/anunt/' in href and href.endswith('.html'):
                    if href.startswith('/'):
                        href = 'https://www.autovit.ro' + href
                    if href not in detail_links:
                        detail_links.append(href)
            found_json = False
            script = soup.find('script', {'id': 'listing-json-ld', 'type': 'application/ld+json'})
            if script and script.string:
                try:
                    data = json.loads(script.string)
                    items = data.get('mainEntity', {}).get('itemListElement', [])
                    for (idx, elem) in enumerate(items):
                        item = elem.get('itemOffered', {})
                        name = item.get('name')
                        if not name:
                            continue
                        price_spec = elem.get('priceSpecification', {})
                        price_raw = price_spec.get('price')
                        link = item.get('url') or elem.get('url')
                        if not link:
                            link = url
                        if link.startswith('/'):
                            link = 'https://www.autovit.ro' + link
                        img_url = item.get('image')
                        if isinstance(img_url, list) and img_url:
                            img_url = img_url[0]
                        fingerprint = link if '-ID' in link else f'{link}__img__{img_url}'
                        car_year_raw = item.get('productionDate') or item.get('modelDate')
                        car_year = None
                        if car_year_raw and re.match('^\\d{4}$', str(car_year_raw)):
                            car_year = str(car_year_raw)
                        car_km_dict = item.get('mileageFromOdometer', {})
                        car_km = car_km_dict.get('value') if isinstance(car_km_dict, dict) else None
                        if fingerprint in seen_links_total:
                            scrape_stats['dupes'] += 1
                            continue
                        seen_links_total.add(fingerprint)
                        if price_raw:
                            try:
                                final_price = int(float(price_raw))
                                page_ads.append({'title': name, 'price': f'{final_price} €', 'link': link, 'image': img_url, 'subsource': 'Autovit', 'year': car_year, 'km': f'{car_km} km' if car_km else None})
                                found_json = True
                            except:
                                pass
                except Exception as e:
                    print(f'JSON-LD Parsing Error: {e}')
            if True:
                articles = soup.find_all('article')
                for art in articles:
                    try:
                        if not art.has_attr('data-id'):
                            continue
                        a = art.find('a', href=True)
                        if not a:
                            continue
                        lnk = a['href']
                        if lnk.startswith('/'):
                            lnk = 'https://www.autovit.ro' + lnk
                        if lnk in seen_links_total:
                            continue
                        seen_links_total.add(lnk)
                        h2 = art.find('h2') or art.find('h1')
                        title = h2.get_text(strip=True) if h2 else 'No Title'
                        price = '0'
                        price_span = art.find(string=re.compile('EUR'))
                        if price_span:
                            parent = price_span.parent.parent if price_span.parent else None
                            if parent:
                                h3 = parent.find('h3')
                                if h3:
                                    raw_p = h3.get_text(strip=True)
                                    clean_p = raw_p.replace(' ', '')
                                    if ',' in clean_p:
                                        clean_p = clean_p.replace('.', '').replace(',', '.')
                                    else:
                                        clean_p = clean_p.replace('.', '')
                                    try:
                                        price = str(int(float(clean_p)))
                                    except:
                                        pass
                        img = art.find('img')
                        image_url = img.get('src') if img else None
                        p_num = 0
                        try:
                            p_num = int(float(str(price).replace('€', '').strip()))
                        except:
                            pass
                        needs_enrichment = p_num < 15000 or not image_url
                        if needs_enrichment:
                            try:
                                (new_p, new_img) = await _fetch_next_data_details(lnk)
                                if new_p:
                                    try:
                                        new_p_val = int(float(str(new_p).replace('€', '')))
                                        if new_p_val > p_num:
                                            price = new_p
                                    except:
                                        if p_num == 0:
                                            price = new_p
                                if new_img and (not image_url):
                                    image_url = new_img
                            except:
                                pass
                        if price == '0' or price == 0:
                            scrape_stats['invalid'] += 1
                            continue
                        html_year = None
                        html_km = None
                        nd = soup.find('script', {'id': '__NEXT_DATA__'})
                        if nd and nd.string:
                            try:
                                nd_data = json.loads(nd.string)
                                urql = nd_data.get('props', {}).get('pageProps', {}).get('urqlState', {})
                                for (_k, _v) in urql.items():
                                    if 'data' in _v:
                                        _d = json.loads(_v['data'])
                                        if 'advertSearch' in _d:
                                            for edge in _d['advertSearch'].get('edges', []):
                                                node = edge.get('node', {})
                                                node_url = node.get('url', '')
                                                if node_url and node_url in lnk:
                                                    for param in node.get('parameters', []):
                                                        if param.get('key') == 'year':
                                                            html_year = param.get('value')
                                                        elif param.get('key') == 'mileage':
                                                            html_km = param.get('value')
                                                    break
                                            break
                            except:
                                pass
                        page_ads.append({'title': title, 'price': f'{price} €', 'link': lnk, 'image': image_url, 'subsource': 'Autovit', 'year': html_year, 'km': f'{html_km} km' if html_km else None})
                    except:
                        pass
            return page_ads
        except Exception as e:
            return None
    current_p = page
    empty_pages = 0
    failed_pages = []
    while len(results) < limit:
        if current_p > max_pages:
            break
        ads = await fetch_page(current_p)
        if ads is None:
            failed_pages.append(current_p)
            current_p += 1
            continue
        if ads is None or len(ads) == 0:
            print(f'Warning: Page {current_p} returned 0 ads. (Consecutive empty: {empty_pages + 1})')
            empty_pages += 1
            if empty_pages >= 2:
                print('Stopping: Too many consecutive empty pages.')
                break
        else:
            empty_pages = 0
        enrich_tasks = []
        for ad in ads:
            if ad['link'] not in seen_links_total:
                seen_links_total.add(ad['link'])
                p_n = 0
                try:
                    p_n = int(ad['price'].replace('€', '').strip())
                except:
                    pass
                if p_n < 15000 or not ad['image']:
                    enrich_tasks.append(_fetch_next_data_details(ad['link']))
                else:
                    results.append(ad)
        if enrich_tasks:
            enriched_data = await asyncio.gather(*enrich_tasks)
            for (idx, e_data) in enumerate(enriched_data):
                (p_new, i_new) = e_data
                pass
        for ad in ads:
            if ad['link'] not in [r['link'] for r in results]:
                results.append(ad)
        current_p += 1
        if len(results) >= limit:
            break
    if failed_pages:
        print(f'🔄 Retrying {len(failed_pages)} failed pages: {failed_pages}')
        for p_idx in failed_pages:
            if len(results) >= limit:
                break
            await asyncio.sleep(random.uniform(2.0, 4.0))
            ads = await fetch_page(p_idx)
            if ads:
                for ad in ads:
                    if ad['link'] not in seen_links_total:
                        seen_links_total.add(ad['link'])
                        results.append(ad)
    print(f"Autovit Stats: Found {len(results)} | Skipped {scrape_stats['dupes']} Duplicates | Skipped {scrape_stats['invalid']} Invalid (Price=0)")
    return results[:limit]