import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Calculadora de Colapsabilidad", layout="wide")

st.title("Determinación de la Colapsabilidad de Suelos")
st.markdown("""
Esta aplicación realiza los cálculos geotécnicos basándose en los criterios de **González Vallejo**, **Priklonski** y **Gibbs**.
""")

# --- BARRA LATERAL: DATOS DE ENTRADA ---
st.sidebar.header("Datos de Entrada")

# Valores por defecto (basados en el PDF original)
def_gamma_d = 12.00
def_w = 9.00
def_Sr = 80.00
def_LL = 30.00
def_LP = 20.00
def_Cp = 2.00

# Entradas de usuario
gamma_d_kn = st.sidebar.number_input("Peso específico seco, γd (KN/m³)", value=def_gamma_d, format="%.2f")
w = st.sidebar.number_input("Humedad natural, w (%)", value=def_w, format="%.2f")
Sr = st.sidebar.number_input("Grado de saturación, Sr (%)", value=def_Sr, format="%.2f")
LL = st.sidebar.number_input("Límite Líquido, LL", value=def_LL, format="%.2f")
LP = st.sidebar.number_input("Límite Plástico, LP", value=def_LP, format="%.2f")
Cp = st.sidebar.number_input("Potencial de colapso, Cp (%)", value=def_Cp, format="%.2f")

# Cálculos previos generales
IP = LL - LP
gamma_d_t = gamma_d_kn / 9.81 

st.sidebar.markdown("---")
st.sidebar.info(f"**Índice de Plasticidad (IP):** {IP:.2f}")
st.sidebar.info(f"**γd (T/m³):** {gamma_d_t:.2f}")

# --- CUERPO PRINCIPAL ---

# ==========================================
# 1. CRITERIO DE GONZÁLEZ VALLEJO (2002)
# ==========================================
st.subheader("1. Criterio de González Vallejo (2002)")

# Definición de la tabla de referencia
data_vallejo = {
    "Grado de colapso": ["Bajo", "Bajo a medio", "Medio a alto", "Alto a muy alto"],
    "Peso específico seco (KN/m³)": ["> 14,0", "12,0 - 14,0", "10,0 - 12,0", "< 10,0"],
    "Potencial de colapso (%)": ["< 0,25", "0,25 - 1,0", "1,0 - 5,0", "> 5,0"]
}
df_vallejo = pd.DataFrame(data_vallejo)

# Determinar índices para resaltar
# Para Peso Específico (KN/m3)
idx_gamma = 3 # Default (Alto a muy alto / <10)
if gamma_d_kn > 14.0: idx_gamma = 0
elif gamma_d_kn > 12.0: idx_gamma = 1
elif gamma_d_kn >= 10.0: idx_gamma = 2

# Para Potencial de Colapso (%)
idx_cp = 3 # Default (>5.0)
if Cp < 0.25: idx_cp = 0
elif Cp < 1.0: idx_cp = 1
elif Cp <= 5.0: idx_cp = 2

# Función de estilo para resaltar celdas individuales
def highlight_cells(x):
    df_st = pd.DataFrame('', index=x.index, columns=x.columns)
    # Resaltar celda de Peso Específico (Columna 1)
    df_st.iloc[idx_gamma, 1] = 'background-color: #ff4b4b; color: white; font-weight: bold'
    # Resaltar celda de Potencial de Colapso (Columna 2)
    df_st.iloc[idx_cp, 2] = 'background-color: #ff4b4b; color: white; font-weight: bold'
    return df_st

st.markdown("La tabla muestra en **rojo** la clasificación correspondiente a cada parámetro por separado:")
st.table(df_vallejo.style.apply(highlight_cells, axis=None))

st.markdown(f"**Análisis:**")
st.markdown(f"- Según Peso Específico ({gamma_d_kn} KN/m³): **{df_vallejo.iloc[idx_gamma, 0]}**")
st.markdown(f"- Según Potencial de Colapso ({Cp}%): **{df_vallejo.iloc[idx_cp, 0]}**")

st.markdown("---")

# Columnas para los otros dos métodos
col1, col2 = st.columns(2)

# ==========================================
# 2. CRITERIO DE PRIKLONSKI (1952)
# ==========================================
with col1:
    st.subheader("2. Criterio de Priklonski (1952)")
    
    # Cálculo
    if IP != 0:
        Kd = (w - LP) / IP
        calc_str = f"({w} - {LP}) / {IP}"
    else:
        Kd = 0
        calc_str = "Error (IP=0)"

    # Clasificación
    if Kd < 0:
        estado_prik = "ALTAMENTE COLAPSABLE"
        color_prik = "🔴" # Rojo
    elif Kd > 1:
        estado_prik = "EXPANSIVO"
        color_prik = "🔵" # Azul
    else:
        estado_prik = "NO COLAPSABLE"
        color_prik = "🟢" # Verde

    # Tabla de Resultados Estética
    df_prik = pd.DataFrame({
        "Parámetro": ["Humedad (w)", "Límite Plástico (LP)", "Índice Plasticidad (IP)", "Resultado (KD)", "Clasificación"],
        "Valor": [f"{w}%", f"{LP}", f"{IP}", f"{Kd:.2f}", f"{color_prik} {estado_prik}"]
    })
    
    st.latex(r"K_D = \frac{w - LP}{IP}")
    st.table(df_prik.set_index("Parámetro"))
    
    st.caption("Criterio: $K_D < 0$ (Colapsable), $K_D > 1$ (Expansivo)")


# ==========================================
# 3. CRITERIO DE GIBBS (1961)
# ==========================================
with col2:
    st.subheader("3. Criterio de Gibbs (1961)")
    
    # Cálculo
    Ig = 2.6 / (1 + (0.026 * LL))
    
    # Clasificación
    if Ig > gamma_d_t:
        estado_gibbs = "SUELO COLAPSABLE"
        desc_gibbs = "Densidad Real < Crítica"
        color_gibbs = "🔴"
    else:
        estado_gibbs = "NO COLAPSABLE"
        desc_gibbs = "Densidad Real > Crítica"
        color_gibbs = "🟢"

    # Tabla de Resultados Estética
    df_gibbs = pd.DataFrame({
        "Parámetro": ["Límite Líquido (LL)", "Densidad Crítica calc. (IG)", "Densidad Real (γd)", "Clasificación"],
        "Valor": [f"{LL}", f"{Ig:.2f} T/m³", f"{gamma_d_t:.2f} T/m³", f"{color_gibbs} {estado_gibbs}"]
    })

    st.latex(r"I_G = \frac{2.6}{1 + (0.026 \cdot LL)}")
    st.table(df_gibbs.set_index("Parámetro"))
    
    st.caption(f"Condición: {desc_gibbs}")

# ==========================================
# GRÁFICO DE GIBBS
# ==========================================
st.markdown("---")
st.subheader("Gráfico del Criterio de Gibbs")

# Generar datos curva
ll_range = np.linspace(10, 80, 100)
ig_curve = 2.6 / (1 + (0.026 * ll_range))

fig, ax = plt.subplots(figsize=(10, 5))

# Curva límite
ax.plot(ig_curve, ll_range, label="Curva Límite (Gibbs)", color="#1f77b4", linewidth=2)

# Punto del suelo
ax.scatter([gamma_d_t], [LL], color="red", s=150, zorder=5, label="Muestra Actual", edgecolors="black")

# Zonas
ax.fill_betweenx(ll_range, 0, ig_curve, color='red', alpha=0.1, label="Zona Colapsable")
ax.fill_betweenx(ll_range, ig_curve, 3.0, color='green', alpha=0.1, label="Zona Estable")

# Formato
ax.set_xlabel("Peso Específico Seco (T/m³)", fontsize=12)
ax.set_ylabel("Límite Líquido (LL)", fontsize=12)
ax.set_xlim(0.5, 2.5) # Ajustado para mejor visualización
ax.set_ylim(0, 80)
ax.set_title("Relación de Densidad vs Límite Líquido")
ax.legend(loc="upper right")
ax.grid(True, linestyle='--', alpha=0.5)

st.pyplot(fig)