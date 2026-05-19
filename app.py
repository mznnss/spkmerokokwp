import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================
# 1. PENGATURAN HALAMAN & INTERFACE (BAB 3)
# ==========================================
st.set_page_config(page_title="SPK Kecanduan Merokok - SAW", layout="wide")

st.title("🚬 Sistem Pendukung Keputusan Penentuan Faktor Penyebab Kecanduan Merokok")
st.markdown("### Pendekatan Metode Simple Additive Weighting (SAW) Berbasis Web")
st.write("Aplikasi ini menghitung bobot kriteria secara otomatis dari data kuesioner dan menentukan faktor yang paling dominan.")

st.sidebar.header("📁 Menu Unggah & Filter")
uploaded_file = st.sidebar.file_uploader("Unggah File CSV Kuesioner (Form Responses)", type=["csv"])

# Define Kriteria sesuai dokumen utama
kriteria_info = {
    'C1': {'nama': 'Psikologis', 'type': 'benefit'},
    'C2': {'nama': 'Lingkungan', 'type': 'benefit'},
    'C3': {'nama': 'Kebiasaan', 'type': 'benefit'},
    'C4': {'nama': 'Ekonomi', 'type': 'benefit'},
    'C5': {'nama': 'Ketergantungan', 'type': 'benefit'},
    'C6': {'nama': 'Pengetahuan', 'type': 'cost'}
}

# ==========================================
# 2. PROSES UTAMA (METODOLOGI & PERHITUNGAN)
# ==========================================
if uploaded_file is not None:
    try:
        # Membaca data kuesioner
        df = pd.read_csv(uploaded_file)
        
        st.success("✅ Berhasil memuat data kuesioner!")
        
        with st.expander("👀 Lihat Data Mentah Kuesioner"):
            st.dataframe(df.head())

        # --- LANGKAH 1: PREPROCESSING & MAPPING ---
        # Catatan: Sesuaikan nama kolom di bawah ini dengan nama kolom di CSV kuesioner Anda
        # Di sini diasumsikan Anda melakukan rename kolom/mengambil kolom kriteria langsung
        
        st.subheader("📊 1. Hasil Perhitungan Bobot Rata-Rata Kuesioner Global")
        
        # Simulasi/Kalkulasi ekstraksi skor kriteria dari kuesioner (Skala 1-5 atau 1-100)
        # Sebagai contoh praktis, kita buat dummy agregasi jika struktur kolom persis kriteria
        list_kriteria = [info['nama'] for info in kriteria_info.values()]
        
        # Mencari kolom yang mengandung nama kriteria
        kolom_valid = []
        for kat in list_kriteria:
            match = [col for col in df.columns if kat.lower() in col.lower()]
            if match:
                kolom_valid.append(match[0])
        
        if len(kolom_valid) < 6:
            # FALLBACK SYSTEM (BAB 4): Jika nama kolom tidak cocok, gunakan data sampel default agar web tidak crash
            st.warning("⚠️ Kolom kuesioner tidak terdeteksi otomatis secara sempurna. Mengaktifkan Fallback System (Data Sampel Makalah)...")
            skor_rata_rata = np.array([3.5, 4.2, 3.8, 4.5, 3.0, 2.5]) # Skala 1-5 dari kuesioner
        else:
            # Menghitung rata-rata skor dari jawaban responden langsung
            skor_rata_rata = df[kolom_valid].mean().values

        # Normalisasi Bobot agar Total = 1.00 (100%) sesuai standar SAW Makalah Laptop
        total_skor = sum(skor_rata_rata)
        bobot_w = [round(skor / total_skor, 3) for skor in skor_rata_rata]
        
        # Tampilkan Tabel Bobot Hasil Kuesioner
        df_bobot = pd.DataFrame({
            'Kode': kriteria_info.keys(),
            'Kriteria': list_kriteria,
            'Jenis': [info['type'].upper() for info in kriteria_info.values()],
            'Nilai Bobot Rata-rata (Wj)': bobot_w
        })
        st.table(df_bobot)

        # --- LANGKAH 2 & 3: MATRIKS KEPUTUSAN & NORMALISASI (R) ---
        st.subheader("🔢 2. Matriks Keputusan & Normalisasi SAW (Real-time)")
        
        # Membuat contoh matriks keputusan berbasis agregasi data responden (atau per sampel subjek)
        # Untuk visualisasi global, kita lakukan perhitungan perankingan Kriteria/Faktor
        
        # Hitung Nilai SAW Global
        nilai_saw_akhir = []
        for idx, (kode, info) in enumerate(kriteria_info.items()):
            # Logika Normalisasi sederhana untuk perankingan faktor global:
            if info['type'] == 'benefit':
                # Nilai normalisasi rata-rata kriteria terhadap skor maksimum kriteria benefit
                r_ij = skor_rata_rata[idx] / max(skor_rata_rata[:5]) 
            else:
                # Nilai normalisasi untuk kriteria cost
                r_ij = min(skor_rata_rata) / skor_rata_rata[idx]
                
            # Preferensi V_i = W_j * R_ij
            v_i = round(bobot_w[idx] * r_ij, 3)
            nilai_saw_akhir.append(v_i)

        # --- LANGKAH 4: PERANKINGAN AKHIR (BAB 4) ---
        st.subheader("🏆 3. Hasil Perankingan Faktor Paling Dominan")
        
        df_hasil = pd.DataFrame({
            'Faktor Penyebab (Kriteria)': list_kriteria,
            'Nilai SAW Akumulatif': nilai_saw_akhir
        }).sort_values(by='Nilai SAW Akumulatif', ascending=False).reset_index(drop=True)
        
        df_hasil['Peringkat Akhir'] = df_hasil.index + 1
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"#### 🎉 Faktor Paling Dominan: **{df_hasil.iloc[0]['Faktor Penyebab (Kriteria)']}**")
            st.dataframe(df_hasil[['Peringkat Akhir', 'Faktor Penyebab (Kriteria)', 'Nilai SAW Akumulatif']])
            
        with col2:
            # Visualisasi Data Gambar (Bab 4) menggunakan Plotly Express interaktif
            fig = px.bar(df_hasil, x='Faktor Penyebab (Kriteria)', y='Nilai SAW Akumulatif',
                         title="Grafik Urutan Faktor Penyebab Kecanduan Merokok",
                         labels={'Nilai SAW Akumulatif': 'Nilai Preferensi SAW'},
                         color='Nilai SAW Akumulatif', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file: {e}")
        st.info("💡 Pastikan file CSV yang Anda unggah berformat standar hasil unduhan Google Form.")

else:
    # Tampilan awal jika file belum diunggah
    st.info("👋 Silakan unggah file CSV data kuesioner Anda pada sidebar di sebelah kiri untuk memulai kalkulasi.")
    
    # Menampilkan tabel kriteria default sistem
    st.markdown("#### Daftar Kriteria Sistem")
    df_default_kriteria = pd.DataFrame([
        {"Kode": k, "Kriteria": v["nama"], "Jenis Atribut": v["type"].upper()} for k, v in kriteria_info.items()
    ])
    st.table(df_default_kriteria)
