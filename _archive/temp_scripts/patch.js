function submitSQLi() {
  const u = document.getElementById('sqli_user').value;
  const p = document.getElementById('sqli_pass').value;
  
  fetch('http://localhost:3000/api/sqli/login', {
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

function submitOSC() {
  const s = document.getElementById('osc_store').value;
  const resEl = document.getElementById('osc_result');
  resEl.style.display = 'block';
  resEl.textContent = 'Executing...';
  
  fetch('http://localhost:3000/api/osc/stock', {
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
  
  fetch('http://localhost:3000/api/ssrf/fetch', {
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