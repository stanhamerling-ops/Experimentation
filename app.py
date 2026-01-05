import streamlit as st
import os

st.title("DEBUG — Welke file draait Streamlit?")

st.write("Current working directory:", os.getcwd())

st.write("Files in this folder:")
st.write(os.listdir("."))

st.write("Files in pages/ folder (if exists):")
if "pages" in os.listdir("."):
    st.write(os.listdir("pages"))
else:
    st.error("pages/ map bestaat NIET in de map die Streamlit draait.")
