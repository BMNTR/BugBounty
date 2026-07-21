import re

with open('C:/BugBounty/bugbounty_tutorial.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. UPDATE SIDEBAR
new_sidebar = """
      <div class="sidebar-label">PENGANTAR</div>
      <a href="#web101" class="sidebar-item" id="nav-web101">Web 101: Dari Nol</a>
      <a href="#dashboard" class="sidebar-item active" id="nav-dashboard">Dashboard</a>
      
      <div class="sidebar-label">LABS (PRAKTEK)</div>
      <a href="#sqli" class="sidebar-item" id="nav-sqli">1. SQL Injection <span class="status-icon" id="sidebar_status_sqli_1"></span></a>
      <a href="#xss" class="sidebar-item" id="nav-xss">2. Cross-Site Scripting <span class="status-icon" id="sidebar_status_xss_1"></span></a>
      <a href="#csrf" class="sidebar-item" id="nav-csrf">3. CSRF <span class="status-icon" id="sidebar_status_csrf_1"></span></a>
      <a href="#os-command" class="sidebar-item" id="nav-os-command">4. OS Command <span class="status-icon" id="sidebar_status_osc_1"></span></a>
      <a href="#ssrf" class="sidebar-item" id="nav-ssrf">5. SSRF <span class="status-icon" id="sidebar_status_ssrf_1"></span></a>
      <a href="#auth" class="sidebar-item" id="nav-auth">6. Auth Bypass <span class="status-icon" id="sidebar_status_auth_1"></span></a>
      <a href="#path-traversal" class="sidebar-item" id="nav-path-traversal">7. Path Traversal <span class="status-icon" id="sidebar_status_path_1"></span></a>
      <a href="#idor" class="sidebar-item" id="nav-idor">8. IDOR <span class="status-icon" id="sidebar_status_idor_1"></span></a>
      <a href="#info-disc" class="sidebar-item" id="nav-info-disc">9. Info Disclosure <span class="status-icon" id="sidebar_status_info_1"></span></a>
      <a href="#file-upload" class="sidebar-item" id="nav-file-upload">10. File Upload <span class="status-icon" id="sidebar_status_upload_1"></span></a>
"""
# Replace sidebar links
html = re.sub(r'<div class="sidebar-label">TOTAL PROGRESS.*?<a href="#auth".*?</a>', new_sidebar, html, flags=re.DOTALL)

# 2. CREATE NEW SECTIONS (Web 101 + 10 Labs)
new_sections = """
    <!-- WEB 101 -->
    <div class="section" id="web101">
      <h2>Web 101: Internet Itu Apa Sih?</h2>
      <p>Buat lo yang bener-bener baru pegang komputer dan pengen jadi *hacker*, santai aja! Kita akan pelajari semuanya pakai analogi restoran.</p>
      <div class="skill-theory">
        <h3>Bayangkan Internet Sebagai Sebuah Restoran 🍔</h3>
        <ul>
          <li><strong>Client (Browser lo):</strong> Ini adalah <strong>Pelanggan</strong>. Lo duduk di meja dan pengen pesen makan (minta halaman web).</li>
          <li><strong>Server:</strong> Ini adalah <strong>Pelayan dan Dapur</strong>. Mereka yang nerima pesenan lo, masakin, dan nganterin makanannya balik ke meja lo.</li>
          <li><strong>Database:</strong> Ini adalah <strong>Gudang Bahan Makanan & Buku Resep Rahasia</strong> di belakang restoran. Isinya username, password, dan data penting lainnya.</li>
          <li><strong>HTML & CSS:</strong> Ini adalah <strong>Dekorasi Restoran & Buku Menu</strong>. Cuma tampilan visual biar lo bisa baca.</li>
          <li><strong>JavaScript (JS):</strong> Ini adalah <strong>Pelayan Robot di Meja Lo</strong>. Dia bisa ngerjain tugas kecil langsung di meja lo tanpa harus bolak-balik ke dapur (Server).</li>
          <li><strong>Request (HTTP):</strong> Ini adalah <strong>Kertas Pesanan</strong> yang lo tulis dan kasih ke pelayan.</li>
          <li><strong>Response (HTTP):</strong> Ini adalah <strong>Makanan</strong> (Halaman Web) yang dianterin pelayan ke meja lo.</li>
        </ul>
        <br>
        <h3>Jadi "Hacking" itu apa?</h3>
        <p>Hacking itu pada dasarnya adalah <strong>mencari celah aturan di restoran tersebut</strong>. Misalnya, di menu nggak ada tulisan "Boleh masuk dapur", tapi lo iseng masuk aja ke dapur. Kalau restorannya nggak dikunci, lo berhasil nge-hack!</p>
      </div>
    </div>

    <!-- DASHBOARD -->
    <div class="section active" id="dashboard">
      <h2>Welcome to Bug Bounty Academy</h2>
      <p>Kerjakan lab di bawah ini untuk belajar *hacking* selangkah demi selangkah. Jangan lupa baca teorinya dulu!</p>
      <div class="dashboard-grid" id="dashboardGrid">
        <!-- Injected via JS -->
      </div>
    </div>

    <!-- SQLI -->
    <div class="section" id="sqli">
      <h2>1. SQL Injection (SQLi)</h2>
      <div class="skill-theory">
        <h3>Analogi: Menipu Satpam dengan KTP Aneh 👮‍♂️</h3>
        <p>Bayangin lo mau masuk klub malam elit. Satpam nanya, "Namanya siapa?". Aturannya, satpam bakal nyari nama lo di buku tamu. Kalau ada, lo boleh masuk.</p>
        <p>Tapi, gimana kalau lo jawab: <strong>"Nama gw Budi, ATAU gw adalah bos pemilik klub ini"</strong>?</p>
        <p>Kalau si satpam polos (aplikasinya rentan), dia bakal ngecek: "Oh, namanya Budi, eh atau dia bos pemilik klub? Ya udah masuk aja bos!". Lo berhasil masuk tanpa password (tanpa nama lo ada di daftar tamu) karena lo ngasih <strong>perintah logika tambahan</strong> ke pertanyaan satpam.</p>
        <h4>Cara Hack (Untuk Pemula):</h4>
        <ul>
          <li>Di form login (kolom username), coba masukin tanda petik tunggal <code>'</code>. Kalau muncul <em>error</em> aneh, artinya lo bisa ngomong langsung ke Satpam (Database).</li>
          <li>Masukin: <code>' OR 1=1--</code>. Penjelasannya: Tanda petik <code>'</code> buat nutup pertanyaan satpam. <code>OR 1=1</code> artinya "Atau 1 sama dengan 1" (yang mana selalu benar!). <code>--</code> artinya "Abaikan sisa pertanyaan satpam di belakang".</li>
        </ul>
      </div>
      <div class="lab-card" id="lab_sqli_1">
        <div class="lab-header">
          <span class="lab-badge apprentice">Pemula (Apprentice)</span>
          <span class="lab-status unsolved" id="status_sqli_1">[ ] Belum Selesai</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Login bypass menggunakan SQL Injection</h4>
          <p>Login ke dalam aplikasi sebagai <code>administrator</code> tanpa mengetahui passwordnya menggunakan trik KTP aneh di atas!</p>
          <button class="btn-access" onclick="openLab('sqli_1')">Mulai Lab</button>
        </div>
      </div>
    </div>

    <!-- XSS -->
    <div class="section" id="xss">
      <h2>2. Cross-Site Scripting (XSS)</h2>
      <div class="skill-theory">
        <h3>Analogi: Menempel Pengumuman Hipnotis di Mading Sekolah 📌</h3>
        <p>Bayangin ada mading (papan pengumuman) di sekolah lo yang siapa aja bebas nulis pesan. Lo nulis: <em>"Hai semua, ini Budi"</em>. Semua yang lewat baca pesan itu.</p>
        <p>Gimana kalau lo iseng nulis instruksi hipnotis: <strong>"Hai semua, siapapun yang baca tulisan ini, tampar wajah kalian sendiri sekarang!"</strong></p>
        <p>Di dunia komputer, mading itu adalah <em>kolom komentar</em> atau <em>fitur pencarian</em>. Dan tulisan hipnotis itu adalah <strong>JavaScript</strong>. Saat orang lain ngebuka halaman web itu, browser mereka bakal terhipnotis dan ngejalanin JavaScript buatan lo!</p>
        <h4>Cara Hack (Untuk Pemula):</h4>
        <ul>
          <li>Kode ajaib JavaScript paling dasar buat ngetes: <code>&lt;script&gt;alert(1)&lt;/script&gt;</code></li>
          <li>Kalo lo masukin kode itu ke kolom pencarian dan tiba-tiba muncul kotak <em>popup</em> kecil berisi angka "1" di layar, BOOM! Lo berhasil menghipnotis webnya!</li>
        </ul>
      </div>
      <div class="lab-card" id="lab_xss_1">
        <div class="lab-header">
          <span class="lab-badge apprentice">Pemula</span>
          <span class="lab-status unsolved" id="status_xss_1">[ ] Belum Selesai</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Memunculkan popup Alert</h4>
          <p>Coba masukin kode ajaib di atas ke dalam fitur pencarian, lalu klik Search. Kalau berhasil memunculkan popup, lo menang!</p>
          <button class="btn-access" onclick="openLab('xss_1')">Mulai Lab</button>
        </div>
      </div>
    </div>

    <!-- CSRF -->
    <div class="section" id="csrf">
      <h2>3. Cross-Site Request Forgery (CSRF)</h2>
      <div class="skill-theory">
        <h3>Analogi: Memalsukan Surat Kuasa ke Teller Bank 📝</h3>
        <p>Bayangin lo lagi antre di bank. Lo udah ngasih KTP dan buka tabungan. Terus ada copet yang diem-diem nyelipin surat di tumpukan dokumen lo yang isinya: <em>"Tolong transfer semua uang gw ke rekening si Copet"</em>.</p>
        <p>Si Teller bank (Server) ngeliat lo udah kasih KTP asli (udah Login/Punya Cookie), jadi dia percaya aja dan ngejalanin surat transfer itu tanpa konfirmasi ulang ke lo.</p>
        <p>Itulah CSRF! Hacker bikin link palsu. Kalau korban (yang kebetulan lagi login ke Facebook/Bank) ngeklik link itu, browser korban bakal ngirim perintah (kayak ganti password atau transfer uang) tanpa disadari si korban.</p>
      </div>
      <div class="lab-card" id="lab_csrf_1">
        <div class="lab-header">
          <span class="lab-badge practitioner">Menengah</span>
          <span class="lab-status unsolved" id="status_csrf_1">[ ] Belum Selesai</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Ubah Email Korban Tanpa Sadar</h4>
          <p>Tugas lo: bikin kode HTML yang bakal otomatis nge-submit form ganti email pas halamannya dibuka, trus jalanin kode itu.</p>
          <button class="btn-access" onclick="openLab('csrf_1')">Mulai Lab</button>
        </div>
      </div>
    </div>

    <!-- OS COMMAND -->
    <div class="section" id="os-command">
      <h2>4. OS Command Injection</h2>
      <div class="skill-theory">
        <h3>Analogi: Menyelipkan Pesan Rahasia ke Robot Pelayan 🤖</h3>
        <p>Di restoran tadi, ada Robot Pelayan. Lo ngasih kertas perintah: <em>"Tolong cek stok Beras"</em>. Robotnya nurut.</p>
        <p>Gimana kalau lo nulis di kertas itu: <strong>"Tolong cek stok Beras DAN DAN (&&) kasih tau gw rahasia resep krabby patty"</strong>?</p>
        <p>Kalau robotnya bego, dia bakal ngerjain tugas pertama, trus lanjut ngerjain tugas kedua yang sebenernya perintah terlarang dari lo! Di dunia nyata, karakter pemisah perintah ini adalah tanda titik koma <code>;</code>, pipa <code>|</code>, atau <code>&&</code>.</p>
        <h4>Cara Hack (Untuk Pemula):</h4>
        <ul>
          <li>Misal ada kolom input Cek Stok Toko: <code>1</code></li>
          <li>Tambahkan pipa <code>|</code> lalu perintah sistem (kayak nanya ke sistem Windows "Siapa gw?"): <code>1 | whoami</code></li>
        </ul>
      </div>
      <div class="lab-card" id="lab_osc_1">
        <div class="lab-header">
          <span class="lab-badge apprentice">Pemula</span>
          <span class="lab-status unsolved" id="status_osc_1">[ ] Belum Selesai</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Tanya Identitas Sistem</h4>
          <p>Di fitur Cek Stok, selipkan perintah <code>whoami</code> (Siapa Saya?) ke server untuk melihat identitas pengguna sistem operasinya.</p>
          <button class="btn-access" onclick="openLab('osc_1')">Mulai Lab</button>
        </div>
      </div>
    </div>

    <!-- SSRF -->
    <div class="section" id="ssrf">
      <h2>5. Server-Side Request Forgery (SSRF)</h2>
      <div class="skill-theory">
        <h3>Analogi: Nipu Kurir Buat Ngambil Paket Rahasia Bos 📦</h3>
        <p>Lo pengen ngeliat dokumen rahasia di brankas Bos di ruang belakang restoran, tapi lo ditahan satpam di depan.</p>
        <p>Terus lo ngeliat ada Kurir Restoran yang tugasnya ngambilin barang apa aja buat pelanggan. Lo suruh Kurir: <em>"Tolong ambilin pesanan di Ruang Brankas Bos ya"</em>.</p>
        <p>Satpam ngeliat si Kurir (orang dalam) masuk, jadi dia biarin aja! Terus Kurir bawa dokumen rahasia itu ke lo. Itulah SSRF! Lo nyuruh Server buat ngunjungin <em>link</em> lokal (misal: <code>http://localhost/admin</code>) yang cuma bisa diakses oleh orang dalam.</p>
      </div>
      <div class="lab-card" id="lab_ssrf_1">
        <div class="lab-header">
          <span class="lab-badge apprentice">Pemula</span>
          <span class="lab-status unsolved" id="status_ssrf_1">[ ] Belum Selesai</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Serang Admin Panel dari Dalam</h4>
          <p>Suruh webnya (lewat fitur cek stok yang masukin URL) buat ngunjungin <code>http://localhost/admin/delete?username=carlos</code> untuk ngehapus akun Carlos!</p>
          <button class="btn-access" onclick="openLab('ssrf_1')">Mulai Lab</button>
        </div>
      </div>
    </div>

    <!-- AUTH BYPASS -->
    <div class="section" id="auth">
      <h2>6. Authentication Bypass</h2>
      <div class="skill-theory">
        <h3>Analogi: Nebak Kata Sandi dari Wajah Satpam 🧐</h3>
        <p>Lo nyoba nebak password brankas restoran. Lo masukin "Kucing". Satpam merespon dalam 1 detik: "Salah!".</p>
        <p>Lo masukin "Admin". Satpam butuh waktu 5 detik buat mikir, trus keringetan, baru bilang: "Salah password!".</p>
        <p>Dari kelakuan satpam itu, lo tau: OH, akun "Admin" itu ADA (makanya dia ngeceknya lama/keringetan), gw cuma tinggal nebak passwordnya aja! Ini namanya <strong>Username Enumeration</strong> (menebak username dari pesan error atau waktu respon yang beda).</p>
      </div>
      <div class="lab-card" id="lab_auth_1">
        <div class="lab-header">
          <span class="lab-badge practitioner">Menengah</span>
          <span class="lab-status unsolved" id="status_auth_1">[ ] Belum Selesai</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Tebak Username dari Respon Error</h4>
          <p>Pahami respon server (misal pesan error yang berbeda) untuk mencari tahu username apa yang beneran terdaftar di sistem.</p>
          <button class="btn-access" onclick="openLab('auth_1')">Mulai Lab</button>
        </div>
      </div>
    </div>

    <!-- PATH TRAVERSAL -->
    <div class="section" id="path-traversal">
      <h2>7. Path Traversal (Directory Traversal)</h2>
      <div class="skill-theory">
        <h3>Analogi: Mundur dari Ruang Tunggu ke Ruang Arsip Rahasia 🚪</h3>
        <p>Di restoran, pelayan bilang: "Silakan ambil foto menu di folder <code>/Tamu/Menu/</code>". Kalau lo mau liat gambar ayam, lo bilang: "Kasih gw file <code>ayam.jpg</code>".</p>
        <p>Gimana kalau lo pinter, trus lo bilang: "Kasih gw file <strong>Mundur 2 Langkah, terus masuk ke Ruang Bos, file Rahasia.txt</strong>". Di bahasa komputer, "Mundur 1 Langkah" (Naik ke folder atas) itu ditulis pakai kode titik-titik-garis-miring: <code>../</code></p>
        <p>Jadi lo minta: <code>../../../Windows/System32/drivers/etc/hosts</code> atau di Linux <code>../../../etc/passwd</code> (File super rahasia yang isinya daftar pengguna).</p>
        <h4>Cara Hack:</h4>
        <p>Kalo ada link kayak <code>?file=gambar.png</code>, ubah jadi <code>?file=../../../../etc/passwd</code>.</p>
      </div>
      <div class="lab-card" id="lab_path_1">
        <div class="lab-header">
          <span class="lab-badge apprentice">Pemula</span>
          <span class="lab-status unsolved" id="status_path_1">[ ] Belum Selesai</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Baca File Rahasia Komputer</h4>
          <p>Ubah parameter nama gambar produk untuk mundur ke belakang (folder root) dan baca isi file rahasia <code>/etc/passwd</code>.</p>
          <button class="btn-access" onclick="openLab('path_1')">Mulai Lab</button>
        </div>
      </div>
    </div>

    <!-- IDOR -->
    <div class="section" id="idor">
      <h2>8. IDOR (Insecure Direct Object Reference)</h2>
      <div class="skill-theory">
        <h3>Analogi: Ganti Nomor Kamar Hotel di Kunci Pintar 🏨</h3>
        <p>Lo lagi nginep di hotel. Kasir ngasih lo kunci kartu digital buat buka kamar nomor <strong>101</strong>.</p>
        <p>Karena kuncinya abal-abal, lo iseng nyambungin kuncinya ke laptop, dan lo ganti angka `101` jadi `102`. Terus lo tap ke pintu tetangga, EH KEBONGKAR!</p>
        <p>Itulah IDOR! Server nggak ngecek <strong>apakah si User benar-benar berhak ngeliat data nomor 102</strong>, dia cuma mikir "Oh dia minta data 102, nih gw kasih". Sering banget kejadian di kuitansi belanja (URL: <code>?receipt_id=100</code> diubah jadi <code>101</code>).</p>
      </div>
      <div class="lab-card" id="lab_idor_1">
        <div class="lab-header">
          <span class="lab-badge apprentice">Pemula</span>
          <span class="lab-status unsolved" id="status_idor_1">[ ] Belum Selesai</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Ngintip Chat Pengguna Lain</h4>
          <p>Lo lagi ngeliat history chat lo sendiri di URL parameter <code>?user_id=2</code>. Coba ganti angka itu buat ngintip rahasia punya user nomor 1 (carlos).</p>
          <button class="btn-access" onclick="openLab('idor_1')">Mulai Lab</button>
        </div>
      </div>
    </div>

    <!-- INFO DISCLOSURE -->
    <div class="section" id="info-disc">
      <h2>9. Information Disclosure</h2>
      <div class="skill-theory">
        <h3>Analogi: Kasir Ember yang Suka Keceplosan 🗣️</h3>
        <p>Lo tanya ke pelayan: "Kopi ini pakai gula aren ya?". Pelayan yang polos dan ember ini ngejawab: "Bukan mas, ini gula biasa. Wah kalau gula aren mah resep rahasianya disimpen di brankas passwordnya 123456!".</p>
        <p>Sistem kadang terlalu berisik ngasih pesan Error yang kepanjangan. Saat terjadi <em>error</em>, web bukannya ngomong "Maaf ada gangguan", eh malah nge-print seluruh kode kotornya ke layar (misalnya nampilin <em>Stack Trace</em> atau komentar developer: <code><!-- password database: admin123 --></code>).</p>
      </div>
      <div class="lab-card" id="lab_info_1">
        <div class="lab-header">
          <span class="lab-badge apprentice">Pemula</span>
          <span class="lab-status unsolved" id="status_info_1">[ ] Belum Selesai</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Cari Rahasia Tersembunyi</h4>
          <p>Developer teledor meninggalkan kunci rahasia di dalam komentar kode HTML (View Source) atau di halaman dokumentasi web yang bocor. Tugas lo: temukan kuncinya.</p>
          <button class="btn-access" onclick="openLab('info_1')">Mulai Lab</button>
        </div>
      </div>
    </div>

    <!-- FILE UPLOAD -->
    <div class="section" id="file-upload">
      <h2>10. File Upload Vulnerability</h2>
      <div class="skill-theory">
        <h3>Analogi: Nyelundupin Bom Dalam Koper Baju 🧳</h3>
        <p>Waktu masuk bandara (Server), lo disuruh masukin tas berisi baju (Upload Foto Profile berformat <code>.png</code>). Petugas bandara nggak teliti, dia cuma ngecek stiker di koper "Oh ini baju", padahal isinya Bom Waktu (Script <code>.php</code> berbahaya)!</p>
        <p>Begitu bomnya masuk ke dalam bandara (tersimpan di server), lo tinggal neken remot kontrol (mengunjungi URL foto tersebut) untuk meledakkan servernya (mengambil alih komputernya)!</p>
      </div>
      <div class="lab-card" id="lab_upload_1">
        <div class="lab-header">
          <span class="lab-badge practitioner">Menengah</span>
          <span class="lab-status unsolved" id="status_upload_1">[ ] Belum Selesai</span>
        </div>
        <div class="lab-body">
          <h4>Lab: Upload Virus (Web Shell)</h4>
          <p>Fitur upload foto profil ini mengizinkan upload file berbahaya. Upload file berekstensi <code>.php</code> berisi script jahat, lalu jalankan script itu untuk mencuri password rahasia server.</p>
          <button class="btn-access" onclick="openLab('upload_1')">Mulai Lab</button>
        </div>
      </div>
    </div>
"""

# Extract the old sections and replace with the new ones.
start_idx = html.find('<!-- SQLI -->')
end_idx = html.find('</div>\n</main>')
if start_idx != -1 and end_idx != -1:
    html = html[:start_idx] + new_sections + '\n  ' + html[end_idx:]

with open('C:/BugBounty/bugbounty_tutorial.html', 'w', encoding='utf-8') as f:
    f.write(html)