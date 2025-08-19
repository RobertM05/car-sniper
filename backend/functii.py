from .scraper.olx_scraper import scrape_olx
from .scraper.autovit_scraper import scrape_autovit
import re


def search_cars(
    make: str,
    model: str,
    max_price: int,
    site: str = "olx",
    *,
    max_km: int | None = None,
    min_year: int | None = None,
    min_cc: int | None = None,
    min_hp: int | None = None,
    limit: int = 50,
    max_pages: int = 5,
):
    cars = []
    query = f"{make} {model}"
    
    if site.lower() == "olx":
        cars = scrape_olx(query, limit=limit)
    elif site.lower() == "autovit":
        cars = scrape_autovit(make, model, limit=limit, max_pages=max_pages)
    else:
        return[]
    filtered = []
    for car in cars:
        # Keep only digits from price text to be resilient to spaces, currency symbols, etc.
        digits_only = re.sub(r"\D", "", str(car.get("price", "")))
        if not digits_only:
            continue
        try:
            price = int(digits_only)
        except ValueError:
            continue
        if price > max_price:
            continue

        # Optional filters
        if max_km is not None:
            km_digits = re.sub(r"\D", "", str(car.get("km", "")))
            if km_digits and km_digits.isdigit():
                if int(km_digits) > max_km:
                    continue

        if min_year is not None:
            year_val = car.get("year")
            if isinstance(year_val, int):
                if year_val < min_year:
                    continue
            else:
                year_digits = re.sub(r"\D", "", str(year_val or ""))
                if year_digits.isdigit() and int(year_digits) < min_year:
                    continue

        if min_cc is not None:
            cc_digits = re.sub(r"\D", "", str(car.get("cc", "")))
            if cc_digits and cc_digits.isdigit():
                if int(cc_digits) < min_cc:
                    continue

        if min_hp is not None:
            hp_digits = re.sub(r"\D", "", str(car.get("hp", "")))
            if hp_digits and hp_digits.isdigit():
                if int(hp_digits) < min_hp:
                    continue

        car["price"] = price
        filtered.append(car)
    return filtered

alerts = []
def add_alert(user_email: str, make: str, model: str, max_price: int):
    alert = {"user_email": user_email, "make": make, "model": model, "max_price": max_price}
    alerts.append(alert)
    return alert

def check_alerts():
    for alert in alerts:
        cars = search_cars(alert["make"], alert["model"], alert["max_price"])
        for car in cars:
            print(f"ALERT: {alert['user_email']} → {car['title']} la {car['price']}")