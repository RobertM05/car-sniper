## 2026-06-10T15:46:45Z

Analyze the FastAPI backend to plan the implementation of `/api/deals/top`. Identify the files to modify (typically `backend/core_app.py` and possibly `backend/car_database.py` if a new db helper function is needed).
Requirements:
- Fetch up to 5 car deals from the database.
- The deals must be active (active = TRUE).
- The deals must be added/updated within the last 48 hours.
- The deals must be sorted by their calculated Deal Score (highest first).
- Calculate Deal Score by finding peers of the same make/model (same year +/- 2 years) in all active ads from the database, or using the model stats if peers are fewer than 3, just like how `calculate_deal_scores` is used in `api_search`.
- Read-only queries only. No database schema changes, table drops, or deletion of data.

Suggest the exact code changes and how they fit into the existing backend architecture. Write your proposal to a file named handoff.md in your working directory (/Users/robert/car-sniper/.agents/explorer_backend). Report back with a message containing your recommendations.
