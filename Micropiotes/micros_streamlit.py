import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Cálculo de Rozamiento (Micropilotes)", layout="wide")

st.title("🧮 Calculadora de Rozamiento límite por Fuste")
st.markdown("""
Esta aplicación permite determinar el **rozamiento unitario límite** ($\\tau_{f,lim}$) 
para el diseño de micropilotes y anclajes, respetando los rangos mínimos de aplicación de las gráficas.
""")

# --- LÓGICA MATEMÁTICA ---

def calcular_arenas(plim):
    """Modelo lineal a trozos para Arenas y Gravas."""
    # IU: Satura en 0.40
    tau_iu = np.minimum(0.114 * plim, 0.40)
    # IR: Satura en 0.50
    tau_ir = np.minimum(0.145 * plim, 0.50)
    # IRS: Satura en 0.62
    tau_irs = np.minimum(0.210 * plim, 0.62)
    return tau_iu, tau_ir, tau_irs

def calcular_arcillas(plim):
    """Modelo de potencia para Arcillas y Limos."""
    plim = np.maximum(plim, 0.0)
    # IRS: Potencia 0.5, satura en 0.40
    tau_irs = np.minimum(0.28 * np.power(plim, 0.5), 0.40)
    # IR: Potencia 0.6, satura en 0.30
    tau_ir = np.minimum(0.19 * np.power(plim, 0.6), 0.30)
    # IU: Potencia 0.7, satura en 0.20
    tau_iu = np.minimum(0.11 * np.power(plim, 0.7), 0.20)
    return tau_iu, tau_ir, tau_irs

# --- BARRA LATERAL (ENTRADAS) ---
st.sidebar.header("⚙️ Configuración de Entrada")

tipo_suelo = st.sidebar.selectbox(
    "Selecciona el Tipo de Suelo:",
    ("Arenas y Gravas", "Arcillas y Limos")
)

# Variables de estado
plim_calculo = 0.0
input_label = ""
x_min_plot = 0.0 # Límite inferior para la gráfica

if tipo_suelo == "Arenas y Gravas":
    st.sidebar.info("⚠️ **Rango válido:**\n\n$P_{lim} \geq 0.5$ MPa\n($N_{SPT} \geq 10$)")
    tipo_dato = st.sidebar.radio("Dato de entrada disponible:", ["Presión Límite (Plim)", "Índice SPT (N)"])
    
    if tipo_dato == "Presión Límite (Plim)":
        # MÍNIMO 0.5 MPa
        val = st.sidebar.number_input("Valor Plim (MPa)", min_value=0.5, max_value=8.0, value=2.0, step=0.1)
        plim_calculo = val
        input_label = f"Plim = {val} MPa"
    else:
        # MÍNIMO 10 GOLPES
        val = st.sidebar.number_input("Valor SPT (N)", min_value=10, max_value=150, value=30, step=1)
        plim_calculo = val / 20.0
        input_label = f"N = {val} (Plim ≈ {plim_calculo:.2f} MPa)"
    
    x_min_plot = 0.5 # Límite para gráfica Arenas

else: # Arcillas y Limos
    st.sidebar.info("⚠️ **Rango válido:**\n\n$P_{lim} \geq 0.25$ MPa\n($q_u \geq 0.05$ MPa)")
    tipo_dato = st.sidebar.radio("Dato de entrada disponible:", ["Presión Límite (Plim)", "Compresión Simple (qu)"])
    
    if tipo_dato == "Presión Límite (Plim)":
        # MÍNIMO 0.25 MPa (Inicio visual de la curva)
        val = st.sidebar.number_input("Valor Plim (MPa)", min_value=0.25, max_value=3.0, value=1.0, step=0.05)
        plim_calculo = val
        input_label = f"Plim = {val} MPa"
    else:
        # MÍNIMO 0.05 MPa
        val = st.sidebar.number_input("Valor qu (MPa)", min_value=0.05, max_value=0.6, value=0.2, step=0.01)
        plim_calculo = val * 5.0
        input_label = f"qu = {val} MPa (Plim ≈ {plim_calculo:.2f} MPa)"
    
    x_min_plot = 0.25 # Límite para gráfica Arcillas

# --- CÁLCULOS ---

if tipo_suelo == "Arenas y Gravas":
    res_iu, res_ir, res_irs = calcular_arenas(plim_calculo)
else:
    res_iu, res_ir, res_irs = calcular_arcillas(plim_calculo)

# --- VISUALIZACIÓN ---

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Resultados")
    st.write(f"**Entrada:** {input_label}")
    st.markdown("---")
    
    # Formato condicional para resaltar el valor seleccionado
    st.metric(label="IRS (Iny. Selectiva)", value=f"{res_irs:.3f} MPa")
    st.metric(label="IR (Iny. Repetitiva)", value=f"{res_ir:.3f} MPa")
    st.metric(label="IU (Iny. Única)", value=f"{res_iu:.3f} MPa")
    
    st.markdown("---")
    if tipo_suelo == "Arenas y Gravas":
        st.caption("Nota: Para $N < 10$, se recomienda consultar normativas específicas o realizar ensayos in situ adicionales.")
    else:
        st.caption("Nota: Para arcillas muy blandas ($q_u < 0.05$ MPa), la capacidad de fuste es despreciable o requiere un estudio especial.")

with col2:
    st.subheader("📈 Gráfico de Comprobación")
    
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    if tipo_suelo == "Arenas y Gravas":
        x_max = 7.0
        title_graph = "Arenas y Gravas"
        label_sec = "Índice SPT (N)"
        # Generar curvas
        x_vals = np.linspace(x_min_plot, x_max, 200)
        y_iu, y_ir, y_irs = calcular_arenas(x_vals)
        
    else:
        x_max = 2.5
        title_graph = "Arcillas y Limos"
        label_sec = "Compresión Simple qu (MPa)"
        # Generar curvas
        x_vals = np.linspace(x_min_plot, x_max, 200)
        y_iu, y_ir, y_irs = calcular_arcillas(x_vals)

    # Plot curvas
    ax1.plot(x_vals, y_irs, 'k-', label='IRS', linewidth=2)
    ax1.plot(x_vals, y_ir, 'k-.', label='IR', linewidth=2)
    ax1.plot(x_vals, y_iu, 'k--', label='IU', linewidth=2)
    
    # Línea del usuario
    ax1.axvline(x=plim_calculo, color='red', linestyle=':', linewidth=2, label='Tu Dato')
    ax1.scatter([plim_calculo]*3, [res_iu, res_ir, res_irs], color='red', zorder=5)
    
    ax1.set_xlabel('Presión límite $P_{lim}$ (MPa)')
    ax1.set_ylabel('Rozamiento unitario $\\tau_{f,lim}$ (MPa)')
    ax1.set_title(f'Curvas de Diseño: {title_graph}')
    
    # AJUSTE DE LÍMITES EJE X (Dinámico según suelo)
    ax1.set_xlim(x_min_plot, x_max)
    ax1.set_ylim(0, 0.7 if tipo_suelo == "Arenas y Gravas" else 0.45)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Eje secundario
    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    
    ticks = ax1.get_xticks()
    # Filtrar ticks para que estén dentro del rango visual
    ticks = [t for t in ticks if t >= x_min_plot and t <= x_max]
    ax2.set_xticks(ticks)
    
    if tipo_suelo == "Arenas y Gravas":
        ax2.set_xticklabels([f"{int(t * 20)}" for t in ticks])
    else:
        ax2.set_xticklabels([f"{t / 5:.2f}" for t in ticks])
        
    ax2.set_xlabel(label_sec)
    ax2.xaxis.set_ticks_position('bottom')
    ax2.xaxis.set_label_position('bottom')
    ax2.spines['bottom'].set_position(('outward', 40))
    
    st.pyplot(fig)