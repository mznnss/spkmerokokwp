# =============================================================================
PENJELASAN ARSITEKTUR KODE PROGRAM SPK WP ROKOK
UNTUK BAHAN SIDANG / LAPORAN

Secara teknis, kode program yang dibangun menggunakan Python dan Streamlit  ini terbagi menjadi 3 blok utama yang saling terintegrasi:

1. INISIALISASI & INPUT BOBOT KRITERIA (Sidebar UI)

---

* st.set_page_config():
Mengatur judul tab browser menjadi "SPK Pemilihan Rokok Unggulan - Warung Madura" dan menetapkan layout halaman menjadi 'wide' (lebar). Ini dilakukan agar tabel matriks kriteria C1 sampai C4 tidak terpotong saat dibaca di layar browser.
* w_rasa, w_harga, w_aroma, w_kemasan (Slider Input):
Bertindak sebagai panel kendali masukan (*input parameter adjustment*) bagi pengguna untuk menentukan nilai tingkat kepentingan awal kriteria (skala 1 - 5). Pergeseran nilai slider ini akan langsung memicu hitung ulang tanpa perlu memuat ulang halaman (*reload page*).



2. PROSES MEMBACA DATA & PREPROCESSING (Pandas Engine)

---

* pd.read_csv():
Berfungsi untuk membaca dataset kuesioner primer dari jalur bawaan (`Data customer rokok - Form Responses 1 (1).csv`) atau file CSV baru yang diunggah secara mandiri oleh pengguna melalui widget uploader di sidebar.
* Ekstraksi Frekuensi ke Numerik:
Mengubah data tanggapan kualitatif dari Google Form (teks alasan "Rasa", "Harga", dll.) menjadi bentuk angka numerik bilangan bulat (*integer*) dengan cara menghitung total akumulasi frekuensi kemunculan alasan tersebut untuk setiap alternatif merek rokok.
* X.replace(0, 1) [Zero-Value Fallback System]:
Bertindak sebagai komponen pengolahan awal (*preprocessing*) sekaligus *crash protection* untuk mendeteksi nilai frekuensi 0 dan mengonversinya secara otomatis menjadi skor minimal 1. Prosedur ini sangat krusial untuk mencegah terjadinya eror *runtime* matematika atau hasil 0 mutlak akibat operasi perkalian perpangkatan berderet pada metode WP.

3. DEKLARASI PERHITUNGAN INTI METODE WEIGHTED PRODUCT (WP)

---

Blok ini merupakan jantung pemrograman sistem (backend) yang mengeksekusi tahapan komputasi metode WP secara berurutan:

* Perbaikan Bobot Kriteria ($w_j$):
Sistem menormalisasikan bobot kepentingan awal dari slider (`w_awal / total_w`) sehingga total nilai seluruh bobot kriteria baru menghasilkan nilai mutlak sama dengan 1.00 atau 100% ($\sum w_j = 1,00$). Seluruh kriteria dialokasikan sebagai atribut keuntungan (*benefit*) sehingga pangkatnya bertanda positif (+).
* Perhitungan Vektor Kesesuaian ($S_i$):
Mengalikan seluruh elemen rating kriteria alternatif setelah masing-masing dipangkatkan secara eksponensial dengan nilai bobot perbaikannya secara *real-time* menggunakan skrip iterasi *looping* Python.
[Rumus: $S_i = (C1^{w_1}) \times (C2^{w_2}) \times (C3^{w_3}) \times (C4^{w_4})$]
* Perhitungan Vektor Preferensi Relatif ($V_i$):
Membagi skor kesesuaian Vektor $S_i$ masing-masing alternatif dengan total akumulasi seluruh nilai Vektor $S$ ($\sum S$) untuk menghasilkan nilai desimal akhir di dalam rentang rentang 0 sampai 1 sebagai dasar penentu urutan peringkat (*descending ranking*).
[Rumus: $V_i = \frac{S_i}{\sum S_j}$]

4. KOMPONEN ANTARMUKA INTERAKTIF (User Interface Streamlit)

---

Bagian front-end yang menangani interaksi langsung dengan pengguna:

* st.tabs():
Membagi tata letak halaman web menjadi 3 tab utama secara rapi, yaitu "📊 Data Kuesioner & Matriks", "🧮 Proses Perhitungan WP" (memperlihatkan transparansi hitungan rumus manual), dan "🏆 Hasil Rekomendasi".
* st.data_editor():
Merender komponen tabel matriks keputusan awal hasil kuesioner. Fitur dinamis ini memperbolehkan pengguna (pemilik Warung Madura atau dosen penguji) untuk menyimulasikan modifikasi data frekuensi kinerja alternatif secara langsung di browser.
* st.success():
Menampilkan kotak kesimpulan berwarna hijau yang menonjolkan nama alternatif pemenang utama (misal: **Sampoerna Mild**) beserta skor akhir preferensinya secara otomatis sebagai produk yang paling direkomendasikan untuk ditambah pasokannya (*restock*).
* px.bar() & st.plotly_chart():
Memanfaatkan pustaka Plotly Express untuk memproduksi visualisasi grafik batang horizontal (*horizontal bar chart*) yang dinamis, lengkap dengan fitur kotak informasi (*hover data tooltip*) saat kursor diarahkan ke batang grafik.
* st.download_button():
Menyediakan widget tombol aksi untuk mengekspor data tabel final perankingan merek rokok ke dalam format spreadsheet dokumen CSV eksternal (`Rekomendasi_Stok_Warung_Madura.csv`).

=============================================================================

* Kesimpulan Akhir: Seluruh alur fungsi dalam kode ini bersifat reaktif.
Jika ada penyesuaian slider bobot kriteria oleh pengguna atau perubahan angka
di tabel data_editor, seluruh kalkulator matematika WP, grafik Plotly, dan
kesimpulan widget success akan langsung memperbarui tampilannya secara otomatis
dalam hitungan milidetik tanpa perlu memuat ulang halaman browser.
=============================================================================
