=============================================================================
             PENJELASAN ARSITEKTUR KODE PROGRAM SPK SAW MEROKOK
                      UNTUK BAHAN SIDANG / LAPORAN
=============================================================================

Secara teknis, kode program yang dibangun menggunakan Python dan Streamlit 
ini terbagi menjadi 3 blok utama yang saling terintegrasi:

1. INISIALISASI & DATABASE TEMPORAL (Session State)
-----------------------------------------------------------------------------
* st.set_page_config(): 
  Mengatur judul tab browser menjadi "SPK SAW Merokok - UNPAM" dan menetapkan
  layout halaman menjadi 'wide' (lebar). Ini dilakukan agar tabel matriks 
  kriteria C1 sampai C9 tidak terpotong saat dibaca di layar browser.
  
* st.session_state.kuesioner_bobot_data: 
  Berperan sebagai database sementara di memori RAM lokal. Variabel ini 
  bertugas menampung ringkasan jawaban dari setiap pakar/penilai yang diinput
  melalui sidebar, sehingga data tidak hilang saat halaman web melakukan
  refresh otomatis (st.rerun()).


2. DEKLARASI CLASS CORE METODE SAW (SAWMethod)
-----------------------------------------------------------------------------
Blok ini merupakan jantung pemrograman sistem (backend) yang merujuk langsung
pada rumus matematika pada materi Sistem Pendukung Keputusan:

* Fungsi __init__ (Inisialisasi Objek):
  Menerima tiga parameter wajib: data matriks alternatif, vektor bobot 
  kuesioner (Wj), dan tipe atribut kriteria (benefit/cost).

* Fungsi normalize_matrix (Proses Pembentukan Matriks R):
  Melakukan perulangan (looping) pada setiap kolom kriteria untuk membagi 
  skala nilai berdasarkan karakteristiknya:
  - Jika KRITERIA BENEFIT (C1 - C7): Nilai riil sel akan dibagi dengan nilai
    tertinggi pada kolom tersebut. [Rumus: Rij = Xij / Max(Xij)]
  - Jika KRITERIA COST (C8 - C9): Nilai terendah pada kolom akan dibagi 
    dengan nilai riil sel alternatif tersebut. [Rumus: Rij = Min(Xij) / Xij]
  * Catatan: Penggunaan fungsi np.where() bertindak sebagai "proteksi 
    pengaman" agar program tidak mengalami error 'division by zero' jika ada
    data matriks yang bernilai 0.

* Fungsi calculate_scores (Perhitungan Preferensi Vi):
  Mengalikan baris nilai matriks yang sudah ternormalisasi (Rij) dengan vektor
  bobot kepentingan (Wj) secara horizontal memakai perintah perkalian matriks
  Pandas & NumPy. Hasil penjumlahan horizontal tersebut disimpan ke dalam 
  kolom baru bernama 'Score', kemudian diurutkan secara otomatis untuk 
  mendapatkan peringkat ('Rank'). [Rumus: Vi = Sigma(Wj * Rij)]


3. MODUL AGREGASI BOBOT OTOMATIS (Fallback System)
-----------------------------------------------------------------------------
Sistem ini mengimplementasikan logika penyaringan data adaptif berdasarkan 
ketersediaan sampel data pakar di lapangan:
* Kondisi Jika Ada Input Pakar: Program mengubah data teks skala Likert 
  menjadi angka numerik (1-5), mencari rata-rata nilai per kolom kriteria, 
  lalu membaginya dengan total keseluruhan rata-rata untuk menghasilkan 
  bobot relatif yang jumlah akhirnya mutlak 1.00 (100%).
* Kondisi Jika Input Kosong (Fallback): Jika kuesioner pakar belum diisi, 
  sistem otomatis mengaktifkan Fallback System dengan memuat konfigurasi 
  bobot standar Tugas Akhir yang sudah divalidasi, yaitu:
  [W = 0.15, 0.15, 0.12, 0.10, 0.08, 0.08, 0.07, 0.10, 0.15]


4. KOMPONEN ANTARMUKA INTERAKTIF (User Interface Streamlit)
-----------------------------------------------------------------------------
Bagian front-end yang menangani interaksi langsung dengan pengguna:
* st.data_editor(): Merender komponen tabel matriks keputusan alternatif 
  kelompok perokok (A1, A2, A3) secara dinamis. Fitur ini memperbolehkan 
  dosen penguji untuk mengubah langsung angka skor skala 1-100 di layar web.
* st.success(): Menampilkan kotak kesimpulan berwarna hijau yang secara 
  dinamis mencetak nama alternatif dengan nilai tertinggi beserta skor akhir 
  preferensinya secara real-time.
* px.bar(): Memanfaatkan pustaka Plotly Express untuk memproduksi grafik 
  batang (bar chart) interaktif berbasis data hasil peringkat metode SAW, 
  lengkap dengan visualisasi gradasi warna merah untuk mempertegas tingkat 
  kekritisan adiksi.

=============================================================================
* Kesimpulan Akhir: Seluruh alur fungsi dalam kode ini bersifat reaktif. 
Jika ada perubahan data pakar atau perubahan angka di tabel data_editor, 
seluruh grafik dan kesimpulan akan langsung berubah otomatis dalam hitungan 
milidetik tanpa perlu melakukan restart server.
=============================================================================
