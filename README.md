<p align="center">
  <img src="https://img.shields.io/badge/CarSniper-v2.0-0ea5e9?style=for-the-badge&labelColor=0a0a0a" alt="version"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=white&labelColor=0a0a0a" alt="react"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=0a0a0a" alt="fastapi"/>
  <img src="https://img.shields.io/badge/Vite-5-646CFF?style=for-the-badge&logo=vite&logoColor=white&labelColor=0a0a0a" alt="vite"/>
  <img src="https://img.shields.io/badge/Vercel-Deployed-000?style=for-the-badge&logo=vercel&logoColor=white&labelColor=0a0a0a" alt="vercel"/>
</p>

<h1 align="center">CarSniper</h1>

<p align="center">
  <strong>Agregator inteligent de anunturi auto SH din Romania</strong><br/>
  Cauta simultan pe <b>OLX</b> si <b>Autovit</b> · Filtre avansate · Alerte email · Analiza piata
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#arhitectura">Arhitectura</a> •
  <a href="#instalare">Instalare</a> •
  <a href="#api-endpoints">API</a> •
  <a href="#deployment">Deployment</a>
</p>

---

## Features

| Feature | Detalii |
|---------|---------|
| **Cautare Unificata** | Scraping simultan pe OLX si Autovit cu un singur query |
| **Slug Intelligence** | 600+ mapari de modele la URL slugs (ex: `BMW 320d` la `seria-3`) |
| **Statistici Piata** | Pret mediu, min, max — calculat live din anunturi reale |
| **Alerte Email** | Notificari automate via [Resend](https://resend.com) cand apare o oferta |
| **Bilingv (RO/EN)** | Interfata completa in romana si engleza |
| **Autentificare** | Register / Login cu bcrypt hashing |
| **B2B Leads** | Formular "Devino Partener" cu lead capture pe email |
| **Background Crawler** | Crawler autonom care verifica periodic anunturi noi si le stocheaza |
| **Responsive Design** | Glassmorphism UI, dark mode, animatii fluide |

---

## Arhitectura

```
+--------------------------------------------------------------+
|                        FRONTEND                              |
|              React 18 + Vite - Glassmorphism UI              |
|                                                              |
|  SearchForm - CarCard - PriceStats - Pagination - Modals     |
|  LanguageContext (RO/EN) - SkeletonCard loading states       |
+---------------------------+----------------------------------+
                            |  REST API (fetch)
                            v
+--------------------------------------------------------------+
|                     BACKEND (FastAPI)                         |
|                                                              |
|  core_app.py --- API Endpoints (/api/search, /api/brands...) |
|  functii.py ---- Search Engine + Slug Translations           |
|  car_database.py - PostgreSQL (Supabase) ORM + Statistics Engine            |
|  mailer.py ----- Email Notifications (Resend API)            |
|  crawler.py ---- Autonomous Background Scraper               |
|                                                              |
|  +----------------------------------------------------+     |
|  |              SCRAPERS                               |     |
|  |  olx_scraper.py --------- aiohttp + JSON API       |     |
|  |  autovit_scraper.py ----- API + BeautifulSoup       |     |
|  |  autovit_playwright.py -- Headless Chromium          |     |
|  +----------------------------------------------------+     |
+---------------------------+----------------------------------+
                            |
                            v
+--------------------------------------------------------------+
|                     DATABASE (PostgreSQL (Supabase))                         |
|                                                              |
|  Ads Storage - User Auth - Alerts - Search Stats             |
|  Stale Ad Cleanup - Model Generation Mapping                 |
+--------------------------------------------------------------+
```

---

## Structura Proiectului

```
car-sniper/
├── backend/
│   ├── core_app.py              # FastAPI app + toate rutele API
│   ├── functii.py               # Motor de cautare, slug mappings, filtre
│   ├── car_database.py          # PostgreSQL (Supabase) ORM, statistici, user management
│   ├── mailer.py                # Notificari email via Resend
│   ├── crawler.py               # Background crawler autonom
│   ├── autovit_catalog.json     # Catalog complet marci/modele
│   ├── main.py                  # Entry point (Vercel + uvicorn)
│   └── scraper/
│       ├── olx_scraper.py       # OLX async scraper (aiohttp)
│       ├── autovit_scraper.py   # Autovit API scraper
│       └── autovit_playwright.py # Autovit headless browser fallback
├── frontend/
│   └── car-sniper/              # React + Vite application
│       └── src/
│           ├── App.jsx          # Main app component
│           ├── App.css          # Design system (dark glassmorphism)
│           ├── LanguageContext.jsx # i18n (romana / english)
│           └── components/
│               ├── SearchForm.jsx    # Formular de cautare
│               ├── CarCard.jsx       # Card anunt auto
│               ├── ResultsList.jsx   # Grid rezultate
│               ├── PriceStats.jsx    # Statistici pret piata
│               ├── Pagination.jsx    # Navigare pagini
│               ├── AlertModal.jsx    # Modal alerta email
│               ├── AuthModal.jsx     # Login / Register
│               ├── ContactModal.jsx  # Devino Partener (B2B)
│               └── SkeletonCard.jsx  # Loading placeholder
├── database/
│   └── db.sqlite                # PostgreSQL (Supabase) database (gitignored)
├── api/                         # Vercel serverless functions
├── vercel.json                  # Vercel deployment config
├── requirements.txt             # Python dependencies
└── start.sh                     # One-command local startup
```

---

## Instalare

### Cerinte
- **Python** 3.10+
- **Node.js** 18+
- **Chromium** (optional, pentru Playwright scraper)

### 1. Clonare

```bash
git clone https://github.com/RobertM05/car-sniper.git
cd car-sniper
```

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r ../requirements.txt

# (Optional) Instalare Playwright pentru scraping avansat
playwright install chromium
```

### 3. Variabile de mediu

Creaza fisierul `backend/.env`:

```env
RESEND_API_KEY=re_xxxxxxxxxxxx    # Pentru alerte email (optional)
```

### 4. Frontend

```bash
cd frontend/car-sniper
npm install
```

### 5. Pornire rapida (tot sistemul)

```bash
chmod +x start.sh
./start.sh
```

Sau manual, in terminale separate:

```bash
# Terminal 1 — Backend
cd backend && source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend/car-sniper
npm run dev
```

| Serviciu | URL |
|----------|-----|
| Frontend | `http://localhost:5173` |
| Backend API | `http://localhost:8000` |
| API Docs (Swagger) | `http://localhost:8000/docs` |

---

## API Endpoints

### Cautare

| Metoda | Endpoint | Descriere |
|--------|----------|-----------|
| `GET` | `/api/search` | Cautare unificata OLX + Autovit |
| `GET` | `/api/brands` | Lista tuturor marcilor disponibile |
| `GET` | `/api/models/{brand}` | Modele pentru o marca |
| `GET` | `/api/generations/{make}/{model}` | Generatii pentru un model |

### Statistici

| Metoda | Endpoint | Descriere |
|--------|----------|-----------|
| `GET` | `/api/stats/{make}/{model}` | Statistici pret (avg, min, max) |
| `GET` | `/api/model-info/{make}/{model}` | Info detaliat model |
| `GET` | `/api/model-year-range/{make}/{model}` | Interval ani productie |

### Utilizatori & Alerte

| Metoda | Endpoint | Descriere |
|--------|----------|-----------|
| `POST` | `/api/auth/register` | Inregistrare cont |
| `POST` | `/api/auth/login` | Autentificare |
| `POST` | `/api/alert` | Creare alerta de pret |
| `POST` | `/api/contact` | Formular B2B "Devino Partener" |

<details>
<summary><strong>Exemplu: Cautare BMW Seria 3 sub 15.000 EUR</strong></summary>

```bash
curl "http://localhost:8000/api/search?make=BMW&model=Seria%203&max_price=15000&site=both&limit=50"
```

**Raspuns:**
```json
{
  "results": [
    {
      "title": "BMW 320d M-Sport 2019",
      "price": 14500,
      "year": 2019,
      "km": 85000,
      "link": "https://www.autovit.ro/anunt/...",
      "image": "https://...",
      "source": "autovit"
    }
  ]
}
```

</details>

---

## Functionalitati Interesante

### Slug Intelligence Engine

Sistemul traduce automat numele modelelor in URL slugs specifice fiecarei platforme:

```
BMW 320d      ->  seria-3       (OLX: bmw/seria-3, Autovit: bmw/seria-3)
Mercedes C220 ->  clasa-c       (OLX: mercedes-benz/clasa-c)
Audi A4       ->  a4            (direct match)
Land Rover    ->  land-rover    (brand slug normalization)
```

### Crawler Autonom

Crawler-ul ruleaza in background si:
- Scaneaza periodic modelele populare pe ambele platforme
- Repara automat anunturi cu imagini sau preturi lipsa
- Detecteaza si dezactiveaza anunturi expirate (ghost ads)
- Rate limiting inteligent cu sleep-uri randomizate

### Deduplicare Cross-Platform

Sistemul elimina duplicatele din OLX si Autovit pe baza link-ului unic, asigurand rezultate curate.

---

## Deployment

### Vercel (Recomandat)

Proiectul include configurare completa pentru Vercel (`vercel.json`):

```bash
# Instalare Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

**Environment Variables** necesare pe Vercel:

| Variabila | Descriere |
|-----------|-----------|
| `RESEND_API_KEY` | API key pentru notificari email |
| `VITE_API_URL` | URL-ul backend-ului (daca hosted separat) |

### Alternativ

Backend-ul poate fi hosted pe **Railway**, **Render**, sau orice platforma care suporta Python + ASGI.

---

## Tech Stack

| Layer | Tehnologii |
|-------|-----------|
| **Frontend** | React 18 - Vite - Vanilla CSS (Glassmorphism) |
| **Backend** | FastAPI - Python 3.10+ - Uvicorn |
| **Scraping** | aiohttp - BeautifulSoup4 - Playwright |
| **Database** | PostgreSQL (Supabase) (embedded) |
| **Email** | Resend API |
| **Deployment** | Vercel (Serverless Functions + Static Build) |

---

## Licenta

Distribuit sub licenta **MIT**. Vezi fisierul [LICENSE](LICENSE) pentru detalii.

---

<p align="center">
  <strong>CarSniper</strong> — Agregator de anunturi auto SH din Romania
  <br/>
  <sub>Built with FastAPI + React</sub>
</p>
