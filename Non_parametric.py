import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ==============================
#   PAGE CONFIG (WIDE MODE)
# ==============================
st.set_page_config(layout="wide")

# ==============================
#   INIT STATE (schema check)
# ==============================

required_cols_table1 = [
    "KPI", "Control", "Variant",
    "Normality Control", "Normality Variant",
    "SRM Result", "Median Control", "Median Variant"
]

required_cols_table2 = [
    "KPI", "Control", "Variant",
    "Avg. Control", "Avg. Variant",
    "Impact (%)", "p-value"
]

if "table1" not in st.session_state or list(st.session_state.table1.columns) != required_cols_table1:
    st.session_state.table1 = pd.DataFrame(columns=required_cols_table1)

if "table2" not in st.session_state or list(st.session_state.table2.columns) != required_cols_table2:
    st.session_state.table2 = pd.DataFrame(columns=required_cols_table2)

# Toggle state for showing/hiding plot
if "show_plot" not in st.session_state:
    st.session_state.show_plot = False

# ==============================
# FUNCTIONS
# ==============================

def raw_data_plotter(setA, setB, variable):
    fig, ax = plt.subplots(1, 1, figsize=(5, 3))  # <-- HALVE GROOTTE (breed + hoog)
    ax.hist(setA, density=False, histtype='stepfilled', alpha=0.7, label='A', bins=100)
    ax.hist(setB, density=False, histtype='stepfilled', alpha=0.7, label='B', bins=100)
    ax.legend(loc='best', frameon=False)
    ax.set_title('Density curve')
    ax.set_xlabel(variable)
    ax.set_ylabel('Density')
    st.pyplot(fig)

def normality_check(sample, alpha):
    k2, p = stats.normaltest(sample)
    return (f"violates normality (p={p:.3f})", p) if p < alpha else (f"normal (p={p:.3f})", p)

def SRM_check(sample_A, sample_B, alpha):
    observed = [len(sample_A), len(sample_B)]
    chi, p = stats.chisquare(observed)
    return f"SRM mismatch (p={p:.3f})" if p < alpha else f"OK (p={p:.3f})"

def MWW_test(sampleA, sampleB):
    U, p = stats.mannwhitneyu(sampleA, sampleB)
    return p

# ==============================
#   UI — SETTINGS/GRAPH SECTION
# ==============================

st.title("Non-Parametric Tester (A/B Statistical Tool)")

uploaded_file = st.file_uploader("Upload your CSV file")

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("Columns found:", list(data.columns))

    variantcolumn = st.selectbox("Select the variant column", data.columns)
    variants = data[variantcolumn].astype(str).unique()

    varA = st.selectbox("Select Variant A", variants)
    varB = st.selectbox("Select Variant B", variants)

    numeric_columns = data.select_dtypes(include=['int64', 'float64']).columns
    var1 = st.selectbox("Select the metric column", numeric_columns)

    setA = data[var1][data[variantcolumn].astype(str) == varA].fillna(0)
    setB = data[var1][data[variantcolumn].astype(str) == varB].fillna(0)

    # ==============================
    #   RAW DATA PLOT + TOGGLE BUTTON
    # ==============================
    st.subheader("Raw Data Plot")

    # Toggle knop
    if st.button("📊 Grafiek tonen / verbergen"):
        st.session_state.show_plot = not st.session_state.show_plot

    # 50% breedte via kolommen
    if st.session_state.show_plot:
        col_plot, col_empty = st.columns([1, 1])
        with col_plot:
            raw_data_plotter(setA, setB, var1)

    # ==============================
    #   ANALYSE
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

        st.session_state.table1.loc[len(st.session_state.table1)] = [
            var1, varA, varB, normalA, normalB, srm_result, medA, medB
        ]

        st.session_state.table2.loc[len(st.session_state.table2)] = [
            var1, varA, varB, round(avgA, 3), round(avgB, 3),
            round(percent_impact, 2), round(mw_p, 4)
        ]

# ==============================
#   TABLE SECTION
# ==============================

st.markdown("### Analyse checks")
st.dataframe(st.session_state.table1, use_container_width=True)

st.markdown("### Impact")
st.dataframe(st.session_state.table2, use_container_width=True)

if st.button("Tabel resetten"):
    st.session_state.table1 = st.session_state.table1.iloc[0:0]
    st.session_state.table2 = st.session_state.table2.iloc[0:0]
    st.success("Tabellen leeggemaakt!")
