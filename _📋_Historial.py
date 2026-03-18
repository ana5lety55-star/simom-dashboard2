import streamlit as st
import pandas as pd

st.title("📋 Historial de cambios")

try:
    data = pd.read_excel("data/historial.xlsx")
    st.dataframe(data)
except:
    st.warning("No hay historial aún")