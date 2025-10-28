#!/usr/bin/env python3
"""
Script de demonstrație pentru sistemul de matching Ani ↔ Generații
Demonstrează cum funcționează optimizarea cu generații de modele
"""

from car_database import car_db_optimizer, get_optimized_search_params

def demonstrate_generation_matching():
    """Demonstrează matching-ul între ani și generații"""
    print("🎯 DEMONSTRAȚIE MATCHING ANI ↔ GENERAȚII")
    print("=" * 60)
    
    # Teste pentru BMW Seria 3
    print("\n🚗 BMW SERIA 3 - Generații Disponibile:")
    generations = car_db_optimizer.get_generations_for_model("bmw", "seria-3")
    
    for i, gen in enumerate(generations, 1):
        print(f"  {i}. {gen['generation']} ({gen['min_year']}-{gen['max_year']}) - {gen['body_type']}")
        print(f"     Motore: {', '.join(gen['engine_types'])}")
    
    print("\n" + "=" * 60)
    
    # Teste pentru diferite scenarii de căutare
    test_scenarios = [
        {
            "name": "Căutare cu generație specifică",
            "make": "bmw",
            "model": "seria-3", 
            "generation": "F30",
            "user_min_year": None,
            "user_max_year": None
        },
        {
            "name": "Căutare cu generație + restricții utilizator",
            "make": "bmw",
            "model": "seria-3",
            "generation": "F30", 
            "user_min_year": 2015,
            "user_max_year": 2017
        },
        {
            "name": "Căutare fără generație specificată",
            "make": "bmw",
            "model": "seria-3",
            "generation": None,
            "user_min_year": 2015,
            "user_max_year": 2020
        },
        {
            "name": "Căutare Audi A4 cu generație",
            "make": "audi",
            "model": "a4",
            "generation": "B8",
            "user_min_year": None,
            "user_max_year": None
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 {scenario['name'].upper()}")
        print(f"   Marca: {scenario['make'].upper()}")
        print(f"   Model: {scenario['model'].upper()}")
        print(f"   Generația: {scenario['generation'] or 'Nu specificată'}")
        print(f"   Ani utilizator: {scenario['user_min_year'] or 'Minim'} - {scenario['user_max_year'] or 'Maxim'}")
        
        # Obținem parametrii optimizați
        params = get_optimized_search_params(
            scenario['make'],
            scenario['model'], 
            scenario['user_min_year'],
            scenario['user_max_year'],
            scenario['generation']
        )
        
        print(f"   ✅ Ani optimizați: {params['min_year']} - {params['max_year']}")
        print(f"   ✅ Model normalizat: {params['normalized_model']}")
        
        if params['generations']:
            print(f"   ✅ Generații disponibile: {len(params['generations'])}")
            for gen in params['generations']:
                print(f"      - {gen['generation']} ({gen['min_year']}-{gen['max_year']})")

def demonstrate_year_to_generation_mapping():
    """Demonstrează cum se mapează anii la generații"""
    print("\n" + "=" * 60)
    print("🔄 MAPAREA ANI → GENERAȚII")
    print("=" * 60)
    
    # Teste pentru diferite ani BMW Seria 3
    test_years = [2007, 2010, 2013, 2016, 2019, 2022]
    
    print("\n📅 BMW Seria 3 - Maparea anilor la generații:")
    for year in test_years:
        generations = car_db_optimizer.get_generations_for_model("bmw", "seria-3")
        
        matching_generation = None
        for gen in generations:
            if gen['min_year'] <= year <= gen['max_year']:
                matching_generation = gen['generation']
                break
        
        if matching_generation:
            print(f"   {year} → {matching_generation}")
        else:
            print(f"   {year} → Nu se încadrează în nicio generație")

def demonstrate_search_optimization():
    """Demonstrează optimizarea căutărilor cu generații"""
    print("\n" + "=" * 60)
    print("🔍 OPTIMIZAREA CĂUTĂRILOR CU GENERAȚII")
    print("=" * 60)
    
    # Simulăm o căutare reală
    print("\n🎯 Exemplu practic:")
    print("   Utilizatorul caută: BMW Seria 3, generația F30")
    print("   Sistemul automat:")
    
    # Obținem intervalul pentru F30
    min_year, max_year = car_db_optimizer.get_year_range_for_generation("bmw", "seria-3", "F30")
    print(f"   1. Identifică intervalul F30: {min_year}-{max_year}")
    
    # Obținem parametrii optimizați
    params = get_optimized_search_params("bmw", "seria-3", None, None, "F30")
    print(f"   2. Calculează parametrii optimizați: {params['min_year']}-{params['max_year']}")
    
    print(f"   3. Normalizează modelul: '320d' → '{params['normalized_model']}'")
    print(f"   4. Caută pe OLX/Autovit: 'BMW {params['normalized_model']}' din {params['min_year']}-{params['max_year']}")
    
    print("\n✅ Rezultat: Căutare precisă și relevante!")

def main():
    """Funcția principală de demonstrație"""
    print("🚗 SISTEM DE MATCHING ANI ↔ GENERAȚII 🚗")
    print("Demonstrație funcționalitate completă")
    
    try:
        # Demonstrație matching generații
        demonstrate_generation_matching()
        
        # Demonstrație mapare ani → generații
        demonstrate_year_to_generation_mapping()
        
        # Demonstrație optimizare căutări
        demonstrate_search_optimization()
        
        print("\n" + "=" * 60)
        print("✅ DEMONSTRAȚIA S-A TERMINAT CU SUCCES!")
        print("Sistemul de matching Ani ↔ Generații este funcțional.")
        
    except Exception as e:
        print(f"\n❌ EROARE ÎN TIMPUL DEMONSTRAȚIEI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
