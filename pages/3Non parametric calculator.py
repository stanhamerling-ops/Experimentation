import os
import sys
import re
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==============================
# PATH SETUP
# ==============================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT_DIR, "statistics"))

from non_parametric_stats import analyze_with_zeros, analyze_no_zeros

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(layout="wide")
st.title("Non-Parametric Calculator")

# ==============================
# SESSION STATE
# ==============================
cols_checks = [
    "Metric","Control","Variant",
    "Normality (C)","Normality (V)",
    "SRM","St. deviation (C)","St. deviation (V)"
]

cols_impact = [
    "Metric","Control","Variant",
    "Sample (C)","Sample (V)",
    "Average (C)","Average (V)",
    "Impact (%)","P-value"
]

if "checks" not in st.session_state:
    st.session_state.checks = pd.DataFrame(columns=cols_checks)

if "impact" not in st.session_state:
    st.session_state.impact = pd.DataFrame(columns=cols_impact)

if "show_plot" not in st.session_state:
    st.session_state.show_plot = False

if "df" not in st.session_state:
    st.session_state.df = None

if "transform_log" not in st.session_state:
    st.session_state.transform_log = {}

# ==============================
# HELPERS
# ==============================
def format_rows(n):
    if n >= 1_000_000:
        return f"{round(n/1_000_000)}M"
    if n >= 1_000:
        return f"{round(n/1_000)}K"
    return str(n)

def column_conclusion(series):
    if pd.api.types.is_integer_dtype(series):
        return "✅ integer"
    if pd.api.types.is_float_dtype(series):
        return "✅ float"
    return f"❌ {series.dtype}"

def sd(series):
    return round(series.std(ddof=1),2)

def safe_round(value,decimals=2):
    if isinstance(value,(int,float)):
        return round(value,decimals)
    return value

def normalize_normality(value):
    if isinstance(value,bool):
        return "normal" if value else "not-normal"
    if isinstance(value,str):
        v=value.lower()
        if "not" in v or "false" in v:
            return "not-normal"
        if "normal" in v or "true" in v:
            return "normal"
    return value

def get_sample(series,exclude_zeros=True):
    if exclude_zeros:
        return series[series!=0]
    return series

# ==============================
# VALUE LOGGING
# ==============================
def value_distribution(series):

    s = pd.to_numeric(series, errors="coerce")

    total = len(s)
    zeros = (s==0).sum()
    valid = s.notna().sum()

    return {
        "total":int(total),
        "zeros":int(zeros)
    }

# ==============================
# DETECT TRANSFORMABLE
# ==============================
def needs_transformation(series):

    if series.dtype!="object":
        return False

    sample = series.dropna().astype(str).head(50)

    pattern=r"[€$£]|,|\."

    for v in sample:
        if re.search(pattern,v):
            return True

    return False

# ==============================
# CLEAN NUMERIC (ROBUST EU)
# ==============================
def clean_numeric(series):

    original = series.astype(str)

    cleaned = (
        original
        .str.replace("€","",regex=False)
        .str.replace("$","",regex=False)
        .str.replace("£","",regex=False)
        .str.replace(" ","",regex=False)
        .str.replace(".","",regex=False)
        .str.replace(",",".",regex=False)
    )

    numeric = pd.to_numeric(cleaned,errors="coerce")

    changed = (original != cleaned).sum()

    return numeric, changed

# ==============================
# PLOT
# ==============================
def plot_raw(a,b,label):

    fig,ax=plt.subplots(figsize=(5,3))

    ax.hist(a,bins=100,alpha=0.6,label="Control")
    ax.hist(b,bins=100,alpha=0.6,label="Variant")

    ax.set_xlabel(label)
    ax.set_title("Raw distribution")

    ax.legend()

    st.pyplot(fig)

# ==============================
# FILE UPLOAD
# ==============================
file=st.file_uploader("Upload CSV")

if file:

    if st.session_state.df is None:
        st.session_state.df=pd.read_csv(file)

    df=st.session_state.df

    st.caption(f"{format_rows(len(df))} rows")

    # ==============================
    # KOLOMCONTROLE
    # ==============================
    st.markdown("### Kolomcontrole")

    box = st.container(border=True)

    with box:

        h1,h2,h3,h4 = st.columns([3,2,1.5,5])

        h1.markdown("**Kolom**")
        h2.markdown("**Type**")
        h3.markdown("**Fix**")
        h4.markdown("**Status**")

        for col in df.columns:

            c1,c2,c3,c4 = st.columns([3,2,1.5,5])

            c1.write(col)

            c2.write(column_conclusion(df[col]))

            transformed = col in st.session_state.transform_log
            transformable = needs_transformation(df[col])

            if transformable:

                if c3.button(
                    "Fix",
                    key=f"transform_{col}",
                    disabled=transformed
                ):

                    new_col,changed = clean_numeric(df[col])

                    df[col]=new_col
                    st.session_state.df=df

                    st.session_state.transform_log[col]=changed

                    st.rerun()

            if col in st.session_state.transform_log:

                changed = st.session_state.transform_log[col]

                dist=value_distribution(df[col])

                c4.markdown(
                    f"""
                    ✅ {changed} values aangepast  
                    total: {dist['total']}  
                    zeros: {dist['zeros']}  
                    """
                )

    # ==============================
    # ANALYSE INSTELLINGEN
    # ==============================
    st.markdown("### Analyse instellingen")

    col_left,col_right = st.columns(2)

    with col_left:
        variant_col=st.selectbox(
            "Variant kolom",
            df.columns
        )

    numeric_cols=df.select_dtypes(include=["int","float"]).columns.tolist()

    with col_right:
        metric_col=st.selectbox(
            "Metric kolom",
            numeric_cols if numeric_cols else df.columns
        )

    statistic_type=st.selectbox(
        "0-waardes",
        ["Waardes uitsluiten","Waardes opnemen"],
        index=0
    )

    variants=df[variant_col].astype(str).unique()

    control_col,variant_col_select = st.columns(2)

    with control_col:
        control=st.selectbox("Control",variants)

    with variant_col_select:
        variant=st.selectbox("Variant",variants)

    exclude_zeros=statistic_type=="Waardes uitsluiten"

    raw_a=df.loc[
        df[variant_col].astype(str)==control,metric_col
    ].fillna(0)

    raw_b=df.loc[
        df[variant_col].astype(str)==variant,metric_col
    ].fillna(0)

    set_a=get_sample(raw_a,exclude_zeros)
    set_b=get_sample(raw_b,exclude_zeros)

    if st.button("📊 Grafiek tonen / verbergen"):
        st.session_state.show_plot=not st.session_state.show_plot

    if st.session_state.show_plot:
        plot_raw(set_a,set_b,metric_col)

    # ==============================
    # ANALYSE
    # ==============================
    if st.button("Analyse uitvoeren"):

        if exclude_zeros:
            r = analyze_no_zeros(set_a, set_b)
        else:
            r = analyze_with_zeros(set_a, set_b)

        st.session_state.checks.loc[len(st.session_state.checks)] = [
            metric_col,
            control,
            variant,
            normalize_normality(r["normalA"]),
            normalize_normality(r["normalB"]),
            r["srm"],
            sd(set_a),
            sd(set_b)
        ]

        st.session_state.impact.loc[len(st.session_state.impact)] = [
            metric_col,
            control,
            variant,
            len(set_a),
            len(set_b),
            safe_round(r["avgA"], 2),
            safe_round(r["avgB"], 2),
            safe_round(r["impact"], 2),
            safe_round(r["p_value"], 4)
        ]

# ==============================
# OUTPUT
# ==============================
st.subheader("Analyse checks")

st.dataframe(
    st.session_state.checks,
    use_container_width=True
)

st.subheader("Impact")

st.dataframe(
    st.session_state.impact,
    use_container_width=True
)

if st.button("Reset tabellen"):

    st.session_state.checks=st.session_state.checks.iloc[0:0]
    st.session_state.impact=st.session_state.impact.iloc[0:0]
    st.session_state.transform_log={}

    st.success("Tabellen gereset ✅")