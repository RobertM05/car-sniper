# CLINE.md — Agent Memory File

> **Read this first when starting any session in motorbit.**

---

## Quick Start
1. Read [`docs/BUG_TRACKER.md`](docs/BUG_TRACKER.md) — master bug registry
2. Read [`docs/CHANGELOG.md`](docs/CHANGELOG.md) — what changed when
3. Read [`SESSION_NOTES.md`](SESSION_NOTES.md) — historical decisions
4. Check `git log --oneline -20` for recent commits

---

## Project: motorbit
- **Repo:** `github.com/RobertM05/motorbit`
- **Purpose:** Scrapes car listings from OLX.ro & Autovit.ro
- **Stack:** Python 3.11, PostgreSQL, Playwright, aiohttp
- **Entry points:** `start_crawler.py`, `deep_scrape.py`, `crawler.py`

---

## Bug Tracking Convention
- **Single source of truth:** `docs/BUG_TRACKER.md`
- Every fix commit MUST reference the bug ID: `fix: [Bug 1.3] description`
- After fixing a bug, update `docs/BUG_TRACKER.md` status and `docs/CHANGELOG.md`
- After every session, update `SESSION_NOTES.md` with what was done

---

## Risk Rules (DO NOT VIOLATE)
- **NEVER** change scraping rates, delays, User-Agent, SSL settings, or HTTP headers without explicit user approval
- Bugs 3.1–3.5 (anti-detection) and 7.1 (coordination lock) are **deferred** — require staged rollout plan
- Before any code change, check: "Does this change how we interact with websites?" If yes, flag it

---

## Current State (last updated 2026-06-29)
- **11 of 28 bugs fixed** (all low-risk: data integrity, error handling, observability)
- **17 bugs remain** — mostly anti-detection, coverage, and performance
- **GitHub Actions active:** CI on PRs, rollback workflow ready
- **gh CLI not installed** — cannot create GitHub Issues programmatically

---

## Session Workflow
1. User gives a task → read this file first
2. Check `docs/BUG_TRACKER.md` for relevant open bugs
3. Propose plan → execute → commit per bug → push
4. Update tracker + changelog + session notes
5. Never leave uncommitted work

---

## Key Files Map
```
motorbit/
├── CLINE.md                    ← THIS FILE — agent memory
├── SESSION_NOTES.md            ← session-by-session log
├── docs/
│   ├── BUG_TRACKER.md          ← master bug registry (28 bugs)
│   ├── CHANGELOG.md            ← keepachangelog format
│   └── README.md               ← docs index
├── .github/
│   ├── workflows/ci.yml        ← lint + type-check + test
│   ├── workflows/rollback.yml  ← one-click revert
│   ├── ISSUE_TEMPLATE/bug_report.md
│   └── PULL_REQUEST_TEMPLATE.md
└── backend/
    ├── logger.py               ← structured JSON logging
    ├── metrics.py              ← in-process counters + @timed
    ├── dead_letter.py          ← file-based DLQ
    ├── start_crawler.py        ← main crawler
    ├── deep_scrape.py          ← broad brand search
    ├── crawler.py              ← legacy crawler
    ├── olx_scraper.py          ← OLX scraper
    ├── autovit_scraper.py      ← Autovit scraper
    ├── functii.py              ← helpers + model slugs
    └── car_database.py         ← PostgreSQL DB layer
```
