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

# Inisialisasi session state dengan nama kolom terstandarisasi C1 - C9
if 'kuesioner_bobot_data' not in st.session_state:
    st.session_state.kuesioner_bobot_data = pd.DataFrame(columns=[
        "Nama Penilai", "C1_Psikologis", "C2_Lingkungan", "C3_Kebiasaan", 
        "C4_Ketergantungan", "C5_Intensitas", "C6_Efek_Sosial", 
        "C7_Kondisi_Fisik", "C8_Ekonomi", "C9_Pengetahuan"
    ])

# =========================================================================
# CLASS MURNI METODE SAW (Sesuai Modul Hal 1 & Makalah Bab 2.2)
# =========================================================================
class SAWMethod:
    def __init__(self, data: pd.DataFrame, weights: List[float], criteria_type: List[str]):
        self.data = data.copy()
        self.weights = np.array(weights)
        self.criteria_type = criteria_type
        self.normalized_data = None
        self.scores = None

    def normalize_matrix(self) -> pd.DataFrame:
        """Normalisasi matriks keputusan (R) [Sesuai Modul & Makalah]"""
        normalized_data = self.data.copy()
        for i, col in enumerate(self.data.columns[1:]):  # Skip kolom Alternatif
            if self.criteria_type[i] == 'benefit':
                max_val = self.data[col].max()
                if max_val == 0: 
                    normalized_data[col] = 0
                else:
                    normalized_data[col] = self.data[col] / max_val
            else: # cost
                min_val = self.data[col].min()
                normalized_data[col] = np.where(
                    self.data[col] != 0,
                    min_val / self.data[col],
                    0
                )
        self.normalized_data = normalized_data
        return normalized_data

    def calculate_scores(self) -> pd.DataFrame:
        """Hitung nilai preferensi akhir (Vi)"""
        if self.normalized_data is None:
            self.normalize_matrix()
        criteria_columns = self.normalized_data.columns[1:]
        weighted_scores = self.normalized_data[criteria_columns] * self.weights
        self.normalized_data['Score'] = weighted_scores.sum(axis=1)
        self.normalized_data['Rank'] = self.normalized_data['Score'].rank(ascending=False, method='min').astype(int)
        return self.normalized_data

    def get_ranking(self) -> pd.DataFrame:
        if self.scores is None:
            self.scores = self.calculate_scores()
        alt_column = self.scores.columns[0]
        result = self.scores[[alt_column, 'Score', 'Rank']].sort_values('Rank')
        result = result.rename(columns={alt_column: 'Alternatif'})
        return result

# =========================================================================
# INTERMUKA WEB STREAMLIT (Sesuai Standar Aplikasi Web UNPAM)
# =========================================================================
st.title("🚭 SPK Faktor Penyebab Kecanduan Merokok")
st.caption("Modul Terintegrasi: Filter Bobot Kuesioner Interaktif & Engine Perhitungan SAW Ganda (Benefit & Cost)")
st.markdown("---")

# -------------------------------------------------------------------------
# SIDEBAR: PANEL FORM KUESIONER BOBOT
# -------------------------------------------------------------------------
st.sidebar.title("🔌 Filter & Simulasi Bobot Pakar")
st.sidebar.markdown("Masukkan penilaian pakar untuk menentukan bobot kriteria ($W$).")

with st.sidebar.form(key="form_simulasi_bobot", clear_on_submit=True):
    nama_pakar = st.text_input("Nama Penilai/Pakar", value=f"Pakar {len(st.session_state.kuesioner_bobot_data) + 1}")
    options = ["Sangat Tidak Penting", "Tidak Penting", "Cukup Penting", "Penting", "Sangat Penting"]
    
    # 9 Kriteria sinkron dengan struktur C1 - C9 Makalah Laptop UNPAM
    q1 = st.selectbox("C1. Tingkat Emosi/Stres (Psikologis)", options=options, index=3)
    q2 = st.selectbox("C2. Pengaruh Teman Sebaya (Lingkungan)", options=options, index=4)
    q3 = st.selectbox("C3. Efek Setelah Makan (Kebiasaan)", options=options, index=3)
    q4 = st.selectbox("C4. Ketergantungan Zat (Nikotin)", options=options, index=4)
    q5 = st.selectbox("C5. Jumlah Konsumsi Harian (Intensitas)", options=options, index=3)
    q6 = st.selectbox("C6. Gengsi/Sosial (Efek Sosial)", options=options, index=2)
    q7 = st.selectbox("C7. Mulut Terasa Pahit (Kondisi Fisik)", options=options, index=3)
    q8 = st.selectbox("C8. Harga Rokok Mahal (Ekonomi)", options=options, index=2) # Cost
    q9 = st.selectbox("C9. Paham Dampak Kanker (Pengetahuan)", options=options, index=1) # Cost
    
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
        st.session_state.kuesioner_bobot_data = pd.DataFrame(columns=[
            "Nama Penilai", "C1_Psikologis", "C2_Lingkungan", "C3_Kebiasaan", 
            "C4_Ketergantungan", "C5_Intensitas", "C6_Efek_Sosial", 
            "C7_Kondisi_Fisik", "C8_Ekonomi", "C9_Pengetahuan"
        ])
        st.rerun()

# -------------------------------------------------------------------------
# PROSES FILTER OTOMATIS & GENERATE BOBOT (W)
# -------------------------------------------------------------------------
nama_kriteria = ["Psikologis", "Lingkungan", "Kebiasaan", "Ketergantungan", "Intensitas", "Efek Sosial", "Kondisi Fisik", "Ekonomi", "Pengetahuan"]
criteria_type = ['benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'cost', 'cost']
mapping_likert = {"Sangat Tidak Penting": 1, "Tidak Penting": 2, "Cukup Penting": 3, "Penting": 4, "Sangat Penting": 5}

if not st.session_state.kuesioner_bobot_data.empty:
    st.subheader("📄 1. Hasil Pengumpulan Kuesioner Penilai (Form Simulasi)")
    st.dataframe(st.session_state.kuesioner_bobot_data, use_container_width=True)
    
    df_bobot_numeric = st.session_state.kuesioner_bobot_data.replace(mapping_likert)
    
    # Perbaikan Filter kata kunci agar memetakan kolom C1-C9 secara berurutan dan akurat
    w_cols = [
        [c for c in df_bobot_numeric.columns if "psikologis" in c.lower() or "c1" in c.lower()],
        [c for c in df_bobot_numeric.columns if "lingkungan" in c.lower() or "c2" in c.lower()],
        [c for c in df_bobot_numeric.columns if "kebiasaan" in c.lower() or "c3" in c.lower()],
        [c for c in df_bobot_numeric.columns if "ketergantungan" in c.lower() or "c4" in c.lower()],
        [c for c in df_bobot_numeric.columns if "intensitas" in c.lower() or "c5" in c.lower()],
        [c for c in df_bobot_numeric.columns if "sosial" in c.lower() or "c6" in c.lower()],
        [c for c in df_bobot_numeric.columns if "fisik" in c.lower() or "c7" in c.lower()],
        [c for c in df_bobot_numeric.columns if "ekonomi" in c.lower() or "c8" in c.lower()],
        [c for c in df_bobot_numeric.columns if "pengetahuan" in c.lower() or "c9" in c.lower()]
    ]
    
    raw_scores = [df_bobot_numeric[cols].astype(float).mean().mean() if len(cols) > 0 else 3.0 for cols in w_cols]
    total_raw = sum(raw_scores)
    weights = [score / total_raw for score in raw_scores]
else:
    # Default bobot awal kuesioner UNPAM (Total = 1.0)
    weights = [0.15, 0.15, 0.12, 0.10, 0.08, 0.08, 0.07, 0.10, 0.15]
    st.info("ℹ️ Belum ada data pakar diisi. Menggunakan parameter bobot default kuesioner UNPAM.")

# -------------------------------------------------------------------------
# 2. EVALUASI MATRIKS ALTERNATIF KELOMPOK PEROKOK
# -------------------------------------------------------------------------
st.subheader("📊 2. Matriks Keputusan Kelompok Perokok (Alternatif)")
st.markdown("Kamu bisa menyunting nilai evaluasi (Skala 1-100) langsung pada tabel interaktif berikut:")

default_alternatif = {
    'Alternatif': ['A1 (Perokok Ringan)', 'A2 (Perokok Sedang)', 'A3 (Perokok Berat)'],
    'C1 (Psikologis)': [55, 75, 95], 'C2 (Lingkungan)': [85, 70, 50], 'C3 (Kebiasaan)': [60, 80, 90],
    'C4 (Ketergantungan)': [35, 65, 95], 'C5 (Intensitas)': [40, 70, 95], 'C6 (Efek Sosial)': [75, 70, 60],
    'C7 (Kondisi Fisik)': [45, 65, 85], 'C8 (Ekonomi)': [80, 55, 35], 'C9 (Pengetahuan)': [85, 50, 25]
}
df_alternatif = pd.DataFrame(default_alternatif)
matrix_data = st.data_editor(df_alternatif, hide_index=True, use_container_width=True)

# -------------------------------------------------------------------------
# 3. PERHITUNGAN DAN OUTPUT AKHIR SAW METHOD
# -------------------------------------------------------------------------
if matrix_data is not None:
    saw = SAWMethod(matrix_data, weights, criteria_type)
    
    col_layout1, col_layout2 = st.columns(2)
    
    with col_layout1:
        st.markdown("### 📋 Parameter & Bobot Akhir Hasil Filter")
        df_parameter = pd.DataFrame({
            "Kode": [f"C{i+1}" for i in range(9)],
            "Kriteria": nama_kriteria,
            "Tipe Atribut": saw.criteria_type,
            "Bobot Terhitung (W)": saw.weights
        })
        st.dataframe(df_parameter, hide_index=True, use_container_width=True)
        
        st.markdown("### ⚙️ Matriks Hasil Normalisasi (R)")
        df_norm_res = saw.normalize_matrix()
        st.dataframe(df_norm_res.round(3), hide_index=True, use_container_width=True)

    with col_layout2:
        st.markdown("### 🏆 Hasil Perankingan Faktor Dominan")
        ranking = saw.get_ranking()
        st.dataframe(ranking.round(3), hide_index=True, use_container_width=True)
        
        best_alternative = ranking.iloc[0]['Alternatif']
        best_score = ranking.iloc[0]['Score']
        
        st.success(f"⭐ **KESIMPULAN:** Kategori **{best_alternative}** menjadi kelompok paling rentan/kritis terhadap kecanduan dengan nilai akhir preferensi SAW sebesar **{best_score:.3f}**")
        
        fig = px.bar(ranking, x="Alternatif", y="Score", text_auto='.3f', color="Score", color_continuous_scale="Reds", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
