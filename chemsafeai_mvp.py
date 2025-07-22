# ChemSafeAI MVP Prototype (Streamlit Version)
# Technology Stack: Python + Streamlit + Pandas + Basic Rule Engine

import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import seaborn as sns
import matplotlib.pyplot as plt

# ─── Chemical Compatibility Matrix ─────────────────────────────────────────────
compatibility_matrix = {
    ("Acid", "Base"): "High Risk: Acid-base neutralization",
    ("Oxidizer", "Reducer"): "Critical Risk: Redox reaction",
    ("Peroxide", "Metal"): "Severe Risk: Explosion potential",
    ("Flammable", "Oxidizer"): "High Risk: Combustion/explosion",
    ("Water-Reactive", "Water"): "Danger: Violent reaction"
}

# ─── Sample Chemical Class Database ────────────────────────────────────────────
chemical_classes = {
    "Sulfuric Acid": "Acid",
    "Sodium Hydroxide": "Base",
    "Hydrogen Peroxide": "Peroxide",
    "Iron": "Metal",
    "Methanol": "Flammable",
    "Potassium Permanganate": "Oxidizer",
    "Sodium": "Water-Reactive",
    "Water": "Water"
}

# ─── Classification Logic ──────────────────────────────────────────────────────
def classify_chemicals(chemicals):
    return [(chem, chemical_classes.get(chem, "Unknown")) for chem in chemicals]

# ─── Compatibility Check ───────────────────────────────────────────────────────
def check_compatibility(classified):
    risk_messages = []
    for i in range(len(classified)):
        for j in range(i + 1, len(classified)):
            c1, class1 = classified[i]
            c2, class2 = classified[j]
            risk = compatibility_matrix.get((class1, class2)) or compatibility_matrix.get((class2, class1))
            if risk:
                risk_messages.append(f"{c1} ({class1}) + {c2} ({class2}) → {risk}")
    return risk_messages
st.write("### Thermal Hazard Heatmap")
required_columns = {"Chemical", "DSC_OnsetTemp", "ARC_Tad", "RC1e_Qmax"}
if required_columns.issubset(df.columns):
    try:
        thermal_df = df[["Chemical", "DSC_OnsetTemp", "ARC_Tad", "RC1e_Qmax"]].set_index("Chemical")
        st.write("Thermal Hazard Data")
        st.dataframe(thermal_df)

        st.write("#### Heatmap (DSC, ARC, RC1e)")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(thermal_df, annot=True, cmap="YlOrRd", fmt=".0f", ax=ax, cbar_kws={'label': 'Thermal Parameter Value'})
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error generating thermal heatmap: {e}")
else:
    st.warning("Thermal hazard data columns not found. Ensure your Excel file includes: DSC_OnsetTemp, ARC_Tad, RC1e_Qmax")

    
def generate_heatmap_matrix(classified):
    chems =[chem for chem, _ in classified]
    matrix = pd.DataFrame(0, index=chems, columns=chems)
    for i in range(len(classified)):
        for j in range(i + 1, len(classified)):
            c1, class1 = classified[i]
            c2, class2 = classified[j]
            risk = compatibility_matrix.get((class1, class2)) or compatibility_matrix.get((class2, class1))
        if risk:
            matrix.loc[c1, c2] = risk[1]
            matrix.loc[c2, c1] = risk[1]
    return matrix

# ─── PDF Report Generator ──────────────────────────────────────────────────────
def generate_pdf_report(classified_data, risk_messages, thermal_df=None):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 40, "ChemSafeAI Compatibility Risk Report")

    y = height - 80
    c.setFont("Helvetica", 12)

    c.drawString(40, y, "Chemical Classifications:")
    y -= 20
    for chem, cls in classified_data:
        c.drawString(60, y, f"- {chem}: {cls}")
        y -= 16
        if y < 50:
            c.showPage()
            y = height - 40

    y -= 10
    c.drawString(40, y, "Detected Compatibility Risks:")
    y -= 20
    if risk_messages:
        for msg in risk_messages:
            c.drawString(60, y, f"- {msg}")
            y -= 16
            if y < 50:
                c.showPage()
                y = height - 40
    else:
        c.drawString(60, y, "No critical risks detected.")
        y -= 20

    if thermal_df is not None:
        y -= 20
        c.drawString(40, y, "Thermal Hazard Data (DSC, ARC, RC1e):")
        y -= 20
        for _, row in thermal_df.iterrows():
            desc = f"{row['Chemical']}: DSC={row.get('DSC_OnsetTemp','N/A')}°C, ARC_Tad={row.get('ARC_Tad','N/A')}°C, RC1e_Qmax={row.get('RC1e_Qmax','N/A')} J/g"
            c.drawString(60, y, f"- {desc}")
            y -= 16
            if y < 50:
                c.showPage()
                y = height - 40

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ─── Streamlit UI ──────────────────────────────────────────────────────────────
st.title("ChemSafeAI – Reactive Compatibility & Thermal Hazard Checker")

st.markdown("""
Upload a batch Excel file with chemical names and optional thermal hazard data. The app will analyze incompatibilities and generate a downloadable PDF report.
""")

uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        st.subheader("📋 Uploaded Data")
        st.write(df)

        if 'Chemical' not in df.columns:
            st.error("❌ Excel file must contain a 'Chemical' column.")
        else:
            chemicals = df['Chemical'].tolist()
            classified = classify_chemicals(chemicals)

            st.subheader("🔬 Chemical Classifications")
            st.dataframe(pd.DataFrame(classified, columns=["Chemical", "Class"]))

            st.subheader("⚠️ Compatibility Risk Report")
            risks = check_compatibility(classified)

            if risks:
                for msg in risks:
                    st.warning(msg)
            else:
                st.success("✅ No critical compatibility risks detected.")

            st.subheader("📄 Generate PDF Report")
            pdf_buffer = generate_pdf_report(classified, risks, df)
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_buffer,
                file_name="chemsafeai_report.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Error processing file: {e}")
