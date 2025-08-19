from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading, time
from pydantic import BaseModel
from .scraper.olx_scraper import scrape_olx
from .scraper.autovit_scraper import scrape_autovit
from .functii import search_cars, add_alert, alerts, check_alerts
import logging 
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Car Sniper API")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # pentru development
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

@app.get("/api/search")
def api_search(
    make: str,
    model: str,
    max_price: int,
    site: str = "olx",
    max_km: int | None = None,
    min_year: int | None = None,
    min_cc: int | None = None,
    min_hp: int | None = None,
    limit: int = 50,
    max_pages: int = 5,
):
    """
    Cauta masini pe OLX sau Autovit si filtreaza dupa max_price
    """
    results = search_cars(
        make,
        model,
        max_price,
        site,
        max_km=max_km,
        min_year=min_year,
        min_cc=min_cc,
        min_hp=min_hp,
        limit=limit,
        max_pages=max_pages,
    )
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
def api_scrape(site: str = "olx", make: str = "audi", model: str = "a4", page: int = 1):
    """
    Scrapeaza OLX sau Autovit
    """
    results = []
    if site.lower() == "olx":
        results = scrape_olx(f"{make} {model}", page=page, limit=20)
    elif site.lower() == "autovit":
        results = scrape_autovit(make, model, page=page, limit=20)
    else:
        return {"error": "Site necunoscut. Foloseste 'olx' sau 'autovit'."}

    return {"results": results}

# ---------------- Scheduler alerte ----------------
def run_alerts_scheduler():
    while True:
        logging.info("[Scheduler] Verific alertele...")
        check_alerts()
        time.sleep(10)

threading.Thread(target=run_alerts_scheduler, daemon=True).start()
