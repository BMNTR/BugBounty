import os
import re

css = open('C:/BugBounty/temp_css.txt', 'r', encoding='utf-8').read()

html_head = f'''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bug Bounty: Web Security Academy</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
{css}
<style>
/* WSA Specific Styles */
.dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px; margin-top: 32px; }}
.topic-card {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; padding: 24px; cursor: pointer; transition: all 0.2s; }}
.topic-card:hover {{ border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0, 255, 204, 0.1); }}
.topic-card h3 {{ margin-bottom: 8px; font-family: var(--font-display); font-size: 20px; }}
.topic-card p {{ color: var(--text2); font-size: 14px; margin-bottom: 16px; line-height: 1.5; }}
.progress-container {{ background: var(--bg3); height: 6px; border-radius: 3px; overflow: hidden; margin-top: auto; }}
.progress-fill {{ background: var(--accent); height: 100%; width: 0%; transition: width 0.3s; }}
.progress-text {{ font-size: 12px; color: var(--text2); margin-top: 8px; text-align: right; font-family: var(--font-mono); }}

.lab-card {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin-bottom: 24px; }}
.lab-header {{ padding: 16px 24px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }}
.lab-badge {{ font-size: 11px; padding: 4px 8px; border-radius: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
.lab-badge.apprentice {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; }}
.lab-badge.practitioner {{ background: rgba(168, 85, 247, 0.2); color: #c084fc; }}
.lab-badge.expert {{ background: rgba(239, 68, 68, 0.2); color: #f87171; }}
.lab-status {{ font-size: 12px; font-family: var(--font-mono); display: flex; align-items: center; gap: 6px; }}
.lab-status.solved {{ color: var(--green); }}
.lab-status.unsolved {{ color: var(--text2); }}
.lab-body {{ padding: 24px; }}
.lab-body h4 {{ font-family: var(--font-display); font-size: 18px; margin-bottom: 12px; }}
.btn-access {{ display: inline-block; background: var(--accent); color: var(--bg); padding: 10px 20px; border-radius: 6px; font-weight: 600; text-decoration: none; margin-top: 16px; cursor: pointer; transition: 0.2s; border: none; }}
.btn-access:hover {{ background: #00e6b8; transform: scale(0.98); }}

.lab-modal {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 100; display: none; align-items: center; justify-content: center; backdrop-filter: blur(4px); }}
.lab-modal.active {{ display: flex; }}
.lab-window {{ width: 90%; max-width: 800px; background: #fff; border-radius: 8px; overflow: hidden; color: #333; font-family: sans-serif; display: flex; flex-direction: column; }}
.lab-browser-bar {{ background: #e5e7eb; padding: 12px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #d1d5db; }}
.lab-browser-url {{ flex: 1; background: #fff; padding: 6px 12px; border-radius: 16px; font-size: 13px; color: #6b7280; font-family: monospace; border: 1px solid #d1d5db; }}
.lab-browser-close {{ cursor: pointer; font-weight: bold; font-size: 18px; color: #4b5563; }}
.lab-iframe-content {{ padding: 32px; min-height: 400px; background: #f9fafb; position: relative; }}

/* Alert styles inside lab */
.lab-alert {{ padding: 16px; border-radius: 6px; margin-bottom: 16px; }}
.lab-alert.success {{ background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
.lab-alert.error {{ background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }}
</style>
</head>
<body>
<div class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <h2><span style="color:var(--accent)">//</span> Web Security Academy</h2>
  </div>
  <div style="padding: 16px 20px;">
    <div style="font-size: 12px; color: var(--text2); margin-bottom: 8px;">TOTAL PROGRESS</div>
    <div class="progress-container"><div class="progress-fill" id="globalProgressFill"></div></div>
    <div class="progress-text" id="globalProgressText">0 / 6 Labs</div>
  </div>
  <nav class="sidebar-nav" id="sidebarNav"></nav>
</div>

<main class="main">
  <div class="topbar">
    <button class="mobile-menu" id="mobileMenu" onclick="toggleSidebar()">&#9776;</button>
    <div class="topbar-page" id="topbarBreadcrumb">
      <span>Academy</span>
      <span class="sep">/</span>
      <span class="cur" id="topbarCurrent">Dashboard</span>
    </div>
    <div class="topbar-actions">
      <div id="google_translate_element"></div>
      <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">Dark</button>
    </div>
  </div>
  <div class="content" id="mainContent">
'''

html_sections = '''
    <!-- DASHBOARD -->
    <div class="section page-active" id="home">
      <div class="home-hero" style="text-align: left; padding: 40px 0;">
        <h2><span style="color:var(--text)">All</span> <span>Topics</span></h2>
        <p style="margin: 0;">Select a vulnerability topic to read the theory and access the interactive labs.</p>
      </div>
      <div class="dashboard-grid" id="dashboardGrid">
        <!-- Injected via JS -->
      </div>
    </div>

    <!-- SQLI -->
    <div class="section" id="sqli">
      <h2>SQL Injection (SQLi)</h2>
      <p>SQL injection is a web security vulnerability that allows an attacker to interfere with the queries that an application makes to its database.</p>
      
      <h3>How it works</h3>
      <p>When user input is passed directly to a database query without sanitization or parameterization, attackers can inject SQL commands.</p>
      <pre><code> = "SELECT * FROM users WHERE username = '" . ['user'] . "'";</code></pre>
      
      <div class="lab-card" id="lab_sqli_1">
        <div class="lab-header">
          <span class="lab-badge apprentice">Apprentice</span>
          <span class="lab-status unsolved" id="status_sqli_1">[ ] Not solved</span>
        </div>
        <div class="lab-body">
          <h4>Lab: SQL injection vulnerability allowing login bypass</h4>
          <p>This lab contains a SQL injection vulnerability in the login bypass. To solve the lab, perform a SQL injection attack that logs in to the application as the <code>administrator</code> user.</p>
          <button class="btn-access" onclick="openLab('sqli_1')">Access the lab</button>
        </div>
      </div>
    </div>

    <!-- XSS -->
    <div class="section" id="xss">
      <h2>Cross-Site Scripting (XSS)</h2>
      <p>Cross-site scripting (also known as XSS) is a web security vulnerability that allows an attacker to compromise the interactions that users have with a vulnerable application.</p>
      
      <div class="lab-card" id="lab_xss_1">
        <div class="lab-header">
          <span class="lab-badge apprentice">Apprentice</span>
          <span class="lab-status unsolved" id="status_xss_1">[ ] Not solved</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Reflected XSS into HTML context with nothing encoded</h4>
          <p>This lab contains a simple reflected cross-site scripting vulnerability in the search functionality. To solve the lab, perform a cross-site scripting attack that calls the <code>alert</code> function.</p>
          <button class="btn-access" onclick="openLab('xss_1')">Access the lab</button>
        </div>
      </div>
    </div>

    <!-- CSRF -->
    <div class="section" id="csrf">
      <h2>Cross-Site Request Forgery (CSRF)</h2>
      <p>CSRF is a vulnerability that allows an attacker to induce users to perform actions that they do not intend to perform.</p>
      
      <div class="lab-card" id="lab_csrf_1">
        <div class="lab-header">
          <span class="lab-badge practitioner">Practitioner</span>
          <span class="lab-status unsolved" id="status_csrf_1">[ ] Not solved</span>
        </div>
        <div class="lab-body">
          <h4>Lab: CSRF vulnerability with no defenses</h4>
          <p>This lab's email change functionality is vulnerable to CSRF. To solve the lab, craft some HTML that uses a CSRF attack to change the viewer's email address and execute it.</p>
          <button class="btn-access" onclick="openLab('csrf_1')">Access the lab</button>
        </div>
      </div>
    </div>
    
    <!-- OS COMMAND -->
    <div class="section" id="os-command">
      <h2>OS Command Injection</h2>
      <p>OS command injection (also known as shell injection) is a web security vulnerability that allows an attacker to execute arbitrary operating system (OS) commands on the server that is running an application, and typically fully compromise the application and all its data.</p>
      
      <div class="lab-card" id="lab_osc_1">
        <div class="lab-header">
          <span class="lab-badge apprentice">Apprentice</span>
          <span class="lab-status unsolved" id="status_osc_1">[ ] Not solved</span>
        </div>
        <div class="lab-body">
          <h4>Lab: OS command injection, simple case</h4>
          <p>This lab contains an OS command injection vulnerability in the product stock checker. To solve the lab, execute the <code>whoami</code> command to determine the name of the current user.</p>
          <button class="btn-access" onclick="openLab('osc_1')">Access the lab</button>
        </div>
      </div>
    </div>

    <!-- SSRF -->
    <div class="section" id="ssrf">
      <h2>Server-Side Request Forgery (SSRF)</h2>
      <p>SSRF is a web security vulnerability that allows an attacker to induce the server-side application to make requests to an unintended location.</p>
      
      <div class="lab-card" id="lab_ssrf_1">
        <div class="lab-header">
          <span class="lab-badge apprentice">Apprentice</span>
          <span class="lab-status unsolved" id="status_ssrf_1">[ ] Not solved</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Basic SSRF against the local server</h4>
          <p>This lab has a stock check feature which fetches data from an internal system. To solve the lab, change the stock check URL to access the admin interface at <code>http://localhost/admin</code> and delete the user <code>carlos</code>.</p>
          <button class="btn-access" onclick="openLab('ssrf_1')">Access the lab</button>
        </div>
      </div>
    </div>
    
    <!-- AUTH BYPASS -->
    <div class="section" id="auth">
      <h2>Authentication Bypass</h2>
      <p>Authentication vulnerabilities allow attackers to bypass login screens or escalate their privileges.</p>
      
      <div class="lab-card" id="lab_auth_1">
        <div class="lab-header">
          <span class="lab-badge practitioner">Practitioner</span>
          <span class="lab-status unsolved" id="status_auth_1">[ ] Not solved</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Username enumeration via subtly different responses</h4>
          <p>This lab is vulnerable to username enumeration and password brute-forcing. Solve the lab by determining a valid username and password, then logging in.</p>
          <button class="btn-access" onclick="openLab('auth_1')">Access the lab</button>
        </div>
      </div>
    </div>
  </div>
</main>

<!-- LAB MODAL -->
<div class="lab-modal" id="labModal">
  <div class="lab-window">
    <div class="lab-browser-bar">
      <div style="display:flex;gap:6px;">
        <div style="width:12px;height:12px;border-radius:50%;background:#ef4444;"></div>
        <div style="width:12px;height:12px;border-radius:50%;background:#eab308;"></div>
        <div style="width:12px;height:12px;border-radius:50%;background:#22c55e;"></div>
      </div>
      <div class="lab-browser-url" id="labUrl">https://random-id.web-security-academy.net/</div>
      <div class="lab-browser-close" onclick="closeLab()">&#10005;</div>
    </div>
    <div class="lab-iframe-content" id="labContent">
      <!-- Lab specific UI injected here -->
    </div>
  </div>
</div>
'''

html_js = '''
<script>
// TOPICS & ROUTING
const topics = [
  {id: 'home', label: 'Dashboard'},
  {id: 'sqli', label: 'SQL Injection', labs: ['sqli_1']},
  {id: 'xss', label: 'Cross-Site Scripting', labs: ['xss_1']},
  {id: 'csrf', label: 'CSRF', labs: ['csrf_1']},
  {id: 'os-command', label: 'OS Command Injection', labs: ['osc_1']},
  {id: 'ssrf', label: 'SSRF', labs: ['ssrf_1']},
  {id: 'auth', label: 'Authentication Bypass', labs: ['auth_1']}
];

// STATE MANAGEMENT
let solvedLabs = JSON.parse(localStorage.getItem('wsa_solved_labs') || '[]');

function saveSolved(labId) {
  if (!solvedLabs.includes(labId)) {
    solvedLabs.push(labId);
    localStorage.setItem('wsa_solved_labs', JSON.stringify(solvedLabs));
    updateUI();
  }
}

function updateUI() {
  let totalSolved = 0;
  let totalLabs = 0;
  
  // Build sidebar
  const nav = document.getElementById('sidebarNav');
  nav.innerHTML = '';
  
  topics.forEach(t => {
    const a = document.createElement('a');
    a.href = '#' + t.id;
    a.dataset.section = t.id;
    
    let labelHTML = t.label;
    if (t.labs) {
      const solvedInTopic = t.labs.filter(l => solvedLabs.includes(l)).length;
      totalSolved += solvedInTopic;
      totalLabs += t.labs.length;
      if (solvedInTopic === t.labs.length) {
        labelHTML +=  <span style="float:right;color:var(--green)">&#10003;</span>;
      }
    }
    
    a.innerHTML = labelHTML;
    a.addEventListener('click', e => { e.preventDefault(); goTo(t.id); });
    nav.appendChild(a);
    
    // Update lab cards
    if (t.labs) {
      t.labs.forEach(labId => {
        const statEl = document.getElementById('status_' + labId);
        if (statEl) {
          if (solvedLabs.includes(labId)) {
            statEl.className = 'lab-status solved';
            statEl.innerHTML = '&#10003; Solved';
          }
        }
      });
    }
  });
  
  // Highlight current in sidebar
  document.querySelectorAll('.sidebar-nav a').forEach(a => {
    if (a.dataset.section === currentPageId) a.classList.add('active');
  });
  
  // Update Global Progress
  document.getElementById('globalProgressText').textContent = ${totalSolved} /  Labs;
  document.getElementById('globalProgressFill').style.width = (totalLabs ? (totalSolved / totalLabs) * 100 : 0) + '%';
  
  // Build Dashboard Grid
  const grid = document.getElementById('dashboardGrid');
  grid.innerHTML = '';
  topics.filter(t => t.id !== 'home').forEach(t => {
    const card = document.createElement('div');
    card.className = 'topic-card';
    const solved = t.labs.filter(l => solvedLabs.includes(l)).length;
    const total = t.labs.length;
    const pct = total ? (solved/total)*100 : 0;
    
    card.innerHTML = 
      <h3></h3>
      <p> Lab</p>
      <div class="progress-container"><div class="progress-fill" style="width:%"></div></div>
      <div class="progress-text"> /  Solved</div>
    ;
    card.addEventListener('click', () => goTo(t.id));
    grid.appendChild(card);
  });
}

let currentPageId = 'home';
function goTo(pageId) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('page-active'));
  document.querySelectorAll('.sidebar-nav a').forEach(a => {
    a.classList.remove('active');
    if (a.dataset.section === pageId) a.classList.add('active');
  });
  const target = document.getElementById(pageId);
  if (target) target.classList.add('page-active');
  currentPageId = pageId;
  window.scrollTo({top:0, behavior:'instant'});
  const topic = topics.find(t => t.id === pageId);
  document.getElementById('topbarCurrent').textContent = topic ? topic.label : pageId;
  
  if (window.innerWidth <= 1024) document.getElementById('sidebar').classList.remove('open');
}

// SIDEBAR COLLAPSE LOGIC
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const main = document.querySelector('.main');
  if (window.innerWidth <= 1024) {
    sidebar.classList.toggle('open');
  } else {
    sidebar.classList.toggle('collapsed');
    main.classList.toggle('expanded');
    localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
  }
}
if (window.innerWidth > 1024 && localStorage.getItem('sidebarCollapsed') === 'true') {
  document.getElementById('sidebar').classList.add('collapsed');
  document.querySelector('.main').classList.add('expanded');
}

// THEME TOGGLE
let dark = true;
function toggleTheme() {
  dark = !dark;
  document.documentElement.style.setProperty('--bg', dark ? '#09090b' : '#fafafa');
  document.documentElement.style.setProperty('--bg2', dark ? '#18181b' : '#ffffff');
  document.documentElement.style.setProperty('--bg3', dark ? '#27272a' : '#f4f4f5');
  document.documentElement.style.setProperty('--border', dark ? '#27272a' : '#e4e4e7');
  document.documentElement.style.setProperty('--text', dark ? '#f8fafc' : '#0f172a');
  document.documentElement.style.setProperty('--text2', dark ? '#94a3b8' : '#475569');
}

// LAB ENGINE
let currentLabId = '';
const labModal = document.getElementById('labModal');
const labContent = document.getElementById('labContent');

const labDefinitions = {
  sqli_1: {
    url: '/login',
    render: () => 
      <h2 style="margin-top:0">Login</h2>
      <div id="sqli_alert"></div>
      <div style="margin-bottom:12px">
        <label style="display:block;margin-bottom:4px">Username</label>
        <input type="text" id="sqli_user" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:4px" />
      </div>
      <div style="margin-bottom:16px">
        <label style="display:block;margin-bottom:4px">Password</label>
        <input type="password" id="sqli_pass" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:4px" />
      </div>
      <button onclick="submitSQLi()" style="background:#3b82f6;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer">Login</button>
    ,
    validate: (user, pass) => {
      // Basic SQLi bypass check: administrator'-- or ' OR 1=1--
      const u = user.toLowerCase();
      if ((u.includes("administrator'") && (u.includes("--") || u.includes("#"))) || 
          (u.includes("'") && u.includes("or") && (u.includes("1=1") || u.includes("true")) && (u.includes("--") || u.includes("#")))) {
        return { success: true, msg: "Logged in as administrator! Lab solved." };
      }
      if (user === 'administrator' && pass === 'password') return { success: false, msg: "Don't guess the password, use SQL injection." };
      return { success: false, msg: "Invalid username or password." };
    }
  },
  xss_1: {
    url: '/search',
    render: () => 
      <h2 style="margin-top:0">Blog Search</h2>
      <div id="xss_alert"></div>
      <div style="display:flex;gap:8px">
        <input type="text" id="xss_q" placeholder="Search..." style="flex:1;padding:8px;border:1px solid #ccc;border-radius:4px" />
        <button onclick="submitXSS()" style="background:#3b82f6;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer">Search</button>
      </div>
      <div id="xss_result" style="margin-top:24px"></div>
    ,
    validate: (q) => {
      if (q.includes('<script>') && q.includes('alert(') && q.includes('</script>')) {
        return { success: true, msg: "XSS triggered! alert() executed. Lab solved." };
      }
      if (q.includes('onerror=') && q.includes('alert(')) {
        return { success: true, msg: "XSS triggered! alert() executed. Lab solved." };
      }
      return { success: false, msg:   search results for: <strong></strong> };
    }
  },
  csrf_1: {
    url: '/my-account',
    render: () => 
      <h2 style="margin-top:0">Update Email</h2>
      <div id="csrf_alert"></div>
      <div style="margin-bottom:12px">
        <label style="display:block;margin-bottom:4px">New Email</label>
        <input type="email" id="csrf_email" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:4px" />
      </div>
      <button onclick="submitCSRF()" style="background:#3b82f6;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer">Update</button>
      <hr style="margin:24px 0;border:none;border-top:1px solid #ddd">
      <p style="font-size:12px;color:#666">Simulate CSRF Attack delivery below (Paste your exploit HTML):</p>
      <textarea id="csrf_payload" rows="4" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:4px;font-family:monospace" placeholder="<html>..."></textarea>
      <button onclick="simulateCSRF()" style="background:#ef4444;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;margin-top:8px">Deliver to Victim</button>
    
  },
  osc_1: {
    url: '/product/stock',
    render: () => 
      <h2 style="margin-top:0">Check Stock</h2>
      <div id="osc_alert"></div>
      <div style="margin-bottom:12px">
        <label style="display:block;margin-bottom:4px">Store ID</label>
        <input type="text" id="osc_store" value="1" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:4px" />
      </div>
      <button onclick="submitOSC()" style="background:#3b82f6;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer">Check</button>
      <div id="osc_result" style="margin-top:16px;font-family:monospace;white-space:pre-wrap;background:#333;color:#4ade80;padding:12px;border-radius:4px;display:none"></div>
    
  },
  ssrf_1: {
    url: '/product/stock',
    render: () => 
      <h2 style="margin-top:0">Check Stock (API)</h2>
      <div id="ssrf_alert"></div>
      <div style="margin-bottom:12px">
        <label style="display:block;margin-bottom:4px">Stock API URL</label>
        <input type="text" id="ssrf_url" value="http://stock.weliketoshop.net:8080/product/stock/check?productId=1" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:4px" />
      </div>
      <button onclick="submitSSRF()" style="background:#3b82f6;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer">Check</button>
    
  },
  auth_1: {
    url: '/login',
    render: () => 
      <h2 style="margin-top:0">Login (Brute Force)</h2>
      <div id="auth_alert"></div>
      <div style="margin-bottom:12px">
        <label style="display:block;margin-bottom:4px">Username</label>
        <input type="text" id="auth_user" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:4px" />
      </div>
      <div style="margin-bottom:16px">
        <label style="display:block;margin-bottom:4px">Password</label>
        <input type="password" id="auth_pass" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:4px" />
      </div>
      <button onclick="submitAuth()" style="background:#3b82f6;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer">Login</button>
      <p style="margin-top:16px;font-size:12px;color:#666">Hint: Valid user is "alberto", valid pass is "carlos". In real labs you use Intruder.</p>
    
  }
};

function openLab(id) {
  currentLabId = id;
  const def = labDefinitions[id];
  if (!def) return;
  document.getElementById('labUrl').textContent = https://0a8f000-.web-security-academy.net;
  labContent.innerHTML = def.render();
  labModal.classList.add('active');
}

function closeLab() {
  labModal.classList.remove('active');
  currentLabId = '';
}

function showLabAlert(prefix, html, type) {
  const el = document.getElementById(prefix + '_alert');
  el.className = 'lab-alert ' + type;
  el.innerHTML = html;
}

// Lab Submit Handlers
function submitSQLi() {
  const u = document.getElementById('sqli_user').value;
  const p = document.getElementById('sqli_pass').value;
  const res = labDefinitions.sqli_1.validate(u, p);
  showLabAlert('sqli', res.msg, res.success ? 'success' : 'error');
  if (res.success) saveSolved('sqli_1');
}

function submitXSS() {
  const q = document.getElementById('xss_q').value;
  const res = labDefinitions.xss_1.validate(q);
  if (res.success) {
    showLabAlert('xss', res.msg, 'success');
    saveSolved('xss_1');
  } else {
    document.getElementById('xss_result').innerHTML = res.msg;
  }
}

function submitCSRF() {
  showLabAlert('csrf', 'Email updated successfully.', 'success');
}
function simulateCSRF() {
  const payload = document.getElementById('csrf_payload').value.toLowerCase();
  if (payload.includes('<form') && payload.includes('action=') && payload.includes('/my-account') && (payload.includes('submit()') || payload.includes('autofocus'))) {
    showLabAlert('csrf', 'Victim visited your page and their email was changed! Lab solved.', 'success');
    saveSolved('csrf_1');
  } else {
    showLabAlert('csrf', 'Payload delivered to victim, but nothing happened. Ensure it submits a POST request to change email.', 'error');
  }
}

function submitOSC() {
  const s = document.getElementById('osc_store').value;
  const resEl = document.getElementById('osc_result');
  resEl.style.display = 'block';
  if (s.includes(';') || s.includes('|') || s.includes('&')) {
    let cmd = s.split(/[;|]/)[1].trim().toLowerCase();
    if (cmd === 'whoami') {
      resEl.textContent = 'peter-wiener';
      showLabAlert('osc', 'whoami executed successfully! Lab solved.', 'success');
      saveSolved('osc_1');
      return;
    } else {
      resEl.textContent = 'Command executed but not whoami.';
      return;
    }
  }
  resEl.textContent = 'Stock: 43 units.';
}

function submitSSRF() {
  const u = document.getElementById('ssrf_url').value;
  if (u.includes('localhost') || u.includes('127.0.0.1')) {
    if (u.includes('/admin/delete?username=carlos')) {
      showLabAlert('ssrf', 'Admin interface accessed and carlos deleted! Lab solved.', 'success');
      saveSolved('ssrf_1');
    } else {
      showLabAlert('ssrf', 'Admin panel accessed. Status: 200 OK. But carlos is not deleted.', 'success');
    }
  } else {
    showLabAlert('ssrf', 'Could not connect to external API.', 'error');
  }
}

function submitAuth() {
  const u = document.getElementById('auth_user').value;
  const p = document.getElementById('auth_pass').value;
  if (u === 'alberto' && p === 'carlos') {
    showLabAlert('auth', 'Logged in as alberto! Lab solved.', 'success');
    saveSolved('auth_1');
  } else if (u === 'alberto') {
    showLabAlert('auth', 'Invalid password', 'error'); // subtle difference
  } else {
    showLabAlert('auth', 'Invalid username or password', 'error');
  }
}

// INITIALIZE
updateUI();
goTo('home');

// MAGIC: Force hide Google Translate Banner without breaking the dropdown
const clearTranslateBanner = setInterval(() => {
  document.body.style.top = '0px';
  const banners = document.querySelectorAll('.goog-te-banner-frame, .VIpgJd-ZVi9od-aZ2wEe-wOHMyf');
  banners.forEach(b => b.style.display = 'none');
}, 500);
</script>
<script type="text/javascript">
function googleTranslateElementInit() {
  new google.translate.TranslateElement({pageLanguage: 'id', includedLanguages: 'en,id', layout: google.translate.TranslateElement.InlineLayout.SIMPLE}, 'google_translate_element');
}
</script>
<script type="text/javascript" src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
</body>
</html>
'''

full_html = html_head + html_sections + html_js
with open('C:/BugBounty/bugbounty_tutorial.html', 'w', encoding='utf-8') as f:
    f.write(full_html)
print("Successfully generated WSA version.")