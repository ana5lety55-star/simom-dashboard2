import streamlit as st
import pandas as pd
from datetime import datetime

st.title("📝 Captura de datos")

fecha = st.date_input("Fecha")
area = st.text_input("Área")
maquina = st.text_input("Máquina")
producto = st.text_input("Producto")
real = st.number_input("Producción real")

if st.button("Guardar"):

    nuevo = pd.DataFrame({
        "fecha":[fecha],
        "area":[area],
        "maquina":[maquina],
        "producto":[producto],
        "produccion_real":[real]
    })

    prod = pd.read_excel("data/produccion.xlsx")
    prod = pd.concat([prod, nuevo])
    prod.to_excel("data/produccion.xlsx", index=False)

    # HISTORIAL
    hist = pd.DataFrame({
        "usuario":[st.session_state["usuario"]],
        "accion":["Registro creado"],
        "fecha":[datetime.now()]
    })

    try:
        h = pd.read_excel("data/historial.xlsx")
        h = pd.concat([h, hist])
    except:
        h = hist

    h.to_excel("data/historial.xlsx", index=False)

    st.success("Guardado")
import streamlit as st

if "rol" not in st.session_state or st.session_state["rol"] not in ["Administrador", "Operador"]:
    st.error("⛔ Acceso restringido")
    st.stop()