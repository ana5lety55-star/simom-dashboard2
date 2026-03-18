import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Dashboard Ejecutivo")

prod = pd.read_excel("data/produccion.xlsx")
merma = pd.read_excel("data/merma.xlsx")

prod.columns = prod.columns.str.lower()
merma.columns = merma.columns.str.lower()

data = pd.merge(prod, merma, on=["fecha","area","producto","molde","color"], how="left")
data["cantidad"] = data["cantidad"].fillna(0)

data["eficiencia"] = ((data["produccion_real"] - data["cantidad"]) / data["produccion_programada"]) * 100

# KPI
st.metric("Eficiencia General", f"{data['eficiencia'].mean():.2f}%")

# Gráfica ejecutiva
fig = px.line(data, x="fecha", y="eficiencia", title="Tendencia KPI")
st.plotly_chart(fig, use_container_width=True)

# Recomendaciones automáticas
if data["eficiencia"].mean() < 40:
    st.error("CRÍTICO: revisar operación completa")
elif data["eficiencia"].mean() < 80:
    st.warning("RIESGO: optimizar procesos")
else:
    st.success("ÓPTIMO") 
import streamlit as st

if "rol" not in st.session_state or st.session_state["rol"] != "Administrador":
    st.error("⛔ No tienes acceso a esta página")
    st.stop()