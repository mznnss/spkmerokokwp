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
.main {
    background-color: #0f172a;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

.card {
    background: linear-gradient(135deg,#1e293b,#0f172a);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #334155;
    text-align: center;
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
}

.card h3 {
    color: white;
    font-size: 20px;
}

.card p {
    color: #38bdf8;
    font-size: 28px;
    font-weight: bold;
}

.title {
    font-size: 42px;
    font-weight: bold;
    color: white;
}

.subtitle {
    color: #94a3b8;
    font-size: 18px;
}

.stSpinner > div {
    border-top-color: #38bdf8 !important;
}

.block-container {
    padding-top: 1rem;
    background: linear-gradient(180deg,#020617,#0f172a);
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown('<div class="title">🚭 SPK Faktor Penyebab Kecanduan Merokok</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Metode Simple Additive Weighting (SAW)</div>', unsafe_allow_html=True)
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

# Pilihan Mode Data (Gabungan Fitur Asli & Simulasi Slider & Simulasi Kuesioner)
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
# BOBOT
# =========================
weights = {
    "Psikologis": 0.15,
    "Lingkungan": 0.25,
    "Kebiasaan": 0.20,
    "Ekonomi": 0.25,
    "Ketergantungan": 0.10,
    "Pengetahuan": 0.05
}

# =========================
# KONDISI 1: MODE UPLOAD EXCEL
# =========================
if sumber_data == "Upload Excel Google Form":
    uploaded_file = st.sidebar.file_uploader(
        "📂 Upload Excel Google Form",
        type=["xlsx", "xls"]
    )
    
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
            if len(cols) > 0:
                return df_numeric[cols].astype(float).mean().mean()
            return 0
            
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
# KONDISI 2: MODE SIMULASI SLIDER
# =========================
elif sumber_data == "Mode Simulasi (Slider)":
    st.sidebar.markdown("**Geser nilai kriteria (Skala 1-5):**")
    sim_psikologis = st.sidebar.slider("🧠 Faktor Psikologis", 1.0, 5.0, 3.5, 0.1)
    sim_lingkungan = st.sidebar.slider("👥 Faktor Lingkungan", 1.0, 5.0, 4.0, 0.1)
    sim_kebiasaan = st.sidebar.slider("🔄 Faktor Kebiasaan", 1.0, 5.0, 3.8, 0.1)
    sim_ekonomi = st.sidebar.slider("💰 Faktor Ekonomi", 1.0, 5.0, 3.0, 0.1)
    sim_ketergantungan = st.sidebar.slider("⚡ Faktor Ketergantungan", 1.0, 5.0, 4.2, 0.1)
    sim_pengetahuan = st.sidebar.slider("📚 Faktor Pengetahuan", 1.0, 5.0, 2.5, 0.1)
    
    criteria_scores = {
        "Psikologis": sim_psikologis,
        "Lingkungan": sim_lingkungan,
        "Kebiasaan": sim_kebiasaan,
        "Ekonomi": sim_ekonomi,
        "Ketergantungan": sim_ketergantungan,
        "Pengetahuan": sim_pengetahuan
    }
    total_responden = "Simulasi Kontrol Slider"
    siap_hitung = True

# =========================
# KONDISI 3: MODE SIMULASI ISI KUESIONER FORM
# =========================
else:
    st.subheader("📝 Form Simulasi Pengisian Kuesioner")
    
    # Formulir Kuesioner Internal
    with st.form(key="kuesioner_form", clear_on_submit=True):
        nama = st.text_input("Nama Responden", value=f"Responden {len(st.session_state.kuesioner_data) + 1}")
        
        options = ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]
        
        q1 = st.radio("1. Apakah Anda merokok atau menambah porsi rokok saat merasa stres/tertekan? (Psikologis)", options, index=3, horizontal=True)
        q2 = st.radio("2. Apakah Anda sulit menolak merokok jika berada di lingkungan teman-teman perokok? (Lingkungan)", options, index=3, horizontal=True)
        q3 = st.radio("3. Apakah merokok setelah makan sudah menjadi rutinitas wajib yang sulit ditinggalkan? (Kebiasaan)", options, index=4, horizontal=True)
        q4 = st.radio("4. Apakah rokok saat ini harganya murah dan sangat mudah didapat di sekitar Anda? (Ekonomi)", options, index=3, horizontal=True)
        q5 = st.radio("5. Apakah Anda merasa selalu ingin merokok kembali dan gelisah jika belum merokok? (Ketergantungan)", options, index=2, horizontal=True)
        q6 = st.radio("6. Apakah Anda tetap merokok meskipun tahu info bahaya rokok bagi kesehatan? (Pengetahuan)", options, index=3, horizontal=True)
        
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
            # Tambahkan baris data responden baru ke session state
            st.session_state.kuesioner_data = pd.concat([st.session_state.kuesioner_data, pd.DataFrame([new_row])], ignore_index=True)
            st.toast(f"Berhasil menyimpan data {nama}!", icon="✅")
            st.rerun()

    # Tombol Reset Data Form
    if len(st.session_state.kuesioner_data) > 0:
        if st.button("🗑️ Reset/Hapus Semua Responden Form"):
            st.session_state.kuesioner_data = pd.DataFrame(columns=["Nama Responden", "Psikologis", "Lingkungan", "Kebiasaan", "Ekonomi", "Ketergantungan", "Pengetahuan"])
            st.rerun()

    # Hitung rata-rata kuesioner dari data yang telah dikumpulkan
    if not st.session_state.kuesioner_data.empty:
        df = st.session_state.kuesioner_data
        total_responden = len(df)
        
        criteria_scores = {
            "Psikologis": df["Psikologis"].mean(),
            "Lingkungan": df["Lingkungan"].mean(),
            "Kebiasaan": df["Kebiasaan"].mean(),
            "Ekonomi": df["Ekonomi"].mean(),
            "Ketergantungan": df["Ketergantungan"].mean(),
            "Pengetahuan": df["Pengetahuan"].mean()
        }
        siap_hitung = True
    else:
        st.warning("⚠️ Belum ada data kuesioner yang diisi. Silakan isi form di atas dan klik 'Kirim Jawaban Kuesioner'.")

# =========================
# PEMROSESAN METODE SAW
# =========================
if siap_hitung:
    max_value = max(criteria_scores.values()) if max(criteria_scores.values()) > 0 else 1
    
    normalized_scores = {
        key: value / max_value
        for key, value in criteria_scores.items()
    }
    
    final_scores = {
        key: normalized_scores[key] * weights[key]
        for key in criteria_scores.keys()
    }
    
    ranking_df = pd.DataFrame({
        "Faktor": list(final_scores.keys()),
        "Nilai SAW": list(final_scores.values())
    })
    
    ranking_df = ranking_df.sort_values(by="Nilai SAW", ascending=False)
    ranking_df.reset_index(drop=True, inplace=True)
    
    top_factor = ranking_df.iloc[0]["Faktor"]
    top_score = ranking_df.iloc[0]["Nilai SAW"]
    
    criteria_df = pd.DataFrame({
        "Faktor": list(criteria_scores.keys()),
        "Nilai": list(criteria_scores.values())
    })

    # =========================
    # MENU: DASHBOARD
    # =========================
    if menu == "Dashboard":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f'''
            <div class="card">
                <h3>Total Responden</h3>
                <p>{total_responden}</p>
            </div>
            ''', unsafe_allow_html=True)
            
        with col2:
            st.markdown(f'''
            <div class="card">
                <h3>Faktor Dominan</h3>
                <p>{top_factor}</p>
            </div>
            ''', unsafe_allow_html=True)
            
        with col3:
            st.markdown(f'''
            <div class="card">
                <h3>Nilai Tertinggi</h3>
                <p>{top_score:.3f}</p>
            </div>
            ''', unsafe_allow_html=True)
            
        st.markdown("---")
        
        st.subheader("📊 Grafik Faktor Penyebab")
        fig = px.bar(
            ranking_df,
            x="Faktor",
            y="Nilai SAW",
            text_auto='.3f',
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🥧 Persentase Faktor")
        pie = px.pie(
            ranking_df,
            values="Nilai SAW",
            names="Faktor",
            template="plotly_dark"
        )
        st.plotly_chart(pie, use_container_width=True)

    # =========================
    # MENU: ANALISIS SAW
    # =========================
    elif menu == "Analisis SAW":
        if df is not None:
            st.subheader("📄 Data Responden")
            st.dataframe(df)
        else:
            st.subheader("📄 Data Responden")
            st.info("Mode Simulasi Slider Aktif: Data mentah tabel individual tidak dimuat.")
            
        st.subheader("📊 Nilai Rata-rata Faktor")
        st.dataframe(criteria_df)
        
        st.subheader("🏆 Ranking Faktor Penyebab")
        st.dataframe(ranking_df)
        
        st.success(
            f"🎯 Faktor paling dominan adalah {top_factor} dengan nilai {top_score:.3f}"
        )
        
        # EXPORT CSV
        csv = ranking_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Hasil CSV",
            data=csv,
            file_name='hasil_saw.csv',
            mime='text/csv'
        )
        
        # =========================
        # EXPORT PDF LENGKAP
        # =========================
        def create_pdf(dataframe, criteria_df, top_factor, top_score, total_resp):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            title = Paragraph("<b>Sistem Pendukung Keputusan Faktor Penyebab Kecanduan Merokok</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            subtitle = Paragraph("Metode Simple Additive Weighting (SAW)", styles['Heading2'])
            elements.append(subtitle)
            elements.append(Spacer(1, 20))
            
            info = Paragraph(
                f"Jumlah responden: <b>{total_resp}</b><br/>"
                f"Faktor dominan: <b>{top_factor}</b><br/>"
                f"Nilai tertinggi SAW: <b>{top_score:.3f}</b>",
                styles['BodyText']
            )
            elements.append(info)
            elements.append(Spacer(1, 20))
            
            rata_title = Paragraph("<b>Tabel Nilai Rata-rata Faktor</b>", styles['Heading3'])
            elements.append(rata_title)
            elements.append(Spacer(1, 10))
            
            criteria_table_data = [list(criteria_df.columns)] + criteria_df.values.tolist()
            criteria_table = Table(criteria_table_data)
            criteria_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ]))
            elements.append(criteria_table)
            elements.append(Spacer(1, 20))
            
            ranking_title = Paragraph("<b>Tabel Ranking Faktor Penyebab</b>", styles['Heading3'])
            elements.append(ranking_title)
            elements.append(Spacer(1, 10))
            
            ranking_table_data = [list(dataframe.columns)] + dataframe.values.tolist()
            ranking_table = Table(ranking_table_data)
            ranking_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ]))
            elements.append(ranking_table)
            elements.append(Spacer(1, 20))
            
            kesimpulan_title = Paragraph("<b>Kesimpulan</b>", styles['Heading3'])
            elements.append(kesimpulan_title)
            elements.append(Spacer(1, 10))
            
            kesimpulan = Paragraph(
                f"Berdasarkan hasil analisis menggunakan metode SAW, faktor <b>{top_factor}</b> "
                f"menjadi faktor paling dominan penyebab kecanduan merokok dengan nilai <b>{top_score:.3f}</b>. "
                "Hasil ini menunjukkan bahwa faktor tersebut memiliki pengaruh paling besar dibandingkan faktor lainnya.",
                styles['BodyText']
            )
            elements.append(kesimpulan)
            elements.append(Spacer(1, 20))
            
            footer = Paragraph("Laporan dibuat otomatis oleh Sistem Pendukung Keputusan Berbasis Streamlit.", styles['Italic'])
            elements.append(footer)
            
            doc.build(elements)
            buffer.seek(0)
            return buffer
            
        pdf_file = create_pdf(ranking_df, criteria_df, top_factor, top_score, total_responden)
        st.download_button(
            label="📄 Download PDF Lengkap",
            data=pdf_file,
            file_name="laporan_spk_merokok.pdf",
            mime="application/pdf"
        )

    # =========================
    # MENU: TENTANG SISTEM
    # =========================
    elif menu == "Tentang Sistem":
        st.subheader("ℹ️ Tentang")
        st.markdown("""
        Sistem ini dibuat untuk menganalisis faktor penyebab kecanduan merokok
        menggunakan metode Simple Additive Weighting (SAW).
        
        ### Fitur:
        - Mode Fleksibel (Upload Excel Google Form / Mode Input Simulasi Slider / Mode Simulasi Kuesioner Form)
        - Perhitungan otomatis metode SAW
        - Dashboard interaktif
        - Grafik visualisasi
        - Ranking faktor penyebab
        - Export hasil ke CSV dan PDF Laporan formal
        """)
