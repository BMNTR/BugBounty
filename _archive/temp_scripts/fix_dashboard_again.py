import re

with open('C:/BugBounty/bugbounty_tutorial.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Change the new dashboard ID from 'dashboard' to 'home' to match JS
html = html.replace('<div class="section active" id="dashboard">', '<div class="section page-active" id="home">')

# 2. Fix the JS that builds the dashboard grid. It is currently at line 1032:
old_grid_js = """  // Build Dashboard Grid
  const grid = document.getElementById('dashboardGrid');
  grid.innerHTML = '';
  topics.filter(t => t.id !== 'home').forEach(t => {
    const card = document.createElement('div');
    card.className = 'topic-card';
    const solved = t.labs.filter(l => solvedLabs.includes(l)).length;
    const total = t.labs.length;
    const pct = total ? (solved/total)*100 : 0;
    
    card.innerHTML = `
      <h3>${t.label}</h3>
      <p>${total} Lab(s)</p>
      <div class="progress-container"><div class="progress-fill" style="width:${pct}%"></div></div>
      <div class="progress-text">${solved} / ${total} Solved</div>
    `;
    card.addEventListener('click', () => goTo(t.id));
    grid.appendChild(card);
  });"""

new_grid_js = """  // Build Dashboard Grid
  const grid = document.getElementById('dashboardGrid');
  if (grid) {
    grid.innerHTML = '';
    
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
    
    topics.filter(t => t.id !== 'home' && t.id !== 'web101').forEach(t => {
      const card = document.createElement('div');
      card.className = 'topic-card dash-card';
      let solved = 0;
      let total = 1;
      if (t.labs) {
          solved = t.labs.filter(l => solvedLabs.includes(l)).length;
          total = t.labs.length;
      }
      const pct = total ? (solved/total)*100 : 0;
      
      let enTitle = enTitles[t.id] || t.label;
      
      card.innerHTML = `
        <h3 class="lang-id">${t.label}</h3>
        <h3 class="lang-en">${enTitle}</h3>
        <p>${total} Lab(s)</p>
        <div class="progress-container"><div class="progress-fill" style="width:${pct}%"></div></div>
        <div class="progress-text">${solved} / ${total} Solved</div>
      `;
      card.addEventListener('click', () => goTo(t.id));
      grid.appendChild(card);
    });
  }"""

html = html.replace(old_grid_js, new_grid_js)

with open('C:/BugBounty/bugbounty_tutorial.html', 'w', encoding='utf-8') as f:
    f.write(html)