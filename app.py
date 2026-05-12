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
st.image("logo.png", width=100)
st.image("logo.png", width=100)
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

uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Excel Google Form",
    type=["xlsx", "xls"]
)

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
# DASHBOARD
# =========================
if uploaded_file:

    df = pd.read_excel(uploaded_file)

    mapping = {
        "Sangat Tidak Setuju": 1,
        "Tidak Setuju": 2,
        "Netral": 3,
        "Setuju": 4,
        "Sangat Setuju": 5
    }

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

    max_value = max(criteria_scores.values())

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

    # =========================
    # DASHBOARD
    # =========================
    if menu == "Dashboard":

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f'''
            <div class="card">
                <h3>Total Responden</h3>
                <p>{len(df)}</p>
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
    # ANALISIS
    # =========================
    elif menu == "Analisis SAW":

        st.subheader("📄 Data Responden")
        st.dataframe(df)

        st.subheader("📊 Nilai Rata-rata Faktor")

        criteria_df = pd.DataFrame({
            "Faktor": list(criteria_scores.keys()),
            "Nilai": list(criteria_scores.values())
        })

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
        # EXPORT PDF
        # =========================
        def create_pdf(dataframe, top_factor, top_score):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            title = Paragraph("Hasil Analisis SPK Faktor Penyebab Kecanduan Merokok", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))

            summary = Paragraph(
                f"Faktor paling dominan adalah <b>{top_factor}</b> dengan nilai <b>{top_score:.3f}</b>.",
                styles['BodyText']
            )
            elements.append(summary)
            elements.append(Spacer(1, 12))

            table_data = [list(dataframe.columns)] + dataframe.values.tolist()

            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ]))

            elements.append(table)

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_file = create_pdf(ranking_df, top_factor, top_score)

        st.download_button(
            label="📄 Download PDF",
            data=pdf_file,
            file_name="hasil_spk_merokok.pdf",
            mime="application/pdf"
        )

    # =========================
    # ABOUT
    # =========================
    elif menu == "Tentang Sistem":

        st.subheader("ℹ️ Tentang")

        st.markdown("""
        Sistem ini dibuat untuk menganalisis faktor penyebab kecanduan merokok
        menggunakan metode Simple Additive Weighting (SAW).

        ### Fitur:
        - Upload Excel Google Form
        - Perhitungan otomatis metode SAW
        - Dashboard interaktif
        - Grafik visualisasi
        - Ranking faktor penyebab
        - Export hasil

        ### Teknologi:
        - Streamlit
        - Python
        - Pandas
        - Plotly
        """)

else:
    st.info("⬅️ Upload file Excel terlebih dahulu dari sidebar")
