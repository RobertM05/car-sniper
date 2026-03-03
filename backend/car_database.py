import sqlite3
import json
from typing import Dict, List, Optional, Tuple
import re
import bcrypt
import os

class CarDatabaseOptimizer:

    def __init__(self, db_path: str=None):
        if db_path is None:
            if os.environ.get("VERCEL"):
                self.db_path = "/tmp/db.sqlite"
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.db_path = os.path.join(base_dir, 'database', 'db.sqlite')
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        else:
            self.db_path = db_path
        self.init_database()

    def format_brand_name(self, brand: str) -> str:
        brand = brand.lower().strip()
        special_cases = {'bmw': 'BMW', 'vw': 'VW', 'volkswagen': 'Volkswagen', 'mercedes': 'Mercedes-Benz', 'mercedes-benz': 'Mercedes-Benz', 'mercedesbenz': 'Mercedes-Benz', 'mg': 'MG', 'gmc': 'GMC', 'acura': 'Acura', 'alfa romeo': 'Alfa Romeo', 'aston martin': 'Aston Martin', 'land rover': 'Land Rover', 'range rover': 'Range Rover', 'rolls-royce': 'Rolls-Royce', 'seat': 'SEAT', 'fiat': 'FIAT', 'mini': 'MINI'}
        return special_cases.get(brand, brand.title())

    def format_model_name(self, model: str) -> str:
        model = model.lower().strip()
        model = re.sub('\\b(19|20)\\d{2}\\b', '', model).strip()
        model = model.replace('-', ' ')
        words = model.split()
        formatted_words = []
        for word in words:
            if word in ['bmw', 'vw', 'gti', 'gtd', 'amg', 'rs', 'wrx', 'sti', 'cr-v', 'hr-v', 'rav4', 'mx-5', 'cx-3', 'cx-5', 'cx-30', 'cx-60', 'cx-90']:
                formatted_words.append(word.upper())
            elif word.startswith('mk') and word[2:].isdigit():
                formatted_words.append('Mk' + word[2:])
            elif word in ['ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']:
                formatted_words.append(word.upper())
            elif word in ['cdi', 'tdi', 'tfsi', 'tsi', 'fsi', 'd', 'i', 'e', 'h']:
                formatted_words.append(word.upper())
            elif word == 'seria':
                formatted_words.append('Seria')
            elif word == 'clasa':
                formatted_words.append('Clasa')
            elif word == 'class':
                formatted_words.append('Class')
            else:
                formatted_words.append(word.title())
        formatted_model = ' '.join(formatted_words)
        if 'Seria ' in formatted_model and formatted_model[-1].isdigit():
            pass
        return formatted_model

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS car_models (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                make TEXT NOT NULL,\n                model TEXT NOT NULL,\n                model_variants TEXT,  -- JSON cu variantele modelului\n                min_year INTEGER,\n                max_year INTEGER,\n                generation TEXT,      -- Generația modelului\n                body_type TEXT,      -- sedan, suv, hatchback, etc.\n                engine_types TEXT,   -- JSON cu tipurile de motor\n                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                UNIQUE(make, model)\n            )\n        ')
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS search_stats (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                make TEXT,\n                model TEXT,\n                search_count INTEGER DEFAULT 1,\n                last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                avg_price REAL,\n                avg_year REAL,\n                avg_km REAL\n            )\n        ')
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS alerts (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                user_email TEXT NOT NULL,\n                make TEXT NOT NULL,\n                model TEXT NOT NULL,\n                min_price INTEGER,\n                max_price INTEGER,\n                min_year INTEGER,\n                max_year INTEGER,\n                max_km INTEGER,\n                active BOOLEAN DEFAULT 1,\n                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                last_checked TIMESTAMP\n            )\n        ')
        cursor.execute("\n            CREATE TABLE IF NOT EXISTS ads (\n                id TEXT PRIMARY KEY,       -- Unic, bazat pe link hash sau ID site\n                source TEXT,               -- OLX, Autovit\n                title TEXT,\n                price INTEGER,\n                currency TEXT DEFAULT 'EUR',\n                link TEXT UNIQUE,\n                image TEXT,\n                make TEXT,\n                model TEXT,\n                year INTEGER,\n                km INTEGER,\n                fuel TEXT,\n                transmission TEXT,\n                body_type TEXT,\n                city TEXT,\n                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                active BOOLEAN DEFAULT 1\n            )\n        ")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ads_make_model ON ads(make, model)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ads_price ON ads(price)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ads_link ON ads(link)')
        conn.commit()
        conn.close()

    def delete_ad(self, ad_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM ads WHERE id = ?', (ad_id,))
        conn.commit()
        conn.close()

    def upsert_ad(self, ad_data: dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        import hashlib
        link = ad_data.get('link', '')
        if not ad_data.get('id'):
            ad_id = hashlib.md5(link.encode()).hexdigest()
        else:
            ad_id = ad_data['id']
        try:
            price_val = int(ad_data.get('price', 0))
        except:
            price_val = 0
        cursor.execute('\n            INSERT INTO ads (\n                id, source, title, price, link, image, make, model, year, km, \n                fuel, transmission, body_type, city, last_seen, active, updated_at\n            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP)\n            ON CONFLICT(link) DO UPDATE SET\n                price = excluded.price,\n                last_seen = CURRENT_TIMESTAMP,\n                active = 1,\n                updated_at = CURRENT_TIMESTAMP,\n                image = COALESCE(excluded.image, ads.image) \n        ', (ad_id, ad_data.get('subsource') or ad_data.get('source', 'Unknown'), ad_data.get('title'), price_val, link, ad_data.get('image'), ad_data.get('make'), ad_data.get('model'), ad_data.get('year'), ad_data.get('km'), ad_data.get('fuel'), ad_data.get('transmission'), ad_data.get('body_type'), ad_data.get('city')))
        conn.commit()
        conn.close()
        return ad_id

    def search_ads_db(self, make: str, model: str, min_price=None, max_price=None, min_year=None, max_year=None, min_km=None, max_km=None, limit=100, sort_by='price', order='asc') -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = 'SELECT * FROM ads WHERE active = 1'
        params = []
        if make:
            query += ' AND make LIKE ?'
            params.append(f'%{make}%')
        if model:
            query += ' AND (model LIKE ? OR title LIKE ?)'
            params.append(f'%{model}%')
            params.append(f'%{model}%')
        if min_price:
            query += ' AND price >= ?'
            params.append(min_price)
        if max_price:
            query += ' AND price <= ?'
            params.append(max_price)
        if min_year:
            query += ' AND year >= ?'
            params.append(min_year)
        if max_year:
            query += ' AND year <= ?'
            params.append(max_year)
        if max_km:
            query += ' AND km <= ?'
            params.append(max_km)
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        ads = []
        for r in rows:
            d = dict(r)
            d['price'] = f"{d['price']} €"
            ads.append(d)
        conn.close()
        return ads

    def deactivate_stale_ads(self, hours_threshold=24):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE ads SET active = 0 WHERE last_seen < datetime('now', '-{hours_threshold} hours')")
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count

    def add_car_model(self, make: str, model: str, min_year: int=None, max_year: int=None, generation: str=None, body_type: str=None, model_variants: List[str]=None, engine_types: List[str]=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        variants_json = json.dumps(model_variants) if model_variants else None
        engines_json = json.dumps(engine_types) if engine_types else None
        cursor.execute('\n            INSERT OR REPLACE INTO car_models \n            (make, model, model_variants, min_year, max_year, generation, body_type, engine_types, updated_at)\n            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)\n        ', (make.lower(), model.lower(), variants_json, min_year, max_year, generation, body_type, engines_json))
        conn.commit()
        conn.close()

    def get_model_info(self, make: str, model: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('\n            SELECT make, model, model_variants, min_year, max_year, generation, body_type, engine_types\n            FROM car_models \n            WHERE make = ? AND model = ?\n        ', (make.lower(), model.lower()))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {'make': result[0], 'model': result[1], 'model_variants': json.loads(result[2]) if result[2] else [], 'min_year': result[3], 'max_year': result[4], 'generation': result[5], 'body_type': result[6], 'engine_types': json.loads(result[7]) if result[7] else []}
        return None

    def get_generations_for_model(self, make: str, model: str) -> List[Dict]:
        make_normalized = make.lower().strip()
        model_normalized = model.lower().strip()
        generations = self._get_model_generations_from_db(make_normalized, model_normalized)
        if generations:
            return generations
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('\n            SELECT generation, min_year, max_year, body_type, engine_types\n            FROM car_models \n            WHERE make = ? AND model = ?\n        ', (make_normalized, model_normalized))
        result = cursor.fetchone()
        conn.close()
        if result and result[0]:
            return [{'generation': result[0], 'min_year': result[1], 'max_year': result[2], 'body_type': result[3], 'engine_types': json.loads(result[4]) if result[4] else []}]
        return []

    def _get_model_generations_from_db(self, make: str, model: str) -> List[Dict]:
        if make.lower() == 'bmw' and any((x in model.lower() for x in ['seria-3', 'seria3', '3', 'seria 3'])):
            return [{'generation': 'E90', 'min_year': 2005, 'max_year': 2012, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'F30', 'min_year': 2012, 'max_year': 2019, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'G20', 'min_year': 2019, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() == 'bmw' and any((x in model.lower() for x in ['seria-5', 'seria5', '5', 'seria 5'])):
            return [{'generation': 'E60', 'min_year': 2003, 'max_year': 2010, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'F10', 'min_year': 2010, 'max_year': 2017, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'G30', 'min_year': 2017, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() == 'audi' and model.lower() in ['a4', 'a-4']:
            return [{'generation': 'B7', 'min_year': 2004, 'max_year': 2008, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'B8', 'min_year': 2008, 'max_year': 2016, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'B9', 'min_year': 2016, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() in ['mercedes', 'mercedes-benz'] and any((x in model.lower() for x in ['c', 'c-class', 'cclass', 'c class'])):
            return [{'generation': 'W204', 'min_year': 2007, 'max_year': 2014, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'W205', 'min_year': 2014, 'max_year': 2021, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'W206', 'min_year': 2021, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() == 'volkswagen' and model.lower() in ['golf', 'golf-7', 'golf-8']:
            return [{'generation': 'Mk5', 'min_year': 2003, 'max_year': 2008, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol']}, {'generation': 'Mk6', 'min_year': 2008, 'max_year': 2012, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol']}, {'generation': 'Mk7', 'min_year': 2012, 'max_year': 2019, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol']}, {'generation': 'Mk8', 'min_year': 2019, 'max_year': 2024, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        return []

    def get_year_range_for_generation(self, make: str, model: str, generation: str) -> Tuple[int, int]:
        hardcoded_gens = {'W203': (2000, 2007), 'W204': (2007, 2015), 'W205': (2014, 2021), 'W206': (2021, 2025), 'W211': (2002, 2009), 'W212': (2009, 2016), 'W213': (2016, 2024), 'W221': (2005, 2013), 'W222': (2013, 2021), 'E46': (1998, 2006), 'E90': (2005, 2012), 'F30': (2012, 2019), 'G20': (2019, 2025), 'E60': (2003, 2010), 'F10': (2010, 2017), 'G30': (2017, 2024), 'B7': (2004, 2009), 'B8': (2008, 2016), 'B9': (2015, 2025), 'C6': (2004, 2011), 'C7': (2011, 2018), 'C8': (2018, 2025), 'MK5': (2003, 2009), 'MK6': (2008, 2013), 'MK7': (2012, 2020), 'MK8': (2019, 2025)}
        requested = generation.upper().replace(' ', '').replace('-', '')
        for (key, (min_y, max_y)) in hardcoded_gens.items():
            if key == requested:
                return (min_y, max_y)
        generations = self.get_generations_for_model(make, model)
        if generations:
            for gen in generations:
                gen_name = gen['generation'].upper()
                target_gen = generation.upper()
                if gen_name == target_gen:
                    return (gen['min_year'], gen['max_year'])
        return (None, None)

    def get_optimized_year_range(self, make: str, model: str, user_min_year: int=None, user_max_year: int=None) -> Tuple[int, int]:
        model_info = self.get_model_info(make, model)
        if not model_info:
            return (user_min_year, user_max_year)
        db_min_year = model_info.get('min_year')
        db_max_year = model_info.get('max_year')
        optimized_min = user_min_year
        optimized_max = user_max_year
        if db_min_year and db_max_year:
            if not user_min_year:
                optimized_min = db_min_year
            else:
                optimized_min = max(user_min_year, db_min_year)
            if not user_max_year:
                optimized_max = db_max_year
            else:
                optimized_max = min(user_max_year, db_max_year)
        return (optimized_min, optimized_max)

    def normalize_model_name(self, make: str, model: str) -> str:
        make_lc = make.lower().strip()
        model_lc = model.lower().strip()
        if make_lc == 'bmw':
            m = re.match('^(x)?(\\d)', model_lc)
            if m:
                is_x = m.group(1) == 'x'
                digit = m.group(2)
                if is_x:
                    return f'x{digit}'
                return f'seria-{digit}'
        elif make_lc == 'audi':
            m = re.match('^([aq])(\\d+)', model_lc)
            if m:
                series = m.group(1)
                number = m.group(2)
                return f'{series}{number}'
        elif make_lc in ['mercedes', 'mercedesbenz']:
            m = re.match('^([a-z])', model_lc)
            if m:
                return m.group(1)
        return model_lc

    def update_search_stats(self, make: str, model: str, avg_price: float=None, avg_year: float=None, avg_km: float=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, search_count FROM search_stats WHERE make = ? AND model = ? ORDER BY id DESC LIMIT 1', (make.lower(), model.lower()))
        row = cursor.fetchone()
        if row:
            cursor.execute('\n                UPDATE search_stats \n                SET search_count = search_count + 1,\n                    last_searched = CURRENT_TIMESTAMP,\n                    avg_price = ?, avg_year = ?, avg_km = ?\n                WHERE id = ?\n            ', (avg_price, avg_year, avg_km, row[0]))
        else:
            cursor.execute('\n                INSERT INTO search_stats \n                (make, model, search_count, last_searched, avg_price, avg_year, avg_km)\n                VALUES (?, ?, 1, CURRENT_TIMESTAMP, ?, ?, ?)\n            ', (make.lower(), model.lower(), avg_price, avg_year, avg_km))
        conn.commit()
        conn.close()

    def get_popular_models(self, make: str=None, limit: int=10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if make:
            cursor.execute('\n                SELECT make, model, search_count, avg_price, avg_year, avg_km\n                FROM search_stats \n                WHERE make = ?\n                ORDER BY search_count DESC, last_searched DESC\n                LIMIT ?\n            ', (make.lower(), limit))
        else:
            cursor.execute('\n                SELECT make, model, search_count, avg_price, avg_year, avg_km\n                FROM search_stats \n                ORDER BY search_count DESC, last_searched DESC\n                LIMIT ?\n            ', (limit,))
        results = cursor.fetchall()
        conn.close()
        return [{'make': r[0], 'model': r[1], 'search_count': r[2], 'avg_price': r[3], 'avg_year': r[4], 'avg_km': r[5]} for r in results]

    def get_model_stats(self, make: str, model: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('\n            SELECT make, model, search_count, avg_price, avg_year, avg_km, last_searched\n            FROM search_stats \n            WHERE make = ? AND model = ?\n            ORDER BY id DESC LIMIT 1\n        ', (make.lower(), model.lower()))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {'make': result[0], 'model': result[1], 'search_count': result[2], 'avg_price': result[3], 'avg_year': result[4], 'avg_km': result[5], 'last_searched': result[6]}
        return None

    def populate_sample_data(self):
        sample_models = [('bmw', 'seria-3', 2012, 2024, 'F30/G20', 'sedan', ['320d', '330d', '320i', '330i'], ['diesel', 'petrol']), ('bmw', 'seria-5', 2010, 2024, 'F10/G30', 'sedan', ['520d', '530d', '520i', '530i'], ['diesel', 'petrol']), ('bmw', 'x3', 2010, 2024, 'F25/G01', 'suv', ['x3', 'xdrive30d', 'xdrive20d'], ['diesel', 'petrol']), ('bmw', 'x5', 2006, 2024, 'E70/F15/G05', 'suv', ['x5', 'xdrive30d', 'xdrive40d'], ['diesel', 'petrol']), ('audi', 'a4', 2008, 2024, 'B8/B9', 'sedan', ['a4', 'avant', 'allroad'], ['diesel', 'petrol']), ('audi', 'a6', 2011, 2024, 'C7/C8', 'sedan', ['a6', 'avant', 'allroad'], ['diesel', 'petrol']), ('audi', 'q5', 2008, 2024, '8R/FY', 'suv', ['q5', 'sq5'], ['diesel', 'petrol']), ('audi', 'q7', 2006, 2024, '4L/4M', 'suv', ['q7', 'sq7'], ['diesel', 'petrol']), ('mercedes', 'c', 2007, 2024, 'W204/W205', 'sedan', ['c220d', 'c250d', 'c200', 'c250'], ['diesel', 'petrol']), ('mercedes', 'e', 2009, 2024, 'W212/W213', 'sedan', ['e220d', 'e250d', 'e200', 'e250'], ['diesel', 'petrol']), ('mercedes', 'g', 2005, 2024, 'W463', 'suv', ['g350d', 'g500', 'g63'], ['diesel', 'petrol']), ('volkswagen', 'golf', 2008, 2024, 'Mk6/Mk7/Mk8', 'hatchback', ['golf', 'gti', 'gtd'], ['diesel', 'petrol']), ('volkswagen', 'passat', 2010, 2024, 'B7/B8', 'sedan', ['passat', 'passat-variant'], ['diesel', 'petrol']), ('volkswagen', 'tiguan', 2007, 2024, '5N/AD1', 'suv', ['tiguan', 'tiguan-allspace'], ['diesel', 'petrol']), ('skoda', 'octavia', 2013, 2024, 'Mk3/Mk4', 'sedan', ['octavia', 'octavia-combi'], ['diesel', 'petrol']), ('skoda', 'superb', 2008, 2024, '3T/3V', 'sedan', ['superb', 'superb-combi'], ['diesel', 'petrol']), ('skoda', 'kodiaq', 2017, 2024, 'NS', 'suv', ['kodiaq'], ['diesel', 'petrol'])]
        for model_data in sample_models:
            self.add_car_model(*model_data)

    def populate_from_scraper(self, max_brands: int=None, max_models_per_brand: int=None):
        from auto_data_scraper import AutoDataScraper
        scraper = AutoDataScraper(self)
        print('Încep popularea bazei de date cu date din auto-data.net...')
        data = scraper.scrape_all_data(max_brands, max_models_per_brand)
        print(f'Popularea s-a terminat. Am procesat {len(data)} modele.')
        return data

    def add_alert(self, user_email: str, make: str, model: str, min_price: int=None, max_price: int=None, min_year: int=None, max_year: int=None, max_km: int=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('\n            INSERT INTO alerts (user_email, make, model, min_price, max_price, min_year, max_year, max_km, active, last_checked)\n            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)\n        ', (user_email, make, model, min_price, max_price, min_year, max_year, max_km))
        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {'id': alert_id, 'user_email': user_email, 'make': make, 'model': model, 'min_price': min_price, 'max_price': max_price, 'min_year': min_year, 'max_year': max_year, 'max_km': max_km, 'active': 1}

    def deactivate_alert(self, alert_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE alerts SET active = 0 WHERE id = ?', (alert_id,))
        conn.commit()
        conn.close()

    def get_alerts(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alerts')
        rows = cursor.fetchall()
        alerts = []
        for row in rows:
            alerts.append(dict(row))
        conn.close()
        return alerts

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def register_user(self, email: str, password: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            hashed = self._hash_password(password)
            cursor.execute('INSERT INTO users (email, hashed_password) VALUES (?, ?)', (email, hashed))
            user_id = cursor.lastrowid
            conn.commit()
            return {"success": True, "id": user_id, "email": email}
        except sqlite3.IntegrityError:
            return {"success": False, "error": "Email already registered"}
        finally:
            conn.close()

    def verify_login(self, email: str, password: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, email, hashed_password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return {"success": False, "error": "User not found"}
            
        try:
            if bcrypt.checkpw(password.encode('utf-8'), user["hashed_password"].encode('utf-8')):
                return {"success": True, "id": user["id"], "email": user["email"]}
            else:
                return {"success": False, "error": "Incorrect password"}
        except ValueError:
            return {"success": False, "error": "Incorrect password or outdated security hash"}

    def get_all_brands(self) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT make FROM car_models ORDER BY make ASC')
        rows = cursor.fetchall()
        brands = [self.format_brand_name(row[0]) for row in rows if row[0]]
        conn.close()
        return sorted(list(set(brands)))

    def get_models(self, make: str) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT model FROM car_models WHERE make = ? ORDER BY model ASC', (make.lower(),))
        rows = cursor.fetchall()
        models = [self.format_model_name(row[0]) for row in rows if row[0]]
        conn.close()
        return sorted(list(set(models)))
car_db_optimizer = CarDatabaseOptimizer()

def get_optimized_search_params(make: str, model: str, user_min_year: int=None, user_max_year: int=None) -> Dict:
    (optimized_min_year, optimized_max_year) = car_db_optimizer.get_optimized_year_range(make, model, user_min_year, user_max_year)
    model_info = car_db_optimizer.get_model_info(make, model)
    generations = car_db_optimizer.get_generations_for_model(make, model)
    return {'min_year': optimized_min_year, 'max_year': optimized_max_year, 'model_info': model_info, 'generations': generations, 'selected_generation': None, 'normalized_model': car_db_optimizer.normalize_model_name(make, model)}