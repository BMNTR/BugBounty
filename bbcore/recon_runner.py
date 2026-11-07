"""
WAF-aware recon pipeline runner.
Wraps subfinder, httpx, ffuf, nuclei, gau, katana with proxy, delay, and UA rotation.
"""
import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from .proxy_manager import ProxyManager
from .waf_detector import WAFInfo, detect as detect_waf, get_recon_flags

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
]


def random_ua() -> str:
    return random.choice(USER_AGENTS)


def run_tool(
    cmd: list[str],
    proxy: ProxyManager,
    extra_headers: Optional[list[str]] = None,
    timeout: int = 120,
    cwd: Optional[Path] = None,
    input_data: Optional[str] = None,
    active_proxy=None,
) -> tuple[str, str, int]:
    """Run a tool with proxy and headers injected.

    Pass active_proxy (resolved ONCE via proxy.current) so env vars and
    explicit -x/-proxy flags stay in sync in rotate mode. If omitted,
    falls back to proxy.peek() (no rotation).
    """
    env = os.environ.copy()
    if active_proxy is None:
        # One rotation per tool call (preserves intentional WAF-evasion
        # rotation for env-only tools like subfinder/assetfinder).
        active_proxy = proxy.current
    if active_proxy is not None:
        env.update({
            "HTTP_PROXY": active_proxy.url,
            "HTTPS_PROXY": active_proxy.url,
            "ALL_PROXY": active_proxy.url,
            "NO_PROXY": "127.0.0.1,localhost,.local",
        })

    final_cmd = list(cmd)

    # Inject UA if tool supports -H
    if extra_headers:
        final_cmd.extend(extra_headers)

    try:
        r = subprocess.run(
            final_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=str(cwd) if cwd else None,
            input=input_data,
        )
        return r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return "", f"[TIMEOUT] {timeout}s", -1
    except FileNotFoundError:
        return "", f"[NOT FOUND] {cmd[0]} not installed", -2


class ReconRunner:
    """Orchestrates WAF-aware recon using installed tools."""

    def __init__(self, proxy: ProxyManager, bb_dir: Optional[Path] = None):
        self.proxy = proxy
        self.bb_dir = bb_dir if bb_dir is not None else Path(__file__).resolve().parent.parent
        self.tools_dir = self.bb_dir / "tools"
        self.wordlists_dir = self.bb_dir / "wordlists"

    def _tool_path(self, name: str) -> str:
        """Find tool binary."""
        local = self.tools_dir / f"{name}.exe"
        if local.exists():
            return str(local)
        return name  # fallback to PATH

    def _ua_flag(self) -> list[str]:
        return ["-H", f"User-Agent: {random_ua()}"]

    def _rate_flag(self, flags: dict) -> list[str]:
        args = []
        if flags.get("rate_limit"):
            args.extend(["-rl", str(flags["rate_limit"])])
        if flags.get("delay"):
            args.extend(["-delay", flags["delay"]])
        return args

    def preflight_waf_check(self, domain: str) -> tuple[WAFInfo, dict]:
        """Run WAF detection on the target before recon."""
        print(f"  [*] WAF check: {domain}")
        waf = detect_waf(f"https://{domain}")
        rec_flags = get_recon_flags(waf)
        if waf.detected:
            print(f"  [!] WAF DETECTED: {waf.name} ({waf.confidence:.0%})")
            print(f"  [+] Rate limit: {rec_flags['rate_limit']}/min")
            print(f"  [+] Delay: {rec_flags['delay']}")
        else:
            print(f"  [+] No WAF detected")
        return waf, rec_flags

    def phase_subdomains(self, domain: str, out_dir: Path) -> list[str]:
        """Phase 1: Subdomain enumeration."""
        print(f"\n{'='*50}")
        print(f"  PHASE 1: Subdomain Enumeration")
        print(f"{'='*50}")

        subs_file = out_dir / "subs.txt"
        all_subs: set[str] = set()

        # subfinder
        print(f"  [>] subfinder -d {domain}")
        out, err, code = run_tool(
            [self._tool_path("subfinder"), "-d", domain, "-silent"],
            self.proxy,
        )
        if code not in (-2,):
            for line in out.splitlines():
                line = line.strip()
                if line:
                    all_subs.add(line.lower())
        print(f"      subfinder: {len([l for l in out.splitlines() if l.strip()])}")

        # assetfinder
        print(f"  [>] assetfinder --subs-only {domain}")
        out2, err2, code2 = run_tool(
            [self._tool_path("assetfinder"), "--subs-only", domain],
            self.proxy,
        )
        if code2 not in (-2,):
            for line in out2.splitlines():
                line = line.strip()
                if line:
                    all_subs.add(line.lower())
        print(f"      assetfinder: {len([l for l in out2.splitlines() if l.strip()])}")

        total = len(all_subs)
        sorted_subs = sorted(all_subs)
        subs_file.write_text("\n".join(sorted_subs) + "\n")
        print(f"  [+] Total unique subdomains: {total}")
        return sorted_subs

    def phase_alive(
        self, subs: list[str], out_dir: Path, waf_flags: dict
    ) -> list[str]:
        """Phase 2: Alive host probing with browser UA (WAF-friendly)."""
        print(f"\n{'='*50}")
        print(f"  PHASE 2: Live Host Probing")
        print(f"{'='*50}")

        alive_file = out_dir / "alive.txt"
        temp_file = out_dir / "_subs_temp.txt"
        temp_file.write_text("\n".join(subs) + "\n")

        # Resolve proxy ONCE per phase so env + explicit flag stay in sync
        # (ProxyManager.current rotates on every access in rotate mode).
        active_proxy = self.proxy.current

        cmd = [
            self._tool_path("httpx"),
            "-l", str(temp_file),
            "-silent",
            "-status-code",
            "-title",
            "-tech-detect",
            "-follow-redirects",
            "-o", str(alive_file),
        ]

        if active_proxy:
            cmd.extend(["-http-proxy", active_proxy.url])

        print(f"  [>] httpx probing {len(subs)} hosts...")
        # Browser UA matches bbp-web-recon workflow; keeps WAF noise low.
        out, err, code = run_tool(cmd, self.proxy,
                                  extra_headers=self._ua_flag(),
                                  timeout=180,
                                  active_proxy=active_proxy)

        alive_urls: list[str] = []
        if alive_file.exists():
            for line in alive_file.read_text().splitlines():
                line = line.strip()
                if line and line.startswith("http"):
                    alive_urls.append(line)

        print(f"  [+] Alive hosts: {len(alive_urls)}")
        return alive_urls

    def phase_urls(self, subs: list[str], out_dir: Path) -> list[str]:
        """Phase 3: URL collection from passive sources."""
        print(f"\n{'='*50}")
        print(f"  PHASE 3: Passive URL Collection")
        print(f"{'='*50}")

        urls_file = out_dir / "urls.txt"
        all_urls: set[str] = set()

        # gau reads domains from args or stdin; feed subs via stdin so
        # large subdomain lists don't overflow the arg limit.
        print(f"  [>] gau")
        temp_file = out_dir / "_subs_temp.txt"
        temp_file.write_text("\n".join(subs) + "\n")
        out, err, code = run_tool(
            [self._tool_path("gau"), "--o", str(out_dir / "_gau.txt")],
            self.proxy,
            extra_headers=self._ua_flag(),
            timeout=180,
            input_data="\n".join(subs),
        )
        gau_file = out_dir / "_gau.txt"
        if gau_file.exists():
            for line in gau_file.read_text().splitlines():
                line = line.strip()
                if line:
                    all_urls.add(line)

        # waybackurls reads from stdin only; reuse gau's proxy slot so both
        # passive sources share one rotation per phase.
        print(f"  [>] waybackurls")
        wb_proxy = self.proxy.peek()
        wb_env = {**os.environ}
        if wb_proxy is not None:
            wb_env.update({
                "HTTP_PROXY": wb_proxy.url,
                "HTTPS_PROXY": wb_proxy.url,
                "ALL_PROXY": wb_proxy.url,
            })
        try:
            r = subprocess.run(
                [self._tool_path("waybackurls")],
                input="\n".join(subs),
                capture_output=True,
                text=True,
                timeout=120,
                env=wb_env,
            )
            for line in r.stdout.splitlines():
                line = line.strip()
                if line:
                    all_urls.add(line)
        except Exception:
            pass

        total = len(all_urls)
        urls_file.write_text("\n".join(sorted(all_urls)) + "\n")
        print(f"  [+] Unique URLs collected: {total}")
        return sorted(all_urls)

    def phase_triagetalon(
        self, domain: str, out_dir: Path
    ):
        """Phase 3.5: Passive Triage using TriageTalon."""
        print(f"\n{'='*50}")
        print(f"  PHASE 3.5: Passive Triage (TriageTalon)")
        print(f"{'='*50}")

        target_name = out_dir.parent.name
        tt_script = self.bb_dir / "TriageTalon" / "recon_local_pro.py"
        
        if not tt_script.exists():
            print("  [-] TriageTalon not found. Skipping.")
            return

        cmd = ["python", str(tt_script), domain, target_name]
        print(f"  [>] python recon_local_pro.py {domain} {target_name}")
        out, err, code = run_tool(cmd, self.proxy, timeout=600)
        print("  [+] TriageTalon completed")

    def phase_nuclei(
        self, alive_urls: list[str], out_dir: Path, waf_flags: dict
    ):
        """Phase 4: Vulnerability scan with WAF-aware rate limiting."""
        print(f"\n{'='*50}")
        print(f"  PHASE 4: Vulnerability Scan (Nuclei)")
        print(f"{'='*50}")

        if not alive_urls:
            print("  [-] No alive hosts to scan")
            return

        alive_file = out_dir / "alive.txt"
        nuclei_file = out_dir / "nuclei.txt"

        cmd = [
            self._tool_path("nuclei"),
            "-l", str(alive_file),
            "-severity", "critical,high,medium",
            "-o", str(nuclei_file),
            "-silent",
        ]

        if waf_flags["rate_limit"] < 100:
            cmd.extend(["-rl", str(waf_flags["rate_limit"]), "-bs", "15"])

        active_proxy = self.proxy.current
        if active_proxy:
            cmd.extend(["-proxy", active_proxy.url])

        print(f"  [>] nuclei scan (rate-limit={waf_flags['rate_limit']}/min)")
        out, err, code = run_tool(cmd, self.proxy,
                                  extra_headers=self._ua_flag(),
                                  timeout=600,
                                  active_proxy=active_proxy)

        findings = []
        if nuclei_file.exists():
            for line in nuclei_file.read_text().splitlines():
                line = line.strip()
                if line:
                    findings.append(line)

        print(f"  [+] Nuclei findings: {len(findings)}")
        for f in findings[:10]:
            print(f"      {f[:120]}")
        if len(findings) > 10:
            print(f"      ... and {len(findings) - 10} more")

    def phase_ffuf(
        self, alive_urls: list[str], out_dir: Path, waf_flags: dict,
        wordlist: Optional[str] = None
    ):
        """Phase 5: Content discovery with delay and jitter."""
        print(f"\n{'='*50}")
        print(f"  PHASE 5: Content Discovery (ffuf)")
        print(f"{'='*50}")

        if not alive_urls:
            return

        # Find wordlist
        if not wordlist or not Path(wordlist).exists():
            candidates = [
                Path(self.wordlists_dir) / "SecLists" / "Discovery" / "Web-Content" / "common.txt",
                Path(self.wordlists_dir) / "SecLists" / "Discovery" / "Web-Content" / "raft-small-words.txt",
            ]
            for c in candidates:
                if c.exists():
                    wordlist = str(c)
                    break

        if not wordlist or not Path(wordlist).exists():
            print("  [-] No wordlist found. Skipping ffuf.")
            return

        # Only scan top 3 targets to avoid massive bans
        targets = alive_urls[:3]
        active_proxy = self.proxy.current
        for t in targets:
            safe = t.replace("://", "_").replace("/", "_").replace(".", "_")
            out_json = out_dir / f"ffuf_{safe}.json"
            cmd = [
                self._tool_path("ffuf"),
                "-u", f"{t}/FUZZ",
                "-w", wordlist,
                "-ac",
                "-t", "30",
                "-o", str(out_json),
                "-of", "json",
                "-fc", "404",
            ]
            cmd.extend(self._ua_flag())
            if waf_flags["jitter"]:
                cmd.extend(["-p", waf_flags["jitter"]])
            if active_proxy:
                cmd.extend(["-x", active_proxy.url])

            print(f"  [>] ffuf {t} ({wordlist})")
            out, err, code = run_tool(cmd, self.proxy, timeout=120,
                                      active_proxy=active_proxy)

            # Parse results
            if out_json.exists():
                try:
                    data = json.loads(out_json.read_text())
                    results = data.get("results", [])
                    print(f"      Found {len(results)} entries")
                except Exception:
                    pass

    def phase_katana(
        self, alive_urls: list[str], out_dir: Path
    ):
        """Active crawling with katana."""
        print(f"\n{'='*50}")
        print(f"  PHASE: Active Crawl (katana)")
        print(f"{'='*50}")
        if not alive_urls:
            return
        alive_file = out_dir / "alive.txt"
        out_file = out_dir / "katana_urls.txt"
        cmd = [
            self._tool_path("katana"),
            "-l", str(alive_file),
            "-o", str(out_file),
            "-silent", "-jc", "-kf",
        ]
        print(f"  [>] katana crawling {len(alive_urls)} hosts...")
        out, err, code = run_tool(cmd, self.proxy, extra_headers=self._ua_flag(), timeout=180)
        count = 0
        if out_file.exists():
            count = len(out_file.read_text().splitlines())
        print(f"      {count} URLs discovered")

    def phase_gowitness(
        self, alive_urls: list[str], out_dir: Path
    ):
        """Screenshots of live hosts."""
        print(f"\n{'='*50}")
        print(f"  PHASE: Screenshots (gowitness)")
        print(f"{'='*50}")
        if not alive_urls:
            return
        alive_file = out_dir / "alive.txt"
        screen_dir = out_dir / "screenshots"
        screen_dir.mkdir(exist_ok=True)
        cmd = [
            self._tool_path("gowitness"), "file", "-f", str(alive_file),
            "-P", str(screen_dir), "--no-http",
        ]
        print(f"  [>] gowitness screenshots...")
        run_tool(cmd, self.proxy, timeout=300)
        count = len(list(screen_dir.glob("*"))) if screen_dir.exists() else 0
        print(f"      {count} screenshots saved")

    def run_full(
        self, domain: str, out_dir: Path, skip_nuclei: bool = False,
        skip_ffuf: bool = False
    ) -> dict:
        """Run full recon pipeline with WAF-awareness."""
        start = datetime.now()
        print(f"\n{'#'*60}")
        print(f"  BugBounty Recon: {domain}")
        print(f"  Output: {out_dir}")
        print(f"  Proxy:  {self.proxy.status_text()}")
        print(f"{'#'*60}\n")

        out_dir.mkdir(parents=True, exist_ok=True)

        # Preflight WAF check
        waf, waf_flags = self.preflight_waf_check(domain)

        # Phase 1: Subdomains
        subs = self.phase_subdomains(domain, out_dir)
        if not subs:
            print("[-] No subdomains found. Aborting.")
            return {"domain": domain, "error": "no subdomains"}

        # Phase 2: Alive hosts
        alive = self.phase_alive(subs, out_dir, waf_flags)

        # Phase 3: URL collection
        urls = self.phase_urls(subs, out_dir)

        # Phase 3.5: Passive Triage (TriageTalon)
        if alive:
            self.phase_triagetalon(domain, out_dir)

        # Phase 4: Nuclei
        if not skip_nuclei and alive:
            self.phase_nuclei(alive, out_dir, waf_flags)

        # Phase 5: ffuf
        if not skip_ffuf and alive:
            self.phase_ffuf(alive, out_dir, waf_flags)

        # Phase 6: Active crawl (katana)
        if alive:
            self.phase_katana(alive, out_dir)

        # Phase 7: Screenshots (gowitness)
        if alive:
            self.phase_gowitness(alive, out_dir)

        elapsed = (datetime.now() - start).total_seconds()
        summary = {
            "domain": domain,
            "subdomains": len(subs),
            "alive": len(alive),
            "urls": len(urls),
            "waf": waf.name if waf.detected else "None",
            "elapsed_seconds": round(elapsed),
            "output_dir": str(out_dir),
        }

        # Write summary
        summary_file = out_dir / "_recon_summary.json"
        summary_file.write_text(json.dumps(summary, indent=2))

        print(f"\n{'='*50}")
        print(f"  RECON COMPLETE ({elapsed:.0f}s)")
        print(f"  Subdomains: {summary['subdomains']}")
        print(f"  Alive:      {summary['alive']}")
        print(f"  URLs:       {summary['urls']}")
        print(f"  WAF:        {summary['waf']}")
        print(f"{'='*50}")

        return summary
