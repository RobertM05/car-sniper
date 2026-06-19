import sys
import os
import json
from dotenv import load_dotenv

# Load env FIRST
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

from car_database import car_db_optimizer
from core_app import calculate_deal_scores
import re

def main():
    with car_db_optimizer.get_connection() as c:
        cur = c.cursor()
        cur.execute('SELECT DISTINCT make, model FROM ads WHERE make IS NOT NULL AND model IS NOT NULL')
        rows = cur.fetchall()
        
    brands_models = {}
    for r in rows:
        mk = r['make'].strip()
        md = r['model'].strip()
        if not mk or not md: continue
        if mk not in brands_models:
            brands_models[mk] = set()
        brands_models[mk].add(md)
        
    bugs = []
    
    print(f"Testing {len(brands_models)} brands...")

    for brand, models in brands_models.items():
        for model in models:
            norm_model = car_db_optimizer.normalize_model_name(brand, model)
            
            # 1. Base search
            ads = car_db_optimizer.search_ads_db(make=brand, model=norm_model, limit=100)
            if not ads:
                continue

            prices = []
            years = []
            kms = []
            for ad in ads:
                p_str = str(ad.get('price', '0'))
                p_digits = ''.join(filter(str.isdigit, p_str))
                if p_digits: prices.append(int(p_digits))
                
                if ad.get('year'): years.append(ad['year'])
                if ad.get('km'): kms.append(ad['km'])

            min_p = min(prices) if prices else 1000
            max_p = max(prices) if prices else 50000
            min_y = min(years) if years else 2000
            max_y = max(years) if years else 2024
            min_k = min(kms) if kms else 10000
            max_k = max(kms) if kms else 200000

            # Price Filter Test
            f_min_p = min_p + (max_p - min_p) // 4
            f_max_p = max_p - (max_p - min_p) // 4
            if f_min_p < f_max_p:
                res = car_db_optimizer.search_ads_db(make=brand, model=norm_model, min_price=f_min_p, max_price=f_max_p, limit=50)
                for r in res:
                    p = int(''.join(filter(str.isdigit, str(r.get('price', '0')))))
                    if p < f_min_p or p > f_max_p:
                        bugs.append({
                            "severity": "High", "type": "Filter Violation",
                            "desc": f"Price filter violation for {brand} {model}. Expected [{f_min_p}, {f_max_p}], got {p}.",
                            "ad_id": r['id']
                        })

            # Year Filter Test
            f_min_y = min_y + (max_y - min_y) // 4
            f_max_y = max_y - (max_y - min_y) // 4
            if f_min_y <= f_max_y:
                res = car_db_optimizer.search_ads_db(make=brand, model=norm_model, min_year=f_min_y, max_year=f_max_y, limit=50)
                for r in res:
                    y = r.get('year', 0)
                    if y < f_min_y or y > f_max_y:
                        bugs.append({
                            "severity": "High", "type": "Filter Violation",
                            "desc": f"Year filter violation for {brand} {model}. Expected [{f_min_y}, {f_max_y}], got {y}.",
                            "ad_id": r['id']
                        })

            # Km Filter Test
            f_max_k = max_k - (max_k - min_k) // 4
            if f_max_k > 0:
                res = car_db_optimizer.search_ads_db(make=brand, model=norm_model, max_km=f_max_k, limit=50)
                for r in res:
                    k = r.get('km', 0)
                    if k > f_max_k:
                        bugs.append({
                            "severity": "High", "type": "Filter Violation",
                            "desc": f"Km filter violation for {brand} {model}. Expected max {f_max_k}, got {k}.",
                            "ad_id": r['id']
                        })

            # Case sensitivity Test
            res_diff_case = car_db_optimizer.search_ads_db(make=brand.upper(), model=norm_model.upper(), limit=50)
            if len(ads) > 0 and len(res_diff_case) == 0:
                bugs.append({
                    "severity": "Medium", "type": "Case Sensitivity",
                    "desc": f"Case sensitivity issue for {brand} {model}: UPPERCASE search returned 0 results.",
                    "ad_id": None
                })

            # Deal Score & Data Integrity
            stats = car_db_optimizer.get_model_stats(brand, norm_model.replace(' ', '-'))
            peer_pool = car_db_optimizer.get_active_ads_for_make_model(brand, norm_model)
            scored_ads = calculate_deal_scores(ads, stats or {}, peer_pool=peer_pool)
            
            for ad in scored_ads:
                # Price = 0
                p = int(''.join(filter(str.isdigit, str(ad.get('price', '0')))))
                if p == 0:
                    bugs.append({
                        "severity": "High", "type": "Data Integrity",
                        "desc": f"Price is 0 or missing for {brand} {model}.",
                        "ad_id": ad['id']
                    })
                
                # Deal Score
                if ad.get('deal_score') is None:
                    bugs.append({
                        "severity": "Medium", "type": "Deal Score",
                        "desc": f"deal_score is None for {brand} {model}.",
                        "ad_id": ad['id']
                    })
                
                # Match Make/Model
                ad_make = str(ad.get('make', '')).lower()
                ad_model = str(ad.get('model', '')).lower()
                ad_title = str(ad.get('title', '')).lower()
                
                brand_lc = brand.lower()
                model_lc = norm_model.lower()

                if brand_lc not in ad_make and ad_make not in brand_lc:
                    bugs.append({
                        "severity": "Medium", "type": "Mismatch Make",
                        "desc": f"Make mismatch: requested '{brand}', got '{ad.get('make')}'.",
                        "ad_id": ad['id']
                    })
                
                if len(model_lc) <= 2:
                    match_model = re.search(rf'(^|\s|-){model_lc}(\s|$|-)', ad_model)
                    match_title = re.search(rf'(^|\s|-){model_lc}\s?\d{{2,3}}', ad_title)
                    if not match_model and not match_title:
                        # Allow if model_lc is in ad_model exactly
                        if model_lc != ad_model.strip():
                            bugs.append({
                                "severity": "High", "type": "Mismatch Model",
                                "desc": f"Strict model mismatch: requested '{model_lc}', got model '{ad_model}', title '{ad_title}'.",
                                "ad_id": ad['id']
                            })
                else:
                    if model_lc not in ad_model and model_lc not in ad_title:
                        bugs.append({
                            "severity": "High", "type": "Mismatch Model",
                            "desc": f"Model mismatch: requested '{model_lc}', got model '{ad_model}', title '{ad_title}'.",
                            "ad_id": ad['id']
                        })
                
                # Link missing
                if not ad.get('link'):
                    bugs.append({
                        "severity": "High", "type": "Data Integrity",
                        "desc": f"Missing link for ad {ad['id']}.",
                        "ad_id": ad['id']
                    })
                
                # Year invalid
                y = ad.get('year', 0)
                if not y or y < 1900 or y > 2026:
                    bugs.append({
                        "severity": "Low", "type": "Data Integrity",
                        "desc": f"Invalid year {y} for {brand} {model}.",
                        "ad_id": ad['id']
                    })

    # Save bugs to json so we can format them
    with open('qa_bugs.json', 'w') as f:
        json.dump(bugs, f, indent=2)
    print(f"Found {len(bugs)} issues. Saved to qa_bugs.json.")

if __name__ == '__main__':
    main()
