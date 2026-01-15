import os
import sys
import streamlit as st
import pandas as pd

# =====================================================
#   FIX ROOT PATH
# =====================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATISTICS_DIR = os.path.join(ROOT_DIR, "statistics")
if STATISTICS_DIR not in sys.path:
    sys.path.append(STATISTICS_DIR)

from bayesian_stats import prob_variant_beats_control

# =====================================================
#   PAGE CONFIG
# =====================================================

st.set_page_config(layout="centered")
st.title("Bayesian calculator")
st.markdown(
    """
Voor een snelle & gebruiksvriendelijke Bayesian calculator gebruiken we **Google Sheets**
"""
)

SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "15HWWgoxnqxDfx6q9XNIE6ozHrccA7FHT/edit"
    "?gid=1171288171#gid=1171288171"
)

st.link_button(
    "📊 Open Bayesian calculator Google Sheets",
    SHEET_URL,
)

st.markdown("""
✅ **Waarom niet via Streamlit?**
- Streamlit is geen Excel
- UX rondom typen is ruk
- Beste alternatief is Excel zelf
""")


