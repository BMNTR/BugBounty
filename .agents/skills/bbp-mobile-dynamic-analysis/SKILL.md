---
name: bbp-mobile-dynamic-analysis
description: Specialized skill for runtime manipulation, memory instrumentation, bypassing SSL pinning, and hooking methods using Frida and Objection.
---

# Mobile Dynamic Analysis Skill

This skill provides methodologies for manipulating mobile applications at runtime (while they are executing).

## Workflow

### 1. Environment Setup
- Ensure the device (physical or emulator like Genymotion/Corellium) is rooted.
- Run `frida-server` on the device (`adb push frida-server /data/local/tmp/`, `chmod +x`, `./frida-server &`).
- Forward ports: `adb forward tcp:27042 tcp:27042`.

### 2. Bypassing Security Controls (SSL Pinning & Root Detection)
Applications often refuse to run on rooted devices or refuse to connect through Burp Suite (SSL Pinning).
- **Using Objection:** 
  - `objection -g com.target.app explore`
  - Run `android sslpinning disable` to bypass certificate pinning.
  - Run `android root disable` to bypass common root detection checks.
- **Using Frida Scripts:** If Objection fails, use specialized Frida scripts from `codeshare.frida.re` (e.g., `frida -U -f com.target.app -l ssl-bypass.js --no-pause`).

### 3. Hooking & Method Tracing
Intercept and modify function calls and return values at runtime without needing to decompile/recompile the app.
- **Tracing Classes/Methods in Objection:**
  - `android hooking watch class com.target.app.AuthManager` to see when authentication methods are called.
  - `android hooking set return_value com.target.app.AuthManager.isAdmin true` to instantly bypass an admin check in memory.
- **Custom Frida Scripts (Javascript):** Write custom scripts to hook specific functions (e.g., cryptographic encryption functions) to dump the plaintext data before it gets encrypted.

### 4. Memory Dumping & Inspection
- **Keystore Extraction:** Dump the Android Keystore to extract certificates or cryptographic keys stored securely.
- **Heap Search:** Search the application's live memory heap for sensitive strings (e.g., passwords, session tokens) that are currently loaded into variables. `objection: memory search "password"`.
- **Clipboard Monitoring:** Monitor if the application insecurely copies sensitive data (like OTPs or passwords) to the system clipboard.
