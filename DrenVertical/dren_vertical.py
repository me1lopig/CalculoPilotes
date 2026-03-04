import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Cálculo de Drenes Verticales", layout="wide")

st.title("💧 Consolidación mediante Drenes Verticales")
st.markdown("Cálculo del grado de consolidación usando la teoría tridimensional (Flujo vertical + Flujo radial).")

# --- BARRA LATERAL: DATOS DE ENTRADA ---
st.sidebar.header("📥 Datos de Entrada")

S = st.sidebar.number_input("Separación entre drenes (S) [cm]", min_value=50.0, max_value=500.0, value=150.0, step=10.0)
malla = st.sidebar.selectbox("Tipo de malla", ["Triangular", "Cuadrada"])
D_w = st.sidebar.number_input("Diámetro del dren (Dw) [cm]", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
C_v = st.sidebar.number_input("Coeficiente consol. vertical (Cv) [cm²/s]", value=0.001529, format="%.6f")
C_h = st.sidebar.number_input("Coeficiente consol. horizontal (Ch) [cm²/s]", value=0.006116, format="%.6f")
L = st.sidebar.number_input("Espesor del terreno (L) [m]", min_value=1.0, value=6.0, step=0.5)
bordes = st.sidebar.selectbox("Nº de bordes de drenaje", [1, 2], index=0)

# --- CÁLCULOS INTERMEDIOS ---
coeficiente = 1.05 if malla == "Triangular" else 1.13
D = coeficiente * S
n = D / D_w

# Factor a (Fórmula exacta de Barron)
a = ((n**2) / (n**2 - 1)) * np.log(n) - ((3 * n**2 - 1) / (4 * n**2))

st.sidebar.markdown("---")
st.sidebar.subheader("Cálculos Internos Geométricos")
st.sidebar.write(f"**Diámetro equivalente (D):** {D:.2f} cm")
st.sidebar.write(f"**Relación (n):** {n:.2f}")
st.sidebar.write(f"**Factor de resistencia (a):** {a:.4f}")

# --- MOTOR DE CÁLCULO DE LA TABLA ---
# Días: 0, 15, y luego de 30 a 810 de 30 en 30
dias = [0, 15] + list(range(30, 811, 30))
df = pd.DataFrame({"Tiempo (días)": dias})
df["Tiempo (años)"] = df["Tiempo (días)"] / 365.0

t_segundos = df["Tiempo (días)"] * 86400

# Consolidación Radial (Uh)
T_h = (C_h * t_segundos) / (D**2)
df["Th"] = T_h
df["Uh (%)"] = np.where(t_segundos == 0, 0, (1 - np.exp(-8 * T_h / a)) * 100)

# Consolidación Vertical (Uv)
H = (L * 100) if bordes == 1 else (L * 100) / 2
T_v = (C_v * t_segundos) / (H**2)
df["Tv"] = T_v

U_v_frac = np.where(T_v <= 0.283, 
                    np.sqrt((4 * T_v) / np.pi), 
                    1 - (8 / np.pi**2) * np.exp(-(np.pi**2 / 4) * T_v))
df["Uv (%)"] = np.where(t_segundos == 0, 0, U_v_frac * 100)

# Grado de Consolidación Total (U)
df["U (%)"] = 100 * (1 - (1 - df["Uh (%)"]/100) * (1 - df["Uv (%)"]/100))

# Redondeo para mostrar limpio
df_display = df.copy()
for col in ["Th", "Tv", "Uh (%)", "Uv (%)", "U (%)"]:
    df_display[col] = df_display[col].round(4)

# --- ZONA CENTRAL: PESTAÑAS (TABS) ---
tab1, tab2, tab3 = st.tabs(["📈 Gráficas de Consolidación", "📋 Tabla de Cálculos", "🧮 Fórmulas de Cálculo"])

with tab1:
    st.subheader("Evolución del Grado de Consolidación en el Tiempo")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Tiempo (días)"], df["U (%)"], label="Consolidación Total (U)", color="blue", linewidth=2.5)
    ax.plot(df["Tiempo (días)"], df["Uh (%)"], label="Consol. Radial (Uh)", color="green", linestyle="--")
    ax.plot(df["Tiempo (días)"], df["Uv (%)"], label="Consol. Vertical (Uv)", color="red", linestyle=":")
    
    ax.set_xlabel("Tiempo (días)", fontsize=12)
    ax.set_ylabel("Grado de Consolidación (%)", fontsize=12)
    ax.set_title(f"Malla {malla} - Separación {S} cm", fontsize=14)
    ax.set_ylim(0, 105)
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend(loc="lower right")
    
    st.pyplot(fig)
    
    st.info(f"💡 **Dato clave:** Para alcanzar un 90% de consolidación total se requieren aproximadamente **{np.interp(90, df['U (%)'], df['Tiempo (días)']):.0f} días** con esta configuración.")

with tab2:
    st.subheader("Hoja de Resultados")
    st.dataframe(df_display, use_container_width=True)
    
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar tabla como CSV",
        data=csv,
        file_name='calculo_drenes.csv',
        mime='text/csv',
    )

with tab3:
    st.subheader("Formulación Matemática Aplicada")
    
    st.markdown("**1. Consolidación Total (Fórmula de Carrillo)**")
    st.markdown("Combina el efecto del drenaje vertical natural y el drenaje radial forzado:")
    st.latex(r"U = 1 - (1 - U_h) \times (1 - U_v)")
    st.markdown("---")
    
    st.markdown("**2. Consolidación Radial (Teoría de Hansbo / Barron)**")
    st.markdown("Calcula el porcentaje de consolidación debido exclusivamente al flujo horizontal hacia los drenes:")
    st.latex(r"U_h = 1 - \exp\left( - \frac{8 \cdot T_h}{F(n)} \right)")
    st.markdown("Donde el **Factor de Tiempo Radial ($T_h$)** es:")
    st.latex(r"T_h = \frac{C_h \cdot t}{D^2}")
    st.markdown("---")
    
    st.markdown("**3. Factor de Geometría Exácto ($F(n)$ o $a$)**")
    st.markdown("Representa la resistencia al flujo dependiendo de la relación entre el diámetro de influencia ($D$) y el diámetro del dren ($D_w$). Se utiliza la formulación exacta de Barron:")
    st.latex(r"F(n) = \frac{n^2}{n^2 - 1} \ln(n) - \frac{3n^2 - 1}{4n^2}")
    st.markdown("Donde $n = D / D_w$")