"""
Main orchestrator — connects proxy manager, recon runner, skill loader,
specialized scripts, and program state into one unified interface.
"""
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from .proxy_manager import ProxyManager
from .recon_runner import ReconRunner
from .skill_loader import SkillLoader

BB_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BB_DIR / "_templates"
SCRIPTS_DIR = BB_DIR / "scripts"


def slugify(url_or_host: str) -> str:
    """Single slug convention: host lowercased, dots/underscores -> dashes.

    Preserved for existing programs (use_program takes slug as-is); only
    new init/triagetalon defaults go through here.
    """
    import re
    h = (url_or_host or "").strip().lower()
    if "://" in h:
        h = h.split("//", 1)[1]
    h = h.split("/")[0].split(":")[0].split("?")[0]
    h = h.lstrip(".")
    h = h.replace("_", "-").replace(".", "-")
    h = re.sub(r"[^a-z0-9-]", "-", h)
    h = re.sub(r"-{2,}", "-", h).strip("-")
    return h or "program"


class ProgramState:
    def __init__(self, slug: str):
        self.slug = slug
        self.dir = BB_DIR / "programs" / slug
        self.state_file = self.dir / "state.json"
        self.data = self._load()

    def _load(self) -> dict:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except Exception:
                pass
        return {
            "program": self.slug,
            "slug": self.slug,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "phase": "init",
            "domains": [],
            "subdomains": {"total": 0, "scanned": False, "file": ""},
            "alive": {"total": 0, "scanned": False, "file": ""},
            "urls": {"total": 0, "scanned": False, "file": ""},
            "scans": [],
            "queue": [],
            "errors": [],
        }

    def save(self):
        self.dir.mkdir(parents=True, exist_ok=True)
        self.data["updated"] = datetime.now().isoformat()
        self.state_file.write_text(json.dumps(self.data, indent=2))

    def set(self, key: str, value):
        self.data[key] = value
        self.save()

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    @property
    def recon_dir(self) -> Path:
        d = self.dir / "recon"; d.mkdir(parents=True, exist_ok=True); return d

    @property
    def evidence_dir(self) -> Path:
        d = self.dir / "evidence"; d.mkdir(parents=True, exist_ok=True); return d

    @property
    def reports_dir(self) -> Path:
        d = self.dir / "reports"; d.mkdir(parents=True, exist_ok=True); return d

    @property
    def scripts_dir(self) -> Path:
        d = self.dir / "scripts"; d.mkdir(parents=True, exist_ok=True); return d

    @property
    def temp_dir(self) -> Path:
        d = self.dir / "temp"; d.mkdir(parents=True, exist_ok=True); return d


class Orchestrator:
    def __init__(self, bb_dir: Path = BB_DIR):
        self.bb_dir = bb_dir
        self.proxy = ProxyManager()
        self.recon = ReconRunner(self.proxy, bb_dir)
        self.skills = SkillLoader(bb_dir)
        self._program: Optional[ProgramState] = None

    @property
    def program(self) -> Optional[ProgramState]:
        return self._program

    def use_program(self, slug: str) -> ProgramState:
        self._program = ProgramState(slug)
        return self._program

    def _create_bb_toml(self, url: str, slug: str, classification: str):
        """Create bb.toml from template."""
        tmpl = TEMPLATES_DIR / "bb.toml"
        if not tmpl.exists():
            return
        content = tmpl.read_text()
        content = content.replace("target-name", slug)
        content = content.replace("target.com", url.split("//")[-1].split("/")[0])
        out = self._program.dir / "policy" / "bb.toml"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content)

    def init_program(self, url: str, name: Optional[str] = None) -> ProgramState:
        slug = slugify(name) if name else slugify(url)
        prog = self.use_program(slug)
        classification = self.skills.classify_from_url(url)
        prog.set("url", url)
        prog.set("status", "initialized")
        prog.set("phase", "init")
        prog.set("classification", classification)
        prog.set("domains", [url])
        # Create subdirs
        prog.recon_dir; prog.evidence_dir; prog.reports_dir
        prog.scripts_dir; prog.temp_dir
        # Create bb.toml from template
        self._create_bb_toml(url, slug, classification)
        print(f"[+] Program initialized: {slug}")
        print(f"    URL:  {url}")
        print(f"    Type: {classification}")
        return prog

    def run_recon(self, domain: str, slug: Optional[str] = None,
                  skip_nuclei: bool = False, skip_ffuf: bool = False) -> dict:
        if slug:
            self.use_program(slug)
        if not self._program:
            self.init_program(domain)
        out_dir = self._program.recon_dir
        self._program.set("phase", "recon_in_progress")
        self._program.set("recon_domain", domain)
        self._program.set("recon_started", datetime.now().isoformat())
        result = self.recon.run_full(domain, out_dir, skip_nuclei, skip_ffuf)
        if result.get("error"):
            self._program.set("phase", "recon_failed")
            self._program.set("status", "recon_failed")
            self._program.set("recon_summary", result)
            self._program.set("recon_finished", datetime.now().isoformat())
            return result
        self._program.set("phase", "recon_done")
        self._program.set("recon_summary", result)
        self._program.set("recon_finished", datetime.now().isoformat())
        self._program.set("subdomains", {"total": result.get("subdomains", 0), "scanned": True, "file": "subs.txt"})
        self._program.set("alive", {"total": result.get("alive", 0), "scanned": True, "file": "alive.txt"})
        self._program.set("urls", {"total": result.get("urls", 0), "scanned": True, "file": "urls.txt"})
        self._program.set("status", "recon_done")
        return result

    def run_source_audit(self, path: str) -> str:
        ps = SCRIPTS_DIR / "source_audit.ps1"
        if not ps.exists():
            return "source_audit.ps1 not found"
        r = subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(ps),
                           "-Path", path], capture_output=True, text=True, timeout=300)
        return r.stdout + r.stderr

    def run_secrets_scan(self, path: str) -> str:
        ps = SCRIPTS_DIR / "secrets_scan.ps1"
        if not ps.exists():
            return "secrets_scan.ps1 not found"
        r = subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(ps),
                           "-Path", path], capture_output=True, text=True, timeout=300)
        return r.stdout + r.stderr

    def run_mobile_audit(self, apk_path: str) -> str:
        ps = SCRIPTS_DIR / "mobile_audit.ps1"
        if not ps.exists():
            return "mobile_audit.ps1 not found"
        r = subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(ps),
                           "-ApkPath", apk_path], capture_output=True, text=True, timeout=600)
        return r.stdout + r.stderr

    def run_dependency_audit(self, path: str) -> str:
        ps = SCRIPTS_DIR / "dependency_audit.ps1"
        if not ps.exists():
            return "dependency_audit.ps1 not found"
        r = subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(ps),
                           "-Path", path], capture_output=True, text=True, timeout=300)
        return r.stdout + r.stderr

    def list_programs(self) -> list[dict]:
        prog_dir = self.bb_dir / "programs"
        if not prog_dir.exists():
            return []
        programs = []
        for d in sorted(prog_dir.iterdir()):
            if d.is_dir():
                sf = d / "state.json"
                if sf.exists():
                    try:
                        data = json.loads(sf.read_text())
                        programs.append(data)
                    except Exception:
                        programs.append({"slug": d.name, "status": "unknown"})
                else:
                    programs.append({"slug": d.name, "status": "no state"})
        return programs

    def generate_report(self, slug: str) -> Optional[str]:
        self.use_program(slug)
        state = self._program
        summary = state.get("recon_summary", {})

        nuclei_findings = []
        nf = state.recon_dir / "nuclei.txt"
        if nf.exists():
            for line in nf.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    nuclei_findings.append(line)

        draft_banner = (
            "> [!WARNING]\n"
            "> DRAFT recon summary — NOT submittable. Every `TBD` below must be\n"
            "> replaced with validated evidence (raw HTTP, impact proof) and pass\n"
            "> `python bbcore/cli.py scope <slug> --check <asset>` + `--sweep`\n"
            "> before submission. See bbp-report-writer Mode 1.\n"
        )
        # Try to use template
        tmpl_path = TEMPLATES_DIR / "report.md"
        if tmpl_path.exists():
            tmpl = tmpl_path.read_text()
            tmpl = tmpl.replace("{{VULN_TYPE}}", "Multiple")
            tmpl = tmpl.replace("{{ENDPOINT}}", state.get("url", slug))
            tmpl = tmpl.replace("{{IMPACT}}", "TBD")
            tmpl = tmpl.replace("{{VULN_CLASS}}", state.get("classification", "web"))
            tmpl = tmpl.replace("{{ASSET_URL}}", state.get("url", ""))
            tmpl = tmpl.replace("{{COMPONENT}}", "Web Application")
            tmpl = tmpl.replace("{{VULNERABILITY_DESCRIPTION}}",
                                f"Recon completed on {state.get('recon_finished', 'N/A')}. "
                                f"Found {summary.get('alive', 0)} alive hosts and "
                                f"{len(nuclei_findings)} potential findings.")
            tmpl = tmpl.replace("{{IMPACT_POINT_1}}", "TBD after validation")
            tmpl = tmpl.replace("{{IMPACT_POINT_2}}", "TBD after validation")
            tmpl = tmpl.replace("{{BUSINESS_IMPACT_DESCRIPTION}}", "TBD")
            tmpl = tmpl.replace("{{STEP_1}}", "Run recon (see recon summary)")
            tmpl = tmpl.replace("{{STEP_2}}", "Validate nuclei findings")
            tmpl = tmpl.replace("{{STEP_3}}", "Exploit and capture evidence")
            tmpl = tmpl.replace("{{OBSERVATION}}", "See findings below")
            tmpl = tmpl.replace("{{HTTP_REQUEST}}", "TBD")
            tmpl = tmpl.replace("{{COMMAND_OR_REQUEST}}", "TBD")
            tmpl = tmpl.replace("{{REMEDIATION_SUGGESTION}}", "TBD after validation")
            tmpl = tmpl.replace("{{SCREENSHOT_DESCRIPTION}}", "Screenshot")
            tmpl = tmpl.replace("{{SCREENSHOT_PATH}}", "evidence/")
            tmpl = tmpl.replace("{{EVIDENCE_FILE}}", "HTTP dump")
            tmpl = tmpl.replace("{{EVIDENCE_PATH}}", "evidence/")
            lines = [tmpl]
        else:
            lines = [f"# Bug Bounty Report: {slug}", ""]

        # Append recon summary
        lines += [
            "",
            "## Recon Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Target | {state.get('url', 'N/A')} |",
            f"| Classification | {state.get('classification', 'N/A')} |",
            f"| Recon Date | {state.get('recon_finished', 'N/A')} |",
            f"| Subdomains | {summary.get('subdomains', 0)} |",
            f"| Alive Hosts | {summary.get('alive', 0)} |",
            f"| URLs Collected | {summary.get('urls', 0)} |",
            f"| WAF Detected | {summary.get('waf', 'None')} |",
            f"| Duration | {summary.get('elapsed_seconds', 0)}s |",
            "",
        ]
        if nuclei_findings:
            lines += ["## Nuclei Findings", "```"]
            lines += nuclei_findings
            lines += ["```", ""]
        lines += [
            "",
            "## Pre-submit Checklist (RTFS guard)",
            "",
            f"- [ ] `python bbcore/cli.py scope {slug} --sweep` returns CLEAN",
            "- [ ] Every finding asset checked with `scope --check <asset>` (exit 0)",
            "- [ ] All TBD replaced with replayable PoC + evidence in evidence/",
            "",
            "---",
            "",
            f"*DRAFT generated by BugBounty Orchestrator — do NOT submit as-is*",
        ]
        report = draft_banner + "\n" + "\n".join(lines)
        rp = state.reports_dir / "report.md"
        rp.write_text(report)
        print(f"[+] DRAFT report saved: {rp}")
        print("[!] Replace all TBD + run scope --sweep before submission.")
        return report

    def start_tor(self) -> bool:
        return self.proxy.start_tor()

    def stop_tor(self):
        self.proxy.stop_tor()

    def set_proxy_mode(self, mode: str):
        self.proxy.mode = mode

    def set_proxy_static(self, proxy_url: str):
        p = self.proxy._parse_proxy(proxy_url)
        if p:
            self.proxy.static_proxy = p
            self.proxy.mode = ProxyManager.MODE_STATIC

    def load_proxy_file(self, filepath: str):
        path = Path(filepath)
        if path.exists():
            self.proxy.proxy_list = []
            for line in path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    p = self.proxy._parse_proxy(line)
                    if p:
                        self.proxy.proxy_list.append(p)
            self.proxy.mode = ProxyManager.MODE_ROTATE
            print(f"[+] Loaded {len(self.proxy.proxy_list)} proxies from {filepath}")

    def status(self) -> dict:
        return {
            "proxy_mode": self.proxy.mode,
            "proxy_status": self.proxy.status_text(),
            "active_program": self._program.slug if self._program else None,
            "active_program_phase": self._program.get("phase", "none") if self._program else "none",
            "available_skills": len(self.skills.list_available()),
            "programs": len(self.list_programs()),
        }
