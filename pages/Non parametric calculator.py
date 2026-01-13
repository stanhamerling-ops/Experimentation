# pages/Non parametric calculator.py

import os
import sys

# ✅ voeg project root toe
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT_DIR, "statistics"))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from non_parametric_stats import run_non_parametric_analysis

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(layout="wide")
st.title("Non‑Parametric Calculator")

# ==============================
# SESSION STATE
# ==============================
cols_checks = [
    "KPI", "Control", "Variant",
    "N Control", "N Variant",
    "Norm Control", "Norm Variant",
    "SRM", "Median Control", "Median Variant"
]

cols_impact = [
    "KPI", "Control", "Variant",
    "N Control", "N Variant",
    "Avg Control", "Avg Variant",
    "Impact (%)", "p-value"
]

if "checks" not in st.session_state:
    st.session_state.checks = pd.DataFrame(columns=cols_checks)

if "impact" not in st.session_state:
    st.session_state.impact = pd.DataFrame(columns=cols_impact)

if "show_plot" not in st.session_state:
    st.session_state.show_plot = False


# ==============================
# PLOT
# ==============================
def plot_raw(a, b, label):
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.hist(a, bins=100, alpha=0.6, label="Control")
    ax.hist(b, bins=100, alpha=0.6, label="Variant")
    ax.set_xlabel(label)
    ax.set_title("Raw distribution")
    ax.legend()
    st.pyplot(fig)


# ==============================
# UI
# ==============================
file = st.file_uploader("Upload CSV")

if file:
    df = pd.read_csv(file)

    variant_col = st.selectbox("Variant column", df.columns)

    metric_col = st.selectbox(
        "Metric column",
        df.select_dtypes(include=["int", "float"]).columns
    )

    variants = df[variant_col].astype(str).unique()
    control = st.selectbox("Control", variants)
    variant = st.selectbox("Variant", variants)

    set_a = df.loc[df[variant_col].astype(str) == control, metric_col].fillna(0)
    set_b = df.loc[df[variant_col].astype(str) == variant, metric_col].fillna(0)

    if st.button("📊 Grafiek tonen / verbergen"):
        st.session_state.show_plot = not st.session_state.show_plot

    if st.session_state.show_plot:
        plot_raw(set_a, set_b, metric_col)

    if st.button("Analyse uitvoeren"):
        r = run_non_parametric_analysis(set_a, set_b)

        st.session_state.checks.loc[len(st.session_state.checks)] = [
            metric_col,
            control,
            variant,
            r["nA"],
            r["nB"],
            r["normalA"],
            r["normalB"],
            r["srm"],
            r["medA"],
            r["medB"]
        ]

        st.session_state.impact.loc[len(st.session_state.impact)] = [
            metric_col,
            control,
            variant,
            r["nA"],
            r["nB"],
            round(r["avgA"], 3),
            round(r["avgB"], 3),
            round(r["impact"], 2),
            round(r["p_value"], 4)
        ]


# ==============================
# OUTPUT
# ==============================
st.subheader("Analyse checks")
st.dataframe(st.session_state.checks, use_container_width=True)

st.subheader("Impact")
st.dataframe(st.session_state.impact, use_container_width=True)

if st.button("Reset tabellen"):
    st.session_state.checks = st.session_state.checks.iloc[0:0]
    st.session_state.impact = st.session_state.impact.iloc[0:0]
    st.success("Tabellen gereset ✅")