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

# =========================================================================
# CLASS MURNI METODE SAW (Sesuai Landasan Teori Makalah)
# =========================================================================
class SAWMethod:
    def __init__(self, data: pd.DataFrame, weights: List[float], criteria_type: List[str]):
        self.data = data.copy()
        self.weights = np.array(weights)
        self.criteria_type = criteria_type
        self.normalized_data = None
        self.scores = None

    def normalize_matrix(self) -> pd.DataFrame:
        """Normalisasi matriks keputusan (R) [Sesuai Makalah Bab 2.2 & 4.2.2]"""
        normalized_data = self.data.copy()
        for i, col in enumerate(self.data.columns[1:]):  # Skip kolom Alternatif
            if self.criteria_type[i] == 'benefit':
                # Rumus Benefit: Xij / max(Xij) [Sesuai Makalah Bab 4.2.2]
                max_val = self.data[col].max()
                if max_val == 0: 
                    normalized_data[col] = 0
                else:
                    normalized_data[col] = self.data[col] / max_val
            else: # cost
                # Rumus Cost: min(Xij) / Xij [Sesuai Makalah Bab 4.2.2]
                min_val = self.data[col].min()
                normalized_data[col] = np.where(
                    self.data[col] != 0,
                    min_val / self.data[col],
                    0
                )
        self.normalized_data = normalized_data
        return normalized_data

    def calculate_scores(self) -> pd.DataFrame:
        """Hitung nilai preferensi (Vi) [Sesuai Makalah Bab 4.2.3]"""
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
# INTERMUKA WEB STREAMLIT (Sesuai Desain Makalah UNPAM)
# =========================================================================
st.title("🚭 SPK Faktor Penyebab Kecanduan Merokok")
st.caption("Implementasi Metode Simple Additive Weighting (SAW) - Tugas Project Universitas Pamulang")
st.markdown("---")

# -------------------------------------------------------------------------
# SIDEBAR: PANEL FILTERING SIMULASI (Sesuai Desain Makalah Bab 4.3.1)
# -------------------------------------------------------------------------
st.sidebar.title("🔍 Panel Filter Tingkat Keparahan")
st.sidebar.markdown("Silakan filter kriteria simulasi kelompok perokok:")

filter_usia = st.sidebar.slider("Batas Minimum Usia Responden (Cost)", min_value=12, max_value=60, value=15)
min_intensitas = st.sidebar.number_input("Minimal Skor Intensitas Merokok (1-100)", min_value=10, max_value=100, value=30, step=5)

# -------------------------------------------------------------------------
# DATASET REPLIKA MATRIKS KEPUTUSAN ROKOK (Format Sesuai Makalah Bab 4.2.1)
# -------------------------------------------------------------------------
dataset_merokok = pd.DataFrame({
    'Alternatif': [
        'A1 (Kelompok Perokok Ringan)', 
        'A2 (Kelompok Perokok Sedang)', 
        'A3 (Kelompok Perokok Berat)'
    ],
    'C1 (Psikologis)': [60, 80, 95],
    'C2 (Lingkungan)': [85, 75, 60],
    'C3 (Kebiasaan)': [55, 75, 90],
    'C4 (Ketergantungan)': [40, 70, 95],
    'C5 (Intensitas)': [35, 65, 90],
    'C6 (Efek Sosial)': [70, 75, 80],
    'C7 (Kondisi Fisik)': [50, 70, 85],
    'C8 (Pengetahuan Bahaya)': [80, 50, 30], # Cost (Semakin tahu bahaya, harusnya tingkat kecanduan rendah)
    'C9 (Rata-rata Usia)': [17, 28, 42]        # Cost (Semakin muda usia mulai merokok, semakin kritis dampaknya)
})

# -------------------------------------------------------------------------
# PROSES FILTER DATA / FALLBACK SYSTEM (Sesuai Konsep Makalah Bab 4.3.4)
# -------------------------------------------------------------------------
df_filtered = dataset_merokok[
    (dataset_merokok['C9 (Rata-rata Usia)'] >= filter_usia) & 
    (dataset_merokok['C5 (Intensitas)'] >= min_intensitas)
]

# Jalankan Fallback System jika filter user terlalu ketat hingga data kosong
if df_filtered.empty:
    st.warning("⚠️ **Fallback System Aktif:** Filter terlalu ketat untuk budget/kriteria data. Sistem menurunkan batas Intensitas secara otomatis agar data tetap tampil.")
    df_filtered = dataset_merokok[dataset_merokok['C9 (Rata-rata Usia)'] >= filter_usia]

# -------------------------------------------------------------------------
# PROSES KALKULASI SAW MURNI (Sesuai Logika Bab 4.1 & 4.2)
# -------------------------------------------------------------------------
if not df_filtered.empty:
    
    # Nilai Bobot Rata-rata dari Kuesioner (Total wajib 1.00 sesuai Makalah Bab 4.1)
    weights = [0.15, 0.15, 0.12, 0.10, 0.08, 0.08, 0.07, 0.10, 0.15]
    
    # Penentuan Jenis Kriteria (C1-C7 Benefit, C8-C9 Cost sesuai Makalah Bab 4.2.1)
    criteria_type = ['benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'cost', 'cost']
    
    # Eksekusi Class SAWMethod Modul
    saw = SAWMethod(df_filtered, weights, criteria_type)
    
    # Tampilan Layout Aplikasi Web UNPAM
    col_kiri, col_kanan = st.columns(2)
    
    with col_kiri:
        st.markdown("### 📊 Parameter Bobot Kriteria Hasil Kuesioner Laporan")
        df_kriteria_laporan = pd.DataFrame({
            "Kode": [f"C{i+1}" for i in range(9)],
            "Kriteria": ["Psikologis", "Lingkungan", "Kebiasaan", "Ketergantungan", "Intensitas", "Efek Sosial", "Kondisi Fisik", "Pengetahuan Bahaya", "Rata-rata Usia"],
            "Jenis Kriteria": criteria_type,
            "Nilai Bobot Rata-rata (W)": weights
        })
        st.dataframe(df_kriteria_laporan, hide_index=True, use_container_width=True)
        
        st.markdown("### 🧮 Matriks Normalisasi (R) [Sesuai Bab 4.2.2]")
        df_normalized = saw.normalize_matrix()
        cols_to_show = [c for c in df_normalized.columns if c not in ['Score', 'Rank']]
        st.dataframe(df_normalized[cols_to_show].round(3), hide_index=True, use_container_width=True)

    with col_kanan:
        st.markdown("### 🏆 Hasil Perankingan Faktor Dominan [Sesuai Bab 4.2.3]")
        ranking_result = saw.get_ranking()
        st.dataframe(ranking_result.round(3), hide_index=True, use_container_width=True)
        
        # Output Kesimpulan Akhir (Sesuai Bab 4.2.3)
        best_alt = ranking_result.iloc[0]['Alternatif']
        best_score = ranking_result.iloc[0]['Score']
        st.success(f"⭐ **HASIL EVALUASI PROYEK:** Kategori **{best_alt}** memiliki tingkat kecanduan paling tinggi/kritis dengan nilai akhir preferensi SAW sebesar **{best_score:.3f}**")
        
        # Visualisasi Data Interaktif (Sesuai Bab 4.3.3)
        st.markdown("### 📈 Grafik Perbandingan Skor Hasil Analisis")
        fig = px.bar(
            ranking_result, 
            x="Alternatif", 
            y="Score", 
            text_auto='.3f', 
            color="Score", 
            color_continuous_scale="Reds", 
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.error("❌ Data tidak ditemukan untuk simulasi ini. Harap sesuaikan filter di sidebar.")
