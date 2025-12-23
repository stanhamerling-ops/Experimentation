# ui_airtable.py
import streamlit as st
from pyairtable import Table

def airtable_test_ui():

    # Verbind met Airtable via Cloud Secrets
    API_KEY = st.secrets["AIRTABLE_API_KEY"]
    BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
    TABLE_NAME = st.secrets["AIRTABLE_TABLE_NAME"]

    # Maak Airtable table object
    table = Table(API_KEY, BASE_ID, TABLE_NAME)

    st.subheader("📡 Airtable Verbinding Test")

    st.title("Airtable Test Connectie Checker")
    st.write("Base ID:", BASE_ID)
    st.write("Table Name:", TABLE_NAME)

    # Probeer records op te halen
    try:
        records = table.all()
        st.success("Verbinding geslaagd! Records opgehaald uit Airtable.")
    except Exception as e:
        st.error("Kon niet verbinden met Airtable.")
        st.code(str(e))
        st.stop()

    if len(records) == 0:
        st.warning("Geen records gevonden in deze tabel.")
        return

    # Haal alle namen op (pas kolomnaam aan indien nodig)
    names = []
    for rec in records:
        fields = rec.get("fields", {})
        name = fields.get("Name", None)  # Kolomnaam "Name"
        if name:
            names.append(name)

    if not names:
        st.warning("Geen 'Name' kolom gevonden. Pas kolomnaam aan in ui_airtable.py.")
        return

    selected_name = st.selectbox("Selecteer een test uit Airtable:", names)

    # Details van het geselecteerde record tonen
    for rec in records:
        if rec.get("fields", {}).get("Name") == selected_name:
            st.subheader("Details van geselecteerde test:")
            st.json(rec["fields"])
            break
