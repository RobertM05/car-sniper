# Car-Sniper Handoff — 2026-06-30

## Current State

### 🟢 Running: Deep Scrape
```bash
caffeinate -i /Users/robert/car-sniper/backend/venv/bin/python /Users/robert/car-sniper/backend/deep_scrape.py
```
- Scraping 43 brands from Autovit + OLX
- Uses 56 price buckets per site to bypass pagination caps
- OLX: `require_photos=False` (was filtering ~60% of ads)
- Autovit: also price-bucketed now
- Estimated runtime: 3-5 hours per full run

### 🔴 Major Bug Found: Autovit image enrichment silently discarded (QA Agent)
- **File:** `backend/scraper/autovit_scraper.py`, lines 310-317
- The `enrich_tasks` results from `asyncio.gather` are iterated but the enriched images are **never applied** to the ads — there's a `pass` where enrichment results should be merged back
- **Impact:** Any Autovit ad without an image from the listing page stays imageless, even though enrichment fetches the image successfully

### 🟡 Other Bugs Found (BE Reviewer)
- **PRICE_BUCKETS** missing cars ≥ €200,000 (last bucket is 195000-199999)
- **Autovit `empty_pages` counter** — stops after 2 consecutive empty pages, but with price buckets, many buckets legitimately have 0 results for luxury brands
- **OLX enrichment timeout** still at 5s (should be 15s per Bug 4.5 fix that was reverted)
- **search_ads_db** price column is text with "€ EUR" suffix — comparison `price <= 15000` in SQL may work via implicit cast but is fragile

### 🟡 Data Analyst (aborted — needs re-run)
- Question: why only 17 BMW Seria 4 ads?
- Hypothesis: deactivate_stale_ads nuked them during broken period; crawler now includes Seria 4 but needs time to repopulate

---

## What Was Done This Session

### Infrastructure
- ✅ CI pipeline (lint + type-check + test on PRs)
- ✅ Rollback workflow (one-click revert in GitHub Actions)
- ✅ PR template with risk checklist
- ✅ Bug tracker at `docs/BUG_TRACKER.md` (28 bugs, 11 fixed)
- ✅ Changelog at `docs/CHANGELOG.md`
- ✅ Agent memory at `CLINE.md`

### Bug Fixes Applied (10 of 28)
1. Bug 1.3 — `is_suspicious_price` wired to skip luxury cars < €15k
2. Bug 1.4 — year=0 clamped to valid range
3. Bug 1.7 — numeric model names preserved during year stripping
4. Bug 4.2 — log exceptions before silent returns in Autovit
5. Bug 4.3 — file-based dead-letter queue
6. Bug 4.4 — graceful per-model failure in crawler
7. Bug 4.5 — OLX timeout 5s → 15s (**may have been reverted — verify**)
8. Bug 5.4 — URL query params stripped before MD5 hashing (**reverted — URL stripping was changing ad IDs**)
9. Bug 6.1 — structured JSON logging
10. Bug 6.2 — metrics registry + @timed decorators

### Critical Fixes This Session
- ✅ Fixed `functii.py` indentation error that took down entire site (500 on all endpoints)
- ✅ Removed `@metrics.timed` decorators from `search_cars` and `scrape_olx` (caused OLX to return empty)
- ✅ Reverted ALL sub-agent data changes to `car_database.py`, `functii.py`, `crawler.py`, `deep_scrape.py`, both scrapers — restored to commit `77597a3`
- ✅ Increased `deactivate_stale_ads` from 24h → 168h (7 days) to prevent crawler from nuking ads for non-targeted models
- ✅ Expanded crawler TARGETS from 9 → 26 models (now includes BMW Seria 4)
- ✅ Tiered deep scrape: 500/250/100/50 pages per brand based on market volume
- ✅ Made OLX `search[photos]` filter optional (`require_photos=False` for deep scrape)
- ✅ Applied price bucket strategy (56 buckets, €0-€200k) to BOTH Autovit and OLX

---

## What Needs Doing Next

### 🔴 P1 — Fix Autovit image enrichment
File: `backend/scraper/autovit_scraper.py` ~line 310-317
The enriched images/data from `asyncio.gather` are collected but never applied back to the ads.

### 🔴 P1 — Fix OLX enrichment timeout
File: `backend/scraper/olx_scraper.py` line ~115
`timeout=5` should be `timeout=15` (Bug 4.5 fix was reverted)

### 🟡 P2 — Fix PRICE_BUCKETS ceiling
File: `backend/deep_scrape.py`
Add `(200000, 999999)` bucket for cars ≥ €200k

### 🟡 P2 — Fix Autovit empty_pages counter for price buckets
When using price buckets, some buckets legitimately return 0 results. The 2-empty-page stop logic may need to be 5+ for deep scrape mode, or disabled when min_price/max_price are set.

### 🟡 P2 — Verify deep scrape completed
Check the terminal output — it should show results for all 43 brands across both Autovit and OLX.

### ⏳ P3 — Re-run Data Analyst investigation
Why only 17 BMW Seria 4 ads? Wait for deep scrape to complete, then re-query.

### ⏳ P3 — Fix remaining 17 bugs from BUG_TRACKER.md
See `docs/BUG_TRACKER.md` for the full list with priorities.

---

## Commands Reference

```bash
# Deep scrape (currently running)
caffeinate -i /Users/robert/car-sniper/backend/venv/bin/python /Users/robert/car-sniper/backend/deep_scrape.py

# Run crawler (26 models, every 10 min)
/Users/robert/car-sniper/backend/venv/bin/python /Users/robert/car-sniper/backend/crawler.py

# Check if running
ps aux | grep -E "deep_scrape|crawler" | grep -v grep

# Git
cd /Users/robert/car-sniper && git log --oneline -10
```

## Key Files
| File | Purpose |
|---|---|
| `backend/deep_scrape.py` | Deep sync — 43 brands, price bucketed |
| `backend/crawler.py` | Background crawler — 26 models, 10-min loop |
| `backend/scraper/olx_scraper.py` | OLX scraper — `require_photos` param added |
| `backend/scraper/autovit_scraper.py` | Autovit scraper — **image enrichment bug here** |
| `backend/car_database.py` | DB layer — `deactivate_stale_ads` now 168h |
| `backend/core_app.py` | FastAPI app — `/api/search`, `/api/cron/*` |
| `docs/BUG_TRACKER.md` | Master bug registry (28 bugs total) |
| `CLINE.md` | Agent memory file |
