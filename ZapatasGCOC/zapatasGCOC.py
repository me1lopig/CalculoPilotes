import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import math

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Cimentaciones Superficiales - Guía Fomento", 
    page_icon="🏗️", 
    layout="wide"
)

# --- FUNCIONES MATEMÁTICAS (MOTOR DE CÁLCULO) ---
def calcular_factores_N(phi_grados):
    """Calcula los factores de capacidad de carga de Brinch-Hansen."""
    if phi_grados == 0:
        return 1.0, 5.14, 0.0  # Nq, Nc, Ng para condiciones no drenadas (Corto Plazo)
    
    phi_rad = math.radians(phi_grados)
    Nq = math.exp(math.pi * math.tan(phi_rad)) * (math.tan(math.radians(45) + phi_rad/2))**2
    Nc = (Nq - 1) / math.tan(phi_rad)
    Ng = 2 * (Nq - 1) * math.tan(phi_rad)
    return Nq, Nc, Ng

def calcular_gamma_efectivo(gamma_ap, gamma_sub, hw, B_star):
    """Interpola el peso específico efectivo según la posición del nivel freático."""
    if hw == 0:
        return gamma_sub
    elif hw > 0:
        gamma_calc = gamma_sub + 0.6 * (gamma_ap - gamma_sub) * (hw / B_star)
        return min(gamma_calc, gamma_ap)
    else:
        return gamma_sub

def calcular_pvh(q, c, gamma, B_star, L_star, Nq, Nc, Ng, phi_grados):
    """Calcula la presión vertical de hundimiento teórica (Fórmula general)."""
    # Factores de forma simplificados (Brinch-Hansen)
    if phi_grados == 0:
        sq = 1.0
        sc = 1.0 + 0.2 * (B_star / L_star)
        sg = 1.0
    else:
        sq = 1.0 + (B_star / L_star) * math.sin(math.radians(phi_grados))
        sc = (sq * Nq - 1) / (Nq - 1)
        sg = max(1.0 - 0.3 * (B_star / L_star), 0.6)
        
    term_q = q * Nq * sq
    term_c = c * Nc * sc
    term_g = 0.5 * gamma * B_star * Ng * sg
    
    return term_q + term_c + term_g

# --- INTERFAZ DE USUARIO ---
st.title("🏗️ Dimensionamiento Analítico de Cimentaciones")
st.markdown("Basado en la Guía de Cimentaciones en Obras de Carretera (Método de Brinch-Hansen)")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración Global")
    modo_operacion = st.radio(
        "Modo de Operación:", 
        options=[
            "A: Pre-dimensionamiento (Carta de Tensiones)", 
            "B: Verificación Estructural (Con Cargas)"
        ]
    )
    
    st.divider()
    situacion = st.selectbox(
        "Situación de Proyecto (FS Objetivo):",
        options=[
            "Persistente (FS = 3.00)", 
            "Transitoria (FS = 2.50)", 
            "Accidental (FS = 2.00)"
        ]
    )
    # Extraer el número del texto seleccionado
    fs_objetivo = float(situacion.split("= ")[1].replace(")", ""))
    
    drenaje = st.radio(
        "Condición del terreno:", 
        options=["Largo Plazo (Drenado)", "Corto Plazo (No Drenado)"]
    )

# --- ENTRADA DE DATOS ---
col1, col2, col3 = st.columns(3)

with col1:
    with st.expander("🌍 Parámetros del Terreno", expanded=True):
        if drenaje == "Largo Plazo (Drenado)":
            c = st.number_input("Cohesión efectiva, c (kPa)", min_value=0.0, value=10.0)
            phi = st.number_input("Ángulo rozamiento, $\phi$ (°)", min_value=0.0, max_value=45.0, value=30.0)
        else:
            c = st.number_input("Resistencia al corte, $s_u$ (kPa)", min_value=0.0, value=50.0)
            phi = 0.0
            st.info("A corto plazo se asume $\phi = 0$")
            
        gamma_ap = st.number_input("Peso esp. aparente, $\gamma_{ap}$ (kN/m³)", min_value=0.1, value=20.0)
        gamma_sub = st.number_input("Peso esp. sumergido, $\gamma'$ (kN/m³)", min_value=0.1, value=10.0)

with col2:
    with st.expander("📏 Geometría Iterativa y Nivel Freático", expanded=True):
        D = st.number_input("Profundidad de apoyo, D (m)", min_value=0.0, value=1.5, step=0.1)
        hw = st.number_input("Nivel Freático bajo base, $h_w$ (m)", min_value=0.0, value=5.0)
        
        st.markdown("**Rangos de Dimensiones de la Zapata:**")
        B_min = st.number_input("Ancho B min (m)", min_value=0.5, value=1.0, step=0.5)
        B_max = st.number_input("Ancho B max (m)", min_value=1.0, value=4.0, step=0.5)
        B_inc = st.number_input("Incremento de B (m)", min_value=0.1, value=0.5, step=0.1)
        
        L_min = st.number_input("Longitud L min (m)", min_value=0.5, value=1.0, step=0.5)
        L_max = st.number_input("Longitud L max (m)", min_value=1.0, value=5.0, step=0.5)
        L_inc = st.number_input("Incremento de L (m)", min_value=0.1, value=0.5, step=0.1)

with col3:
    with st.expander("⚖️ Cargas de la Estructura", expanded=True):
        if modo_operacion.startswith("B"):
            V = st.number_input("Carga Vertical, V (kN)", min_value=0.1, value=1000.0)
            M_B = st.number_input("Momento flector en eje B, $M_B$ (mkN)", value=0.0)
            M_L = st.number_input("Momento flector en eje L, $M_L$ (mkN)", value=0.0)
            st.caption("Nota: En esta versión simplificada no se calculan los factores de inclinación de carga ($i$).")
        else:
            st.info("Modo A: Cargas desactivadas. Se asume carga totalmente centrada y vertical para generar la Carta de Tensiones Admisibles.")

st.divider()

# --- MOTOR DE CÁLCULO ITERATIVO ---
resultados = []
Nq, Nc, Ng = calcular_factores_N(phi)
q_sobrecarga = gamma_ap * D

# Bucle bidimensional
for B in np.arange(B_min, B_max + B_inc, B_inc):
    for L in np.arange(L_min, L_max + L_inc, L_inc):
        
        # Evitar calcular zapatas donde L < B (por definición B es el lado menor)
        if L < B:
            continue
            
        if modo_operacion.startswith("B"):
            # Modo B: Cargas reales con excentricidad
            e_B, e_L = abs(M_B / V), abs(M_L / V)
            B_star = B - 2 * e_B
            L_star = L - 2 * e_L
            
            # Comprobar vuelco geométrico (excentricidad mayor que B/2 o L/2)
            if B_star <= 0 or L_star <= 0:
                continue 
                
            p_actuante = V / (B_star * L_star)
        else:
            # Modo A: Zapatas puras y centradas
            B_star, L_star = B, L
            p_actuante = 0.0
            
        gamma_eff = calcular_gamma_efectivo(gamma_ap, gamma_sub, hw, B_star)
        pvh = calcular_pvh(q_sobrecarga, c, gamma_eff, B_star, L_star, Nq, Nc, Ng, phi)
        
        # Guardar en diccionario de resultados según el modo
        if modo_operacion.startswith("B"):
            fs_calc = pvh / p_actuante
            cumple = "✅ Sí" if fs_calc >= fs_objetivo else "❌ No"
            resultados.append({
                "B (m)": round(B, 2), 
                "L (m)": round(L, 2), 
                "Área Ef. (m²)": round(B_star * L_star, 2), 
                "p_actuante (kPa)": round(p_actuante, 1), 
                "p_hundimiento (kPa)": round(pvh, 1), 
                "FS": round(fs_calc, 2), 
                "Cumple": cumple
            })
        else:
            p_adm = pvh / fs_objetivo
            resultados.append({
                "B (m)": round(B, 2), 
                "L (m)": round(L, 2), 
                "p_hundimiento (kPa)": round(pvh, 1), 
                "p_admisible (kPa)": round(p_adm, 1)
            })

# Convertir la lista de resultados a un DataFrame de Pandas
df_res = pd.DataFrame(resultados)

# --- PANEL DE RESULTADOS (PESTAÑAS) ---
st.header("📊 Resultados del Análisis")
tab_grafica, tab_datos, tab_exportar = st.tabs(["📈 Gráfica General", "📋 Tabla de Datos", "📥 Exportar Memoria"])

with tab_grafica:
    if df_res.empty:
        st.error("⚠️ No hay geometrías válidas en el rango seleccionado o la excentricidad hace volcar la zapata en todas las iteraciones.")
    else:
        if modo_operacion.startswith("A"):
            # Gráfica Modo A: Mapa de Calor Exacto (Limpiando valores nulos)
            matriz_z = df_res.pivot(index="L (m)", columns="B (m)", values="p_admisible (kPa)")
            
            # Máscara para borrar los 'nan' y que no salgan ceros en el gráfico
            text_matrix = np.round(matriz_z.values, 1).astype(str)
            text_matrix[text_matrix == 'nan'] = ''
            
            fig = go.Figure(data=go.Heatmap(
                z=matriz_z.values,
                x=matriz_z.columns,
                y=matriz_z.index,
                colorscale="Viridis",
                text=text_matrix,
                texttemplate="%{text}",
                hoverongaps=False,
                showscale=True
            ))
            
            fig.update_layout(
                title=f"Mapa de Calor: Tensión Admisible del Terreno (kPa) para FS = {fs_objetivo}",
                xaxis_title="Ancho de Zapata, B (m)",
                yaxis_title="Longitud de Zapata, L (m)",
                plot_bgcolor='rgba(0,0,0,0)' # Fondo transparente para celdas vacías
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif modo_operacion.startswith("B"):
            # Gráfica Modo B: Scatter Plot de Seguridad
            fig = px.scatter(
                df_res, 
                x="B (m)", 
                y="L (m)", 
                color="FS", 
                title="Mapa de Seguridad Estructural: Combinaciones B x L",
                color_continuous_scale="RdYlGn", 
                range_color=[fs_objetivo - 1, fs_objetivo + 2], # Rango centrado en el límite
                hover_data=["p_actuante (kPa)", "p_hundimiento (kPa)", "Cumple"]
            )
            fig.update_traces(marker=dict(size=15, line=dict(width=1, color='DarkSlateGrey')))
            fig.update_layout(xaxis_title="Ancho de Zapata, B (m)", yaxis_title="Longitud de Zapata, L (m)")
            st.plotly_chart(fig, use_container_width=True)

with tab_datos:
    st.subheader("Desglose Iterativo")
    if not df_res.empty:
        st.dataframe(df_res, use_container_width=True, hide_index=True)

with tab_exportar:
    st.subheader("Descargar Resultados")
    if not df_res.empty:
        st.write("Haz clic en el botón inferior para exportar la tabla iterativa en formato CSV, lista para integrar en los Anejos de Geotecnia o Estructuras.")
        csv = df_res.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Descargar Tabla en CSV",
            data=csv,
            file_name='analisis_cimentacion.csv',
            mime='text/csv',
        )