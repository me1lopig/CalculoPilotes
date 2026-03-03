import streamlit as st
import math
import pandas as pd
import numpy as np
import matplotlib.cm as mcm
import matplotlib.colors as mcolors

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Cálculo Carga Admisible DB-SE-C", layout="wide")

st.title("Cálculo de Carga Admisible en Cimentaciones Superficiales")
st.markdown("**Según el Método Analítico del Código Técnico de la Edificación (DB-SE-C)**")


# ==============================================================================
# --- BARRA LATERAL: ENTRADA DE DATOS ---
# ==============================================================================

st.sidebar.header("1. Geometría de la Zapata")
B = st.sidebar.number_input("Ancho de la zapata, B (m)", min_value=0.1, value=2.0, step=0.1)
L = st.sidebar.number_input("Largo de la zapata, L (m)", min_value=0.1, value=3.0, step=0.1)
D = st.sidebar.number_input("Profundidad de apoyo, D (m)", min_value=0.0, value=1.5, step=0.1)

st.sidebar.header("2. Cargas y Excentricidades")
considerar_cargas = st.sidebar.checkbox("Considerar cargas horizontales y excentricidades", value=False,
                                        help="Desmarca para un cálculo de capacidad portante bruta (carga centrada y puramente vertical).")

if considerar_cargas:
    V = st.sidebar.number_input("Carga Vertical, V (kN)", min_value=1.0, value=1000.0, step=10.0)
    H = st.sidebar.number_input("Carga Horizontal, H (kN)", min_value=0.0, value=50.0, step=10.0)
    e_B = st.sidebar.number_input("Excentricidad en B, e_B (m)", min_value=0.0, value=0.1, step=0.05)
    e_L = st.sidebar.number_input("Excentricidad en L, e_L (m)", min_value=0.0, value=0.1, step=0.05)
else:
    V = 1000.0
    H = 0.0
    e_B = 0.0
    e_L = 0.0

st.sidebar.header("3. Parámetros del Terreno")
phi = st.sidebar.number_input("Ángulo de rozamiento, φ (°)", min_value=0.0, max_value=45.0, value=30.0)
c_k = st.sidebar.number_input("Cohesión característica, ck (kPa)", min_value=0.0, value=10.0)

st.sidebar.subheader("Densidades del Suelo")
gamma_w = 9.81

st.sidebar.markdown("*Terreno POR ENCIMA de la cota de apoyo:*")
gamma_sup_ap  = st.sidebar.number_input("Peso esp. aparente, γ_sup (kN/m³)",     min_value=10.0, value=18.0)
gamma_sup_sat = st.sidebar.number_input("Peso esp. saturado, γ_sat_sup (kN/m³)", min_value=10.0, value=20.0)

st.sidebar.markdown("*Terreno POR DEBAJO de la cota de apoyo:*")
gamma_inf_ap  = st.sidebar.number_input("Peso esp. aparente, γ_inf (kN/m³)",     min_value=10.0, value=19.0)
gamma_inf_sat = st.sidebar.number_input("Peso esp. saturado, γ_sat_inf (kN/m³)", min_value=10.0, value=21.0)

st.sidebar.header("4. Nivel Freático y Talud")
D_w  = st.sidebar.number_input("Profundidad del Nivel Freático desde la SUPERFICIE, Dw (m)", min_value=0.0, value=5.0, step=0.5)
beta = st.sidebar.number_input("Inclinación de talud próximo, β (°)", min_value=0.0, max_value=45.0, value=0.0)

# --- SECCIÓN TABLA PARAMÉTRICA ---
st.sidebar.header("5. Tabla Paramétrica B × L")
with st.sidebar.expander("Configurar rango de B y L", expanded=True):
    B_min  = st.sidebar.number_input("B mínimo (m)",       min_value=0.1, value=1.0,  step=0.1, key="Bmin")
    B_max  = st.sidebar.number_input("B máximo (m)",       min_value=0.2, value=4.0,  step=0.1, key="Bmax")
    B_step = st.sidebar.number_input("Incremento ΔB (m)",  min_value=0.1, value=0.5,  step=0.1, key="Bstep")
    L_min  = st.sidebar.number_input("L mínimo (m)",       min_value=0.1, value=1.0,  step=0.1, key="Lmin")
    L_max  = st.sidebar.number_input("L máximo (m)",       min_value=0.2, value=5.0,  step=0.1, key="Lmax")
    L_step = st.sidebar.number_input("Incremento ΔL (m)",  min_value=0.1, value=0.5,  step=0.1, key="Lstep")

resultado_tabla = st.sidebar.radio(
    "Valor a mostrar en la tabla",
    ["q_adm (kPa)", "q_h (kPa)"],
    horizontal=True
)


# ==============================================================================
# --- FUNCIÓN DE CÁLCULO PRINCIPAL ---
# ==============================================================================

def calcular(B_val, L_val,
             D, phi, c_k,
             gamma_w, gamma_sup_ap, gamma_sup_sat,
             gamma_inf_ap, gamma_inf_sat,
             D_w, beta,
             V, H, e_B, e_L,
             considerar_cargas):
    """
    Calcula la presión de hundimiento (q_h) y carga admisible (q_adm)
    para una zapata de dimensiones B_val × L_val según CTE DB-SE-C.
    Devuelve un diccionario con todos los resultados intermedios.
    """
    FS = 3.0

    # 1. Dimensiones equivalentes
    B_star = B_val - 2 * e_B
    L_star = L_val - 2 * e_L

    # B* siempre es la dimensión menor
    if B_star > L_star:
        B_star, L_star = L_star, B_star

    if B_star <= 0 or L_star <= 0:
        return None  # Excentricidad excesiva → vuelco

    # 2. Pesos sumergidos
    gamma_sup_sub = gamma_sup_sat - gamma_w
    gamma_inf_sub = gamma_inf_sat - gamma_w

    # 3. Presión efectiva de sobrecarga (q_0k)
    if D_w >= D:
        q_0k = gamma_sup_ap * D
    else:
        q_0k = (gamma_sup_ap * D_w) + (gamma_sup_sub * (D - D_w))

    # 4. Peso específico efectivo de la cuña de rotura (gamma_k)
    z = D_w - D
    if z <= 0:
        gamma_k = gamma_inf_sub
    elif z >= B_star:
        gamma_k = gamma_inf_ap
    else:
        gamma_k = gamma_inf_sub + (gamma_inf_ap - gamma_inf_sub) * (z / B_star)

    # 5. Factores de capacidad de carga
    phi_rad = math.radians(phi)
    if phi == 0:
        Nq = 1.0
        Nc = 5.14
        Ny = 0.0
    else:
        Nq = math.exp(math.pi * math.tan(phi_rad)) * (math.tan(math.radians(45 + phi / 2))) ** 2
        Nc = (Nq - 1) / math.tan(phi_rad)
        Ny = 1.5 * (Nq - 1) * math.tan(phi_rad)

    # 6. Factores de forma
    sc = 1 + 0.2 * (B_star / L_star)
    sq = 1 + 1.5 * math.tan(phi_rad) * (B_star / L_star) if phi > 0 else 1.0
    sy = 1 - 0.3 * (B_star / L_star)

    # 7. Factores de profundidad
    if D >= 2.0:
        D_calc = min(D, 2 * B_star)
        dc = 1 + 0.34 * math.atan(D_calc / B_star)
        dq = 1 + 2 * math.tan(phi_rad) * (1 - math.sin(phi_rad)) ** 2 * math.atan(D_calc / B_star) if phi != 0 else 1.0
        dy = 1.0
    else:
        dc = dq = dy = 1.0

    # 8. Factores de inclinación de carga
    if H / V < 0.1 or not considerar_cargas:
        ic = iq = iy = 1.0
    else:
        delta_rad = math.atan(H / V)
        iq = (1 - 0.7 * math.tan(delta_rad)) ** 3
        iy = (1 - math.tan(delta_rad)) ** 3
        if phi == 0:
            ic = 0.5 * (1 + math.sqrt(1 - min(1.0, H / (B_star * L_star * c_k)))) if c_k > 0 else 1.0
        else:
            ic = (iq * Nq - 1) / (Nq - 1)

    # 9. Factores de talud
    beta_rad = math.radians(beta)
    if beta <= 5:
        tc = tq = ty = 1.0
    else:
        tq = (1 - math.sin(2 * beta_rad))
        ty = (1 - math.sin(2 * beta_rad))
        tc = math.exp(-2 * beta_rad * math.tan(phi_rad)) if phi > 0 else 1.0

    # 10. Cálculo de la presión de hundimiento
    term_c = c_k * Nc * dc * sc * ic * tc
    term_q = q_0k * Nq * dq * sq * iq * tq
    term_y = 0.5 * B_star * gamma_k * Ny * dy * sy * iy * ty

    q_h   = term_c + term_q + term_y
    q_adm = q_h / FS

    return {
        "B_star": B_star, "L_star": L_star,
        "q_0k": q_0k, "gamma_k": gamma_k,
        "Nc": Nc, "Nq": Nq, "Ny": Ny,
        "sc": sc, "sq": sq, "sy": sy,
        "dc": dc, "dq": dq, "dy": dy,
        "ic": ic, "iq": iq, "iy": iy,
        "tc": tc, "tq": tq, "ty": ty,
        "term_c": term_c, "term_q": term_q, "term_y": term_y,
        "q_h": q_h, "q_adm": q_adm, "FS": FS,
    }


# Argumentos comunes del terreno que se pasan a la función
kwargs_terreno = dict(
    D=D, phi=phi, c_k=c_k,
    gamma_w=gamma_w,
    gamma_sup_ap=gamma_sup_ap, gamma_sup_sat=gamma_sup_sat,
    gamma_inf_ap=gamma_inf_ap, gamma_inf_sat=gamma_inf_sat,
    D_w=D_w, beta=beta,
    V=V, H=H, e_B=e_B, e_L=e_L,
    considerar_cargas=considerar_cargas,
)


# ==============================================================================
# --- CÁLCULO PUNTUAL (B, L del sidebar) ---
# ==============================================================================

res = calcular(B, L, **kwargs_terreno)

if res is None:
    st.error("❌ Las excentricidades son demasiado grandes. La zapata equivalente es nula o negativa. El vuelco es inminente.")
    st.stop()

st.header("① Resultado Puntual")
st.caption(f"Para la zapata B = {B} m × L = {L} m introducida en el sidebar")

col1, col2, col3 = st.columns(3)
col1.metric("Zapata Equivalente (B* × L*)", f"{res['B_star']:.2f} × {res['L_star']:.2f} m")
col2.metric("Peso Esp. Cuña Rotura (γ_k)", f"{res['gamma_k']:.2f} kN/m³")
col3.metric("Sobrecarga Efectiva (q_0k)", f"{res['q_0k']:.2f} kPa")

st.subheader("Desglose de la Fórmula Trinomia")
desglose_data = {
    "Término":                   ["Cohesión (c)", "Sobrecarga (q)", "Peso Específico (γ)"],
    "Factores N":                [f"{res['Nc']:.2f}", f"{res['Nq']:.2f}", f"{res['Ny']:.2f}"],
    "Fact. Forma (s)":           [f"{res['sc']:.2f}", f"{res['sq']:.2f}", f"{res['sy']:.2f}"],
    "Fact. Prof. (d)":           [f"{res['dc']:.2f}", f"{res['dq']:.2f}", f"{res['dy']:.2f}"],
    "Fact. Inclin. (i)":         [f"{res['ic']:.2f}", f"{res['iq']:.2f}", f"{res['iy']:.2f}"],
    "Fact. Talud (t)":           [f"{res['tc']:.2f}", f"{res['tq']:.2f}", f"{res['ty']:.2f}"],
    "Subtotal por Término (kPa)":[f"{res['term_c']:.2f}", f"{res['term_q']:.2f}", f"{res['term_y']:.2f}"],
}
st.table(desglose_data)

st.success(f"### Presión de Hundimiento ($q_h$): {res['q_h']:.2f} kPa")
st.info(f"### Carga Admisible de Cálculo ($q_{{adm}}$): {res['q_adm']:.2f} kPa  *(FS = {res['FS']})*")


# --- ALERTAS NORMATIVAS ---
st.subheader("⚠️ Avisos Normativos y Verificaciones DB-SE-C")

if not considerar_cargas:
    st.info("ℹ️ Cálculo realizado suponiendo **carga perfectamente centrada y vertical**.")
else:
    if H / V < 0.1:
        st.success("✅ La componente horizontal es menor al 10% de la vertical. Se ignora el efecto de inclinación (i = 1).")
    else:
        st.warning("⚠️ La componente horizontal penaliza la capacidad portante (factores 'i' < 1). Verifica el EL de **Deslizamiento**.")

if D < 2.0:
    st.warning("⚠️ Factores de profundidad (d) = 1.0 porque D < 2.0 m.")

if D_w <= D:
    st.error(f"💧 **NF crítico:** El agua está por encima de la base (Dw = {D_w} m). Se usan presiones efectivas y peso sumergido.")
elif D_w < (D + res['B_star']):
    st.warning(f"💧 **NF intermedio:** El agua corta la cuña de rotura. Se ha interpolado γ_k.")
else:
    st.success(f"✅ NF profundo (Dw = {D_w} m). No afecta la capacidad portante.")

if beta > (phi / 2):
    st.error("🛑 **Talud excesivo:** β > φ/2. El CTE exige análisis global de estabilidad.")


# ==============================================================================
# --- TABLA PARAMÉTRICA B × L ---
# ==============================================================================

st.header("② Tabla Paramétrica de Carga Admisible")

# Validar rangos
if B_max <= B_min:
    st.warning("⚠️ En la sección 5 del sidebar: B máximo debe ser mayor que B mínimo.")
elif L_max <= L_min:
    st.warning("⚠️ En la sección 5 del sidebar: L máximo debe ser mayor que L mínimo.")
else:
    # Generar vectores de B y L
    B_vals = np.arange(B_min, B_max + B_step * 0.01, B_step)
    L_vals = np.arange(L_min, L_max + L_step * 0.01, L_step)

    # Limitar a 15 valores por eje para evitar tablas enormes
    MAX_VALS = 15
    if len(B_vals) > MAX_VALS:
        st.warning(f"⚠️ Se han reducido los valores de B a {MAX_VALS} (demasiados pasos). Aumenta ΔB.")
        B_vals = B_vals[:MAX_VALS]
    if len(L_vals) > MAX_VALS:
        st.warning(f"⚠️ Se han reducido los valores de L a {MAX_VALS} (demasiados pasos). Aumenta ΔL.")
        L_vals = L_vals[:MAX_VALS]

    campo = "q_adm" if resultado_tabla == "q_adm (kPa)" else "q_h"

    # Construir la tabla: filas = B, columnas = L
    tabla = {}
    for L_v in L_vals:
        col_key = f"L={L_v:.2f}m"
        col_data = []
        for B_v in B_vals:
            if B_v > L_v:
                # Solo se calculan casos con B ≤ L (normativa)
                col_data.append(float("nan"))
            else:
                r = calcular(B_v, L_v, **kwargs_terreno)
                if r is None:
                    col_data.append(float("nan"))
                else:
                    col_data.append(round(r[campo], 2))
        tabla[col_key] = col_data

    index_labels = [f"B={b:.2f}m" for b in B_vals]
    df = pd.DataFrame(tabla, index=index_labels, dtype=float)
    df.index.name = "B \\ L"

    unidad = "kPa"
    titulo_campo = "Carga Admisible $q_{adm}$" if campo == "q_adm" else "Presión de Hundimiento $q_h$"

    st.markdown(f"**{titulo_campo}** ({unidad}) — D = {D} m | φ = {phi}° | ck = {c_k} kPa")
    st.caption("Filas = Ancho B (m) | Columnas = Largo L (m)")

    # Coloreado manual: se calcula el color YlGn para cada celda con dato
    # y se deja blanco donde no hay cálculo (B > L). Esto evita el problema
    # de que background_gradient + Streamlit (renderer Arrow) pinta NaN en negro.
    cmap      = mcm.get_cmap("YlGn")
    vmin_val  = float(np.nanmin(df.values))
    vmax_val  = float(np.nanmax(df.values))

    def color_celda(val):
        if pd.isna(val):
            return "background-color: white;"
        norma = (val - vmin_val) / (vmax_val - vmin_val) if vmax_val != vmin_val else 0.5
        r, g, b, _ = cmap(norma)
        return f"background-color: rgb({int(r*255)},{int(g*255)},{int(b*255)});"

    st.dataframe(
        df.style
          .format("{:.2f}", na_rep="")
          .applymap(color_celda),
        use_container_width=True,
    )

    # Botón de descarga CSV
    csv = df.to_csv(float_format="%.2f")
    st.download_button(
        label="⬇️ Descargar tabla como CSV",
        data=csv,
        file_name=f"tabla_{campo}_D{D}_phi{phi}.csv",
        mime="text/csv",
    )