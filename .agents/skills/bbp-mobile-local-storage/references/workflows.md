# Mobile Local Storage — Deep Workflows

Companion to SKILL.md. Storage location map, secret hunting, evidence.

## Step 1: Pull app data (rooted device / debuggable / run-as)

```bash
adb shell run-as com.target.app ls -la        # debuggable builds only
adb backup -noapk com.target.app              # allowBackup=true builds
# Emulator with root:
adb root && adb shell "ls -R /data/data/com.target.app/" > listing.txt
adb pull /data/data/com.target.app ./appdata/
```

## Step 2: Storage locations cheat sheet

```text
shared_prefs/*.xml          plaintext key-value (tokens, flags, PII)
databases/*.db              SQLite; check PRAGMA cipher? (SQLCipher or raw)
files/ cache/               downloaded docs, cached responses, logs
external_storage            Android/data/<pkg>/ on SD = world-readable
keychain/keystore           keys themselves (should NEVER hold data secrets)
Webview: app_webview/       LocalStorage/ Cookies (encrypted w/ Chrome v80+)
```

## Step 3: Secret hunt greps

```bash
grep -rEi "(api[_-]?key|secret|token|bearer|password|jwt)" appdata/ | head -30
# SQLite dump + search:
sqlite3 databases/app.db ".tables"
for t in $(sqlite3 databases/app.db ".tables"); do
  sqlite3 databases/app.db "SELECT * FROM $t LIMIT 5;" >> dump_all.txt
done
grep -iE "(email|ssn|token)" dump_all.txt
```

## Step 4: Classify findings

```text
CRITICAL : third-party API secrets, master crypto keys, admin tokens
HIGH     : user session tokens persistent after logout, PII in plaintext db
MEDIUM   : sensitive cache without encryption at rest
INFO     : device-only prefs (theme, flags) -> not a finding
```

## Step 5: Logout persistence test (high-yield)

```bash
1. Login, snapshot shared_prefs hash (Get-FileHash).
2. Logout in app. Re-snapshot.
3. Token still present server-side valid? curl an authed endpoint with it.
Valid-after-logout = session invalidation gap (server-side finding too).
```

## False-positive elimination

1. Encrypted blobs are not "plaintext secrets" until you prove decryption
   path (hook Cipher.doFinal to confirm they ARE decrypted for use).
2. Test keys in debug builds != prod finding — verify release build.
3. Confirm the secret is actually SENSITIVE (try it against the API it
   belongs to, using your own account context).

Report via bbp-android-apk-audit template pattern with storage-path table.
