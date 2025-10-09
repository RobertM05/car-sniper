from scraper.olx_scraper import scrape_olx
from scraper.autovit_scraper import scrape_autovit
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

    def map_autovit_model(make_text: str, model_text: str) -> str:
        make_lc = (make_text or "").strip().lower()
        model_lc = (model_text or "").strip().lower()
        # BMW numeric models: 320d -> seria-3, 520d -> seria-5
        m = re.match(r"^(x)?(\d)", model_lc)
        if make_lc == "bmw" and m:
            is_x = m.group(1) == "x"
            digit = m.group(2)
            if is_x:
                return f"x{digit}"
            return f"seria-{digit}"
        # default: keep original model
        return model_lc

    # Fetch cars from specified site(s)
    site_lc = (site or "").lower()
    if site_lc == "olx":
        cars = scrape_olx(
            query,
            limit=limit,
            max_price=max_price,
            min_year=min_year,
            max_km=max_km,
        )
    elif site_lc == "autovit":
        model_for_autovit = map_autovit_model(make, model)
        cars = scrape_autovit(
            make,
            model_for_autovit,
            limit=limit,
            max_pages=max_pages,
            max_price=max_price,
            min_year=min_year,
            max_km=max_km,
        )
    elif site_lc == "both":
        cars_olx = scrape_olx(
            query,
            limit=limit,
            max_price=max_price,
            min_year=min_year,
            max_km=max_km,
        )
        model_for_autovit = map_autovit_model(make, model)
        cars_autovit = scrape_autovit(
            make,
            model_for_autovit,
            limit=limit,
            max_pages=max_pages,
            max_price=max_price,
            min_year=min_year,
            max_km=max_km,
        )
        cars = cars_olx + cars_autovit
    else:
        return []

    # Filter cars
    strict_filtered = []
    loose_filtered = []
    for car in cars:
        # price is required; skip if cannot parse
        try:
            price = int(re.sub(r"\D", "", str(car.get("price", ""))))
        except ValueError:
            continue

        # Enforce make/model presence using relaxed matching (ignore spaces/punctuation)
        def normalize(text: str) -> str:
            return re.sub(r"[^a-z0-9]+", "", (text or "").lower())

        title_norm = normalize(str(car.get("title") or car.get("name") or ""))
        link_norm = normalize(str(car.get("link") or car.get("url") or ""))
        make_norm = normalize(make or "")
        model_norm = normalize(model or "")

        # Make must match if provided
        if make_norm and (make_norm not in title_norm and make_norm not in link_norm):
            continue
        # Track strict (model must match) vs loose (model may be missing in title/link)
        model_matches = (not model_norm) or (model_norm in title_norm or model_norm in link_norm)

        # Optional fields parsing
        km_val = None
        year_val = None
        cc_val = None
        hp_val = None
        try:
            km_raw = re.sub(r"\D", "", str(car.get("km", "")))
            km_val = int(km_raw) if km_raw else None
        except ValueError:
            km_val = None
        try:
            year_raw = re.sub(r"\D", "", str(car.get("year", "")))
            year_val = int(year_raw) if year_raw else None
        except ValueError:
            year_val = None
        try:
            cc_raw = re.sub(r"\D", "", str(car.get("cc", "")))
            cc_val = int(cc_raw) if cc_raw else None
        except ValueError:
            cc_val = None
        try:
            hp_raw = re.sub(r"\D", "", str(car.get("hp", "")))
            hp_val = int(hp_raw) if hp_raw else None
        except ValueError:
            hp_val = None

        # Apply filters only when values exist
        if price > max_price:
            continue
        if max_km is not None and km_val is not None and km_val > max_km:
            continue
        if min_year is not None:
            # Exclude if year is missing or below the threshold
            if year_val is None or year_val < min_year:
                continue
        if min_cc is not None and cc_val is not None and cc_val < min_cc:
            continue
        if min_hp is not None and hp_val is not None and hp_val < min_hp:
            continue

        car["price"] = price
        if model_matches:
            strict_filtered.append(car)
        else:
            # For BMW: if user asked for a non-X model (e.g., 320d, 520d), exclude X-series results on fallback
            make_is_bmw = (make_norm == "bmw")
            model_is_x = model_norm.startswith("x") if model_norm else False
            contains_x_series = any(x in title_norm or x in link_norm for x in ["x1","x2","x3","x4","x5","x6","x7"]) if (title_norm or link_norm) else False
            if make_is_bmw and not model_is_x and contains_x_series:
                # skip X-series when searching for non-X BMW models
                continue
            # For BMW numeric series (e.g., 320d -> series 3, 520d -> series 5):
            # Accept if title/link contains series token (RO/EN variants) OR model number (e.g., "520", "520d")
            if make_is_bmw and not model_is_x and model_norm:
                import re as _re
                # model number like 520, 320 extracted from model
                m_num = _re.match(r"(\d{3})", model_norm)
                model_num = m_num.group(1) if m_num else ""
                # series digit like 5, 3 ...
                m_series = _re.match(r"(\d)", model_norm)
                series_digit = m_series.group(1) if m_series else ""
                allowed = False
                if model_num and (model_num in title_norm or model_num in link_norm or (model_num + "d") in title_norm):
                    allowed = True
                if series_digit:
                    series_tokens = [
                        f"seria{series_digit}",
                        f"serie{series_digit}",
                        f"{series_digit}series",
                        f"series{series_digit}",
                    ]
                    if any(tok in title_norm or tok in link_norm for tok in series_tokens):
                        allowed = True
                if not allowed:
                    continue

            # For Audi: if model is not Q-series, exclude Q-series in fallback and require correct A-series when possible
            make_is_audi = (make_norm == "audi")
            model_is_q = model_norm.startswith("q") if model_norm else False
            contains_q_series = any(q in title_norm or q in link_norm for q in ["q2","q3","q4","q5","q7","q8"]) if (title_norm or link_norm) else False
            if make_is_audi and not model_is_q and contains_q_series:
                continue
            if make_is_audi and not model_is_q and model_norm:
                # Require matching A-series token (e.g., A4 -> a4)
                import re as _re2
                m2 = _re2.match(r"([a-z])(\d)", model_norm)
                if m2:
                    series_token = f"{m2.group(1)}{m2.group(2)}"  # e.g., a4
                    if series_token.startswith("a"):
                        has_series = (series_token in title_norm) or (series_token in link_norm)
                        if not has_series:
                            continue

            # For Mercedes: if model is non-G class (e.g., E220d/C220d), exclude SUV GLA/GLB/GLC/GLE/GLS/G* on fallback
            make_is_mercedes = make_norm in ("mercedes", "mercedesbenz", "mercedesbenz")
            # Detect requested class letter from model (c/e/s etc.)
            import re as _re3
            mer_class_match = _re3.match(r"([a-z])", model_norm or "")
            requested_class = mer_class_match.group(1) if mer_class_match else ""
            is_g_requested = requested_class == "g"
            contains_g_suv = any(tok in title_norm or tok in link_norm for tok in ["gla","glb","glc","gle","gls","g55","g63","g500","g350"]) if (title_norm or link_norm) else False
            if make_is_mercedes and not is_g_requested and contains_g_suv:
                continue
            # If we can infer class (c/e/s), require that class to appear as token in title/link (e.g., "clasae", "eclass")
            if make_is_mercedes and requested_class in ("c","e","s"):
                class_tokens = [f"clasa{requested_class}", f"{requested_class}class"]
                has_class = any(tok in title_norm or tok in link_norm for tok in class_tokens)
                if not has_class:
                    continue
            loose_filtered.append(car)

    # Prefer strict matches; if none and model requested, fall back to make-only matches
    if strict_filtered:
        return strict_filtered
    if model:
        return loose_filtered
    return strict_filtered

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