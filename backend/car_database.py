import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import json
from typing import Dict, List, Optional, Tuple
import re
import bcrypt
import os
from contextlib import contextmanager
from logger import get_logger
from metrics import metrics

log = get_logger('car_database')

class CarDatabaseOptimizer:

    def __init__(self, db_path: str=None):
        if db_path is None:
            # Preluam de la Vercel sau din mediul local. Daca lipsește, dăm un fallback simulat.
            self.db_path = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/car_sniper")
        else:
            self.db_path = db_path
            
        try:
            self.connection_pool = pool.ThreadedConnectionPool(1, 20, self.db_path, cursor_factory=RealDictCursor)
        except Exception as e:
            log.error("Connection pool error", extra={"error": str(e)})
            metrics.increment("errors")
            self.connection_pool = None
            
        self.init_database()

    @contextmanager
    def get_connection(self):
        # Using RealDictCursor allows us to fetch rows as dictionaries, similar to sqlite3.Row
        if self.connection_pool:
            from_pool = False
            try:
                conn = self.connection_pool.getconn()
                from_pool = True
                try:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                except psycopg2.OperationalError:
                    self.connection_pool.putconn(conn, close=True)
                    conn = self.connection_pool.getconn()
                    from_pool = True
            except Exception as e:
                log.warning("Pool connection fallback", extra={"error": str(e)})
                conn = psycopg2.connect(self.db_path, cursor_factory=RealDictCursor)
                from_pool = False

            try:
                yield conn
            finally:
                if from_pool and self.connection_pool:
                    try:
                        self.connection_pool.putconn(conn, close=bool(conn.closed))
                    except:
                        pass
                else:
                    if conn:
                        conn.close()
        else:
            conn = psycopg2.connect(self.db_path, cursor_factory=RealDictCursor)
            try:
                yield conn
            finally:
                conn.close()

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
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
            
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        hashed_password TEXT NOT NULL,
                        role TEXT DEFAULT 'user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS car_models (
                        id SERIAL PRIMARY KEY,
                        make TEXT NOT NULL,
                        model TEXT NOT NULL,
                        model_variants TEXT,
                        min_year INTEGER,
                        max_year INTEGER,
                        generation TEXT,
                        body_type TEXT,
                        engine_types TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(make, model)
                    )
                ''')
            
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS search_stats (
                        id SERIAL PRIMARY KEY,
                        make TEXT,
                        model TEXT,
                        search_count INTEGER DEFAULT 1,
                        last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        avg_price REAL,
                        avg_year REAL,
                        avg_km REAL
                    )
                ''')
            
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id SERIAL PRIMARY KEY,
                        user_email TEXT NOT NULL,
                        make TEXT NOT NULL,
                        model TEXT NOT NULL,
                        min_price INTEGER,
                        max_price INTEGER,
                        min_year INTEGER,
                        max_year INTEGER,
                        max_km INTEGER,
                        active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_checked TIMESTAMP
                    )
                ''')
            
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ads (
                        id TEXT PRIMARY KEY,
                        source TEXT,
                        title TEXT,
                        price INTEGER,
                        currency TEXT DEFAULT 'EUR',
                        link TEXT UNIQUE,
                        image TEXT,
                        make TEXT,
                        model TEXT,
                        year INTEGER,
                        km INTEGER,
                        fuel TEXT,
                        transmission TEXT,
                        body_type TEXT,
                        city TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        active BOOLEAN DEFAULT TRUE
                    )
                ''')
            
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_ads_make_model ON ads(make, model)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_ads_price ON ads(price)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_ads_link ON ads(link)')
                
                # Setup column for Price Drop Tracking
                cursor.execute('ALTER TABLE ads ADD COLUMN IF NOT EXISTS original_price INTEGER')
            
                conn.commit()
        except Exception as e:
            log.error("Database creation error", extra={"error": str(e)})
            metrics.increment("errors")

    def delete_ad(self, ad_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM ads WHERE id = %s', (ad_id,))
            conn.commit()

    def upsert_ad(self, ad_data: dict):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            import hashlib
            link = ad_data.get('link', '')
            if not ad_data.get('id'):
                ad_id = hashlib.md5(link.encode()).hexdigest()
            else:
                ad_id = ad_data['id']
            try:
                p_str = str(ad_data.get('price', '0'))
                p_digits = ''.join(filter(str.isdigit, p_str))
                price_val = int(p_digits) if p_digits else 0
            except:
                price_val = 0

            km_val = ad_data.get('km')
            if km_val:
                km_val = int(''.join(c for c in str(km_val) if c.isdigit()) or 0)
            
            year_val = ad_data.get('year')
            if year_val is not None:
                year_val = int(''.join(c for c in str(year_val) if c.isdigit()) or 0)
                year_val = max(1950, min(year_val, 2026))
                
                cursor.execute('''
                INSERT INTO ads (
                    id, source, title, price, link, image, make, model, year, km, 
                    fuel, transmission, body_type, city, last_seen, active, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, TRUE, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    price = EXCLUDED.price,
                    last_seen = CURRENT_TIMESTAMP,
                    active = TRUE,
                    updated_at = CURRENT_TIMESTAMP,
                    image = COALESCE(EXCLUDED.image, ads.image) 
            ''', (
                ad_id, 
                ad_data.get('subsource') or ad_data.get('source', 'Unknown'), 
                ad_data.get('title'), 
                price_val, 
                link, 
                ad_data.get('image'), 
                ad_data.get('make'), 
                ad_data.get('model'), 
                year_val, 
                km_val, 
                ad_data.get('fuel'), 
                ad_data.get('transmission'), 
                ad_data.get('body_type'), 
                ad_data.get('city')
            ))
            conn.commit()
            return ad_id

    @metrics.timed('upsert_ads')
    def upsert_ads(self, ads_data: List[Dict]):
        if not ads_data:
            return []
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            import hashlib
            from psycopg2.extras import execute_values
            
            insert_query = '''
                INSERT INTO ads (
                    id, source, title, price, original_price, link, image, make, model, year, km, 
                    fuel, transmission, body_type, city, last_seen, active, updated_at
                ) VALUES %s
                ON CONFLICT(id) DO UPDATE SET
                    price = EXCLUDED.price,
                    original_price = COALESCE(ads.original_price, EXCLUDED.price),
                    last_seen = CURRENT_TIMESTAMP,
                    active = TRUE,
                    updated_at = CURRENT_TIMESTAMP,
                    image = COALESCE(EXCLUDED.image, ads.image) 
            '''
            
            values = []
            ad_ids = []
            
            for ad_data in ads_data:
                link = ad_data.get('link', '')
                if not ad_data.get('id'):
                    clean_link = link.split('?')[0]
                    ad_id = hashlib.md5(clean_link.encode()).hexdigest()
                else:
                    ad_id = ad_data['id']
                try:
                    p_str = str(ad_data.get('price', '0'))
                    p_digits = ''.join(filter(str.isdigit, p_str))
                    price_val = int(p_digits) if p_digits else 0
                except:
                    price_val = 0

                km_val = ad_data.get('km')
                if km_val:
                    km_val = int(''.join(c for c in str(km_val) if c.isdigit()) or 0)
                
                year_val = ad_data.get('year')
                if year_val is not None:
                    year_val = int(''.join(c for c in str(year_val) if c.isdigit()) or 0)
                    year_val = max(1950, min(year_val, 2026))

                # Upscale image quality by altering OLX/Autovit CDN params
                img_url = ad_data.get('image')
                if img_url and 'image;s=' in img_url:
                    img_url = re.sub(r'image;s=\d+x\d+.*$', 'image;s=1000x750;q=90', img_url)

                values.append((
                    ad_id, 
                    ad_data.get('subsource') or ad_data.get('source', 'Unknown'), 
                    ad_data.get('title'), 
                    price_val, 
                    price_val,
                    link, 
                    img_url, 
                    ad_data.get('make'), 
                    ad_data.get('model'), 
                    year_val, 
                    km_val, 
                    ad_data.get('fuel'), 
                    ad_data.get('transmission'), 
                    ad_data.get('body_type'), 
                    ad_data.get('city')
                ))
                ad_ids.append(ad_id)
                
            execute_values(cursor, insert_query, values, template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, TRUE, CURRENT_TIMESTAMP)")
            conn.commit()
            return ad_ids

    def mark_ghost_ads_inactive(self, make: str, model: str, buffer_hours: int = 12):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE ads SET active = FALSE 
                WHERE make = %s AND model = %s AND active = TRUE AND last_seen < NOW() - CAST(%s AS interval)
            ''', (make, model, f"{buffer_hours} hours"))
            count = cursor.rowcount
            conn.commit()
            return count

    def search_ads_db(self, make: str, model: str, min_price=None, max_price=None, min_year=None, max_year=None, min_km=None, max_km=None, fuel=None, transmission=None, limit=100, sort_by='price', order='asc') -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM ads WHERE active = TRUE'
            params = []
            if make:
                query += ' AND make ILIKE %s'
                params.append(f'%{make}%')
            if model:
                if len(model) <= 2:
                    # STRICT matching for short models (like M3, Q5). Do not fallback to title!
                    query += r' AND model ~* %s'
                    params.append(rf'(^|\s|-){model}(\s|$|-)')
                else:
                    query += ' AND (model ILIKE %s OR title ILIKE %s)'
                    params.append(f'%{model}%')
                    params.append(f'%{model}%')
            if min_price:
                query += ' AND price >= %s'
                params.append(min_price)
            else:
                # Default filter: allow price=0 (e.g., 'Schimb'/Trade), but reject price < 500 if it's > 0 (parts/toys)
                query += ' AND (price = 0 OR price >= 500)'
            if max_price:
                query += ' AND price <= %s'
                params.append(max_price)
            if min_year:
                query += ' AND year >= %s'
                params.append(min_year)
            if max_year:
                query += ' AND year <= %s'
                params.append(max_year)
            if max_km:
                query += ' AND km <= %s'
                params.append(max_km)
            if fuel:
                query += ' AND fuel ILIKE %s'
                params.append(fuel)
            if transmission:
                query += ' AND transmission ILIKE %s'
                params.append(transmission)
        
            valid_sort_columns = {'price': 'price', 'year': 'year', 'km': 'km', 'created_at': 'created_at'}
            sort_column = valid_sort_columns.get(sort_by, 'created_at')
            sort_order = 'ASC' if order.lower() == 'asc' else 'DESC'
            
            query += f' ORDER BY {sort_column} {sort_order} LIMIT %s'
            params.append(limit)
        
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            ads = []
            for r in rows:
                d = dict(r)
                d['price'] = f"{d['price']} €"
                ads.append(d)
            return ads

    def get_recent_active_ads(self, hours_threshold: int = 48) -> List[Dict]:
        """Fetch all active ads updated/added within the last hours_threshold hours."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT * FROM ads 
                WHERE active = TRUE 
                  AND updated_at >= NOW() - CAST(%s AS interval)
            '''
            cursor.execute(query, (f"{hours_threshold} hours",))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_active_ads_for_make_model(self, make: str, model: str) -> List[Dict]:
        """Fetch all active ads for a specific make and model to act as a peer comparison group."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT * FROM ads 
                WHERE active = TRUE 
                  AND make ILIKE %s 
                  AND model ILIKE %s
            '''
            cursor.execute(query, (make, model))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def deactivate_stale_ads(self, hours_threshold=24):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # PostgreSQL syntax for interval
            cursor.execute("UPDATE ads SET active = FALSE WHERE last_seen < NOW() - CAST(%s AS interval)", (f"{hours_threshold} hours",))
            count = cursor.rowcount
            conn.commit()
            return count

    def get_cron_groups(self, limit=2):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT make, model 
                    FROM alerts 
                    WHERE active = TRUE 
                    GROUP BY make, model 
                    ORDER BY MIN(COALESCE(last_checked, '2000-01-01')) ASC
                    LIMIT %s
                ''', (limit,))
                groups = cursor.fetchall()
                cursor.close()
                return [{'make': r[0], 'model': r[1]} for r in groups]
        except Exception as e:
                log.error("Cron groups error", extra={"error": str(e)})
                metrics.increment("errors")
                return []

    def get_alerts_for_group(self, make, model):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user_email, min_price, max_price, min_year, max_year, max_km 
                    FROM alerts 
                    WHERE active = TRUE AND make = %s AND model = %s
                ''', (make, model))
            
                alerts = cursor.fetchall()
                cursor.execute('''
                    UPDATE alerts SET last_checked = CURRENT_TIMESTAMP WHERE active = TRUE AND make = %s AND model = %s
                ''', (make, model))
                conn.commit()
                cursor.close()
            
                return [{
                    'id': r[0], 'user_email': r[1], 'min_price': r[2], 'max_price': r[3],
                    'min_year': r[4], 'max_year': r[5], 'max_km': r[6]
                } for r in alerts]
        except Exception as e:
                log.error("Alerts for group error", extra={"error": str(e)})
                metrics.increment("errors")
                return []

    def insert_cron_ads(self, ads):
        new_ads = []
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
            
                for ad in ads:
                    ad_id = ad.get('id')
                    if not ad_id:
                        continue
                
                    cursor.execute('''
                        INSERT INTO ads (id, source, title, price, currency, link, image, make, model, year, km, fuel, transmission, body_type, city)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        RETURNING id
                    ''', (
                        ad_id, ad.get('source'), ad.get('title'), ad.get('price'), ad.get('currency', 'EUR'), ad.get('link'),
                        ad.get('image'), ad.get('make'), ad.get('model'), ad.get('year'), ad.get('km'),
                        ad.get('fuel'), ad.get('transmission'), ad.get('body_type'), ad.get('city')
                    ))
                
                    if cursor.fetchone():
                        new_ads.append(ad)
            
                conn.commit()
                cursor.close()
                return new_ads
        except Exception as e:
                log.error("Cron ads insert error", extra={"error": str(e)})
                metrics.increment("errors")
                return []

    def add_car_model(self, make: str, model: str, min_year: int=None, max_year: int=None, generation: str=None, body_type: str=None, model_variants: List[str]=None, engine_types: List[str]=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            variants_json = json.dumps(model_variants) if model_variants else None
            engines_json = json.dumps(engine_types) if engine_types else None
        
            cursor.execute('''
                INSERT INTO car_models 
                (make, model, model_variants, min_year, max_year, generation, body_type, engine_types, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (make, model) DO UPDATE SET
                    model_variants = EXCLUDED.model_variants,
                    min_year = EXCLUDED.min_year,
                    max_year = EXCLUDED.max_year,
                    generation = EXCLUDED.generation,
                    body_type = EXCLUDED.body_type,
                    engine_types = EXCLUDED.engine_types,
                    updated_at = CURRENT_TIMESTAMP
            ''', (make.lower(), model.lower(), variants_json, min_year, max_year, generation, body_type, engines_json))
            conn.commit()

    def get_model_info(self, make: str, model: str) -> Optional[Dict]:
        if not make or not model:
            return None
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT make, model, model_variants, min_year, max_year, generation, body_type, engine_types
                FROM car_models 
                WHERE make = %s AND model = %s
            ''', (make.lower(), model.lower()))
            result = cursor.fetchone()
            if result:
                return {'make': result['make'], 'model': result['model'], 'model_variants': json.loads(result['model_variants']) if result['model_variants'] else [], 'min_year': result['min_year'], 'max_year': result['max_year'], 'generation': result['generation'], 'body_type': result['body_type'], 'engine_types': json.loads(result['engine_types']) if result['engine_types'] else []}
            return None

    def get_generations_for_model(self, make: str, model: str) -> List[Dict]:
        if not hasattr(self, '_gens_cache'):
            self._gens_cache = {}
            # Load generations.json if it exists
            gen_path = os.path.join(os.path.dirname(__file__), 'generations.json')
            self._json_gens = {}
            if os.path.exists(gen_path):
                try:
                    with open(gen_path, 'r', encoding='utf-8') as f:
                        self._json_gens = json.load(f)
                except Exception as e:
                    logging.error(f"Error loading generations.json: {e}")

        cache_key = f"{make}_{model}"
        if cache_key in self._gens_cache:
            return self._gens_cache[cache_key]

        make_normalized = make.lower().strip()
        model_normalized = model.lower().strip()

        # Custom normalization for performance models to map to base models
        if make_normalized in ['mercedes', 'mercedes-benz', 'mercedes benz']:
            make_normalized = 'mercedes-benz'
            if 'amg' in model_normalized or re.match(r'^[a-z]{1,2}\s?\d{2}', model_normalized):
                # E.g. C 63 AMG -> c-class
                if 'c' in model_normalized: model_normalized = 'c-class'
                elif 'e' in model_normalized: model_normalized = 'e-class'
                elif 's' in model_normalized and 'g' not in model_normalized: model_normalized = 's-class'
                elif 'g' in model_normalized and 'l' not in model_normalized: model_normalized = 'g-class'
        elif make_normalized == 'audi':
            if model_normalized.startswith('rs'):
                model_normalized = re.sub(r'^rs', 'a', model_normalized)
            elif model_normalized.startswith('s') and not model_normalized.startswith('sq'):
                model_normalized = re.sub(r'^s', 'a', model_normalized)
            elif model_normalized.startswith('sq'):
                model_normalized = re.sub(r'^sq', 'q', model_normalized)
        elif make_normalized == 'bmw':
            if model_normalized.startswith('m') and len(model_normalized) <= 2:
                model_normalized = model_normalized.replace('m', 'seria ')

        # Find in JSON first
        for json_make, models in self._json_gens.items():
            if json_make.lower() == make_normalized or json_make.lower().replace('-', '') == make_normalized.replace('-', ''):
                for json_model, gens in models.items():
                    if json_model.lower() == model_normalized or json_model.lower().replace('-', '') == model_normalized.replace('-', ''):
                        # Convert JSON format to expected format
                        formatted_gens = []
                        for g in gens:
                            formatted_gens.append({
                                'generation': g['code'],
                                'min_year': g['start_year'],
                                'max_year': g['end_year'],
                                'facelift_year': g.get('facelift_year')
                            })
                        self._gens_cache[cache_key] = formatted_gens
                        return formatted_gens

        # Fallback to hardcoded logic if not in JSON
        generations = self._get_model_generations_from_db(make_normalized, model_normalized)
        if generations:
            self._gens_cache[cache_key] = generations
            return generations

        self._gens_cache[cache_key] = []
        return []

    def _get_model_generations_from_db(self, make: str, model: str) -> List[Dict]:
        if make.lower() == 'bmw' and any((x in model.lower() for x in ['seria-3', 'seria3', '3', 'seria 3'])):
            return [{'generation': 'E90', 'min_year': 2005, 'max_year': 2012, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'F30', 'min_year': 2012, 'max_year': 2019, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'G20', 'min_year': 2019, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() == 'bmw' and any((x in model.lower() for x in ['seria-5', 'seria5', '5', 'seria 5'])):
            return [{'generation': 'E60', 'min_year': 2003, 'max_year': 2010, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'F10', 'min_year': 2010, 'max_year': 2017, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'G30', 'min_year': 2017, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() == 'audi' and model.lower() in ['a4', 'a-4']:
            return [{'generation': 'B7', 'min_year': 2004, 'max_year': 2008, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'B8', 'min_year': 2008, 'max_year': 2016, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'B9', 'min_year': 2016, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() == 'audi' and model.lower() in ['a6', 'a-6']:
            return [{'generation': 'C6', 'min_year': 2004, 'max_year': 2011, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'C7', 'min_year': 2011, 'max_year': 2018, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'C8', 'min_year': 2018, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() == 'audi' and model.lower() in ['a3', 'a-3']:
            return [{'generation': '8P', 'min_year': 2003, 'max_year': 2012, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol']}, {'generation': '8V', 'min_year': 2012, 'max_year': 2020, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol']}, {'generation': '8Y', 'min_year': 2020, 'max_year': 2024, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() in ['mercedes', 'mercedes-benz'] and any((x in model.lower() for x in ['c', 'c-class', 'cclass', 'c class'])):
            return [{'generation': 'W204', 'min_year': 2007, 'max_year': 2014, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'W205', 'min_year': 2014, 'max_year': 2021, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'W206', 'min_year': 2021, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() in ['mercedes', 'mercedes-benz'] and any((x in model.lower() for x in ['e', 'e-class', 'eclass', 'e class'])):
            return [{'generation': 'W211', 'min_year': 2002, 'max_year': 2009, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'W212', 'min_year': 2009, 'max_year': 2016, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'W213', 'min_year': 2016, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() == 'volkswagen' and model.lower() in ['golf', 'golf-7', 'golf-8']:
            return [{'generation': 'Mk5', 'min_year': 2003, 'max_year': 2008, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol']}, {'generation': 'Mk6', 'min_year': 2008, 'max_year': 2012, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol']}, {'generation': 'Mk7', 'min_year': 2012, 'max_year': 2019, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol']}, {'generation': 'Mk8', 'min_year': 2019, 'max_year': 2024, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() == 'volkswagen' and model.lower() in ['passat', 'passat-cc']:
            return [{'generation': 'B6', 'min_year': 2005, 'max_year': 2010, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'B7', 'min_year': 2010, 'max_year': 2014, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'B8', 'min_year': 2014, 'max_year': 2023, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() == 'skoda' and model.lower() in ['octavia']:
            return [{'generation': 'Mk2', 'min_year': 2004, 'max_year': 2013, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'Mk3', 'min_year': 2013, 'max_year': 2020, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']}, {'generation': 'Mk4', 'min_year': 2020, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        elif make.lower() == 'bmw' and any((x in model.lower() for x in ['x5', 'x-5'])):
            return [{'generation': 'E70', 'min_year': 2006, 'max_year': 2013, 'body_type': 'suv', 'engine_types': ['diesel', 'petrol']}, {'generation': 'F15', 'min_year': 2013, 'max_year': 2018, 'body_type': 'suv', 'engine_types': ['diesel', 'petrol', 'hybrid']}, {'generation': 'G05', 'min_year': 2018, 'max_year': 2024, 'body_type': 'suv', 'engine_types': ['diesel', 'petrol', 'hybrid']}]
        return []

    def get_generation_for_year(self, make: str, model: str, year: int) -> str:
        generations = self.get_generations_for_model(make, model)
        if not generations:
            return None
        for gen in generations:
            if gen['min_year'] <= year <= gen['max_year']:
                return gen['generation']
        return None

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

    def normalize_model_name(self, make: str | None, model: str | None) -> str:
        make_lc = make.lower().strip() if make else ''
        model_lc = model.lower().strip() if model else ''
        if make_lc == 'bmw':
            m = re.match('^(x)?(\\d)', model_lc)
            if m:
                is_x = m.group(1) == 'x'
                digit = m.group(2)
                if is_x:
                    return f'x{digit}'
                return f'seria-{digit}'
        elif make_lc == 'audi':
            # Preserve "allroad" suffix before truncating
            is_allroad = 'allroad' in model_lc
            m = re.match('^([aq])(\\d+)', model_lc)
            if m:
                series = m.group(1)
                number = m.group(2)
                base = f'{series}{number}'
                return f'{base} allroad' if is_allroad else base
            return model_lc
        elif make_lc in ['mercedes', 'mercedesbenz', 'mercedes-benz']:
            if 'clasa' in model_lc or 'class' in model_lc:
                m = re.search(r'\b([a-z])\b', model_lc.replace('clasa', '').replace('class', ''))
                if m:
                    return m.group(1)
            return model_lc
        elif make_lc == 'mazda':
            if model_lc.startswith('cx ') or model_lc.startswith('mx '):
                return model_lc.replace(' ', '-')
            return model_lc
            
        return model_lc

    def update_search_stats(self, make: str, model: str, avg_price: float=None, avg_year: float=None, avg_km: float=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, search_count FROM search_stats WHERE make = %s AND model = %s ORDER BY id DESC LIMIT 1', (make.lower(), model.lower()))
            row = cursor.fetchone()
            if row:
                cursor.execute('''
                    UPDATE search_stats 
                    SET search_count = search_count + 1,
                        last_searched = CURRENT_TIMESTAMP,
                        avg_price = %s, avg_year = %s, avg_km = %s
                    WHERE id = %s
                ''', (avg_price, avg_year, avg_km, row['id']))
            else:
                cursor.execute('''
                    INSERT INTO search_stats 
                    (make, model, search_count, last_searched, avg_price, avg_year, avg_km)
                    VALUES (%s, %s, 1, CURRENT_TIMESTAMP, %s, %s, %s)
                ''', (make.lower(), model.lower(), avg_price, avg_year, avg_km))
            conn.commit()

    def get_popular_models(self, make: str=None, limit: int=10) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if make:
                cursor.execute('''
                    SELECT make, model, search_count, avg_price, avg_year, avg_km
                    FROM search_stats 
                    WHERE make = %s
                    ORDER BY search_count DESC, last_searched DESC
                    LIMIT %s
                ''', (make.lower(), limit))
            else:
                cursor.execute('''
                    SELECT make, model, search_count, avg_price, avg_year, avg_km
                    FROM search_stats 
                    ORDER BY search_count DESC, last_searched DESC
                    LIMIT %s
                ''', (limit,))
            results = cursor.fetchall()
            return [{'make': r['make'], 'model': r['model'], 'search_count': r['search_count'], 'avg_price': r['avg_price'], 'avg_year': r['avg_year'], 'avg_km': r['avg_km']} for r in results]

    def get_model_stats(self, make: str, model: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT make, model, search_count, avg_price, avg_year, avg_km, last_searched
                FROM search_stats 
                WHERE make = %s AND model = %s
                ORDER BY id DESC LIMIT 1
            ''', (make.lower(), model.lower()))
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None

    def populate_sample_data(self):
        sample_models = [('bmw', 'seria-3', 2012, 2024, 'F30/G20', 'sedan', ['320d', '330d', '320i', '330i'], ['diesel', 'petrol']), ('bmw', 'seria-5', 2010, 2024, 'F10/G30', 'sedan', ['520d', '530d', '520i', '530i'], ['diesel', 'petrol']), ('bmw', 'x3', 2010, 2024, 'F25/G01', 'suv', ['x3', 'xdrive30d', 'xdrive20d'], ['diesel', 'petrol']), ('bmw', 'x5', 2006, 2024, 'E70/F15/G05', 'suv', ['x5', 'xdrive30d', 'xdrive40d'], ['diesel', 'petrol']), ('audi', 'a4', 2008, 2024, 'B8/B9', 'sedan', ['a4', 'avant', 'allroad'], ['diesel', 'petrol']), ('audi', 'a6', 2011, 2024, 'C7/C8', 'sedan', ['a6', 'avant', 'allroad'], ['diesel', 'petrol']), ('audi', 'q5', 2008, 2024, '8R/FY', 'suv', ['q5', 'sq5'], ['diesel', 'petrol']), ('audi', 'q7', 2006, 2024, '4L/4M', 'suv', ['q7', 'sq7'], ['diesel', 'petrol']), ('mercedes', 'c', 2007, 2024, 'W204/W205', 'sedan', ['c220d', 'c250d', 'c200', 'c250'], ['diesel', 'petrol']), ('mercedes', 'e', 2009, 2024, 'W212/W213', 'sedan', ['e220d', 'e250d', 'e200', 'e250'], ['diesel', 'petrol']), ('mercedes', 'g', 2005, 2024, 'W463', 'suv', ['g350d', 'g500', 'g63'], ['diesel', 'petrol']), ('volkswagen', 'golf', 2008, 2024, 'Mk6/Mk7/Mk8', 'hatchback', ['golf', 'gti', 'gtd'], ['diesel', 'petrol']), ('volkswagen', 'passat', 2010, 2024, 'B7/B8', 'sedan', ['passat', 'passat-variant'], ['diesel', 'petrol']), ('volkswagen', 'tiguan', 2007, 2024, '5N/AD1', 'suv', ['tiguan', 'tiguan-allspace'], ['diesel', 'petrol']), ('skoda', 'octavia', 2013, 2024, 'Mk3/Mk4', 'sedan', ['octavia', 'octavia-combi'], ['diesel', 'petrol']), ('skoda', 'superb', 2008, 2024, '3T/3V', 'sedan', ['superb', 'superb-combi'], ['diesel', 'petrol']), ('skoda', 'kodiaq', 2017, 2024, 'NS', 'suv', ['kodiaq'], ['diesel', 'petrol'])]
        for model_data in sample_models:
            self.add_car_model(*model_data)

    def populate_from_scraper(self, max_brands: int=None, max_models_per_brand: int=None):
        from auto_data_scraper import AutoDataScraper
        scraper = AutoDataScraper(self)
        log.info("Populating database from auto-data.net")
        data = scraper.scrape_all_data(max_brands, max_models_per_brand)
        log.info('Database population complete', extra={'models': len(data)})
        return data

    def add_alert(self, user_email: str, make: str, model: str, min_price: int=None, max_price: int=None, min_year: int=None, max_year: int=None, max_km: int=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (user_email, make, model, min_price, max_price, min_year, max_year, max_km, active, last_checked)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP)
                RETURNING id
            ''', (user_email, make, model, min_price, max_price, min_year, max_year, max_km))
            row = cursor.fetchone()
            alert_id = row['id'] if row else None
            conn.commit()
            return {'id': alert_id, 'user_email': user_email, 'make': make, 'model': model, 'min_price': min_price, 'max_price': max_price, 'min_year': min_year, 'max_year': max_year, 'max_km': max_km, 'active': 1}

    def deactivate_alert(self, alert_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE alerts SET active = FALSE WHERE id = %s', (alert_id,))
            conn.commit()

    def get_alerts(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM alerts')
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def register_user(self, email: str, password: str) -> dict:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                hashed = self._hash_password(password)
                cursor.execute('INSERT INTO users (email, hashed_password) VALUES (%s, %s) RETURNING id', (email, hashed))
                row = cursor.fetchone()
                user_id = row['id']
                conn.commit()
                return {"success": True, "id": user_id, "email": email}
            except psycopg2.IntegrityError:
                conn.rollback() # necesar in Postgres
                return {"success": False, "error": "Email already registered"}

    def verify_login(self, email: str, password: str) -> dict:
        with self.get_connection() as conn:
            cursor = conn.cursor()
        
            cursor.execute('SELECT id, email, hashed_password, role FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
        
            if not user:
                return {"success": False, "error": "User not found"}
            
            try:
                if bcrypt.checkpw(password.encode('utf-8'), user["hashed_password"].encode('utf-8')):
                    return {"success": True, "id": user["id"], "email": user["email"], "role": user.get("role", "user")}
                else:
                    return {"success": False, "error": "Incorrect password"}
            except ValueError:
                return {"success": False, "error": "Incorrect password or outdated security hash"}

    def get_all_brands(self) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT make FROM car_models ORDER BY make ASC')
            rows = cursor.fetchall()
            brands = [self.format_brand_name(row['make']) for row in rows if row['make']]
            return sorted(list(set(brands)))

    def get_models(self, make: str) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT model FROM car_models WHERE make = %s ORDER BY model ASC', (make.lower(),))
            rows = cursor.fetchall()
            models = [self.format_model_name(row['model']) for row in rows if row['model']]
            return sorted(list(set(models)))
        
car_db_optimizer = CarDatabaseOptimizer()

def get_optimized_search_params(make: str, model: str, user_min_year: int=None, user_max_year: int=None) -> Dict:
    (optimized_min_year, optimized_max_year) = car_db_optimizer.get_optimized_year_range(make, model, user_min_year, user_max_year)
    model_info = car_db_optimizer.get_model_info(make, model)
    generations = car_db_optimizer.get_generations_for_model(make, model)
    return {'min_year': optimized_min_year, 'max_year': optimized_max_year, 'model_info': model_info, 'generations': generations, 'selected_generation': None, 'normalized_model': car_db_optimizer.normalize_model_name(make, model)}
