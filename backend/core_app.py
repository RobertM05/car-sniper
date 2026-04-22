from fastapi import FastAPI, Request
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

@app.get('/api/search')
@limiter.limit("30/minute")
async def api_search(request: Request, make: str, model: str, max_price: int, site: str='both', min_price: int | None=None, max_km: int | None=None, min_year: int | None=None, max_year: int | None=None, min_cc: int | None=None, min_hp: int | None=None, limit: int=200, max_pages: int=5, sort: str='price_asc'):
    calculated_pages = limit // 30 + 2
    if max_pages < calculated_pages:
        max_pages = min(calculated_pages, 20)
    print(f'API CALL: make={make}, model={model}, limit={limit}, max_price={max_price}, min_year={min_year}, max_year={max_year}, site={site}')
    results = await search_cars(make=make, model=model, sort=sort, min_price=min_price, max_price=max_price, min_year=min_year, max_year=max_year, max_km=max_km, min_cc=min_cc, min_hp=min_hp, limit=limit, max_pages=max_pages, site=site)
    reverse = True if 'desc' in sort else False
    key = 'price'
    if 'year' in sort:
        key = 'year'
    elif 'km' in sort:
        key = 'km'
    try:
        results.sort(key=lambda x: int(str(x.get(key, 0)).replace(' ', '').replace('€', '') or 0), reverse=reverse)
        if 'asc' in sort and (not reverse):
            pass
    except:
        pass
    return {'results': results}

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

@app.post('/api/contact')
@limiter.limit("3/minute")
def api_submit_contact(request: Request, req: ContactRequest):
    threading.Thread(
        target=send_contact_email,
        args=(req.name, req.phone, req.company_email, req.company_name, req.has_website, req.website_ip),
        daemon=True
    ).start()
    
    return {'status': 'success'}

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import datetime

JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-fallback-token-sniper-2026")
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
def api_create_alert(request: Request, req: AlertRequest, user_email: str = Depends(verify_token)):
    # Overwrite the request email with the verified token email
    verified_email = user_email
    alert = add_alert(verified_email, req.make, req.model, req.min_price, req.max_price, req.min_year, req.max_year, req.max_km)
    
    threading.Thread(
        target=send_alert_email,
        args=(req.user_email, req.make, req.model, req.max_price),
        daemon=True
    ).start()
    
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