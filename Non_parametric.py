import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ==============================
#   INIT STATE  (met schema-fix)
# ==============================

# Verwijder oude tabellen om kolom-mismatch te voorkomen
if "table1" in st.session_state:
    del st.session_state["table1"]
if "table2" in st.session_state:
    del st.session_state["table2"]

# Initialiseer nieuwe tabellen met juiste kolommen
if "table1" not in st.session_state:
    st.session_state.table1 = pd.DataFrame(columns=[
        "Metric", "Variant A", "Variant B",
        "Normality A", "Normality B",
        "SRM Result", "Median A", "Median B"
    ])

if "table2" not in st.session_state:
    st.session_state.table2 = pd.DataFrame(columns=[
        "Metric", "Variant A", "Variant B",
        "Average A", "Average B",
        "Impact (%)", "Mann–Whitney p-value"
    ])

# ==============================
#   FUNCTIONS
# ==============================
def raw_data_plotter(setA, setB, variable):
    fig, ax = plt.subplots(1, 1)
    ax.hist(setA, density=False, histtype='stepfilled', alpha=0.7, label='A', bins=100)
    ax.hist(setB, density=False, histtype='stepfilled', alpha=0.7, label='B', bins=100)
    ax.legend(loc='best', frameon=False)
    ax.set_title('Density curve')
    ax.set_xlabel(variable)
    ax.set_ylabel('Density')
    st.pyplot(fig)

def normality_check(sample, alpha):
    k2, p = stats.normaltest(sample)
    if p < alpha:
        return f"violates normality (p={p:.3f})", p
    else:
        return f"normal (p={p:.3f})", p

def SRM_check(sample_A, sample_B, alpha):
    observed = [len(sample_A), len(sample_B)]
    chi, p = stats.chisquare(observed)
    if p < alpha:
        return f"SRM mismatch (p={p:.3f})"
    else:
        return f"OK (p={p:.3f})"

def MWW_test(sampleA, sampleB):
    U, p = stats.mannwhitneyu(sampleA, sampleB)
    return p

# ==============================
# STREAMLIT UI
# ==============================
st.title("Non-Parametric Tester (A/B Statistical Tool)")

uploaded_file = st.file_uploader("Upload your CSV file")

if uploaded_file:
    # Load data
    data = pd.read_csv(uploaded_file)
    st.write("Columns found:", list(data.columns))

    variantcolumn = st.selectbox("Select the variant column", data.columns)
    variants = data[variantcolumn].astype(str).unique()

    varA = st.selectbox("Select Variant A", variants)
    varB = st.selectbox("Select Variant B", variants)

    numeric_columns = data.select_dtypes(include=['int64', 'float64']).columns
    var1 = st.selectbox("Select the metric column", numeric_columns)

    # Filter sets
    setA = data[var1][data[variantcolumn].astype(str) == varA].fillna(0)
    setB = data[var1][data[variantcolumn].astype(str) == varB].fillna(0)

    st.subheader("Raw Data Plot")
    raw_data_plotter(setA, setB, var1)

    # ==============================
    # ANALYSE KNOP
    # ==============================
    if st.button("Analyse uitvoeren"):
        normalA, pA = normality_check(setA, 0.05)
        normalB, pB = normality_check(setB, 0.05)
        srm_result = SRM_check(setA, setB, 0.05)

        avgA = setA.mean()
        avgB = setB.mean()
        medA = round(setA.median(), 1)
        medB = round(setB.median(), 1)

        percent_impact = ((avgB - avgA) / avgA) * 100 if avgA != 0 else float("inf")
        mw_p = MWW_test(setA, setB)

        # Update table 1
        st.session_state.table1.loc[len(st.session_state.table1)] = [
            var1, varA, varB, normalA, normalB, srm_result, medA, medB
        ]

        # Update table 2
        st.session_state.table2.loc[len(st.session_state.table2)] = [
            var1, varA, varB,
            round(avgA, 3), round(avgB, 3),
            round(percent_impact, 2), round(mw_p, 4)
        ]

# ==============================
# DISPLAY TABLES (WITH WIDTH FIX)
# ==============================
st.subheader("Tabel 1: Normality, SRM, Medians")
st.dataframe(st.session_state.table1, use_container_width=True)

st.subheader("Tabel 2: Averages, Impact, Mann–Whitney")
st.dataframe(st.session_state.table2, use_container_width=True)

# ==============================
# RESET BUTTON NOW AT BOTTOM
# ==============================
if st.button("Tabel resetten"):
    st.session_state.table1 = st.session_state.table1.iloc[0:0]
    st.session_state.table2 = st.session_state.table2.iloc[0:0]
    st.success("Tabellen leeggemaakt!")
