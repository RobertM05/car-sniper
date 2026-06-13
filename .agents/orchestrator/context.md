# Project Context - Deal of the Day

## Current State
- The project is initialized.
- Global `PROJECT.md` has been defined with milestones.
- Heartbeat cron has been scheduled.
- The project is starting Milestone 1 (Setup & Verification).

## Environment Info
- Backend: FastAPI, running on port 8000, connecting to a PostgreSQL Supabase database.
- Frontend: React + Vite, running on port 5173.
- Database: Supabase PostgreSQL (`DATABASE_URL` is set in `backend/.env`).
- Database constraints: No schema changes, no data modification, read-only queries for deal retrieval.
