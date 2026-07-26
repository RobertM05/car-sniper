# Motorbit — Car Deal Aggregator for Romania

Aggregates listings from OLX.ro and Autovit.ro. Scores deals vs market average. Dealer platform with Stripe subscriptions.

## Quick Start
```sh
./start.sh                           # Both frontend + backend
cd frontend/car-sniper && npm run dev  # Frontend only
cd backend && uvicorn main:app --reload  # Backend only
```

## Stack
React 19 + Vite | Python FastAPI | PostgreSQL (Supabase) | Stripe | Resend

## Key Files
- `frontend/car-sniper/src/App.jsx` — Routes + global state (~650 lines)
- `frontend/car-sniper/src/App.css` — All styles (~1900 lines)
- `backend/core_app.py` — FastAPI: 25+ endpoints, JWT, Stripe
- `backend/car_database.py` — PostgreSQL: tables, queries (~1800 lines)
- `backend/functii.py` — Scraper logic, deal scoring, price parsing
- `docs/CONTEXT.md` — Full architecture map (routes, components, DB schema)
- `docs/audit-issues.md` — 156-item tracker

## Design System
- Light default (white/gray), dark via `.dark` class (navy #0f172a)
- Emerald green `#10b981`, DM Sans font
- 20 components, 9 routes, full RO/EN i18n

## Before Editing
- Always read `docs/CONTEXT.md` first for full architecture context
- Run `npm run build` after frontend changes
- Run `python3 -m py_compile` after backend changes
- Run `ruff check backend/ && ruff format backend/` before commits
- NEVER use `git add .` — it pulls in venv noise. Stage specific files only.
- Commits must pass `.githooks/` checks: no AI markers in code, no trailing whitespace, clean commit messages
