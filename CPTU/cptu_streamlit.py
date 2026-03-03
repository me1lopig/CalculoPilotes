import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN INICIAL DE LA PÁGINA ---
st.set_page_config(page_title="Visor CPTU Profesional", layout="wide")

st.title("📊 Análisis Geotécnico Avanzado de Ensayo CPTU")
st.markdown("Visualización de datos, extracción de parámetros y deducción automática de estratigrafía mediante el método de **Robertson (1990/2010)**.")
st.divider()

# --- FUNCIONES GEOTÉCNICAS ---
@st.cache_data 
def calcular_ic_y_sbt(df):
    pa = 0.1  # Presión atmosférica aproximada en MPa
    df_calc = df[(df['Qc'] > 0.01) & (df['Rf'] > 0.01)].copy()
    df_calc['Qc_pa'] = df_calc['Qc'] / pa
    df_calc['Ic'] = np.sqrt((3.47 - np.log10(df_calc['Qc_pa']))**2 + (np.log10(df_calc['Rf']) + 1.22)**2)
    
    condiciones = [
        (df_calc['Ic'] < 1.31),
        (df_calc['Ic'] >= 1.31) & (df_calc['Ic'] < 2.05),
        (df_calc['Ic'] >= 2.05) & (df_calc['Ic'] < 2.60),
        (df_calc['Ic'] >= 2.60) & (df_calc['Ic'] < 2.95),
        (df_calc['Ic'] >= 2.95) & (df_calc['Ic'] < 3.60),
        (df_calc['Ic'] >= 3.60)
    ]
    
    zonas_sbt = [
        '7. Grava arenosa a arena',           
        '6. Arena a arena limosa',            
        '5. Arena limosa a limo arenoso',     
        '4. Limo arcilloso a arcilla limosa', 
        '3. Arcilla a arcilla limosa',        
        '2. Suelos orgánicos y turbas'        
    ]
    zonas_num = [7, 6, 5, 4, 3, 2]
    
    df_calc['SBT_Name'] = np.select(condiciones, zonas_sbt, default='Desconocido')
    df_calc['SBT_Zone'] = np.select(condiciones, zonas_num, default=0)
    
    return df_calc

SBT_COLORS = {
    7: '#d8b365', 6: '#f5f5dc', 5: '#c7eae5', 
    4: '#80cdc1', 3: '#dfc27d', 2: '#8c510a'
}

# --- INTERFAZ PRINCIPAL DE USUARIO ---
uploaded_file = st.file_uploader("📂 Sube el archivo CPTU (.CSV separado por punto y coma)", type=["csv", "CSV"])

if uploaded_file is not None:
    # --- 1. EXTRACCIÓN DE METADATOS (CABECERA) ---
    content = uploaded_file.read().decode('utf-8').splitlines()
    header_data = {}
    
    for line in content[:20]:
        if ';' in line:
            key, val = line.split(';', 1)
            clean_key = key.strip().rstrip(':')
            clean_val = val.strip().strip(';')
            if clean_key and clean_val:
                header_data[clean_key] = clean_val
                
    with st.expander("📋 Ver Datos de la Campaña (Cabecera)", expanded=True):
        # Convertimos el diccionario a lista de pares
        items = list(header_data.items())
        # Calculamos la mitad para dividir la tabla en dos columnas
        mitad = len(items) // 2 + len(items) % 2
        
        # Creamos dos DataFrames, asignamos el parámetro como índice para que se vea en negrita
        df_left = pd.DataFrame(items[:mitad], columns=["Parámetro", "Valor"]).set_index("Parámetro")
        df_right = pd.DataFrame(items[mitad:], columns=["Parámetro", "Valor"]).set_index("Parámetro")
        
        # Mostramos las tablas en dos columnas paralelas
        col1, col2 = st.columns(2)
        with col1:
            st.table(df_left)
        with col2:
            st.table(df_right)

    # --- 2. LECTURA Y PROCESAMIENTO DE DATOS ---
    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file, sep=';', decimal=',', skiprows=23)
    df['Depth_m'] = df['Depth'] / 100.0 
    df_calc = calcular_ic_y_sbt(df)
    
    # --- 3. GRÁFICA DE PERFIL ESTRATIGRÁFICO ---
    st.header("1. Perfiles del Ensayo frente a la Profundidad")
    st.write("Clasificación del terreno basada en el SBT Index (Ic), mostrando resistencia por punta (Qc), fricción lateral (Fs) y presión de poros (U2).")
    
    fig_strat, axs_strat = plt.subplots(1, 6, figsize=(18, 8), sharey=True, gridspec_kw={'width_ratios': [1, 2, 2, 2, 2, 1.5]})
    
    for zone in df_calc['SBT_Zone'].unique():
        if zone == 0: continue
        mask = df_calc['SBT_Zone'] == zone
        axs_strat[0].fill_betweenx(df_calc['Depth_m'], 0, 1, where=mask, color=SBT_COLORS.get(zone, '#ffffff'), step='mid')
    axs_strat[0].set_xlim(0, 1)
    axs_strat[0].set_xticks([])
    axs_strat[0].set_ylabel('Profundidad (m)', fontsize=12)
    axs_strat[0].invert_yaxis() 
    axs_strat[0].set_title('Estratigrafía', fontsize=10)
    
    axs_strat[1].plot(df_calc['Qc'], df_calc['Depth_m'], color='#1f77b4', linewidth=1)
    axs_strat[1].grid(True, linestyle='--', alpha=0.5)
    axs_strat[1].set_title('Qc (MPa)', fontsize=10)

    axs_strat[2].plot(df_calc['Fs'], df_calc['Depth_m'], color='#ff7f0e', linewidth=1)
    axs_strat[2].grid(True, linestyle='--', alpha=0.5)
    axs_strat[2].set_title('Fs (kPa)', fontsize=10)
    
    axs_strat[3].plot(df_calc['U2'], df_calc['Depth_m'], color='#d62728', linewidth=1)
    axs_strat[3].grid(True, linestyle='--', alpha=0.5)
    axs_strat[3].set_title('U2 (kPa)', fontsize=10)
    
    axs_strat[4].plot(df_calc['Ic'], df_calc['Depth_m'], color='#2ca02c', linewidth=1)
    axs_strat[4].axvline(2.6, color='red', linestyle='--', alpha=0.5, label='Límite Grueso/Fino')
    axs_strat[4].grid(True, linestyle='--', alpha=0.5)
    axs_strat[4].set_title('SBT Index (Ic)', fontsize=10)
    axs_strat[4].legend(loc='lower right', fontsize=8)
    
    axs_strat[5].axis('off') 
    legend_elements = [plt.Rectangle((0,0),1,1, color=SBT_COLORS[k], label=v) 
                       for k, v in zip([7,6,5,4,3,2], 
                       ['7. Grava / Arena', '6. Arena a arena limosa', '5. Arena limosa', 
                        '4. Limo arcilloso', '3. Arcilla limosa', '2. Orgánico / Turba'])]
    axs_strat[5].legend(handles=legend_elements, loc='center', title="Clasificación Robertson", fontsize=9)

    plt.tight_layout()
    st.pyplot(fig_strat)

    # --- 4. TABLA DE RESUMEN DE CAPAS (MEJORADA VISUALMENTE) ---
    st.header("2. Capas Detectadas Automáticamente")
    st.write("Resumen de parámetros medios agrupados por intervalos de 1 metro de profundidad.")
    
    df_calc['Depth_Interval'] = np.floor(df_calc['Depth_m'])
    resumen_capas = df_calc.groupby('Depth_Interval').agg(
        SBT_Predominante=('SBT_Name', lambda x: x.mode()[0] if len(x)>0 else 'N/A'),
        Qc_Medio_MPa=('Qc', 'mean'),
        Fs_Medio_kPa=('Fs', 'mean'),
        U2_Medio_kPa=('U2', 'mean')
    ).reset_index()
    resumen_capas.rename(columns={'Depth_Interval': 'Profundidad (m)'}, inplace=True)
    
    # Configuramos las columnas para hacerlas impactantes (Barras y formatos)
    st.dataframe(
        resumen_capas,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Profundidad (m)": st.column_config.NumberColumn(
                "Profundidad Inicial (m)",
                format="%.1f m",
            ),
            "SBT_Predominante": st.column_config.TextColumn(
                "Clasificación SBT (Robertson)",
            ),
            "Qc_Medio_MPa": st.column_config.NumberColumn(
                "Qc Medio (MPa) 📈",
                help="Resistencia por punta promedio",
                format="%.2f",
            ),
            "Fs_Medio_kPa": st.column_config.NumberColumn(
                "Fs Medio (kPa)",
                format="%.1f",
            ),
            # U2 lo convertimos en una barra de progreso visual dentro de la celda
            "U2_Medio_kPa": st.column_config.ProgressColumn(
                "U2 Medio (kPa) 💧",
                help="Presión intersticial promedio con indicador visual",
                format="%.1f",
                min_value=0,
                max_value=float(resumen_capas["U2_Medio_kPa"].max()) # La barra se ajusta al máximo de cada ensayo
            )
        }
    )