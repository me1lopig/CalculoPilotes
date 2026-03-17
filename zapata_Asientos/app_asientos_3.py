import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# CONSTANTES
# ==========================================
GAMMA_AGUA = 9.81  # kN/m³

# ==========================================
# FUNCIONES MATEMÁTICAS: ASIENTOS (Ec. 69, 70, 71)
# ==========================================
def calcular_phi1(m, n):
    if m == 0:
        term1 = np.log(np.sqrt(1 + n**2) + n)
        term2 = n * np.log((np.sqrt(1 + n**2) + 1) / n)
    else:
        term1 = np.log((np.sqrt(1 + m**2 + n**2) + n) / np.sqrt(1 + m**2))
        term2 = n * np.log((np.sqrt(1 + m**2 + n**2) + 1) / np.sqrt(n**2 + m**2))
    return (1 / np.pi) * (term1 + term2)

def calcular_phi2(m, n):
    if m == 0: return 0.0
    return (m / np.pi) * np.arctan(n / (m * np.sqrt(1 + m**2 + n**2)))

def calcular_s_z(p, B, E, nu, z, L):
    n = L / B
    m = (2 * z) / B
    phi1 = calcular_phi1(m, n)
    phi2 = calcular_phi2(m, n)
    corchete = ((1 - nu**2) * phi1) - ((1 - nu - 2 * nu**2) * phi2)
    return (p * B / E) * corchete

# ==========================================
# FUNCIONES MATEMÁTICAS: TENSIONES HOLL
# ==========================================
def tensiones_holl_centro(p, B, L, z):
    if z <= 0.01:
        return p, p/2, p/2

    B_cuad = B / 2.0
    L_cuad = L / 2.0

    R1 = np.sqrt(L_cuad**2 + z**2)
    R2 = np.sqrt(B_cuad**2 + z**2)
    R3 = np.sqrt(L_cuad**2 + B_cuad**2 + z**2)

    term_arctan = np.arctan((B_cuad * L_cuad) / (z * R3))

    sigma_z_esq = (p / (2 * np.pi)) * (term_arctan + B_cuad * L_cuad * (1/R1**2 + 1/R2**2) * (z / R3))
    sigma_x_esq = (p / (2 * np.pi)) * (term_arctan - (B_cuad * L_cuad * z) / (R1**2 * R3))
    sigma_y_esq = (p / (2 * np.pi)) * (term_arctan - (B_cuad * L_cuad * z) / (R2**2 * R3))

    return 4 * sigma_z_esq, 4 * sigma_x_esq, 4 * sigma_y_esq

# ==========================================
# FUNCIONES: TENSIÓN EFECTIVA VERTICAL (σ'v0)
# ==========================================
def calcular_sigma_v0(df_terreno, z, Nf):
    """
    Calcula la tensión efectiva vertical geoestática σ'v0 (kPa)
    a la profundidad z, teniendo en cuenta el nivel freático Nf.
    - Por encima de Nf: se usa γ (peso específico aparente)
    - Por debajo de Nf: se usa γ' = γsat - γagua (peso sumergido)
    """
    sigma_v0 = 0.0
    z_actual = 0.0

    for _, row in df_terreno.iterrows():
        espesor = float(row["Espesor (m)"])
        gamma_ap = float(row["γ (kN/m³)"])
        gamma_sat = float(row["γsat (kN/m³)"])

        z_techo = z_actual
        z_base = z_actual + espesor

        if z <= z_techo:
            break  # Ya hemos pasado la profundidad objetivo

        z_eval = min(z, z_base)  # Hasta dónde integramos en esta capa

        # Tramo de la capa por encima del freático
        z_seco_techo = z_techo
        z_seco_base = min(z_eval, Nf)
        if z_seco_base > z_seco_techo:
            sigma_v0 += gamma_ap * (z_seco_base - z_seco_techo)

        # Tramo de la capa por debajo del freático
        z_sat_techo = max(z_techo, Nf)
        z_sat_base = z_eval
        if z_sat_base > z_sat_techo:
            gamma_efectivo = gamma_sat - GAMMA_AGUA
            sigma_v0 += gamma_efectivo * (z_sat_base - z_sat_techo)

        z_actual = z_base

    return sigma_v0

def calcular_zona_influencia(p, B, L, df_terreno, Nf):
    """
    Calcula la profundidad de influencia z_i (m) según el criterio EC7:
        Δσz(z_i) = 0.20 · σ'v0(z_i)
    Usa búsqueda iterativa sobre el rango de profundidades disponible.
    Devuelve (z_i, encontrado): z_i en metros, encontrado=True/False
    """
    espesor_total = float(pd.to_numeric(df_terreno["Espesor (m)"]).sum())
    if espesor_total <= 0:
        return None, False

    z_vals = np.linspace(0.05, espesor_total, 500)

    for z in z_vals:
        delta_sigma_z, _, _ = tensiones_holl_centro(p, B, L, z)
        sigma_v0 = calcular_sigma_v0(df_terreno, z, Nf)

        if sigma_v0 > 0 and delta_sigma_z <= 0.20 * sigma_v0:
            return z, True

    # Si no se encontró en el rango → la influencia supera la profundidad estudiada
    return espesor_total, False

# ==========================================
# GESTIÓN DE ESTADO (SESSION STATE)
# ==========================================
def reset_calculo():
    st.session_state.calculo_realizado = False

if 'calculo_realizado' not in st.session_state:
    st.session_state.calculo_realizado = False

if 'df_terreno' not in st.session_state:
    st.session_state.df_terreno = pd.DataFrame({
        "Descripción":               ["Relleno",  "Arcilla", "Grava"],
        "Espesor (m)":               [1.5,         8.0,       15.0],
        "Módulo Deformación E (kPa)":[10000.0,     5000.0,    40000.0],
        "Coef. Poisson (nu)":        [0.30,         0.45,      0.25],
        "γ (kN/m³)":                 [18.0,         17.0,      20.0],
        "γsat (kN/m³)":              [20.0,         19.0,      21.0],
    })

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y BARRA LATERAL
# ==========================================
st.set_page_config(page_title="Cálculo de Cimentaciones EC7", layout="wide", page_icon="🏗️")

st.sidebar.title("Navegación")
modo_vista = st.sidebar.radio(
    "Selecciona la vista principal:",
    ("🧮 Panel de Cálculo", "🔍 Desglose de Asientos", "📉 Incremento de Tensiones", "📖 Fundamento Teórico")
)

st.sidebar.markdown("---")
st.sidebar.header("📥 Datos Geométricos")

B = st.sidebar.number_input("Ancho zapata (B) [m]", min_value=0.1, value=2.0, step=0.1, on_change=reset_calculo)
L = st.sidebar.number_input("Longitud zapata (L) [m]", min_value=0.1, value=3.0, step=0.1, on_change=reset_calculo)
p = st.sidebar.number_input("Presión neta (p) [kPa]", min_value=1.0, value=150.0, step=10.0, on_change=reset_calculo)

if L < B:
    st.sidebar.warning("⚠️ L debería ser $\\ge$ B. Se intercambian internamente.")
    B, L = L, B

st.sidebar.info(f"**Esbeltez (n = L/B):** {L/B:.2f}")

st.sidebar.markdown("---")
st.sidebar.header("💧 Nivel Freático")
Nf = st.sidebar.number_input(
    "Profundidad nivel freático (Nf) [m]",
    min_value=0.0,
    value=100.0,
    step=0.5,
    help="Profundidad desde la base de la cimentación. Valor alto (p.ej. 100 m) = sin freático.",
    on_change=reset_calculo
)
if Nf >= 100.0:
    st.sidebar.caption("⬆️ Sin nivel freático activo.")
else:
    st.sidebar.caption(f"🌊 Freático a {Nf:.1f} m de profundidad.")

st.sidebar.markdown("---")

# --- BOTÓN DE CÁLCULO ---
if st.sidebar.button("🚀 Calcular Asiento Total", type="primary", use_container_width=True):
    asiento_total = 0.0
    z_actual = 0.0
    resultados_basicos = []
    resultados_detallados = []
    n_factor = L / B

    for index, row in st.session_state.df_terreno.iterrows():
        espesor = float(row["Espesor (m)"])
        E = float(row["Módulo Deformación E (kPa)"])
        nu = float(row["Coef. Poisson (nu)"])
        nombre = str(row["Descripción"])

        z_techo = z_actual
        z_base = z_actual + espesor

        m_techo = (2 * z_techo) / B
        m_base  = (2 * z_base)  / B

        s_techo = calcular_s_z(p, B, E, nu, z_techo, L)
        s_base  = calcular_s_z(p, B, E, nu, z_base,  L)

        delta_s = s_techo - s_base
        asiento_total += delta_s

        sigma_v0_techo = calcular_sigma_v0(st.session_state.df_terreno, z_techo, Nf)
        sigma_v0_base  = calcular_sigma_v0(st.session_state.df_terreno, z_base,  Nf)
        dsz_techo, _, _ = tensiones_holl_centro(p, B, L, max(z_techo, 0.01))
        dsz_base,  _, _ = tensiones_holl_centro(p, B, L, z_base)

        resultados_basicos.append({
            "Capa":                    nombre,
            "Prof. Techo [m]":         round(z_techo, 2),
            "Prof. Base [m]":          round(z_base,  2),
            "σ'v0 Techo [kPa]":        round(sigma_v0_techo, 2),
            "σ'v0 Base [kPa]":         round(sigma_v0_base,  2),
            "Δσz Techo [kPa]":         round(dsz_techo, 2),
            "Δσz Base [kPa]":          round(dsz_base,  2),
            "Asiento Aportado [mm]":   round(delta_s * 1000, 2)
        })

        resultados_detallados.append({
            "Capa":                    nombre,
            "z_techo [m]":             round(z_techo, 2),
            "m_techo":                 round(m_techo, 4),
            "φ1_techo":                round(calcular_phi1(m_techo, n_factor), 4),
            "φ2_techo":                round(calcular_phi2(m_techo, n_factor), 4),
            "s_techo_teórico [mm]":    round(s_techo * 1000, 3),
            "z_base [m]":              round(z_base,  2),
            "m_base":                  round(m_base,  4),
            "φ1_base":                 round(calcular_phi1(m_base, n_factor), 4),
            "φ2_base":                 round(calcular_phi2(m_base, n_factor), 4),
            "s_base_teórico [mm]":     round(s_base * 1000, 3),
            "Δs Real [mm]":            round(delta_s * 1000, 2)
        })

        z_actual = z_base

    # Zona de influencia
    z_i, zi_encontrado = calcular_zona_influencia(p, B, L, st.session_state.df_terreno, Nf)

    st.session_state.df_basico       = pd.DataFrame(resultados_basicos)
    st.session_state.df_detallado    = pd.DataFrame(resultados_detallados)
    st.session_state.asiento_total   = asiento_total
    st.session_state.z_i             = z_i
    st.session_state.zi_encontrado   = zi_encontrado
    st.session_state.calculo_realizado = True

# ==========================================
# ÁREA PRINCIPAL CENTRAL
# ==========================================
st.title("🏗️ Proyecto de Cimentaciones Superficiales")
st.markdown("Basado en la **Guía de Cimentaciones con Eurocódigo 7** (Ministerio de Transportes).")
st.markdown("---")

# --- VISTA 1: PANEL DE CÁLCULO ---
if modo_vista == "🧮 Panel de Cálculo":

    st.header("1. Estratigrafía del Terreno")
    st.write("Introduce las capas de terreno. Las columnas **γ** y **γsat** se usan para el cálculo de tensión efectiva y zona de influencia.")

    df_actualizado = st.data_editor(
        st.session_state.df_terreno,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "γ (kN/m³)":    st.column_config.NumberColumn("γ (kN/m³)",    min_value=10.0, max_value=25.0, step=0.5),
            "γsat (kN/m³)": st.column_config.NumberColumn("γsat (kN/m³)", min_value=10.0, max_value=25.0, step=0.5),
        }
    )

    if not df_actualizado.equals(st.session_state.df_terreno):
        st.session_state.df_terreno = df_actualizado
        st.session_state.calculo_realizado = False
        st.rerun()

    st.markdown("---")
    st.header("2. Resultados del Cálculo")

    if st.session_state.calculo_realizado:
        # --- Tabla y gráfico a ancho completo ---
        st.dataframe(st.session_state.df_basico, use_container_width=True)
        st.bar_chart(st.session_state.df_basico.set_index("Capa")["Asiento Aportado [mm]"])

        st.success("✅ Cálculo completado correctamente.")
        st.markdown("---")

        # --- Métricas debajo, en columnas simétricas ---
        z_i   = st.session_state.z_i
        zi_enc = st.session_state.zi_encontrado

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(
                label="🏗️ Asiento Total Estimado",
                value=f"{round(st.session_state.asiento_total * 1000, 2)} mm"
            )
        with col_m2:
            if zi_enc:
                st.metric(label="📐 Profundidad de Influencia z_i", value=f"{z_i:.2f} m")
                st.caption("Criterio EC7: Δσz ≤ 0.20·σ'v0")
            else:
                st.metric(label="📐 Profundidad de Influencia z_i", value=f"> {z_i:.2f} m")
                st.warning("⚠️ La zona de influencia supera el espesor de terreno definido. Añade más capas.")
    else:
        st.info("👈 Modifica los datos y haz clic en **Calcular Asiento Total** en el panel izquierdo.")

# --- VISTA 2: DESGLOSE DE ASIENTOS ---
elif modo_vista == "🔍 Desglose de Asientos":
    st.header("📋 Cálculos Intermedios y Factores Geométricos")

    if not st.session_state.calculo_realizado:
        st.warning("⚠️ Los datos han cambiado o no se ha calculado aún. Pulsa el botón de calcular en el panel izquierdo.")
    else:
        st.write("Valores evaluados en el techo y la base de cada estrato.")
        st.dataframe(st.session_state.df_detallado, use_container_width=True)
        st.info(f"**Factor de esbeltez global:** n = {L/B:.4f}")

# --- VISTA 3: INCREMENTO DE TENSIONES ---
elif modo_vista == "📉 Incremento de Tensiones":
    st.header("Disipación de Tensiones en Profundidad (Solución de Holl)")
    st.write("Evolución de tensiones bajo el **centro** de la zapata y comparación con el criterio EC7 de zona de influencia.")

    espesor_total = float(pd.to_numeric(st.session_state.df_terreno["Espesor (m)"]).sum())
    espesor_total = max(1.0, espesor_total)

    col1, col2 = st.columns([1, 3])
    with col1:
        val_inicial = min(15.0, espesor_total)
        z_max = st.slider("Profundidad máxima a graficar [m]:", min_value=1.0, max_value=espesor_total, value=val_inicial, step=0.5)

        st.markdown(f"**$p$ (Carga):** {p} kPa  \n**$B$ (Ancho):** {B} m  \n**$L$ (Largo):** {L} m")
        if Nf < 100.0:
            st.markdown(f"**💧 Nivel freático:** {Nf:.1f} m")
        st.markdown("---")
        st.info(f"**Profundidad del estudio:** {espesor_total:.1f} m")
        st.success(f"**Criterio 10% carga:**\n0.1p = {p*0.1:.1f} kPa")

        # Calcular z_i para mostrar en panel
        z_i_plot, zi_enc_plot = calcular_zona_influencia(p, B, L, st.session_state.df_terreno, Nf)
        if zi_enc_plot:
            st.metric("📐 z_i (EC7, 20%·σ'v0)", f"{z_i_plot:.2f} m")
        else:
            st.metric("📐 z_i (EC7, 20%·σ'v0)", f"> {z_i_plot:.2f} m")
            st.warning("⚠️ z_i supera la estratigrafía definida.")

    with col2:
        z_vals = np.linspace(0.05, z_max, 200)
        sigma_z_vals, sigma_x_vals, sigma_y_vals = [], [], []
        sigma_v0_vals, umbral_20_vals = [], []

        for z in z_vals:
            sz, sx, sy = tensiones_holl_centro(p, B, L, z)
            sigma_z_vals.append(sz)
            sigma_x_vals.append(sx)
            sigma_y_vals.append(sy)
            s_v0 = calcular_sigma_v0(st.session_state.df_terreno, z, Nf)
            sigma_v0_vals.append(s_v0)
            umbral_20_vals.append(0.20 * s_v0)

        fig, ax = plt.subplots(figsize=(9, 7))

        # Tensiones de Holl
        ax.plot(sigma_z_vals, z_vals, label=r'Vertical ($\Delta\sigma_z$)', color='red',   linewidth=2)
        ax.plot(sigma_x_vals, z_vals, label=r'Horiz. Transversal ($\Delta\sigma_x$)', color='blue',  linestyle='--')
        ax.plot(sigma_y_vals, z_vals, label=r'Horiz. Longitudinal ($\Delta\sigma_y$)', color='green', linestyle='-.')

        # Tensión efectiva vertical y umbral EC7
        ax.plot(sigma_v0_vals,   z_vals, label=r"$\sigma'_{v0}$ (tensión efectiva natural)", color='saddlebrown', linestyle=':', linewidth=1.5)
        ax.plot(umbral_20_vals,  z_vals, label=r"$0.20 \cdot \sigma'_{v0}$ (criterio EC7)", color='orange',      linestyle='-',  linewidth=2)

        # Línea clásica 10% p
        ax.axvline(x=p*0.1, color='gray', linestyle=':', label=f'10% carga (0.1p = {p*0.1:.0f} kPa)')

        # Marcar z_i
        if z_i_plot is not None and z_i_plot <= z_max:
            ax.axhline(y=z_i_plot, color='orange', linestyle='--', linewidth=1.5,
                       label=f'z_i EC7 = {z_i_plot:.2f} m')
            ax.annotate(f' z_i = {z_i_plot:.2f} m',
                        xy=(0, z_i_plot), xytext=(p*0.05, z_i_plot - z_max*0.03),
                        color='darkorange', fontsize=10, fontweight='bold')

        # Marcar línea del freático
        if Nf < z_max and Nf < 100.0:
            ax.axhline(y=Nf, color='deepskyblue', linestyle='-.', linewidth=1.5,
                       label=f'Nivel freático Nf = {Nf:.1f} m')

        ax.set_ylim(z_max, 0)
        ax.set_xlim(left=0)
        ax.set_xlabel("Tensión (kPa)", fontsize=11)
        ax.set_ylabel("Profundidad z (m)", fontsize=11)
        ax.set_title("Bulbo de presiones y zona de influencia EC7", fontsize=13)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(loc='lower right', fontsize=9)
        st.pyplot(fig)

# --- VISTA 4: TEORÍA ---
elif modo_vista == "📖 Fundamento Teórico":
    st.header("Metodología de Cálculo")

    st.subheader("1. Cálculo de Asientos (Steinbrenner)")
    st.markdown("Basado en el Apartado 5.2.8.3 de la Guía EC7. El asiento a profundidad $z$ en medio semi-infinito es:")
    st.latex(r"s(z) = \frac{p \cdot B}{E} \left[ (1 - \nu^2) \phi_1 - (1 - \nu - 2\nu^2) \phi_2 \right]")
    st.markdown("Donde $\\phi_1$ y $\\phi_2$ dependen de $n = L/B$ y $m = 2z/B$:")
    st.latex(r"\phi_1 = \frac{1}{\pi} \left[ \ln \left( \frac{\sqrt{1+m^2+n^2}+n}{\sqrt{1+m^2}} \right) + n \ln \left( \frac{\sqrt{1+m^2+n^2}+1}{\sqrt{n^2+m^2}} \right) \right]")
    st.latex(r"\phi_2 = \frac{m}{\pi} \arctan \left( \frac{n}{m \sqrt{1+m^2+n^2}} \right)")
    st.markdown("Para estratos múltiples, se aplica superposición:")
    st.latex(r"\Delta s_i = s(z_i) - s(z_{i+1}) \quad \rightarrow \quad s_{total} = \sum \Delta s_i")

    st.subheader("2. Distribución de Tensiones (Holl)")
    st.markdown("Incrementos de tensión bajo la **esquina** de un rectángulo $B \\times L$ a profundidad $z$, evaluado en $B/2 \\times L/2$ y multiplicado por 4 (centro de la zapata).")
    st.latex(r"\sigma_z = \frac{p}{2\pi} \left[ \arctan\left(\frac{BL}{zR_3}\right) + \frac{BLz}{R_3} \left(\frac{1}{R_1^2} + \frac{1}{R_2^2}\right) \right]")
    st.latex(r"\sigma_x = \frac{p}{2\pi} \left[ \arctan\left(\frac{BL}{zR_3}\right) - \frac{BLz}{R_1^2 R_3} \right]")
    st.latex(r"\sigma_y = \frac{p}{2\pi} \left[ \arctan\left(\frac{BL}{zR_3}\right) - \frac{BLz}{R_2^2 R_3} \right]")
    st.markdown("Siendo $R_1 = \\sqrt{L^2+z^2}$, $R_2 = \\sqrt{B^2+z^2}$ y $R_3 = \\sqrt{L^2+B^2+z^2}$.")

    st.subheader("3. Profundidad de Influencia (Criterio EC7)")
    st.markdown(r"""
La profundidad de influencia $z_i$ es aquella a partir de la cual el incremento de tensión
generado por la cimentación es despreciable frente al estado tensional natural del terreno.
El **criterio del EC7** establece:
""")
    st.latex(r"\Delta\sigma_z(z_i) \leq 0.20 \cdot \sigma'_{v0}(z_i)")
    st.markdown(r"""
Donde $\sigma'_{v0}$ es la **tensión efectiva vertical geoestática**, calculada integrando el peso
específico efectivo de cada capa:
""")
    st.latex(r"\sigma'_{v0}(z) = \sum_{i} \gamma'_i \cdot \Delta z_i")
    st.markdown(r"""
Con:
- $\gamma'_i = \gamma_i$ (peso aparente) para suelo **por encima** del nivel freático  
- $\gamma'_i = \gamma_{sat,i} - \gamma_w$ (peso sumergido) para suelo **por debajo** del nivel freático  
- $\gamma_w = 9.81$ kN/m³ (peso específico del agua)

> **Nota:** Este criterio es más riguroso que el simplificado $\Delta\sigma_z \leq 0.1 \cdot p$,
> ya que tiene en cuenta el estado tensional real del suelo a cada profundidad.
""")
