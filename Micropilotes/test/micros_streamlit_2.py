import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Cálculo de Adherencia límite (Micropilotes)", layout="wide")

st.title("🧮 Calculadora de Adherencia límite por Fuste")
st.markdown("""
Esta herramienta calcula la **Adherencia límite** ($r_{f,lim}$) utilizando **modelos lineales a trozos** ajustados a las gráficas de la normativa.
""")

# --- FUNCIONES DE CÁLCULO (PIECEWISE LINEAR) ---

def calcular_arenas(plim):
    """Modelo lineal a trozos para Arenas y Gravas (Imagen 1)"""
    # Puntos extraídos: (Plim, rf_lim)
    # IRS: Satura 0.62 en ~2.8
    x_irs = [0.0, 0.5, 2.8, 10.0]; y_irs = [0.0, 0.14, 0.62, 0.62]
    # IR: Satura 0.50 en ~3.3
    x_ir  = [0.0, 0.5, 3.3, 10.0]; y_ir  = [0.0, 0.09, 0.50, 0.50]
    # IU: Satura 0.40 en ~3.5
    x_iu  = [0.0, 0.5, 3.5, 10.0]; y_iu  = [0.0, 0.04, 0.40, 0.40]
    
    tau_irs = np.interp(plim, x_irs, y_irs)
    tau_ir  = np.interp(plim, x_ir, y_ir)
    tau_iu  = np.interp(plim, x_iu, y_iu)
    return tau_iu, tau_ir, tau_irs

def calcular_arcillas(plim):
    """Modelo lineal a trozos para Arcillas y Limos (Imagen 2)"""
    # Puntos extraídos para seguir la curvatura de la imagen:
    # IRS: (0.25, 0.12), (0.5, 0.20), (1.0, 0.30), (1.8, 0.40)
    x_irs = [0.0, 0.25, 0.5, 1.0, 1.8, 10.0]
    y_irs = [0.0, 0.12, 0.20, 0.30, 0.40, 0.40]
    
    # IR: (0.25, 0.07), (0.5, 0.12), (1.0, 0.18), (2.1, 0.30)
    x_ir  = [0.0, 0.25, 0.5, 1.0, 2.1, 10.0]
    y_ir  = [0.0, 0.07, 0.12, 0.18, 0.30, 0.30]
    
    # IU: (0.25, 0.05), (0.5, 0.08), (1.0, 0.12), (2.3, 0.20)
    x_iu  = [0.0, 0.25, 0.5, 1.0, 2.3, 10.0]
    y_iu  = [0.0, 0.05, 0.08, 0.12, 0.20, 0.20]
    
    tau_irs = np.interp(plim, x_irs, y_irs)
    tau_ir  = np.interp(plim, x_ir, y_ir)
    tau_iu  = np.interp(plim, x_iu, y_iu)
    return tau_iu, tau_ir, tau_irs

# --- BARRA LATERAL (ENTRADAS) ---
st.sidebar.header("⚙️ Datos de Entrada")

tipo_suelo = st.sidebar.selectbox("Selecciona el Tipo de Suelo:", ("Arenas y Gravas", "Arcillas y Limos"))

plim_calculo = 0.0
input_label = ""

if tipo_suelo == "Arenas y Gravas":
    st.sidebar.info("Rango: $P_{lim} \geq 0.5$ MPa ($N \geq 10$)")
    tipo_dato = st.sidebar.radio("Entrada:", ["Presión Límite (Plim)", "Índice SPT (N)"])
    if tipo_dato == "Presión Límite (Plim)":
        val = st.sidebar.number_input("Plim (MPa)", min_value=0.5, max_value=7.0, value=2.0, step=0.1)
        plim_calculo = val
        input_label = f"Plim = {val} MPa"
    else:
        val = st.sidebar.number_input("SPT (N)", min_value=10, max_value=100, value=30, step=1)
        plim_calculo = val / 20.0
        input_label = f"N = {val} (Plim ≈ {plim_calculo:.2f} MPa)"
    x_min_plot, x_max_plot, p_transicion = 0.0, 7.0, 0.5

else: # Arcillas y Limos
    st.sidebar.info("Rango: $P_{lim} \geq 0.25$ MPa ($q_u \geq 0.05$ MPa)")
    tipo_dato = st.sidebar.radio("Entrada:", ["Presión Límite (Plim)", "Compresión Simple (qu)"])
    if tipo_dato == "Presión Límite (Plim)":
        val = st.sidebar.number_input("Plim (MPa)", min_value=0.25, max_value=2.5, value=1.0, step=0.05)
        plim_calculo = val
        input_label = f"Plim = {val} MPa"
    else:
        val = st.sidebar.number_input("qu (MPa)", min_value=0.05, max_value=0.5, value=0.2, step=0.01)
        plim_calculo = val * 5.0
        input_label = f"qu = {val} MPa (Plim ≈ {plim_calculo:.2f} MPa)"
    x_min_plot, x_max_plot, p_transicion = 0.0, 2.5, 0.25

# --- CÁLCULOS ---
if tipo_suelo == "Arenas y Gravas":
    res_iu, res_ir, res_irs = calcular_arenas(plim_calculo)
else:
    res_iu, res_ir, res_irs = calcular_arcillas(plim_calculo)

# --- VISUALIZACIÓN ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Resultados ($r_{f,lim}$)")
    st.write(f"**Suelo:** {tipo_suelo}")
    st.write(f"**Entrada:** {input_label}")
    st.markdown("---")
    st.metric(label="IRS (Selectiva)", value=f"{res_irs:.3f} MPa")
    st.metric(label="IR (Repetitiva)", value=f"{res_ir:.3f} MPa")
    st.metric(label="IU (Única)", value=f"{res_iu:.3f} MPa")
    st.info("Valores ajustados mediante interpolación lineal por tramos.")

with col2:
    st.subheader("📈 Gráfico de Diseño")
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    # Generar datos para la gráfica
    x_solid = np.linspace(p_transicion, x_max_plot, 200)
    x_dotted = np.linspace(0, p_transicion, 50)
    
    if tipo_suelo == "Arenas y Gravas":
        y_sol = calcular_arenas(x_solid); y_dot = calcular_arenas(x_dotted)
        label_sec = "Índice SPT (N)"; y_lim_max = 0.8
    else:
        y_sol = calcular_arcillas(x_solid); y_dot = calcular_arcillas(x_dotted)
        label_sec = "Compresión Simple $q_u$ (MPa)"; y_lim_max = 0.45

    # Dibujar líneas (sólidas para rango válido, punteadas para el inicio)
    for i, (lab, style) in enumerate(zip(['IU', 'IR', 'IRS'], ['--', '-.', '-'])):
        ax1.plot(x_solid, y_sol[i], 'k', linestyle=style, label=lab, linewidth=2)
        ax1.plot(x_dotted, y_dot[i], 'k', linestyle=':', alpha=0.5, linewidth=1)
    
    # Indicador de usuario
    ax1.axvline(x=plim_calculo, color='red', linestyle=':', alpha=0.6)
    ax1.scatter([plim_calculo]*3, [res_iu, res_ir, res_irs], color='red', zorder=5)
    
    ax1.set_xlabel('Presión límite $P_{lim}$ (MPa)')
    ax1.set_ylabel('Rozamiento unitario límite $r_{f,lim}$ (MPa)')
    ax1.set_xlim(0, x_max_plot)
    ax1.set_ylim(0, y_lim_max)
    ax1.grid(True, which='both', linestyle='--', alpha=0.3)
    ax1.legend()

    # Eje secundario
    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    ax2.xaxis.set_ticks_position('bottom')
    ax2.xaxis.set_label_position('bottom')
    ax2.spines['bottom'].set_position(('outward', 45))
    
    ticks = ax1.get_xticks()
    ax2.set_xticks(ticks)
    if tipo_suelo == "Arenas y Gravas":
        ax2.set_xticklabels([f"{int(t * 20)}" for t in ticks])
    else:
        ax2.set_xticklabels([f"{t / 5:.2f}" for t in ticks])
    ax2.set_xlabel(label_sec)
    
    st.pyplot(fig)