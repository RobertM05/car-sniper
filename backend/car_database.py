"""
Car Database Optimization Module
Acest modul conține funcții pentru optimizarea căutărilor prin matching-ul
datelor din scrapere cu informațiile din baza de date auto.
"""

import sqlite3
import json
from typing import Dict, List, Optional, Tuple
import re


class CarDatabaseOptimizer:
    def __init__(self, db_path: str = "../database/db.sqlite"):
        self.db_path = db_path
        self.init_database()

    def format_brand_name(self, brand: str) -> str:
        """Formatează numele mărcii pentru afișare"""
        brand = brand.lower().strip()
        
        special_cases = {
            "bmw": "BMW",
            "vw": "VW",
            "volkswagen": "Volkswagen",
            "mercedes": "Mercedes-Benz",
            "mercedes-benz": "Mercedes-Benz",
            "mercedesbenz": "Mercedes-Benz",
            "mg": "MG",
            "gmc": "GMC",
            "acura": "Acura",
            "alfa romeo": "Alfa Romeo",
            "aston martin": "Aston Martin",
            "land rover": "Land Rover",
            "range rover": "Range Rover",
            "rolls-royce": "Rolls-Royce",
            "seat": "SEAT", # Uneori scris SEAT
            "fiat": "FIAT", # Uneori scris FIAT
            "mini": "MINI"
        }
        
        return special_cases.get(brand, brand.title())

    def format_model_name(self, model: str) -> str:
        """Formatează numele modelului pentru afișare"""
        model = model.lower().strip()
        
        # Remove years (19xx or 20xx) if they appear as standalone words
        model = re.sub(r"\b(19|20)\d{2}\b", "", model).strip()
        
        # Înlocuiește cratimele cu spații, păstrând cratimele pentru anumite cazuri dacă e nevoie
        # Deocamdată simplu: replace - with space
        model = model.replace("-", " ")
        
        words = model.split()
        formatted_words = []
        
        for word in words:
            if word in ["bmw", "vw", "gti", "gtd", "amg", "rs", "wrx", "sti", "cr-v", "hr-v", "rav4", "mx-5", "cx-3", "cx-5", "cx-30", "cx-60", "cx-90"]:
                formatted_words.append(word.upper())
            elif word.startswith("mk") and word[2:].isdigit(): # Mk7, Mk8
                formatted_words.append("Mk" + word[2:])
            elif word in ["ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]: # Numerale romane
                formatted_words.append(word.upper())
            elif word in ["cdi", "tdi", "tfsi", "tsi", "fsi", "d", "i", "e", "h"]: # Sufixe motorizari izolate
                formatted_words.append(word.upper())
            elif word == "seria":
                formatted_words.append("Seria")
            elif word == "clasa":
                formatted_words.append("Clasa")
            elif word == "class":
                formatted_words.append("Class")
            else:
                formatted_words.append(word.title())
                
        # Reconstruct string
        formatted_model = " ".join(formatted_words)
        
        # Ajustări fine finale post-join
        if "Seria " in formatted_model and formatted_model[-1].isdigit():
             pass # E ok, gen "Seria 3"
             
        return formatted_model
    
    def init_database(self):
        """Inițializează baza de date cu tabela pentru modelele de mașini"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Creează tabela pentru modelele de mașini cu informații despre anii de producție
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS car_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                model_variants TEXT,  -- JSON cu variantele modelului
                min_year INTEGER,
                max_year INTEGER,
                generation TEXT,      -- Generația modelului
                body_type TEXT,      -- sedan, suv, hatchback, etc.
                engine_types TEXT,   -- JSON cu tipurile de motor
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(make, model)
            )
        """)
        
        # Creează tabela pentru statistici de căutare
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                make TEXT,
                model TEXT,
                search_count INTEGER DEFAULT 1,
                last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                avg_price REAL,
                avg_year REAL,
                avg_km REAL
            )
        """)

        # Creează tabela pentru alerte
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                max_price INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP
            )
        """)

        # Creează tabela pentru anunțuri (Ads)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id TEXT PRIMARY KEY,       -- Unic, bazat pe link hash sau ID site
                source TEXT,               -- OLX, Autovit
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
                active BOOLEAN DEFAULT 1
            )
        """)
        
        # Index pentru viteza
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ads_make_model ON ads(make, model)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ads_price ON ads(price)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ads_link ON ads(link)")
        
        conn.commit()
        conn.close()

    def delete_ad(self, ad_id: str):
        """Sterge un anunț din baza de date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ads WHERE id = ?", (ad_id,))
        conn.commit()
        conn.close()

    def upsert_ad(self, ad_data: dict):
        """Introduce sau actualizează un anunț în baza de date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generare ID simplu dacă nu există (hash la link)
        import hashlib
        link = ad_data.get("link", "")
        if not ad_data.get("id"):
            ad_id = hashlib.md5(link.encode()).hexdigest()
        else:
            ad_id = ad_data["id"]

        # Parse price safe
        try:
             price_val = int(ad_data.get("price", 0))
        except:
             price_val = 0

        cursor.execute("""
            INSERT INTO ads (
                id, source, title, price, link, image, make, model, year, km, 
                fuel, transmission, body_type, city, last_seen, active, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(link) DO UPDATE SET
                price = excluded.price,
                last_seen = CURRENT_TIMESTAMP,
                active = 1,
                updated_at = CURRENT_TIMESTAMP,
                image = COALESCE(excluded.image, ads.image) 
        """, (
            ad_id,
            ad_data.get("subsource") or ad_data.get("source", "Unknown"),
            ad_data.get("title"),
            price_val,
            link,
            ad_data.get("image"),
            ad_data.get("make"),
            ad_data.get("model"),
            ad_data.get("year"),
            ad_data.get("km"),
            ad_data.get("fuel"),
            ad_data.get("transmission"),
            ad_data.get("body_type"),
            ad_data.get("city")
        ))
        
        conn.commit()
        conn.close()
        return ad_id

    def search_ads_db(self, make: str, model: str, min_price=None, max_price=None, 
                     min_year=None, max_year=None, min_km=None, max_km=None, limit=100,
                     sort_by="price", order="asc") -> List[Dict]:
        """Caută anunțuri în baza de date locală"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM ads WHERE active = 1"
        params = []
        
        if make:
            query += " AND make LIKE ?"
            params.append(f"%{make}%")
        if model:
            # Simplu fuzzy matching
            query += " AND (model LIKE ? OR title LIKE ?)"
            params.append(f"%{model}%")
            params.append(f"%{model}%")
            
        if min_price:
            query += " AND price >= ?"
            params.append(min_price)
        
        if max_price:
            query += " AND price <= ?"
            params.append(max_price)
            
        if min_year:
            query += " AND year >= ?"
            params.append(min_year)
        if max_year:
            query += " AND year <= ?"
            params.append(max_year)
            
        if max_km:
            query += " AND km <= ?"
            params.append(max_km)
            
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        ads = []
        for r in rows:
            d = dict(r)
            # Format price for UI compatibility
            d["price"] = f"{d['price']} €"
            ads.append(d)
            
        conn.close()
        return ads

    def deactivate_stale_ads(self, hours_threshold=24):
        """Marchează ca inactive anunțurile care nu au fost văzute recent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE ads SET active = 0 WHERE last_seen < datetime('now', '-{hours_threshold} hours')")
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count

    
    def add_car_model(self, make: str, model: str, min_year: int = None, 
                     max_year: int = None, generation: str = None, 
                     body_type: str = None, model_variants: List[str] = None,
                     engine_types: List[str] = None):
        """Adaugă un model de mașină în baza de date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        variants_json = json.dumps(model_variants) if model_variants else None
        engines_json = json.dumps(engine_types) if engine_types else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO car_models 
            (make, model, model_variants, min_year, max_year, generation, body_type, engine_types, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (make.lower(), model.lower(), variants_json, min_year, max_year, 
              generation, body_type, engines_json))
        
        conn.commit()
        conn.close()
    
    def get_model_info(self, make: str, model: str) -> Optional[Dict]:
        """Obține informațiile despre un model de mașină"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT make, model, model_variants, min_year, max_year, generation, body_type, engine_types
            FROM car_models 
            WHERE make = ? AND model = ?
        """, (make.lower(), model.lower()))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'make': result[0],
                'model': result[1],
                'model_variants': json.loads(result[2]) if result[2] else [],
                'min_year': result[3],
                'max_year': result[4],
                'generation': result[5],
                'body_type': result[6],
                'engine_types': json.loads(result[7]) if result[7] else []
            }
        return None
    
    def get_generations_for_model(self, make: str, model: str) -> List[Dict]:
        """Obține toate generațiile disponibile pentru un model"""
        # Normalizează input-ul pentru matching mai bun
        make_normalized = make.lower().strip()
        model_normalized = model.lower().strip()
        
        # Pentru modele cu multiple generații, le extragem din baza de date
        generations = self._get_model_generations_from_db(make_normalized, model_normalized)
        
        if generations:
            return generations
        
        # Dacă nu găsim în funcția hardcodată, încercăm din baza de date SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT generation, min_year, max_year, body_type, engine_types
            FROM car_models 
            WHERE make = ? AND model = ?
        """, (make_normalized, model_normalized))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:  # Dacă există generația
            # Pentru modele cu o singură generație, o returnăm
            return [{
                'generation': result[0],
                'min_year': result[1],
                'max_year': result[2],
                'body_type': result[3],
                'engine_types': json.loads(result[4]) if result[4] else []
            }]
        
        return []
    
    def _get_model_generations_from_db(self, make: str, model: str) -> List[Dict]:
        """Extrage generațiile pentru un model din baza de date"""
        # Pentru BMW Seria 3
        if make.lower() == "bmw" and any(x in model.lower() for x in ["seria-3", "seria3", "3", "seria 3"]):
            return [
                {'generation': 'E90', 'min_year': 2005, 'max_year': 2012, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']},
                {'generation': 'F30', 'min_year': 2012, 'max_year': 2019, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']},
                {'generation': 'G20', 'min_year': 2019, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}
            ]
        
        # Pentru BMW Seria 5
        elif make.lower() == "bmw" and any(x in model.lower() for x in ["seria-5", "seria5", "5", "seria 5"]):
            return [
                {'generation': 'E60', 'min_year': 2003, 'max_year': 2010, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']},
                {'generation': 'F10', 'min_year': 2010, 'max_year': 2017, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']},
                {'generation': 'G30', 'min_year': 2017, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}
            ]
        
        # Pentru Audi A4
        elif make.lower() == "audi" and model.lower() in ["a4", "a-4"]:
            return [
                {'generation': 'B7', 'min_year': 2004, 'max_year': 2008, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']},
                {'generation': 'B8', 'min_year': 2008, 'max_year': 2016, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']},
                {'generation': 'B9', 'min_year': 2016, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}
            ]
        
        # Pentru Mercedes C-Class
        elif make.lower() in ["mercedes", "mercedes-benz"] and any(x in model.lower() for x in ["c", "c-class", "cclass", "c class"]):
            return [
                {'generation': 'W204', 'min_year': 2007, 'max_year': 2014, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']},
                {'generation': 'W205', 'min_year': 2014, 'max_year': 2021, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol']},
                {'generation': 'W206', 'min_year': 2021, 'max_year': 2024, 'body_type': 'sedan', 'engine_types': ['diesel', 'petrol', 'hybrid']}
            ]
        
        # Pentru Volkswagen Golf
        elif make.lower() == "volkswagen" and model.lower() in ["golf", "golf-7", "golf-8"]:
            return [
                {'generation': 'Mk5', 'min_year': 2003, 'max_year': 2008, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol']},
                {'generation': 'Mk6', 'min_year': 2008, 'max_year': 2012, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol']},
                {'generation': 'Mk7', 'min_year': 2012, 'max_year': 2019, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol']},
                {'generation': 'Mk8', 'min_year': 2019, 'max_year': 2024, 'body_type': 'hatchback', 'engine_types': ['diesel', 'petrol', 'hybrid']}
            ]
        
        return []
    
    def get_year_range_for_generation(self, make: str, model: str, generation: str) -> Tuple[int, int]:
        """Obține intervalul de ani pentru o generație specifică"""
        generations = self.get_generations_for_model(make, model)
        
        for gen in generations:
            # Verificăm dacă generația se potrivește (poate fi formatată diferit)
            gen_name = gen['generation'].upper()
            target_gen = generation.upper()
            
            # Verificăm match exact sau parțial
            if gen_name == target_gen or target_gen in gen_name or gen_name in target_gen:
                return gen['min_year'], gen['max_year']
        
        return None, None
    
    def get_optimized_year_range(self, make: str, model: str, 
                                user_min_year: int = None, 
                                user_max_year: int = None,
                                generation: str = None) -> Tuple[int, int]:
        """
        Returnează intervalul optimizat de ani pentru căutare
        Combină informațiile din baza de date cu preferințele utilizatorului
        Dacă se specifică o generație, folosește intervalul de ani pentru acea generație
        """
        # Dacă se specifică o generație, folosim intervalul pentru acea generație
        if generation:
            gen_min_year, gen_max_year = self.get_year_range_for_generation(make, model, generation)
            if gen_min_year and gen_max_year:
                # Combinăm cu preferințele utilizatorului
                if user_min_year:
                    optimized_min = max(user_min_year, gen_min_year)
                else:
                    optimized_min = gen_min_year
                
                if user_max_year:
                    optimized_max = min(user_max_year, gen_max_year)
                else:
                    optimized_max = gen_max_year
                
                return optimized_min, optimized_max
        
        # Logica originală pentru când nu se specifică generația
        model_info = self.get_model_info(make, model)
        
        if not model_info:
            # Dacă nu avem informații în baza de date, folosim valorile utilizatorului
            return user_min_year, user_max_year
        
        db_min_year = model_info.get('min_year')
        db_max_year = model_info.get('max_year')
        
        # Optimizează intervalul de ani
        optimized_min = user_min_year
        optimized_max = user_max_year
        
        if db_min_year and db_max_year:
            # Dacă utilizatorul nu a specificat anul minim, folosim cel din baza de date
            if not user_min_year:
                optimized_min = db_min_year
            else:
                # Folosim cel mai mare dintre anul minim al utilizatorului și cel din baza de date
                optimized_min = max(user_min_year, db_min_year)
            
            # Dacă utilizatorul nu a specificat anul maxim, folosim cel din baza de date
            if not user_max_year:
                optimized_max = db_max_year
            else:
                # Folosim cel mai mic dintre anul maxim al utilizatorului și cel din baza de date
                optimized_max = min(user_max_year, db_max_year)
        
        return optimized_min, optimized_max
    
    def normalize_model_name(self, make: str, model: str) -> str:
        """
        Normalizează numele modelului pentru matching mai bun
        """
        make_lc = make.lower().strip()
        model_lc = model.lower().strip()
        
        # Mapări specifice pentru modele BMW
        if make_lc == "bmw":
            # BMW numeric models: 320d -> seria-3, 520d -> seria-5
            m = re.match(r"^(x)?(\d)", model_lc)
            if m:
                is_x = m.group(1) == "x"
                digit = m.group(2)
                if is_x:
                    return f"x{digit}"
                return f"seria-{digit}"
        
        # Mapări specifice pentru modele Audi
        elif make_lc == "audi":
            # Audi A4, A6, etc. -> a4, a6
            m = re.match(r"^([aq])(\d+)", model_lc)
            if m:
                series = m.group(1)
                number = m.group(2)
                return f"{series}{number}"
        
        # Mapări specifice pentru modele Mercedes
        elif make_lc in ["mercedes", "mercedesbenz"]:
            # Mercedes C220d, E220d, etc. -> c, e
            m = re.match(r"^([a-z])", model_lc)
            if m:
                return m.group(1)
        
        return model_lc
    
    def update_search_stats(self, make: str, model: str, avg_price: float = None,
                           avg_year: float = None, avg_km: float = None):
        """Actualizează statisticile de căutare"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO search_stats 
            (make, model, search_count, last_searched, avg_price, avg_year, avg_km)
            VALUES (?, ?, 
                COALESCE((SELECT search_count FROM search_stats WHERE make = ? AND model = ?), 0) + 1,
                CURRENT_TIMESTAMP, ?, ?, ?)
        """, (make.lower(), model.lower(), make.lower(), model.lower(), 
              avg_price, avg_year, avg_km))
        
        conn.commit()
        conn.close()
    
    def get_popular_models(self, make: str = None, limit: int = 10) -> List[Dict]:
        """Obține modelele cele mai căutate"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if make:
            cursor.execute("""
                SELECT make, model, search_count, avg_price, avg_year, avg_km
                FROM search_stats 
                WHERE make = ?
                ORDER BY search_count DESC, last_searched DESC
                LIMIT ?
            """, (make.lower(), limit))
        else:
            cursor.execute("""
                SELECT make, model, search_count, avg_price, avg_year, avg_km
                FROM search_stats 
                ORDER BY search_count DESC, last_searched DESC
                LIMIT ?
            """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'make': r[0],
                'model': r[1],
                'search_count': r[2],
                'avg_price': r[3],
                'avg_year': r[4],
                'avg_km': r[5]
            }
            for r in results
        ]

    def get_model_stats(self, make: str, model: str) -> Optional[Dict]:
        """Obține statistici pentru un model specific"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT make, model, search_count, avg_price, avg_year, avg_km, last_searched
            FROM search_stats 
            WHERE make = ? AND model = ?
        """, (make.lower(), model.lower()))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'make': result[0],
                'model': result[1],
                'search_count': result[2],
                'avg_price': result[3],
                'avg_year': result[4],
                'avg_km': result[5],
                'last_searched': result[6]
            }
        return None
    
    def populate_sample_data(self):
        """Populează baza de date cu date de exemplu"""
        sample_models = [
            # BMW
            ("bmw", "seria-3", 2012, 2024, "F30/G20", "sedan", ["320d", "330d", "320i", "330i"], ["diesel", "petrol"]),
            ("bmw", "seria-5", 2010, 2024, "F10/G30", "sedan", ["520d", "530d", "520i", "530i"], ["diesel", "petrol"]),
            ("bmw", "x3", 2010, 2024, "F25/G01", "suv", ["x3", "xdrive30d", "xdrive20d"], ["diesel", "petrol"]),
            ("bmw", "x5", 2006, 2024, "E70/F15/G05", "suv", ["x5", "xdrive30d", "xdrive40d"], ["diesel", "petrol"]),
            
            # Audi
            ("audi", "a4", 2008, 2024, "B8/B9", "sedan", ["a4", "avant", "allroad"], ["diesel", "petrol"]),
            ("audi", "a6", 2011, 2024, "C7/C8", "sedan", ["a6", "avant", "allroad"], ["diesel", "petrol"]),
            ("audi", "q5", 2008, 2024, "8R/FY", "suv", ["q5", "sq5"], ["diesel", "petrol"]),
            ("audi", "q7", 2006, 2024, "4L/4M", "suv", ["q7", "sq7"], ["diesel", "petrol"]),
            
            # Mercedes
            ("mercedes", "c", 2007, 2024, "W204/W205", "sedan", ["c220d", "c250d", "c200", "c250"], ["diesel", "petrol"]),
            ("mercedes", "e", 2009, 2024, "W212/W213", "sedan", ["e220d", "e250d", "e200", "e250"], ["diesel", "petrol"]),
            ("mercedes", "g", 2005, 2024, "W463", "suv", ["g350d", "g500", "g63"], ["diesel", "petrol"]),
            
            # Volkswagen
            ("volkswagen", "golf", 2008, 2024, "Mk6/Mk7/Mk8", "hatchback", ["golf", "gti", "gtd"], ["diesel", "petrol"]),
            ("volkswagen", "passat", 2010, 2024, "B7/B8", "sedan", ["passat", "passat-variant"], ["diesel", "petrol"]),
            ("volkswagen", "tiguan", 2007, 2024, "5N/AD1", "suv", ["tiguan", "tiguan-allspace"], ["diesel", "petrol"]),
            
            # Skoda
            ("skoda", "octavia", 2013, 2024, "Mk3/Mk4", "sedan", ["octavia", "octavia-combi"], ["diesel", "petrol"]),
            ("skoda", "superb", 2008, 2024, "3T/3V", "sedan", ["superb", "superb-combi"], ["diesel", "petrol"]),
            ("skoda", "kodiaq", 2017, 2024, "NS", "suv", ["kodiaq"], ["diesel", "petrol"]),
        ]
        
        for model_data in sample_models:
            self.add_car_model(*model_data)
    
    def populate_from_scraper(self, max_brands: int = None, max_models_per_brand: int = None):
        """Populează baza de date cu date din scraper-ul auto-data.net"""
        from auto_data_scraper import AutoDataScraper
        
        scraper = AutoDataScraper(self)
        print("Încep popularea bazei de date cu date din auto-data.net...")
        
        data = scraper.scrape_all_data(max_brands, max_models_per_brand)
        
        print(f"Popularea s-a terminat. Am procesat {len(data)} modele.")
        return data

    def add_alert(self, user_email: str, make: str, model: str, max_price: int):
        """Adaugă o alertă nouă în baza de date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alerts (user_email, make, model, max_price, last_checked)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_email, make, model, max_price))
        
        # Get the ID of the new row
        alert_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return {
            "id": alert_id,
            "user_email": user_email,
            "make": make,
            "model": model,
            "max_price": max_price
        }

    def get_alerts(self):
        """Obține toate alertele active"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Pentru a accesa coloanele prin nume
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM alerts")
        rows = cursor.fetchall()
        
        alerts = []
        for row in rows:
            alerts.append(dict(row))
            
        conn.close()
        return alerts

    def get_all_brands(self) -> List[str]:
        """Obține toate mărcile distincte din baza de date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT make FROM car_models ORDER BY make ASC")
        rows = cursor.fetchall()
        
        brands = [self.format_brand_name(row[0]) for row in rows if row[0]]
        conn.close()
        return sorted(list(set(brands)))

    def get_models(self, make: str) -> List[str]:
        """Obține toate modelele pentru o marcă din baza de date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT model FROM car_models WHERE make = ? ORDER BY model ASC", (make.lower(),))
        rows = cursor.fetchall()
        
        models = [self.format_model_name(row[0]) for row in rows if row[0]]
        conn.close()
        return sorted(list(set(models)))


# Instanță globală pentru optimizator
car_db_optimizer = CarDatabaseOptimizer()


def get_optimized_search_params(make: str, model: str, 
                               user_min_year: int = None, 
                               user_max_year: int = None,
                               generation: str = None) -> Dict:
    """
    Funcție helper pentru a obține parametrii optimizați de căutare
    """
    optimized_min_year, optimized_max_year = car_db_optimizer.get_optimized_year_range(
        make, model, user_min_year, user_max_year, generation
    )
    
    model_info = car_db_optimizer.get_model_info(make, model)
    generations = car_db_optimizer.get_generations_for_model(make, model)
    
    return {
        'min_year': optimized_min_year,
        'max_year': optimized_max_year,
        'model_info': model_info,
        'generations': generations,
        'selected_generation': generation,
        'normalized_model': car_db_optimizer.normalize_model_name(make, model)
    }
