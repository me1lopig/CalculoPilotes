import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS PROFESIONALES
st.set_page_config(page_title="Cimentaciones en Roca - Herramienta de Ingeniería", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .titulo-seccion { 
        background-color: #1b5e20; 
        color: white; 
        padding: 12px; 
        font-weight: bold; 
        border-radius: 4px; 
        text-align: center; 
        margin-bottom: 20px; 
    }
    .titulo-norma {
        background-color: #1b5e20; 
        color: white; 
        padding: 8px 15px; 
        font-weight: bold; 
        border-radius: 4px 4px 0 0; 
        font-size: 14px;
        margin-top: 10px;
        border: 1px solid #1b5e20;
    }
    .tabla-profesional {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        margin-bottom: 25px;
        border: 1px solid #d1d1d1;
        background-color: white;
    }
    .tabla-profesional th {
        background-color: #f5f5f5;
        color: #333;
        padding: 10px;
        border: 1px solid #d1d1d1;
        font-weight: bold;
    }
    .tabla-profesional td {
        padding: 10px;
        border: 1px solid #d1d1d1;
        text-align: center;
        color: #444;
    }
    .text-left { text-align: left !important; padding-left: 15px !important; }
    .grupo-roca { background-color: #fafafa; font-weight: 500; }
    .requisitos { 
        background-color: #f1f8e9; 
        padding: 15px; 
        border-left: 5px solid #2e7d32; 
        border-radius: 4px; 
        font-size: 14px; 
        line-height: 1.6; 
    }
    .nota-pie-tabla { font-size: 11px; color: #666; margin-top: -15px; margin-bottom: 20px; padding-left: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ Cálculo de Presión Vertical Admisible en Roca según CTE DB SE C")

# --- SECCIÓN A: INDICACIONES Y FORMULACIÓN ---
st.markdown('<div class="titulo-seccion">INDICACIONES TÉCNICAS Y FORMULACIÓN</div>', unsafe_allow_html=True)

col_req, col_form = st.columns([0.6, 0.4])

with col_req:
    st.markdown("""
    <div class="requisitos">
        <strong>Requisitos del Cálculo Analítico Simplificado:</strong><br>
        • Para roca sana o poco meteorizada (qu > 2.5 MPa, RQD > 25 y GM < IV).<br>
        • Superficie de la roca esencialmente horizontal y sin problemas de estabilidad lateral.<br>
        • Carga con componente tangencial inferior al 10% de la carga normal.<br>
        • En rocas sedimentarias los estratos deben ser horizontales o subhorizontales.
    </div>
    """, unsafe_allow_html=True)

with col_form:
    st.markdown("**Formulación Matemática:**")
    st.latex(r"K_{sp} = \frac{3 + \frac{s}{1000 \cdot B}}{10 \sqrt{1 + 300 \frac{a}{s}}}")
    st.latex(r"q_d = q_u \cdot K_{sp}")
    st.caption("Donde: $s$ y $a$ en mm, $B$ en m.")

st.divider()

# --- SECCIÓN B: TABLAS NORMATIVAS ---
st.subheader("📚 Normas y Códigos de Uso Habitual")
col_izq, col_der = st.columns(2)

with col_izq:
    st.markdown('<div class="titulo-norma">DIN 1054</div>', unsafe_allow_html=True)
    st.markdown("""
    <table class="tabla-profesional">
        <tr>
            <th rowspan="2">Estado del macizo</th>
            <th colspan="2">Presión Admisible (MPa)</th>
        </tr>
        <tr>
            <th>Roca sana / poco alterada</th>
            <th>Roca quebradiza / alterada</th>
        </tr>
        <tr><td class="text-left grupo-roca">Homogéneo</td><td>4.00</td><td>1.50</td></tr>
        <tr><td class="text-left grupo-roca">Estratificado o diaclasado</td><td>2.00</td><td>1.00</td></tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown('<div class="titulo-norma">CTE 2006 (España)</div>', unsafe_allow_html=True)
    st.markdown("""
    <table class="tabla-profesional">
        <tr><th>Tipo de roca</th><th>q<sub>adm</sub> (MPa)</th></tr>
        <tr><td class="text-left grupo-roca">Rocas ígneas y metamórficas sanas (1)</td><td>10.00</td></tr>
        <tr><td class="text-left grupo-roca">Rocas metamórficas foliadas sanas (1) (2)</td><td>3.00</td></tr>
        <tr><td class="text-left grupo-roca">Rocas sedimentarias sanas (1) (2)</td><td>1.00 - 4.00</td></tr>
        <tr><td class="text-left grupo-roca">Rocas arcillosas sanas (2) (4)</td><td>0.50 - 1.00</td></tr>
        <tr><td class="text-left grupo-roca">Rocas diaclasadas (s > 0.30m)</td><td>1.00</td></tr>
        <tr><td class="text-left grupo-roca">Rocas muy diaclasadas o meteorizadas</td><td>(ver nota 3)</td></tr>
    </table>
    <div class="nota-pie-tabla">(1) Estrat. subhorizontal. (2) s > 1m. (3) In situ. (4) Arcillosas sanas.</div>
    """, unsafe_allow_html=True)

with col_der:
    st.markdown('<div class="titulo-norma">CP 2004 / 1972</div>', unsafe_allow_html=True)
    st.markdown("""
    <table class="tabla-profesional">
        <tr><th>Tipo de roca</th><th>q<sub>adm</sub> (MPa)</th></tr>
        <tr><td class="text-left grupo-roca">Rocas ígneas (granitos y gneises), sanas</td><td>10.00</td></tr>
        <tr><td class="text-left grupo-roca">Calizas y areniscas duras</td><td>4.00</td></tr>
        <tr><td class="text-left grupo-roca">Esquistos y pizarras</td><td>3.00</td></tr>
        <tr><td class="text-left grupo-roca">Argilitas/limolitas duras, areniscas blandas</td><td>2.00</td></tr>
        <tr><td class="text-left grupo-roca">Arenas cementadas</td><td>1.00</td></tr>
        <tr><td class="text-left grupo-roca">Argilitas y limolitas blandas</td><td>0.60 - 1.00</td></tr>
        <tr><td class="text-left grupo-roca">Calizas blandas y porosas</td><td>0.60</td></tr>
    </table>
    <div class="nota-pie-tabla">* Observaciones: Para rocas estables en agua.</div>
    """, unsafe_allow_html=True)

st.divider()

# --- SECCIÓN C: SIDEBAR (CONTROLES) ---
with st.sidebar:
    st.header("⚙️ Parámetros del Macizo")
    qu = st.number_input("Resistencia qu [MPa]", value=23.0, step=1.0)
    s = st.number_input("Espaciamiento s [mm]", value=200, step=10)
    a = st.number_input("Apertura a [mm]", value=3.0, step=0.1)
    
    # Etiquetas exactas del Excel
    opcion_limpia = "Limpias"
    opcion_rellena = "Rellenas con suelo o con fragmentos de roca alterada"
    estado_junta = st.selectbox("Estado de juntas", [opcion_limpia, opcion_rellena])
    
    st.divider()
    st.header("📏 Configuración de Anchos (B)")
    b_min = st.number_input("Ancho Mínimo B (m)", value=1.0, min_value=0.10, step=0.10)
    b_max = st.number_input("Ancho Máximo B (m)", value=3.00, min_value=b_min, step=0.50)
    b_step = st.selectbox("Incremento de B (m)", [0.25, 0.50, 1.00], index=1)

# Lógica de comprobaciones (LÍMITES DINÁMICOS)
c_s = s > 300
if estado_junta == opcion_limpia:
    c_a = a < 5
    label_a = "a < 5mm (Junta limpia)"
else:
    c_a = a < 25
    label_a = "a < 25mm (Junta rellena/alterada)"

rel_as = a/s
c_rel = 0 < rel_as < 0.02

st.subheader("✅ Comprobaciones de Seguridad")
v1, v2, v3 = st.columns(3)
v1.metric("Espaciamiento s > 300mm", "CUMPLE" if c_s else "NO CUMPLE")
v2.metric(label_a, "CUMPLE" if c_a else "NO CUMPLE")
v3.metric(f"Relación a/s < 0.02 ({rel_as:.3f})", "CUMPLE" if c_rel else "NO CUMPLE")

st.divider()

# --- SECCIÓN D: RESULTADOS ---
def calc_ksp(s_val, B_val, a_val):
    return (3 + (s_val / (B_val * 1000))) / (10 * np.sqrt(1 + 300 * (a_val / s_val)))

col_res_t, col_res_g = st.columns([0.45, 0.55], gap="large")

anchos_b = np.arange(b_min, b_max + 0.001, b_step)
filas = []
for b in anchos_b:
    k = calc_ksp(s, b, a)
    qd = qu * k
    valido = "SÍ" if 0.05 < (s / (b * 1000)) < 2 else "NO"
    filas.append({
        "B (m)": b,
        "Válido 0.05 < s/B < 2": valido,
        "Ksp": k,
        "qd (MPa)": qd,
        "qd (kg/cm²)": qd * 1000/98.1 # Tu conversión específica
    })
df_res = pd.DataFrame(filas)

with col_res_t:
    st.subheader("📋 Resultados del Cálculo Analítico")
    st.dataframe(
        df_res,
        hide_index=True,
        use_container_width=True,
        column_config={
            "B (m)": st.column_config.NumberColumn(format="%.2f"),
            "Ksp": st.column_config.NumberColumn(format="%.2f"),
            "qd (MPa)": st.column_config.NumberColumn(format="%.2f"),
            "qd (kg/cm²)": st.column_config.NumberColumn(format="%.2f"),
        }
    )
    csv = df_res.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Resultados (CSV)", data=csv, file_name="calculo_roca.csv", mime="text/csv")

with col_res_g:
    st.subheader("📈 Presión admisible de servicio")
    b_smooth = np.linspace(b_min, b_max, 100)
    qd_smooth = [qu * calc_ksp(s, b, a) for b in b_smooth]
    
    fig = go.Figure(go.Scatter(
        x=b_smooth, y=qd_smooth,
        mode='lines',
        line=dict(color='#1b5e20', width=4),
        name='qd (MPa)',
        hovertemplate='B: %{x:.2f}m<br>qd: %{y:.2f} MPa<extra></extra>'
    ))
    
    fig.update_layout(
        xaxis_title="Ancho B (m)", yaxis_title="qd (MPa)",
        plot_bgcolor='white', margin=dict(l=0, r=0, t=10, b=0), height=400,
        yaxis=dict(gridcolor='#f0f0f0'), xaxis=dict(gridcolor='#f0f0f0')
    )
    st.plotly_chart(fig, use_container_width=True)