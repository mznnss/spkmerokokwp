import streamlit as st
import pandas as pd
import numpy as np
from typing import List

st.set_page_config(
    page_title="SPK SAW - Filter Bobot Kuesioner",
    page_icon="🚭",
    layout="wide"
)

# =========================================================================
# CLASS MURNI DARI MODUL (Logika Perhitungan Dipertahankan 100%)
# =========================================================================
class SAWMethod:
    def __init__(self, data: pd.DataFrame, weights: List[float], criteria_type: List[str]):
        """Inisialisasi metode SAW sesuai modul [cite: 90, 91]"""
        self.data = data.copy() [cite: 96]
        self.weights = np.array(weights) [cite: 97]
        self.criteria_type = criteria_type [cite: 98]
        self.normalized_data = None [cite: 99]
        self.scores = None [cite: 100]

    def normalize_matrix(self) -> pd.DataFrame:
        """Normalisasi matriks keputusan sesuai modul [cite: 101, 102]"""
        normalized_data = self.data.copy() [cite: 103]
        for i, col in enumerate(self.data.columns[1:]):  # Skip kolom alternatif [cite: 104]
            if self.criteria_type[i] == 'benefit': [cite: 105]
                max_val = self.data[col].max() [cite: 108]
                if max_val == 0:  [cite: 109]
                    normalized_data[col] = 0 [cite: 110]
                else: [cite: 111]
                    normalized_data[col] = self.data[col] / max_val [cite: 112]
            else: # cost [cite: 113]
                min_val = self.data[col].min() [cite: 115]
                normalized_data[col] = np.where( [cite: 117]
                    self.data[col] != 0, [cite: 119]
                    min_val / self.data[col], [cite: 120]
                    0 [cite: 121]
                )
        self.normalized_data = normalized_data [cite: 122]
        return normalized_data [cite: 123]

    def calculate_scores(self) -> pd.DataFrame:
        """Hitung skor akhir dan ranking sesuai modul [cite: 124, 125]"""
        if self.normalized_data is None: [cite: 126]
            self.normalize_matrix() [cite: 127]
        criteria_columns = self.normalized_data.columns[1:] [cite: 129]
        weighted_scores = self.normalized_data[criteria_columns] * self.weights [cite: 130]
        self.normalized_data['Score'] = weighted_scores.sum(axis=1) [cite: 132]
        self.normalized_data['Rank'] = self.normalized_data['Score'].rank(ascending=False, method='min').astype(int) [cite: 134]
        return self.normalized_data [cite: 135]

    def get_ranking(self) -> pd.DataFrame:
        """Dapatkan hasil ranking sesuai modul [cite: 136, 137]"""
        if self.scores is None: [cite: 138]
            self.scores = self.calculate_scores() [cite: 139]
        alt_column = self.scores.columns[0] [cite: 141]
        result = self.scores[[alt_column, 'Score', 'Rank']].sort_values('Rank') [cite: 142]
        result = result.rename(columns={alt_column: 'Alternatif'}) [cite: 143]
        return result [cite: 144]

# =========================================================================
# INTERMUKA STREAMLIT
# =========================================================================
st.title("🚭 SPK - METODE SAW (Simple Additive Weighting)")
st.caption("Modul Terintegrasi: Pengolah Bobot via Filter Excel Google Form & Simulasi Matriks Keputusan")
st.markdown("---")

# -------------------------------------------------------------------------
# PILIHAN SIDEBAR: 1. FILTER BOBOT DARI EXCEL GOOGLE FORM
# -------------------------------------------------------------------------
st.sidebar.title("🔌 Filter Bobot Kriteria")
st.sidebar.markdown("Upload file hasil Google Form penilaian tingkat kepentingan kriteria oleh pakar/koresponden:")
uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Excel Kuesioner Bobot",
    type=["xlsx", "xls"]
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

if uploaded_file:
    # Membaca data kuesioner bobot
    df_bobot_mentah = pd.read_excel(uploaded_file)
    df_bobot_numeric = df_bobot_mentah.replace(mapping_likert)
    
    # Proses Filter Otomatis Kolom Berdasarkan Kata Kunci (Keyword Filtering)
    w_psikologis = [col for col in df_bobot_numeric.columns if "psikologis" in col.lower() or "stres" in col.lower()]
    w_lingkungan = [col for col in df_bobot_numeric.columns if "lingkungan" in col.lower() or "teman" in col.lower()]
    w_kebiasaan = [col for col in df_bobot_numeric.columns if "kebiasaan" in col.lower() or "rutinitas" in col.lower()]
    w_ekonomi = [col for col in df_bobot_numeric.columns if "ekonomi" in col.lower() or "harga" in col.lower()]
    w_ketergantungan = [col for col in df_bobot_numeric.columns if "ketergantungan" in col.lower() or "nikotin" in col.lower()]
    w_pengetahuan = [col for col in df_bobot_numeric.columns if "pengetahuan" in col.lower() or "bahaya" in col.lower()]
    
    def hitung_rata_kriteria(cols):
        if len(cols) > 0:
            return df_bobot_numeric[cols].astype(float).mean().mean()
        return 3.0 # Nilai default jika kolom tidak tersaring
        
    # Mengambil nilai rata-rata mentah (skala 1-5) dari koresponden
    raw_scores = [
        hitung_rata_kriteria(w_psikologis),
        hitung_rata_kriteria(w_lingkungan),
        hitung_rata_kriteria(w_kebiasaan),
        hitung_rata_kriteria(w_ekonomi),
        hitung_rata_kriteria(w_ketergantungan),
        hitung_rata_kriteria(w_pengetahuan)
    ]
    
    # Validasi & Normalisasi bobot otomatis agar total keseluruhan bernilai 1.0 (Sesuai Modul baris 293-299) 
    total_raw = sum(raw_scores)
    weights = [score / total_raw for score in raw_scores] [cite: 298]
    
    st.sidebar.success(f"✅ Berhasil memproses & memfilter bobot dari {len(df_bobot_mentah)} responden Google Form!")
else:
    # Menggunakan bobot default jika file belum diunggah untuk keperluan simulasi awal
    weights = [0.15, 0.25, 0.20, 0.25, 0.10, 0.05]
    st.sidebar.info("ℹ️ Menggunakan bobot preferensi bawaan. Silakan upload file kuesioner di atas untuk menyaring bobot baru.")

# -------------------------------------------------------------------------
# 2. HALAMAN UTAMA: SIMULASI INPUT MATRIKS KEPUTUSAN KELOMPOK PEROKOK
# -------------------------------------------------------------------------
st.subheader("📊 Matriks Keputusan Kelompok Perokok (Alternatif)")
st.markdown("Silakan simulasikan nilai evaluasi kelompok perokok (Skala 1-5) secara langsung pada tabel interaktif di bawah ini:")

# Alternatif disesuaikan dengan objek penelitian kecanduan rokok kelompok
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

# Komponen data_editor agar pengguna bisa melakukan input manual/mengubah data (Simulasi) 
matrix_data = st.data_editor(df_alternatif, hide_index=True, use_container_width=True)

# -------------------------------------------------------------------------
# 3. PROSES KALKULASI & OUTPUT EVALUASI METODE SAW MURNI DARI MODUL
# -------------------------------------------------------------------------
if matrix_data is not None and len(weights) > 0:
    # Mengirimkan data simulasi dan bobot terfilter ke Class SAWMethod bawaan modul 
    saw = SAWMethod(matrix_data, weights, criteria_type)
    
    col_layout1, col_layout2 = st.columns(2)
    
    with col_layout1:
        st.markdown("### 📋 Parameter Kriteria Hasil Filter Kuesioner")
        df_parameter = pd.DataFrame({
            "Kriteria": nama_kriteria,
            "Bobot Preferensi (W)": saw.weights, [cite: 157]
            "Tipe Atribut": saw.criteria_type [cite: 158]
        })
        st.dataframe(df_parameter, hide_index=True, use_container_width=True)
        
        st.markdown("### ⚙️ Matriks Hasil Normalisasi (Output Rumus Modul)")
        # Pemanggilan fungsi normalisasi bawaan modul
        df_norm_res = saw.normalize_matrix() [cite: 127]
        st.dataframe(df_norm_res.round(4), hide_index=True, use_container_width=True) [cite: 164]

    with col_layout2:
        st.markdown("### 🏆 Hasil Akhir Perankingan Kategori Alternatif")
        # Pemanggilan fungsi ranking bawaan modul
        ranking = saw.get_ranking() [cite: 170]
        st.dataframe(ranking.round(4), hide_index=True, use_container_width=True) [cite: 173]
        
        # Penentuan alternatif terbaik mengacu baris 176-180 modul [cite: 176, 177]
        best_alternative = ranking.iloc[0]['Alternatif'] [cite: 176]
        best_score = ranking.iloc[0]['Score'] [cite: 177]
        
        st.success(f"⭐ **KESIMPULAN:** Kategori **{best_alternative}** menjadi kelompok paling dominan memicu tingkat kecanduan dengan total pencapaian nilai akhir SAW sebesar **{best_score:.4f}**") [cite: 178, 180]
        
        # Visualisasi tambahan berupa grafik batang untuk memperkuat presentasi hasil [cite: 78]
        import plotly.express as px
        fig = px.bar(ranking, x="Alternatif", y="Score", text_auto='.4f', color="Score", color_continuous_scale="Reds", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
