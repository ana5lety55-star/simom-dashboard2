import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
st.set_page_config(page_title="SIMOM Dashboard", layout="wide")

# ---------------- ESTILO PRO ----------------
st.markdown("""
<style>
body {
    background-color: #f4f6f9;
}
h1, h2, h3 {
    color: #1f3c88;
}
[data-testid="metric-container"] {
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    border-left: 6px solid #1f77b4;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}
section[data-testid="stSidebar"] {
    background-color: #1f3c88;
    color: white;
}
button {
    background-color: #1f77b4 !important;
    color: white !important;
    border-radius: 10px !important;
}
button:hover {
    background-color: orange !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
usuarios = {
    "admin": {"password": "1234", "rol": "Administrador"},
    "operador1": {"password": "1234", "rol": "Operador"}
}

if "login" not in st.session_state:
    st.session_state["login"] = False

def login():
    try:
        st.image("logo.jpg", width=120)
    except:
        st.warning("⚠️ Logo no encontrado")

    st.title("SIMOM Sistema Industrial")

    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if user in usuarios and usuarios[user]["password"] == pwd:
            st.session_state["login"] = True
            st.session_state["usuario"] = user
            st.session_state["rol"] = usuarios[user]["rol"]
            st.rerun()
        else:
            st.error("Acceso denegado")

if not st.session_state["login"]:
    login()
    st.stop()

# ---------------- DATOS ----------------
prod = pd.read_excel("data/produccion.xlsx")
merma = pd.read_excel("data/merma.xlsx")

prod.columns = prod.columns.str.lower()
merma.columns = merma.columns.str.lower()

prod["fecha"] = pd.to_datetime(prod["fecha"])
merma["fecha"] = pd.to_datetime(merma["fecha"])

data = pd.merge(prod, merma,
    on=["fecha","area","producto","molde","color"],
    how="left"
)

data["cantidad"] = data["cantidad"].fillna(0)

data["eficiencia"] = (
    (data["produccion_real"] - data["cantidad"]) /
    data["produccion_programada"]
) * 100

# ---------------- FILTROS ----------------
st.sidebar.header("Filtros")

fecha_inicio = st.sidebar.date_input("Desde", data["fecha"].min())
fecha_fin = st.sidebar.date_input("Hasta", data["fecha"].max())

maquinas = st.sidebar.multiselect("Máquina", data["maquina"].unique())
productos = st.sidebar.multiselect("Producto", data["producto"].unique())
moldes = st.sidebar.multiselect("Molde", data["molde"].unique())
colores = st.sidebar.multiselect("Color", data["color"].unique())

# aplicar filtros
data = data[
    (data["fecha"] >= pd.to_datetime(fecha_inicio)) &
    (data["fecha"] <= pd.to_datetime(fecha_fin))
]

if maquinas:
    data = data[data["maquina"].isin(maquinas)]
if productos:
    data = data[data["producto"].isin(productos)]
if moldes:
    data = data[data["molde"].isin(moldes)]
if colores:
    data = data[data["color"].isin(colores)]

# ---------------- KPIs ----------------
ef = data["eficiencia"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Eficiencia", f"{ef:.2f}%")
col2.metric("Producción", int(data["produccion_real"].sum()))
col3.metric("Merma", int(data["cantidad"].sum()))
col4.metric("Programado", int(data["produccion_programada"].sum()))

# ---------------- SEMÁFORO ----------------
st.subheader("Estado General")

if ef < 40:
    estado = "CRITICO"
    color = "red"
    st.error("🔴 CRÍTICO")
elif ef < 80:
    estado = "RIESGO"
    color = "orange"
    st.warning("🟠 RIESGO")
else:
    estado = "OPTIMO"
    color = "green"
    st.success("🟢 ÓPTIMO")

# ---------------- GRAFICAS ----------------
st.subheader("Eficiencia en el tiempo")
fig1 = px.line(data, x="fecha", y="eficiencia", color="area")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Producción por producto")
fig2 = px.bar(data, x="producto", y="produccion_real", color="area")
st.plotly_chart(fig2, use_container_width=True)

# ---------------- PDF PROFESIONAL ----------------
def generar_pdf(data, ef, estado):

    plt.figure()
    data.groupby("fecha")["eficiencia"].mean().plot()
    plt.title("Eficiencia en el tiempo")
    plt.savefig("grafica.png")
    plt.close()

    pdf = FPDF()
    pdf.add_page()

    try:
        pdf.image("logo.jpg", 10, 8, 30)
    except:
        pass

    pdf.set_font("Arial", "B", 16)
    pdf.cell(200,10,"REPORTE GERENCIAL SIMOM", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200,10,f"Eficiencia: {ef:.2f}%", ln=True)

    if estado == "CRITICO":
        pdf.set_fill_color(255,0,0)
    elif estado == "RIESGO":
        pdf.set_fill_color(255,165,0)
    else:
        pdf.set_fill_color(0,128,0)

    pdf.cell(60,10,estado, ln=True, fill=True)

    pdf.ln(10)
    pdf.image("grafica.png", w=180)

    pdf.ln(10)
    pdf.multi_cell(0,8,"Recomendaciones:")

    if ef < 40:
        pdf.multi_cell(0,8,"- Revisar maquinaria\n- Reducir merma\n- Capacitar personal")
    elif ef < 80:
        pdf.multi_cell(0,8,"- Optimizar procesos\n- Ajustar producción")
    else:
        pdf.multi_cell(0,8,"- Mantener estándar")

    pdf.output("reporte_kpi.pdf")

# ---------------- EMAIL ----------------
def enviar_alerta(pdf_path, ef, estado):
    try:
        correo = "ana5lety55@gmail.com"
        password = "edmaobluisqehxas"
        destino = "ana6lety66@gmail.com"

        msg = EmailMessage()
        msg["Subject"] = "🚨 ALERTA KPI SIMOM"
        msg["From"] = correo
        msg["To"] = destino

        html = f"""
        <h2 style='color:#1f3c88;'>ALERTA KPI</h2>
        <p><b>Estado:</b> {estado}</p>
        <p><b>Eficiencia:</b> {ef:.2f}%</p>
        """

        msg.add_alternative(html, subtype="html")

        with open(pdf_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="reporte.pdf")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(correo, password)
            smtp.send_message(msg)

    except Exception as e:
        st.warning(f"Error correo: {e}")

# ---------------- AUTOMATIZACION ----------------
if ef < 80:
    generar_pdf(data, ef, estado)
    enviar_alerta("reporte_kpi.pdf", ef, estado)

# ---------------- TABLA ----------------
st.subheader("Datos")
st.dataframe(data)

# ---------------- DESCARGA ----------------
if st.button("Descargar PDF"):
    generar_pdf(data, ef, estado)
    with open("reporte_kpi.pdf", "rb") as f:
        st.download_button("Descargar", f)
st.subheader("Captura de Datos")

with st.form("form_produccion"):
    fecha = st.date_input("Fecha")
    area = st.text_input("Área")
    producto = st.text_input("Producto")
    maquina = st.text_input("Máquina")
    produccion = st.number_input("Producción real", min_value=0)
    
    enviar = st.form_submit_button("Guardar")

    if enviar:
        nuevo = pd.DataFrame([{
            "fecha": fecha,
            "area": area,
            "producto": producto,
            "maquina": maquina,
            "produccion_real": produccion
        }])

        st.success("Datos capturados correctamente")
        st.dataframe(nuevo)
