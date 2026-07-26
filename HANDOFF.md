# Motorbit — Handoff Document

**Date:** 2026-07-06
**Branch:** `feature/canva-design-upgrade`
**Audit:** 114/156 issues resolved (73%) — see `docs/audit-issues.md`

## Quick Start
```sh
cd backend && source venv/bin/activate && uvicorn main:app --reload
cd frontend/motorbit && npm run dev
```
Backend: http://localhost:8000 | Frontend: http://localhost:5173

---

## What Was Done (This Session — July 6, 2026)

### Design System — Full Canva-Inspired Restyle
- Light mode as default (white/gray), dark mode via `.dark` class (navy `#0f172a`)
- DM Sans font, emerald green accent (`#10b981`)
- Flat cards with shadow hover, clean nav bar, 520px hero with inline search bar
- Score rings (green/amber/red outline style) on deal cards per Canva spec
- Trust stats strip, brand grid, DOTD featured hero card, filter sidebar
- Mobile responsive with hamburger menu and slide-out filter overlay

### i18n — Complete RO/EN Across All Components
- All 14 components translated: AuthModal, ContactModal, PartnerDashboard, Pagination, SearchForm, CarCard, DealOfTheDay, FilterSidebar, ResultsList, AlertModal, TrustStats, BrandGrid, PriceStats, LegalPage
- Number formatting with Intl.NumberFormat, parameterized strings support

### Backend — Security & Data Integrity
- JWT auth with random fallback for local dev (set `JWT_SECRET` in production `.env`)
- SQL regex injection fixed (`re.escape` on model param)
- Price parsing fixed (strip all non-digits instead of splitting on comma)
- SSL verification enabled on scrapers
- Email sending wrapped in try/except (no more silent thread failures)
- Password minimum length validation (6 chars)
- Timezone-aware datetime for JWT expiry
- Pagination metadata in search response (total, limit, page)
- `min_km` filter wired into SQL WHERE clause
- `/api/health` endpoint with database connectivity check
- Fake dashboard trend data replaced with empty array

### Dealer Platform Foundation
- `dealer_profiles`, `dealer_listings`, `contact_submissions` tables
- Dealer registration: contact form saves to DB, `/api/dealer/register` endpoint
- Inventory CRUD: `POST/GET/DELETE /api/dealer/listings` + UI in PartnerDashboard
- Verified partner badge on CarCard (green "Partener Verificat" pill)
- `create_dealer_profile`, `get_dealer_listings`, `approve_dealer` DB methods

### Frontend — Bugs Fixed
- CarCard NaN crash on undefined `price_diff`
- Deal ring overlay blocking (pointer-events fix)
- Deal ring + price-drop badge overlap (moved to opposite corners)
- Fuel/transmission filter mismatch between SearchForm and FilterSidebar
- 5 missing CSS classes defined, 2 undefined CSS variables added
- Light mode invisible elements (hardcoded white tints replaced with CSS vars)
- Stale closure in URL params useEffect
- Deal tooltip clipped by overflow hidden
- Sort chevron invisible in light mode (currentColor instead of white)
- Empty state, error message, footer all use CSS classes instead of inline styles
- 404 catch-all route, ErrorBoundary component
- `prefers-reduced-motion` and `:focus-visible` support
- Open Graph meta tags + JSON-LD structured data
- Modal accessibility: `role="dialog"`, `aria-modal`, `aria-label`
- Form label associations: `htmlFor`/`id` on all SearchForm and FilterSidebar fields

---

## Design Feedback — Near-Future Improvements

Feedback received: "Design direction 8.5/10, Execution 7.5/10. Strong concept — next step is making results page feel as rich as the homepage."

### Applied (This Session)
1. **Smoother hero headline** — "Gasesti masina la pretul corect" replaces the fragmented "Masini Premium. Performanta. Exceptionala."
2. **Search form contrast** — Hero form fields now have white/dark backgrounds with visible borders instead of blending into the hero image
3. **Stats row icons** — TrustStats now shows Lucide icons (Crosshair, TrendingUp, RefreshCw, Clock) next to each number

### Still To Do (Quick Wins — 1-2 hours)
4. **Results page filter hierarchy** — Add subtle separators between filter groups (price, year, km, fuel, transmission, source) in FilterSidebar. File: `App.css` → `.filter-section`
5. **Deal score badges more visible** — Increase score ring size on results cards from 48px to 56px, or add a subtle glow. File: `App.css` → `.deal-ring`
6. **Price comparison text** — Show "% sub media pietei" more prominently below the price on CarCard. Currently shown only in the tooltip. File: `CarCard.jsx` → add text below the price
7. **Reduce empty space** — Tighten gap between filter sidebar and results grid from 1.5rem to 1rem. File: `App.css` → `.results-layout`
8. **Skeleton loading state** — Upgrade from single pulsing block to card-like structure (image rect, title line, spec chips, price). File: `SkeletonCard.jsx`

### Medium Effort (4-8 hours)
9. **Results page feels complete** — Ensure real data cards render with images, prices, scores immediately after search. The skeleton state is only for loading — once results arrive, the page should feel dense and useful.
10. **Filter sidebar polish** — Add count badges next to each filter option (e.g., "Diesel (142)"). Requires backend support.
11. **Brand grid dynamic** — Fetch brands from `/api/brands` instead of hardcoded list. File: `BrandGrid.jsx`

---

## Remaining Audit Items (46, mostly polish)

### Medium (14)
| ID | Issue | File |
|---|---|---|
| M11 | BrandGrid uses static brand list | `BrandGrid.jsx` |
| M13 | No dealer profile page (`/dealer/:id`) | New route |
| M15 | No dealer pricing/subscription model | Business |
| M17 | No dealer approval workflow | `core_app.py` |
| M18 | No dealer-specific analytics | `PartnerDashboard.jsx` |
| M23 | No foreign keys on tables | `car_database.py` |
| M24 | Batch insert for cron ads | `car_database.py` |
| M26 | Duplicate log messages | `start_crawler.py` |
| M28-M30 | Inline styles in modals and PriceStats | AuthModal, ContactModal, PriceStats |
| M43 | Search history / saved searches | New feature |
| M44 | Alert management page | New feature |

### Low (30)
| ID | Issue |
|---|---|
| L2 | PropTypes or TypeScript migration |
| L3 | Wrap handleSearch in useCallback |
| L5 | Grid/list view toggle for results |
| L7-L8 | Scraper status endpoint, dead letter queue API |
| L13-L14 | Cursor lifecycle, brand matching edge cases |
| L25 | Progress indicator during long scrapes |
| L27-L32 | Dealer features: welcome email, messaging, reviews, bulk upload, white-label |
| L34-L35 | SEO: canonical URLs, sitemap |
| L36 | SkeletonCard structure improvement |
| L37-L48 | Various minor polish |

---

## Key Files

| File | Purpose |
|---|---|
| `frontend/motorbit/src/App.jsx` | Routes, state, search logic, all component wiring |
| `frontend/motorbit/src/App.css` | All component styles (~1400 lines) |
| `frontend/motorbit/src/index.css` | Design tokens: CSS variables, fonts, light/dark themes |
| `frontend/motorbit/src/LanguageContext.jsx` | RO/EN translations (25+ sections) |
| `frontend/motorbit/src/components/` | 17 React components |
| `backend/core_app.py` | FastAPI: 20+ endpoints, JWT, dealer API, search |
| `backend/car_database.py` | PostgreSQL: tables, queries, dealer methods (~1750 lines) |
| `backend/functii.py` | Scraper logic, price parsing, deal scoring |
| `backend/crawler.py` | Background link verification crawler |
| `backend/mailer.py` | Resend email (alerts, contact form) |
| `docs/audit-issues.md` | Full 156-item tracker with status per issue |
