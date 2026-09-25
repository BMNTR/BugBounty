#!/usr/bin/env python3
"""graphql_recon.py - authorized GraphQL endpoint discovery and introspection.

Capabilities:
  --discover    probe a built-in path list for a working GraphQL endpoint
  --introspect  send full introspection query and save JSON schema dump
  --suggest     probe field-name suggestions to leak schema hints

Use only against endpoints you are authorized to test. Request volume is
deliberately minimal (one request per candidate path / probe).

Usage:
  python graphql_recon.py --url https://host/api/graphql --introspect --out schema.json
  python graphql_recon.py --base https://host --discover
"""

import argparse
import json
import sys
import urllib.error
import urllib.request

PATHS = [
    "/graphql", "/graphiql", "/api/graphql", "/api/graphiql", "/app/graphql",
    "/v1/graphql", "/v2/graphql", "/gql", "/query", "/explorer",
    "/playground", "/altair", "/service/graphql", "/internal/graphql",
]

INTROSPECTION_QUERY = (
    "query IntrospectionQuery { __schema { queryType { name } "
    "mutationType { name } subscriptionType { name } "
    "types { kind name description fields(includeDeprecated: true) { name "
    "args { name type { kind name ofType { kind name } } } "
    "type { kind name ofType { kind name ofType { kind name } } } "
    "isDeprecated deprecationReason } } directives { name locations } } }"
)

SUGGEST_PROBES = ["userr", "userz", "queryy", "mutationn", "orderz", "tokenn"]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def post_json(url: str, payload: dict, timeout: float = 10.0):
    """POST JSON, return (status, body_text). Never raises on HTTP errors."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(65536).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read(65536).decode("utf-8", errors="replace")
        except Exception:
            return e.code, ""
    except Exception as exc:
        return -1, "ERROR: %s" % exc


def looks_like_graphql(body: str) -> bool:
    if not body:
        return False
    lowered = body.lower()
    return ("typename" in lowered or "__schema" in lowered
            or "cannot query" in lowered or "did you mean" in lowered)


def discover(base: str) -> int:
    base = base.rstrip("/")
    print("[*] Probing %d candidate paths..." % len(PATHS))
    found = []
    for p in PATHS:
        status, body = post_json(base + p, {"query": "{ __typename }"})
        ok = status == 200 and looks_like_graphql(body)
        marker = "[+] ENDPOINT" if ok else "[-] "
        print("%s %-22s status=%s %s" % (marker, p, status, body[:60].replace("\n", " ")))
        if ok:
            found.append(base + p)
    if found:
        print("\n[*] Working GraphQL endpoints:")
        for f in found:
            print("    " + f)
    else:
        print("\n[*] No endpoint found from list. Try JS bundle analysis for paths.")
    return 0


def introspect(url: str, out: str | None) -> int:
    if not out:
        out = "introspection_schema.json"
    status, body = post_json(url, {"query": INTROSPECTION_QUERY})
    if status != 200 or "__schema" not in body:
        print("[!] Introspection failed (status=%s)." % status)
        print("[!] Body excerpt: %s" % body[:200])
        print("[*] Try the bypass ladder in references/workflows.md.")
        return 1
    try:
        parsed = json.loads(body)
    except ValueError as exc:
        print("[!] Response was not valid JSON: %s" % exc)
        return 2
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(parsed, fh, indent=2)
    types = []
    try:
        types = [t.get("name") for t in parsed["data"]["__schema"]["types"] if t.get("name")]
    except (KeyError, TypeError) as exc:
        print("[!] Unexpected introspection shape: %s" % exc)
    print("[+] Introspection succeeded. %d types dumped -> %s" % (len(types), out))
    interesting = [t for t in types if any(
        k in t.lower() for k in ("admin", "token", "internal", "secret", "user", "payment"))]
    if interesting:
        print("[*] Interesting types worth queueing for BOLA tests:")
        for t in interesting[:25]:
            print("      " + t)
    return 0


def suggest(url: str) -> int:
    print("[*] Probing suggestion-based schema leaks (low volume)...")
    leaks = []
    for probe in SUGGEST_PROBES:
        status, body = post_json(url, {"query": "{ %s { __typename } }" % probe})
        if "Did you mean" in body:
            # extract the suggestion list verbatim
            idx = body.find("Did you mean")
            snippet = body[idx:idx + 160].replace("\n", " ")
            print("[+] Suggest leak on '%s': %s" % (probe, snippet))
            leaks.append({"probe": probe, "hint": snippet})
        else:
            print("[-] No leak via '%s' (status=%s)" % (probe, status))
    print("[*] %d/%d probes leaked names. Feed hits into clairvoyance for full recovery." % (
        len(leaks), len(SUGGEST_PROBES)))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Authorized GraphQL recon helper")
    p.add_argument("--url", help="Full GraphQL endpoint URL")
    p.add_argument("--base", help="Base URL for --discover mode")
    p.add_argument("--discover", action="store_true", help="Probe common endpoint paths")
    p.add_argument("--introspect", action="store_true", help="Attempt full introspection")
    p.add_argument("--suggest", action="store_true", help="Probe error-suggestion leaks")
    p.add_argument("--out", help="Output file for introspection dump")
    args = p.parse_args()

    if args.discover:
        if not args.base:
            print("[!] --discover requires --base https://host")
            return 1
        return discover(args.base)

    if not args.url:
        print("[!] Provide --url <endpoint> or --discover --base <url>")
        return 1

    rc = 0
    if args.introspect:
        rc = introspect(args.url, args.out)
    if args.suggest:
        rc = suggest(args.url) or rc
    if not args.introspect and not args.suggest:
        status, body = post_json(args.url, {"query": "{ __typename }"})
        print("status=%s body=%s" % (status, body[:300]))
        print(looks_like_graphql(body) and "[+] Looks like GraphQL." or "[-] Not obviously GraphQL.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
