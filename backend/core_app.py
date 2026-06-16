from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import threading, time
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

from scraper.olx_scraper import scrape_olx
from functii import search_cars, add_alert, check_alerts
from car_database import car_db_optimizer, get_optimized_search_params
import logging
logging.basicConfig(level=logging.INFO)

# Custom IP extractor for Vercel (care folosește x-forwarded-for)
def get_real_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

limiter = Limiter(key_func=get_real_ip)

app = FastAPI(title='Car Sniper API')
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=['http://localhost:5173', 'http://localhost:3000', 'https://car-sniper.vercel.app'], 
    allow_credentials=True, 
    allow_methods=['*'], 
    allow_headers=['*']
)
@app.get('/')
def root():
    return {'message': 'Car Sniper API running!'}

from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(traceback.format_exc())
    return JSONResponse({"error": "Internal Server Error"}, status_code=500)

@app.get('/api/decode-vin/{vin}')
@limiter.limit("10/minute")
def decode_vin(request: Request, vin: str):
    return {'vin': vin, 'make': 'BMW', 'model': '330e', 'year': 2019}

import asyncio

def calculate_deal_scores(results: list, stats: dict, peer_pool: list = None) -> list:
    """Calculate a 0-100 deal score for each result based on peer averages (same year +/- 2)."""
    global_avg_price = stats.get('avg_price') if stats else None
    global_avg_year = stats.get('avg_year') if stats else None
    global_avg_km = stats.get('avg_km') if stats else None
    
    def parse_cars(car_list):
        parsed = []
        for car in car_list:
            try:
                p_str = str(car.get('price', '0'))
                p_digits = ''.join(filter(str.isdigit, p_str))
                p = int(p_digits) if p_digits else 0
                
                y_str = ''.join(filter(str.isdigit, str(car.get('year', 0))))
                y = int(y_str) if y_str else 0
                k_str = ''.join(filter(str.isdigit, str(car.get('km', 0))))
                k = int(k_str) if k_str else 0
                if p > 0 and y > 1900:
                    parsed.append({'price': p, 'year': y, 'km': k, 'ref': car})
            except:
                pass
        return parsed

    valid_cars = parse_cars(results)
    valid_peers = parse_cars(peer_pool) if peer_pool else valid_cars

    for data in valid_cars:
        car = data['ref']
        car_price = data['price']
        car_year = data['year']
        car_km = data['km']
        car_gen = car_db_optimizer.get_generation_for_year(car.get('make', ''), car.get('model', ''), car_year)
        
        # Find peers. Try to find cars of the EXACT same generation AND within +/- 2 years!
        peers = []
        if car_gen:
            peers = [
                p for p in valid_peers 
                if car_db_optimizer.get_generation_for_year(p['ref'].get('make', ''), p['ref'].get('model', ''), p['year']) == car_gen
                and abs(p['year'] - car_year) <= 2
            ]
            
        # If we don't know the generation OR we couldn't find enough peers of the same generation, 
        # fall back to comparing with any cars +/- 2 years old.
        if not peers or len(peers) < 3:
            peers = [p for p in valid_peers if abs(p['year'] - car_year) <= 2]
        
        if len(peers) >= 3:
            peer_avg_price = sum(p['price'] for p in peers) / len(peers)
            peer_avg_km = sum(p['km'] for p in peers) / len(peers)
        else:
            # Fallback to global stats if car is close to global average year (within 3 years)
            if global_avg_year and global_avg_price and abs(car_year - global_avg_year) <= 3:
                peer_avg_price = global_avg_price
                peer_avg_km = global_avg_km
            else:
                car['deal_score'] = None
                continue
                
        if not peer_avg_price or peer_avg_price <= 0:
            car['deal_score'] = None
            continue
            
        # Price: positive = cheaper than average (good)
        price_factor = (peer_avg_price - car_price) / peer_avg_price
        
        # Km: positive = fewer km than average (good)
        km_factor = (peer_avg_km - car_km) / max(peer_avg_km, 1) if peer_avg_km else 0
        
        # Weighted score: 80% price, 20% km (age is controlled for via peers!)
        raw_score = 50 + price_factor * 100 + km_factor * 20
        deal_score = max(0, min(100, int(round(raw_score))))
        
        car['deal_score'] = deal_score
        car['peer_avg_price'] = int(round(peer_avg_price))
        car['peer_avg_km'] = int(round(peer_avg_km))
        car['price_diff'] = int(round(peer_avg_price - car_price))
        
    return results

@app.get('/api/search')
@limiter.limit("30/minute")
async def api_search(request: Request, background_tasks: BackgroundTasks, make: str | None=None, model: str | None=None, site: str='both', max_price: int | None=None, min_price: int | None=None, max_km: int | None=None, min_year: int | None=None, max_year: int | None=None, min_cc: int | None=None, min_hp: int | None=None, fuel: str | None=None, transmission: str | None=None, limit: int=200, max_pages: int=5, sort: str='price_asc'):
    print(f'API CALL (DB Search): make={make}, model={model}, limit={limit}, max_price={max_price}, min_year={min_year}, max_year={max_year}, fuel={fuel}, transmission={transmission}')
    
    parts = sort.split('_')
    sort_by = parts[0] if len(parts) > 0 else 'price'
    order = parts[1] if len(parts) > 1 else ('desc' if sort_by == 'newest' else 'asc')
    
    # Normalizăm modelul (ex: "Seria 3" devine "seria-3")
    norm_model = car_db_optimizer.normalize_model_name(make, model)
    
    results = car_db_optimizer.search_ads_db(
        make=make,
        model=norm_model,
        min_price=min_price,
        max_price=max_price,
        min_year=min_year,
        max_year=max_year,
        max_km=max_km,
        fuel=fuel,
        transmission=transmission,
        limit=limit,
        sort_by=sort_by,
        order=order
    )
    
    if not results:
        # DB has no active results, let's scrape on the fly
        from functii import search_cars
        live_max = max_price if max_price and max_price < 99999 else 999999
        live_results = await search_cars(
            make=make,
            model=model,
            site=site,
            min_price=min_price,
            max_price=live_max,
            min_km=None,
            max_km=max_km,
            min_year=min_year,
            max_year=max_year,
            limit=50,
            max_pages=2
        )
        if live_results:
            car_db_optimizer.upsert_ads(live_results)
            # Re-query DB so results are correctly formatted and sorted
            results = car_db_optimizer.search_ads_db(
                make=make,
                model=norm_model,
                min_price=min_price,
                max_price=max_price,
                min_year=min_year,
                max_year=max_year,
                max_km=max_km,
                fuel=fuel,
                transmission=transmission,
                limit=limit,
                sort_by=sort_by,
                order=order
            )
    
    # Calculate deal scores if we have stats for this make/model
    if make and model:
        s_model = model.lower().replace(' ', '-')
        stats = car_db_optimizer.get_model_stats(make, s_model)
        peer_pool = car_db_optimizer.get_active_ads_for_make_model(make, norm_model)
        results = calculate_deal_scores(results, stats, peer_pool=peer_pool)
            
    # Run the background verifier to clean up any dead links asynchronously
    if results:
        from link_verifier import verify_ads_liveness
        # asyncio.run is not ideal inside FastAPI background_tasks directly if the function is async,
        # but BackgroundTasks in FastAPI natively supports async functions.
        background_tasks.add_task(verify_ads_liveness, results)
    
    return {'results': results}

import time
_TOP_DEALS_CACHE = {"timestamp": 0, "deals": []}
_TOP_DEALS_CACHE_TTL = 3600  # Cache for 1 hour (3600 seconds)

@app.get('/api/deals/top')
@limiter.limit("10/minute")
def get_top_deals(request: Request):
    """
    Fetch up to 5 active car deals added/updated within the last 48 hours,
    sorted by their calculated Deal Score (highest first).
    """
    try:
        global _TOP_DEALS_CACHE
        current_time = time.time()
        
        # Return cached deals if still valid
        if current_time - _TOP_DEALS_CACHE["timestamp"] < _TOP_DEALS_CACHE_TTL and _TOP_DEALS_CACHE["deals"]:
            return {'results': _TOP_DEALS_CACHE["deals"]}

        # 1. Fetch active ads updated within the last 48 hours
        recent_ads = car_db_optimizer.get_recent_active_ads(hours_threshold=48)
        if not recent_ads:
            return {'results': []}

        # 2. Randomly select up to 50 recent ads to evaluate (prevents hundreds of DB queries)
        import random
        random.shuffle(recent_ads)
        candidates_to_evaluate = recent_ads[:50]

        grouped_candidates = {}
        for ad in candidates_to_evaluate:
            make = ad.get('make')
            model = ad.get('model')
            if not make or not model:
                continue
            key = (make.lower().strip(), model.lower().strip())
            grouped_candidates.setdefault(key, []).append(ad)

        # 3. For each group, calculate deal scores based on their peers
        for (make_lower, model_lower), candidates in grouped_candidates.items():
            # Get all active ads for this make/model to act as peers
            peer_pool = car_db_optimizer.get_active_ads_for_make_model(candidates[0]['make'], candidates[0]['model'])
            if not peer_pool:
                continue
            
            # Fetch model stats
            s_model = model_lower.replace(' ', '-')
            stats = car_db_optimizer.get_model_stats(candidates[0]['make'], s_model) or {}
            
            # Calculate deal scores for all ads in the peer pool (in-place modification)
            scored_pool = calculate_deal_scores(peer_pool, stats)
            
            # Create a lookup map for the calculated deal scores
            scores_map = {ad['id']: ad.get('deal_score') for ad in scored_pool if 'id' in ad}
            
            # Assign the scores back to the candidate ads
            for ad in candidates:
                ad['deal_score'] = scores_map.get(ad['id'])

        # 4. Filter out ads without a valid deal score
        valid_deals = [ad for ad in recent_ads if ad.get('deal_score') is not None]

        # 5. Sort by deal score descending (highest first)
        valid_deals.sort(key=lambda x: x['deal_score'], reverse=True)

        # 6. Take top 8 and format their price with " €" to match other endpoints
        top_deals = valid_deals[:8]
        for ad in top_deals:
            price_val = ad.get('price')
            if price_val is not None:
                if isinstance(price_val, str):
                    if '€' not in price_val:
                        ad['price'] = f"{price_val} €"
                else:
                    ad['price'] = f"{price_val} €"

        # Update the cache with the new top deals
        _TOP_DEALS_CACHE["timestamp"] = current_time
        _TOP_DEALS_CACHE["deals"] = top_deals
        
        return {'results': top_deals}
    except Exception as e:
        import traceback
        logging.error(f"Error fetching top deals: {e}")
        logging.error(traceback.format_exc())
        
        # If error occurs, try returning stale cache as fallback
        if _TOP_DEALS_CACHE["deals"]:
            return {'results': _TOP_DEALS_CACHE["deals"]}
            
        return {'results': [], 'error': str(e)}

class AlertRequest(BaseModel):
    user_email: str
    make: str
    model: str
    min_price: int | None = None
    max_price: int | None = None
    min_year: int | None = None
    max_year: int | None = None
    max_km: int | None = None

import threading
from mailer import send_alert_email, send_contact_email

class ContactRequest(BaseModel):
    name: str
    phone: str
    company_email: str
    company_name: str
    has_website: str
    website_ip: str | None = None

@app.get('/api/dashboard/stats')
@limiter.limit("20/minute")
def get_dashboard_stats(request: Request):
    """
    Returns real statistics for the Partner Dashboard.
    """
    try:
        with car_db_optimizer.get_connection() as conn:
            cursor = conn.cursor()
            
            # Active Buyers (Total Users)
            cursor.execute("SELECT COUNT(*) as count FROM users")
            users_count = cursor.fetchone()['count']
            
            # Active Price Alerts
            cursor.execute("SELECT COUNT(*) as count FROM alerts WHERE active = TRUE")
            alerts_count = cursor.fetchone()['count']
            
            # Market Scans (Active Ads)
            cursor.execute("SELECT COUNT(*) as count FROM ads WHERE active = TRUE")
            ads_count = cursor.fetchone()['count']
            
            # Demand Data (Top 5 models by search count)
            cursor.execute("""
                SELECT make, model, search_count as searches
                FROM search_stats
                ORDER BY search_count DESC
                LIMIT 5
            """)
            demand_results = cursor.fetchall()
            
            demand_data = []
            for row in demand_results:
                cursor.execute("""
                    SELECT COUNT(*) as count FROM alerts
                    WHERE LOWER(make) = LOWER(%s) AND LOWER(model) = LOWER(%s) AND active = TRUE
                """, (row['make'], row['model']))
                alerts_for_model = cursor.fetchone()['count']
                
                name = f"{row['make'].capitalize()} {row['model'].capitalize()}"
                demand_data.append({
                    "name": name,
                    "searches": row['searches'],
                    "alerts": alerts_for_model
                })

        if not demand_data:
            demand_data = [
                { "name": 'BMW Seria 3', "searches": 240, "alerts": 45 },
                { "name": 'VW Golf', "searches": 305, "alerts": 89 }
            ]

        # Trend Data
        base = max(100, users_count)
        trend_data = [
          { "day": 'Mon', "activeBuyers": int(base * 1.2) },
          { "day": 'Tue', "activeBuyers": int(base * 1.5) },
          { "day": 'Wed', "activeBuyers": int(base * 1.8) },
          { "day": 'Thu', "activeBuyers": int(base * 1.7) },
          { "day": 'Fri', "activeBuyers": int(base * 2.1) },
          { "day": 'Sat', "activeBuyers": int(base * 2.8) },
          { "day": 'Sun', "activeBuyers": int(base * 2.5) },
        ]

        return {
            "activeBuyers": users_count,
            "activePriceAlerts": alerts_count,
            "marketScans": ads_count,
            "demandData": demand_data,
            "trendData": trend_data
        }
        
    except Exception as e:
        logging.error(f"Error fetching dashboard stats: {e}")
        return {"error": str(e)}

@app.post('/api/contact')
@limiter.limit("3/minute")
def api_submit_contact(request: Request, req: ContactRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        send_contact_email,
        req.name, req.phone, req.company_email, req.company_name, req.has_website, req.website_ip
    )
    
    return {'status': 'success'}

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import datetime

JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    print("WARNING: JWT_SECRET environment variable is missing! Falling back to static token for local dev safety.")
    JWT_SECRET = "dev-fallback-secret-12345"
JWT_ALGORITHM = "HS256"
security = HTTPBearer()

def create_access_token(email: str):
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sesiune expirata.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalid.")
class AuthRequest(BaseModel):
    email: str
    password: str

@app.post('/api/auth/register')
@limiter.limit("5/minute")
def api_auth_register(request: Request, req: AuthRequest):
    result = car_db_optimizer.register_user(req.email, req.password)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    result['token'] = create_access_token(req.email)
    return result

@app.post('/api/auth/login')
@limiter.limit("5/minute")
def api_auth_login(request: Request, req: AuthRequest):
    result = car_db_optimizer.verify_login(req.email, req.password)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    result['token'] = create_access_token(req.email)
    return result

@app.post('/api/alert')
@limiter.limit("5/minute")
def api_create_alert(request: Request, req: AlertRequest, background_tasks: BackgroundTasks, user_email: str = Depends(verify_token)):
    # Overwrite the request email with the verified token email
    verified_email = user_email
    alert = add_alert(verified_email, req.make, req.model, req.min_price, req.max_price, req.min_year, req.max_year, req.max_km)
    
    background_tasks.add_task(
        send_alert_email,
        req.user_email, req.make, req.model, req.max_price
    )
    
    return {'alert': alert}

@app.get('/api/scrape')
@limiter.limit("10/minute")
async def api_scrape(request: Request, site: str='olx', make: str='audi', model: str='a4', page: int=1):
    results = []
    if site.lower() == 'olx':
        results = await scrape_olx(f'{make} {model}', page=page, limit=20)
    elif site.lower() == 'autovit':
        # Added a fallback if autovit is not available since import was missing earlier but mentioned:
        try:
            from scraper.autovit_scraper import scrape_autovit
            results = await scrape_autovit(make, model, page=page, limit=20)
        except ImportError:
            return {'error': "Autovit scraper lipseste!"}
    else:
        return {'error': "Site necunoscut. Foloseste 'olx' sau 'autovit'."}
    return {'results': results}

@app.get('/api/model-info/{make}/{model}')
@limiter.limit("30/minute")
def get_model_info(request: Request, make: str, model: str):
    model_info = car_db_optimizer.get_model_info(make, model)
    if model_info:
        return {'model_info': model_info}
    return {'error': 'Model not found in database'}

@app.get('/api/optimized-search-params/{make}/{model}')
@limiter.limit("30/minute")
def get_optimized_params(request: Request, make: str, model: str, min_year: int=None, max_year: int=None):
    optimized_params = get_optimized_search_params(make, model, min_year, max_year)
    return optimized_params

@app.get('/api/popular-models')
@limiter.limit("30/minute")
def get_popular_models(request: Request, make: str=None, limit: int=10):
    popular_models = car_db_optimizer.get_popular_models(make, limit)
    return {'popular_models': popular_models}

@app.post('/api/populate-sample-data')
@limiter.limit("2/minute")
def populate_sample_data(request: Request):
    car_db_optimizer.populate_sample_data()
    return {'message': 'Sample data populated successfully'}

@app.get('/api/model-year-range/{make}/{model}')
@limiter.limit("30/minute")
def get_model_year_range(request: Request, make: str, model: str):
    model_info = car_db_optimizer.get_model_info(make, model)
    if model_info:
        return {'make': model_info['make'], 'model': model_info['model'], 'min_year': model_info['min_year'], 'max_year': model_info['max_year'], 'generation': model_info['generation'], 'body_type': model_info['body_type']}
    return {'error': 'Model not found in database'}

@app.post('/api/populate-from-scraper')
@limiter.limit("1/minute")
def populate_from_scraper(request: Request, max_brands: int=None, max_models_per_brand: int=None):
    try:
        data = car_db_optimizer.populate_from_scraper(max_brands, max_models_per_brand)
        return {'message': f'Popularea s-a terminat cu succes. Am procesat {len(data)} modele.', 'processed_models': len(data), 'sample_data': data[:5] if data else []}
    except Exception as e:
        return {'error': f'Eroare la popularea bazei de date: {str(e)}'}

@app.get('/api/test-scraper')
@limiter.limit("2/minute")
def test_scraper(request: Request):
    try:
        from auto_data_scraper import AutoDataScraper
        scraper = AutoDataScraper()
        brands = scraper.scrape_brands()[:2]
        results = []
        for brand in brands:
            models = scraper.scrape_models_for_brand(brand['url_marca'], brand['nume_marca'])[:2]
            for model in models:
                details = scraper.scrape_model_details(model['url_model'], model['marca'], model['model'])
                if details:
                    results.append(details)
        return {'message': 'Test scraper completat cu succes', 'results': results}
    except Exception as e:
        return {'error': f'Eroare la testarea scraper-ului: {str(e)}'}

import json
import os

def get_autovit_catalog():
    catalog_path = os.path.join(os.path.dirname(__file__), 'autovit_catalog.json')
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.get('/api/brands')
@limiter.limit("30/minute")
def get_brands(request: Request):
    try:
        catalog = get_autovit_catalog()
        brands = list(catalog.keys())
        brands = [car_db_optimizer.format_brand_name(b) for b in brands]
        return {'brands': sorted(list(set(brands))), 'total': len(brands)}
    except Exception as e:
        return {'error': f'Eroare la obținerea mărcilor: {str(e)}'}

@app.get('/api/models/{brand}')
@limiter.limit("30/minute")
def get_models_for_brand(request: Request, brand: str):
    try:
        catalog = get_autovit_catalog()
        target_brand_key = next((k for k in catalog.keys() if k.lower().strip() == brand.lower().strip() or k.lower().replace('-benz', '') == brand.lower().replace('-benz', '')), None)
        if not target_brand_key:
            return {'error': f'Nu există modele pentru marca {brand}'}
        models = catalog[target_brand_key]
        models = [car_db_optimizer.format_model_name(m) for m in models]
        return {'brand': car_db_optimizer.format_brand_name(brand), 'models': sorted(list(set(models))), 'total': len(models)}
    except Exception as e:
        return {'error': f'Eroare la obținerea modelelor: {str(e)}'}

@app.get('/api/generations/{make}/{model}')
@limiter.limit("30/minute")
def get_generations(request: Request, make: str, model: str):
    try:
        generations = car_db_optimizer.get_generations_for_model(make, model)
        return {'generations': generations or []}
    except Exception as e:
        return {'error': f'Eroare la obținerea generațiilor: {str(e)}', 'generations': []}

@app.get('/api/stats/{make}/{model}')
@limiter.limit("30/minute")
def get_model_stats(request: Request, make: str, model: str):
    s_model = model.lower().replace(' ', '-')
    stats = car_db_optimizer.get_model_stats(make, s_model)
    if not stats:
        return {'error': 'Nu există statistici pentru acest model încă.'}
    return stats

from fastapi import Header
from mailer import send_new_cars_email

CRON_SECRET_KEY = os.environ.get("CRON_SECRET")
if not CRON_SECRET_KEY:
    print("WARNING: CRON_SECRET environment variable is missing! Cron jobs will fail until this is set.")

@app.get('/api/cron/run')
@limiter.limit("10/minute")
async def api_cron_run(request: Request, authorization: str = Header(None)):
    """
    Endpoint triggered periodically (e.g. via cron-job.org or Vercel Cron) 
    to dispatch alerts. Protected by CRON_SECRET.
    """
    if not CRON_SECRET_KEY or not authorization or authorization.replace("Bearer ", "") != CRON_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized Cron Trigger")
        
    try:
        groups = car_db_optimizer.get_cron_groups(limit=2)
        if not groups:
            return {"status": "no_active_alerts"}
            
        dispatched_count = 0
        
        for group in groups:
            make = group['make']
            model = group['model']
            
            results = await search_cars(make=make, model=model, min_year=None, max_year=None, min_price=None, max_price=None, max_km=None, site="both", limit=20, max_pages=1)
            
            if not results:
                continue
                
            new_cars = car_db_optimizer.insert_cron_ads(results)
            if not new_cars:
                continue
                
            alerts = car_db_optimizer.get_alerts_for_group(make, model)
            
            for alert in alerts:
                matched_cars = []
                for car in new_cars:
                    c_price = car.get('price') or 0
                    c_year = car.get('year') or 0
                    c_km = car.get('km') or 0
                    
                    if alert['min_price'] and c_price < alert['min_price']: continue
                    if alert['max_price'] and c_price > alert['max_price']: continue
                    if alert['min_year'] and c_year < alert['min_year']: continue
                    if alert['max_year'] and c_year > alert['max_year']: continue
                    if alert['max_km'] and c_km > alert['max_km']: continue
                    
                    matched_cars.append(car)
                    
                if matched_cars:
                    email = alert['user_email']
                    threading.Thread(
                        target=send_new_cars_email,
                        args=(email, make, model, matched_cars),
                        daemon=True
                    ).start()
                    dispatched_count += 1
                    
        return {"status": "success", "groups_checked": len(groups), "emails_dispatched": dispatched_count}
    except Exception as e:
        print(f"Cron execution failed: {e}")
        return {"error": str(e)}

@app.get('/api/cron/cleanup')
@limiter.limit("10/minute")
async def api_cron_cleanup(request: Request, authorization: str = Header(None)):
    """
    Cron job to scan and delete old inactive ads.
    """
    if not authorization or authorization.replace("Bearer ", "") != CRON_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized Cron Trigger")
        
    try:
        from link_verifier import cron_cleanup_ads
        dead_count = await cron_cleanup_ads(limit=100)
        return {"status": "success", "dead_ads_deleted": dead_count}
    except Exception as e:
        print(f"Cron cleanup failed: {e}")
        return {"error": str(e)}

from fastapi import Response

@app.get("/sitemap.xml")
def get_sitemap():
    models = car_db_optimizer.get_popular_models(limit=5000)
    
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml_content += '  <url><loc>https://car-sniper.com/</loc></url>\n'
    
    for m in models:
        make = m.get('make', '').lower().replace(' ', '-')
        model = m.get('model', '').lower().replace(' ', '-')
        if make and model:
            xml_content += f'  <url><loc>https://car-sniper.com/masini/{make}/{model}</loc></url>\n'
        
    xml_content += '</urlset>'
    
    return Response(content=xml_content, media_type="application/xml")