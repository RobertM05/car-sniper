## Summary
<!-- What does this PR do? -->

## Checklist
- [ ] Lint passes (`ruff check backend/`)
- [ ] No new `except: pass` or bare exceptions
- [ ] No changes to rate-limiting / anti-detection without explicit approval
- [ ] Database migrations are backward-compatible
- [ ] SESSION_NOTES.md updated if audit bugs are addressed

## Risk Assessment
- [ ] **Low** — code quality / logging / tests only
- [ ] **Medium** — data processing logic changes
- [ ] **High** — scraping behavior, rate limits, or anti-detection changes
