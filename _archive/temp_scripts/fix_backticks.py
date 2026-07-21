import re

html = open('C:/BugBounty/bugbounty_tutorial.html', 'r', encoding='utf-8').read()

# The broken javascript starts at "const labDefinitions = {"
# and ends right before "function openLab(id)"
start_idx = html.find('const labDefinitions = {')
end_idx = html.find('function openLab(id)')

if start_idx != -1 and end_idx != -1:
    correct_js = '''const labDefinitions = {
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
      return { success: false, msg: "0 search results for: <strong>" + q.replace(/</g, '&lt;') + "</strong>" };
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

'''
    html = html[:start_idx] + correct_js + html[end_idx:]
    open('C:/BugBounty/bugbounty_tutorial.html', 'w', encoding='utf-8').write(html)
    print("Fixed backticks successfully.")
else:
    print("Could not find start or end index.")