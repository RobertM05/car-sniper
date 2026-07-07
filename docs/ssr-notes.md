# SSR Setup — Status & Next Steps

**Date:** 2026-07-07
**Status:** Merged to main, SPA mode active on Vercel

## What's in the repo

vike SSR files ready but inactive:
```
pages/_default/+config.js       — vike config
pages/index/+Page.jsx           — SSR entry point
renderer/+onRenderHtml.jsx      — Server-side HTML renderer
renderer/+onRenderClient.jsx    — Client hydration
server/index.mjs                — Express production server
```

Both client and SSR bundles build clean.

## Why it's not active

Vercel static hosting can't run a Node server. vike needs either serverless functions or an Express server. `vercel.json` is set to SPA fallback mode.

## Next steps (pick one)

**A — Vercel Serverless (keeps Vercel)**
Create `api/ssr.js` calling `renderPage()` from vike. vike has a Vercel adapter.

**B — Express server (leaves Vercel)**
Deploy `server/index.mjs` to Railway or Render.

**C — Next.js migration (best long-term)**
Full rewrite. Built-in SSR. Planned for next month.

## Quick SPA fallback
```json
{ "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }
```
