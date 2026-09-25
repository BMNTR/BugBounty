#!/usr/bin/env python3
"""race_probe.py - concurrent request racer for authorized race-condition testing.

Sends N identical requests with a synchronized barrier so they land inside the
TOCTOU window. Use ONLY against endpoints you are authorized to test, on
accounts you own. Keep request counts low to stay out of DoS territory.

Usage:
  python race_probe.py --url https://host/api/coupons/redeem --method POST \
      --header "Cookie: session=abc" --header "Content-Type: application/json" \
      --data '{"code":"SAVE10"}' --threads 20 --requests 40

Output: per-request status/body summary table + count of "success-like" hits.
"""

import argparse
import json
import sys
import threading
import time
import urllib.error
import urllib.request

MAX_REQUESTS = 100
MAX_THREADS = 50


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Authorized race-condition probe")
    p.add_argument("--url", required=True, help="Target endpoint URL")
    p.add_argument("--method", default="POST", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    p.add_argument("--header", action="append", default=[], help="Header 'Name: value' (repeatable)")
    p.add_argument("--data", default=None, help="Raw request body")
    p.add_argument("--threads", type=int, default=10, help="Concurrent threads (1-{})".format(MAX_THREADS))
    p.add_argument("--requests", type=int, default=10, help="Total requests (1-{})".format(MAX_REQUESTS))
    p.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout seconds")
    return p.parse_args()


def build_headers(raw_headers):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for h in raw_headers:
        if ":" not in h:
            print("[!] Ignoring malformed header (no colon): %r" % h, file=sys.stderr)
            continue
        name, _, value = h.partition(":")
        name = name.strip()
        value = value.strip()
        if name and value:
            headers[name] = value
    return headers


def send_one(url: str, method: str, headers: dict, body, timeout: float, idx: int, results: list, lock: threading.Lock):
    try:
        data = body.encode("utf-8") if isinstance(body, str) else None
        req = urllib.request.Request(url, data=data, method=method)
        for k, v in headers.items():
            req.add_header(k, v)
        start = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read(2048).decode("utf-8", errors="replace")
            elapsed_ms = int((time.time() - start) * 1000)
            with lock:
                results.append({"idx": idx, "status": resp.status, "ms": elapsed_ms, "body": payload})
    except urllib.error.HTTPError as e:
        try:
            payload = e.read(2048).decode("utf-8", errors="replace")
        except Exception:
            payload = ""
        with lock:
            results.append({"idx": idx, "status": e.code, "ms": -1, "body": payload})
    except Exception as exc:  # network errors, timeouts
        with lock:
            results.append({"idx": idx, "status": -1, "ms": -1, "body": "ERROR: %s" % exc})


def main() -> int:
    args = parse_args()
    n_req = max(1, min(args.requests, MAX_REQUESTS))
    n_threads = max(1, min(args.threads, MAX_THREADS, n_req))

    headers = build_headers(args.header)
    results = []
    lock = threading.Lock()
    threads = []

    print("[*] Firing %d requests with %d concurrent threads at %s" % (n_req, n_threads, args.url))

    # Pre-spawn threads blocked on a shared event => near-simultaneous fire
    barrier = threading.Event()
    per_thread = max(1, n_req // n_threads)

    def worker(worker_idx):
        barrier.wait()
        for i in range(per_thread):
            idx = worker_idx * per_thread + i
            if idx >= n_req:
                return
            send_one(args.url, args.method, headers, args.data, args.timeout, idx, results, lock)

    for w in range(n_threads):
        t = threading.Thread(target=worker, args=(w,))
        t.start()
        threads.append(t)

    time.sleep(0.2)  # let all threads reach the barrier
    barrier.set()
    for t in threads:
        t.join()

    results.sort(key=lambda r: r["idx"])
    print("\n%-6s %-8s %-8s %s" % ("Req#", "Status", "Ms", "Body excerpt"))
    print("-" * 72)
    success_markers = ('"applied": true', '"applied":true', '"success": true', '"success":true')
    successes = 0
    for r in results:
        excerpt = r["body"].replace("\n", " ")[:60]
        flag = ""
        low = r["body"].lower()
        if any(m.lower() in low for m in success_markers) and r["status"] == 200:
            successes += 1
            flag = "  <-- SUCCESS"
        print("%-6d %-8s %-8s %s%s" % (r["idx"], r["status"], r["ms"], excerpt, flag))

    print("\n[*] Total: %d | success-marker hits: %d" % (len(results), successes))
    print("[*] More than one success hit indicates a race window. Verify server state manually.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
