# Motorbit — Implementation Plan for Remaining 23 Items

**Date:** 2026-07-06 | **Branch:** `feature/canva-design-upgrade`

## Phase 1: Bug Fixes (3 items — NOW)

### M26. Duplicate log messages — `start_crawler.py`
**Spec:** Remove duplicate `log.info(...)` lines. Read file, deduplicate consecutive identical log calls, preserve indentation.
**Files:** `start_crawler.py`
**AC:** Python compiles without IndentationError, no duplicate log lines remain.
**Out of scope:** Do not change log content, only remove exact duplicates.

### L3. handleSearch useCallback — `App.jsx`
**Spec:** Wrap `handleSearch` in `useCallback` with dependency array `[API_BASE_URL]`. Since `handleSearch` reads `formData` directly and also accepts `overrideData`, the closure needs the latest `formData`. Use a ref (`formDataRef`) to track current formData without adding it to deps. Update the ref in a useEffect whenever formData changes.
**Files:** `App.jsx`
**AC:** Build passes, search still works, no stale closure.
**Out of scope:** Do not change handleSearch logic or parameters.

### L13. Cursor used after commit — `car_database.py`
**Spec:** Find cursor operations where `conn.commit()` is called before `cursor.close()`. Reorder to close cursor first or use `with` statement for cursor lifecycle.
**Files:** `car_database.py`
**AC:** Python compiles, no cursor-after-commit warnings.
**Out of scope:** Do not change query logic.

---

## Phase 2: Dealer + Auth Flows (4 items — NOW)

### L27. Dealer welcome email — `mailer.py` + `core_app.py`
**Spec:** Add `send_dealer_welcome_email(email, company_name)` function to mailer.py. Call it from `api_register_dealer` after saving the contact submission. Email content: welcome message with link to PartnerDashboard.
**Files:** `mailer.py`, `core_app.py`
**AC:** Email sent on dealer registration, function has try/except guard.
**Out of scope:** Do not create HTML email template — plain text is fine.

### L43. Email verification flow — `core_app.py` + `mailer.py`
**Spec:** On user registration, generate a verification token (JWT with short expiry), store `email_verified = FALSE` on user, send verification email. Add `GET /api/verify-email?token=...` endpoint that sets `email_verified = TRUE`. Add `email_verified` column to users table. On login, warn if email not verified (but don't block).
**Files:** `core_app.py`, `car_database.py`, `mailer.py`
**AC:** Token generated, email sent, verification endpoint works, column added.
**Out of scope:** Do not block unverified users from using the app.

### L44. Password reset flow — `core_app.py` + `mailer.py`
**Spec:** Add `POST /api/forgot-password` (sends reset email with JWT token) and `POST /api/reset-password` (validates token, updates password). Token expires in 1 hour. Add `send_password_reset_email(email, token)` to mailer.py.
**Files:** `core_app.py`, `mailer.py`
**AC:** Reset email sent, password updated on valid token, token rejected if expired.
**Out of scope:** Do not create reset page UI — API only. Frontend page is separate task.

### M17. Dealer approval workflow — `core_app.py` + `car_database.py`
**Spec:** Add `GET /api/admin/pending-dealers` (returns unverified profiles). Add `POST /api/admin/approve-dealer?dealer_id=X` (approves dealer, sends welcome email). Protect both with a simple admin check (user role == 'admin'). Already have `get_pending_dealers()` and `approve_dealer()` DB methods.
**Files:** `core_app.py`
**AC:** Endpoints return correct data, approval triggers welcome email.
**Out of scope:** Do not create admin UI page — API only.

---

## Phase 3: User Features (3 items — NOW)

### M44. Alert management page — New component
**Spec:** Create `AlertManager.jsx` component. Shows table of user's alerts with columns: make, model, max price, created date, status (active/paused). Each row has a delete button. Add `GET /api/alerts?email=...` and `DELETE /api/alerts/:id` endpoints. Add route `/alerts` to App.jsx. Add nav link "Alertele mele" when user is logged in.
**Files:** New: `AlertManager.jsx`. Modified: `core_app.py`, `App.jsx`, `LanguageContext.jsx`
**AC:** Alerts displayed in table, delete works, page has loading/empty states, i18n RO/EN.
**Out of scope:** Do not add edit functionality — delete only.

### L41. Breadcrumb navigation — New component
**Spec:** Create `Breadcrumbs.jsx` component. Shows: Home > Make > Model for search results, Home > Dealer for dealer profile, etc. Reads current route and builds breadcrumb trail. Add to App.jsx layout. Style as subtle horizontal row below nav.
**Files:** New: `Breadcrumbs.jsx`. Modified: `App.jsx`, `App.css`
**AC:** Breadcrumbs render correctly for all routes, links are clickable, styling is subtle.
**Out of scope:** Do not add schema.org breadcrumb JSON-LD.

### L25. Progress indicator during long searches — `App.jsx`
**Spec:** When `loading` is true and search has been running > 3 seconds, show a progress message below the skeleton cards: "Searching OLX and Autovit... this may take up to 30 seconds." Use a simple setTimeout to toggle the message visibility. Add i18n key `search.progressMessage`.
**Files:** `App.jsx`, `LanguageContext.jsx`
**AC:** Progress message appears after 3s of loading, disappears when results arrive.
**Out of scope:** Do not add actual progress percentage — just the message.

---

## Phase 4: Future Planning (Business — DOCUMENT ONLY)

These items require significant architecture, third-party integrations, or business decisions. Document approach in HANDOFF.md but do NOT implement now.

- **M15**: Dealer pricing — needs payment integration (Stripe), subscription tiers
- **L28**: Messaging system — needs WebSocket infrastructure, real-time DB
- **L29**: Featured listings — needs payment + boost algorithm
- **L30**: White-label — needs multi-tenant architecture
- **L31**: Dealer reviews — needs moderation system
- **L32**: Bulk upload — needs file processing, CSV parsing, image handling
- **L42**: Car comparison — needs complex UI, localStorage persistence
- **L2**: TypeScript migration — months of work, needs dedicated project
- **L8**: Dead letter queue replay — needs queue management UI
- **L48**: DMS docs — needs external documentation site
- **M18**: Dealer analytics — needs real metrics tracking first
- **M43**: Search history — needs user activity tracking table
