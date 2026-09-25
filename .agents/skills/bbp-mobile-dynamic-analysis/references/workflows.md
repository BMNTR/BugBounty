# Mobile Dynamic Analysis — Deep Workflows

Companion to SKILL.md. Frida deployment, objection recipes, pinning bypass.

## Step 1: Environment bring-up

```bash
adb devices                                   # device/emulator ready
# Frida server matching architecture + version:
adb push frida-server-android-arm64 /data/local/tmp/fs
adb shell chmod +x /data/local/tmp/fs
adb shell su -c '/data/local/tmp/fs &'        # rooted device/emulator
frida-ps -U | head                             # verify visibility
```

## Step 2: Objection quick wins

```bash
objection -g com.target.app explore
# Inside prompt:
android sslpinning disable        # okhttp/trustmanager/conscrypt hooks
android root disable              # bypass root detection prompts
android hooking list activities
android hooking watch class com.target.app.AuthManager
android hooking watch class_method com.target.app.AuthManager.login \
  --dump-args --dump-return
```

## Step 3: SSL pinning bypass ladder (when objection misses)

```text
1. objection generic hook (covers most okhttp3 + conscrypt)
2. Custom frida: hook javax.net.ssl.X509TrustManager.checkServerTrusted
   return silently; plus okhttp3.CertificatePinner.check throw-skip
3. Network security config repack: add user CA trust anchors, re-sign
4. For native pinning (BoringSSL): frida-trace libssl.so SSL_read/write
```

Then proxy through Burp (user CA installed as system cert on emulator API<28+
or magisk module for newer).

## Step 4: Runtime inspection targets

```text
- Auth tokens in memory: strings on heap dump OR frida memory scan
- Encrypted prefs: hook javax.crypto.Cipher.doFinal --dump-args => plaintext
- Root/integrity checks: hook returning false to bypass, then observe
  WHICH SERVER calls fail -> if none, check is cosmetic only
- Clipboard/keyboard caches, screenshots of sensitive screens flag
```

## Step 5: Evidence discipline

```text
- Record device model, Android version, build fingerprint
- Script every hook used; save .js files next to evidence
- Screenshots with visible package name + timestamp bar
- Never hook/test against other users' accounts on shared backends
```

## False-positive elimination

1. Pinning bypass success must show REAL decrypted traffic in Burp.
2. Root-detection bypass is not a finding unless paired with server-side
   consequence (e.g., banking action permitted).
3. Verify hooks actually attached (frida logs), not silently failing.
