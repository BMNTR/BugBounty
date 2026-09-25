---
name: opire-bounty-hunter
description: Autonomous Open Source Bounty Orchestrator for Opire, Algora, and GitHub Bounties. Call when given an Opire, Algora, or GitHub issue URL.
---

# Opire Bounty Hunter Orchestrator

Autonomous end-to-end open-source bounty solver. Invoked via `/opire <url>` or when an Opire / Algora / GitHub issue URL is provided.

---

## 🎯 Workflow Phases

### Phase 1 — Autonomous Information Gathering
1. Parse the provided URL:
   - **Opire URL** (`https://app.opire.dev/...`)
   - **Algora URL** (`https://console.algora.io/...`)
   - **GitHub Issue URL** (`https://github.com/<owner>/<repo>/issues/<id>`)
2. Use `read_url_content` or `curl` to fetch the issue details:
   - Target Repository URL (`https://github.com/<owner>/<repo>.git`)
   - Issue Title & Detailed Problem Statement
   - Acceptance Criteria & Requirements
   - Bounty Reward Amount
3. Generate `<bounty-slug>` (e.g., `owner-repo-issue-123`).

---

### Phase 2 — Workspace Initialization
1. Pre-create workspace:
   ```powershell
   New-Item -ItemType Directory -Force -Path "C:\OpireBounty\bounties\<bounty-slug>\{src,patch,notes,temp}"
   ```
2. Clone repository:
   ```powershell
   git clone https://github.com/<owner>/<repo>.git "C:\OpireBounty\bounties\<bounty-slug>\src"
   ```
3. Save issue specification to `C:\OpireBounty\bounties\<bounty-slug>\notes\issue_spec.md`.

---

### Phase 3 — Tech Stack & Dynamic Skill Routing
1. Inspect `src/` to determine language and framework:
   - `package.json` → Node.js / React / Next.js / TypeScript
   - `pyproject.toml` / `requirements.txt` → Python
   - `Cargo.toml` → Rust
   - `go.mod` → Go
   - `pom.xml` / `build.gradle` → Java / Kotlin
2. Match and load relevant skills from `C:\BugBounty\.agents\skills\`:
   - **General Code Fix & Audit** → `bbp-source-code-audit`, `code-security`, `ghost-scan-code`
   - **Frontend & UI Issues** → `design-taste-frontend`, `minimalist-ui`, `image-to-code`
   - **API / Logic Issues** → `bbp-api-audit`, `bbp-business-logic`
   - **Rust Projects** → `bbp-rust-security-review`
3. **External Skill Acquisition Fallback**:
   - If the project uses a specialized framework/stack not covered by local skills, search the web or GitHub for best-practice patterns or community skills, adapt them, and save to `C:\OpireBounty\.agents\skills\`.

---

### Phase 4 — Execution & Local Verification
1. Locate the bug/feature area in `src/`.
2. Apply code modifications to resolve the issue.
3. Run local verification & unit tests in `src/`:
   ```powershell
   # Node.js: npm test / yarn test / pnpm test
   # Python: pytest
   # Rust: cargo test
   # Go: go test ./...
   ```
4. Iterate until 100% of unit tests PASS.

---

### Phase 5 — Patch Generation & Pull Request Draft
1. Export git patch:
   ```powershell
   cd "C:\OpireBounty\bounties\<bounty-slug>\src"
   git diff > "..\patch\fix.patch"
   ```
2. Fill PR template (`C:\OpireBounty\_templates\pr_template.md`) and save to:
   `C:\OpireBounty\bounties\<bounty-slug>\notes\pr_description.md`
3. Present the solution, diff summary, and git push/PR submission commands to the user.

---

## 🚀 Example Invocation:

```
/opire https://app.opire.dev/bounty/12345
/opire https://github.com/facebook/react/issues/9999
```
