import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(
    page_title="SPK SAW - Sesuai Modul",
    page_icon="🚭",
    layout="wide"
)

# =========================
# CUSTOM CSS (Tema Gelap)
# =========================
st.markdown("""
<style>
.main { background-color: #0f172a; }
.title { font-size: 38px; font-weight: bold; color: white; text-align: center; }
.subtitle { color: #94a3b8; font-size: 16px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">SISTEM PENDUKUNG KEPUTUSAN - METODE SAW</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Studi Kasus: Analisis Kelompok Faktor Penyebab Kecanduan Merokok</div>', unsafe_allow_html=True)
st.markdown("---")

# =========================
# 1. INPUT DATA AWAL (MATRIKS KEPUTUSAN)
# =========================
st.subheader("1. Pembentukan Matriks Keputusan")
st.markdown("Masukkan nilai evaluasi (Skala 1-5) untuk setiap kelompok alternatif berdasarkan kriteria:")

# Mendefinisikan Alternatif murni sesuai konsep modul
alternatif_list = ["Kelompok Remaja (12-25 thn)", "Kelompok Dewasa (26-45 thn)", "Kelompok Lansia (>45 thn)"]

# Membuat template data awal (Matriks Keputusan)
default_data = {
    "Alternatif": alternatif_list,
    "Psikologis": [4.5, 3.8, 3.0],
    "Lingkungan": [4.8, 3.5, 2.8],
    "Kebiasaan": [3.8, 4.5, 4.8],
    "Ekonomi": [4.2, 3.0, 2.5],
    "Ketergantungan": [3.5, 4.2, 4.6],
    "Pengetahuan": [2.5, 3.8, 4.0]
}

# Menggunakan data_editor agar user bisa mengedit matriks secara langsung di layar
df_awal = pd.DataFrame(default_data)
matrix_input = st.data_editor(df_awal, hide_index=True, use_container_width=True)

# =========================
# 2. BOBOT & TIPE KRITERIA
# =========================
st.subheader("2. Bobot & Tipe Kriteria")

# Susunan bobot dan tipe disesuaikan dengan aturan Benefit vs Cost di modul
kriteria_info = pd.DataFrame({
    "Kriteria": ["Psikologis", "Lingkungan", "Kebiasaan", "Ekonomi", "Ketergantungan", "Pengetahuan"],
    "Bobot": [0.15, 0.25, 0.20, 0.25, 0.10, 0.05],
    "Tipe": ["benefit", "benefit", "benefit", "benefit", "benefit", "cost"]
})
st.dataframe(kriteria_info, hide_index=True, use_container_width=True)

# Mengonversi ke dalam array/dictionary untuk perhitungan fisik matematika
weights = kriteria_info["Bobot"].values
criteria_types = kriteria_info["Tipe"].values
kriteria_cols = kriteria_info["Kriteria"].tolist()

# =========================
# 3. PROSES NORMALISASI (LOGIKA MURNI DARI MODUL)
# =========================
st.subheader("3. Matriks Normalisasi")

df_normalized = matrix_input.copy()

# Perulangan rumus normalisasi murni mengacu pada kode fungsi 'normalize_matrix' di modul
for i, col in enumerate(kriteria_cols):
    if criteria_types[i] == 'benefit':
        # Rumus Benefit: x / max(x)
        max_val = matrix_input[col].max()
        df_normalized[col] = matrix_input[col] / max_val if max_val > 0 else 0
    else:
        # Rumus Cost: min(x) / x
        min_val = matrix_input[col].min()
        df_normalized[col] = np.where(matrix_input[col] != 0, min_val / matrix_input[col], 0)

st.dataframe(df_normalized.round(4), hide_index=True, use_container_width=True)

# =========================
# 4. PERHITUNGAN SKOR & RANKING
# =========================
st.subheader("4. Hasil Perhitungan Skor Akhir & Ranking")

# Proses perkalian matriks normalisasi dengan array bobot kriteria
weighted_scores = df_normalized[kriteria_cols].values * weights

# Penjumlahan total skor per baris alternatif
df_normalized['Score'] = weighted_scores.sum(axis=1)

# Membuat urutan ranking berdasarkan skor tertinggi
df_normalized['Rank'] = df_normalized['Score'].rank(ascending=False, method='min').astype(int)

# Membuat dataframe hasil akhir untuk ditampilkan dan diurutkan
ranking_result = df_normalized[["Alternatif", "Score", "Rank"]].sort_values("Rank").reset_index(drop=True)
st.dataframe(ranking_result.round(4), hide_index=True, use_container_width=True)

# Menentukan alternatif terbaik berdasarkan peringkat pertama
best_alt = ranking_result.iloc[0]['Alternatif']
best_score = ranking_result.iloc[0]['Score']

st.success(f"🏆 **ALTERNATIF TERBAIK:** {best_alt} dengan total nilai akhir SAW sebesar **{best_score:.4f}**")

# =========================
# 5. VISUALISASI HASIL RANGKING
# =========================
st.markdown("---")
st.subheader("📊 Grafik Perbandingan Skor Alternatif")
fig = px.bar(
    ranking_result,
    x="Alternatif",
    y="Score",
    text_auto='.4f',
    color="Score",
    color_continuous_scale="Viridis",
    template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)
