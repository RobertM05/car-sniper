# Changelog

All notable changes to car-sniper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Structured JSON-line logging across all modules ([6.1], [6.2])
- In-process metrics registry with counters and @timed decorator ([6.2])
- File-based dead-letter queue for failed ad payloads ([4.3])
- CI pipeline: lint (ruff), type-check (pyright), test (pytest) on PRs
- Rollback workflow: one-click revert to any commit via GitHub Actions
- Pull request template with risk assessment checklist
- Bug tracker in `docs/BUG_TRACKER.md` — master registry of all 28 findings

### Fixed
- **1.3**: `is_suspicious_price` now filters luxury cars listed below €15k market threshold ([8574944])
- **1.4**: year=0 values now clamped to valid 1950–2026 range ([c9bf971])
- **1.7**: numeric model names (e.g. "2008") preserved during year stripping ([8366225])
- **4.2**: exceptions logged before silent `return None` in autovit scraper ([dbaedca])
- **4.4**: per-model try/except — one model failure no longer aborts the entire make batch ([d6d3a1d])
- **4.5**: OLX enrichment timeout increased 5s → 15s for slow networks ([0c29267])
- **5.4**: URL query parameters stripped before MD5 ad ID hashing to prevent duplicates ([85824c6])

### Security
- Anti-detection changes deferred pending risk assessment (bugs 3.1–3.5)

---

## [0.5.0] — 2026-06-27

### Fixed
- Restored missing functions deleted during ingestion merge ([77597a3])
- Fixed ingestion bugs: high miss rate, Mercedes class matching, ghost ads ([7f81653])

---

## [0.4.0] — 2026-06-18

### Changed
- Merged Deal Score Algorithm rewrite ([28c53dc])
- Fixed generation matching and performance tier regex ([71f6c64])

---

## [0.3.0] — 2026-06-10

### Added
- GDPR privacy policy consent and backend PII scrubbing ([fcb3c56])

---

*Last updated: 2026-06-29*
