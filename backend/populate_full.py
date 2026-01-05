from auto_data_scraper import AutoDataScraper

def main():
    print("🚀 Starting Database Population...")
    print("This will scrape auto-data.net for car models.")
    print("Press Ctrl+C to stop at any time (data is saved incrementally).")
    
    scraper = AutoDataScraper()
    
    # Putem seta max_brands=None pentru a lua tot, dar pentru început
    # haide să luăm primele 30 de mărci (cele mai populare sunt de obicei primele)
    # și primele 10 modele per marcă.
    
    # Acum rulam pentru TOATE marcile (fara limita)
    data = scraper.scrape_all_data(max_brands=None, max_models_per_brand=None)
    
    print(f"\n✅ Done! Database populated with {len(data)} models.")

if __name__ == "__main__":
    main()
