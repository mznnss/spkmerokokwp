import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px  # Memastikan Plotly Express ter-import secara global
from typing import List

st.set_page_config(
    page_title="SPK SAW - Filter Bobot Kuesioner",
    page_icon="🚭",
    layout="wide"
)

# Inisialisasi session state untuk menampung data kuesioner bobot simulasi
if 'kuesioner_bobot_data' not in st.session_state:
    st.session_state.kuesioner_bobot_data = pd.DataFrame(columns=[
        "Nama Penilai", "Psikologis (Stres)", "Lingkungan (Teman)", "Kebiasaan (Rutinitas)", "Ekonomi (Harga)", "Ketergantungan (Nikotin)", "Pengetahuan (Bahaya)"
    ])

# =========================================================================
# CLASS MURNI DARI MODUL (Logika Perhitungan Dipertahankan 100%)
# =========================================================================
class SAWMethod:
    def __init__(self, data: pd.DataFrame, weights: List[float], criteria_type: List[str]):
        """Inisialisasi metode SAW sesuai modul"""
        self.data = data.copy()
        self.weights = np.array(weights)
        self.criteria_type = criteria_type
        self.normalized_data = None
        self.scores = None

    def normalize_matrix(self) -> pd.DataFrame:
        """Normalisasi matriks keputusan sesuai modul"""
        normalized_data = self.data.copy()
        for i, col in enumerate(self.data.columns[1:]):  # Skip kolom alternatif
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
        """Hitung skor akhir dan ranking sesuai modul"""
        if self.normalized_data is None:
            self.normalize_matrix()
        criteria_columns = self.normalized_data.columns[1:]
        weighted_scores = self.normalized_data[criteria_columns] * self.weights
        self.normalized_data['Score'] = weighted_scores.sum(axis=1)
        self.normalized_data['Rank'] = self.normalized_data['Score'].rank(ascending=False, method='min').astype(int)
        return self.normalized_data

    def get_ranking(self) -> pd.DataFrame:
        """Dapatkan hasil ranking sesuai modul"""
        if self.scores is None:
            self.scores = self.calculate_scores()
        alt_column = self.scores.columns[0]
        result = self.scores[[alt_column, 'Score', 'Rank']].sort_values('Rank')
        result = result.rename(columns={alt_column: 'Alternatif'})
        return result

# =========================================================================
# INTERMUKA STREAMLIT
# =========================================================================
st.title("🚭 SPK - METODE SAW (Simple Additive Weighting)")
st.caption("Modul Terintegrasi: Simulasi Kuesioner Form Pembobotan & Engine Perhitungan Murni dari Modul")
st.markdown("---")

# -------------------------------------------------------------------------
# PILIHAN SIDEBAR: METODE INPUT BOBOT
# -------------------------------------------------------------------------
st.sidebar.title("🔌 Filter & Simulasi Bobot")
sumber_bobot = st.sidebar.radio(
    "Pilih Metode Penentuan Bobot:",
    ["Upload Excel Google Form", "Mode Simulasi (Isi Kuesioner Form)"]
)

# Parameter Kriteria Tetap
nama_kriteria = ["Psikologis", "Lingkungan", "Kebiasaan", "Ekonomi", "Ketergantungan", "Pengetahuan"]
criteria_type = ['benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'cost']

# Mapping konversi Skala Likert kuesioner bobot jika berupa teks
mapping_likert = {
    "Sangat Tidak Penting": 1, "Tidak Penting": 2, "Cukup Penting": 3, "Penting": 4, "Sangat Penting": 5,
    "Sangat Tidak Setuju": 1, "Tidak Setuju": 2, "Netral": 3, "Setuju": 4, "Sangat Setuju": 5
}

weights = []
df_bobot_aktif = pd.DataFrame()

# =========================================================================
# KONDISI SIDEBAR 1: UPLOAD FILE EXCEL
# =========================================================================
if sumber_bobot == "Upload Excel Google Form":
    uploaded_file = st.sidebar.file_uploader("📂 Upload Excel Kuesioner Bobot", type=["xlsx", "xls"])
    
    if uploaded_file:
        df_bobot_aktif = pd.read_excel(uploaded_file)
        st.sidebar.success(f"✅ Berhasil memuat {len(df_bobot_aktif)} data dari Excel!")
    else:
        st.sidebar.info("ℹ️ Silakan upload file Excel di atas.")

# =========================================================================
# KONDISI SIDEBAR 2: SIMULASI ISI FORM KUESIONER LANGSUNG DI APP
# =========================================================================
else:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📝 Form Kuesioner Simulasi")
    
    with st.sidebar.form(key="form_simulasi_bobot", clear_on_submit=True):
        nama_pakar = st.text_input("Nama Penilai/Pakar", value=f"Pakar {len(st.session_state.kuesioner_bobot_data) + 1}")
        options = ["Sangat Tidak Penting", "Tidak Penting", "Cukup Penting", "Penting", "Sangat Penting"]
        
        q1 = st.select_slider("1. Seberapa penting faktor emosi/stres memicu merokok?", options=options, value="Penting")
        q2 = st.select_slider("2. Seberapa penting pengaruh teman dan lingkungan?", options=options, value="Sangat Penting")
        q3 = st.select_slider("3. Seberapa penting rutinitas/kebiasaan setelah makan?", options=options, value="Penting")
        q4 = st.select_slider("4. Seberapa penting faktor harga rokok murah (ekonomi)?", options=options, value="Cukup Penting")
        q5 = st.select_slider("5. Seberapa penting tingkat ketergantungan zat nikotin?", options=options, value="Penting")
        q6 = st.select_slider("6. Seberapa penting info bahaya rokok (pengetahuan)?", options=options, value="Tidak Penting")
        
        submit_btn = st.form_submit_button(label="💾 Simpan Jawaban Pakar")
        
        if submit_btn:
            new_row = {
                "Nama Penilai": nama_pakar,
                "Psikologis (Stres)": q1,
                "Lingkungan (Teman)": q2,
                "Kebiasaan (Rutinitas)": q3,
                "Ekonomi (Harga)": q4,
                "Ketergantungan (Nikotin)": q5,
                "Pengetahuan (Bahaya)": q6
            }
            st.session_state.kuesioner_bobot_data = pd.concat([st.session_state.kuesionot_bobot_data, pd.DataFrame([new_row])], ignore_index=True) if 'kuesionot_bobot_data' in st.session_state else pd.concat([st.session_state.kuesioner_bobot_data, pd.DataFrame([new_row])], ignore_index=True)
            st.rerun()

    if len(st.session_state.kuesioner_bobot_data) > 0:
        df_bobot_aktif = st.session_state.kuesioner_bobot_data
        if st.sidebar.button("🗑️ Reset Semua Data Pakar"):
            st.session_state.kuesioner_bobot_data = pd.DataFrame(columns=["Nama Penilai", "Psikologis (Stres)", "Lingkungan (Teman)", "Kebiasaan (Rutinitas)", "Ekonomi (Harga)", "Ketergantungan (Nikotin)", "Pengetahuan (Bahaya)"])
            st.rerun()

# =========================================================================
# PROSES PEMFILTERAN OTOMATIS DATA BOBOT (EXCEL MAUPUN FORM SIMULASI)
# =========================================================================
if not df_bobot_aktif.empty:
    st.subheader("📄 1. Hasil Pengumpulan Kuesioner Bobot Penilai")
    st.dataframe(df_bobot_aktif, use_container_width=True)
    
    df_bobot_numeric = df_bobot_aktif.replace(mapping_likert)
    
    w_psikologis = [col for col in df_bobot_numeric.columns if "psikologis" in col.lower() or "stres" in col.lower()]
    w_lingkungan = [col for col in df_bobot_numeric.columns if "lingkungan" in col.lower() or "teman" in col.lower()]
    w_kebiasaan = [col for col in df_bobot_numeric.columns if "kebiasaan" in col.lower() or "rutinitas" in col.lower()]
    w_ekonomi = [col for col in df_bobot_numeric.columns if "ekonomi" in col.lower() or "harga" in col.lower()]
    w_ketergantungan = [col for col in df_bobot_numeric.columns if "ketergantungan" in col.lower() or "nikotin" in col.lower()]
    w_pengetahuan = [col for col in df_bobot_numeric.columns if "pengetahuan" in col.lower() or "bahaya" in col.lower()]
    
    def hitung_rata_kriteria(cols):
        if len(cols) > 0:
            return df_bobot_numeric[cols].astype(float).mean().mean()
        return 3.0
        
    raw_scores = [
        hitung_rata_kriteria(w_psikologis),
        hitung_rata_kriteria(w_lingkungan),
        hitung_rata_kriteria(w_kebiasaan),
        hitung_rata_kriteria(w_ekonomi),
        hitung_rata_kriteria(w_ketergantungan),
        hitung_rata_kriteria(w_pengetahuan)
    ]
    
    total_raw = sum(raw_scores)
    weights = [score / total_raw for score in raw_scores]
else:
    weights = [0.15, 0.25, 0.20, 0.25, 0.10, 0.05]
    st.warning("⚠️ Belum ada data kuesioner masuk. Menggunakan bobot *default* bawaan sistem untuk sementara. Silakan isi form simulasi di sidebar kuesioner atau upload file Excel!")

# -------------------------------------------------------------------------
# 2. HALAMAN UTAMA: SIMULASI INPUT MATRIKS KEPUTUSAN KELOMPOK PEROKOK (ALTERNATIF)
# -------------------------------------------------------------------------
st.subheader("📊 2. Matriks Keputusan Kelompok Perokok (Alternatif)")
st.markdown("Kamu bisa mengubah nilai matriks keputusan kelompok alternatif di bawah ini untuk melihat efek perhitungannya:")

default_alternatif = {
    'Alternatif': ['Perokok Ringan (1-4 btg/hari)', 'Perokok Sedang (5-14 btg/hari)', 'Perokok Berat (>15 btg/hari)'],
    'Psikologis': [3.0, 4.0, 5.0],
    'Lingkungan': [4.5, 3.5, 2.5],
    'Kebiasaan': [2.5, 4.0, 5.0],
    'Ekonomi': [4.0, 3.0, 1.5],
    'Ketergantungan': [2.0, 3.5, 5.0],
    'Pengetahuan': [4.5, 3.0, 1.5]
}
df_alternatif = pd.DataFrame(default_alternatif)
matrix_data = st.data_editor(df_alternatif, hide_index=True, use_container_width=True)

# -------------------------------------------------------------------------
# 3. PROSES KALKULASI ENGINE SAW BERBASIS CLASS MODUL MURNI
# -------------------------------------------------------------------------
if matrix_data is not None and len(weights) > 0:
    saw = SAWMethod(matrix_data, weights, criteria_type)
    
    col_layout1, col_layout2 = st.columns(2)
    
    with col_layout1:
        st.markdown("### 📋 Parameter Atribut & Hasil Bobot Filter Kuesioner")
        df_parameter = pd.DataFrame({
            "Kriteria": nama_kriteria,
            "Bobot Preferensi (W)": saw.weights,
            "Tipe Atribut": saw.criteria_type
        })
        st.dataframe(df_parameter, hide_index=True, use_container_width=True)
        
        st.markdown("### ⚙️ Matriks Hasil Normalisasi (Output Rumus Modul)")
        df_norm_res = saw.normalize_matrix()
        st.dataframe(df_norm_res.round(4), hide_index=True, use_container_width=True)

    with col_layout2:
        st.markdown("### 🏆 Hasil Akhir Perankingan Kategori Alternatif")
        ranking = saw.get_ranking()
        st.dataframe(ranking.round(4), hide_index=True, use_container_width=True)
        
        best_alternative = ranking.iloc[0]['Alternatif']
        best_score = ranking.iloc[0]['Score']
        
        st.success(f"⭐ **KESIMPULAN:** Kategori **{best_alternative}** menjadi kelompok paling dominan memicu tingkat kecanduan dengan total pencapaian nilai akhir SAW sebesar **{best_score:.4f}**")
        
        # PERBAIKAN: Membaca px (Plotly Express) dengan aman tanpa memicu NameError
        fig = px.bar(
            ranking, 
            x="Alternatif", 
            y="Score", 
            text_auto='.4f', 
            color="Score", 
            color_continuous_scale="Reds", 
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
