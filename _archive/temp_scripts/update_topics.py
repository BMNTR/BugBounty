import re

with open('C:/BugBounty/bugbounty_tutorial.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_topics = """const topics = [
  { id: 'sqli', title: 'SQL Injection', labsCount: 1, solvedCount: 0 },
  { id: 'xss', title: 'Cross-Site Scripting', labsCount: 1, solvedCount: 0 },
  { id: 'csrf', title: 'CSRF', labsCount: 1, solvedCount: 0 },
  { id: 'os-command', title: 'OS Command Injection', labsCount: 1, solvedCount: 0 },
  { id: 'ssrf', title: 'SSRF', labsCount: 1, solvedCount: 0 },
  { id: 'auth', title: 'Authentication Bypass', labsCount: 1, solvedCount: 0 }
];"""

new_topics = """const topics = [
  { id: 'sqli', title: 'SQL Injection', labsCount: 1, solvedCount: 0 },
  { id: 'xss', title: 'Cross-Site Scripting', labsCount: 1, solvedCount: 0 },
  { id: 'csrf', title: 'CSRF', labsCount: 1, solvedCount: 0 },
  { id: 'os-command', title: 'OS Command Injection', labsCount: 1, solvedCount: 0 },
  { id: 'ssrf', title: 'SSRF', labsCount: 1, solvedCount: 0 },
  { id: 'auth', title: 'Authentication Bypass', labsCount: 1, solvedCount: 0 },
  { id: 'path-traversal', title: 'Path Traversal', labsCount: 1, solvedCount: 0 },
  { id: 'idor', title: 'IDOR', labsCount: 1, solvedCount: 0 },
  { id: 'info-disc', title: 'Info Disclosure', labsCount: 1, solvedCount: 0 },
  { id: 'file-upload', title: 'File Upload', labsCount: 1, solvedCount: 0 }
];"""

html = html.replace(old_topics, new_topics)

with open('C:/BugBounty/bugbounty_tutorial.html', 'w', encoding='utf-8') as f:
    f.write(html)