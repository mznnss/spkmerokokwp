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
        self.data = data.copy() [cite: 96]
        self.weights = np.array(weights) [cite: 97]
        self.criteria_type = criteria_type [cite: 98]
        self.normalized_data = None [cite: 99]
        self.scores = None [cite: 100]

    def normalize_matrix(self) -> pd.DataFrame:
        normalized_data = self.data.copy() [cite: 103]
        for i, col in enumerate(self.data.columns[1:]): [cite: 104]
            if self.criteria_type[i] == 'benefit': [cite: 105]
                max_val = self.data[col].max() [cite: 108]
                if max_val == 0: [cite: 109]
                    normalized_data[col] = 0 [cite: 110]
                else:
                    normalized_data[col] = self.data[col] / max_val [cite: 112]
            else: # cost
                min_val = self.data[col].min() [cite: 115]
                normalized_data[col] = np.where( [cite: 117]
                    self.data[col] != 0, [cite: 119]
                    min_val / self.data[col], [cite: 120]
                    0 [cite: 121]
                )
        self.normalized_data = normalized_data [cite: 122]
        return normalized_data [cite: 123]

    def calculate_scores(self) -> pd.DataFrame:
        if self.normalized_data is None: [cite: 126]
            self.normalize_matrix() [cite: 127]
        criteria_columns = self.normalized_data.columns[1:] [cite: 129]
        weighted_scores = self.normalized_data[criteria_columns] * self.weights [cite: 130]
        self.normalized_data['Score'] = weighted_scores.sum(axis=1) [cite: 132]
        self.normalized_data['Rank'] = self.normalized_data['Score'].rank(ascending=False, method='min').astype(int) [cite: 134]
        return self.normalized_data [cite: 135]

    def get_ranking(self) -> pd.DataFrame:
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
st.caption("Aplikasi dioptimalkan dari modul pemrograman ke dalam framework Streamlit")
st.markdown("---")

# Sidebar Menu Navigasi [Pengganti struktur Menu pada modul] [cite: 313, 314]
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
nama_kriteria = []

# -------------------------------------------------------------------------
# KONDISI MENU 1: STUDI KASUS UTAMA (MEROKOK)
# -------------------------------------------------------------------------
if opsi == "1. Studi Kasus: Kecanduan Merokok":
    st.subheader("📋 Analisis Faktor Kecanduan Merokok Berdasarkan Kelompok")
    st.markdown("Silakan simulasikan nilai matriks keputusan awal (Skala 1-5) langsung pada tabel di bawah ini:")
    
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
    
    nama_kriteria = ['Psikologis', 'Lingkungan', 'Kebiasaan', 'Ekonomi', 'Ketergantungan', 'Pengetahuan']
    weights = [0.15, 0.25, 0.20, 0.25, 0.10, 0.05]
    criteria_type = ['benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'cost']

# -------------------------------------------------------------------------
# KONDISI MENU 2: CONTOH LAPTOP (MURNI MODUL HAL. 9)
# -------------------------------------------------------------------------
elif opsi == "2. Contoh 1: Pemilihan Laptop":
    st.subheader("💻 Contoh 1: Pemilihan Laptop Terbaik")
    data = pd.DataFrame({
        'Alternatif': ['Laptop A', 'Laptop B', 'Laptop C', 'Laptop D', 'Laptop E'],
        'Harga (juta)': [8, 12, 15, 10, 9], [cite: 191]
        'RAM (GB)': [8, 16, 32, 16, 8], [cite: 193]
        'Storage (GB)': [256, 512, 1000, 512, 256], [cite: 195]
        'Baterai (jam)': [6, 8, 5, 7, 9] [cite: 196]
    })
    nama_kriteria = ['Harga (juta)', 'RAM (GB)', 'Storage (GB)', 'Baterai (jam)']
    weights = [0.35, 0.25, 0.25, 0.15] [cite: 200]
    criteria_type = ['cost', 'benefit', 'benefit', 'benefit'] [cite: 202]
    st.dataframe(data, hide_index=True, use_container_width=True)

# -------------------------------------------------------------------------
# KONDISI MENU 3: SELEKSI KARYAWAN (MURNI MODUL HAL. 10)
# -------------------------------------------------------------------------
elif opsi == "3. Contoh 2: Seleksi Karyawan":
    st.subheader("👥 Contoh 2: Seleksi Karyawan Terbaik")
    data = pd.DataFrame({
        'Alternatif': ['Andi', 'Budi', 'Cici', 'Dedi', 'Eka'], [cite: 213]
        'Pengalaman (tahun)': [3, 5, 2, 4, 6], [cite: 215]
        'Nilai Test': [85, 92, 78, 88, 95], [cite: 217]
        'Gaji Ekspektasi (juta)': [8, 12, 6, 10, 15], [cite: 219]
        'Usia': [25, 30, 28, 35, 32] [cite: 220]
    })
    nama_kriteria = ['Pengalaman (tahun)', 'Nilai Test', 'Gaji Ekspektasi (juta)', 'Usia']
    weights = [0.30, 0.35, 0.25, 0.10] [cite: 222]
    criteria_type = ['benefit', 'benefit', 'cost', 'benefit'] [cite: 223]
    st.dataframe(data, hide_index=True, use_container_width=True)

# -------------------------------------------------------------------------
# KONDISI MENU 4: PEMILIHAN SUPPLIER (MURNI MODUL HAL. 11)
# -------------------------------------------------------------------------
elif opsi == "4. Contoh 3: Pemilihan Supplier":
    st.subheader("📦 Contoh 3: Pemilihan Supplier Terbaik")
    data = pd.DataFrame({
        'Alternatif': ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D'], [cite: 232]
        'Harga': [45000, 48000, 42000, 46000], [cite: 233]
        'Kualitas': [90, 85, 92, 88], [cite: 234]
        'Pengiriman (hari)': [3, 5, 2, 4], [cite: 236]
        'Pelayanan': [85, 80, 90, 75] [cite: 238]
    })
    nama_kriteria = ['Harga', 'Kualitas', 'Pengiriman (hari)', 'Pelayanan']
    weights = [0.40, 0.30, 0.20, 0.10] [cite: 241]
    criteria_type = ['cost', 'benefit', 'cost', 'benefit'] [cite: 242]
    st.dataframe(data, hide_index=True, use_container_width=True)

# -------------------------------------------------------------------------
# KONDISI MENU 5: MANUAL INPUT BERBASIS STRUKTUR MODUL
# -------------------------------------------------------------------------
else:
    st.subheader("🛠️ Simulasi Matriks Kustom Manual")
    
    col_config1, col_config2 = st.columns(2)
    with col_config1:
        n_alternatives = st.number_input("Jumlah alternatif", min_value=1, max_value=10, value=3) [cite: 254]
    with col_config2:
        n_criteria = st.number_input("Jumlah kriteria", min_value=1, max_value=10, value=3) [cite: 255]
        
    st.markdown("##### Konfigurasi Nama Kriteria & Tipe")
    columns_name = ["Alternatif"]
    for i in range(int(n_criteria)):
        c_col1, c_col2, c_col3 = st.columns([2, 2, 1])
        with c_col1:
            c_name = st.text_input(f"Nama Kriteria {i+1}", value=f"Kriteria {i+1}") [cite: 268]
            columns_name.append(c_name)
            nama_kriteria.append(c_name)
        with c_col2:
            c_type = st.selectbox(f"Tipe {c_name}", ['benefit', 'cost'], key=f"type_{i}") [cite: 269]
            criteria_type.append(c_type)
        with c_col3:
            w_val = st.number_input(f"Bobot {c_name}", min_value=0.0, max_value=1.0, value=0.1, step=0.05, key=f"w_{i}") [cite: 290]
            weights.append(w_val)
            
    # Validasi Pembobotan Otomatis (Mengadopsi Baris 293-299 Modul)
    total_w = sum(weights) [cite: 293]
    if abs(total_w - 1.0) > 0.001: [cite: 294]
        st.warning(f"Peringatan: Total bobot ({total_w:.3f}) tidak sama dengan 1.0! Sistem menormalisasi otomatis.") [cite: 295]
        weights = [w / total_w for w in weights] [cite: 298]
        
    st.markdown("##### Isi Nilai Matriks Keputusan") [cite: 276]
    blank_data = {"Alternatif": [f"Alternatif {i+1}" for i in range(int(n_alternatives))]} [cite: 277]
    for col_name in columns_name[1:]:
        blank_data[col_name] = [1.0] * int(n_alternatives)
        
    df_blank = pd.DataFrame(blank_data) [cite: 285]
    data = st.data_editor(df_blank, hide_index=True, use_container_width=True)

# =========================================================================
# PROSES EKSEKUSI & DISPLAY HASIL (Konversi Logika display_results() Modul)
# =========================================================================
if data is not None and len(weights) > 0:
    # Mengirim data ke Class murni bawaan modul
    saw = SAWMethod(data, weights, criteria_type) [cite: 204]
    
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.markdown("### 📊 Parameter Analisis")
        
        # PERBAIKAN VISUALISASI: Mengubah list cetakan mentah menjadi tabel DataFrame yang rapi
        df_parameter = pd.DataFrame({
            "Kriteria": nama_kriteria,
            "Bobot Preferensi (W)": saw.weights, [cite: 157]
            "Tipe Atribut": saw.criteria_type [cite: 158]
        })
        st.dataframe(df_parameter, hide_index=True, use_container_width=True)
        
        st.markdown("### 🧮 Matriks Hasil Normalisasi") [cite: 159, 160]
        # Pemanggilan fungsi normalisasi dari class modul
        df_norm_res = saw.normalize_matrix() [cite: 127]
        st.dataframe(df_norm_res.round(4), hide_index=True, use_container_width=True)

    with col_res2:
        st.markdown("### 🏆 Hasil Akhir Perankingan") [cite: 169]
        # Pemanggilan fungsi ranking dari class modul
        ranking = saw.get_ranking() [cite: 170]
        st.dataframe(ranking.round(4), hide_index=True, use_container_width=True)
        
        # Penentuan Alternatif Terbaik (Sesuai Baris 176-180 Modul)
        best_alternative = ranking.iloc[0]['Alternatif'] [cite: 176]
        best_score = ranking.iloc[0]['Score'] [cite: 177]
        
        st.success(f"⭐ **ALTERNATIF TERBAIK:** {best_alternative}  \n🎯 **SKOR AKHIR:** {best_score:.4f}") [cite: 178, 180]
        
        # Visualisasi grafik batang untuk memperkuat hasil ranking
        import plotly.express as px
        fig = px.bar(ranking, x="Alternatif", y="Score", text_auto='.4f', color="Score", color_continuous_scale="Blugrn", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
