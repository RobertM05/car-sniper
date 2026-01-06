from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading, time
from pydantic import BaseModel
from scraper.olx_scraper import scrape_olx
from scraper.autovit_scraper import scrape_autovit
from functii import search_cars, add_alert, check_alerts
from car_database import car_db_optimizer, get_optimized_search_params
import logging 
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Car Sniper API")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Endpoints ----------------
@app.get("/")
def root():
    return {"message": "Car Sniper API running!"}

@app.get("/api/decode-vin/{vin}")
def decode_vin(vin: str):
    # Exemplu simplificat
    return {"vin": vin, "make": "BMW", "model": "330e", "year": 2019}

import asyncio

@app.get("/api/search")
async def api_search(
    make: str,
    model: str,
    max_price: int,
    site: str = "both",
    min_price: int | None = None,
    max_km: int | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    min_cc: int | None = None,
    min_hp: int | None = None,
    generation: str | None = None,
    limit: int = 50,
    max_pages: int = 5,
    sort: str = "price_asc"
):
    """
    Cauta masini pe OLX sau Autovit si filtreaza dupa max_price
    """
    # Force deeper scan for Autovit/OLX to ensure full results (User requested limit 100 pages)
    if max_pages < 100:
        max_pages = 100
    # Direct Scraping Mode
    # Bypasses database cache to ensure real-time data accuracy.
    
    # Sort parameters are applied post-fetch.
    
    results = await search_cars(
        make=make,
        model=model,
        min_price=min_price,
        max_price=max_price,
        min_year=min_year,
        max_year=max_year,
        max_km=max_km,
        min_cc=min_cc,
        min_hp=min_hp,
        limit=limit,
        max_pages=max_pages,
        site=site,
        generation=generation
    )
    
    # Manual Sort since we are not using SQL
    reverse = True if "desc" in sort else False
    key = "price"
    if "year" in sort: key = "year"
    elif "km" in sort: key = "km"
    
    try:
        results.sort(key=lambda x: int(str(x.get(key, 0)).replace(" ", "").replace("€", "") or 0), reverse=reverse)
        if "asc" in sort and not reverse: # Python default is asc, but my reverse logic was for desc
             # Start.sort default is Ascending. reverse=False is Ascending.
             pass
    except:
        pass

    return {"results": results}

class AlertRequest(BaseModel):
    user_email: str
    make: str
    model: str
    max_price: int
    

@app.post("/api/alert")
def api_create_alert(req: AlertRequest):
    alert = add_alert(req.user_email, req.make, req.model, req.max_price)
    return {"alert": alert}

@app.get("/api/scrape")
async def api_scrape(site: str = "olx", make: str = "audi", model: str = "a4", page: int = 1):
    """
    Scrapeaza OLX sau Autovit
    """
    results = []
    if site.lower() == "olx":
        results = await scrape_olx(f"{make} {model}", page=page, limit=20)
    elif site.lower() == "autovit":
        results = await scrape_autovit(make, model, page=page, limit=20)
    else:
        return {"error": "Site necunoscut. Foloseste 'olx' sau 'autovit'."}

    return {"results": results}

# ---------------- Scheduler alerte ----------------
def run_alerts_scheduler():
    while True:
        logging.info("[Scheduler] Verific alertele...")
        asyncio.run(check_alerts())
        time.sleep(10)

threading.Thread(target=run_alerts_scheduler, daemon=True).start()

# ---------------- Database Optimization Endpoints ----------------

@app.get("/api/model-info/{make}/{model}")
def get_model_info(make: str, model: str):
    """
    Obține informațiile despre un model de mașină din baza de date
    """
    model_info = car_db_optimizer.get_model_info(make, model)
    if model_info:
        return {"model_info": model_info}
    return {"error": "Model not found in database"}

@app.get("/api/optimized-search-params/{make}/{model}")
def get_optimized_params(make: str, model: str, min_year: int = None, max_year: int = None):
    """
    Obține parametrii optimizați de căutare pentru un model
    """
    optimized_params = get_optimized_search_params(make, model, min_year, max_year)
    return optimized_params

@app.get("/api/popular-models")
def get_popular_models(make: str = None, limit: int = 10):
    """
    Obține modelele cele mai căutate
    """
    popular_models = car_db_optimizer.get_popular_models(make, limit)
    return {"popular_models": popular_models}

@app.post("/api/populate-sample-data")
def populate_sample_data():
    """
    Populează baza de date cu date de exemplu
    """
    car_db_optimizer.populate_sample_data()
    return {"message": "Sample data populated successfully"}

@app.get("/api/model-year-range/{make}/{model}")
def get_model_year_range(make: str, model: str):
    """
    Obține intervalul de ani pentru un model specific
    """
    model_info = car_db_optimizer.get_model_info(make, model)
    if model_info:
        return {
            "make": model_info["make"],
            "model": model_info["model"],
            "min_year": model_info["min_year"],
            "max_year": model_info["max_year"],
            "generation": model_info["generation"],
            "body_type": model_info["body_type"]
        }
    return {"error": "Model not found in database"}

@app.post("/api/populate-from-scraper")
def populate_from_scraper(max_brands: int = None, max_models_per_brand: int = None):
    """
    Populează baza de date cu date din scraper-ul auto-data.net
    """
    try:
        data = car_db_optimizer.populate_from_scraper(max_brands, max_models_per_brand)
        return {
            "message": f"Popularea s-a terminat cu succes. Am procesat {len(data)} modele.",
            "processed_models": len(data),
            "sample_data": data[:5] if data else []
        }
    except Exception as e:
        return {"error": f"Eroare la popularea bazei de date: {str(e)}"}

@app.get("/api/test-scraper")
def test_scraper():
    """
    Testează scraper-ul cu primele 2 mărci și 2 modele per marcă
    """
    try:
        from auto_data_scraper import AutoDataScraper
        scraper = AutoDataScraper()
        
        # Testăm doar cu primele 2 mărci și 2 modele per marcă
        brands = scraper.scrape_brands()[:2]
        
        results = []
        for brand in brands:
            models = scraper.scrape_models_for_brand(brand['url_marca'], brand['nume_marca'])[:2]
            for model in models:
                details = scraper.scrape_model_details(
                    model['url_model'], 
                    model['marca'], 
                    model['model']
                )
                if details:
                    results.append(details)
        
        return {
            "message": "Test scraper completat cu succes",
            "results": results
        }
    except Exception as e:
        return {"error": f"Eroare la testarea scraper-ului: {str(e)}"}

@app.get("/api/generations/{make}/{model}")
def get_generations(make: str, model: str):
    """
    Obține toate generațiile disponibile pentru un model
    """
    try:
        generations = car_db_optimizer.get_generations_for_model(make, model)
        return {
            "make": make,
            "model": model,
            "generations": generations
        }
    except Exception as e:
        return {"error": f"Eroare la obținerea generațiilor: {str(e)}"}

@app.get("/api/generation-years/{make}/{model}/{generation}")
def get_generation_years(make: str, model: str, generation: str):
    """
    Obține intervalul de ani pentru o generație specifică
    """
    try:
        min_year, max_year = car_db_optimizer.get_year_range_for_generation(make, model, generation)
        if min_year and max_year:
            return {
                "make": make,
                "model": model,
                "generation": generation,
                "min_year": min_year,
                "max_year": max_year
            }
        else:
            return {"error": f"Generația {generation} nu a fost găsită pentru {make} {model}"}
    except Exception as e:
        return {"error": f"Eroare la obținerea anilor pentru generație: {str(e)}"}

@app.get("/api/optimized-search-with-generation/{make}/{model}")
def get_optimized_params_with_generation(make: str, model: str, 
                                        min_year: int = None, 
                                        max_year: int = None, 
                                        generation: str = None):
    """
    Obține parametrii optimizați de căutare cu suport pentru generații
    """
    try:
        optimized_params = get_optimized_search_params(make, model, min_year, max_year, generation)
        return optimized_params
    except Exception as e:
        return {"error": f"Eroare la obținerea parametrilor optimizați: {str(e)}"}

@app.get("/api/brands")
def get_brands():
    """
    Obține lista cu toate mărcile de mașini disponibile
    """
    try:
        # Încercăm să luăm din DB
        brands = car_db_optimizer.get_all_brands()
        
        # Dacă DB e goală, folosim lista hardcodată
        if not brands:
            brands = [
                "Abarth", "AC", "Acura", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", 
                "Bugatti", "Buick", "Cadillac", "Chevrolet", "Chrysler", "Citroen", "Dacia", 
                "Daewoo", "Daihatsu", "Dodge", "Ferrari", "Fiat", "Ford", "Honda", "Hyundai", 
                "Infiniti", "Isuzu", "Jaguar", "Jeep", "Kia", "Lamborghini", "Lancia", "Land Rover", 
                "Lexus", "Lincoln", "Lotus", "Maserati", "Maybach", "Mazda", "McLaren", "Mercedes", 
                "Mercedes-Benz", "Mini", "Mitsubishi", "Nissan", "Opel", "Peugeot", "Porsche", 
                "Renault", "Rolls-Royce", "Saab", "Seat", "Skoda", "Smart", "Subaru", "Suzuki", 
                "Tesla", "Toyota", "Volkswagen", "Volvo"
            ]
            # Apply formatting to hardcoded list too
            brands = [car_db_optimizer.format_brand_name(b) for b in brands]
        
        return {
            "brands": sorted(list(set(brands))), # Asigurăm unicitatea și sortarea
            "total": len(brands)
        }
    except Exception as e:
        return {"error": f"Eroare la obținerea mărcilor: {str(e)}"}

@app.get("/api/models/{brand}")
def get_models_for_brand(brand: str):
    """
    Obține lista cu modelele pentru o marcă specifică
    """
    try:
        # Încercăm să luăm din DB
        models = car_db_optimizer.get_models(brand)
        
        # Fallback la lista hardcodată dacă nu găsim în DB
        if not models:
            models_by_brand = {
                "audi": ["A1", "A3", "A4", "A5", "A6", "A7", "A8", "Q2", "Q3", "Q4", "Q5", "Q7", "Q8", "TT", "R8"],
                "bmw": ["Seria 1", "Seria 2", "Seria 3", "Seria 4", "Seria 5", "Seria 6", "Seria 7", "Seria 8", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "Z3", "Z4", "i3", "i8"],
                "mercedes": ["A-Class", "B-Class", "C-Class", "CLA", "CLS", "E-Class", "G-Class", "GLA", "GLB", "GLC", "GLE", "GLS", "S-Class", "SL", "SLC", "V-Class"],
                "volkswagen": ["Golf", "Polo", "Passat", "Tiguan", "Touareg", "Arteon", "T-Cross", "T-Roc", "ID.3", "ID.4"],
                "skoda": ["Octavia", "Superb", "Fabia", "Kodiaq", "Kamiq", "Karoq", "Scala"],
                "seat": ["Ibiza", "Leon", "Ateca", "Tarraco", "Arona"],
                "ford": ["Fiesta", "Focus", "Mondeo", "Kuga", "EcoSport", "Edge", "Mustang"],
                "opel": ["Corsa", "Astra", "Insignia", "Crossland", "Grandland", "Mokka"],
                "renault": ["Clio", "Megane", "Kadjar", "Koleos", "Captur", "Talisman"],
                "peugeot": ["208", "308", "508", "2008", "3008", "5008"],
                "citroen": ["C3", "C4", "C5", "C3 Aircross", "C4 Cactus", "C5 Aircross"],
                "dacia": ["Sandero", "Logan", "Duster", "Lodgy", "Dokker"],
                "toyota": ["Yaris", "Corolla", "Camry", "RAV4", "Highlander", "Prius", "C-HR"],
                "honda": ["Civic", "Accord", "CR-V", "HR-V", "Pilot", "Fit"],
                "nissan": ["Micra", "Sentra", "Altima", "Rogue", "Pathfinder", "Murano"],
                "hyundai": ["i10", "i20", "i30", "Elantra", "Sonata", "Tucson", "Santa Fe"],
                "kia": ["Picanto", "Rio", "Ceed", "Optima", "Sportage", "Sorento"],
                "mazda": ["Mazda2", "Mazda3", "Mazda6", "CX-3", "CX-5", "CX-9"],
                "subaru": ["Impreza", "Legacy", "Outback", "Forester", "WRX"],
                "suzuki": ["Swift", "Baleno", "Vitara", "S-Cross", "Jimny"],
                "volvo": ["V40", "S60", "S90", "XC40", "XC60", "XC90"],
                "porsche": ["911", "Boxster", "Cayman", "Panamera", "Macan", "Cayenne", "Taycan"],
                "jaguar": ["XE", "XF", "XJ", "F-PACE", "E-PACE", "I-PACE"],
                "land rover": ["Defender", "Discovery", "Range Rover", "Range Rover Sport", "Range Rover Evoque"],
                "tesla": ["Model S", "Model 3", "Model X", "Model Y"],
                "ferrari": ["488", "F8", "SF90", "Roma", "Portofino"],
                "lamborghini": ["Huracan", "Aventador", "Urus"],
                "maserati": ["Ghibli", "Quattroporte", "Levante", "GranTurismo"],
                "bentley": ["Continental", "Flying Spur", "Bentayga"],
                "rolls-royce": ["Ghost", "Phantom", "Cullinan", "Wraith", "Dawn"],
                "mclaren": ["540C", "570S", "600LT", "720S", "Senna"],
                "aston martin": ["Vantage", "DB11", "DBS", "DBX"],
                "lotus": ["Elise", "Exige", "Evora", "Emira"]
            }
            models = models_by_brand.get(brand.lower(), [])

        if not models:
            # Dacă tot nu am găsit modele (nici în DB, nici hardcodat)
            if not car_db_optimizer.get_model_info(brand, ""): # Verifică sumar
                 return {"error": f"Nu există modele pentru marca {brand}"}
            models = []
        
        # Apply formatting
        models = [car_db_optimizer.format_model_name(m) for m in models]
        
        return {
            "brand": car_db_optimizer.format_brand_name(brand),
            "models": sorted(list(set(models))),
            "total": len(models)
        }
    except Exception as e:
        return {"error": f"Eroare la obținerea modelelor: {str(e)}"}

@app.get("/api/stats/{make}/{model}")
def get_model_stats(make: str, model: str):
    """
    Obține statistici despre un model (preț mediu, an mediu etc.)
    """
    stats = car_db_optimizer.get_model_stats(make, model)
    if not stats:
        return {"error": "Nu există statistici pentru acest model încă."}
    return stats
