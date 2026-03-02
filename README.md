# Car Sniper - Advanced Auto Search Engine

## Description

Car Sniper is a robust search engine and aggregation tool for second-hand vehicles. It integrates headless scraping from platforms like OLX and Autovit, utilizing a highly optimized internal database mapping architecture to translate complex car model names into platform-specific URL slugs.

## Core Features

### 1. Optimized Search Parameters
- Minimum and Maximum Price filters
- Production Year bounding
- Maximum Mileage (KM) caps
- Engine Capacity (CC) and Horsepower (HP) targets

### 2. Comprehensive Database Mapping
- Translates over 600 complex vehicle names directly to backend URLs for immediate fetching.
- Supports highly specific generation mapping for all major brands.
- Price, year, and mileage statistics aggregated from search history logic.

### 3. Integrated Web Scraping Architecture
- Asynchronous API endpoints fetching live JSON from backend platform APIs.
- Playwright integration for edge-case URL verification and dynamic content rendering.
- Robust exception handling and rate-limit bypassing algorithms.

## System Architecture

```text
+-----------------+    +------------------+    +-----------------+
|   Frontend      |    |     Backend      |    |   Database      |
|   (React/Vite)  |<-->|   (FastAPI)      |<-->|   (SQLite)      |
+-----------------+    +------------------+    +-----------------+
                              |
                              v
                       +------------------+
                       |   Scrapers       |
                       | OLX + Autovit    |
                       +------------------+
```

## Project Structure

```text
car-sniper/
|-- backend/
|   |-- car_database.py      # Core database optimization module
|   |-- functii.py           # Core search algorithms and slug translations
|   |-- main.py              # FastAPI application initialization
|   |-- scraper/
|   |   |-- olx_scraper.py   # OLX asynchronous request engine
|   |   |-- autovit_playwright.py # Autovit headless browser scraper
|   |   |-- autovit_scraper.py # Fallback API search handler
|-- frontend/
|   |-- car-sniper/          # React Vite application
|-- database/
|   |-- db.sqlite            # Internal application states
|-- requirements.txt
```

## Installation & Environment Setup

### 1. Install Dependencies

```bash
# Backend Setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Playwright Dependencies (Required for Autovit Scraper)
playwright install chromium

# Frontend Setup
cd frontend/car-sniper
npm install
```

### 2. Running the Services

```bash
# Terminal 1: Initialize the FastAPI Application
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2: Initialize the React Frontend
cd frontend/car-sniper
npm run dev
```

## Advanced Functionality

### 1. Model Normalization Algorithm
- BMW 320d -> seria-3
- Audi A4 -> a4  
- Mercedes C220d -> c

### 2. Intelligent Rate Limiting
- Built-in asynchronous sleep routines mapping pagination behavior to mimic human interaction.

## Deployment Notes (Vercel)

The frontend is ready for Vercel deployment. Ensure you define `VITE_API_URL` within your Vercel Production Environment Variables, pointing to the external IP where the FastAPI backend is hosted (e.g., Render, Railway).

## License

This project is licensed under the MIT License - see the LICENSE file for more details.

---

**Car Sniper** - Aggregating targeted automated search results with intelligent database mappings.
