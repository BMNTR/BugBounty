"""
Skill loader — maps program classification to BugBounty skills.
Reads SKILL.md files and generates AI agent context.
"""
from pathlib import Path
from typing import Optional

SKILL_DIR = Path(__file__).resolve().parent.parent / ".agents" / "skills"

CLASSIFICATION_MAP = {
    "web": {
        "primary": [
            "bbp-web-recon", "bbp-wpscan", "bbp-advanced-fuzzing",
            "bbp-auth-bypass", "bbp-waf-bypass",
        ],
        "vuln_specific": [
            "bbp-xss-hunter", "bbp-sqli-hunter", "bbp-ssrf-hunter",
            "bbp-osci-hunter", "bbp-xxe-hunter", "bbp-file-upload-lfi",
            "bbp-prototype-pollution", "bbp-cache-poisoning",
        ],
    },
    "api": {
        "primary": [
            "bbp-api-audit", "bbp-advanced-fuzzing",
            "bbp-auth-bypass", "bbp-graphql-audit",
        ],
    },
    "mobile": {
        "primary": [
            "bbp-android-apk-audit", "bbp-mobile-reverse-engine",
            "bbp-mobile-dynamic-analysis", "bbp-mobile-ipc-exploit",
            "bbp-mobile-local-storage",
        ],
    },
    "source": {
        "primary": [
            "bbp-source-code-audit", "code-security",
            "security-auditor", "variant-analysis",
        ],
    },
    "cloud": {
        "primary": [
            "bbp-cloud-security-audit", "bbp-subdomain-takeover",
        ],
    },
    "crypto": {
        "primary": [
            "bbp-crypto-audit", "bbp-evoting-crypto-audit",
        ],
    },
    "rust": {
        "primary": [
            "bbp-rust-security-review",
        ],
    },
    "windows": {
        "primary": [
            "windows-privilege-escalation", "windows-lateral-movement",
            "windows-av-evasion",
        ],
    },
    "binary": {
        "primary": [
            "binary-triage", "binary-analysis-patterns",
            "ctf-reverse", "protocol-reverse-engineering", "rev-frida",
        ],
    },
}

ALWAYS_LOAD = [
    "bbp-evidence-workbench", "bbp-report-writer", "bbp-duplicate-guard",
    "bbp-edoverflow-cheatsheet", "bbp-payloads-all-the-things",
    "bbp-hackerone-disclosures", "bbp-nuclei-templates",
    "bbp-cve-poc-db", "bbp-hacktricks", "bbp-seclists",
]


class SkillLoader:
    def __init__(self, bb_dir: Path = Path(r"C:\BugBounty")):
        self.skill_dir = bb_dir / ".agents" / "skills"

    def list_available(self) -> list[str]:
        if not self.skill_dir.exists():
            return []
        return sorted(d.name for d in self.skill_dir.iterdir() if d.is_dir())

    def load_skill(self, name: str) -> Optional[str]:
        """Read a skill's SKILL.md content."""
        skill_file = self.skill_dir / name / "SKILL.md"
        if skill_file.exists():
            return skill_file.read_text()
        return None

    def get_skill_context(self, name: str, max_lines: int = 50) -> Optional[str]:
        """Get first N lines of a skill for context."""
        content = self.load_skill(name)
        if not content:
            return None
        lines = content.splitlines()
        return "\n".join(lines[:max_lines])

    def classify_from_url(self, url: str) -> str:
        """Simple classification based on URL patterns."""
        url_lower = url.lower()
        if any(ext in url for ext in [".apk", "play.google", "apps.apple"]):
            return "mobile"
        if any(k in url_lower for k in ["api.", "/api/", "graphql", "swagger"]):
            return "api"
        if any(k in url_lower for k in [".s3.", "s3.amazonaws", "cloudfront"]):
            return "cloud"
        return "web"

    def get_skills_for_classification(self, classification: str) -> dict:
        """Get skill loadout for a target classification."""
        result = {
            "always_load": ALWAYS_LOAD,
            "primary": [],
            "vuln_specific": [],
        }
        mapping = CLASSIFICATION_MAP.get(classification, CLASSIFICATION_MAP["web"])
        result["primary"] = mapping.get("primary", [])
        result["vuln_specific"] = mapping.get("vuln_specific", [])
        return result

    def generate_agent_prompt(self, slug: str, classification: str,
                               findings: Optional[list[str]] = None) -> str:
        """Generate a comprehensive prompt for an AI agent."""
        skills = self.get_skills_for_classification(classification)
        lines = [
            f"# BugBounty Agent: {slug}",
            f"Classification: {classification}",
            "",
            "## Loaded Skills",
        ]
        for s in skills["always_load"] + skills["primary"] + skills["vuln_specific"]:
            ctx = self.get_skill_context(s, 30)
            if ctx:
                lines.append(f"\n### {s}")
                lines.append(ctx)

        if findings:
            lines.append("\n## Findings to Validate")
            for f in findings:
                lines.append(f"- {f}")

        return "\n".join(lines)
