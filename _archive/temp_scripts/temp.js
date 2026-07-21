
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
        labelHTML += `<span style="float:right;color:var(--green)">&#10003;</span>`;
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
    a.classList.remove('active');
    if (a.dataset.section === currentPageId) a.classList.add('active');
  });
  
  // Update Global Progress
  document.getElementById('globalProgressText').textContent = `${totalSolved} / ${totalLabs} Labs`;
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
    
    card.innerHTML = `
      <h3>${t.label}</h3>
      <p>${total} Lab(s)</p>
      <div class="progress-container"><div class="progress-fill" style="width:${pct}%"></div></div>
      <div class="progress-text">${solved} / ${total} Solved</div>
    `;
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
    render: () => `
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
    `,
    validate: (user, pass) => {
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
    render: () => `
      <h2 style="margin-top:0">Blog Search</h2>
      <div id="xss_alert"></div>
      <div style="display:flex;gap:8px">
        <input type="text" id="xss_q" placeholder="Search..." style="flex:1;padding:8px;border:1px solid #ccc;border-radius:4px" />
        <button onclick="submitXSS()" style="background:#3b82f6;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer">Search</button>
      </div>
      <div id="xss_result" style="margin-top:24px"></div>
    `,
    validate: (q) => {
      if (q.includes('<script>') && q.includes('alert(') && q.includes('<\\/script>')) {
        return { success: true, msg: "XSS triggered! alert() executed. Lab solved." };
      }
      if (q.includes('onerror=') && q.includes('alert(')) {
        return { success: true, msg: "XSS triggered! alert() executed. Lab solved." };
      }
      return { success: false, msg: "0 search results for: <strong>" + q.replace(/</g, '&lt;') + "</strong>" };
    }
  },
  csrf_1: {
    url: '/my-account',
    render: () => `
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
    `
  },
  osc_1: {
    url: '/product/stock',
    render: () => `
      <h2 style="margin-top:0">Check Stock</h2>
      <div id="osc_alert"></div>
      <div style="margin-bottom:12px">
        <label style="display:block;margin-bottom:4px">Store ID</label>
        <input type="text" id="osc_store" value="1" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:4px" />
      </div>
      <button onclick="submitOSC()" style="background:#3b82f6;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer">Check</button>
      <div id="osc_result" style="margin-top:16px;font-family:monospace;white-space:pre-wrap;background:#333;color:#4ade80;padding:12px;border-radius:4px;display:none"></div>
    `
  },
  ssrf_1: {
    url: '/product/stock',
    render: () => `
      <h2 style="margin-top:0">Check Stock (API)</h2>
      <div id="ssrf_alert"></div>
      <div style="margin-bottom:12px">
        <label style="display:block;margin-bottom:4px">Stock API URL</label>
        <input type="text" id="ssrf_url" value="http://stock.weliketoshop.net:8080/product/stock/check?productId=1" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:4px" />
      </div>
      <button onclick="submitSSRF()" style="background:#3b82f6;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer">Check</button>
    `
  },
  auth_1: {
    url: '/login',
    render: () => `
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
    `
  }
};
function openLab(id) {
  currentLabId = id;
  const def = labDefinitions[id];
  if (!def) return;
  document.getElementById('labUrl').textContent = `https://0a8f000-${id}.web-security-academy.net${def.url}`;
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
  
  fetch('http://127.0.0.1:3000/api/sqli/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: u, password: p })
  })
  .then(res => res.json())
  .then(data => {
    showLabAlert('sqli', data.msg, data.success ? 'success' : 'error');
    if (data.success) saveSolved('sqli_1');
  })
  .catch(err => showLabAlert('sqli', 'Error connecting to backend: ' + err.message, 'error'));
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
  resEl.textContent = 'Executing...';
  
  fetch('http://127.0.0.1:3000/api/osc/stock', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ storeId: s })
  })
  .then(res => res.json())
  .then(data => {
    resEl.textContent = data.output;
    if (data.solved) {
      showLabAlert('osc', 'OS Command Injection successful! Lab solved.', 'success');
      saveSolved('osc_1');
    } else {
      showLabAlert('osc', 'Check output below.', 'info');
    }
  })
  .catch(err => {
    resEl.textContent = 'Error: ' + err.message;
  });
}

function submitSSRF() {
  const u = document.getElementById('ssrf_url').value;
  
  fetch('http://127.0.0.1:3000/api/ssrf/fetch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stockApi: u })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success && data.msg.includes('deleted')) {
      showLabAlert('ssrf', 'Admin interface accessed and carlos deleted! Lab solved.', 'success');
      saveSolved('ssrf_1');
    } else {
      showLabAlert('ssrf', data.msg, data.success ? 'success' : 'error');
    }
  })
  .catch(err => showLabAlert('ssrf', 'Error: ' + err.message, 'error'));
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

