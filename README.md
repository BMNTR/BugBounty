# BugBounty

Bug bounty workflow automation — agent-assisted recon, scanning, source audit, mobile analysis, and report writing.

## Prerequisites

Install these first:

| Tool | Minimum | Check |
|------|---------|-------|
| **Go** | 1.21+ | `go version` |
| **Python** | 3.11+ | `python --version` |
| **Node.js** | 18+ | `node -v` |
| **Rust** | 1.70+ | `rustc --version` |
| **Java JDK** | 17 | `java -version` |
| **Git** | any | `git --version` |

Windows only: install [Go](https://go.dev/dl/), [Python](https://www.python.org/downloads/), [Node](https://nodejs.org/), [Rust](https://rustup.rs/), [Java](https://adoptium.net/), [Git](https://git-scm.com/).

## Quick Setup

Clone and install:

```powershell
git clone <your-repo-url> C:\BugBounty
cd C:\BugBounty
scripts\update_all_tools.ps1
```

This installs:
- **Subdomain**: subfinder, amass, assetfinder
- **URL/Spider**: gau, waybackurls, katana, hakrawler
- **Probe**: httpx, dnsx
- **Fuzz**: ffuf
- **Scan**: nuclei
- **Secrets**: gitleaks, trufflehog
- **SCA**: trivy, grype, osv-scanner, cargo-audit
- **Code**: semgrep, codeql
- **Mobile**: apktool, jadx, frida, objection
- **Other**: jq, yq, fd, fzf, bat, delta

## Wordlists

```powershell
cd wordlists
git clone https://github.com/danielmiessler/SecLists
git clone https://github.com/swisskyrepo/PayloadsAllTheThings
```

## Agent Setup (opencode)

This repo is designed to work with [opencode](https://opencode.ai) CLI.

```powershell
# install opencode
npm install -g @anthropic-ai/claude-code
# or if using opencode:
npm install -g opencode-cli
```

Then open the repo:

```powershell
cd C:\BugBounty
opencode
# or: claude
```

The agent reads `AGENTS.md` and `SKILL.md` for full workflow instructions.

## Workflow

```
/program <program-url> [name]
```

This triggers:
1. Recon (subs → alive → URLs → nuclei)
2. Skill loading (web/API/mobile/source/cloud)
3. Deep testing based on findings
4. Report generation

```mermaid
flowchart TD
    %% Styling definitions
    classDef startend fill:#2ecc71,stroke:#27ae60,stroke-width:2px,color:#fff,font-weight:bold
    classDef phase fill:#ecf0f1,stroke:#bdc3c7,stroke-width:2px,color:#2c3e50,font-weight:bold
    classDef action fill:#3498db,stroke:#2980b9,stroke-width:1px,color:#fff
    classDef tool fill:#9b59b6,stroke:#8e44ad,stroke-width:1px,color:#fff
    classDef storage fill:#f1c40f,stroke:#f39c12,stroke-width:2px,color:#000

    %% Main flow
    Start(["🚀 Start: /program <url>"]):::startend --> Phase1

    %% Phase 1: Recon
    subgraph Phase1 [Phase 1: Autonomous Recon]
        direction TB
        R1["Passive Recon<br>(Google/GitHub Dorking, Shodan)"]:::action --> R2["Subdomain Enum<br>(subfinder, assetfinder)"]:::action
        R2 --> R3["DNS & Port Scan<br>(dnsx, naabu)"]:::action
        R3 --> R4["HTTP Probing<br>(httpx)"]:::action
        R4 --> R5["URL History & Crawling<br>(gau, waybackurls, katana)"]:::action
        R5 --> R6["Vuln Scanning<br>(nuclei, dalfox)"]:::action
        
        R6 --> DB1[("📁 programs/&lt;slug&gt;/recon/")]:::storage
        R6 --> DB2[("📁 programs/&lt;slug&gt;/evidence/")]:::storage
    end

    Phase1 --> Phase2

    %% Phase 2: Classification
    subgraph Phase2 [Phase 2: Target Classification & Skill Loading]
        direction TB
        C1{"Target Type?"}:::phase
        C1 -- Web --> T1["Load bbp-web-recon"]:::tool
        C1 -- API --> T2["Load bbp-api-audit"]:::tool
        C1 -- Mobile --> T3["Load bbp-android-apk-audit"]:::tool
        C1 -- Source --> T4["Load bbp-source-code-audit"]:::tool
        
        T1 & T2 & T3 & T4 --> C2["Load Base Skills<br>(triage, evidence, report, duplicate)"]:::tool
    end

    Phase2 --> Phase3

    %% Phase 3: Execution
    subgraph Phase3 [Phase 3: Execution & Validation]
        direction TB
        E1["Run Specialized Scripts<br>(recon.ps1, etc.)"]:::action --> E2["Deep Manual Testing & Validation"]:::action
        E2 --> E3["Exploitation & PoC Creation"]:::action
        E3 --> DB3[("📝 programs/&lt;slug&gt;/findings.md")]:::storage
    end

    Phase3 --> Phase4

    %% Phase 4: Reporting
    subgraph Phase4 [Phase 4: Report Generation]
        direction TB
        Rep1["Load bbp-report-writer"]:::tool --> Rep2["Generate Report"]:::action
        Rep2 --> Rep3["Attach Evidence<br>(Screenshots, PoC)"]:::action
        Rep3 --> DB4[("📄 programs/&lt;slug&gt;/final_report.md")]:::storage
    end

    Phase4 --> Finish(["🎉 Report Submitted!"]):::startend
```

## Structure

```
C:\BugBounty\
├── scripts\           # workflow automation scripts
├── .agents\skills\    # security audit skills & skill packs
├── _templates\        # report templates
├── programs\          # per-target workspace
│   └── <slug>\
│       ├── recon\     # raw recon output (gitignored)
│       ├── evidence\  # PoCs, screenshots (gitignored)
│       └── state.json
├── tools\             # binaries (gitignored, auto-installed)
├── wordlists\         # SecLists, PayloadsAllTheThings (gitignored)
├── recon\             # global recon (gitignored)
├── AGENTS.md          # agent workflow rules
├── SKILL.md           # command encyclopedia
└── README.md
```

## Private Programs

Login to your target platform (HackerOne, YesWeHack, Bugcrowd, etc.) in your browser, then:

```powershell
scripts\setup-cookies.ps1
```

Saves `cookies.txt` (gitignored). The agent auto-detects and uses it.
