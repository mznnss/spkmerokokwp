import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

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
st.markdown('<div class="subtitle">Studi Kasus: Analisis Tingkat Kecanduan Merokok Berdasarkan Kelompok Perokok</div>', unsafe_allow_html=True)
st.markdown("---")

# =========================
# 1. INPUT DATA AWAL (MATRIKS KEPUTUSAN)
# =========================
st.subheader("1. Pembentukan Matriks Keputusan")
st.markdown("Silakan simulasikan dengan mengubah angka nilai (Skala 1-5) pada tabel di bawah ini secara langsung:")

# Alternatif disesuaikan dengan studi kasus merokok namun berorientasi objek kelompok (sesuai modul)
alternatif_list = ["Perokok Ringan (1-4 batang/hari)", "Perokok Sedang (5-14 batang/hari)", "Perokok Berat (>15 batang/hari)"]

# Template Matriks Keputusan Awal
default_data = {
    "Alternatif": alternatif_list,
    "Psikologis": [3.2, 4.0, 4.8],
    "Lingkungan": [4.5, 3.8, 3.0],
    "Kebiasaan": [2.8, 4.2, 4.9],
    "Ekonomi": [4.0, 3.5, 2.0],
    "Ketergantungan": [2.0, 3.8, 4.8],
    "Pengetahuan": [4.2, 3.0, 1.8]
}

df_awal = pd.DataFrame(default_data)

# Menggunakan data_editor agar pengguna bisa melakukan simulasi interaktif (input/geser nilai)
matrix_input = st.data_editor(df_awal, hide_index=True, use_container_width=True)

# =========================
# 2. BOBOT & TIPE KRITERIA
# =========================
st.subheader("2. Bobot & Tipe Kriteria")

# Aturan pembobotan dan tipe kriteria (benefit/cost) murni mengikuti aturan logika modul
kriteria_info = pd.DataFrame({
    "Kriteria": ["Psikologis", "Lingkungan", "Kebiasaan", "Ekonomi", "Ketergantungan", "Pengetahuan"],
    "Bobot": [0.15, 0.25, 0.20, 0.25, 0.10, 0.05],
    "Tipe": ["benefit", "benefit", "benefit", "benefit", "benefit", "cost"]
})
st.dataframe(kriteria_info, hide_index=True, use_container_width=True)

weights = kriteria_info["Bobot"].values
criteria_types = kriteria_info["Tipe"].values
kriteria_cols = kriteria_info["Kriteria"].tolist()

# =========================
# 3. PROSES NORMALISASI MATRIKS
# =========================
st.subheader("3. Matriks Normalisasi")

df_normalized = matrix_input.copy()

# Perulangan rumus normalisasi murni mengacu pada fungsi 'normalize_matrix' di modul
for i, col in enumerate(kriteria_cols):
    if criteria_types[i] == 'benefit':
        # Rumus Benefit: x / max(x) [Sesuai isi modul halaman 6]
        max_val = matrix_input[col].max()
        df_normalized[col] = matrix_input[col] / max_val if max_val > 0 else 0
    else:
        # Rumus Cost: min(x) / x [Sesuai isi modul halaman 6-7]
        min_val = matrix_input[col].min()
        df_normalized[col] = np.where(matrix_input[col] != 0, min_val / matrix_input[col], 0)

st.dataframe(df_normalized.round(4), hide_index=True, use_container_width=True)

# =========================
# 4. PERHITUNGAN SKOR & RANKING
# =========================
st.subheader("4. Hasil Perhitungan Skor Akhir & Ranking")

# Perkalian matriks normalisasi dengan bobot kriteria [Sesuai isi modul halaman 7]
weighted_scores = df_normalized[kriteria_cols].values * weights

# Total skor penjumlahan terbobot untuk setiap alternatif [Sesuai isi modul halaman 7]
df_normalized['Score'] = weighted_scores.sum(axis=1)

# Peringkat/Ranking berdasarkan skor tertinggi [Sesuai isi modul halaman 7]
df_normalized['Rank'] = df_normalized['Score'].rank(ascending=False, method='min').astype(int)

# Menampilkan hasil rangking akhir
ranking_result = df_normalized[["Alternatif", "Score", "Rank"]].sort_values("Rank").reset_index(drop=True)
st.dataframe(ranking_result.round(4), hide_index=True, use_container_width=True)

# Kesimpulan alternatif terbaik
best_alt = ranking_result.iloc[0]['Alternatif']
best_score = ranking_result.iloc[0]['Score']

st.success(f"🏆 **KESIMPULAN (ALTERNATIF TERBAIK):** Kategori **{best_alt}** memiliki tingkat kecanduan merokok tertinggi/paling kritis dengan total nilai akhir SAW sebesar **{best_score:.4f}**")

# =========================
# 5. VISUALISASI GRAFIK
# =========================
st.markdown("---")
st.subheader("📊 Grafik Perbandingan Skor Hasil SAW")
fig = px.bar(
    ranking_result,
    x="Alternatif",
    y="Score",
    text_auto='.4f',
    color="Score",
    color_continuous_scale="Reds",
    template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)
