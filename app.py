import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="SPK Faktor Kecanduan Merokok", layout="wide")

st.title("🚭 Sistem Pendukung Keputusan Faktor Penyebab Kecanduan Merokok")
st.markdown("### Metode Simple Additive Weighting (SAW)")

st.sidebar.header("📂 Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload file Excel hasil Google Form", 
    type=["xlsx", "xls"]
)

# Bobot kriteria
weights = {
    "Psikologis": 0.15,
    "Lingkungan": 0.25,
    "Kebiasaan": 0.20,
    "Ekonomi": 0.25,
    "Ketergantungan": 0.10,
    "Pengetahuan": 0.05
}

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        st.success("✅ File berhasil diupload")

        st.subheader("📄 Data Responden")
        st.dataframe(df)

        # Mapping jawaban ke angka
        mapping = {
            "Sangat Tidak Setuju": 1,
            "Tidak Setuju": 2,
            "Netral": 3,
            "Setuju": 4,
            "Sangat Setuju": 5
        }

        df_numeric = df.replace(mapping)

        # Deteksi kolom otomatis berdasarkan nama pertanyaan
        psikologis_cols = [col for col in df_numeric.columns if "stres" in col.lower() or "sulit berhenti" in col.lower() or "tidak nyaman" in col.lower()]

        lingkungan_cols = [col for col in df_numeric.columns if "teman" in col.lower() or "lingkungan" in col.lower() or "berkumpul" in col.lower()]

        kebiasaan_cols = [col for col in df_numeric.columns if "rutinitas" in col.lower() or "setelah makan" in col.lower() or "tanpa sadar" in col.lower()]

        ekonomi_cols = [col for col in df_numeric.columns if "mudah didapat" in col.lower() or "harga" in col.lower()]

        ketergantungan_cols = [col for col in df_numeric.columns if "ingin merokok" in col.lower() or "mengurangi" in col.lower()]

        pengetahuan_cols = [col for col in df_numeric.columns if "bahaya" in col.lower() or "berbahaya" in col.lower()]

        # Fungsi rata-rata
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

        st.subheader("📊 Nilai Rata-rata Faktor")

        criteria_df = pd.DataFrame({
            "Faktor": list(criteria_scores.keys()),
            "Nilai": list(criteria_scores.values())
        })

        st.dataframe(criteria_df)

        # ======================
        # NORMALISASI SAW
        # ======================
        max_value = max(criteria_scores.values())

        normalized_scores = {
            key: value / max_value
            for key, value in criteria_scores.items()
        }

        # ======================
        # PERHITUNGAN SAW
        # ======================
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

        st.subheader("🏆 Ranking Faktor Penyebab")
        st.dataframe(ranking_df)

        # ======================
        # GRAFIK
        # ======================
        st.subheader("📈 Grafik Ranking Faktor")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(ranking_df["Faktor"], ranking_df["Nilai SAW"])
        ax.set_xlabel("Faktor")
        ax.set_ylabel("Nilai")
        ax.set_title("Hasil Perhitungan SAW")

        st.pyplot(fig)

        # Faktor tertinggi
        top_factor = ranking_df.iloc[0]["Faktor"]
        top_score = ranking_df.iloc[0]["Nilai SAW"]

        st.success(
            f"🎯 Faktor paling dominan penyebab kecanduan merokok adalah: **{top_factor}** dengan nilai **{top_score:.3f}**"
        )

    except Exception as e:
        st.error(f"❌ Terjadi error: {e}")

else:
    st.info("⬅️ Upload file Excel terlebih dahulu untuk memulai analisis")

st.markdown("---")
st.caption("SPK Faktor Penyebab Kecanduan Merokok - Metode SAW")

