"""
Auto-Data.net Scraper
Scraper pentru extragerea informațiilor despre modelele de mașini de pe auto-data.net
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
import sqlite3
import json
import re
from typing import Dict, List, Optional, Tuple
from car_database import CarDatabaseOptimizer

# Adresa URL de bază a site-ului
BASE_URL = "https://www.auto-data.net"
# URL-ul paginii care conține toate mărcile
ALL_BRANDS_URL = "https://www.auto-data.net/ro/allbrands"

# Setăm un User-Agent pentru a simula un browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

class AutoDataScraper:
    def __init__(self, db_optimizer: CarDatabaseOptimizer = None):
        self.db_optimizer = db_optimizer or CarDatabaseOptimizer()
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def get_page_content(self, url: str) -> Optional[str]:
        """Descarcă conținutul HTML al unei pagini."""
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Eroare la accesarea {url}: Status {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Eroare de rețea: {e}")
            return None
    
    def scrape_brands(self) -> List[Dict]:
        """Extrage toate mărcile și link-urile lor de pe pagina principală."""
        print("Încep extragerea mărcilor...")
        html_content = self.get_page_content(ALL_BRANDS_URL)
        
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        brands_list = []
        
        # Selectorul pentru mărci pe auto-data.net
        brand_elements = soup.find_all('a', class_='marki_blok')
        
        if not brand_elements:
            print("Selectorul pentru mărci nu a fost găsit.")
            return []

        for element in brand_elements:
            brand_name = element.text.strip() 
            brand_url_partial = element.get('href')
            
            if brand_name and brand_url_partial:
                brand_full_url = BASE_URL + brand_url_partial
                brands_list.append({
                    'nume_marca': brand_name,
                    'url_marca': brand_full_url
                })
                
        print(f"Am găsit {len(brands_list)} mărci.")
        return brands_list
    
    def scrape_models_for_brand(self, brand_url: str, brand_name: str) -> List[Dict]:
        """Extrage toate modelele pentru o marcă specifică."""
        print(f"Extrag modelele pentru {brand_name}...")
        html_content = self.get_page_content(brand_url)
        
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        models_list = []
        
        # Selectorul pentru modele - poate varia în funcție de structura paginii
        model_elements = soup.find_all('a', class_='modeli_blok')
        
        if not model_elements:
            # Încercăm alte selectori posibile
            model_elements = soup.find_all('a', href=re.compile(r'/ro/.*-model-'))
        
        for element in model_elements:
            model_name = element.text.strip()
            model_url_partial = element.get('href')
            
            if model_name and model_url_partial:
                model_full_url = BASE_URL + model_url_partial
                models_list.append({
                    'marca': brand_name,
                    'model': model_name,
                    'url_model': model_full_url
                })
        
        print(f"Am găsit {len(models_list)} modele pentru {brand_name}")
        return models_list
    
    def scrape_model_details(self, model_url: str, brand_name: str, model_name: str) -> Optional[Dict]:
        """Extrage detaliile pentru un model specific."""
        print(f"Extrag detaliile pentru {brand_name} {model_name}...")
        html_content = self.get_page_content(model_url)
        
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extragem informațiile despre anii de producție
        years_info = self._extract_years_info(soup)
        
        # Extragem informațiile despre tipul de caroserie
        body_type = self._extract_body_type(soup)
        
        # Extragem informațiile despre motoare
        engines_info = self._extract_engines_info(soup)
        
        # Extragem generația modelului
        generation = self._extract_generation(soup)
        
        return {
            'make': brand_name.lower(),
            'model': model_name.lower(),
            'min_year': years_info.get('min_year'),
            'max_year': years_info.get('max_year'),
            'body_type': body_type,
            'generation': generation,
            'engines': engines_info,
            'url': model_url
        }
    
    def _extract_years_info(self, soup: BeautifulSoup) -> Dict:
        """Extrage informațiile despre anii de producție."""
        years = []
        
        # Căutăm elemente care conțin ani
        year_elements = soup.find_all(text=re.compile(r'19\d{2}|20\d{2}'))
        
        for element in year_elements:
            year_match = re.search(r'(19\d{2}|20\d{2})', element)
            if year_match:
                year = int(year_match.group(1))
                if 1950 <= year <= 2025:  # Filtru pentru ani realiști
                    years.append(year)
        
        # Căutăm și în link-uri sau alte elemente
        links = soup.find_all('a', href=re.compile(r'year|an'))
        for link in links:
            year_match = re.search(r'(19\d{2}|20\d{2})', link.get('href', ''))
            if year_match:
                year = int(year_match.group(1))
                if 1950 <= year <= 2025:
                    years.append(year)
        
        if years:
            return {
                'min_year': min(years),
                'max_year': max(years),
                'all_years': sorted(list(set(years)))
            }
        
        return {'min_year': None, 'max_year': None, 'all_years': []}
    
    def _extract_body_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrage tipul de caroserie."""
        # Căutăm cuvinte cheie pentru tipul de caroserie
        body_types = ['sedan', 'hatchback', 'suv', 'coupe', 'convertible', 'wagon', 'pickup', 'van']
        
        page_text = soup.get_text().lower()
        
        for body_type in body_types:
            if body_type in page_text:
                return body_type
        
        # Căutăm în română
        romanian_body_types = {
            'berlina': 'sedan',
            'hatchback': 'hatchback',
            'suv': 'suv',
            'coupe': 'coupe',
            'cabrio': 'convertible',
            'break': 'wagon',
            'pickup': 'pickup',
            'furgoneta': 'van'
        }
        
        for ro_type, en_type in romanian_body_types.items():
            if ro_type in page_text:
                return en_type
        
        return None
    
    def _extract_generation(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrage generația modelului."""
        # Căutăm coduri de generație (ex: F30, G20, B8, etc.)
        generation_patterns = [
            r'([A-Z]\d{2})',  # F30, G20, etc.
            r'([A-Z]\d)',     # B8, C7, etc.
            r'(Mk\d+)',       # Mk6, Mk7, etc.
            r'(W\d+)',        # W204, W205, etc.
        ]
        
        page_text = soup.get_text()
        
        for pattern in generation_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                return matches[0]  # Returnează prima generație găsită
        
        return None
    
    def _extract_engines_info(self, soup: BeautifulSoup) -> List[str]:
        """Extrage informațiile despre motoare."""
        engines = []
        
        # Căutăm informații despre motoare
        engine_elements = soup.find_all(text=re.compile(r'\d+\.\d+[LT]|\d+cc|\d+HP|\d+CP'))
        
        for element in engine_elements:
            # Extragem capacitatea motorului
            cc_match = re.search(r'(\d+\.\d+[LT]|\d+cc)', element)
            if cc_match:
                engines.append(cc_match.group(1))
        
        return list(set(engines))  # Eliminăm duplicatele
    
    def scrape_all_data(self, max_brands: int = None, max_models_per_brand: int = None) -> List[Dict]:
        """Scrapează toate datele pentru toate mărcile și modelele."""
        brands = self.scrape_brands()
        
        if max_brands:
            brands = brands[:max_brands]
        
        all_models_data = []
        
        for i, brand in enumerate(brands):
            print(f"\nProcesez marca {i+1}/{len(brands)}: {brand['nume_marca']}")
            
            models = self.scrape_models_for_brand(brand['url_marca'], brand['nume_marca'])
            
            if max_models_per_brand:
                models = models[:max_models_per_brand]
            
            for j, model in enumerate(models):
                print(f"  Procesez modelul {j+1}/{len(models)}: {model['model']}")
                
                model_details = self.scrape_model_details(
                    model['url_model'], 
                    model['marca'], 
                    model['model']
                )
                
                if model_details:
                    all_models_data.append(model_details)
                    
                    # Adăugăm în baza de date
                    self.db_optimizer.add_car_model(
                        make=model_details['make'],
                        model=model_details['model'],
                        min_year=model_details['min_year'],
                        max_year=model_details['max_year'],
                        generation=model_details['generation'],
                        body_type=model_details['body_type'],
                        engine_types=model_details['engines']
                    )
                
                # Pauză între cereri pentru a nu suprasolicita serverul
                time.sleep(1)
            
            # Pauză mai mare între mărci
            time.sleep(2)
        
        return all_models_data
    
    def save_to_csv(self, data: List[Dict], filename: str = 'auto_data_models.csv'):
        """Salvează datele într-un fișier CSV."""
        if not data:
            print("Nu există date de salvat.")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['make', 'model', 'min_year', 'max_year', 'body_type', 'generation', 'engines', 'url']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                # Convertim lista de motoare în string pentru CSV
                row_copy = row.copy()
                row_copy['engines'] = ', '.join(row['engines']) if row['engines'] else ''
                writer.writerow(row_copy)
        
        print(f"Datele au fost salvate în {filename}")


def main():
    """Funcția principală pentru testare."""
    scraper = AutoDataScraper()
    
    # Testăm cu primele 2 mărci și primele 3 modele per marcă
    print("Încep scraping-ul cu limitări pentru test...")
    data = scraper.scrape_all_data(max_brands=2, max_models_per_brand=3)
    
    # Salvăm rezultatele
    scraper.save_to_csv(data)
    
    print(f"\nScraping-ul s-a terminat. Am procesat {len(data)} modele.")
    
    # Afișăm câteva exemple
    for i, model in enumerate(data[:5]):
        print(f"\nExemplu {i+1}:")
        print(f"  Marca: {model['make']}")
        print(f"  Model: {model['model']}")
        print(f"  Ani: {model['min_year']} - {model['max_year']}")
        print(f"  Tip caroserie: {model['body_type']}")
        print(f"  Generație: {model['generation']}")


if __name__ == "__main__":
    main()
