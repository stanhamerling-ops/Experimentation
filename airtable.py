# ui_airtable.py
import streamlit as st
from pyairtable import Table
import requests

def airtable_test_ui():
    st.markdown("---")
    st.header("🔍 Airtable Debug & Verbindingstest")

    # ==============================
    # 0. SECRETS OPHALEN + LENGTE DEBUG
    # ==============================
    st.subheader("Stap 0: Secrets ophalen & valideren")

    try:
        API_KEY = st.secrets["AIRTABLE_API_KEY"]
        BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
        TABLE_NAME = st.secrets["AIRTABLE_TABLE_NAME"]
        st.success("Secrets succesvol opgehaald.")
    except Exception as e:
        st.error("❌ Kan secrets niet ophalen. Controleer je Streamlit Cloud Secrets.")
        st.code(str(e))
        return

    # 🔍 Lengte check
    st.write("🔑 API Key length:", len(API_KEY))
    st.write("📦 Base ID length:", len(BASE_ID))
    st.write("📄 Table Name length:", len(TABLE_NAME))

    # ✔ Verwachte lengtes
    if len(API_KEY) < 20:
        st.error("❌ API KEY lijkt NIET juist. Controleer quotes en formatting in TOML.")
    if not BASE_ID.startswith("app"):
        st.error("❌ BASE_ID is ongeldig (moet beginnen met 'app').")
    if len(TABLE_NAME) == 0:
        st.error("❌ TABLE_NAME is leeg. Controleer TOML formatting.")

    # ==============================
    # 1. TEST OF API KEY GELDIG IS
    # ==============================
    st.subheader("Stap 1: API-token validatie (meta/bases call)")

    test_url = "https://api.airtable.com/v0/meta/bases"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    resp = requests.get(test_url, headers=headers)

    st.write("➡ Status code:", resp.status_code)

    if resp.status_code == 200:
        st.success("API-token is geldig ✔")
    else:
        st.error("❌ API-token is ongeldig OF gehinderd door permissies.")
        st.code(resp.text)
        return

    # ==============================
    # 2. CONTROLEER OF TOKEN TOEGANG TOT DEZE BASE HEEFT
    # ==============================
    st.subheader("Stap 2: Base‑toegang controleren")

    bases = resp.json().get("bases", [])
    base_ids = [b["id"] for b in bases]

    st.write("📋 Bases waar token toegang toe heeft:")
    st.json(base_ids)

    if BASE_ID in base_ids:
        st.success(f"Toegang tot Base '{BASE_ID}' ✔")
    else:
        st.error(f"❌ Token heeft GEEN toegang tot Base '{BASE_ID}'.")
        st.info("→ Oplossing: Edit je token → Add Base → selecteer de juiste Base → Save.")
        return

    # ==============================
    # 3. CONTROLEER OF TABLE BESTAAT IN BASE
    # ==============================
    st.subheader("Stap 3: Tabellen ophalen uit Base")

    table_meta_url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    table_meta_resp = requests.get(table_meta_url, headers=headers)

    if table_meta_resp.status_code != 200:
        st.error("❌ Kan tabellen niet ophalen uit Base.")
        st.code(table_meta_resp.text)
        return

    tables = table_meta_resp.json().get("tables", [])
    table_names = [t["name"] for t in tables]

    st.write("📄 Tabellen in deze Base:")
    st.json(table_names)

    if TABLE_NAME in table_names:
        st.success(f"Tabel '{TABLE_NAME}' gevonden ✔")
    else:
        st.error(f"❌ Tabel '{TABLE_NAME}' bestaat NIET in Base '{BASE_ID}'.")
        return

    # ==============================
    # 4. PROBEER RECORDS OP TE HALEN
    # ==============================
    st.subheader("Stap 4: Records ophalen vanuit Airtable")

    try:
        table = Table(API_KEY, BASE_ID, TABLE_NAME)
        records = table.all()
        st.success(f"✔ {len(records)} records opgehaald.")
    except Exception as e:
        st.error("❌ Records ophalen mislukt.")
        st.code(str(e))
        return

    if not records:
        st.warning("⚠ Geen records gevonden in de tabel.")
        return

    # ==============================
    # 5. SELECTIE UI
    # ==============================
    st.subheader("🔽 Selecteer een record op basis van 'Name'")

    names = [r["fields"].get("Name") for r in records if r["fields"].get("Name")]

    if not names:
        st.warning("⚠ Kolom 'Name' niet gevonden in records.")
        st.write("Beschikbare kolommen:")
        st.json(records[0]["fields"].keys())
        return

    selected_name = st.selectbox("Naam:", names)

    for rec in records:
        if rec["fields"].get("Name") == selected_name:
            st.subheader("📌 Record details")
            st.json(rec["fields"])
            break
