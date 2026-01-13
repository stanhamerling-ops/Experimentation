import streamlit as st
import pandas as pd

# ==============================
#   PAGE CONFIG
# ==============================

st.set_page_config(layout="wide")
st.title("Bayesian calculator")

# ==============================
#   CALLBACKS
# ==============================

def toggle_global_active():
    st.session_state.global_active = not st.session_state.global_active

def toggle_include(key):
    st.session_state[key] = not st.session_state[key]

def recompute_large_table():
    base_df = st.session_state.input_table.copy()

    base_df["Control"] = 0
    base_df["Variant"] = 0

    sources = [
        ("mobile_table", st.session_state.include_mobile),
        ("desktop_table", st.session_state.include_desktop),
    ]

    for src_key, include in sources:
        if not include:
            continue

        src_df = st.session_state[src_key]

        for i in range(min(len(base_df), len(src_df))):
            for col in ["Control", "Variant"]:
                try:
                    val = float(src_df.at[i, col])
                except (ValueError, TypeError):
                    val = 0
                base_df.at[i, col] += val

    if st.session_state.global_active:
        base_df["Control"] = "None"
        base_df["Variant"] = "None"

    st.session_state.input_table = base_df

# ==============================
#   INIT STATE
# ==============================

if "global_active" not in st.session_state:
    st.session_state.global_active = True

if "include_mobile" not in st.session_state:
    st.session_state.include_mobile = True

if "include_desktop" not in st.session_state:
    st.session_state.include_desktop = True

# ==============================
#   ACTIVATE / DEACTIVATE
# ==============================

col_btn, col_space = st.columns([1, 5])

with col_btn:
    st.button(
        "✅ Activate" if not st.session_state.global_active else "⛔ Deactivate",
        on_click=toggle_global_active,
    )

st.caption(
    f"Huidige status: **{'Active' if st.session_state.global_active else 'Inactive'}**"
)

# ==============================
#   INIT LARGE TABLE
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

# ==============================
#   INIT SMALL TABLES
# ==============================

def init_small_table(key):
    if (
        key not in st.session_state
        or list(st.session_state[key].columns) != ["KPI", "Control", "Variant"]
    ):
        st.session_state[key] = pd.DataFrame(
            {
                "KPI": [""] * 10,
                "Control": [0] * 10,
                "Variant": [0] * 10,
            }
        )

init_small_table("mobile_table")
init_small_table("desktop_table")

# ==============================
#   RECOMPUTE BEFORE DISPLAY
# ==============================

recompute_large_table()

# ==============================
#   DISPLAY LARGE TABLE (TOP)
# ==============================

st.subheader("Resultaten")

display_table = st.session_state.input_table.copy()

st.data_editor(
    display_table,
    hide_index=True,
    use_container_width=True,
    disabled=True,
)

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
#   SMALL TABLES + INCLUDE BUTTONS
# ==============================

col_mobile, col_desktop = st.columns(2)

with col_mobile:
    st.subheader("📱 Mobiel")

    st.button(
        "✅ Included" if st.session_state.include_mobile else "➕ Include",
        key="btn_mobile",
        on_click=toggle_include,
        args=("include_mobile",),
    )

    st.session_state.mobile_table = st.data_editor(
        st.session_state.mobile_table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "KPI": st.column_config.TextColumn("KPI"),
            "Control": st.column_config.NumberColumn("Control"),
            "Variant": st.column_config.NumberColumn("Variant"),
        },
        key="mobile_editor",
    )

    if not st.session_state.include_mobile:
        st.caption("🚫 Deze tabel telt niet mee")

with col_desktop:
    st.subheader("🖥️ Desktop")

    st.button(
        "✅ Included" if st.session_state.include_desktop else "➕ Include",
        key="btn_desktop",
        on_click=toggle_include,
        args=("include_desktop",),
    )

    st.session_state.desktop_table = st.data_editor(
        st.session_state.desktop_table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "KPI": st.column_config.TextColumn("KPI"),
            "Control": st.column_config.NumberColumn("Control"),
            "Variant": st.column_config.NumberColumn("Variant"),
        },
        key="desktop_editor",
    )

    if not st.session_state.include_desktop:
        st.caption("🚫 Deze tabel telt niet mee")

# ==============================
#   INFO
# ==============================

st.info(
    "⬆️ De grote tabel staat nu bovenaan. "
    "Mobiel en Desktop vullen deze tabel automatisch aan."
)