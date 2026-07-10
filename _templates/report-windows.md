# [{{VULN_TYPE}}] in [{{EXECUTABLE_OR_SERVICE}}] leading to [{{IMPACT}}]

## Summary
- **Vulnerability Class:** {{VULN_CLASS}} (e.g., Local Privilege Escalation, DLL Hijacking, Buffer Overflow)
- **Target Binary:** {{BINARY_PATH_OR_NAME}}
- **Affected Component:** {{COMPONENT_OR_MODULE}}

## Description
{{VULNERABILITY_DESCRIPTION}}

## Impact / Risk
An attacker could:
- {{IMPACT_POINT_1}}
- {{IMPACT_POINT_2}}

{{BUSINESS_IMPACT_DESCRIPTION}}

## Prerequisites
- The attacker must have {{REQUIRED_PRIVILEGES}} privileges on the system.
- {{OTHER_CONDITIONS}}

## Steps to Reproduce
1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}
4. Observe: {{OBSERVATION}}

## Proof of Concept (PoC)

**Execution Flow / Code Path:**
```text
{{RELEVANT_ASSEMBLY_OR_CODE_FLOW}}
```

**Exploit Commands:**
```powershell
{{EXPLOIT_COMMANDS}}
```

## Remediation
{{REMEDIATION_SUGGESTION}}

## Supporting Material / Evidence
- **Procmon / Debugger Screenshot**: `{{SCREENSHOT_PATH}}`
- **Reverse Engineering Details (e.g. Ghidra/x64dbg excerpt)**: `{{EVIDENCE_PATH}}`
