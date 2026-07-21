import re

with open('C:/BugBounty/bugbounty_tutorial.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update CSS to hide languages based on body class
css_addition = """
/* LANGUAGE SYSTEM */
body.lang-id .lang-en { display: none !important; }
body.lang-en .lang-id { display: none !important; }
.lang-toggle-btn { background: var(--bg2); color: var(--text); border: 1px solid var(--border); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-family: var(--font-body); font-size: 13px; }
.lang-toggle-btn:hover { background: var(--bg3); }
"""
html = html.replace('/* === QUIZ & LAB SYSTEM === */', css_addition + '\n/* === QUIZ & LAB SYSTEM === */')

# Ensure body has default lang
if '<body class="lang-id">' not in html:
    html = html.replace('<body>', '<body class="lang-id">')

# 2. Update topbar to replace Google Translate with native toggle
new_topbar = """
    <div class="topbar-actions">
      <button class="lang-toggle-btn" onclick="toggleLanguage()" id="langToggleBtn">EN / ID</button>
      <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">Dark</button>
    </div>
"""
html = re.sub(r'<div class="topbar-actions">.*?</div>', new_topbar, html, flags=re.DOTALL)

# Add toggleLanguage function
js_lang_func = """
function toggleLanguage() {
  const body = document.body;
  if (body.classList.contains('lang-id')) {
    body.classList.remove('lang-id');
    body.classList.add('lang-en');
    localStorage.setItem('wsa_lang', 'en');
  } else {
    body.classList.remove('lang-en');
    body.classList.add('lang-id');
    localStorage.setItem('wsa_lang', 'id');
  }
}
// Init lang
if (localStorage.getItem('wsa_lang') === 'en') {
  document.body.classList.remove('lang-id');
  document.body.classList.add('lang-en');
}
"""
html = html.replace('// STATE MANAGEMENT', js_lang_func + '\n\n// STATE MANAGEMENT')

# Remove Google translate script
html = re.sub(r'<script type="text/javascript" src="https://translate.google.com/translate_a/element.js\?cb=googleTranslateElementInit"></script>', '', html)
html = re.sub(r'function googleTranslateElementInit\(\) \{.*?\}', '', html, flags=re.DOTALL)

# 3. Rewrite all sections (Web 101 to 10 Labs) with polite language, no emojis, and bilingual support.
new_sections = """
    <!-- WEB 101 -->
    <div class="section" id="web101">
      <div class="lang-id">
        <h2>Web 101: Internet Dari Dasar</h2>
        <p>Bagi Anda yang baru memulai belajar keamanan siber, silakan pelajari konsep dasar internet menggunakan analogi sederhana berikut.</p>
        <div class="skill-theory">
          <h3>Membayangkan Internet Sebagai Sebuah Restoran</h3>
          <ul>
            <li><strong>Client (Browser Anda):</strong> Ini adalah <strong>Pelanggan</strong>. Anda duduk dan meminta menu (meminta halaman web).</li>
            <li><strong>Server:</strong> Ini adalah <strong>Pelayan dan Dapur</strong>. Mereka menerima pesanan Anda, memprosesnya, dan mengantarkannya kembali.</li>
            <li><strong>Database:</strong> Ini adalah <strong>Gudang Bahan Makanan dan Buku Resep Rahasia</strong>. Tempat menyimpan username, kata sandi, dan data penting.</li>
            <li><strong>HTML & CSS:</strong> Ini adalah <strong>Dekorasi Restoran dan Buku Menu</strong>. Hanya tampilan visual.</li>
            <li><strong>JavaScript (JS):</strong> Ini adalah <strong>Pelayan Robot di Meja Anda</strong>. Membantu tugas kecil langsung di layar tanpa harus menghubungi server.</li>
            <li><strong>Request (HTTP):</strong> Kertas pesanan yang Anda berikan ke pelayan.</li>
            <li><strong>Response (HTTP):</strong> Makanan (Halaman Web) yang diantarkan ke meja Anda.</li>
          </ul>
          <br>
          <h3>Apa itu "Hacking"?</h3>
          <p>Meretas (Hacking) pada dasarnya adalah mencari celah pada aturan restoran tersebut. Misalnya, pelanggan dilarang masuk ke dapur, namun Anda menemukan pintu dapur yang tidak terkunci dan berhasil masuk.</p>
        </div>
      </div>
      <div class="lang-en">
        <h2>Web 101: Internet Basics</h2>
        <p>For those who are completely new to cybersecurity, please learn the basic concepts of the internet using this simple analogy.</p>
        <div class="skill-theory">
          <h3>Imagine the Internet as a Restaurant</h3>
          <ul>
            <li><strong>Client (Your Browser):</strong> This is the <strong>Customer</strong>. You sit and ask for the menu (request a webpage).</li>
            <li><strong>Server:</strong> This is the <strong>Waiter and Kitchen</strong>. They take your order, process it, and deliver it back to you.</li>
            <li><strong>Database:</strong> This is the <strong>Storage Room and Secret Recipe Book</strong>. It stores usernames, passwords, and important data.</li>
            <li><strong>HTML & CSS:</strong> This is the <strong>Restaurant Decoration and Menu Book</strong>. Just visual presentation.</li>
            <li><strong>JavaScript (JS):</strong> This is a <strong>Robot Waiter at your table</strong>. It helps with small tasks directly on your screen without contacting the server.</li>
            <li><strong>Request (HTTP):</strong> The order slip you give to the waiter.</li>
            <li><strong>Response (HTTP):</strong> The food (Webpage) delivered to your table.</li>
          </ul>
          <br>
          <h3>What is "Hacking"?</h3>
          <p>Hacking is basically finding loopholes in the restaurant's rules. For example, customers are forbidden from entering the kitchen, but you find an unlocked door and successfully enter.</p>
        </div>
      </div>
    </div>

    <!-- DASHBOARD -->
    <div class="section active" id="dashboard">
      <h2 class="lang-id">Selamat Datang di Bug Bounty Academy</h2>
      <h2 class="lang-en">Welcome to Bug Bounty Academy</h2>
      <p class="lang-id">Kerjakan lab di bawah ini untuk belajar keamanan web selangkah demi selangkah. Jangan lupa membaca teorinya terlebih dahulu.</p>
      <p class="lang-en">Complete the labs below to learn web security step by step. Don't forget to read the theory first.</p>
      <div class="dashboard-grid" id="dashboardGrid">
        <!-- Injected via JS -->
      </div>
    </div>

    <!-- SQLI -->
    <div class="section" id="sqli">
      <h2>1. SQL Injection (SQLi)</h2>
      <div class="lang-id">
        <div class="skill-theory">
          <h3>Analogi: Mengelabui Penjaga Keamanan dengan Logika</h3>
          <p>Bayangkan Anda ingin masuk ke sebuah klub malam. Penjaga akan menanyakan nama Anda dan mencarinya di daftar tamu.</p>
          <p>Namun, bagaimana jika Anda menjawab: <strong>"Nama saya Budi, ATAU saya adalah pemilik klub ini"</strong>?</p>
          <p>Jika sistem keamanan sangat lugu, ia akan mengevaluasi logika tersebut dan mengizinkan Anda masuk karena bagian "saya adalah pemilik klub" bernilai benar. Anda berhasil masuk tanpa memiliki akun yang sah.</p>
          <h4>Cara Menyelesaikan Lab:</h4>
          <ul>
            <li>Di kolom username, masukkan tanda petik tunggal <code>'</code> untuk memanipulasi pertanyaan sistem.</li>
            <li>Gunakan <code>' OR 1=1--</code>. Penjelasannya: <code>'</code> menutup teks, <code>OR 1=1</code> selalu benar, dan <code>--</code> mengabaikan sisa perintah di belakangnya.</li>
          </ul>
        </div>
      </div>
      <div class="lang-en">
        <div class="skill-theory">
          <h3>Analogy: Tricking a Security Guard with Logic</h3>
          <p>Imagine you want to enter an exclusive club. The guard asks for your name and checks the guest list.</p>
          <p>But what if you reply: <strong>"My name is Bob, OR I am the owner of this club"</strong>?</p>
          <p>If the security system is naive, it evaluates the logic and lets you in because the "I am the owner" part is mathematically true. You bypass authentication without a valid account.</p>
          <h4>How to Solve the Lab:</h4>
          <ul>
            <li>In the username field, input a single quote <code>'</code> to manipulate the system's query.</li>
            <li>Use <code>' OR 1=1--</code>. Explanation: <code>'</code> closes the text, <code>OR 1=1</code> is always true, and <code>--</code> ignores the rest of the query.</li>
          </ul>
        </div>
      </div>
      <div class="lab-card" id="lab_sqli_1">
        <div class="lab-header">
          <span class="lab-badge apprentice lang-id">Pemula</span><span class="lab-badge apprentice lang-en">Beginner</span>
          <span class="lab-status unsolved" id="status_sqli_1"></span>
        </div>
        <div class="lab-body">
          <h4 class="lang-id">Lab: Melewati login dengan SQL Injection</h4><h4 class="lang-en">Lab: Login bypass using SQL Injection</h4>
          <p class="lang-id">Masuklah sebagai <code>administrator</code> menggunakan trik logika di atas.</p>
          <p class="lang-en">Log in as <code>administrator</code> using the logic trick described above.</p>
          <button class="btn-access lang-id" onclick="openLab('sqli_1')">Akses Lab</button>
          <button class="btn-access lang-en" onclick="openLab('sqli_1')">Access Lab</button>
        </div>
      </div>
    </div>

    <!-- XSS -->
    <div class="section" id="xss">
      <h2>2. Cross-Site Scripting (XSS)</h2>
      <div class="lang-id">
        <div class="skill-theory">
          <h3>Analogi: Menempelkan Pesan Menyesatkan di Papan Pengumuman</h3>
          <p>Bayangkan sebuah papan pengumuman di mana siapa saja boleh menulis pesan. Anda menulis sebuah instruksi: <strong>"Siapapun yang membaca ini, tolong tampar wajah Anda sendiri"</strong>.</p>
          <p>Di dunia komputer, papan pengumuman tersebut adalah <em>kolom komentar</em>. Instruksi tersebut adalah <strong>JavaScript</strong>. Saat pengguna lain membuka halaman tersebut, peramban (browser) mereka akan menjalankan JavaScript tersebut secara otomatis.</p>
          <h4>Cara Menyelesaikan Lab:</h4>
          <ul>
            <li>Kode JavaScript dasar untuk pengujian: <code>&lt;script&gt;alert(1)&lt;/script&gt;</code></li>
            <li>Jika Anda memasukkannya ke dalam pencarian dan muncul kotak peringatan berisi angka 1, Anda telah berhasil.</li>
          </ul>
        </div>
      </div>
      <div class="lang-en">
        <div class="skill-theory">
          <h3>Analogy: Pinning Misleading Instructions on a Notice Board</h3>
          <p>Imagine a notice board where anyone can write a message. You write an instruction: <strong>"Whoever reads this, please slap your own face"</strong>.</p>
          <p>In computers, the notice board is a <em>comment section</em>. The instruction is <strong>JavaScript</strong>. When other users open the page, their browsers will execute the JavaScript automatically.</p>
          <h4>How to Solve the Lab:</h4>
          <ul>
            <li>Basic testing JavaScript code: <code>&lt;script&gt;alert(1)&lt;/script&gt;</code></li>
            <li>If you input it into the search bar and a warning box with the number 1 appears, you succeed.</li>
          </ul>
        </div>
      </div>
      <div class="lab-card" id="lab_xss_1">
        <div class="lab-header">
          <span class="lab-badge apprentice lang-id">Pemula</span><span class="lab-badge apprentice lang-en">Beginner</span>
          <span class="lab-status unsolved" id="status_xss_1"></span>
        </div>
        <div class="lab-body">
          <h4 class="lang-id">Lab: Memunculkan peringatan Alert</h4><h4 class="lang-en">Lab: Triggering an Alert popup</h4>
          <p class="lang-id">Masukkan kode JavaScript ke dalam fitur pencarian untuk memunculkan kotak peringatan.</p>
          <p class="lang-en">Input JavaScript code into the search feature to trigger a warning box.</p>
          <button class="btn-access lang-id" onclick="openLab('xss_1')">Akses Lab</button>
          <button class="btn-access lang-en" onclick="openLab('xss_1')">Access Lab</button>
        </div>
      </div>
    </div>

    <!-- CSRF -->
    <div class="section" id="csrf">
      <h2>3. Cross-Site Request Forgery (CSRF)</h2>
      <div class="lang-id">
        <div class="skill-theory">
          <h3>Analogi: Memalsukan Surat Kuasa</h3>
          <p>Bayangkan Anda memberikan KTP Anda ke teller bank. Seseorang menyusupkan surat permintaan transfer uang di antara dokumen Anda.</p>
          <p>Teller bank (Server) melihat KTP asli Anda, sehingga mereka langsung memproses surat tersebut tanpa meminta konfirmasi ulang. Begitulah cara kerja CSRF: penyerang membuat tautan rahasia yang, jika diklik oleh korban yang sedang login, akan mengeksekusi tindakan tanpa sepengetahuan korban.</p>
        </div>
      </div>
      <div class="lang-en">
        <div class="skill-theory">
          <h3>Analogy: Forging a Letter of Authorization</h3>
          <p>Imagine handing your ID card to a bank teller. Someone slips a money transfer request among your documents.</p>
          <p>The teller (Server) sees your valid ID and processes the request without asking for further confirmation. That is how CSRF works: an attacker creates a secret link that, when clicked by a logged-in victim, executes actions without the victim's knowledge.</p>
        </div>
      </div>
      <div class="lab-card" id="lab_csrf_1">
        <div class="lab-header">
          <span class="lab-badge practitioner lang-id">Menengah</span><span class="lab-badge practitioner lang-en">Intermediate</span>
          <span class="lab-status unsolved" id="status_csrf_1"></span>
        </div>
        <div class="lab-body">
          <h4 class="lang-id">Lab: Mengubah Email Korban Secara Paksa</h4><h4 class="lang-en">Lab: Forcibly Changing Victim's Email</h4>
          <p class="lang-id">Buat kode HTML yang akan secara otomatis mengirimkan formulir penggantian email saat halaman dibuka.</p>
          <p class="lang-en">Create HTML code that automatically submits an email change form when the page is opened.</p>
          <button class="btn-access lang-id" onclick="openLab('csrf_1')">Akses Lab</button>
          <button class="btn-access lang-en" onclick="openLab('csrf_1')">Access Lab</button>
        </div>
      </div>
    </div>

    <!-- OS COMMAND -->
    <div class="section" id="os-command">
      <h2>4. OS Command Injection</h2>
      <div class="lang-id">
        <div class="skill-theory">
          <h3>Analogi: Menyisipkan Perintah Tambahan kepada Robot</h3>
          <p>Anda memberikan instruksi kepada robot pelayan: <em>"Tolong periksa stok beras"</em>.</p>
          <p>Bagaimana jika Anda menulis: <strong>"Periksa stok beras DAN (&&) berikan saya kunci brankas"</strong>?</p>
          <p>Karakter khusus seperti <code>;</code> atau <code>|</code> atau <code>&&</code> memungkinkan Anda menambahkan perintah sistem operasi tambahan yang akan dieksekusi oleh server.</p>
        </div>
      </div>
      <div class="lang-en">
        <div class="skill-theory">
          <h3>Analogy: Appending Extra Commands to a Robot</h3>
          <p>You give an instruction to a robot waiter: <em>"Please check the rice stock"</em>.</p>
          <p>What if you wrote: <strong>"Check the rice stock AND (&&) give me the safe key"</strong>?</p>
          <p>Special characters like <code>;</code> or <code>|</code> or <code>&&</code> allow you to append additional operating system commands that the server will execute.</p>
        </div>
      </div>
      <div class="lab-card" id="lab_osc_1">
        <div class="lab-header">
          <span class="lab-badge apprentice lang-id">Pemula</span><span class="lab-badge apprentice lang-en">Beginner</span>
          <span class="lab-status unsolved" id="status_osc_1"></span>
        </div>
        <div class="lab-body">
          <h4 class="lang-id">Lab: Memeriksa Identitas Sistem</h4><h4 class="lang-en">Lab: Checking System Identity</h4>
          <p class="lang-id">Gunakan karakter <code>|</code> diikuti dengan perintah <code>whoami</code> pada kolom pemeriksa stok.</p>
          <p class="lang-en">Use the <code>|</code> character followed by the <code>whoami</code> command in the stock checker field.</p>
          <button class="btn-access lang-id" onclick="openLab('osc_1')">Akses Lab</button>
          <button class="btn-access lang-en" onclick="openLab('osc_1')">Access Lab</button>
        </div>
      </div>
    </div>

    <!-- SSRF -->
    <div class="section" id="ssrf">
      <h2>5. Server-Side Request Forgery (SSRF)</h2>
      <div class="lang-id">
        <div class="skill-theory">
          <h3>Analogi: Mengelabui Kurir Internal</h3>
          <p>Anda ingin melihat dokumen di brankas staf, namun Anda dihentikan oleh penjaga di pintu masuk.</p>
          <p>Anda lalu meminta bantuan kurir internal perusahaan: <em>"Tolong ambilkan barang dari brankas staf untuk saya"</em>. Penjaga mengizinkan kurir tersebut karena ia adalah orang dalam. SSRF mengeksploitasi fungsi server untuk mengakses alamat lokal (seperti <code>localhost</code>).</p>
        </div>
      </div>
      <div class="lang-en">
        <div class="skill-theory">
          <h3>Analogy: Tricking an Internal Courier</h3>
          <p>You want to see documents in the staff safe, but the guard stops you at the entrance.</p>
          <p>You then ask the company's internal courier: <em>"Please fetch the item from the staff safe for me"</em>. The guard allows the courier because they are an insider. SSRF exploits the server to access local addresses (like <code>localhost</code>).</p>
        </div>
      </div>
      <div class="lab-card" id="lab_ssrf_1">
        <div class="lab-header">
          <span class="lab-badge apprentice lang-id">Pemula</span><span class="lab-badge apprentice lang-en">Beginner</span>
          <span class="lab-status unsolved" id="status_ssrf_1"></span>
        </div>
        <div class="lab-body">
          <h4 class="lang-id">Lab: Menyerang Panel Admin Secara Internal</h4><h4 class="lang-en">Lab: Attacking Admin Panel Internally</h4>
          <p class="lang-id">Perintahkan server untuk mengakses <code>http://localhost/admin/delete?username=carlos</code>.</p>
          <p class="lang-en">Instruct the server to access <code>http://localhost/admin/delete?username=carlos</code>.</p>
          <button class="btn-access lang-id" onclick="openLab('ssrf_1')">Akses Lab</button>
          <button class="btn-access lang-en" onclick="openLab('ssrf_1')">Access Lab</button>
        </div>
      </div>
    </div>

    <!-- AUTH BYPASS -->
    <div class="section" id="auth">
      <h2>6. Authentication Bypass</h2>
      <div class="lang-id">
        <div class="skill-theory">
          <h3>Analogi: Menebak Nama dari Respons Penjaga</h3>
          <p>Saat Anda menebak kata sandi untuk akun "Budi", penjaga menjawab "Salah!" dalam 1 detik. Namun untuk akun "Admin", penjaga butuh 5 detik dan merespons "Kata sandi salah!".</p>
          <p>Perbedaan waktu ini memberitahu Anda bahwa akun "Admin" memang benar ada di dalam sistem. Ini disebut Enumerasi Pengguna (Username Enumeration).</p>
        </div>
      </div>
      <div class="lang-en">
        <div class="skill-theory">
          <h3>Analogy: Guessing Names from Guard Responses</h3>
          <p>When you guess the password for "Bob", the guard replies "Wrong!" in 1 second. But for "Admin", the guard takes 5 seconds and replies "Incorrect password!".</p>
          <p>This time difference tells you that the "Admin" account actually exists in the system. This is called Username Enumeration.</p>
        </div>
      </div>
      <div class="lab-card" id="lab_auth_1">
        <div class="lab-header">
          <span class="lab-badge practitioner lang-id">Menengah</span><span class="lab-badge practitioner lang-en">Intermediate</span>
          <span class="lab-status unsolved" id="status_auth_1"></span>
        </div>
        <div class="lab-body">
          <h4 class="lang-id">Lab: Menebak Username dari Perbedaan Respons</h4><h4 class="lang-en">Lab: Guessing Usernames from Response Differences</h4>
          <p class="lang-id">Pahami perbedaan pesan kesalahan (error) untuk menemukan username yang valid.</p>
          <p class="lang-en">Understand the differences in error messages to find a valid username.</p>
          <button class="btn-access lang-id" onclick="openLab('auth_1')">Akses Lab</button>
          <button class="btn-access lang-en" onclick="openLab('auth_1')">Access Lab</button>
        </div>
      </div>
    </div>

    <!-- PATH TRAVERSAL -->
    <div class="section" id="path-traversal">
      <h2>7. Path Traversal (Directory Traversal)</h2>
      <div class="lang-id">
        <div class="skill-theory">
          <h3>Analogi: Melangkah Mundur ke Ruang Arsip Rahasia</h3>
          <p>Pelayan mempersilakan Anda mengambil foto menu di folder <code>/Tamu/Menu/</code> dengan meminta file <code>menu.jpg</code>.</p>
          <p>Bagaimana jika Anda meminta file bernama <strong>"Mundur 2 Langkah, masuk ke Ruang Staf, berikan file Rahasia.txt"</strong>? Di dunia komputer, "mundur satu direktori" disimbolkan dengan <code>../</code>. Anda dapat menggunakannya untuk membaca file sistem operasi yang sensitif.</p>
        </div>
      </div>
      <div class="lang-en">
        <div class="skill-theory">
          <h3>Analogy: Stepping Back into the Secret Archive</h3>
          <p>The waiter lets you retrieve a menu photo from the <code>/Guests/Menu/</code> folder by requesting <code>menu.jpg</code>.</p>
          <p>What if you request a file named <strong>"Step back 2 times, enter the Staff Room, give me Secret.txt"</strong>? In computing, "step back one directory" is symbolized by <code>../</code>. You can use it to read sensitive operating system files.</p>
        </div>
      </div>
      <div class="lab-card" id="lab_path_1">
        <div class="lab-header">
          <span class="lab-badge apprentice lang-id">Pemula</span><span class="lab-badge apprentice lang-en">Beginner</span>
          <span class="lab-status unsolved" id="status_path_1"></span>
        </div>
        <div class="lab-body">
          <h4 class="lang-id">Lab: Membaca File Sistem</h4><h4 class="lang-en">Lab: Reading System Files</h4>
          <p class="lang-id">Gunakan <code>../../../../etc/passwd</code> pada parameter gambar untuk membaca file rahasia.</p>
          <p class="lang-en">Use <code>../../../../etc/passwd</code> on the image parameter to read a secret file.</p>
          <button class="btn-access lang-id" onclick="openLab('path_1')">Akses Lab</button>
          <button class="btn-access lang-en" onclick="openLab('path_1')">Access Lab</button>
        </div>
      </div>
    </div>

    <!-- IDOR -->
    <div class="section" id="idor">
      <h2>8. IDOR (Insecure Direct Object Reference)</h2>
      <div class="lang-id">
        <div class="skill-theory">
          <h3>Analogi: Menukar Nomor Kamar di Kartu Akses Hotel</h3>
          <p>Anda diberikan kartu akses untuk masuk ke kamar nomor <strong>101</strong>.</p>
          <p>Sistem keamanan hotel buruk. Anda memodifikasi cip di kartu tersebut menjadi angka <strong>102</strong>, dan sistem mengizinkan Anda masuk ke kamar orang lain. Begitulah IDOR bekerja: memodifikasi nilai identitas di URL atau sistem tanpa adanya pengecekan hak akses.</p>
        </div>
      </div>
      <div class="lang-en">
        <div class="skill-theory">
          <h3>Analogy: Swapping Room Numbers on a Hotel Keycard</h3>
          <p>You are given an access card for room number <strong>101</strong>.</p>
          <p>The hotel's security is poor. You modify the chip on the card to number <strong>102</strong>, and the system lets you into someone else's room. That is how IDOR works: modifying identity values in URLs or systems without proper access control checks.</p>
        </div>
      </div>
      <div class="lab-card" id="lab_idor_1">
        <div class="lab-header">
          <span class="lab-badge apprentice lang-id">Pemula</span><span class="lab-badge apprentice lang-en">Beginner</span>
          <span class="lab-status unsolved" id="status_idor_1"></span>
        </div>
        <div class="lab-body">
          <h4 class="lang-id">Lab: Mengintip Pesan Orang Lain</h4><h4 class="lang-en">Lab: Peeking at Others' Messages</h4>
          <p class="lang-id">Ubah parameter ID dari 2 menjadi 1 untuk membaca pesan rahasia pengguna lain.</p>
          <p class="lang-en">Change the ID parameter from 2 to 1 to read another user's secret message.</p>
          <button class="btn-access lang-id" onclick="openLab('idor_1')">Akses Lab</button>
          <button class="btn-access lang-en" onclick="openLab('idor_1')">Access Lab</button>
        </div>
      </div>
    </div>

    <!-- INFO DISCLOSURE -->
    <div class="section" id="info-disc">
      <h2>9. Information Disclosure</h2>
      <div class="lang-id">
        <div class="skill-theory">
          <h3>Analogi: Karyawan yang Terlalu Banyak Bicara</h3>
          <p>Saat terjadi kendala di restoran, bukannya mengatakan "Mohon maaf atas ketidaknyamanan ini", seorang karyawan malah membeberkan: "Maaf, brankas kami yang kata sandinya 12345 sedang rusak."</p>
          <p>Sistem komputer seringkali mengeluarkan pesan kesalahan (Error Message) yang terlalu detail (verbose), sehingga membocorkan informasi sensitif yang dapat digunakan oleh peretas.</p>
        </div>
      </div>
      <div class="lang-en">
        <div class="skill-theory">
          <h3>Analogy: The Talkative Employee</h3>
          <p>When an issue occurs at a restaurant, instead of saying "Sorry for the inconvenience," an employee blurts out: "Sorry, our safe with the password 12345 is currently broken."</p>
          <p>Computer systems often output error messages that are too detailed (verbose), inadvertently leaking sensitive information that hackers can exploit.</p>
        </div>
      </div>
      <div class="lab-card" id="lab_info_1">
        <div class="lab-header">
          <span class="lab-badge apprentice lang-id">Pemula</span><span class="lab-badge apprentice lang-en">Beginner</span>
          <span class="lab-status unsolved" id="status_info_1"></span>
        </div>
        <div class="lab-body">
          <h4 class="lang-id">Lab: Menemukan Rahasia Tersembunyi</h4><h4 class="lang-en">Lab: Finding Hidden Secrets</h4>
          <p class="lang-id">Simulasikan kesalahan server untuk memunculkan pesan error yang membocorkan data penting.</p>
          <p class="lang-en">Simulate a server error to trigger an error message that leaks critical data.</p>
          <button class="btn-access lang-id" onclick="openLab('info_1')">Akses Lab</button>
          <button class="btn-access lang-en" onclick="openLab('info_1')">Access Lab</button>
        </div>
      </div>
    </div>

    <!-- FILE UPLOAD -->
    <div class="section" id="file-upload">
      <h2>10. File Upload Vulnerability</h2>
      <div class="lang-id">
        <div class="skill-theory">
          <h3>Analogi: Menyelundupkan Barang Berbahaya</h3>
          <p>Saat melewati pemeriksaan keamanan, petugas hanya memeriksa label di koper Anda yang bertuliskan "Pakaian" (File <code>.png</code>). Namun, sistem tidak memeriksa isi di dalamnya.</p>
          <p>Anda dapat mengunggah skrip berbahaya (File <code>.php</code>) dengan memanipulasi nama ekstensinya, lalu menjalankan perintah dari jarak jauh.</p>
        </div>
      </div>
      <div class="lang-en">
        <div class="skill-theory">
          <h3>Analogy: Smuggling Dangerous Items</h3>
          <p>When passing through security, the officer only checks the label on your suitcase that says "Clothes" (A <code>.png</code> file). However, they don't inspect the actual contents.</p>
          <p>You can upload a malicious script (A <code>.php</code> file) by manipulating its extension, and then execute remote commands.</p>
        </div>
      </div>
      <div class="lab-card" id="lab_upload_1">
        <div class="lab-header">
          <span class="lab-badge practitioner lang-id">Menengah</span><span class="lab-badge practitioner lang-en">Intermediate</span>
          <span class="lab-status unsolved" id="status_upload_1"></span>
        </div>
        <div class="lab-body">
          <h4 class="lang-id">Lab: Mengunggah Skrip Berbahaya</h4><h4 class="lang-en">Lab: Uploading a Malicious Script</h4>
          <p class="lang-id">Ubah ekstensi file Anda menjadi <code>.php</code> agar server mengeksekusinya sebagai program.</p>
          <p class="lang-en">Change your file extension to <code>.php</code> so the server executes it as a program.</p>
          <button class="btn-access lang-id" onclick="openLab('upload_1')">Akses Lab</button>
          <button class="btn-access lang-en" onclick="openLab('upload_1')">Access Lab</button>
        </div>
      </div>
    </div>
"""

start_idx = html.find('<!-- WEB 101 -->')
end_idx = html.find('</div>\n</main>')
if start_idx != -1 and end_idx != -1:
    html = html[:start_idx] + new_sections + '\n  ' + html[end_idx:]

# 4. Remove emojis from JS modal definitions and add language classes
html = html.replace('<h4>💡 Cara Hack (Untuk Pemula):</h4>', '<h4>Petunjuk Teknis / Technical Hint:</h4>')
html = html.replace('Pesan dari pacar: Jangan lupa jemput!', 'Pesan biasa / Normal message.')
html = html.replace('🍔', '').replace('👮‍♂️', '').replace('📌', '').replace('📝', '').replace('🤖', '').replace('📦', '').replace('🧐', '').replace('🚪', '').replace('🏨', '').replace('🗣️', '').replace('🧳', '').replace('💡', '')

# 5. Fix Javascript so that renderDashboard formats string cleanly
dashboard_js = """
function renderDashboard() {
  const grid = document.getElementById('dashboardGrid');
  let html = '';
  topics.forEach(t => {
    if (t.id === 'home' || t.id === 'web101') return;
    let titleHtml = t.label;
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
        <div style="color:var(--text3); font-size:13px; margin: 8px 0;">${t.labsCount} Lab(s)</div>
        <div class="progress-ring"><div class="fill" style="width: ${(t.solvedCount/t.labsCount)*100}%"></div></div>
        <div style="font-size:12px; color:var(--text2); text-align:right;">${t.solvedCount} / ${t.labsCount} Solved</div>
      </div>
    `;
  });
  grid.innerHTML = html;
}
"""
html = re.sub(r'function renderDashboard\(\) \{.*?\}', dashboard_js, html, flags=re.DOTALL)

with open('C:/BugBounty/bugbounty_tutorial.html', 'w', encoding='utf-8') as f:
    f.write(html)