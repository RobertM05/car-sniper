# Project: CarSniper - Deal of the Day

## Architecture
CarSniper is a React/Vite + FastAPI web application using PostgreSQL (Supabase) as the backend database.
- **Backend**: FastAPI app serving APIs. Rutele sunt definite în `backend/core_app.py`. DB helper functions are in `backend/car_database.py`.
- **Frontend**: React application inside `frontend/car-sniper/src`. Components are in `frontend/car-sniper/src/components`.
- **Database**: PostgreSQL database. The main table for car listings is `ads`, containing details like make, model, price, year, km, created_at, updated_at, active.

## Code Layout
- Backend: `/Users/robert/car-sniper/backend`
- Frontend: `/Users/robert/car-sniper/frontend/car-sniper`
- Agent metadata: `/Users/robert/car-sniper/.agents`

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Setup & Verification | Initialize environment, verify DB connectivity, audit setup | None | DONE |
| 2 | Backend: Deal of the Day API | Create `/api/deals/top` endpoint in FastAPI backend | M1 | DONE |
| 3 | Frontend: DealOfTheDay Component | Create `DealOfTheDay` React component and integrate it | M2 | DONE |
| 4 | E2E Testing & Hardening | Write E2E test cases, execute test verification, run Forensic Auditor | M3 | DONE |

## Interface Contracts
### Backend Endpoint `/api/deals/top`
- **Method**: `GET`
- **Description**: Fetches top 5 active deals from the database added/updated in the last 48 hours, sorted by calculated Deal Score descending.
- **Request Parameters**: None
- **Response Format**:
  ```json
  [
    {
      "id": "string",
      "source": "string",
      "title": "string",
      "price": "string", // e.g. "12000 €"
      "currency": "string",
      "link": "string",
      "image": "string",
      "make": "string",
      "model": "string",
      "year": 1234,
      "km": 12345,
      "fuel": "string",
      "transmission": "string",
      "body_type": "string",
      "city": "string",
      "created_at": "string",
      "updated_at": "string",
      "last_seen": "string",
      "active": true,
      "deal_score": 95
    }
  ]
  ```
