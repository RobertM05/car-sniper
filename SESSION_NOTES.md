# Car-Sniper Audit Notes

> **Session:** 2026-06-29 | **Mode:** Plan | **Status:** Analysis complete, no fixes applied yet  
> **Prompt:** "use a data analyst to check the scraping script for the deep sync"

---

## Architecture Summary

**car-sniper** scrapes car listings from **OLX.ro** and **Autovit.ro**. Three independent entry points exist:

| Script | Role |
|---|---|
| `backend/start_crawler.py` | Main crawler — model-specific searches, sharded by year range |
| `backend/deep_scrape.py` | Brand-level broad search (model=""), no stale cleanup |
| `backend/crawler.py` | Legacy entry point — only 9 models |

Key supporting files: `backend/olx_scraper.py`, `backend/autovit_scraper.py`, `backend/functii.py`, `backend/car_database.py`

**No coordination lock** — all three scripts can overwrite each other's data.

---

## Bug Audit (28 findings)

### 1. Data Integrity

| ID | Severity | Location | Description |
|---|---|---|---|
| 1.1 | 🔴 CRITICAL | `start_crawler.py:100-103` | `split(',')[0]` truncates prices with commas (e.g. `1,234` → `1`) |
| 1.2 | 🔴 CRITICAL | `car_database.py` (upsert) | `original_price` overwritten on every upsert instead of first insert only |
| 1.3 | 🔴 CRITICAL | `crawler.py:29-30` | `is_suspicious_price` computed but never wired to filtering |
| 1.4 | 🟠 HIGH | `car_database.py:299-303` | `year=0` bypasses clamping logic |
| 1.5 | 🟠 HIGH | `autovit_scraper.py:305-309` | No year/km extracted for "expensive" ads |
| 1.6 | 🟡 MEDIUM | `olx_scraper.py:104-107` | Wrong enrichment threshold logic |
| 1.7 | 🟡 MEDIUM | `car_database.py:73` | Year-stripping kills numeric model names |

### 2. Coverage Gaps

| ID | Severity | Location | Description |
|---|---|---|---|
| 2.1 | 🔴 CRITICAL | `start_crawler.py` model list | Only scrapes a subset of brands |
| 2.2 | 🟠 HIGH | `functii.py:124-206` | Slug mapping missing ~15 brands |
| 2.3 | 🟡 MEDIUM | `crawler.py:9` | Only 9 models (1.3% coverage) |
| 2.4 | 🟡 MEDIUM | `deep_scrape.py:13-21` | Missing Romanian-market brands |

### 3. Anti-Detection

| ID | Severity | Location | Description |
|---|---|---|---|
| 3.1 | 🔴 CRITICAL | `olx_scraper.py:12` | Single `Mozilla/5.0` UA for all OLX traffic |
| 3.2 | 🔴 CRITICAL | All scrapers | `ssl=False` on every connection |
| 3.3 | 🟠 HIGH | Multiple files | Fixed delays only, no jitter/backoff |
| 3.4 | 🟠 HIGH | All scrapers | No 429/403 HTTP detection |
| 3.5 | 🟡 MEDIUM | `autovit_scraper.py:9` | Only 6 User Agents |

### 4. Error Handling

| ID | Severity | Location | Description |
|---|---|---|---|
| 4.1 | 🔴 CRITICAL | `olx_scraper.py:135-136` | Bare `except: pass` in enrichment (swallows ALL errors) |
| 4.2 | 🟠 HIGH | `autovit_scraper.py:275-276` | Silent `return None` on all errors |
| 4.3 | 🟠 HIGH | All files | No dead-letter queue for failed ads |
| 4.4 | 🟡 MEDIUM | `start_crawler.py:117-118` | DB failure kills entire model batch |
| 4.5 | 🟡 MEDIUM | `olx_scraper.py:113` | 5s timeout too aggressive |

### 5. Deduplication

| ID | Severity | Location | Description |
|---|---|---|---|
| 5.1 | 🟠 HIGH | `start_crawler.py:79` | No cross-model dedup |
| 5.2 | 🟡 MEDIUM | `autovit_scraper.py:12` | `seen_links_total` doesn't survive shards |
| 5.3 | 🟡 MEDIUM | `olx_scraper.py:10` | `seen_links` per-call scope only |
| 5.4 | 🟢 LOW | `car_database.py:285` | Parameterized URL collision risk |

### 6. Performance / Observability

| ID | Severity | Location | Description |
|---|---|---|---|
| 6.1 | 🔴 CRITICAL | All files | Zero structured logging (only `print()`) |
| 6.2 | 🟠 HIGH | All files | Zero metrics (duration, success rate, etc.) |
| 6.3 | 🟠 HIGH | `functii.py:14-15` | Unbounded in-memory cache |
| 6.4 | 🟡 MEDIUM | `autovit_scraper.py:15` | Semaphore(5) underutilizes network |
| 6.5 | 🟡 MEDIUM | `autovit_scraper.py:315-316` | O(n²) list comprehension per page |
| 6.6 | 🟡 MEDIUM | `car_database.py` (deactivate) | Full table scan on stale check |

### 7. Coordination

| ID | Severity | Location | Description |
|---|---|---|---|
| 7.1 | 🔴 CRITICAL | All entry points | Three independent scripts with no locking |

---

## Remediation Priority

- **P0 (Immediate):** Fix price truncation (`split(',')[0]`), `original_price` upsert, wire `is_suspicious_price`, add coordination lock
- **P1 (This week):** UA rotation, remove `ssl=False`, 429/403 detection with backoff, replace bare `except: pass`
- **P2 (This sprint):** Structured logging (JSON), metrics, dead-letter queue
- **P3 (Next sprint):** Unify 3 scripts into single coordinated pipeline

---

*Last updated: 2026-06-29 — no fixes applied yet*
