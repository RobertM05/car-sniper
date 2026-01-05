# 🚗 Car Sniper - Sistem de Optimizare Căutări Auto

## Descriere

Car Sniper este un sistem complet de căutare și optimizare pentru mașini second-hand, care integrează scraping-ul de pe site-uri precum OLX și Autovit cu o bază de date optimizată pentru informații despre modelele de mașini.

## ✨ Funcționalități Principale

### 1. **Căutare Optimizată cu Filtre**
- ✅ Pret minim și maxim
- ✅ An minim și maxim  
- ✅ Kilometraj maxim
- ✅ Capacitate cilindrică minimă
- ✅ Putere minimă (CP)

### 2. **Bază de Date Auto Optimizată**
- 📊 Informații despre modelele de mașini
- 📅 Anii de producție (min/max)
- 🏷️ Generații de modele
- 🚙 Tipuri de caroserie
- ⚙️ Tipuri de motoare
- 📈 Statistici de căutare

### 3. **Scraper Auto-Data.net**
- 🌐 Scraping automat de pe auto-data.net
- 📋 Extragere mărci și modele
- 🔍 Detalii despre specificații
- 📊 Populare automată a bazei de date

### 4. **Optimizare Inteligentă**
- 🎯 Matching automat între căutări și baza de date
- 🔧 Normalizare nume modele (BMW 320d → seria-3)
- 📊 Parametrii optimizați pentru fiecare model
- 📈 Statistici de utilizare

## 🏗️ Arhitectura Sistemului

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │   Database      │
│   (React)       │◄──►│   (FastAPI)      │◄──►│   (SQLite)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Scrapers       │
                       │ OLX + Autovit    │
                       │ + Auto-Data.net  │
                       └──────────────────┘
```

## 📁 Structura Proiectului

```
car-sniper/
├── backend/
│   ├── car_database.py      # Modul optimizare bază de date
│   ├── auto_data_scraper.py # Scraper auto-data.net
│   ├── functii.py           # Funcții principale de căutare
│   ├── main.py              # API FastAPI
│   ├── scraper/
│   │   ├── olx_scraper.py   # Scraper OLX
│   │   └── autovit_scraper.py # Scraper Autovit
│   └── test_system.py       # Script de test
├── frontend/
│   └── car-sniper/          # Aplicația React
├── database/
│   └── db.sqlite            # Baza de date SQLite
└── requirements.txt
```

## 🚀 Instalare și Configurare

### 1. Instalare Dependențe

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# sau venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend
cd frontend/car-sniper
npm install
```

### 2. Inițializare Bază de Date

```bash
cd backend
source venv/bin/activate
python -c "from car_database import car_db_optimizer; car_db_optimizer.populate_sample_data()"
```

### 3. Pornire Servicii

```bash
# Backend (terminal 1)
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Frontend (terminal 2)
cd frontend/car-sniper
npm run dev
```

## 🔧 Utilizare

### API Endpoints Principale

#### Căutare Mașini
```http
GET /api/search?make=bmw&model=seria-3&max_price=15000&min_price=5000&min_year=2015&max_year=2020
```

#### Informații Model
```http
GET /api/model-info/bmw/seria-3
```

#### Parametrii Optimizați
```http
GET /api/optimized-search-params/bmw/seria-3?min_year=2015&max_year=2020
```

#### Populare Bază de Date
```http
POST /api/populate-from-scraper?max_brands=5&max_models_per_brand=3
```

#### Test Scraper
```http
GET /api/test-scraper
```

### Exemple de Utilizare

#### 1. Căutare Simplă
```python
from functii import search_cars

results = search_cars(
    make="bmw",
    model="320d", 
    max_price=15000,
    min_price=5000,
    site="both",
    min_year=2015,
    max_year=2020
)
```

#### 2. Optimizare cu Bază de Date
```python
from car_database import get_optimized_search_params

params = get_optimized_search_params("bmw", "320d", 2015, 2020)
print(f"Ani optimizați: {params['min_year']} - {params['max_year']}")
```

#### 3. Scraping Auto-Data.net
```python
from auto_data_scraper import AutoDataScraper

scraper = AutoDataScraper()
brands = scraper.scrape_brands()
models = scraper.scrape_models_for_brand(brands[0]['url_marca'], brands[0]['nume_marca'])
```

## 🧪 Testare

Rulează scriptul de test pentru a verifica funcționalitatea completă:

```bash
cd backend
source venv/bin/activate
python test_system.py
```

## 📊 Funcționalități Avansate

### 1. **Normalizare Modele**
- BMW 320d → seria-3
- Audi A4 → a4  
- Mercedes C220d → c

### 2. **Optimizare Parametrii**
- Combină preferințele utilizatorului cu informațiile din baza de date
- Ajustează automat intervalul de ani pentru fiecare model
- Elimină căutările irelevante

### 3. **Statistici de Utilizare**
- Urmărește modelele cele mai căutate
- Calculează prețuri și kilometraj mediu
- Optimizează rezultatele bazate pe istoricul de căutări

### 4. **Scraping Inteligent**
- Rate limiting pentru a respecta termenii de utilizare
- Parsing robust pentru diverse formate de date
- Gestionare erori și retry logic

## 🔮 Dezvoltări Viitoare

- [ ] Integrare cu mai multe site-uri de anunțuri
- [ ] Machine Learning pentru predicții de preț
- [ ] Notificări push pentru anunțuri noi
- [ ] Comparare modele și recomandări
- [ ] Dashboard admin pentru gestionare date
- [ ] API pentru aplicații mobile

## 🤝 Contribuții

Contribuțiile sunt binevenite! Pentru a contribui:

1. Fork repository-ul
2. Creează un branch pentru feature (`git checkout -b feature/AmazingFeature`)
3. Commit modificările (`git commit -m 'Add some AmazingFeature'`)
4. Push la branch (`git push origin feature/AmazingFeature`)
5. Deschide un Pull Request

## 📄 Licență

Acest proiect este licențiat sub MIT License - vezi fișierul [LICENSE](LICENSE) pentru detalii.

## 📞 Contact

Pentru întrebări sau sugestii, deschide un issue pe GitHub sau contactează-mă direct.

---

**Car Sniper** - Găsește mașina perfectă cu optimizare inteligentă! 🚗✨
