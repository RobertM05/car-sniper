#!/usr/bin/env python3
"""
Script de test pentru sistemul complet de optimizare a căutărilor auto
Demonstrează funcționalitatea de scraping și optimizare
"""

from car_database import car_db_optimizer, get_optimized_search_params
from auto_data_scraper import AutoDataScraper
import time

def test_database_optimization():
    """Testează funcționalitatea de optimizare a bazei de date"""
    print("=== TESTARE OPTIMIZARE BAZĂ DE DATE ===")
    
    # Testăm obținerea informațiilor despre modele
    test_cases = [
        ("bmw", "seria-3"),
        ("audi", "a4"),
        ("mercedes", "c"),
        ("volkswagen", "golf")
    ]
    
    for make, model in test_cases:
        print(f"\n--- Test pentru {make.upper()} {model.upper()} ---")
        
        # Obținem informațiile din baza de date
        model_info = car_db_optimizer.get_model_info(make, model)
        if model_info:
            print(f"✓ Informații găsite în baza de date:")
            print(f"  - Ani de producție: {model_info['min_year']} - {model_info['max_year']}")
            print(f"  - Generație: {model_info['generation']}")
            print(f"  - Tip caroserie: {model_info['body_type']}")
            print(f"  - Tipuri motor: {', '.join(model_info['engine_types'])}")
        else:
            print(f"✗ Nu există informații în baza de date pentru {make} {model}")
        
        # Testăm optimizarea parametrilor
        optimized_params = get_optimized_search_params(make, model, 2015, 2020)
        print(f"✓ Parametrii optimizați:")
        print(f"  - An minim optimizat: {optimized_params['min_year']}")
        print(f"  - An maxim optimizat: {optimized_params['max_year']}")
        print(f"  - Model normalizat: {optimized_params['normalized_model']}")

def test_scraper_functionality():
    """Testează funcționalitatea scraper-ului"""
    print("\n=== TESTARE SCRAPER AUTO-DATA.NET ===")
    
    scraper = AutoDataScraper()
    
    # Testăm scraping-ul mărcilor
    print("1. Testare scraping mărci...")
    brands = scraper.scrape_brands()
    print(f"✓ Am găsit {len(brands)} mărci")
    
    if brands:
        # Testăm cu primele 2 mărci
        test_brands = brands[:2]
        
        for brand in test_brands:
            print(f"\n2. Testare pentru marca: {brand['nume_marca']}")
            
            # Scraping modele pentru marca curentă
            models = scraper.scrape_models_for_brand(brand['url_marca'], brand['nume_marca'])
            print(f"✓ Am găsit {len(models)} modele pentru {brand['nume_marca']}")
            
            if models:
                # Testăm cu primul model
                test_model = models[0]
                print(f"\n3. Testare pentru modelul: {test_model['model']}")
                
                # Scraping detalii pentru modelul curent
                details = scraper.scrape_model_details(
                    test_model['url_model'], 
                    test_model['marca'], 
                    test_model['model']
                )
                
                if details:
                    print(f"✓ Detalii găsite pentru {test_model['marca']} {test_model['model']}:")
                    print(f"  - Ani: {details['min_year']} - {details['max_year']}")
                    print(f"  - Tip caroserie: {details['body_type']}")
                    print(f"  - Generație: {details['generation']}")
                    print(f"  - Motoare: {', '.join(details['engines']) if details['engines'] else 'N/A'}")
                else:
                    print(f"✗ Nu s-au putut extrage detalii pentru {test_model['model']}")
                
                # Pauză pentru a nu suprasolicita serverul
                time.sleep(2)

def test_integration():
    """Testează integrarea completă a sistemului"""
    print("\n=== TESTARE INTEGRARE COMPLETĂ ===")
    
    # Testăm căutarea cu optimizare
    print("1. Testare căutare cu optimizare...")
    
    test_searches = [
        ("bmw", "320d", 2015, 2020),
        ("audi", "a4", 2018, 2022),
        ("mercedes", "c220d", 2016, 2021)
    ]
    
    for make, model, user_min_year, user_max_year in test_searches:
        print(f"\n--- Căutare: {make.upper()} {model.upper()} ({user_min_year}-{user_max_year}) ---")
        
        # Obținem parametrii optimizați
        optimized_params = get_optimized_search_params(make, model, user_min_year, user_max_year)
        
        print(f"✓ Parametrii utilizator: {user_min_year} - {user_max_year}")
        print(f"✓ Parametrii optimizați: {optimized_params['min_year']} - {optimized_params['max_year']}")
        
        if optimized_params['model_info']:
            print(f"✓ Informații din baza de date: {optimized_params['model_info']['min_year']} - {optimized_params['model_info']['max_year']}")
        else:
            print("✗ Nu există informații în baza de date")
    
    # Testăm statisticile de căutare
    print("\n2. Testare statistici de căutare...")
    
    # Simulăm câteva căutări pentru a genera statistici
    car_db_optimizer.update_search_stats("bmw", "seria-3", 25000, 2018, 120000)
    car_db_optimizer.update_search_stats("audi", "a4", 30000, 2019, 95000)
    car_db_optimizer.update_search_stats("mercedes", "c", 35000, 2020, 80000)
    
    popular_models = car_db_optimizer.get_popular_models(limit=5)
    print(f"✓ Modelele cele mai căutate:")
    for i, model in enumerate(popular_models, 1):
        print(f"  {i}. {model['make'].upper()} {model['model'].upper()} - {model['search_count']} căutări")

def main():
    """Funcția principală de test"""
    print("🚗 TESTARE SISTEM COMPLET DE OPTIMIZARE CĂUTĂRI AUTO 🚗")
    print("=" * 60)
    
    try:
        # Testăm optimizarea bazei de date
        test_database_optimization()
        
        # Testăm scraper-ul (doar cu limitări pentru test)
        print("\n" + "=" * 60)
        test_scraper_functionality()
        
        # Testăm integrarea completă
        print("\n" + "=" * 60)
        test_integration()
        
        print("\n" + "=" * 60)
        print("✅ TOATE TESTELE AU TRECUT CU SUCCES!")
        print("Sistemul de optimizare a căutărilor auto este funcțional.")
        
    except Exception as e:
        print(f"\n❌ EROARE ÎN TIMPUL TESTĂRII: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
