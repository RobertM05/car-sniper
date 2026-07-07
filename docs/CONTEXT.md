# CarSniper — Project Context

Car marketplace aggregator for Romania. Scrapes OLX.ro and Autovit.ro, scores deals, provides dealer platform.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React 19 + Vite + React Router v7 |
| Styling | Custom CSS with CSS variables (DM Sans font) |
| Backend | Python FastAPI + Uvicorn |
| Database | PostgreSQL (Supabase) |
| Email | Resend |
| Payments | Stripe (Checkout + Customer Portal) |
| SEO | react-helmet-async, JSON-LD, sitemap, robots.txt |
| SSR | vike (installed, inactive — needs Vercel serverless) |

## Directory Map

```
frontend/car-sniper/src/
  App.jsx              — Routes, global state, search logic (~650 lines)
  App.css              — All styles (~1900 lines)
  index.css            — CSS variables, fonts, light/dark themes
  LanguageContext.jsx  — RO/EN translations (25+ sections)
  main.jsx             — React entry point
  components/          — 20 components (see below)
  utils/               — analytics, searchHistory, carComparison

backend/
  core_app.py          — FastAPI app, 25+ endpoints, JWT auth
  car_database.py      — PostgreSQL queries, table creation (~1800 lines)
  functii.py           — Scraper logic, price parsing, deal scoring
  crawler.py           — Background link verification crawler
  mailer.py            — Resend email (alerts, dealer welcome, password reset)
  scraper/             — OLX and Autovit scrapers

docs/
  audit-issues.md      — 156-item tracker (153 resolved)
  implementation-plan.md
  ssr-notes.md
```

## Components (20)

| Component | Purpose | Props |
|-----------|---------|-------|
| SearchForm | Hero search bar (brand, model, price, advanced filters) | formData, setFormData, brands, models |
| ResultsList | Grid of CarCards | results[] |
| CarCard | Listing card with deal score ring, compare button | car{}, index |
| FilterSidebar | Search results sidebar (price/year/km/fuel/transmission) | filters, onFilterChange, onApply |
| DealOfTheDay | Featured deal + grid of top deals | (fetches from API) |
| TrustStats | Stats strip (cars monitored, avg savings, etc) | stats{} optional |
| BrandGrid | Popular brand quick-select buttons | onBrandSelect |
| PriceStats | Market analysis panel | stats{}, currentSearch |
| Pagination | Page navigation | carsPerPage, totalCars, paginate |
| SkeletonCard | Loading skeleton | — |
| AlertModal | Price alert creation form | isOpen, onClose, onSubmit |
| AuthModal | Login/register | isOpen, onClose, onLoginSuccess |
| ContactModal | Dealer contact form | isOpen, onClose |
| LegalPage | Terms and privacy pages | type |
| PartnerDashboard | Dealer dashboard + inventory management | — |
| DealerProfile | Public dealer page with inventory | (reads :email from URL) |
| AlertManager | User alert management table | — |
| Breadcrumbs | Navigation breadcrumbs | — |
| PricingPage | Stripe subscription tiers | — |
| ErrorBoundary | Crash recovery wrapper | children |

## API Routes (core_app.py)

```
GET  /                          — Health check
GET  /api/health                — DB connectivity check
GET  /api/search                — Main search (make, model, price, year, km, fuel, transmission)
GET  /api/brands                — List all brands
GET  /api/models/:make          — List models for brand
GET  /api/stats/:make/:model    — Market stats (avg price, year, km)
GET  /api/deals/top             — Top deals (cached 5min)
POST /api/alert                 — Create price alert
GET  /api/alerts                — List user alerts
DELETE /api/alerts/:id          — Delete alert
POST /api/contact               — Dealer contact form (saves to DB)
POST /api/dealer/register       — Dealer registration
GET  /api/dealer/listings       — Get dealer inventory
POST /api/dealer/listings       — Create listing
DELETE /api/dealer/listings/:id — Delete listing
POST /api/dealer/listings/bulk  — Bulk JSON upload
GET  /api/dealer/analytics      — Views per listing
GET  /api/dealer/reviews/:id    — Get reviews
POST /api/dealer/reviews        — Add review
POST /api/stripe/create-checkout— Stripe Checkout Session
POST /api/stripe/webhook        — Stripe webhook handler
POST /api/stripe/portal         — Customer Portal session
POST /api/forgot-password       — Send reset email
POST /api/reset-password        — Reset with token
GET  /api/verify-email          — Email verification
GET  /api/admin/pending-dealers — List unapproved dealers
POST /api/admin/approve-dealer  — Approve dealer
GET  /api/dead-letter/files     — List dead letter files
POST /api/dead-letter/replay    — Replay dead letter entries
GET  /api/scraper/status        — Cache info
```

## Database Tables

```
users               — email, password (hashed), role, email_verified
alerts              — user_email, make, model, max_price
ads                 — make, model, price, year, km, fuel, link, source
dealer_profiles     — user_email, company_name, stripe_customer_id, subscription_tier
dealer_listings     — dealer_id, title, price, year, km, fuel, active
contact_submissions — name, email, phone, company_name
dealer_reviews      — dealer_id, user_email, rating (1-5), comment
listing_views       — listing_id, dealer_id
search_stats        — make, model, search count
```

## Design System

- Light mode default (white/gray `#f9fafb`), dark via `.dark` class (navy `#0f172a`)
- Primary: emerald green `#10b981`
- Font: DM Sans (400/500/600/700/800)
- Cards: single border + shadow hover
- Score rings: green ≥80, amber ≥60, red <60
- CSS variables for all colors: `--bg-primary`, `--text-primary`, `--border-shell`, etc.

## Key Patterns

- All state in App.jsx, passed down as props (no Redux/Context except Language)
- API calls use `fetch()` with `API_BASE_URL` from env
- i18n: `t('section', 'key', { params })` from LanguageContext
- DB: `car_db_optimizer` singleton with connection pooling
- Theme: `localStorage.getItem('theme')` + `.dark` class on `<html>`

## Common Commands

```sh
cd frontend/car-sniper && npm run dev     # Frontend dev
cd backend && uvicorn main:app --reload   # Backend dev
./start.sh                                # Both at once
npm run build                             # Production build
ruff format backend/                      # Python formatting
```
