import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sea
import plotly.express as px
from scipy import stats
from scipy.stats import skewnorm
import random

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

def normality_check(sample, alpha, name):
    k2, p = stats.normaltest(sample)
    if p < alpha:
        return f"{name} violates normality (p={p:.3f})"
    else:
        return f"{name} is normally distributed (p={p:.3f})"

def SRM_check(sample_A, sample_B, alpha):
    observed = [len(sample_A), len(sample_B)]
    chi, p = stats.chisquare(observed)
    if p < alpha:
        return f"Sample Ratio Mismatch detected (p={p:.3f})"
    else:
        return f"Sample ratio is OK (p={p:.3f})"

def MWW_test(sampleA, sampleB, alpha):
    U, p = stats.mannwhitneyu(sampleA, sampleB)
    if p < alpha:
        return f"Difference is significant (U={U:.3f}, p={p:.3f})"
    else:
        return f"No significant difference (U={U:.3f}, p={p:.3f})"

# ==============================
# STREAMLIT UI
# ==============================
st.title("Non-Parametric Tester (A/B Statistical Tool)")

uploaded_file = st.file_uploader("Upload your CSV file")

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("Columns found:", list(data.columns))

    variantcolumn = st.selectbox("Select the variant column", data.columns)

    variants = data[variantcolumn].astype(str).unique()
    st.write("Detected variants:", variants)

    varA = st.selectbox("Select Variant A", variants)
    varB = st.selectbox("Select Variant B", variants)

    numeric_columns = data.select_dtypes(include=['int64', 'float64']).columns
    var1 = st.selectbox("Select the metric column", numeric_columns)

    # Filter sets
    setA = data[var1][data[variantcolumn].astype(str) == varA].fillna(0)
    setB = data[var1][data[variantcolumn].astype(str) == varB].fillna(0)

    # ==============================
    # ANALYSIS
    # ==============================
    st.subheader("Raw Data Plot")
    raw_data_plotter(setA, setB, var1)

    st.subheader("Normality Tests")
    st.write(normality_check(setA, 0.05, 'Set A'))
    st.write(normality_check(setB, 0.05, 'Set B'))

    st.subheader("Sample Ratio Test (SRM)")
    st.write(SRM_check(setA, setB, 0.05))

    st.subheader("Averages & Impact")
    avgA = setA.mean()
    avgB = setB.mean()
    st.write(f"Average A: {avgA:.3f}")
    st.write(f"Average B: {avgB:.3f}")

    percent_impact = ((avgB - avgA) / avgA) * 100 if avgA != 0 else float("inf")
    st.write(f"Percentual impact: {percent_impact:.2f}%")

    st.subheader("Medians")
    st.write(f"Median A: {setA.median():.3f}")
    st.write(f"Median B: {setB.median():.3f}")

    st.subheader("Mann-Whitney U Test")
    st.write(MWW_test(setA, setB, 0.1))
