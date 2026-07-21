# Anchored Summary — Just Eat Takeaway.com Bug Bounty (updated 2026-07-13)

## Objective
- Bug bounty recon on Just Eat Takeaway.com (Bugcrowd: engagements/justeattakeaway), strict-scoped, manual testing of high-value targets (auth/payment/API/shortlink). Pivot to POS / Order APIs in progress.

## Important Details
- Program: `https://bugcrowd.com/engagements/justeattakeaway`; user **BMNTR** (Rafli Bimantara); header `X-Bug-Bounty: BMNTR` on all target traffic.
- 20 wildcard IN-SCOPE (`*.takeaway.com`, `*.just-eat.io`, `*.jet-external.com`, `*.thuisbezorgd.nl`, `*.lieferando.de`, `*.just-eat.es`, etc.); staging in-scope; **open-redirect excluded**; @bugcrowdninja.com for signup.
- Cloudflare blocks our IP (110.138.x) on ALL prod JET web/API hosts (uk.api.just-eat.io, tconnect.just-eat.com, www.just-eat.es -> "Just a moment..."). Staging API + several prod hosts (tconnect.takeaway.com, tcapp, pull-posapi, posapi, restaurant-openclose, live-orders-api, restaurant-portal-api) are REACHABLE (no CF challenge).
- `auth.jet-external.com` (prod auth) = DNS FAIL from our env.
- agent-browser: invoke ONLY via `cmd /c "agent-browser ..."`; currently BROKEN in this env (`Unknown: ChildProcess.kill`, `doctor --fix` hangs) — cannot render authenticated SPA pages.
- curlfix: Windows curl intermittent `getaddrinfo() thread failed to start` -> use retry loop.

## Work State
### Completed
- short.takeaway.com: Bitly short domain, no eligible surface (open-redirect excluded) -> deprioritized.
- Staging API (api-lieferando-de-stage): reachable, rejects prod JWT (invalid_token); all sensitive endpoints need staging token (unobtainable). Enumerated 85 paths -> real endpoints need auth; public search no vuln.
- **PIVOT**: open S3 bucket `tcapp.takeaway.com` (read-only listing) exposed tconnectapp APKs + **POS/Order API manuals** -> led to discovering:
  - `pull-posapi.takeaway.com` — `GET /1.1/orders/<RestaurantId>` (Apikey header + Basic Auth) returns orders + customer PII. Reachable; 401 without creds (confirmed).
  - `posapi.takeaway.com` — `POST /login` {apiKey, restaurant, ...} -> returns **HS256 JWT** (Bearer). Validates (apiKey,restaurant) pair (401 "No restaurant matched..."). 
  - `restaurant-openclose.takeaway.com` — `POST /open|close/<date>` (405 on GET), Bearer JWT.
- Reverse-engineered tconnectapp APK (Qt5/C++): no hardcoded creds/URLs.
- tconnect.takeaway.com: Spring Boot `/actuator/health` exposed (low).
- live-orders-api / restaurant-portal-api: reachable, no public specs, no unauth findings.
- **Draft report written**: `programs/engagements-justeattakeaway/reports/draft_report.md` (Report 1: BOLA + suspected HS256 JWT forgery on POS/Order APIs; Report 2: open S3 listing low; Report 3: actuator low). PoC for Report 1 PENDING a valid test POS apiKey.

### Blocked
- **Report 1 PoC needs a valid vendor POS apiKey** (manual says test keys available via jetconnectsupport@justeattakeaway.com or program test-cred facility). Without it, BOLA/JWT-forgery is unconfirmed hypothesis.
- Browser automation broken (ChildProcess.kill / hangs) -> cannot scrape Bugcrowd Targets tab for creds; curl XHR endpoints for Targets not discoverable (return SPA shell / 404).
- Prod JWT (user-provided, nl tenant) unusable: staging rejects, prod CF-blocked, auth server DNS-fails.

## Next Move
1. To complete Report 1: obtain a test POS apiKey -> login -> decode JWT -> test HS256 secret==apiKey forgery (close any restaurant via /close, read other restaurants' orders via pull-posapi). 
2. If no key: Report 1 stays a design-level hypothesis (lower acceptance risk on JET); Reports 2/3 are low-severity.
3. Alternative: deeper mobile RE of tconnectapp, or pivot to other in-scope hosts.

## Relevant Files
- `programs/engagements-justeattakeaway/reports/draft_report.md` — DRAFT reports (primary deliverable).
- `programs/engagements-justeattakeaway/notes/pivot_recon.md` — POS/Order API recon + BOLA hypothesis.
- `programs/engagements-justeattakeaway/notes/staging_enum.md` — staging API enum + token blocker.
- `programs/engagements-justeattakeaway/notes/api_recon.md`, `short_takeaway_com.md`.
- `programs/engagements-justeattakeaway/evidence/` — tcapp_s3_listing.xml, manuals_*.pdf, live_android_tconnectapp-2.155.apk, external_api_full.txt, posapi_full.txt, extract/dump/scan scripts.
- `programs/engagements-justeattakeaway/notes/jwt.txt` — user prod JWT (nl, unusable here).
- `programs/engagements-justeattakeaway/recon/takeaway.com_alive.txt` — 78 alive hosts.
- `C:\BugBounty\cookies.txt` — valid Bugcrowd session (BMNTR); authenticated API calls work (e.g. /scope_ranks).
