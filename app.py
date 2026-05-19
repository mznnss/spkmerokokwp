import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from typing import List

st.set_page_config(
    page_title="SPK SAW Merokok - UNPAM",
    page_icon="🚭",
    layout="wide"
)

# Struktur nama kolom kriteria C1 - C9 yang baku dan konsisten
KOLOM_KRITERIA = [
    "C1_Psikologis", "C2_Lingkungan", "C3_Kebiasaan", 
    "C4_Ketergantungan", "C5_Intensitas", "C6_Efek_Sosial", 
    "C7_Kondisi_Fisik", "C8_Ekonomi", "C9_Pengetahuan"
]

if 'kuesioner_bobot_data' not in st.session_state:
    st.session_state.kuesioner_bobot_data = pd.DataFrame(columns=["Nama Penilai"] + KOLOM_KRITERIA)

# =========================================================================
# CLASS MURNI METODE SAW (Sesuai Laporan Bab 2.2 & Bab 3.7)
# =========================================================================
class SAWMethod:
    def __init__(self, data: pd.DataFrame, weights: List[float], criteria_type: List[str]):
        self.data = data.copy()
        self.weights = np.array(weights)
        self.criteria_type = criteria_type
        self.normalized_data = None

    def normalize_matrix(self) -> pd.DataFrame:
        """Normalisasi matriks keputusan (R) [Sesuai Rumus Benefit & Cost Laporan]"""
        if self.normalized_data is not None:
            return self.normalized_data
            
        normalized_data = self.data.copy()
        # Loop mulai dari indeks 1 untuk melewati kolom nama Alternatif
        for i, col in enumerate(self.data.columns[1:]):  
            if self.criteria_type[i] == 'benefit':
                max_val = self.data[col].max()
                normalized_data[col] = np.where(max_val != 0, self.data[col] / max_val, 0)
            else: # cost
                min_val = self.data[col].min()
                normalized_data[col] = np.where(self.data[col] != 0, min_val / self.data[col], 0)
                
        self.normalized_data = normalized_data
        return normalized_data

    def calculate_scores(self) -> pd.DataFrame:
        """Menghitung Nilai Preferensi Akhir (Vi) & Perankingan"""
        self.normalize_matrix()
        criteria_columns = self.data.columns[1:]
        
        # Perkalian matriks R_ij dengan Vektor Bobot W_j
        weighted_scores = self.normalized_data[criteria_columns].astype(float) * self.weights
        self.normalized_data['Score'] = weighted_scores.sum(axis=1)
        self.normalized_data['Rank'] = self.normalized_data['Score'].rank(ascending=False, method='min').astype(int)
        return self.normalized_data

    def get_ranking(self) -> pd.DataFrame:
        scores_df = self.calculate_scores()
        alt_column = scores_df.columns[0]
        result = scores_df[[alt_column, 'Score', 'Rank']].sort_values('Rank')
        return result.rename(columns={alt_column: 'Alternatif'})

# =========================================================================
# ANTARMUKA WEB STREAMLIT
# =========================================================================
st.title("🚭 SPK Faktor Penyebab Kecanduan Merokok")
st.caption("Aplikasi Sistem Pendukung Keputusan Penentuan Faktor Risiko Dominan Menggunakan Metode SAW")
st.markdown("---")

# -------------------------------------------------------------------------
# SIDEBAR: PANEL FORM KUESIONER BOBOT PAKAR
# -------------------------------------------------------------------------
st.sidebar.title("🔌 Filter & Simulasi Bobot Pakar")
st.sidebar.markdown("Masukkan penilaian pakar untuk menentukan bobot kriteria ($W$).")

with st.sidebar.form(key="form_simulasi_bobot", clear_on_submit=True):
    nama_pakar = st.text_input("Nama Penilai/Pakar", value=f"Pakar {len(st.session_state.kuesioner_bobot_data) + 1}")
    options = ["Sangat Tidak Penting", "Tidak Penting", "Cukup Penting", "Penting", "Sangat Penting"]
    
    q1 = st.selectbox("C1. Tingkat Emosi/Stres (Psikologis)", options=options, index=3)
    q2 = st.selectbox("C2. Pengaruh Teman Sebaya (Lingkungan)", options=options, index=4)
    q3 = st.selectbox("C3. Efek Setelah Makan (Kebiasaan)", options=options, index=3)
    q4 = st.selectbox("C4. Ketergantungan Zat (Nikotin)", options=options, index=4)
    q5 = st.selectbox("C5. Jumlah Konsumsi Harian (Intensitas)", options=options, index=3)
    q6 = st.selectbox("C6. Gengsi/Sosial (Efek Sosial)", options=options, index=2)
    q7 = st.selectbox("C7. Mulut Terasa Pahit (Kondisi Fisik)", options=options, index=3)
    q8 = st.selectbox("C8. Harga Rokok Mahal (Ekonomi) [Cost]", options=options, index=2)
    q9 = st.selectbox("C9. Paham Dampak Kanker (Pengetahuan) [Cost]", options=options, index=1)
    
    submit_btn = st.form_submit_button(label="💾 Simpan & Filter Jawaban")
    
    if submit_btn:
        new_row = {
            "Nama Penilai": nama_pakar, 
            "C1_Psikologis": q1, "C2_Lingkungan": q2, "C3_Kebiasaan": q3,
            "C4_Ketergantungan": q4, "C5_Intensitas": q5, "C6_Efek_Sosial": q6, 
            "C7_Kondisi_Fisik": q7, "C8_Ekonomi": q8, "C9_Pengetahuan": q9
        }
        st.session_state.kuesioner_bobot_data = pd.concat([st.session_state.kuesioner_bobot_data, pd.DataFrame([new_row])], ignore_index=True)
        st.rerun()

if len(st.session_state.kuesioner_bobot_data) > 0:
    if st.sidebar.button("🗑️ Reset Semua Data Pakar"):
        st.session_state.kuesioner_bobot_data = pd.DataFrame(columns=["Nama Penilai"] + KOLOM_KRITERIA)
        st.rerun()

# -------------------------------------------------------------------------
# PROSES AGREGASI BOBOT OTOMATIS (FALLBACK SYSTEM SINKRON)
# -------------------------------------------------------------------------
nama_kriteria = ["Psikologis", "Lingkungan", "Kebiasaan", "Ketergantungan", "Intensitas", "Efek Sosial", "Kondisi Fisik", "Ekonomi", "Pengetahuan"]
criteria_type = ['benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'cost', 'cost']
mapping_likert = {"Sangat Tidak Penting": 1, "Tidak Penting": 2, "Cukup Penting": 3, "Penting": 4, "Sangat Penting": 5}

if not st.session_state.kuesioner_bobot_data.empty:
    st.subheader("📄 1. Hasil Pengumpulan Kuesioner Penilai (Form Simulasi)")
    st.dataframe(st.session_state.kuesioner_bobot_data, use_container_width=True)
    
    # Konversi string ke angka numerik secara aman
    df_bobot_numeric = st.session_state.kuesioner_bobot_data[KOLOM_KRITERIA].replace(mapping_likert).astype(float)
    
    # Perbaikan Filter Kolom: Dipetakan langsung secara rigid ke variabel urut Kriteria C1-C9
    raw_scores = [df_bobot_numeric[col].mean() for col in KOLOM_KRITERIA]
    total_raw = sum(raw_scores)
    weights = [score / total_raw if total_raw > 0 else 1/9 for score in raw_scores]
else:
    # Default bobot awal kuesioner UNPAM (Sesuai Laporan Bab 4.1, Total = 1.0)
    weights = [0.15, 0.15, 0.12, 0.10, 0.08, 0.08, 0.07, 0.10, 0.15]
    st.info("ℹ️ Belum ada data kuesioner pakar yang diisi. Menggunakan parameter bobot default kuesioner Tugas Akhir.")

# -------------------------------------------------------------------------
# 2. EVALUASI MATRIKS ALTERNATIF KELOMPOK PEROKOK
# -------------------------------------------------------------------------
st.subheader("📊 2. Matriks Keputusan Kelompok Perokok (Alternatif)")
st.markdown("Anda dapat menyesuaikan nilai matriks evaluasi (Skala 1-100) langsung pada tabel dinamis di bawah ini:")

default_alternatif = {
    'Alternatif': ['A1 (Perokok Ringan)', 'A2 (Perokok Sedang)', 'A3 (Perokok Berat)'],
    'C1 (Psikologis)': [60, 90, 80], 
    'C2 (Lingkungan)': [8, 16, 8], 
    'C3 (Kebiasaan)': [70, 90, 80],
    'C4 (Ketergantungan)': [50, 90, 60], 
    'C5 (Intensitas)': [70, 85, 90], 
    'C6 (Efek Sosial)': [80, 80, 90],
    'C7 (Kondisi Fisik)': [80, 85, 90], 
    'C8 (Ekonomi)': [80, 55, 35], 
    'C9 (Pengetahuan)': [85, 50, 25]
}
df_alternatif = pd.DataFrame(default_alternatif)
matrix_data = st.data_editor(df_alternatif, hide_index=True, use_container_width=True)

# -------------------------------------------------------------------------
# 3. PEMROSESAN ENGINE METODE SAW & OUTPUT VISUALISASI
# -------------------------------------------------------------------------
if matrix_data is not None:
    # Validasi Fallback System: Cegah error jikalau ada cell data editor diubah menjadi kosong
    if matrix_data.isnull().values.any():
        st.error("⚠️ Peringatan: Terdapat sel data yang kosong pada tabel matriks keputusan. Mohon isi semua nilai terlebih dahulu.")
    else:
        saw = SAWMethod(matrix_data, weights, criteria_type)
        
        col_layout1, col_layout2 = st.columns(2)
        
        with col_layout1:
            st.markdown("### 📋 Parameter & Vektor Bobot Akhir ($W_j$)")
            df_parameter = pd.DataFrame({
                "Kode": [f"C{i+1}" for i in range(9)],
                "Kriteria": nama_kriteria,
                "Tipe Atribut": saw.criteria_type,
                "Bobot Hasil Filter": saw.weights
            })
            st.dataframe(df_parameter, hide_index=True, use_container_width=True)
            
            st.markdown("### ⚙️ Matriks Hasil Normalisasi ($R$)")
            df_norm_res = saw.normalize_matrix()
            st.dataframe(df_norm_res.round(3), hide_index=True, use_container_width=True)

        with col_layout2:
            st.markdown("### 🏆 Hasil Perankingan Nilai Preferensi ($V_i$)")
            ranking = saw.get_ranking()
            st.dataframe(ranking.round(3), hide_index=True, use_container_width=True)
            
            best_alternative = ranking.iloc[0]['Alternatif']
            best_score = ranking.iloc[0]['Score']
            
            st.success(f"⭐ **KESIMPULAN METODE SAW:** Kategori **{best_alternative}** teridentifikasi sebagai kelompok paling rentan/kritis terhadap paparan adiksi dengan nilai preferensi akhir sebesar **{best_score:.3f}**")
            
            # Visualisasi Chart Bar interaktif dinamis menggunakan Plotly
            fig = px.bar(
                ranking, 
                x="Alternatif", 
                y="Score", 
                text_auto='.3f', 
                color="Score", 
                color_continuous_scale="Reds", 
                title="Grafik Hasil Perankingan Nilai Preferensi SAW"
            )
            fig.update_layout(title_x=0.25)
            st.plotly_chart(fig, use_container_width=True)
