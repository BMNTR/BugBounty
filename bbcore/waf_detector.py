"""
WAF detection and bypass strategy engine.
Detects WAF type, suggests bypass headers, and adjusts tool flags.
"""
import re
from dataclasses import dataclass, field
from typing import Optional

import requests


WAF_SIGNATURES = {
    "Cloudflare": [
        r"cloudflare-nginx",
        r"__cfduid",
        r"cf-ray",
        r"cf-cache-status",
        r"server: cloudflare",
        r"challenge-platform",
        r"cdn-cgi\/challenge",
    ],
    "Akamai": [
        r"akamai",
        r"akamaighost",
        r"x-akamai",
        r"x-akamaid",
    ],
    "AWS WAF": [
        r"awswaf",
        r"x-amzn-requestid",
        r"x-amzn-errortype",
    ],
    "Imperva / Incapsula": [
        r"incapsula",
        r"imperva",
        r"x-iinfo",
        r"visid_incap",
    ],
    "ModSecurity": [
        r"mod_security",
        r"modsecurity",
        r"NOYB",
    ],
    "F5 BIG-IP ASM": [
        r"big-ip",
        r"ts\w{5,}=",
        r"x-wa-ident",
    ],
    "Sucuri": [
        r"sucuri",
        r"x-sucuri",
    ],
    "Barracuda": [
        r"barracuda",
        r"xn--",
    ],
}


@dataclass
class WAFInfo:
    detected: bool = False
    name: str = ""
    confidence: float = 0.0
    headers: dict = field(default_factory=dict)
    status_code: int = 0
    response_preview: str = ""


def detect(target_url: str, timeout: int = 15) -> WAFInfo:
    """
    Detect WAF by sending probe requests and analyzing responses.
    Returns WAFInfo with detection results.
    """
    info = WAFInfo()

    try:
        resp = requests.get(
            target_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/125.0.0.0 Safari/537.36"
            },
            timeout=timeout,
            allow_redirects=True,
        )
    except requests.RequestException:
        return info

    info.status_code = resp.status_code
    info.headers = dict(resp.headers)
    info.response_preview = resp.text[:500]

    body_lower = resp.text.lower()
    headers_text = str(resp.headers).lower()

    # Check against known signatures
    best_match = ""
    best_score = 0.0

    for waf_name, patterns in WAF_SIGNATURES.items():
        score = 0.0
        for pattern in patterns:
            if re.search(pattern, headers_text, re.IGNORECASE):
                score += 0.3
            if re.search(pattern, body_lower, re.IGNORECASE):
                score += 0.2

        if score > best_score:
            best_score = score
            best_match = waf_name

    if best_score > 0.3:
        info.detected = True
        info.name = best_match
        info.confidence = min(best_score, 1.0)
    elif resp.status_code in (403, 429, 503):
        info.detected = True
        info.name = "Generic WAF (blocked)"
        info.confidence = 0.5

    return info


def get_bypass_headers(waf_name: str) -> dict[str, str]:
    """Get recommended headers to bypass specific WAF."""
    common = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    bypasses = {
        "Cloudflare": {
            **common,
            "X-Forwarded-For": "8.8.8.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
        "Akamai": {
            **common,
            "X-Forwarded-For": "8.8.4.4",
            "Akamai-Origin-Hop": "1",
        },
        "AWS WAF": {
            **common,
            "X-Forwarded-For": "127.0.0.1",
        },
        "Imperva / Incapsula": {
            **common,
            "X-Forwarded-For": "10.0.0.1",
            "X-Incapsula-Request": "1",
        },
        "ModSecurity": {
            **common,
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        },
    }
    return bypasses.get(waf_name, common)


def get_recon_flags(waf: WAFInfo) -> dict:
    """Get recommended tool flags based on WAF detection."""
    flags = {
        "rate_limit": 150,
        "delay": "0s",
        "jitter": "",
        "timeout": 10,
    }

    if not waf.detected:
        return flags

    if waf.confidence > 0.7:
        flags["rate_limit"] = 30
        flags["delay"] = "2s"
        flags["jitter"] = "0.5-1.5"
        flags["timeout"] = 15
    elif waf.confidence > 0.4:
        flags["rate_limit"] = 60
        flags["delay"] = "1s"
        flags["jitter"] = "0.3-1.0"
        flags["timeout"] = 12
    else:
        flags["rate_limit"] = 100
        flags["delay"] = "0.5s"
        flags["timeout"] = 10

    return flags
