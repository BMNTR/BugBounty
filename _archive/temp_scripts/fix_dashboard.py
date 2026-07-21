import re

with open('C:/BugBounty/bugbounty_tutorial.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove the old duplicate dashboard
old_dashboard = """    <!-- DASHBOARD -->
    <div class="section page-active" id="home">
      <div class="home-hero" style="text-align: left; padding: 40px 0;">
        <h2><span style="color:var(--text)">All</span> <span>Topics</span></h2>
        <p style="margin: 0;">Select a vulnerability topic to read the theory and access the interactive labs.</p>
      </div>
      <div class="dashboard-grid" id="dashboardGrid">
        <!-- Injected via JS -->
      </div>
    </div>"""

html = html.replace(old_dashboard, '')

# 2. Update renderDashboard() to use t.labs.length
correct_dashboard_js = """function renderDashboard() {
  const grid = document.getElementById('dashboardGrid');
  let html = '';
  topics.forEach(t => {
    if (t.id === 'home' || t.id === 'web101') return;
    
    let labsCount = t.labs ? t.labs.length : 1;
    let solvedCount = t.labs ? solvedLabs.filter(x => t.labs.includes(x)).length : 0;
    
    // Extract english title for dual lang
    const enTitles = {
      'sqli': '1. SQL Injection',
      'xss': '2. Cross-Site Scripting',
      'csrf': '3. CSRF',
      'os-command': '4. OS Command Injection',
      'ssrf': '5. SSRF',
      'auth': '6. Authentication Bypass',
      'path-traversal': '7. Path Traversal',
      'idor': '8. IDOR',
      'info-disc': '9. Info Disclosure',
      'file-upload': '10. File Upload'
    };
    
    html += `
      <div class="dash-card" onclick="document.getElementById('nav-${t.id}').click()">
        <h3 class="lang-id">${t.label}</h3>
        <h3 class="lang-en">${enTitles[t.id]}</h3>
        <div style="color:var(--text3); font-size:13px; margin: 8px 0;">${labsCount} Lab(s)</div>
        <div class="progress-ring"><div class="fill" style="width: ${(solvedCount/labsCount)*100}%"></div></div>
        <div style="font-size:12px; color:var(--text2); text-align:right;">${solvedCount} / ${labsCount} Solved</div>
      </div>
    `;
  });
  grid.innerHTML = html;
}"""

html = re.sub(r'function renderDashboard\(\) \{.*?\}\n', correct_dashboard_js + '\n', html, flags=re.DOTALL)

with open('C:/BugBounty/bugbounty_tutorial.html', 'w', encoding='utf-8') as f:
    f.write(html)