import streamlit as st
import pandas as pd
import plotly.express as px

st.title("⚙️ Dashboard Operativo")

data = pd.read_excel("data/produccion.xlsx")

st.plotly_chart(px.bar(data, x="maquina", y="produccion_real", color="area"))
st.plotly_chart(px.bar(data, x="producto", y="produccion_real"))