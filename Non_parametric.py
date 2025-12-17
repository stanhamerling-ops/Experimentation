import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ==============================
#   PAGE CSS (only for TWO tables)
# ==============================

st.markdown("""
    <style>

    /* TABLE 1 WIDE ONLY */
    .custom-wide-table-1 .stDataFrame {
        width: 95% !important;
    }
    .custom-wide-table-1 [data-testid="column-header"] {
        flex: 1 !important;
    }
    .custom-wide-table-1 [data-testid="data-cell"] {
        flex: 1 !important;
    }

    /* TABLE 2 WIDE ONLY */
    .custom-wide-table-2 .stDataFrame {
        width: 95% !important;
    }
    .custom-wide-table-2 [data-testid="column-header"] {
        flex: 1 !important;
    }
    .custom-wide-table-2 [data-testid="data-cell"] {
        flex: 1 !important;
    }

    </style>
""", unsafe_allow_html=True)


# ==============================
#   INIT STATE (schema check)
# ==============================

required_cols_table1 = [
    "Metric", "Variant A", "Variant B",
    "Normality A", "Normality B",
    "SRM Result", "Median A", "Median B"
]

required_cols_table2 = [
    "Metric", "Variant A", "Variant B",
    "Average A", "Average B",
    "Impact (%)", "Mann–Whitney p-value"
]

if "table1" not in st.session_state or list(st.session_state.table1.columns) != required_cols_table1:
    st.session_state.table1 = pd.DataFrame(columns=required_cols_table1)

if "table2" not in st.session_state or list(st.session_state.table2.columns) != required_cols_table2:
    st.session_state.table2 = pd.DataFrame(columns=required_cols_table2)

# ==============================
# FUNCTIONS
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
    return (f"violates normality (p={p:.3f})", p) if p < alpha else (f"normal (p={p:.3f})", p)

def SRM_check(sample_A, sample_B, alpha):
    observed = [len(sample_A), len(sample_B)]
    chi, p = stats.chisquare(observed)
    return f"SRM mismatch (p={p:.3f})" if p < alpha else f"OK (p={p:.3f})"

def MWW_test(sampleA, sampleB):
    U, p = stats.mannwhitneyu(sampleA, sampleB)
    return p

# ==============================
#   UI
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

    st.subheader("Raw Data Plot")
    raw_data_plotter(setA, setB, var1)

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
# TABLES (WIDE ONLY HERE)
# ==============================

st.subheader("Tabel 1: Normality, SRM, Medians")
st.markdown('<div class="custom-wide-table-1">', unsafe_allow_html=True)
st.dataframe(st.session_state.table1, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.subheader("Tabel 2: Averages, Impact, Mann–Whitney")
st.markdown('<div class="custom-wide-table-2">', unsafe_allow_html=True)
st.dataframe(st.session_state.table2, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# RESET BUTTON
# ==============================
if st.button("Tabel resetten"):
    st.session_state.table1 = st.session_state.table1.iloc[0:0]
    st.session_state.table2 = st.session_state.table2.iloc[0:0]
    st.success("Tabellen leeggemaakt!")
