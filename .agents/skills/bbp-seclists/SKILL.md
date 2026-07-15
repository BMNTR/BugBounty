---
name: bbp-seclists
description: Definitive guide for using danielmiessler/SecLists. Use this to determine the exact wordlist path to use for fuzzing directories, parameters, APIs, or passwords.
---

# SecLists Guide & Wordlist Selection

When using `ffuf`, `arjun`, or `gobuster`, selecting the right wordlist from SecLists is critical. Assuming SecLists is installed at `/usr/share/seclists/` or `~/SecLists/`.

## 1. Content Discovery (Files & Directories)
- **General Fast Scan**: `Discovery/Web-Content/raft-small-words.txt`
- **Exhaustive Scan**: `Discovery/Web-Content/raft-large-directories.txt`
- **Files Only**: `Discovery/Web-Content/raft-large-files.txt`
- **API Endpoints**: `Discovery/Web-Content/api/api-endpoints.txt`
- **GraphQL**: `Discovery/Web-Content/graphql.txt`
- **IIS/ASP.NET**: `Discovery/Web-Content/IIS.txt`

## 2. Parameter Discovery
- **General Parameters**: `Discovery/Web-Content/burp-parameter-names.txt`
- **Short/Common**: `Discovery/Web-Content/params.txt`

## 3. Subdomain Enumeration
- **Fast / Top Subdomains**: `Discovery/DNS/subdomains-top1million-5000.txt`
- **Thorough**: `Discovery/DNS/subdomains-top1million-110000.txt`
- **Asset Discovery (Permutations)**: `Discovery/DNS/bitquark-subdomains-top100000.txt`

## 4. Payloads & Bypasses
- **LFI / Path Traversal**: `Fuzzing/LFI/LFI-gracefulsecurity-linux.txt`
- **SQLi**: `Fuzzing/SQLi/Generic-SQLi.txt`
- **XSS**: `Fuzzing/XSS/XSS-Bypass-Strings-BruteForcing.txt`
- **SSRF**: `Fuzzing/SSRF/SSRF-Local-IPs.txt`

Always tailor the wordlist to the target technology. Do not use a generic large list if you know the target is a Spring Boot API.
