import streamlit as st
import pandas as pd

# ==============================
#   PAGE CONFIG
# ==============================

st.set_page_config(layout="wide")
st.title("Bayesian calculator")

# ==============================
#   ACTIVATE / DEACTIVATE (GLOBAL)
# ==============================

if "global_active" not in st.session_state:
    st.session_state.global_active = True

col_btn, col_space = st.columns([1, 5])

with col_btn:
    if st.button(
        "✅ Activate" if not st.session_state.global_active else "⛔ Deactivate"
    ):
        st.session_state.global_active = not st.session_state.global_active

st.caption(
    f"Huidige status: **{'Active' if st.session_state.global_active else 'Inactive'}**"
)

# ==============================
#   LARGE TABLE (READ ONLY)
# ==============================

input_columns = [
    "KPI", "Control", "\u200b", "Variant", "\u200b\u200b", "Impact", "CTBC"
]

if (
    "input_table" not in st.session_state
    or list(st.session_state.input_table.columns) != input_columns
):
    df = pd.DataFrame("", index=range(10), columns=input_columns)
    df.at[0, "KPI"] = "In experiment"
    st.session_state.input_table = df

# Toon None in Control & Variant bij Active
display_table = st.session_state.input_table.copy()
if st.session_state.global_active:
    display_table["Control"] = "None"
    display_table["Variant"] = "None"

st.data_editor(
    display_table,
    hide_index=True,
    use_container_width=True,
    disabled=True,
)

# ==============================
#   INIT SMALL TABLES (EMPTY)
# ==============================

def init_small_table(key):
    if (
        key not in st.session_state
        or list(st.session_state[key].columns) != ["KPI", "Control", "Variant"]
    ):
        st.session_state[key] = pd.DataFrame(
            {
                "KPI": [""] * 10,
                "Control": [""] * 10,
                "Variant": [""] * 10,
            }
        )

init_small_table("mobile_table")
init_small_table("desktop_table")

# ==============================
#   CENTER ALIGNMENT
# ==============================

st.markdown(
    """
    <style>
    thead th { text-align: center !important; }
    tbody td { text-align: center !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================
#   SMALL TABLES (READ-ONLY C/V)
# ==============================

col_mobile, col_desktop = st.columns(2)

with col_mobile:
    st.subheader("📱 Mobiel")
    st.session_state.mobile_table = st.data_editor(
        st.session_state.mobile_table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "KPI": st.column_config.TextColumn("KPI"),
            "Control": st.column_config.NumberColumn(
                "Control", disabled=True
            ),
            "Variant": st.column_config.NumberColumn(
                "Variant", disabled=True
            ),
        },
        key="mobile_editor",
    )

with col_desktop:
    st.subheader("🖥️ Desktop")
    st.session_state.desktop_table = st.data_editor(
        st.session_state.desktop_table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "KPI": st.column_config.TextColumn("KPI"),
            "Control": st.column_config.NumberColumn(
                "Control", disabled=True
            ),
            "Variant": st.column_config.NumberColumn(
                "Variant", disabled=True
            ),
        },
        key="desktop_editor",
    )

# ==============================
#   INFO
# ==============================

st.info(
    "⬆️ 'In experiment' staat nu alleen in de grote tabel. Activate/Deactivate is hersteld."
)