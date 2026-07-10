---
name: bbp-android-apk-audit
description: Audit authorized Android app bug bounty assets. Use for in-scope Android Play Store/APK assets to review manifests, exported components, deep links, local storage, network config, WebViews, intent handling, and safe local PoCs without rooting, MITM, DoS, or testing other users.
---

# BBP Android APK Audit

## Setup

1. Work under `C:\BugBounty\programs\<program>`.
2. Download the official APK only from the in-scope source.
3. Record:
   - app version
   - versionCode
   - package name
   - APK SHA256
   - download URL
4. Decode with apktool or inspect source if available.

## First Checks

Review:

- exported activities/services/receivers/providers
- intent filters and deep links
- custom permissions and protection levels
- WebView JavaScript bridges
- file/content providers
- local sensitive storage
- backup/debuggable flags
- network security config
- hardcoded secrets that apply to in-scope assets

## Exported Component Validation

For exported components:

1. Identify component name and accepted actions/extras.
2. Trace whether the action changes security state, account state, payment state, VPN state, or sensitive data exposure.
3. Use only local ADB or a minimal local test app.
4. Do not interact with other users, production abuse flows, spam, DoS, or private data.

ADB example pattern:

```bash
adb shell am start -W -n <package>/<activity> -a <action> --es <key> <value>
```

## Proof Standard

Strong evidence includes:

- screenshot or video of before/after state
- exact ADB command
- manifest excerpt proving export status
- source/decompiled path showing missing authorization
- APK SHA256 and version metadata

If dynamic testing was not done, state:

```text
Validated through release APK manifest and source review only. Runtime exploit video was not captured.
```

## Report Safety

Do not claim account takeover, RCE, data leak, or server compromise unless the PoC proves it.

For local Android attacks, choose impact based on proven behavior:

- forced disconnect/state change: operational disruption or unauthorized account/resource manipulation
- sensitive local data readable: sensitive data exposure
- arbitrary file access: arbitrary file read/write
- WebView JS bridge abuse: depends on proven sink
