import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ======================================
#   PAGE CONFIG
# ======================================
st.set_page_config(layout="wide")

# ======================================
#   PAGES DEFINITIE
# ======================================

def page_nonparametric():

    # ==============================
    #   INIT STATE (schema check)
    # ==============================

    required_cols_table1 = []
    required_cols_table2 = []

    if "table1" not in st.session_state or list(st.session_state.table1.columns) != required_cols_table1:
        st.session_state.table1 = pd.DataFrame(columns=required_cols_table1)

    if "table2" not in st.session_state or list(st.session_state.table2.columns) != required_cols_table2:
        st.session_state.table2 = pd.DataFrame(columns=required_cols_table2)

    if "show_plot" not in st.session_state:
        st.session_state.show_plot = False

    # ==============================
    # FUNCTIONS
    # ==============================

    def raw_data_plotter(setA, setB, variable):
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.hist(setA, bins=30, alpha=0.5, label="A")
        ax.hist(setB, bins=30, alpha=0.5, label="B")
        ax.legend()
        ax.set_title(f"Raw Data: {variable}")
        st.pyplot(fig)

    def normality_check(sample, alpha):
        k2, p = stats.normaltest(sample)
        return ("normal" if p > alpha else "not normal", p)

    def SRM_check(sample_A, sample_B, alpha):
        # placeholder
        return "OK"

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

        numeric_columns = data.select_dtypes(include=["int64", "float64"]).columns
        var1 = st.selectbox("Select the metric column", numeric_columns)

        setA = data[var1][data[variantcolumn].astype(str) == varA].fillna(0)
        setB = data[var1][data[variantcolumn].astype(str) == varB].fillna(0)

        # ==============================
        #   RAW DATA PLOT + TOGGLE BUTTON
        # ==============================
        st.subheader("Raw Data Plot")

        if st.button("📊 Grafiek tonen / verbergen"):
            st.session_state.show_plot = not st.session_state.show_plot

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
                var1, varA, varB, len(setA), len(setB), normalA, normalB,
                srm_result, medA, medB
            ]

            st.session_state.table2.loc[len(st.session_state.table2)] = [
                var1, varA, varB, len(setA), len(setB),
                round(avgA, 3), round(avgB, 3),
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


# ======================================
#   PAGINA NAVIGATIE (SIDEBAR)
# ======================================

pages = {
    "Pagina 1 — Non‑Parametric Tester": page_nonparametric
}

nav = st.navigation(pages, position="sidebar", expanded=True)
nav.run()success("Tabellen leeggemaakt!")

# ==============================
#   AIRTABLE UI (FROM airtable.py)
# ==============================
# from airtable import airtable_test_ui
# airtable_test_ui()
# ==============================
