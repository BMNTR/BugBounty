# Local Resource Map — SecLists

## What lives where (verified)

```
C:\BugBounty\wordlists\SecLists\                      <- full repo clone
  Discovery\Web-Content\common.txt                    <- first-pass dirs
  Discovery\Web-Content\raft-large-directories.txt
  Discovery\Web-Content\api\                          <- API paths
  Discovery\DNS\                                      <- subdomain lists
  Discovery\DNS\namelist.txt
  Fuzzing\SQLi\  Fuzzing\XSS\  Fuzzing\Generic\
  Passwords\Common-Credentials\10-million-password-list-top-1000000.txt
  Passwords\Default-Credentials\
  Usernames\Names\names.txt
  Payloads\                                           <- misc payload sets
  Web-Shells\
```
Second clone also exists at `C:\BugBounty\tools\SecLists` (verify which is
fresher before relying on it).

WSL path: `/mnt/c/BugBounty/wordlists/SecLists`

## Fast lookups (exact verified files)

| Task | Path under wordlists\SecLists |
|---|---|
| Dir brute force pass 1 | `Discovery\Web-Content\common.txt` |
| Deep dir brute | `Discovery\Web-Content\raft-large-directories.txt` |
| API endpoint discovery | `Discovery\Web-Content\api\api-endpoints.txt` (check exact filename in api\) |
| Subdomain brute | `Discovery\DNS\namelist.txt` |
| Login brute small | `Passwords\Common-Credentials\top-passwords-shortlist.txt` (verify name) |
| Default creds | `Passwords\Default-Credentials\default-passwords.csv` (verify name) |

Always `ls` the directory first if a filename above lacks verification
note — SecLists renames files between versions.

## Usage recipes

```bash
# ffuf with jitter (WAF-aware):
wsl ffuf -u https://target.example.com/FUZZ \
  -w /mnt/c/BugBounty/wordlists/SecLists/Discovery/Web-Content/common.txt \
  -H "User-Agent: Mozilla/5.0" -p "0.1-0.5" -ac -o out.json -of json

# wfuzz alternative for parameter fuzzing:
wsl wfuzz -z file,/mnt/c/BugBounty/wordlists/SecLists/Fuzzing/parameter-names.txt ...
```

## When nothing is local

```bash
cd C:\BugBounty\wordlists\SecLists && git pull --ff-only
# Fresh clone: git clone --depth 1 https://github.com/danielmiessler/SecLists
```
