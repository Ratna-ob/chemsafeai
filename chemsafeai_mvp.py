# ChemSafeAI MVP Prototype (Streamlit Version)
# Technology Stack: Python + Streamlit + Pandas + Basic Rule Engine

import streamlit as st
import pandas as pd

# Sample chemical compatibility rules (simplified)
compatibility_matrix = {
    ("Acid", "Base"): "High Risk: Acid-base neutralization",
    ("Oxidizer", "Reducer"): "Critical Risk: Redox reaction",
    ("Peroxide", "Metal"): "Severe Risk: Explosion potential",
    ("Flammable", "Oxidizer"): "High Risk: Combustion/explosion",
    ("Water-Reactive", "Water"): "Danger: Violent reaction"
}

# Sample chemical class database (simplified)
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

def classify_chemicals(chemicals):
    return [(chem, chemical_classes.get(chem, "Unknown")) for chem in chemicals]

def check_compatibility(classified):
    risk_messages = []
    for i in range(len(classified)):
        for j in range(i + 1, len(classified)):
            c1, class1 = classified[i]
            c2, class2 = classified[j]
            risk = compatibility_matrix.get((class1, class2)) or compatibility_matrix.get((class2, class1))
            if risk:
                risk_messages.append(f"⚠️ {c1} ({class1}) + {c2} ({class2}) → {risk}")
    return risk_messages

st.title("ChemSafeAI - Reactive Compatibility Checker")
st.markdown("""
Upload a batch list and get chemical compatibility risk warnings based on known reactive groups.
""")

uploaded_file = st.file_uploader("Upload batch Excel file (Chemical column required)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.write("### Uploaded Batch Sheet", df)

        chemicals = df['Chemical'].tolist()
        classified = classify_chemicals(chemicals)

        st.write("### Chemical Classifications")
        st.dataframe(pd.DataFrame(classified, columns=["Chemical", "Class"]))

        st.write("### Compatibility Risk Report")
        risks = check_compatibility(classified)
        if risks:
            for msg in risks:
                st.warning(msg)
        else:
            st.success("No critical compatibility risks detected.")

    except Exception as e:
        st.error(f"Error: {e}")
