---
name: bbp-mobile-local-storage
description: Specialized skill for analyzing mobile application data storage, hunting for hardcoded secrets, and finding insecurely stored user data.
---

# Mobile Local Storage Skill

This skill provides methodologies for finding sensitive information that an application writes to the device's storage (internal or external).

## Workflow

### 1. Hardcoded Secrets (Static)
Before analyzing runtime storage, check the compiled APK for hardcoded secrets.
- **Strings Analysis:** Use `strings target.apk | grep -i "key\|token\|secret\|password\|api"` or use `apktool` and search inside `res/values/strings.xml`.
- **Finding:** Firebase API Keys, AWS Access Keys, hardcoded symmetric encryption keys, or API endpoint URLs.

### 2. Insecure SharedPreferences (Runtime)
SharedPreferences are XML files used to store small amounts of data (like user preferences or session state) in `/data/data/com.target.app/shared_prefs/`.
- **Exploitation:** Access the device via `adb shell` (requires root to read `/data/data/`).
- Read the `.xml` files. Look for unencrypted session tokens, PIN codes, passwords, or boolean flags (e.g., `<boolean name="isPremium" value="false" />`).
- **Modification:** If a boolean flag like `isPremium` exists, change it to `true` and restart the app to bypass paywalls.

### 3. Unencrypted SQLite Databases (Runtime)
Applications often store complex data (chat logs, user profiles, offline content) in SQLite databases located in `/data/data/com.target.app/databases/`.
- **Exploitation:** Pull the database file to your machine (`adb pull /data/data/com.target.app/databases/app.db`).
- Open it with a SQLite browser.
- Look for cleartext PII (Personally Identifiable Information), passwords, or tokens.
- **Remediation Check:** The app should use SQLCipher to encrypt the database. If it doesn't, it's a vulnerability (Insecure Data Storage).

### 4. External Storage (SD Card)
Data written to external storage (`/sdcard/` or `/storage/emulated/0/`) is readable by **any** application on the device that has the `READ_EXTERNAL_STORAGE` permission.
- **Exploitation:** Check if the app writes logs, downloads updates, or stores backups in external storage. If it does, a malicious app could steal this data or modify an update file before the target app installs it.

### 5. Logcat Leakage
Developers often leave debugging statements in production builds.
- **Exploitation:** Run `adb logcat | grep com.target.app`.
- Interact with the app (login, make a payment).
- Watch the logcat output. Look for HTTP request bodies, session tokens, passwords, or PII being printed to the system logs, which can be read by other apps (on older Android versions) or via physical access.
