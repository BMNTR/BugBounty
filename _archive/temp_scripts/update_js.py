import re

with open('C:/BugBounty/bugbounty_tutorial.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add the 4 new labs to labDefinitions
new_labs = """
  path_1: {
    id: 'path_1', title: 'Path Traversal / LFI',
    render: function() {
      return `
      <div class="theory-box">
        <h4>💡 Cara Hack (Untuk Pemula):</h4>
        <p>Lihat parameter <code>?file=gambar.png</code>. Coba paksa mundur folder dengan menggantinya menjadi <code>?file=../../../../etc/passwd</code></p>
      </div>
      <div class="db-visualizer">
        <div class="db-title">File System Viewer</div>
        <div class="db-query">Fetching file: <span id="fileQuery">gambar.png</span></div>
        <div class="db-results" id="fileResult" style="white-space: pre-wrap; font-family: monospace;">[IMAGE PREVIEW]</div>
      </div>
      <div style="margin-top:24px;">
        <input type="text" id="filePath" value="gambar.png" class="login-input" style="width:100%; margin-bottom:12px;">
        <button onclick="submitPath()" class="btn-access">Tampilkan File</button>
      </div>
      `;
    }
  },
  idor_1: {
    id: 'idor_1', title: 'Insecure Direct Object Reference (IDOR)',
    render: function() {
      return `
      <div class="theory-box">
        <h4>💡 Cara Hack (Untuk Pemula):</h4>
        <p>Lo sekarang login sebagai pengguna nomor 2 (Wiener). Coba intip pesan rahasia Carlos dengan mengganti ID 2 menjadi 1.</p>
      </div>
      <div class="db-visualizer">
        <div class="db-title">Chat Server</div>
        <div class="db-query">Meminta chat milik User ID: <span id="chatQuery">2</span></div>
        <div class="db-results" id="chatResult">Pesan dari pacar: Jangan lupa jemput!</div>
      </div>
      <div style="margin-top:24px;">
        <input type="number" id="chatId" value="2" class="login-input" style="width:100%; margin-bottom:12px;">
        <button onclick="submitIdor()" class="btn-access">Lihat Pesan</button>
      </div>
      `;
    }
  },
  info_1: {
    id: 'info_1', title: 'Information Disclosure',
    render: function() {
      return `
      <div class="theory-box">
        <h4>💡 Cara Hack (Untuk Pemula):</h4>
        <p>Developer sering ninggalin rahasia di komentar HTML. Coba periksa "View Page Source" dari iframe ini, atau klik tombol di bawah untuk men-simulate error server.</p>
      </div>
      <div style="margin-top:24px; text-align:center;">
        <button onclick="submitInfo()" class="btn-access">Simulasi Server Error</button>
        <div id="infoResult" style="margin-top:20px; text-align:left; color:var(--red); font-family:monospace; background:black; padding:10px;"></div>
      </div>
      <!-- SECRET KEY: ADMIN_1337_HAXXOR -->
      `;
    }
  },
  upload_1: {
    id: 'upload_1', title: 'File Upload Vulnerability',
    render: function() {
      return `
      <div class="theory-box">
        <h4>💡 Cara Hack (Untuk Pemula):</h4>
        <p>Ubah ekstensi gambar dari .png menjadi .php. File PHP bisa mengeksekusi perintah jahat di server!</p>
      </div>
      <div class="db-visualizer" style="background:#000;">
        <div class="db-title">Server Terminal</div>
        <div class="db-results" id="uploadResult" style="color:#0f0; font-family:monospace;">[Waiting for file...]</div>
      </div>
      <div style="margin-top:24px;">
        <input type="text" id="uploadFile" value="foto_profil.png" class="login-input" style="width:100%; margin-bottom:12px;" placeholder="Nama File">
        <input type="text" id="uploadContent" value="INI FOTO" class="login-input" style="width:100%; margin-bottom:12px;" placeholder="Isi File">
        <button onclick="submitUpload()" class="btn-access">Upload File</button>
      </div>
      `;
    }
  }
};"""

# We need to inject these new definitions right before the closing brace of labDefinitions
pattern = r'(const labDefinitions = \{.*?\n)(};\n)'
# Actually, the file structure might be different, let's use a simpler regex
# Find the end of labDefinitions
# It ends with:
#   auth_1: {
#     ...
#     }
#   }
# };
# Let's just do a string replacement on `auth_1: { ... },` or just inject at the end.

# To be safe, let's replace "};" with "}," + new_labs if we can find the exact end of labDefinitions.
# Let's match auth_1 block end.
auth_end_pattern = r"(id: 'auth_1'.*?    }\n  )(}\n);"
replacement = r"\g<1>},\n" + new_labs + "\n;"
html = re.sub(auth_end_pattern, replacement, html, flags=re.DOTALL)


# Now we also need to add the functions to handle the clicks (submitPath, submitIdor, submitInfo, submitUpload)
js_functions = """
async function submitPath() {
  const file = document.getElementById('filePath').value;
  document.getElementById('fileQuery').innerText = file;
  
  try {
    const res = await fetch('http://127.0.0.1:3000/api/path/read', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file: file })
    });
    const data = await res.json();
    document.getElementById('fileResult').innerText = data.output;
    if (data.solved) markSolved('path_1');
  } catch (e) {
    document.getElementById('fileResult').innerText = "Network error";
  }
}

async function submitIdor() {
  const id = document.getElementById('chatId').value;
  document.getElementById('chatQuery').innerText = id;
  
  try {
    const res = await fetch(`http://127.0.0.1:3000/api/idor/chat?id=${id}`);
    const data = await res.json();
    document.getElementById('chatResult').innerText = data.message;
    if (data.solved) markSolved('idor_1');
  } catch (e) {
    document.getElementById('chatResult').innerText = "Network error";
  }
}

async function submitInfo() {
  try {
    const res = await fetch(`http://127.0.0.1:3000/api/info/error`);
    const data = await res.json();
    document.getElementById('infoResult').innerText = data.error_log;
    if (data.solved) markSolved('info_1');
  } catch (e) {
    document.getElementById('infoResult').innerText = "Network error";
  }
}

async function submitUpload() {
  const filename = document.getElementById('uploadFile').value;
  const content = document.getElementById('uploadContent').value;
  
  try {
    const res = await fetch('http://127.0.0.1:3000/api/upload/file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename: filename, content: content })
    });
    const data = await res.json();
    document.getElementById('uploadResult').innerText = data.msg;
    if (data.solved) markSolved('upload_1');
  } catch (e) {
    document.getElementById('uploadResult').innerText = "Network error";
  }
}
"""

html = html.replace('function markSolved(id) {', js_functions + '\n\nfunction markSolved(id) {')

with open('C:/BugBounty/bugbounty_tutorial.html', 'w', encoding='utf-8') as f:
    f.write(html)