# Cálculo de Tensiones y Asientos: ZAPATA CONTINUA
# Versión: FINAL RELEASE (Full Features)

import funcionesCalculo as ft 
import numpy as np 

print("=================================================")
print("   CÁLCULO GEOTÉCNICO: ZAPATA CONTINUA (2D)      ")
print("=================================================")

# 1. Configuración Inicial
directorio = ft.crea_directorio()

# 2. Carga de Datos
try:
    espesor, cotas, az, nf, pe_seco, pe_saturado, E, poisson, c, phi, meta_datos = ft.datos_terreno()
    B, q, ax, incrx, incrz_input = ft.datos_carga() 
    print("-> Datos cargados correctamente.")
except Exception as e:
    print(f"ERROR: {e}")
    exit()

# --- CONTROL DE CALIDAD DEL MALLADO ---
espesores_reales = [e for e in espesor if e > 0.01]
if espesores_reales:
    h_min = min(espesores_reales)
    if incrz_input > h_min:
        print(f"\n[AVISO] El incremento Z ({incrz_input}m) es muy grande para la capa de {h_min}m.")
        incrz = h_min / 2.0 
        print(f"[AUTO-AJUSTE] Nuevo incrz establecido en: {incrz:.3f} m\n")
    else:
        incrz = incrz_input
else:
    incrz = incrz_input

# 3. Preparación de Mallas
b = B / 2.0  
xcoord = np.arange(-(ax), ax + incrx, incrx)

# Malla Vertical Inteligente
z_regular = np.arange(incrz, az + incrz, incrz)
puntos_clave = np.concatenate(([0.05], cotas))
zcoord = np.concatenate((z_regular, puntos_clave))
zcoord = np.unique(zcoord) 
zcoord = zcoord[zcoord > 0.001] 
zcoord = zcoord[zcoord <= az + 0.01] 

# Inicialización
shape = (zcoord.size, xcoord.size)
m_tension_z = np.zeros(shape)
m_tension_x = np.zeros(shape)
m_tension_xz = np.zeros(shape)
m_tension_geo = np.zeros(shape)
v_asientos = []

# 4. Bucle de Cálculo
print(f"-> Procesando malla optimizada ({shape[0]}x{shape[1]} puntos)...")

for i, x in enumerate(xcoord):
    asiento_acumulado = 0
    for j, z in enumerate(zcoord):
        # A. Inducidas
        sz, sx, txz = ft.tension_zapata_continua(b, q, x, z)
        # B. Geostáticas
        s_geo = ft.tension_geostatica(z, cotas, pe_saturado, pe_seco, nf)
        
        m_tension_z[j, i] = sz
        m_tension_x[j, i] = sx
        m_tension_xz[j, i] = txz
        m_tension_geo[j, i] = s_geo
        
        # C. Asientos
        if j == 0:
            dz = z 
        else:
            dz = z - zcoord[j-1]
            
        d_asiento = ft.asiento_deformacion_plana(cotas, z, dz, E, poisson, sx, sz)
        asiento_acumulado += d_asiento
        
    v_asientos.append(asiento_acumulado)

# 5. Exportación
print("-> Generando resultados y gráficos...")

ft.guardar_xlsx_matriz(xcoord, zcoord, m_tension_z, directorio, 'Tension_Vertical_Inducida')
ft.guardar_xlsx_matriz(xcoord, zcoord, m_tension_x, directorio, 'Tension_Horizontal_Inducida')
ft.guardar_xlsx_vector(xcoord, v_asientos, directorio, 'Asientos_Superficiales')

tipos = ['isolinea', 'continua']
for t in tipos:
    ft.graficos_tensiones_zapata(xcoord, zcoord, m_tension_z, directorio, 'Tensión Vertical Sigma_Z', t, B, cotas, nf)
    ft.graficos_tensiones_zapata(xcoord, zcoord, m_tension_x, directorio, 'Tensión Horizontal Sigma_X', t, B, cotas, nf)
    ft.graficos_tensiones_zapata(xcoord, zcoord, m_tension_xz, directorio, 'Tensión Cortante Tau_XZ', t, B, cotas, nf)

# Gráfico de Asientos (Estilo Técnico)
ft.grafico_asientos(xcoord, v_asientos, directorio, 'Perfil de Asientos', cotas, nf, B)

# Informe Word Profesional
print("-> Generando Informe Word...")
ft.guardar_reporte_docx(B, q, ax, az, directorio, espesor, pe_seco, pe_saturado, E, poisson, nf)

print(f"\n✅ PROCESO COMPLETADO. Resultados en: {directorio}")