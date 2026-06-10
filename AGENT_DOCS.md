# CarSniper - Agent Knowledge Base

Welcome! This document provides a deep dive into the CarSniper project structure, architecture, and quirks to help agents and developers understand the codebase quickly.

## 1. Project Overview
CarSniper is a smart aggregator for used car ads in Romania, fetching data from **OLX** and **Autovit**. It offers unified search, "deal scoring", bilingual support (RO/EN), and email alerts for specific price drops or new listings.

## 2. Technology Stack & Deployment
- **Frontend**: React 18 + Vite. Styled with Vanilla CSS focusing on a Dark Mode "Glassmorphism" UI.
- **Backend**: Python 3.10+ + FastAPI.
- **Database**: **Supabase** (PostgreSQL via `psycopg2`). 
  - *Note*: The `README.md` and `database/db.sqlite` suggest SQLite, but the project has migrated to Supabase for production. `backend/car_database.py` explicitly uses `psycopg2` and expects a `DATABASE_URL` environment variable pointing to the Supabase instance.
- **Scraping Engine**: Uses `aiohttp` for async requests, `beautifulsoup4` for HTML parsing, and `playwright` for headless browser fallback.
- **Deployment & CI/CD**: Vercel & GitHub Actions. 
  - **Vercel**: Handles the main web app deployment. `vercel.json` defines two builds: `@vercel/python` for backend API routes and `@vercel/static-build` for the frontend React application.
  - **GitHub Actions**: Acts as a serverless cron runner. The crawler (`.github/workflows/crawler.yml`) executes every 4 hours to scrape data and populate the Supabase database.

## 3. Directory Structure
```
car-sniper/
├── backend/                  # Core Python/FastAPI logic
│   ├── core_app.py           # API endpoints, deal scoring logic, CORS & Rate Limiting
│   ├── functii.py            # Search core & "Slug Intelligence" (Make/Model mappings)
│   ├── car_database.py       # PostgreSQL DB operations (CRUD, Auth, Stats)
│   ├── mailer.py             # Email notifications via Resend API
│   ├── crawler.py            # Autonomous background scraper to fetch fresh ads
│   └── scraper/              # Platform-specific scraper implementations
│       ├── olx_scraper.py
│       ├── autovit_scraper.py
│       └── autovit_playwright.py
├── frontend/car-sniper/      # React Application
│   ├── src/App.jsx           # Main routing & application state
│   ├── src/LanguageContext.jsx # i18n support (RO/EN)
│   └── src/components/       # Reusable UI components
├── database/                 # Contains legacy SQLite files (no longer actively used by code)
├── vercel.json               # Vercel deployment configuration
├── start.sh                  # Local development startup script
└── requirements.txt          # Python dependencies
```

## 4. Key Mechanisms & Business Logic

### 4.1 Slug Intelligence (`functii.py`)
Car naming conventions differ wildly between OLX and Autovit. `functii.py` contains extensive regex-based logic to normalize search inputs into correct URL slugs. For example, searching "Mercedes C Class" or "BMW 320d" will be correctly translated into `clasa-c` or `seria-3` depending on the target site's URL structure.

### 4.2 Deal Score Algorithm (`core_app.py`)
The `calculate_deal_scores` function evaluates how good a price is.
- It compares the car against "peers" of the same make/model and similar manufacturing year (+/- 2 years).
- A score from 0-100 is generated where 80% weight is on price (cheaper = better) and 20% on mileage (fewer km = better).

### 4.3 Database Storage & Deduplication (`car_database.py`)
Ads are stored in the PostgreSQL `ads` table. Duplicate prevention is handled using a hashed version of the ad's unique URL (`ON CONFLICT(link) DO UPDATE`).

### 4.4 Rate Limiting
The backend utilizes `slowapi` to prevent abuse. Because it's deployed on Vercel, it uses a custom IP extractor (`get_real_ip`) to read the `x-forwarded-for` header, bypassing the Vercel proxy IP.

## 5. Development Guidelines
- **Startup**: Run `./start.sh` from the root directory. This script starts Uvicorn on port 8000 and Vite on port 5173.
- **Database setup**: Ensure you have a local PostgreSQL instance running. Create a database named `car_sniper` or override the connection string by setting `DATABASE_URL` in `backend/.env`.
- **Background Crawler (CI/CD)**: The background crawler (`start_crawler.py`) is heavily reliant on GitHub Actions. It runs on a schedule (`0 */4 * * *`) and connects directly to Supabase using secrets (`DATABASE_URL`). When running locally, it is disabled by default in `start.sh` so as not to consume unnecessary resources.
- **Styling**: Stick to the existing `App.css` variables and classes to maintain the glassmorphism aesthetic. Avoid introducing Tailwind unless explicitly migrating the whole app.
