import streamlit as st
import pandas as pd
import numpy as np
from typing import List

st.set_page_config(
    page_title="SPK SAW - Kuesioner & Modul",
    page_icon="🚭",
    layout="wide"
)

# =========================================================================
# CLASS MURNI DARI MODUL (Logika Perhitungan Dipertahankan 100%)
# =========================================================================
class SAWMethod:
    def __init__(self, data: pd.DataFrame, weights: List[float], criteria_type: List[str]):
        self.data = data.copy()
        self.weights = np.array(weights)
        self.criteria_type = criteria_type
        self.normalized_data = None
        self.scores = None

    def normalize_matrix(self) -> pd.DataFrame:
        normalized_data = self.data.copy()
        for i, col in enumerate(self.data.columns[1:]): 
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
# INTERMUKA STREAMLIT
# =========================================================================
st.title("🚭 SPK - METODE SAW (Simple Additive Weighting)")
st.caption("Integrasi Filter Otomatis Kuesioner dengan Engine Perhitungan Murni dari Modul")
st.markdown("---")

# Sidebar untuk upload file
st.sidebar.title("🔌 Sumber Data")
uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Excel Google Form",
    type=["xlsx", "xls"]
)

# Definisi Parameter Tetap (Bobot & Tipe Kriteria)
nama_kriteria = ["Psikologis", "Lingkungan", "Kebiasaan", "Ekonomi", "Ketergantungan", "Pengetahuan"]
weights = [0.15, 0.25, 0.20, 0.25, 0.10, 0.05]
criteria_type = ['benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'cost']

mapping = {
    "Sangat Tidak Setuju": 1,
    "Tidak Setuju": 2,
    "Netral": 3,
    "Setuju": 4,
    "Sangat Setuju": 5
}

if uploaded_file:
    # 1. Membaca data kuesioner awal
    df_mentah = pd.read_excel(uploaded_file)
    
    st.subheader("📄 1. Data Mentah Kuesioner Google Form")
    st.dataframe(df_mentah, use_container_width=True)
    
    # Konversi jawaban teks ke angka (Skala Likert)
    df_numeric = df_mentah.replace(mapping)
    
    # 2. PROSES FILTER OTOMATIS BERDASARKAN KATA KUNCI (Keyword Filtering)
    psikologis_cols = [col for col in df_numeric.columns if "stres" in col.lower() or "sulit berhenti" in col.lower() or "tidak nyaman" in col.lower()]
    lingkungan_cols = [col for col in df_numeric.columns if "teman" in col.lower() or "lingkungan" in col.lower() or "berkumpul" in col.lower()]
    kebiasaan_cols = [col for col in df_numeric.columns if "rutinitas" in col.lower() or "setelah makan" in col.lower() or "tanpa sadar" in col.lower()]
    ekonomi_cols = [col for col in df_numeric.columns if "mudah didapat" in col.lower() or "harga" in col.lower()]
    ketergantungan_cols = [col for col in df_numeric.columns if "ingin merokok" in col.lower() or "mengurangi" in col.lower()]
    pengetahuan_cols = [col for col in df_numeric.columns if "bahaya" in col.lower() or "berbahaya" in col.lower()]
    
    # Fungsi pembantu untuk mengambil rata-rata kolom yang terfilter
    def avg_cols(cols):
        if len(cols) > 0:
            return df_numeric[cols].astype(float).mean(axis=1)
        return 0

    # 3. PEMBENTUKAN MATRIKS KEPUTUSAN (Sesuai Struktur Data Modul)
    # Di sini kita menyusun Alternatif berdasarkan individu responden (misal: Responden 1, Responden 2, dst)
    df_saw_input = pd.DataFrame()
    df_saw_input['Alternatif'] = [f"Responden {i+1}" for i in range(len(df_mentah))]
    df_saw_input['Psikologis'] = avg_cols(psikologis_cols)
    df_saw_input['Lingkungan'] = avg_cols(lingkungan_cols)
    df_saw_input['Kebiasaan'] = avg_cols(kebiasaan_cols)
    df_saw_input['Ekonomi'] = avg_cols(ekonomi_cols)
    df_saw_input['Ketergantungan'] = avg_cols(ketergantungan_cols)
    df_saw_input['Pengetahuan'] = avg_cols(pengetahuan_cols)
    
    st.subheader("🧮 2. Matriks Keputusan Hasil Filter & Ekstraksi Rata-rata")
    st.markdown("Berikut adalah hasil konversi otomatis kuesioner menjadi Matriks Keputusan penunjang rumus SAW:")
    st.dataframe(df_saw_input.round(4), hide_index=True, use_container_width=True)
    
    # =========================================================================
    # PROSES EKSEKUSI ENGINE METODE SAW DARI MODUL
    # =========================================================================
    # Mengirimkan data hasil filter kuesioner ke dalam Class bawaan modul
    saw = SAWMethod(df_saw_input, weights, criteria_type)
    
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.markdown("### 📊 Parameter Atribut Kriteria")
        df_parameter = pd.DataFrame({
            "Kriteria": nama_kriteria,
            "Bobot Preferensi (W)": saw.weights,
            "Tipe Atribut": saw.criteria_type
        })
        st.dataframe(df_parameter, hide_index=True, use_container_width=True)
        
        st.markdown("### ⚙️ Matriks Hasil Normalisasi (Output Modul)")
        # Pemanggilan fungsi normalisasi asli dari modul (Mengeksekusi Benefit & Cost)
        df_norm_res = saw.normalize_matrix()
        st.dataframe(df_norm_res.round(4), hide_index=True, use_container_width=True)

    with col_res2:
        st.markdown("### 🏆 Hasil Akhir Perankingan Responden (Output Modul)")
        # Pemanggilan fungsi perhitungan skor dan ranking asli dari modul
        ranking = saw.get_ranking()
        st.dataframe(ranking.round(4), hide_index=True, use_container_width=True)
        
        # Mengambil baris pertama sebagai alternatif terbaik/paling kritis
        best_alternative = ranking.iloc[0]['Alternatif']
        best_score = ranking.iloc[0]['Score']
        
        st.success(f"⭐ **HASIL EVALUASI:** **{best_alternative}** memiliki kecenderungan tingkat kecanduan paling tinggi/kritis dengan skor SAW sebesar **{best_score:.4f}**")
        
        # Visualisasi interaktif tambahan
        import plotly.express as px
        fig = px.bar(ranking, x="Alternatif", y="Score", text_auto='.4f', color="Score", color_continuous_scale="Reds", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("⬅️ Silakan unggah file Excel Google Form dari sidebar untuk memulai penyaringan data & kalkulasi SAW.")
