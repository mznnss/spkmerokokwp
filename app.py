import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(
    page_title="SPK Faktor Kecanduan Merokok",
    page_icon="🚭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi session state untuk menampung simulasi data kuesioner mandiri
if 'kuesioner_data' not in st.session_state:
    st.session_state.kuesioner_data = pd.DataFrame(columns=[
        "Nama Responden", "Psikologis", "Lingkungan", "Kebiasaan", "Ekonomi", "Ketergantungan", "Pengetahuan"
    ])

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
.main { background-color: #0f172a; }
[data-testid="stSidebar"] { background-color: #111827; }
.card {
    background: linear-gradient(135deg,#1e293b,#0f172a);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #334155;
    text-align: center;
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
}
.card h3 { color: white; font-size: 20px; }
.card p { color: #38bdf8; font-size: 28px; font-weight: bold; }
.title { font-size: 42px; font-weight: bold; color: white; }
.subtitle { color: #94a3b8; font-size: 18px; }
.stSpinner > div { border-top-color: #38bdf8 !important; }
.block-container { padding-top: 1rem; background: linear-gradient(180deg,#020617,#0f172a); }
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown('<div class="title">🚭 SPK Faktor Penyebab Kecanduan Merokok</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Metode Simple Additive Weighting (SAW) Berdasarkan Tipe Kriteria</div>', unsafe_allow_html=True)
st.markdown("---")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📌 Menu")
menu = st.sidebar.radio(
    "Navigasi",
    ["Dashboard", "Analisis SAW", "Tentang Sistem"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔌 Sumber Data")

sumber_data = st.sidebar.radio(
    "Pilih Metode Input:",
    ["Upload Excel Google Form", "Mode Simulasi (Slider)", "Mode Simulasi (Isi Kuesioner Form)"]
)

# Inisialisasi variabel utama
df = None
criteria_scores = {}
total_responden = 0
siap_hitung = False

mapping = {
    "Sangat Tidak Setuju": 1,
    "Tidak Setuju": 2,
    "Netral": 3,
    "Setuju": 4,
    "Sangat Setuju": 5
}

# =========================
# BOBOT & TIPE KRITERIA (SESUAI DOKUMEN PANDUAN)
# =========================
weights = {
    "Psikologis": 0.15,
    "Lingkungan": 0.25,
    "Kebiasaan": 0.20,
    "Ekonomi": 0.25,
    "Ketergantungan": 0.10,
    "Pengetahuan": 0.05
}

# Penentuan tipe kriteria berdasarkan dokumen pembimbing
criteria_types = {
    "Psikologis": "benefit",
    "Lingkungan": "benefit",
    "Kebiasaan": "benefit",
    "Ekonomi": "benefit",
    "Ketergantungan": "benefit",
    "Pengetahuan": "cost"  # Pengetahuan tinggi = menekan tingkat kecanduan
}

# =========================
# KONDISI 1: UPLOAD EXCEL
# =========================
if sumber_data == "Upload Excel Google Form":
    uploaded_file = st.sidebar.file_uploader("📂 Upload Excel Google Form", type=["xlsx", "xls"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        total_responden = len(df)
        df_numeric = df.replace(mapping)
        
        psikologis_cols = [col for col in df_numeric.columns if "stres" in col.lower() or "sulit berhenti" in col.lower() or "tidak nyaman" in col.lower()]
        lingkungan_cols = [col for col in df_numeric.columns if "teman" in col.lower() or "lingkungan" in col.lower() or "berkumpul" in col.lower()]
        kebiasaan_cols = [col for col in df_numeric.columns if "rutinitas" in col.lower() or "setelah makan" in col.lower() or "tanpa sadar" in col.lower()]
        ekonomi_cols = [col for col in df_numeric.columns if "mudah didapat" in col.lower() or "harga" in col.lower()]
        ketergantungan_cols = [col for col in df_numeric.columns if "ingin merokok" in col.lower() or "mengurangi" in col.lower()]
        pengetahuan_cols = [col for col in df_numeric.columns if "bahaya" in col.lower() or "berbahaya" in col.lower()]
        
        def avg_cols(cols):
            return df_numeric[cols].astype(float).mean().mean() if len(cols) > 0 else 0
            
        criteria_scores = {
            "Psikologis": avg_cols(psikologis_cols),
            "Lingkungan": avg_cols(lingkungan_cols),
            "Kebiasaan": avg_cols(kebiasaan_cols),
            "Ekonomi": avg_cols(ekonomi_cols),
            "Ketergantungan": avg_cols(ketergantungan_cols),
            "Pengetahuan": avg_cols(pengetahuan_cols)
        }
        siap_hitung = True
    else:
        st.info("⬅️ Silakan upload file Excel terlebih dahulu dari sidebar")

# =========================
# KONDISI 2: SIMULASI SLIDER
# =========================
elif sumber_data == "Mode Simulasi (Slider)":
    st.sidebar.markdown("**Geser nilai kriteria (Skala 1-5):**")
    criteria_scores = {
        "Psikologis": st.sidebar.slider("🧠 Faktor Psikologis (Benefit)", 1.0, 5.0, 3.5, 0.1),
        "Lingkungan": st.sidebar.slider("👥 Faktor Lingkungan (Benefit)", 1.0, 5.0, 4.0, 0.1),
        "Kebiasaan": st.sidebar.slider("🔄 Faktor Kebiasaan (Benefit)", 1.0, 5.0, 3.8, 0.1),
        "Ekonomi": st.sidebar.slider("💰 Faktor Ekonomi (Benefit)", 1.0, 5.0, 3.0, 0.1),
        "Ketergantungan": st.sidebar.slider("⚡ Faktor Ketergantungan (Benefit)", 1.0, 5.0, 4.2, 0.1),
        "Pengetahuan": st.sidebar.slider("📚 Faktor Pengetahuan (Cost)", 1.0, 5.0, 2.5, 0.1)
    }
    total_responden = "Simulasi Kontrol Slider"
    siap_hitung = True

# =========================
# KONDISI 3: SIMULASI FORM KUESIONER
# =========================
else:
    st.subheader("📝 Form Simulasi Pengisian Kuesioner")
    
    with st.form(key="kuesioner_form", clear_on_submit=True):
        nama = st.text_input("Nama Responden", value=f"Responden {len(st.session_state.kuesioner_data)+1}")
        options = ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]
        
        q1 = st.radio("1. Apakah Anda merokok saat merasa stres/tertekan? (Psikologis)", options, index=3, horizontal=True)
        q2 = st.radio("2. Apakah Anda sulit menolak merokok di lingkungan teman-teman? (Lingkungan)", options, index=3, horizontal=True)
        q3 = st.radio("3. Apakah merokok setelah makan sudah menjadi rutinitas wajib? (Kebiasaan)", options, index=4, horizontal=True)
        q4 = st.radio("4. Apakah harga rokok saat ini murah dan sangat mudah didapat? (Ekonomi)", options, index=3, horizontal=True)
        q5 = st.radio("5. Apakah Anda merasa selalu ingin merokok kembali setiap jam? (Ketergantungan)", options, index=2, horizontal=True)
        q6 = st.radio("6. Apakah Anda tahu info bahaya rokok bagi kesehatan tubuh? (Pengetahuan)", options, index=3, horizontal=True)
        
        submit_btn = st.form_submit_button(label="💾 Kirim Jawaban Kuesioner")
        
        if submit_btn:
            new_row = {
                "Nama Responden": nama,
                "Psikologis": mapping[q1],
                "Lingkungan": mapping[q2],
                "Kebiasaan": mapping[q3],
                "Ekonomi": mapping[q4],
                "Ketergantungan": mapping[q5],
                "Pengetahuan": mapping[q6]
            }
            st.session_state.kuesioner_data = pd.concat([st.session_state.kuesioner_data, pd.DataFrame([new_row])], ignore_index=True)
            st.toast(f"Berhasil menyimpan data {nama}!", icon="✅")
            st.rerun()

    if len(st.session_state.kuesioner_data) > 0:
        if st.button("🗑️ Reset/Hapus Semua Responden Form"):
            st.session_state.kuesioner_data = pd.DataFrame(columns=["Nama Responden", "Psikologis", "Lingkungan", "Kebiasaan", "Ekonomi", "Ketergantungan", "Pengetahuan"])
            st.rerun()

    if not st.session_state.kuesioner_data.empty:
        df = st.session_state.kuesioner_data
        total_responden = len(df)
        criteria_scores = {col: df[col].mean() for col in weights.keys()}
        siap_hitung = True
    else:
        st.warning("⚠️ Belum ada data kuesioner yang diisi. Silakan isi form di atas dan klik 'Kirim Jawaban Kuesioner'.")

# =========================
# PEMROSESAN LOGIKA SAW AKURAT (BENEFIT VS COST)
# =========================
if siap_hitung:
    # Mengambil nilai max dan min global dari skor kriteria untuk normalisasi
    max_val = max(criteria_scores.values()) if max(criteria_scores.values()) > 0 else 1
    min_val = min(criteria_scores.values()) if min(criteria_scores.values()) > 0 else 1
    
    # Penerapan rumus normalisasi berbasis tipe kriteria dari dokumen [Teks Sumber: 105-121]
    normalized_scores = {}
    for key, value in criteria_scores.items():
        if criteria_types[key] == "benefit":
            normalized_scores[key] = value / max_val if max_val > 0 else 0 [cite: 112]
        else: # cost
            normalized_scores[key] = min_val / value if value > 0 else 0 [cite: 120]
            
    # Perhitungan perkalian nilai normalisasi dengan bobot [Teks Sumber: 57, 130]
    final_scores = {k: normalized_scores[k] * weights[k] for k in criteria_scores.keys()}
    
    # Penyusunan Ranking
    ranking_df = pd.DataFrame({"Faktor": list(final_scores.keys()), "Nilai SAW": list(final_scores.values())})
    ranking_df = ranking_df.sort_values(by="Nilai SAW", ascending=False).reset_index(drop=True)
    
    top_factor = ranking_df.iloc[0]["Faktor"]
    top_score = ranking_df.iloc[0]["Nilai SAW"]
    
    criteria_df = pd.DataFrame({
        "Faktor": list(criteria_scores.keys()), 
        "Nilai Rata-rata": list(criteria_scores.values()),
        "Tipe Kriteria": [criteria_types[k] for k in criteria_scores.keys()]
    })

    # =========================
    # MENU: DASHBOARD
    # =========================
    if menu == "Dashboard":
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(f'<div class="card"><h3>Total Responden</h3><p>{total_responden}</p></div>', unsafe_allow_html=True)
        with col2: st.markdown(f'<div class="card"><h3>Faktor Dominan</h3><p>{top_factor}</p></div>', unsafe_allow_html=True)
        with col3: st.markdown(f'<div class="card"><h3>Nilai Tertinggi</h3><p>{top_score:.3f}</p></div>', unsafe_allow_html=True)
            
        st.markdown("---")
        st.subheader("📊 Grafik Faktor Penyebab (Nilai Akhir SAW)")
        fig = px.bar(ranking_df, x="Faktor", y="Nilai SAW", text_auto='.3f', template="plotly_dark", color="Nilai SAW")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🥧 Persentase Proporsi Faktor")
        pie = px.pie(ranking_df, values="Nilai SAW", names="Faktor", template="plotly_dark")
        st.plotly_chart(pie, use_container_width=True)

    # =========================
    # MENU: ANALISIS SAW
    # =========================
    elif menu == "Analisis SAW":
        st.subheader("📄 Data Responden yang Diolah")
        if df is not None:
            st.dataframe(df)
        else:
            st.info("Mode Simulasi Slider Aktif: Tidak menggunakan basis data tabel.")
            
        st.subheader("📊 Nilai Kriteria & Atribut Tipe")
        st.dataframe(criteria_df)
        
        st.subheader("🏆 Peringkat Akhir Faktor Penyebab")
        st.dataframe(ranking_df)
        
        st.success(f"🎯 Kesimpulan: Faktor paling dominan memicu kecanduan merokok adalah **{top_factor}** dengan pencapaian nilai SAW sebesar **{top_score:.3f}**.")
