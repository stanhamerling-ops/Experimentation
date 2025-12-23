# ui_airtable.py
import streamlit as st
from pyairtable import Table
import requests

def airtable_test_ui():
    st.markdown("---")
    st.header("🔍 Airtable Debug & Verbindingstest")

    # ==============================
    # 0. CHECK SECRETS
    # ==============================
    st.subheader("Stap 0: Secrets ophalen")
    try:
        API_KEY = st.secrets["AIRTABLE_API_KEY"]
        BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
        TABLE_NAME = st.secrets["AIRTABLE_TABLE_NAME"]
        st.success("Secrets succesvol opgehaald.")
    except Exception as e:
        st.error("❌ Kan secrets niet ophalen.")
        st.code(str(e))
        return

    # Toon debug info
    st.write("🔑 Base ID:", BASE_ID)
    st.write("📄 Table Name:", TABLE_NAME)
    st.write("DEBUG TOKEN LENGTH:", len(API_KEY))

    # ==============================
    # 1. CHECK: API TOKEN VALID?
    # ==============================
    st.subheader("Stap 1: API-token validatie")

    # Controleren door een simpele request te doen via de officiële API endpoint
    test_url = f"https://api.airtable.com/v0/meta/bases"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    resp = requests.get(test_url, headers=headers)

    if resp.status_code == 200:
        st.success("API-token is geldig ✔")
    else:
        st.error("❌ API-token is ongeldig of heeft geen toegang.")
        st.code(f"Status: {resp.status_code}, Response: {resp.text}")
        return

    # ==============================
    # 2. CHECK: HEEFT TOKEN TOEGANG TOT DEZE BASE?
    # ==============================
    st.subheader("Stap 2: Base‑toegang controleren")

    bases = resp.json().get("bases", [])
    base_ids = [b["id"] for b in bases]

    if BASE_ID in base_ids:
        st.success(f"Toegang tot Base '{BASE_ID}' ✔")
    else:
        st.error(f"❌ Token heeft GEEN toegang tot Base '{BASE_ID}'.")
        st.write("Bases waar token wél toegang toe heeft:")
        st.json(base_ids)
        return

    # ==============================
    # 3. CHECK: HEEFT TOKEN TOEGANG TOT TABEL?
    # ==============================
    st.subheader("Stap 3: Controle op tabel‑toegang")

    table_meta_url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    table_meta_resp = requests.get(table_meta_url, headers=headers)

    if table_meta_resp.status_code != 200:
        st.error("❌ Kan metadata van Base niet ophalen.")
        st.code(table_meta_resp.text)
        return

    tables = table_meta_resp.json().get("tables", [])
    table_names = [t["name"] for t in tables]

    st.write("📋 Tabellen in deze Base:")
    st.json(table_names)

    if TABLE_NAME in table_names:
        st.success(f"Tabel '{TABLE_NAME}' bestaat ✔")
    else:
        st.error(f"❌ Tabel '{TABLE_NAME}' is NIET gevonden in Base '{BASE_ID}'.")
        return

    # ==============================
    # 4. CHECK: KUNNEN WE RECORDS OPHALEN?
    # ==============================
    st.subheader("Stap 4: Records ophalen uit Airtable")

    try:
        table = Table(API_KEY, BASE_ID, TABLE_NAME)
        records = table.all()
        st.success(f"{len(records)} records succesvol opgehaald ✔")
    except Exception as e:
        st.error("❌ Fout bij ophalen van records.")
        st.code(str(e))
        return

    if not records:
        st.warning("⚠ Geen records gevonden.")
        return

    # ==============================
    # 5. UI — Test selecteren
    # ==============================
    st.subheader("🔽 Selecteer een record")

    names = [r["fields"].get("Name") for r in records if r["fields"].get("Name")]

    if not names:
        st.warning("⚠ Kolom 'Name' bestaat niet in records.")
        st.write("Beschikbare kolommen:")
        st.json(records[0]["fields"].keys())
        return

    selected_name = st.selectbox("Naam:", names)

    for rec in records:
        if rec["fields"].get("Name") == selected_name:
            st.subheader("📌 Record details")
            st.json(rec["fields"])
            break
