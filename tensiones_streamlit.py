import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import xlsxwriter
import zipfile

# ==========================================
# 0. CONFIGURACIÓN Y ESTADO
# ==========================================
st.set_page_config(page_title="Tensiones Verticales", layout="wide", page_icon="🌍")

# Inicializar estado para el botón de descarga
if 'archivo_listo' not in st.session_state:
    st.session_state.archivo_listo = False
if 'buffer_zip' not in st.session_state:
    st.session_state.buffer_zip = None

# Función para resetear la descarga al cambiar datos
def resetear_descarga():
    st.session_state.archivo_listo = False
    st.session_state.buffer_zip = None

# ==========================================
# 1. MOTOR DE CÁLCULO
# ==========================================

def obtener_maximo_menor(lista, valor):
    filtro = [x for x in lista if x <= valor]
    if not filtro: return 0
    return max(filtro)

def parametro_terreno(cotas, zt):
    if zt <= 0: return 1
    indice = 0
    for z in range(len(cotas)-1):
        cota_sup = cotas[z]
        cota_inf = cotas[z+1]
        if zt > cota_sup and zt <= cota_inf:
            indice = z + 1
            break
    if indice == 0 and zt > cotas[-1]:
        indice = len(cotas) - 1
    return indice

def presion_total(cotas, valor_nf, pe_saturado, pe_aparente, valor_cota):
    lista_cotas = sorted(list(set(cotas + [valor_nf]))) 
    resultado = obtener_maximo_menor(lista_cotas, valor_cota)
    idx_terreno = parametro_terreno(cotas, valor_cota)
    if idx_terreno >= len(pe_saturado): idx_terreno = len(pe_saturado) - 1
    p_sat_val = pe_saturado[idx_terreno]
    p_aparente_val = pe_aparente[idx_terreno]
    peso = p_aparente_val if valor_cota <= valor_nf else p_sat_val
    presion_acumulada = (valor_cota - resultado) * peso
    try: idx_resultado = lista_cotas.index(resultado)
    except ValueError: idx_resultado = 0
    for j in range(idx_resultado, 0, -1):
        cota_actual = lista_cotas[j]
        cota_anterior = lista_cotas[j-1]
        espesor = cota_actual - cota_anterior
        cota_media = (cota_actual + cota_anterior) / 2
        idx_t = parametro_terreno(cotas, cota_media)
        if idx_t >= len(pe_saturado): idx_t = len(pe_saturado) - 1
        p_sat_capa = pe_saturado[idx_t]
        p_aparente_capa = pe_aparente[idx_t]
        if cota_actual <= valor_nf: peso_tramo = p_aparente_capa
        else: peso_tramo = p_sat_capa
        presion_acumulada += espesor * peso_tramo
    return presion_acumulada

def calcular_perfil_tensiones(df_input, nivel_freatico, usar_nf_logic):
    espesores = [0] + df_input['Espesor (m)'].tolist()
    pe_aparente = [0] + df_input['Peso aparente (kN/m³)'].tolist()
    pe_saturado = [0] + df_input['Peso Sat. (kN/m³)'].tolist()
    cotas = []
    acumulado = 0
    for esp in espesores:
        acumulado += esp
        cotas.append(acumulado)
    max_z = max(cotas)
    if max_z == 0: return pd.DataFrame()
    paso = 0.1
    profundidades = np.arange(0, max_z + paso, paso)
    resultados = []
    
    # Si no usamos NF, forzamos que esté muy profundo
    nf_calculo = nivel_freatico if usar_nf_logic else 99999.9

    for z in profundidades:
        sigma_v = presion_total(cotas, nf_calculo, pe_saturado, pe_aparente, z)
        if z >= nf_calculo: u = (z - nf_calculo) * 9.81
        else: u = 0
        sigma_eff = sigma_v - u
        resultados.append({
            "Profundidad (m)": round(z, 2),
            "Presión de Poro (kPa)": round(u, 2),
            "Presión Efectiva (kPa)": round(sigma_eff, 2),
            "Presión Total (kPa)": round(sigma_v, 2)
        })
    return pd.DataFrame(resultados)

# ==========================================
# 2. INTERFAZ DE USUARIO
# ==========================================

st.title("🌍 Calculadora de Tensiones Verticales")

# --- ENTRADA DE DATOS (Primero, para calcular límites) ---
col1, col2 = st.columns([3, 1])

datos_iniciales = pd.DataFrame([
    {"Espesor (m)": 5.0, "Peso aparente (kN/m³)": 18.0, "Peso Sat. (kN/m³)": 20.0},
    {"Espesor (m)": 10.0, "Peso aparente (kN/m³)": 19.0, "Peso Sat. (kN/m³)": 21.0},
])

with col1:
    st.subheader("1. Niveles")
    df_estratos = st.data_editor(
        datos_iniciales,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Espesor (m)": st.column_config.NumberColumn("Espesor", min_value=0.1, format="%.2f"),
            "Peso aparente (kN/m³)": st.column_config.NumberColumn("γ aparente", min_value=1.0, format="%.1f"),
            "Peso Sat. (kN/m³)": st.column_config.NumberColumn("γ sat", min_value=1.0, format="%.1f"),
        },
        key="editor_datos" 
    )

# Detectar cambios en la tabla para resetear descarga
if 'data_anterior' not in st.session_state:
    st.session_state.data_anterior = df_estratos.to_json()

if df_estratos.to_json() != st.session_state.data_anterior:
    st.session_state.data_anterior = df_estratos.to_json()
    resetear_descarga()

# Calcular Profundidad Total
prof_total = 0.0
if not df_estratos.empty:
    prof_total = df_estratos["Espesor (m)"].sum()

with col2:
    st.markdown("##### Resumen")
    st.metric("Profundidad Total", f"{prof_total:.2f} m")

# --- SIDEBAR (Ahora que tenemos prof_total, configuramos el NF) ---
with st.sidebar:
    st.header("💧 Posición del nivel freático")
    
    usar_nf = st.checkbox("Considerar Nivel Freático", value=True, on_change=resetear_descarga)
    
    if usar_nf:
        # Lógica de Validación Dinámica
        max_limit = prof_total if prof_total > 0 else 100.0
        
        # Recuperar valor anterior o usar defecto
        val_actual = st.session_state.get('nf_input', 3.5)
        
        # CLAMPING: Si el valor actual supera el nuevo límite (ej. borraste capas), se ajusta
        if val_actual > max_limit:
            val_actual = max_limit
            st.warning(f"⚠️ Nivel freático ajustado a {max_limit}m (límite del terreno).")

        nf_input = st.number_input(
            "Profundidad Nivel Freático (m)", 
            min_value=0.0, 
            max_value=max_limit,  # Aquí aplicamos la restricción física
            value=val_actual,
            step=0.1,
            on_change=resetear_descarga,
            key='nf_input' ,# Vincula este input al session_state
        )
    else:
        nf_input = 0.0
        st.info("Cálculo sin presión de poros (Suelo aparente/Húmedo).")


# --- CÁLCULO Y VISUALIZACIÓN ---
if not df_estratos.empty:
    
    df_resultados = calcular_perfil_tensiones(df_estratos, nf_input, usar_nf)
    
    st.divider()
    
    # GRÁFICA Y TABLA
    tab_graf, tab_data = st.tabs(["📈 Gráfica", "📋 Tabla"])
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(df_resultados["Presión Efectiva (kPa)"], df_resultados["Profundidad (m)"], 'darkred', label='Tensión Efectiva')
    ax.plot(df_resultados["Presión Total (kPa)"], df_resultados["Profundidad (m)"], 'blue', linestyle='--', label='Tensión Total')
    ax.plot(df_resultados["Presión de Poro (kPa)"], df_resultados["Profundidad (m)"], 'green', linestyle=':', label='Presión de Poro')
    
    if usar_nf and nf_input <= prof_total:
        ax.axhline(y=nf_input, color='cyan', linestyle='-.', label=f'N.F. ({nf_input:2f}m)')


    ax.invert_yaxis()
    ax.set_xlabel('Tensión [kPa]'); ax.set_ylabel('Profundidad [m]')
    ax.legend(); ax.grid(True, linestyle='--', alpha=0.6)

    with tab_graf:
        col_g1, col_g2 = st.columns([1, 4])
        with col_g2: st.pyplot(fig)
        
    with tab_data:
        st.dataframe(df_resultados, use_container_width=True, height=300)

    # --- SECCIÓN DE DESCARGA CONTROLADA ---
    st.divider()
    st.subheader("📥 Exportar Resultados")
    
    col_gen, col_down = st.columns([1, 1])
    
    with col_gen:
        # El botón de generar crea los archivos en memoria
        if st.button("🔄 Generar Archivos de Descarga", type="primary"):
            
            # Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df_resultados.to_excel(writer, index=False, sheet_name='Resultados')
                writer.sheets['Resultados'].set_column('A:D', 18)
            
            # Imagen
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            
            # ZIP
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("Resultados_Calculo.xlsx", excel_buffer.getvalue())
                zf.writestr("Grafica_Tensiones.png", img_buffer.getvalue())
            
            # Actualizar estado
            st.session_state.buffer_zip = zip_buffer.getvalue()
            st.session_state.archivo_listo = True
            st.rerun() 

    with col_down:
        if st.session_state.archivo_listo:
            st.success("✅ Archivos listos.")
            st.download_button(
                label="📦 Descargar ZIP",
                data=st.session_state.buffer_zip,
                file_name="Calculo_Tensiones.zip",
                mime="application/zip",
                type="aparentendary"
            )
        else:
            st.info("👆 Pulsa 'Generar' para preparar la descarga.")

else:
    st.warning("Introduce datos en la tabla para comenzar.")