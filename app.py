import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Konfigurasi halaman utama Streamlit
st.set_page_config(
    page_title="SPK Pemilihan Rokok Unggulan - Warung Madura",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header Aplikasi
st.title("🏪 SPK Penentuan Produk Rokok Unggulan")
st.subheader("Metode Weighted Product (WP) Berdasarkan Preferensi Konsumen pada Warung Madura")
st.markdown("---")

# 1. SIDEBAR - PENGATURAN BOBOT KRITERIA
st.sidebar.header("⚙️ Pengaturan Bobot Kriteria")
st.sidebar.markdown("Silakan sesuaikan bobot awal kriteria (Skala 1 - 5):")

w_rasa = st.sidebar.slider("C1 - Kriteria Rasa", 1, 5, 5)
w_harga = st.sidebar.slider("C2 - Kriteria Harga", 1, 5, 4)
w_aroma = st.sidebar.slider("C3 - Kriteria Aroma", 1, 5, 3)
w_kemasan = st.sidebar.slider("C4 - Kriteria Desain Kemasan", 1, 5, 2)

# 2. PROSES MEMBACA DATA UPLOAD ATAU DEFAULT
# Menggunakan data dari file kuesioner Anda
file_path = "Data customer rokok - Form Responses 1 (1).csv"

try:
    df_kuesioner = pd.read_csv(file_path)
    
    # Rekap data alasan per merek rokok
    brands = ['Djarum 76', 'Sampoerna Mild', 'Gudang Garam Signature', 'Dji Sam Soe', 'Magnum Filter']
    summary_data = {}
    for brand in brands:
        summary_data[brand] = df_kuesioner[brand].value_counts().to_dict()
        
    df_matriks = pd.DataFrame(summary_data).fillna(0).astype(int)
    df_matriks = df_matriks.reindex(['Rasa', 'Harga', 'Aroma', 'Desain Kemasan'])
    
    # Matriks keputusan awal (X)
    X = df_matriks.T
    X.columns = ['C1', 'C2', 'C3', 'C4']
    X_skala = X.replace(0, 1)  # Menghindari nilai 0 dalam perhitungan pangkat WP
    
    # PEMBAGIAN TAB ANTARMUKA
    tab1, tab2, tab3 = st.tabs(["📊 Data Kuesioner & Matriks", "🧮 Proses Perhitungan WP", "🏆 Hasil Rekomendasi"])
    
    with tab1:
        st.header("📋 Data Hasil Survei Konsumen")
        st.write("Berikut adalah total frekuensi alasan yang dipilih responden untuk setiap merek rokok:")
        st.dataframe(df_matriks, use_container_width=True)
        
        st.header("🔢 Matriks Keputusan (X)")
        st.caption("Catatan: Nilai 0 dikonversi menjadi 1 untuk menjaga kestabilan perkalian pangkat metode WP.")
        st.dataframe(X_skala, use_container_width=True)
        
    with tab2:
        st.header("🧮 Perhitungan Manual Sistem (Sesuai Modul)")
        
        # a. Perbaikan Bobot
        st.subheader("a. Perbaikan Bobot ($W_j$)")
        w_awal = np.array([w_rasa, w_harga, w_aroma, w_kemasan])
        total_w = np.sum(w_awal)
        wj = w_awal / total_w
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("W1 (Rasa)", f"{wj[0]:.4f}", f"Awal: {w_rasa}")
        col2.metric("W2 (Harga)", f"{wj[1]:.4f}", f"Awal: {w_harga}")
        col3.metric("W3 (Aroma)", f"{wj[2]:.4f}", f"Awal: {w_aroma}")
        col4.metric("W4 (Kemasan)", f"{wj[3]:.4f}", f"Awal: {w_kemasan}")
        
        # b. Perhitungan Vektor S
        st.subheader("b. Perhitungan Vektor ($S_i$)")
        S = []
        rumus_s_list = []
        
        for indeks, row in X_skala.iterrows():
            s_i = (row['C1']**wj[0]) * (row['C2']**wj[1]) * (row['C3']**wj[2]) * (row['C4']**wj[3])
            S.append(s_i)
            rumus_text = f"**S_{indeks}**: ({row['C1']}^{wj[0]:.3f}) × ({row['C2']}^{wj[1]:.3f}) × ({row['C3']}^{wj[2]:.3f}) × ({row['C4']}^{wj[3]:.3f}) = **{s_i:.4f}**"
            st.markdown(rumus_text)
            
        total_S = np.sum(S)
        st.info(f"**Total Nilai Vektor S ($\Sigma S_i$)** = {total_S:.4f}")
        
        # c. Perhitungan Vektor V
        st.subheader("c. Perhitungan Vektor Preferensi ($V_i$)")
        V = [s_i / total_S for s_i in S]
        for i, brand in enumerate(X_skala.index):
            st.markdown(f"**V_{brand}** = {S[i]:.4f} / {total_S:.4f} = **{V[i]:.4f}**")
            
    with tab3:
        st.header("🏆 Peringkat Produk Rokok Unggulan")
        
        # Menggabungkan hasil ke Dataframe
        hasil_df = pd.DataFrame({
            'Merek Rokok (Alternatif)': X_skala.index,
            'Nilai Vektor S': S,
            'Nilai Preferensi (V)': V
        })
        
        # Pengurutan Ranking
        hasil_df = hasil_df.sort_values(by='Nilai Preferensi (V)', ascending=False).reset_index(drop=True)
        hasil_df.index = hasil_df.index + 1
        
        # Memisahkan kolom pemenang utama untuk highlight widget
        pemenang_nama = hasil_df.iloc[0]['Merek Rokok (Alternatif)']
        pemenang_skor = hasil_df.iloc[0]['Nilai Preferensi (V)']
        
        st.success(f"🎉 **Rekomendasi Utama:** Produk Rokok Unggulan yang paling direkomendasikan untuk ditambah stoknya di Warung Madura adalah **{pemenang_nama}** dengan nilai preferensi sebesar **{pemenang_skor:.4f}**.")
        
        # Tampilkan Tabel Final
        st.dataframe(hasil_df.style.format({'Nilai Vektor S': '{:.4f}', 'Nilai Preferensi (V)': '{:.4f}'}), use_container_width=True)
        
        # Visualisasi Chart
        st.subheader("📊 Grafik Perbandingan Nilai Preferensi (V)")
        fig = px.bar(
            hasil_df, 
            x='Nilai Preferensi (V)', 
            y='Merek Rokok (Alternatif)', 
            orientation='h',
            color='Nilai Preferensi (V)',
            color_continuous_scale='Blues',
            text_auto='.4f'
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

except FileNotFoundError:
    st.error(f"Berkas '{file_path}' tidak ditemukan. Pastikan Anda sudah mengunggah berkas CSV tersebut ke dalam folder project Anda.")
