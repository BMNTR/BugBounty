# Perbaikan Tampilan — Web Security Academy

Cara pakai: timpa (replace) 3 file ini di project kamu dengan file yang ada di folder ini,
lalu **hapus** `js/legacy.js` dari project kamu (sudah tidak dipakai lagi, dan sekarang
tidak ada file yang men-load-nya).

- `bugbounty_tutorial.html`
- `css/style.css`
- `js/engine.js`

File lain (`js/components.js`, `js/storage.js`, `data/topics/*.json`, `academy-backend/*`)
**tidak diubah** — tidak perlu ditimpa.

## Bug yang diperbaiki

1. **Ada tag `<style>` nyasar di baris pertama `css/style.css`.**
   File CSS itu murni CSS, tapi ada sisa tag HTML di paling atas. Akibatnya, rule
   reset `box-sizing: border-box` di baris itu jadi invalid dan diabaikan browser,
   sehingga padding di banyak elemen (card, input, dsb) ikut menambah lebar elemen
   alih-alih dipotong dari dalam — ini akar dari layout yang gampang berantakan/overflow.

2. **`js/legacy.js` adalah sistem lama yang masih ikut ke-load** bareng sistem baru
   (`engine.js` + `components.js`). Dia diam-diam menimpa `toggleTheme()` dan
   `closeLab()` dengan versi yang rusak/tidak lengkap, dan memanipulasi elemen HTML
   yang sudah tidak ada. File ini sudah dihapus dari HTML dan dari project.

3. **Tombol dark/light theme tidak benar-benar berfungsi** — kodenya set CSS variable
   lalu langsung `location.reload()`, jadi perubahan warnanya hilang lagi seketika.
   Sekarang toggle beneran pakai class `.light` dan tersimpan di `localStorage`
   (jadi persisten setelah refresh, tidak ada flash warna salah saat load).

4. **Tombol hamburger (mobile menu) tidak berfungsi** — dia memanggil `toggleSidebar()`
   yang ternyata cuma didefinisikan di `legacy.js` (poin #2). Di layar kecil sidebar
   di-set `display:none` tanpa cara membukanya lagi. Sekarang: di desktop tombol ini
   collapse/expand sidebar; di mobile sidebar jadi drawer dengan overlay gelap yang
   bisa ditutup dengan tap di luar drawer.

5. **`var(--font-mono)` dipakai di 21 tempat tapi variabel yang didefinisikan cuma
   `--mono`** — jadi font monospace diam-diam tidak kepakai di banyak label/kode.
   Ditambahkan alias `--font-mono` dan `--font-main` di `:root`.

6. **8 dari 10 topik di sidebar belum punya file JSON materinya** (`data/topics/`
   baru ada `sqli.json` dan `xss.json`). Sebelumnya ini menampilkan teks error
   merah yang jelek saat diklik. Sekarang menampilkan state "materi belum
   tersedia" yang rapi. Ini bukan perbaikan konten — materi untuk 8 topik itu
   masih perlu dibuat kalau mau tersedia beneran.

7. Dibersihkan juga CSS mati/sisa desain versi lama (dashboard grid, FAQ,
   glossary, tag, chain/flow lama, dsb.) yang sudah tidak dipakai sistem yang
   aktif sekarang, supaya file-nya lebih ringkas dan tidak gampang bentrok lagi
   ke depannya.

Semua perbaikan di atas sudah diuji langsung pakai browser otomatis (Playwright):
`box-sizing` sekarang benar `border-box`, toggle tema persisten setelah reload,
sidebar collapse di desktop & drawer di mobile terbukti berfungsi, dan state
"belum tersedia" tampil dengan benar untuk topik yang belum ada datanya.
