import sys
import os
import json
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

from car_database import car_db_optimizer
from core_app import calculate_deal_scores
import re

def main():
    with car_db_optimizer.get_connection() as c:
        cur = c.cursor()
        cur.execute('SELECT DISTINCT make, model FROM ads WHERE make IS NOT NULL AND model IS NOT NULL LIMIT 10')
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
                        bugs.append({"severity": "High", "type": "Filter Violation", "desc": f"Price filter violation for {brand} {model}. Expected [{f_min_p}, {f_max_p}], got {p}.", "ad_id": r['id']})

            # Deal Score & Data Integrity
            stats = car_db_optimizer.get_model_stats(brand, norm_model.replace(' ', '-'))
            peer_pool = car_db_optimizer.get_active_ads_for_make_model(brand, norm_model)
            scored_ads = calculate_deal_scores(ads, stats or {}, peer_pool=peer_pool)
            
            for ad in scored_ads:
                p = int(''.join(filter(str.isdigit, str(ad.get('price', '0')))))
                if p == 0:
                    bugs.append({"severity": "High", "type": "Data Integrity", "desc": f"Price is 0 or missing for {brand} {model}.", "ad_id": ad['id']})
                if ad.get('deal_score') is None:
                    bugs.append({"severity": "Medium", "type": "Deal Score", "desc": f"deal_score is None for {brand} {model}.", "ad_id": ad['id']})
                if not ad.get('link'):
                    bugs.append({"severity": "High", "type": "Data Integrity", "desc": f"Missing link for ad {ad['id']}.", "ad_id": ad['id']})

    with open('/Users/robert/car-sniper/qa_bugs_actual.json', 'w') as f:
        json.dump(bugs, f, indent=2)
    print(f"Found {len(bugs)} issues. Saved to qa_bugs_actual.json.")

if __name__ == '__main__':
    main()
