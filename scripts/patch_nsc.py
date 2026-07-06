"""
Patch DANA APK network_security_config at zip level using aapt2.
No full rebuild needed — only replaces one binary XML file.
"""
import zipfile, shutil, subprocess, os, sys

AAPT2 = r'C:\BugBounty\tools\build-tools\android-14\aapt2.exe'
ZIPALIGN = r'C:\BugBounty\tools\build-tools\android-14\zipalign.exe'
APKSIGNER = r'C:\BugBounty\tools\build-tools\android-14\apksigner.bat'
KEYSTORE = r'C:\BugBounty\my-release-key.keystore'
ORIGINAL_APK = r'C:\BugBounty\target-app.apk'
OUTPUT_APK = r'C:\BugBounty\target-patched.apk'
TEMP_DIR = r'C:\BugBounty\nsc_temp'
NSC_ENTRY_IN_APK = 'res/xml/2132213778.xml'

os.makedirs(TEMP_DIR, exist_ok=True)

# Step 1: Write the modified NSC XML
nsc_content = """<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />
            <certificates src="system" />
        </trust-anchors>
    </debug-overrides>
    <domain-config>
        <domain includeSubdomains="true">api.target.com</domain>
        <domain includeSubdomains="true">staging.target.com</domain>
        <trust-anchors>
            <certificates overridePins="true" src="user" />
            <certificates overridePins="true" src="system" />
        </trust-anchors>
    </domain-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">localhost</domain>
    </domain-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
            <certificates overridePins="true" src="user" />
        </trust-anchors>
    </base-config>
</network-security-config>
"""

nsc_xml_path = os.path.join(TEMP_DIR, '2132213778.xml')
with open(nsc_xml_path, 'w', encoding='utf-8') as f:
    f.write(nsc_content)
print(f'[+] Written modified NSC XML to {nsc_xml_path}')

# Step 2: Compile with aapt2
print('[+] Compiling with aapt2...')
r = subprocess.run([AAPT2, 'compile', '--legacy', nsc_xml_path, '-o', TEMP_DIR + '\\'],
                   capture_output=True, text=True)
print('stdout:', r.stdout)
print('stderr:', r.stderr)

flat_files = [f for f in os.listdir(TEMP_DIR) if f.endswith('.flat')]
print(f'[+] Flat files: {flat_files}')

if not flat_files:
    print('[-] aapt2 compile failed, trying direct binary XML from decompiled path')
    # Fallback: use the plain XML as-is (won't work on device but good for testing)
    compiled_xml = nsc_xml_path
else:
    # Extract binary XML from flat file (flat file = length-prefixed binary xml)
    flat_path = os.path.join(TEMP_DIR, flat_files[0])
    with open(flat_path, 'rb') as f:
        flat_data = f.read()
    # flat format: 4 bytes header type, 4 bytes length, then the binary XML
    # Skip first 8 bytes (header) to get the compiled binary XML
    binary_xml = flat_data[8:]
    compiled_xml_path = os.path.join(TEMP_DIR, 'nsc_compiled.bin')
    with open(compiled_xml_path, 'wb') as f:
        f.write(binary_xml)
    print(f'[+] Extracted binary XML ({len(binary_xml)} bytes) to {compiled_xml_path}')
    compiled_xml = compiled_xml_path

# Step 3: Copy original APK and replace the NSC file
temp_apk = os.path.join(TEMP_DIR, 'dana_patching.apk')
shutil.copy(ORIGINAL_APK, temp_apk)
print(f'[+] Copied original APK to {temp_apk}')

# Remove old signatures from the copy
clean_apk = os.path.join(TEMP_DIR, 'dana_clean.apk')
with zipfile.ZipFile(temp_apk, 'r') as zin:
    with zipfile.ZipFile(clean_apk, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename.startswith('META-INF/'):
                continue
            if item.filename == NSC_ENTRY_IN_APK:
                print(f'[+] Replacing {NSC_ENTRY_IN_APK} with patched version')
                with open(compiled_xml, 'rb') as f:
                    zout.writestr(item, f.read())
            else:
                zout.writestr(item, zin.read(item.filename))

print(f'[+] Created patched APK (no signatures): {clean_apk}')

# Step 4: Zipalign
aligned_apk = os.path.join(TEMP_DIR, 'dana_aligned.apk')
r = subprocess.run([ZIPALIGN, '-p', '-f', '-v', '4', clean_apk, aligned_apk],
                   capture_output=True, text=True)
print('[+] Zipalign done:', 'OK' if r.returncode == 0 else r.stderr[-200:])

# Step 5: Sign
r = subprocess.run([APKSIGNER, 'sign',
    '--ks', KEYSTORE, '--ks-pass', 'pass:123456', '--key-pass', 'pass:123456',
    '--v1-signing-enabled', 'true', '--v2-signing-enabled', 'true',
    aligned_apk], capture_output=True, text=True)
print('[+] Signing done:', 'OK' if r.returncode == 0 else r.stderr[-200:])

shutil.copy(aligned_apk, OUTPUT_APK)
print(f'\n[✓] Done! Patched APK saved to: {OUTPUT_APK}')
print(f'[✓] Size: {os.path.getsize(OUTPUT_APK) / 1024 / 1024:.1f} MB')
