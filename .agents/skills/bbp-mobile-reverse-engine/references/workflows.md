# Mobile Reverse Engineering — Deep Workflows

Companion to SKILL.md. Obfuscation handling, native analysis, patching.

## Step 1: Static pipeline

```bash
apktool d app.apk -o dec/                 # resources + smali
jadx -d src/ --show-bad-code app.apk      # readable java (imperfect)
# If jadx output garbled: try --no-inline-errors, or cfr/procyon on dex2jar
d2j-dex2jar.sh app.apk && cfr app-dex2jar.jar --outputdir cfr_out/
```

## Step 2: Obfuscation triage (ProGuard/R8)

```text
Signs: classes a.b.c, methods a()b().
- mapping.txt shipped in APK? -> instant deobfuscation map
- No mapping: rename iteratively in jadx (R key), follow string constants,
  entry points (Manifest) anchor the graph.
- String encryption layers: locate decryptor method, call it via frida
  at runtime instead of reversing statically.
```

## Step 3: Key logic location heuristics

```bash
grep -rEn "(license|premium|isPro|verify|signature|checkLic)" src/ | head
grep -rEn "https?://[a-z0-9.-]+" src/ | grep -v schemas | sort -u   # endpoints
# Crypto usage:
grep -rEn "Cipher\.getInstance|SecretKeySpec|Mac\.getInstance" src/
# Weak patterns: ECB default, static keys, AES/ECB/PKCS5Padding.
```

## Step 4: Native library pointers (Ghidra)

```text
lib/*/armeabi-v7a/*.so -> load into Ghidra:
- JNI exports Java_com_pkg_Class_method = bridge points
- Strings window first; OOB strings often hold flags/keys
- Anti-debug checks: ptrace attach self, /proc/self/status TracerPid scan
  -> note as hardening, not vuln.
```

## Step 5: Runtime-assisted reversal (frida)

```bash
# Trace a class' all methods without static knowledge:
frida -U -f com.target.app -l trace.js
// trace.js
Java.perform(function(){
  var C = Java.use('com.target.app.SecretManager');
  C.verify.implementation = function(t){
    console.log('[+] verify called token='+t);
    return this.verify(t);
  };
});
```
Runtime beats static for encrypted strings and integrity gates.

## Step 6: Patching smali (authorized lab only)

```bash
# Flip boolean return:
#   const/4 v0, 0x0  ->  const/4 v0, 0x1
apktool b dec/ -o patched.apk
uber-apk-signer -a patched.apk     # re-sign for install
adb install patched.apk
```

Only for demonstrating license/authz flaws on YOUR test build.

## False-positive elimination

1. Client-side license checks alone are usually NOT bounty-worthy —
   find the SERVER enforcement gap instead (API trusts client verdict).
2. Debug symbols present != vulnerability by itself.
3. Verify findings against the exact Play Store build version.
