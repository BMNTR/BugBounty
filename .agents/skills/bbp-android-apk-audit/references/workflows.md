# Android APK Audit — Deep Workflows

Companion to SKILL.md. Manifest triage, deep links, storage, network config.

## Step 1: Decode and inventory

```bash
apktool d app.apk -o app_decoded
jadx -d app_src app.apk            # java sources for grep
# Manifest red flags (grep AndroidManifest.xml):
grep -E "exported|allowBackup|debuggable|cleartextTrafficPermitted" \
  app_decoded/AndroidManifest.xml
```

```text
[!] android:exported="true" without permission   -> IPC surface
[!] android:debuggable="true"                    -> prod build debug
[!] allowBackup="true"                           -> adb backup data theft
[!] usesCleartextTraffic / no network_security_config -> MITM exposure
[!] exported ContentProvider w/o grantUriPermissions control
```

## Step 2: Deep link testing

```bash
# Extract from manifest: <data android:scheme host pathPrefix>
adb shell am start -W -a android.intent.action.VIEW \
  -d "appscheme://app/page?user_id=102"
# Test: unauthenticated access to authed screens, IDOR params, XSS via
# webview URL params, intent redirection extras.
```

## Step 3: WebView configuration review

```
grep -E "setJavaScriptEnabled|setAllowFileAccess|addJavascriptInterface|
        setAllowUniversalAccessFromFiles|onReceivedSslError" -r app_src/
```
Dangerous combos: JS enabled + file access + untrusted input into
loadUrl = LFI/XSS bridge; addJavascriptInterface exposes @JavascriptInterface
methods to page JS.

## Step 4: Local storage secrets sweep

```bash
adb shell run-as <pkg> ls databases/ shared_prefs/ files/
adb pull ...
grep -rEi "(api[_-]?key|secret|token|password)" shared_prefs/
# Check: tokens in SharedPreferences plaintext, SQLite unencrypted PII,
# logs leaking (logcat | grep pkg).
```

## Step 5: Network security config & pinning posture

```xml
<!-- res/xml/network_security_config.xml -->
<trust-anchors><certificates src="user"/>  <!-- user CA accepted = MITM ok -->
<domain includeSubdomains="false">api.target.com</domain> <!-- gaps? -->
```

## Step 6: Exported component quick tests

```bash
adb shell am start -n com.pkg/.ExportedActivity --es cmd "id"
adb shell am broadcast -a com.pkg.INTERNAL_EVENT --es action "verify"
adb shell content query --uri content://com.pkg.provider/items
# Any state change/data return without permission = finding.
```

## False-positive elimination

1. exported=true may carry runtime permission checks — verify by behavior.
2. Backup flag needs device consent flow; document realistically.
3. Third-party SDK findings often out-of-scope; check program policy.
