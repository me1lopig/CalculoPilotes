import streamlit as st
import numpy as np
import pandas as pd
import io
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Carga Admisible en Roca - GCOC 2009", layout="centered")

# --- FUNCIÓN PARA RESETEAR INFORME ---
def reset_informe():
    if 'informe_buffer' in st.session_state:
        st.session_state.informe_buffer = None

# Estilos CSS
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .titulo-seccion { background-color: #0d47a1; color: white; padding: 12px; font-weight: bold; border-radius: 4px; text-align: center; margin-bottom: 20px; }
    .titulo-norma { background-color: #0d47a1; color: white; padding: 8px 15px; font-weight: bold; border-radius: 4px 4px 0 0; font-size: 14px; margin-top: 10px; border: 1px solid #0d47a1; }
    .tabla-profesional { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 25px; border: 1px solid #d1d1d1; background-color: white; }
    .tabla-profesional th { background-color: #e3f2fd; color: #333; padding: 10px; border: 1px solid #d1d1d1; font-weight: bold; }
    .tabla-profesional td { padding: 10px; border: 1px solid #d1d1d1; text-align: center; color: #444; }
    .text-left { text-align: left !important; padding-left: 15px !important; }
    .grupo-roca { background-color: #fafafa; font-weight: 500; }
    .requisitos { background-color: #e3f2fd; padding: 15px; border-left: 5px solid #1565c0; border-radius: 4px; font-size: 14px; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛣️ Cálculo de Presión Vertical Admisible en Roca (GCOC 2009)")

# --- FUNCIÓN GENERADORA DE informe WORD ---
def generar_informe_word(inputs, resultados, checks):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    
    # 1. ENCABEZADO
    titulo = doc.add_heading('Informe Técnico: Cimentaciones en Roca', 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p_meta = doc.add_paragraph()
    p_meta.add_run(f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n").bold = True
    p_meta.add_run("Metodología: Guía de Cimentaciones en Obras de Carretera (Cap. 4.5.3)")

    # 2. PARÁMETROS DE ENTRADA
    doc.add_heading('1. Parámetros del Macizo Rocoso', level=1)
    p = doc.add_paragraph()
    p.add_run(f"• Resistencia Compresión Simple (qu): {inputs['qu']} MPa\n")
    p.add_run(f"• RQD: {inputs['rqd']} %\n")
    p.add_run(f"• Espaciamiento discontinuidades (s): {inputs['s']:.2f} m\n")
    p.add_run(f"• Tipo de Roca: {inputs['txt_a1']}\n")
    p.add_run(f"• Grado Meteorización: {inputs['txt_a2']}")

    # 3. VERIFICACIÓN (TABLA)
    doc.add_heading('2. Verificación de las Hipótesis del Modelo', level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light List Accent 1'
    
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Criterio'
    hdr_cells[1].text = 'Estado'
    
    for check_name, status in checks.items():
        row_cells = table.add_row().cells
        row_cells[0].text = check_name
        p_row = row_cells[1].paragraphs[0]
        run = p_row.add_run(status)
        if "NO CUMPLE" in status or "SUELO" in status:
            run.font.color.rgb = RGBColor(200, 0, 0)
            run.bold = True
        else:
            run.font.color.rgb = RGBColor(0, 100, 0)

    doc.add_paragraph()

    # 4. FICHA DE CÁLCULO (RESULTADOS)
    doc.add_heading('3. Datos de Cálculo', level=1)
    
    # Tabla resumen de cálculo
    t_res = doc.add_table(rows=6, cols=3)
    t_res.style = 'Light Shading Accent 1'
    
    # Encabezados
    row0 = t_res.rows[0].cells
    row0[0].text = "Parámetro"
    row0[1].text = "Valor"
    row0[2].text = "Descripción"
    
    # Filas
    data_rows = [
        ("Coef. α1", f"{inputs['a1']}", "Factor por Tipo de Roca"),
        ("Coef. α2", f"{inputs['a2']}", "Factor por Meteorización"),
        ("Coef. α3", f"{resultados['a3']:.3f}", "Factor por Discontinuidades (min(s, RQD/100))"),
        ("Presión Base (p0)", "1.0 MPa", "Presión de referencia"),
        ("PRESIÓN ADMISIBLE", f"{resultados['q_adm']:.2f} MPa", "Valor de diseño")
    ]
    
    for i, (param, val, desc) in enumerate(data_rows):
        cells = t_res.rows[i+1].cells
        cells[0].text = param
        cells[1].text = val
        cells[2].text = desc
        
        # Resaltar la última fila (Resultado)
        if i == len(data_rows) - 1:
            for cell in cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.bold = True
                        run.font.size = Pt(12)

    # Nota sobre límite de 5 MPa
    if resultados['q_adm'] == 5.0 and inputs['qu'] > 5.0:
        doc.add_paragraph("\nNota: El valor ha sido limitado a 5 MPa según especificación de la Guía.", style='Intense Quote')

    bio = io.BytesIO()
    doc.save(bio)
    return bio

# --- SECCIÓN A: INFO ---
st.markdown('<div class="titulo-seccion">MÉTODO GCOC (4.5.3)</div>', unsafe_allow_html=True)
col_req, col_form = st.columns([0.6, 0.4])

with col_req:
    st.markdown("""
    <div class="requisitos">
        <strong>Ámbito de Aplicación (Ap. 4.5.3):</strong><br>
        • Rocas con <strong>qu ≥ 1 MPa</strong>.<br>
        • Rocas con <strong>RQD ≥ 10%</strong>.<br>
        • Grado de meteorización I, II o III (Si es ≥ IV, tratar como suelo).
    </div>
    """, unsafe_allow_html=True)

with col_form:
    st.markdown("**Formulación usada:**")
    st.latex(r"p_{v,adm} = p_0 \cdot \alpha_1 \cdot \alpha_2 \cdot \alpha_3 \cdot \frac{q_u}{p_0}")
    st.caption("Donde: $p_0 = 1$ MPa. Resultado constante independiente de B.")

st.divider()

# --- SECCIÓN B: TABLAS PARA OBTENER COEFICIENTES  ---
st.subheader("📚 Tablas de Coeficientes")
col_izq, col_der = st.columns(2)

with col_izq:
    st.markdown('<div class="titulo-norma">Tabla 4.3: Coeficiente α1 (Tipo de Roca)</div>', unsafe_allow_html=True)
    st.markdown("""<table class="tabla-profesional">
        <tr><th>Grupo</th><th>Tipo de Roca</th><th>α1</th></tr>
        <tr><td>1</td><td class="text-left">Carbonatadas bien desarrolladas (Calizas, dolomías)</td><td>1.0</td></tr>
        <tr><td>2</td><td class="text-left">Ígneas y Metamórficas (esquistosidad subhorizontal)</td><td>0.8</td></tr>
        <tr><td>3</td><td class="text-left">Sedimentarias y Metamórficas (pizarras, esquistos verticalizados)</td><td>0.6</td></tr>
        <tr><td>4</td><td class="text-left">Rocas poco soldadas o cementadas (Margas, Yesos)</td><td>0.4</td></tr>
    </table>""", unsafe_allow_html=True)

with col_der:
    st.markdown('<div class="titulo-norma">Coeficiente α2 y α3</div>', unsafe_allow_html=True)
    st.markdown("""<table class="tabla-profesional">
        <tr><th>Grado</th><th>Meteorización</th><th>α2</th></tr>
        <tr><td>I</td><td class="text-left">Roca sana o fresca</td><td>1.0</td></tr>
        <tr><td>II</td><td class="text-left">Ligeramente meteorizada</td><td>0.7</td></tr>
        <tr><td>III</td><td class="text-left">Moderadamente meteorizada</td><td>0.5</td></tr>
    </table>""", unsafe_allow_html=True)
    st.info("α3 = mín(s, RQD/100)")

st.divider()

# --- SECCIÓN C: SIDEBAR (INPUTS SIMPLIFICADOS) ---
with st.sidebar:
    st.header("⚙️ Parámetros del Macizo")
    
    # 1. Resistencia
    qu_input = st.number_input("Resistencia qu [MPa]", value=15.0, step=0.5, on_change=reset_informe)
    
    # 2. RQD
    rqd_input = st.number_input("RQD [%]", value=50.0, min_value=0.0, max_value=100.0, step=1.0, on_change=reset_informe)

    # 3. Espaciamiento (s)
    s_input = st.number_input("Espaciamiento s [m]", value=0.30, step=0.05, min_value=0.01, format="%.2f", on_change=reset_informe)

    st.divider()
    st.subheader("⛰️ Factores de Calidad (α)")

    # 4. Selector Alfa 1
    opciones_a1 = {
        "G1: Calizas, dolomías (Carbonatadas)": 1.0,
        "G2: Granitos, esquistos subhorizontales (Ígneas)": 0.8,
        "G3: Pizarras, areniscas, esquistos verticales": 0.6,
        "G4: Margas, Yesos, rocas blandas": 0.4
    }
    txt_a1 = st.selectbox("Tipo de Roca (α1)", list(opciones_a1.keys()), on_change=reset_informe)
    val_a1 = opciones_a1[txt_a1]

    # 5. Selector Alfa 2
    opciones_a2 = {
        "Grado I: Roca sana": 1.0,
        "Grado II: Ligeramente meteorizada": 0.7,
        "Grado III: Moderadamente meteorizada": 0.5,
        "Grado IV o superior": 0.0 # Valor nulo
    }
    txt_a2 = st.selectbox("Meteorización (α2)", list(opciones_a2.keys()), on_change=reset_informe)
    val_a2 = opciones_a2[txt_a2]

# --- LÓGICA DE CÁLCULO Y VALIDACIÓN ---

# Validaciones
c_qu = qu_input >= 1.0
c_rqd = rqd_input >= 10.0
c_met = val_a2 > 0.0

checks_dict = {
    "Resistencia qu ≥ 1 MPa": "CUMPLE" if c_qu else "NO CUMPLE (Tratar como suelo)",
    "RQD ≥ 10%": "CUMPLE" if c_rqd else "NO CUMPLE (Tratar como suelo)",
    "Meteorización < Grado IV": "CUMPLE" if c_met else "NO CUMPLE (Tratar como suelo)"
}

# Cálculo
val_a3 = min(s_input, rqd_input / 100.0)

if c_qu and c_rqd and c_met:
    q_calc = 1.0 * val_a1 * val_a2 * val_a3 * qu_input
    # Límite máximo de 5 MPa
    if q_calc > 5.0:
        q_final = 5.0
        nota_limite = "Limitado a 5 MPa (Máx Norma)"
    else:
        q_final = q_calc
        nota_limite = None
else:
    q_final = 0.0
    nota_limite = "Fuera de Norma"

# --- VISUALIZACIÓN ---

# 1. Tabla de Checks
st.subheader("✅ Verificación las Hipótesis del Modelo")
df_checks = pd.DataFrame(list(checks_dict.items()), columns=["Criterio", "Estado"])
df_checks.set_index("Criterio", inplace=True)

def estilo_estado(val):
    if "NO CUMPLE" in val:
        return 'color: #c62828; font-weight: bold'
    return 'color: #2e7d32; font-weight: bold'

st.table(df_checks.style.applymap(estilo_estado, subset=['Estado']))

st.divider()

# 2. Ficha de Resultados
st.subheader("📋 Ficha de Cálculo")

col_res1, col_res2 = st.columns([0.6, 0.4])

with col_res1:
    # Tabla resumen de coeficientes
    df_resumen = pd.DataFrame([
        {"Parámetro": "Coef. α1 (Tipo de Roca)", "Valor": val_a1, "Descripción": txt_a1.split(":")[0]},
        {"Parámetro": "Coef. α2 (Meteorización)", "Valor": val_a2, "Descripción": txt_a2.split(":")[0]},
        {"Parámetro": "Coef. α3 (Discontinuidad)", "Valor": f"{val_a3:.3f}", "Descripción": "mín(s, RQD/100)"},
        {"Parámetro": "Resistencia (qu)", "Valor": f"{qu_input} MPa", "Descripción": "Dato de entrada"},
    ])
    st.table(df_resumen.set_index("Parámetro"))

with col_res2:
    # Resultado Final Destacado
    st.markdown("### Presión Admisible")
    st.markdown(f"""
    <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border: 2px solid #2e7d32; text-align: center;">
        <span style="font-size: 16px; color: #2e7d32; font-weight: bold;">Valor de Diseño (qd)</span><br>
        <span style="font-size: 42px; color: #1b5e20; font-weight: bold;">{q_final:.2f} MPa</span><br>
        <span style="font-size: 14px; color: #555;">{(q_final * 10.197):.2f} kg/cm²</span>
    </div>
    """, unsafe_allow_html=True)
    
    if nota_limite:
        st.warning(f"⚠️ {nota_limite}")

# --- GESTIÓN DE ESTADO Y DESCARGA ---
if 'informe_buffer' not in st.session_state:
    st.session_state.informe_buffer = None

with st.sidebar:
    st.divider()
    st.header("📄 Informe Resultados")
    
    if st.button("Generar informe Word"):
        with st.spinner("Generando informe..."):
            try:
                # Datos para el informe
                inputs_repo = {
                    "qu": qu_input, "rqd": rqd_input, "s": s_input,
                    "a1": val_a1, "txt_a1": txt_a1,
                    "a2": val_a2, "txt_a2": txt_a2
                }
                res_repo = {"a3": val_a3, "q_adm": q_final}
                
                buffer = generar_informe_word(inputs_repo, res_repo, checks_dict)
                
                st.session_state.informe_buffer = buffer
                st.session_state.informe_nombre = f"Informe_GCOC_{datetime.now().strftime('%H%M')}.docx"
                st.success("¡informe generado!")
            except Exception as e:
                st.error(f"Error generando informe: {e}")

    if st.session_state.informe_buffer is not None:
        st.download_button(
            label="📥 Descargar Documento",
            data=st.session_state.informe_buffer.getvalue(),
            file_name=st.session_state.informe_nombre,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary"
        )