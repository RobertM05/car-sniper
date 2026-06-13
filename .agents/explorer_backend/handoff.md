# Implementation Proposal: Top Deals Endpoint `/api/deals/top`

## 1. Observation
- **Endpoint Structure**: Existing API routes are declared in `backend/core_app.py` using FastAPI and standard decorators. The `/api/search` route is defined at lines 118–150 of `backend/core_app.py`.
- **Database Access Pattern**: The `backend/car_database.py` file exports a `car_db_optimizer` instance of the `CarDatabaseOptimizer` class. This class uses `psycopg2` to execute SQL queries on a PostgreSQL database. It exposes methods such as `search_ads_db` (lines 206–248) and `get_model_stats` (lines 502–514).
- **Ad Model Schema**: The `ads` table schema (lines 125–146 in `backend/car_database.py`) has fields including `active` (boolean, defaults to `TRUE`), `updated_at` (timestamp, defaults to `CURRENT_TIMESTAMP`), and `price` (integer).
- **Deal Score Computation**: Deal scores are calculated by the in-memory helper function `calculate_deal_scores(results: list, stats: dict) -> list` located in `backend/core_app.py` (lines 60–116). This helper identifies peer ads of the same make/model (within +/- 2 years) from the input list, calculating a weighted score (80% price, 20% km), and falls back to model-wide statistics when peer count is less than 3.
- **Frontend Price Requirements**: The frontend rendering component `CarCard.jsx` (specifically lines 8–18 in `frontend/car-sniper/src/components/CarCard.jsx`) expects prices to be formatted, and the existing API returns them formatted as strings with the suffix `" €"` (e.g. `d['price'] = f"{d['price']} €"` in `search_ads_db`, line 246).

## 2. Logic Chain
- To implement `/api/deals/top` without changing the database schema or modifying existing table contents, all operations must be read-only select queries followed by in-memory processing.
- To meet the condition of "added/updated within the last 48 hours", we must select ads where `updated_at >= NOW() - CAST('48 hours' AS interval)` in PostgreSQL.
- To compare each candidate ad against its true peer group ("peers of the same make/model in all active ads from the database"), we cannot simply run `calculate_deal_scores` on the 48-hour candidates alone. Candidates must be compared to the entire active database population of the same make and model.
- Therefore, the endpoint logic should:
  1. Retrieve active ads updated in the last 48 hours (candidates).
  2. Group these candidates by `(make, model)`.
  3. For each group, fetch all active ads of that make/model from the database (peers pool).
  4. Fetch the model-wide statistics.
  5. Run `calculate_deal_scores` on the peers pool. This will calculate the scores for all ads (including candidates) within that peer pool.
  6. Map the computed scores back to the candidate ads by ID.
  7. Filter out candidate ads that do not have a valid deal score (`deal_score is not None`), sort them by `deal_score` descending, format their price with `" €"` to match the frontend expectations, and return the top 5.

## 3. Caveats
- **Postgres Dependency**: The queries assume a PostgreSQL database backend since `car_database.py` uses `psycopg2` and interval casts (e.g. `NOW() - CAST('48 hours' AS interval)`). If the environment shifts to a different database vendor, interval syntax would need adjustment.
- **Rate-Limiting**: The new endpoint is configured with a rate-limit of 10 requests per minute using the slowapi rate limiter to prevent potential abuse from heavy peer-group queries.
- **Memory Consumption**: If there are tens of thousands of active ads for a single make/model, fetching all of them as a peer pool could consume substantial memory. However, for typical crawler operations, this is highly manageable.

## 4. Conclusion
We propose adding two read-only helper functions to `backend/car_database.py` and a new FastAPI endpoint `/api/deals/top` to `backend/core_app.py`. This design preserves the existing architecture, utilizes the exact in-memory scoring algorithm already in place, and fully respects the read-only constraint.

### Suggested Code Changes

#### 1. In `backend/car_database.py`
Add the following methods to `CarDatabaseOptimizer` class (suggested insertion point: after `search_ads_db`, around line 249):

```python
    def get_recent_active_ads(self, hours_threshold: int = 48) -> List[Dict]:
        """Fetch all active ads updated/added within the last hours_threshold hours."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT * FROM ads 
                WHERE active = TRUE 
                  AND updated_at >= NOW() - CAST(%s AS interval)
            '''
            cursor.execute(query, (f"{hours_threshold} hours",))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_active_ads_for_make_model(self, make: str, model: str) -> List[Dict]:
        """Fetch all active ads for a specific make and model to act as a peer comparison group."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT * FROM ads 
                WHERE active = TRUE 
                  AND make = %s 
                  AND model = %s
            '''
            cursor.execute(query, (make, model))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
```

#### 2. In `backend/core_app.py`
Add the new endpoint route (suggested insertion point: after `api_search` endpoint, around line 151):

```python
@app.get('/api/deals/top')
@limiter.limit("10/minute")
def get_top_deals(request: Request):
    """
    Fetch up to 5 active car deals added/updated within the last 48 hours,
    sorted by their calculated Deal Score (highest first).
    """
    try:
        # 1. Fetch active ads updated within the last 48 hours
        recent_ads = car_db_optimizer.get_recent_active_ads(hours_threshold=48)
        if not recent_ads:
            return {'results': []}

        # 2. Group candidate ads by (make, model) to perform peer scoring
        grouped_candidates = {}
        for ad in recent_ads:
            make = ad.get('make')
            model = ad.get('model')
            if not make or not model:
                continue
            key = (make.lower(), model.lower())
            grouped_candidates.setdefault(key, []).append(ad)

        # 3. For each group, calculate deal scores based on their peers
        for (make_lower, model_lower), candidates in grouped_candidates.items():
            # Get all active ads for this make/model to act as peers
            peer_pool = car_db_optimizer.get_active_ads_for_make_model(candidates[0]['make'], candidates[0]['model'])
            
            # Fetch model stats
            s_model = model_lower.replace(' ', '-')
            stats = car_db_optimizer.get_model_stats(candidates[0]['make'], s_model) or {}
            
            # Calculate deal scores for all ads in the peer pool (in-place modification)
            scored_pool = calculate_deal_scores(peer_pool, stats)
            
            # Create a lookup map for the calculated deal scores
            scores_map = {ad['id']: ad.get('deal_score') for ad in scored_pool if 'id' in ad}
            
            # Assign the scores back to the candidate ads
            for ad in candidates:
                ad['deal_score'] = scores_map.get(ad['id'])

        # 4. Filter out ads without a valid deal score
        valid_deals = [ad for ad in recent_ads if ad.get('deal_score') is not None]

        # 5. Sort by deal score descending (highest first)
        valid_deals.sort(key=lambda x: x['deal_score'], reverse=True)

        # 6. Take top 5 and format their price with " €" to match other endpoints
        top_deals = valid_deals[:5]
        for ad in top_deals:
            if isinstance(ad['price'], int):
                ad['price'] = f"{ad['price']} €"
            elif isinstance(ad['price'], str) and '€' not in ad['price']:
                ad['price'] = f"{ad['price']} €"

        return {'results': top_deals}
    except Exception as e:
        logging.error(f"Error fetching top deals: {e}")
        return {'results': [], 'error': str(e)}
```

## 5. Verification Method
1. **Endpoint Access**: Run the backend FastAPI application locally (`uvicorn main:app --reload` in `backend/` directory) and verify the endpoint by making a request:
   `curl -i http://127.0.0.1:8000/api/deals/top`
2. **Database Verification**: Insert mock ads via SQL or crawler to verify they show up on the list.
   - Insert an ad with `updated_at` set to 50 hours ago and verify it is **not** returned.
   - Insert multiple active ads of the same make/model (e.g. BMW Seria 3) with different prices, and verify their `deal_score` is computed correctly and they are sorted by `deal_score` descending.
3. **Static Analysis & Linting**: Run `flake8` or `black` on the modified files to ensure styling is preserved:
   `flake8 backend/core_app.py backend/car_database.py`
4. **Invalidation conditions**:
   - If the returned list contains more than 5 ads.
   - If the results are not sorted by `deal_score` descending.
   - If ads modified more than 48 hours ago are included.
   - If prices do not end with the `" €"` suffix.
