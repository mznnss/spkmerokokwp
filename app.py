import streamlit as st
import pandas as pd
import numpy as np
from typing import List

st.set_page_config(
    page_title="SPK SAW - Sesuai Modul",
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
st.caption("Aplikasi dioptimalkan dari modul pemrograman ke dalam framework Streamlit")
st.markdown("---")

# Sidebar Menu Navigasi (Pengganti struktur Menu 'while True' pada modul)
st.sidebar.title("📌 Menu Pilihan")
opsi = st.sidebar.radio(
    "Pilih Kasus Analisis:",
    [
        "1. Studi Kasus: Kecanduan Merokok",
        "2. Contoh 1: Pemilihan Laptop",
        "3. Contoh 2: Seleksi Karyawan",
        "4. Contoh 3: Pemilihan Supplier",
        "5. Input Matriks Manual (Simulasi)"
    ]
)

# Inisialisasi variabel penampung data
data = None
weights = []
criteria_type = []

# -------------------------------------------------------------------------
# KONDISI MENU 1: STUDI KASUS UTAMA (MEROKOK)
# -------------------------------------------------------------------------
if opsi == "1. Studi Kasus: Kecanduan Merokok":
    st.subheader("📋 Analisis Faktor Kecanduan Merokok Berdasarkan Kelompok")
    st.markdown("Silakan simulasikan nilai matriks keputusan awal (Skala 1-5) langsung pada tabel di bawah ini:")
    
    # Matriks keputusan awal objek merokok
    default_merokok = {
        'Alternatif': ['Perokok Ringan (1-4 btg/hari)', 'Perokok Sedang (5-14 btg/hari)', 'Perokok Berat (>15 btg/hari)'],
        'Psikologis': [3.0, 4.0, 5.0],
        'Lingkungan': [4.5, 3.5, 2.5],
        'Kebiasaan': [2.5, 4.0, 5.0],
        'Ekonomi': [4.0, 3.0, 1.5],
        'Ketergantungan': [2.0, 3.5, 5.0],
        'Pengetahuan': [4.5, 3.0, 1.5]
    }
    df_merokok = pd.DataFrame(default_merokok)
    
    # Pengguna bisa mensimulasikan nilai kriteria langsung di layar
    data = st.data_editor(df_merokok, hide_index=True, use_container_width=True)
    
    weights = [0.15, 0.25, 0.20, 0.25, 0.10, 0.05]
    criteria_type = ['benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'cost']

# -------------------------------------------------------------------------
# KONDISI MENU 2: CONTOH LAPTOP (MURNI MODUL HAL. 9)
# -------------------------------------------------------------------------
elif opsi == "2. Contoh 1: Pemilihan Laptop":
    st.subheader("💻 Contoh 1: Pemilihan Laptop Terbaik")
    data = pd.DataFrame({
        'Alternatif': ['Laptop A', 'Laptop B', 'Laptop C', 'Laptop D', 'Laptop E'],
        'Harga (juta)': [8, 12, 15, 10, 9],
        'RAM (GB)': [8, 16, 32, 16, 8],
        'Storage (GB)': [256, 512, 1000, 512, 256],
        'Baterai (jam)': [6, 8, 5, 7, 9]
    })
    weights = [0.35, 0.25, 0.25, 0.15]
    criteria_type = ['cost', 'benefit', 'benefit', 'benefit']
    st.dataframe(data, hide_index=True, use_container_width=True)

# -------------------------------------------------------------------------
# KONDISI MENU 3: SELEKSI KARYAWAN (MURNI MODUL HAL. 10)
# -------------------------------------------------------------------------
elif opsi == "3. Contoh 2: Seleksi Karyawan":
    st.subheader("👥 Contoh 2: Seleksi Karyawan Terbaik")
    data = pd.DataFrame({
        'Alternatif': ['Andi', 'Budi', 'Cici', 'Dedi', 'Eka'],
        'Pengalaman (tahun)': [3, 5, 2, 4, 6],
        'Nilai Test': [85, 92, 78, 88, 95],
        'Gaji Ekspektasi (juta)': [8, 12, 6, 10, 15],
        'Usia': [25, 30, 28, 35, 32]
    })
    weights = [0.30, 0.35, 0.25, 0.10]
    criteria_type = ['benefit', 'benefit', 'cost', 'benefit']
    st.dataframe(data, hide_index=True, use_container_width=True)

# -------------------------------------------------------------------------
# KONDISI MENU 4: PEMILIHAN SUPPLIER (MURNI MODUL HAL. 11)
# -------------------------------------------------------------------------
elif opsi == "4. Contoh 3: Pemilihan Supplier":
    st.subheader("📦 Contoh 3: Pemilihan Supplier Terbaik")
    data = pd.DataFrame({
        'Alternatif': ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D'],
        'Harga': [45000, 48000, 42000, 46000],
        'Kualitas': [90, 85, 92, 88],
        'Pengiriman (hari)': [3, 5, 2, 4],
        'Pelayanan': [85, 80, 90, 75]
    })
    weights = [0.40, 0.30, 0.20, 0.10]
    criteria_type = ['cost', 'benefit', 'cost', 'benefit']
    st.dataframe(data, hide_index=True, use_container_width=True)

# -------------------------------------------------------------------------
# KONDISI MENU 5: MANUAL INPUT BERBASIS STRUKTUR MODUL
# -------------------------------------------------------------------------
else:
    st.subheader("🛠️ Simulasi Matriks Kustom Manual")
    
    col_config1, col_config2 = st.columns(2)
    with col_config1:
        n_alternatives = st.number_input("Jumlah alternatif", min_value=1, max_value=10, value=3)
    with col_config2:
        n_criteria = st.number_input("Jumlah kriteria", min_value=1, max_value=10, value=3)
        
    st.markdown("##### Konfigurasi Nama Kriteria & Tipe")
    columns_name = ["Alternatif"]
    for i in range(int(n_criteria)):
        c_col1, c_col2, c_col3 = st.columns([2, 2, 1])
        with c_col1:
            c_name = st.text_input(f"Nama Kriteria {i+1}", value=f"Kriteria {i+1}")
            columns_name.append(c_name)
        with c_col2:
            c_type = st.selectbox(f"Tipe {c_name}", ['benefit', 'cost'], key=f"type_{i}")
            criteria_type.append(c_type)
        with c_col3:
            w_val = st.number_input(f"Bobot {c_name}", min_value=0.0, max_value=1.0, value=0.1, step=0.05, key=f"w_{i}")
            weights.append(w_val)
            
    # Validasi Pembobotan Otomatis (Mengadopsi Baris 293-299 Modul)
    total_w = sum(weights)
    if abs(total_w - 1.0) > 0.001:
        st.warning(f"Peringatan: Total bobot ({total_w:.3f}) tidak sama dengan 1.0! Sistem menormalisasi otomatis.")
        weights = [w / total_w for w in weights]
        
    st.markdown("##### Isi Nilai Matriks Keputusan")
    blank_data = {"Alternatif": [f"Alternatif {i+1}" for i in range(int(n_alternatives))]}
    for col_name in columns_name[1:]:
        blank_data[col_name] = [1.0] * int(n_alternatives)
        
    df_blank = pd.DataFrame(blank_data)
    data = st.data_editor(df_blank, hide_index=True, use_container_width=True)

# =========================================================================
# PROSES EKSEKUSI & DISPLAY HASIL (Konversi Logika display_results() Modul)
# =========================================================================
if data is not None and len(weights) > 0:
    # Mengirim data ke Class murni bawaan modul
    saw = SAWMethod(data, weights, criteria_type)
    
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.markdown("### 📊 Parameter Analisis")
        st.write("**Bobot Kriteria:**", list(saw.weights))
        st.write("**Tipe Kriteria:**", saw.criteria_type)
        
        st.markdown("### 🧮 Matriks Hasil Normalisasi")
        # Pemanggilan fungsi normalisasi dari class modul
        df_norm_res = saw.normalize_matrix()
        st.dataframe(df_norm_res.round(4), hide_index=True, use_container_width=True)

    with col_res2:
        st.markdown("### 🏆 Hasil Akhir Perankingan")
        # Pemanggilan fungsi ranking dari class modul
        ranking = saw.get_ranking()
        st.dataframe(ranking.round(4), hide_index=True, use_container_width=True)
        
        # Penentuan Alternatif Terbaik (Sesuai Baris 176-180 Modul)
        best_alternative = ranking.iloc[0]['Alternatif']
        best_score = ranking.iloc[0]['Score']
        
        st.success(f"⭐ **ALTERNATIF TERBAIK:** {best_alternative}  \n🎯 **SKOR AKHIR:** {best_score:.4f}")
        
        # Visualisasi tambahan untuk memperkuat hasil ranking
        import plotly.express as px
        fig = px.bar(ranking, x="Alternatif", y="Score", text_auto='.4f', color="Score", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
