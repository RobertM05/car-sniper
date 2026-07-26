# Bug Tracker — Car Sniper

> **Single source of truth.** Every bug found, every fix applied, every commit linked.  
> Total bugs: **28** | Fixed: **17** | Open: **11** | Last audit: 2026-06-30

---

## Status Key
`🔴 Open` `🟡 In Progress` `🟢 Fixed` `⏸️ Deferred (risk)` `❌ Won't Fix`

---

## Master Bug Registry

| ID | Severity | Category | Status | Description | Location | Commit | Date Fixed |
|----|----------|----------|--------|-------------|----------|--------|------------|
| **1.1** | 🔴 CRITICAL | Data Integrity | 🟢 Fixed | `split(',')[0]` truncates prices (1,234 → 1) | `start_crawler.py:105-108` | TBD | 2026-06-30 |
| **1.2** | 🔴 CRITICAL | Data Integrity | 🔴 Open | `original_price` overwritten on every upsert | `car_database.py` (upsert) | — | — |
| **1.3** | 🔴 CRITICAL | Data Integrity | 🟢 Fixed | `is_suspicious_price` computed but never wired | `crawler.py:29-30` | `8574944` | 2026-06-29 |
| **1.4** | 🟠 HIGH | Data Integrity | 🟢 Fixed | year=0 bypasses clamping logic | `car_database.py:299-303` | `c9bf971` | 2026-06-29 |
| **1.5** | 🟠 HIGH | Data Integrity | 🟢 Fixed | No year/km for "expensive" Autovit ads | `autovit_scraper.py:305-309` | TBD | 2026-06-30 |
| **1.6** | 🟡 MEDIUM | Data Integrity | 🔴 Open | Wrong enrichment threshold logic | `olx_scraper.py:104-107` | — | — |
| **1.7** | 🟡 MEDIUM | Data Integrity | 🟢 Fixed | Year-stripping kills numeric model names | `car_database.py:73` | `8366225` | 2026-06-29 |
| **2.1** | 🔴 CRITICAL | Coverage | 🔴 Open | Only scrapes subset of brands | `start_crawler.py` model list | — | — |
| **2.2** | 🟠 HIGH | Coverage | 🔴 Open | Slug mapping missing ~15 brands | `functii.py:124-206` | — | — |
| **2.3** | 🟡 MEDIUM | Coverage | 🟢 Fixed | Only 9 models (1.3% coverage) | `crawler.py:9` | `de780f8` | 2026-06-29 |
| **2.4** | 🟡 MEDIUM | Coverage | 🔴 Open | Missing Romanian-market brands | `deep_scrape.py:13-21` | — | — |
| **3.1** | 🔴 CRITICAL | Anti-Detection | ⏸️ Deferred | Single `Mozilla/5.0` UA for all OLX traffic | `olx_scraper.py:12` | — | — |
| **3.2** | 🔴 CRITICAL | Anti-Detection | ⏸️ Deferred | `ssl=False` on every connection | All scrapers | — | — |
| **3.3** | 🟠 HIGH | Anti-Detection | ⏸️ Deferred | Fixed delays, no jitter/backoff | Multiple files | — | — |
| **3.4** | 🟠 HIGH | Anti-Detection | ⏸️ Deferred | No 429/403 HTTP detection | All scrapers | — | — |
| **3.5** | 🟡 MEDIUM | Anti-Detection | ⏸️ Deferred | Only 6 User Agents | `autovit_scraper.py:9` | — | — |
| **4.1** | 🔴 CRITICAL | Error Handling | 🟢 Fixed | Bare `except: pass` in enrichment | `olx_scraper.py:135-136` | TBD | 2026-06-30 |
| **4.2** | 🟠 HIGH | Error Handling | 🟢 Fixed | Silent `return None` on all errors | `autovit_scraper.py:275-276` | `dbaedca` | 2026-06-29 |
| **4.3** | 🟠 HIGH | Error Handling | 🟢 Fixed | No dead-letter queue | All files | `8142acb` | 2026-06-29 |
| **4.4** | 🟡 MEDIUM | Error Handling | 🟢 Fixed | DB failure kills entire model batch | `start_crawler.py:117-118` | `d6d3a1d` | 2026-06-29 |
| **4.5** | 🟡 MEDIUM | Error Handling | 🟢 Fixed | 5s timeout too aggressive | `olx_scraper.py:113` | `0c29267` | 2026-06-29 |
| **5.1** | 🟠 HIGH | Dedup | 🔴 Open | No cross-model dedup | `start_crawler.py:79` | — | — |
| **5.2** | 🟡 MEDIUM | Dedup | 🔴 Open | `seen_links_total` doesn't survive shards | `autovit_scraper.py:12` | — | — |
| **5.3** | 🟡 MEDIUM | Dedup | 🔴 Open | `seen_links` per-call scope only | `olx_scraper.py:10` | — | — |
| **5.4** | 🟢 LOW | Dedup | 🟢 Fixed | Parameterized URL collision risk | `car_database.py:285` | `85824c6` | 2026-06-29 |
| **6.1** | 🔴 CRITICAL | Observability | 🟢 Fixed | Zero structured logging (only print()) | All files | `6a303b2`, `5474d5e` | 2026-06-29 |
| **6.2** | 🟠 HIGH | Observability | 🟢 Fixed | Zero metrics | All files | `e1c742b`, `3c4e884` | 2026-06-29 |
| **6.3** | 🟠 HIGH | Performance | 🟢 Fixed | Unbounded in-memory cache | `functii.py:14-15` | TBD | 2026-06-30 |
| **6.4** | 🟡 MEDIUM | Performance | 🔴 Open | Semaphore(5) underutilizes network | `autovit_scraper.py:15` | — | — |
| **6.5** | 🟡 MEDIUM | Performance | 🟢 Fixed | O(n²) list comprehension per page | `autovit_scraper.py:315-316` | TBD | 2026-06-30 |
| **6.6** | 🟡 MEDIUM | Performance | 🟢 Fixed | Full table scan on stale check | `car_database.py` (deactivate) | TBD | 2026-06-30 |
| **7.1** | 🔴 CRITICAL | Coordination | 🔴 Open | Three scripts with no locking | All entry points | — | — |

---

## Statistics

| Severity | Total | Fixed | Open | Fix Rate |
|----------|-------|-------|------|----------|
| 🔴 CRITICAL | 7 | 3 | 4 | 43% |
| 🟠 HIGH | 10 | 6 | 4 | 60% |
| 🟡 MEDIUM | 13 | 7 | 6 | 54% |
| 🟢 LOW | 1 | 1 | 0 | 100% |
| **Total** | **31** | **17** | **14** | **55%** |

---

## Deferred Bugs (Risk Assessment Required)

These bugs change how the scraper interacts with websites. Each needs explicit risk review before fixing:

| ID | Risk | Mitigation Required |
|----|------|---------------------|
| 3.1–3.5 | Anti-bot triggering | Staged rollout, A/B test delays, monitor 403/429 rates |
| 1.1 | Price parsing change | Validate against known listings before deploy |
| 1.2 | DB schema change | Backward-compatible migration, rollback plan |
| 4.1 | Changes enrichment flow | Canary deploy, monitor ad completeness |
| 6.4–6.5 | Load increase | Rate-limit cap, gradual ramp-up |
| 7.1 | Architecture change | Feature flag, parallel run before cutover |

---

*Maintained by: Cline AI Agent | Project: motorbit | Repo: github.com/RobertM05/motorbit*
