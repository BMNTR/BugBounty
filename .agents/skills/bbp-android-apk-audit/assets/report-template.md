# Android Finding — Report Template

```markdown
## Android <exported activity/provider/deep link>: <summary>

**Severity**: High/Medium (CVSS per reachability)
**Asset**: com.target.app (Play Store build vX, sha256 noted)
**Type**: CWE-926 Improper Export of Android Application Components

### Manifest evidence

```xml
<activity android:name=".InternalAdminActivity"
          android:exported="true"/>   <!-- no permission attribute -->
```

### Dynamic proof (own rooted/test device)

```
$ adb shell am start -n com.target.app/.InternalAdminActivity \
    --ez is_admin true
-> Activity renders admin dashboard; screenshot evidence/adb_admin.png
```

No confirmation dialog or permission gate observed.

### Impact

Any installed app on the device can launch this component and drive
privileged flows without user interaction beyond one Intent.

### Remediation

1. Set exported=false unless component is a documented entry point.
2. Where export required: enforce signature-level custom permission +
   runtime validation of caller identity.
3. Add CI check failing on new exported components lacking protection.
```
