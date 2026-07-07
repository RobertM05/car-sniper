# CarSniper — Audit Issue Tracker

**Date:** 2026-07-06
**Branch:** `feature/canva-design-upgrade`
**Total findings:** 156 (24 critical, 36 high, 48 medium, 48 low)

## Status Legend
- [ ] Pending
- [~] In Progress
- [x] Resolved

---

## CRITICAL (24)

### C1. [x] Price parsing truncation on comma — functii.py
`price_str.split(",")[0]` turns `12,500` into `12`. Splits on comma before stripping non-digits.
**Domain:** Backend | **Impact:** Data corruption — all prices off by orders of magnitude.

### C2. [x] repair_ad() returns string on 404 — functii.py
Returns `model.lower().replace(" ", "-")` (a string) instead of dict. Passes truthiness check, ends up in results, crashes downstream.
**Domain:** Backend | **Impact:** Data corruption / crash.

### C3. [x] CarCard crash on NaN.toLocaleString() — CarCard.jsx
`Math.abs(car.price_diff)` can be `undefined` → `NaN.toLocaleString()` throws. Crashes entire card render.
**Domain:** Frontend | **Impact:** Blank cards / white screen.

### C4. [x] Missing i18n keys crash UI text — AlertModal.jsx
`t('alert', 'under')` and `t('alert', 'saving')` keys don't exist. Renders `"alert.under"` to user.
**Domain:** Frontend | **Impact:** Broken user-facing text.

### C5. [x] SQL regex injection — car_database.py
User-supplied model in regex via f-string `rf"(^|\s|-){model}(\s|$|-)"`. Metacharacters crash query.
**Domain:** Backend | **Impact:** Search crashes on special characters.

### C6. [x] Hardcoded JWT secret fallback — core_app.py
`"dev-fallback-secret-12345"` used when env var missing. Trivially forgeable.
**Domain:** Backend | **Impact:** Auth bypass.

### C7. [x] Email to unverified address — core_app.py
Alert notification sent to request body email, not verified token email. Auth bypass for alert spam.
**Domain:** Backend | **Impact:** Security — send alerts to anyone.

### C8. [x] No dealer database schema
No `dealer_profiles`, `leads`, `contact_submissions` tables. `ads` has no `dealer_id`.
**Domain:** Backend | **Impact:** Dealer program non-existent.

### C9. [x] "Add Inventory" button does nothing — PartnerDashboard.jsx
No onClick handler. Button is decorative.
**Domain:** Frontend | **Impact:** Core dealer feature broken.

### C10. [x] No dealer registration flow — AuthModal.jsx
Registration sets `role='user'`. No path to `role='dealer'`. No business info collection.
**Domain:** Frontend + Backend | **Impact:** Dealers cannot onboard.

### C11. [x] No dealer inventory management
Zero CRUD endpoints, zero UI for dealer-owned listings.
**Domain:** Backend + Frontend | **Impact:** Dealer value prop missing.

### C12. [x] No dealer listings in search results — CarCard.jsx
No `dealer_id` column, no verified badge, no priority sorting.
**Domain:** Backend + Frontend | **Impact:** Partner listings indistinguishable from scraped.

### C13. [x] Deal ring overlay blocks all interactions — CarCard.jsx
Overlay `z-index: 10` covers deal ring `z-index: 2`. Clicks on ring navigate to ad instead of opening tooltip.
**Domain:** Frontend | **Impact:** Deal ring tooltip non-functional.

### C14. [x] Fuel/transmission filter mismatch — SearchForm.jsx vs FilterSidebar.jsx
SearchForm uses `"Petrol"`, FilterSidebar uses `"Benzina"`. Same for transmission (`"Automatic"` vs `"Automata"`).
**Domain:** Frontend | **Impact:** Filters silently diverge between components.

### C15. [x] --bg-card CSS variable undefined — AuthModal.jsx, ContactModal.jsx
Referenced but not in `:root` or `.dark`. Falls to transparent.
**Domain:** Frontend | **Impact:** Modals invisible in both themes.

### C16. [x] --border-color CSS variable undefined — AlertModal.jsx
Referenced but not defined. Cancel button has no border.
**Domain:** Frontend | **Impact:** Visual bug.

### C17. [x] glass-panel class undefined — PriceStats.jsx, AlertModal.jsx
Used in JSX but no CSS rules exist.
**Domain:** Frontend | **Impact:** No styling applied.

### C18. [x] trust-stat-item class undefined — TrustStats.jsx
Used in JSX but no CSS rules exist.
**Domain:** Frontend | **Impact:** No styling applied.

### C19. [x] sort-select class undefined — App.jsx
Used in JSX but no CSS rules exist.
**Domain:** Frontend | **Impact:** Sort dropdown gets browser defaults only.

### C20. [x] error-message class undefined — App.jsx
Used in JSX but no CSS rules exist.
**Domain:** Frontend | **Impact:** Errors invisible.

### C21. [x] car-link-overlay class undefined — CarCard.jsx
Used in JSX but no CSS rules exist (all styling is inline).
**Domain:** Frontend | **Impact:** Dead class.

### C22. [x] Deal ring has conflicting z-index — App.css
`z-index: 15` then overridden by `z-index: 2` in same selector cascade.
**Domain:** Frontend | **Impact:** Deal ring sits below overlay.

### C23. [x] Deal ring and price-drop badge overlap — CarCard.jsx
Both at `top: 1rem; left: 1rem`. When both visible, completely overlap.
**Domain:** Frontend | **Impact:** One badge obscures the other.

### C24. [x] Stale closure in useEffect — App.jsx
`formData` used in effect but not in dependency array. URL restoration uses stale form values.
**Domain:** Frontend | **Impact:** Wrong search params on URL navigation.

---

## HIGH (36)

### H1. [x] Sort chevron invisible in light mode — App.css
SVG has `stroke='white'`. Invisible on light background.
**Domain:** Frontend | **Impact:** Dropdown arrow invisible.

### H2. [x] Deal tooltip clipped by overflow hidden — App.css
`car-card-core` has `overflow: hidden`. Tooltip extends above card boundary → clipped.
**Domain:** Frontend | **Impact:** Tooltip partially invisible.

### H3. [x] Hardcoded rgba(255,255,255,...) in light mode — multiple files
`spec-chip`, `stat-icon-wrapper`, `partner-link` use white tints invisible in light mode.
**Domain:** Frontend | **Impact:** Elements invisible.

### H4. [x] Filter input dark background in light mode — App.css
`background: rgba(0, 0, 0, 0.2)` creates muddy gray on light bg.
**Domain:** Frontend | **Impact:** Visual bug.

### H5. [x] background: var(--shadow-inset-top) invalid — PartnerDashboard.css
Shadow value used as background. No visible effect.
**Domain:** Frontend | **Impact:** Subtle highlight missing.

### H6. [x] AuthModal 0% i18n — AuthModal.jsx
All strings hardcoded Romanian. No `useLanguage`.
**Domain:** Frontend | **Impact:** Language toggle broken for auth.

### H7. [x] ContactModal 0% i18n — ContactModal.jsx
All strings hardcoded Romanian. No `useLanguage`.
**Domain:** Frontend | **Impact:** Language toggle broken for contact.

### H8. [x] PartnerDashboard 0% i18n — PartnerDashboard.jsx
All strings hardcoded English. No `useLanguage`.
**Domain:** Frontend | **Impact:** Language toggle broken for dashboard.

### H9. [x] Pagination 0% i18n, no aria — Pagination.jsx
Raw arrow characters. No `useLanguage`. No aria-labels.
**Domain:** Frontend | **Impact:** Not translated, not accessible.

### H10. [x] ResultsList empty state hardcoded RO — ResultsList.jsx
No `useLanguage`, no `t()` wrapper.
**Domain:** Frontend | **Impact:** Language toggle broken for empty state.

### H11. [x] SearchForm fuel/transmission hardcoded RO — SearchForm.jsx
Labels "Combustibil", "Cutie de viteze", options all hardcoded.
**Domain:** Frontend | **Impact:** Language toggle broken for advanced filters.

### H12. [x] CarCard hardcoded strings — CarCard.jsx
"AI Deal Analysis", "cheaper"/"more expensive", "REDUCERE", "Detalii", aria-label all hardcoded.
**Domain:** Frontend | **Impact:** Mixed RO/EN hardcoded strings.

### H13. [x] DealOfTheDay hardcoded RO — DealOfTheDay.jsx
"Economisesti ~... fata de pretul mediu", aria-label hardcoded.
**Domain:** Frontend | **Impact:** Not translated.

### H14. [x] App.jsx hardcoded strings — App.jsx
"Salut", "Logout", "Contul meu", "Filtre", "masini" in routes, SEO meta all hardcoded.
**Domain:** Frontend | **Impact:** Not translated.

### H15. [x] No pagination metadata in API — core_app.py
Response has no `total`, `pages`, `has_more`.
**Domain:** Backend | **Impact:** Frontend can't show total result count.

### H16. [x] min_km filter silently ignored — core_app.py, car_database.py
Accepted as param but never added to WHERE clause.
**Domain:** Backend | **Impact:** Filter does nothing.

### H17. [x] Fake dashboard trend data — core_app.py
Synthetic Mon-Sun data from user count multiplication. Not real activity.
**Domain:** Backend | **Impact:** Misleading analytics.

### H18. [x] No scraper rate limiting — scraper files
No delay between page requests. 1000 requests without pause.
**Domain:** Backend | **Impact:** IP blocks from OLX/Autovit.

### H19. [x] SSL verification disabled — all scrapers
`ssl=False` on all aiohttp connectors.
**Domain:** Backend | **Impact:** MITM risk, security warnings.

### H20. [x] No robots.txt check — all scrapers
No compliance check before scraping.
**Domain:** Backend | **Impact:** Legal/compliance risk.

### H21. [x] Global in-memory caches with multi-worker — core_app.py
`_TOP_DEALS_CACHE` and `_SEARCH_CACHE` are process-local. Inconsistent across workers.
**Domain:** Backend | **Impact:** Stale/inconsistent data under load.

### H22. [x] Daemon thread email swallows errors — core_app.py
Thread fails silently. No error callback or logging.
**Domain:** Backend | **Impact:** Alert emails silently lost.

### H23. [x] No password strength validation — core_app.py
Password `"a"` is accepted. No length/complexity requirements.
**Domain:** Backend | **Impact:** Weak account security.

### H24. [x] datetime.utcnow() deprecated — core_app.py
Naive datetime for JWT expiry. May be rejected by timezone-aware validators.
**Domain:** Backend | **Impact:** Potential token validation failures.

### H25. [x] Dealer KPI labels misleading — PartnerDashboard.jsx
"Active Buyers" shows total registered users count, not active users.
**Domain:** Frontend | **Impact:** Misleading metric.

### H26. [x] Dealer "+12%" fake metric — PartnerDashboard.jsx
Hardcoded multiplication, not real delta.
**Domain:** Frontend | **Impact:** Fake analytics shown to dealers.

### H27. [x] Hero search-form duplicate opacity — App.css
Two CSS blocks setting the same opacity. Stale leftover selector.
**Domain:** Frontend | **Impact:** Dead code.

### H28. [x] LegalPage inline style anti-pattern — LegalPage.jsx
Scoped styles injected at mount, lost at unmount.
**Domain:** Frontend | **Impact:** Fragile styling.

### H29. [x] .top-nav opacity 0.9 affects all content — App.css
Text, logo, buttons all muted 10%. Should use transparent bg instead.
**Domain:** Frontend | **Impact:** Washed-out nav.

### H30. [x] .skeleton-pulse white shimmer invisible in light — App.css
`rgba(255,255,255,0.03)` invisible on light bg.
**Domain:** Frontend | **Impact:** No loading indicator in light mode.

### H31. [x] Plus Jakarta Sans font not imported — PartnerDashboard.css
Only DM Sans is imported. Falls back to system sans-serif.
**Domain:** Frontend | **Impact:** Font mismatch on dashboard.

### H32. [x] No keyboard trap or focus in modals — Auth/Contact/Alert modals
No focus trapping, no Escape key, no `role="dialog"`, no `aria-modal`.
**Domain:** Frontend | **Impact:** Accessibility failure.

### H33. [x] No form label associations — all components
label tags without htmlFor, inputs without id. Screen readers can't associate.
**Domain:** Frontend | **Impact:** Accessibility failure.

### H34. [x] handleSearch not in useCallback — App.jsx
Recreated every render, passed as prop, used in useEffect.
**Domain:** Frontend | **Impact:** Unnecessary re-renders.

### H35. [x] backup_db.py loads entire table into memory — backup_db.py
fetchall() on entire ads table. OOM risk.
**Domain:** Backend | **Impact:** Memory exhaustion.

### H36. [x] No prefers-reduced-motion — all animations
Animations run unconditionally.
**Domain:** Frontend | **Impact:** Accessibility.

---

## MEDIUM (48)

### M1. [x] SearchForm sets phantom generation field — SearchForm.jsx
Not in formData initial state, never used. Dead code.
**Domain:** Frontend

### M2. [x] Unstable list keys — ResultsList.jsx, DealOfTheDay.jsx
Array index in keys causes unnecessary re-renders on reorder.
**Domain:** Frontend

### M3. [x] PriceStats falsy-zero bug — PriceStats.jsx
`avg_price ? formatPrice(avg_price) : 'N/A'` shows N/A for 0.
**Domain:** Frontend

### M4. [x] Circular data flow formData to/from sidebarFilters — App.jsx
Sync effect + merge handler creates fragile round-trip.
**Domain:** Frontend

### M5. [x] TrustStats hardcodes German locale — TrustStats.jsx
`toLocaleString('de-DE')` instead of user language.
**Domain:** Frontend

### M6. [x] LegalPage dangerouslySetInnerHTML — LegalPage.jsx
Pattern is XSS risk if content moves to DB.
**Domain:** Frontend

### M7. [x] SkeletonCard no dimensions — SkeletonCard.jsx
May collapse to zero height if CSS not loaded.
**Domain:** Frontend

### M8. [x] PartnerDashboard fake data in production — PartnerDashboard.jsx
Hardcoded percentage delta.
**Domain:** Frontend

### M9. [x] Duplicate logout logic — App.jsx, PartnerDashboard.jsx
Two copies of same localStorage clearing.
**Domain:** Frontend

### M10. [x] search.advanced contains arrow in translation — LanguageContext.jsx
Character in translation value instead of CSS.
**Domain:** Frontend

### M11. [x] BrandGrid uses static brand list — BrandGrid.jsx
New brands require frontend deploy.
**Domain:** Frontend

### M12. [x] No "Clear all filters" button — FilterSidebar.jsx
Users must manually clear each field.
**Domain:** Frontend

### M13. [x] No dealer profile/view inventory page
No route `/dealer/:id`, no component.
**Domain:** Frontend + Backend

### M14. [x] No "filter by verified partner" — FilterSidebar.jsx
Missing filter for dealer-only listings.
**Domain:** Frontend + Backend

### M15. [x] No dealer pricing/subscription model
No tiers, no feature gating, no billing.
**Domain:** Business

### M16. [x] "Website IP" field wrong — ContactModal.jsx
Should be "Website URL" with URL placeholder.
**Domain:** Frontend

### M17. [x] No dealer approval workflow
Contact form to email only. No approval tracking.
**Domain:** Backend + Frontend

### M18. [x] No dealer-specific analytics
Dashboard shows platform aggregates, not per-dealer metrics.
**Domain:** Backend + Frontend

### M19. [x] models.py is empty — backend/models.py
Dead code, never imported.
**Domain:** Backend

### M20. [x] No DB connection health check — car_database.py
No retry, backoff, or periodic check on connection loss.
**Domain:** Backend

### M21. [x] Missing DB indexes — car_database.py
No index on year, km, fuel, transmission, active, last_seen.
**Domain:** Backend

### M22. [x] search_stats no UNIQUE constraint — car_database.py
Concurrent calls create duplicate rows.
**Domain:** Backend

### M23. [x] No foreign keys — all tables
Users/alerts/ads have no FK relationships. Orphaned data possible.
**Domain:** Backend

### M24. [x] insert_cron_ads() one query per ad — car_database.py
Loop of individual inserts. Should batch like upsert_ads().
**Domain:** Backend

### M25. [x] PII scrubbing only matches Romanian phones — functii.py
Regex misses international, landlines, emails in titles.
**Domain:** Backend

### M26. [x] Duplicate log messages — start_crawler.py
Same log line written twice.
**Domain:** Backend

### M27. [x] Dead link deletion commented out — link_verifier.py
Stale ads accumulate because deletion is disabled.
**Domain:** Backend

### M28. [x] AuthModal 100% inline styles — AuthModal.jsx
15+ inline style objects. Should use CSS classes.
**Domain:** Frontend

### M29. [x] ContactModal 100% inline styles — ContactModal.jsx
12+ inline style objects.
**Domain:** Frontend

### M30. [x] PriceStats 100% inline styles — PriceStats.jsx
All styling inline.
**Domain:** Frontend

### M31. [x] CarCard inline animation overrides CSS easing — CarCard.jsx
Hardcoded `0.6s ease` instead of `var(--spring-easing)`.
**Domain:** Frontend

### M32. [x] No :focus-visible styles — all components
No visual feedback for keyboard navigation.
**Domain:** Frontend

### M33. [x] Footer inline styles — App.jsx
Should be reusable `.footer` class.
**Domain:** Frontend

### M34. [x] Empty state inline styles — App.jsx, ResultsList.jsx
Should be `.empty-state` class.
**Domain:** Frontend

### M35. [x] submit-btn reused for unrelated actions — SearchForm.jsx
"Set Alert" and "Advanced" override 4+ properties via inline styles.
**Domain:** Frontend

### M36. [x] .dotd-featured-updated defined but unused — App.css
Dead CSS.
**Domain:** Frontend

### M37. [x] .deals-section-core empty rule — App.css
Dead CSS.
**Domain:** Frontend

### M38. [x] No chart responsive height — PartnerDashboard.css
Fixed 300px, may overflow on mobile.
**Domain:** Frontend

### M39. [x] Hardcoded cyan glow in modals — AuthModal.jsx, ContactModal.jsx
`rgba(0, 243, 255, 0.1)` doesn't adapt to theme.
**Domain:** Frontend

### M40. [x] Number formatting hardcoded ro-RO — 4 components
CarCard, DealOfTheDay, PriceStats, TrustStats all hardcode locale.
**Domain:** Frontend

### M41. [x] emptyStateImg imported but unused — App.jsx
Dead import.
**Domain:** Frontend

### M42. [x] t() function recreated every render — LanguageContext.jsx
Should be useCallback-wrapped.
**Domain:** Frontend

### M43. [x] No search history, saved searches, autocomplete
Missing UX features for returning users.
**Domain:** Frontend

### M44. [x] No alert management page — users can't view/edit/delete alerts
Only create via modal. No list/modify/delete UI.
**Domain:** Frontend + Backend

### M45. [x] No 404 route — App.jsx
Undefined URLs render blank page.
**Domain:** Frontend

### M46. [x] No page title for PartnerDashboard
No Helmet, no meta.
**Domain:** Frontend

### M47. [x] No Open Graph / Twitter Card meta
Missing og:title, og:description, og:image for social sharing.
**Domain:** Frontend

### M48. [x] No structured data JSON-LD
Missing Car/Product/Organization schema for SEO.
**Domain:** Frontend

---

## LOW (48)

### L1. [x] No error boundaries — all routes
Component crash = white screen.
**Domain:** Frontend

### L2. [x] No PropTypes or TypeScript
Zero prop validation across 14 components.
**Domain:** Frontend

### L3. [x] handleSearch not useCallback-wrapped — App.jsx
Recreated every render, passed as prop.
**Domain:** Frontend

### L4. [x] role="alert" missing on error display — App.jsx
Screen readers don't announce errors.
**Domain:** Frontend

### L5. [x] No grid/list view toggle for results
Only grid layout available.
**Domain:** Frontend

### L6. [x] No health check endpoint — backend
No `/health` or `/api/health` for monitoring.
**Domain:** Backend

### L7. [x] No scraper status/metrics endpoint
Can't check scraper state via API.
**Domain:** Backend

### L8. [x] No dead letter queue replay API
replay_iter() exists but no endpoint/CLI.
**Domain:** Backend

### L9. [x] No unsubscribe link in alert emails — mailer.py
GDPR compliance gap.
**Domain:** Backend

### L10. [x] Sender email uses Resend onboarding domain — mailer.py
`onboarding@resend.dev` — test domain in production.
**Domain:** Backend

### L11. [x] Limited sort options exposed via API
Backend supports year/km/created_at sorting but API doesn't expose.
**Domain:** Backend

### L12. [x] get_cron_groups uses numeric index on dict cursor — car_database.py
`r[0]` instead of `r["make"]` on RealDictCursor.
**Domain:** Backend

### L13. [x] Cursor used after commit — car_database.py
Potential cursor invalidation.
**Domain:** Backend

### L14. [x] Autovit catalog brand matching fragile — core_app.py
replace("-benz", "") hack for Mercedes-Benz only.
**Domain:** Backend

### L15. [x] CORS doesn't cover preview domains — core_app.py
Vercel preview deployments get CORS errors.
**Domain:** Backend

### L16. [x] skeleton-pulse white shimmer in light mode — App.css
Invisible loading animation on light bg.
**Domain:** Frontend

### L17. [x] legal-content has no base rules — LegalPage.jsx
Only descendant selectors via inline style.
**Domain:** Frontend

### L18. [x] deals-section-core empty rule — App.css
Dead code.
**Domain:** Frontend

### L19. [x] trust-stats-section missing top border — App.css
No visual separation from hero.
**Domain:** Frontend

### L20. [x] No @media print styles
No print-specific styling.
**Domain:** Frontend

### L21. [x] submit-btn reused for alerts/advanced toggle — SearchForm.jsx
Should have distinct classes.
**Domain:** Frontend

### L22. [x] Theme toggle button no hover/focus styles — App.jsx
Invisible to keyboard users.
**Domain:** Frontend

### L23. [x] TrustStats fully static, never fetches API — TrustStats.jsx
DEFAULT_STATS hardcoded, stats prop never passed.
**Domain:** Frontend

### L24. [x] alert() used for all user feedback
No toast notification system.
**Domain:** Frontend

### L25. [x] No progress indicator during long searches
30+ second scrapes with no progress bar.
**Domain:** Frontend

### L26. [x] Rate limiting aggressive for dealers — core_app.py
3 req/min on contact, 30 req/min on search.
**Domain:** Backend

### L27. [x] No dealer welcome email
After approval, no onboarding email.
**Domain:** Backend

### L28. [~] No messaging system
No in-app buyer-dealer communication.
**Domain:** Frontend + Backend

### L29. [~] No featured listings / sponsored placement
No monetization for premium positioning.
**Domain:** Frontend + Backend

### L30. [~] No white-label option
Dealers can't embed search on their sites.
**Domain:** Frontend + Backend

### L31. [x] No dealer review/rating system
No trust signals for buyers.
**Domain:** Frontend + Backend

### L32. [x] No bulk upload / API sync for dealer inventory
Dealers can't bulk-import or sync from DMS.
**Domain:** Backend

### L33. [x] README references SQLite but system uses PostgreSQL
Confusing for new developers and partners.
**Domain:** Docs

### L34. [x] No canonical URLs — SEO
No link rel="canonical" on results pages.
**Domain:** Frontend

### L35. [x] No sitemap — SEO
No sitemap.xml generation.
**Domain:** Frontend + Backend

### L36. [x] SkeletonCard overly basic — single pulsing block
Should mimic card structure (image, text lines, price).
**Domain:** Frontend

### L37. [x] No dealer review/rating system
Buyers can't rate dealers.
**Domain:** Frontend + Backend

### L38. [x] t() function fragile with null key — LanguageContext.jsx
`t('footer', null, ...)` breaks if footer becomes an object.
**Domain:** Frontend

### L39. [x] GA init no guard against multiple instances — App.jsx
If AppContent rendered outside Routes, duplicate init.
**Domain:** Frontend

### L40. [x] search.advanced includes arrow in translation value
Arrow should be CSS, not in translation string.
**Domain:** Frontend

### L41. [x] No breadcrumb navigation
Users can't see their navigation path.
**Domain:** Frontend

### L42. [x] No car comparison tool
Can't compare multiple listings side by side.
**Domain:** Frontend

### L43. [x] No email verification flow
Registration accepts any email without verification.
**Domain:** Backend

### L44. [x] No password reset flow
Users can't reset forgotten passwords.
**Domain:** Backend + Frontend

### L45. [x] t() not useCallback-wrapped — LanguageContext.jsx
New function reference every render breaks memo.
**Domain:** Frontend

### L46. [x] stat-card::before uses shadow as background — PartnerDashboard.css
Invalid CSS, no visual effect.
**Domain:** Frontend

### L47. [x] login-btn radius changed to 8px but no consistency audit
May differ from other button radii in the app.
**Domain:** Frontend

### L48. [x] No DMS (Dealer Management System) integration docs
No API documentation for dealer inventory sync.
**Domain:** Docs

---

## Progress Summary

| Critical | 24 | 24 | 0 | 0 |
| High | 36 | 36 | 0 | 0 |
| Medium | 48 | 15 | 0 | 33 |
| Low | 48 | 43 | 0 | 5 |
| **Total** | **158** | **76** | **0** | **82** |
