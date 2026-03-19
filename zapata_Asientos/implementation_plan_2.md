# App Comparativa de Métodos de Cálculo de Asientos

Integrar en un único archivo `app_asientos_6.py` los dos métodos:
- **Método 1 — Steinbrenner** ([app_asientos_4.py](file:///d:/Documentos/Desarrollo/Python/CalculoPilotes/zapata_Asientos/app_asientos_4.py)): basado en funciones φ1, φ2 y s(z) analítico.
- **Método 2 — Ec. 68** ([app_asientos_5.py](file:///d:/Documentos/Desarrollo/Python/CalculoPilotes/zapata_Asientos/app_asientos_5.py)): integración directa Δεz = [Δσz - ν(Δσx+Δσy)] / E.

Ambos usan las mismas tensiones de Holl bajo el centro (superposición ×4 con B/2, L/2).

## Proposed Changes

### Nueva App — `app_asientos_6.py`

#### Diseño de vistas (sidebar radio):

| Vista | Contenido |
|---|---|
| 🧮 **Panel de Cálculo** | Tabla de entrada + botón calcular + **comparativa de resultados lado a lado** |
| 📋 **Detalle Steinbrenner** | Tabla φ1, φ2, m, s_techo, s_base por capa |
| 📋 **Detalle Ec. 68** | Tabla Δσz, Δσx, Δσy, Δεz, Δs por capa |
| 📉 **Bulbo de Presiones** | Gráfico único con curvas + criterio EC7 + z_i |
| 📖 **Fundamento Teórico** | Ambas formulaciones con LaTeX |

#### Vista principal — Panel de Cálculo:

```
┌─────────────────────────────────────────────────────────┐
│  2. Resultados          ── Comparativa de Métodos ──     │
│                                                         │
│  Métrica 1 (Steinbrenner)   Métrica 2 (Ec. 68)          │
│   ┌─────────────────┐       ┌─────────────────┐          │
│   │ s_total = X mm  │       │ s_total = Y mm  │          │
│   └─────────────────┘       └─────────────────┘          │
│                                                         │
│  Prof. influencia z_i: Z m (EC7)                        │
│                                                         │
│  Tabla comparativa por capa:                            │
│  Capa | z_techo | z_base | Δs Steinbrenner | Δs Ec.68   │
│  ...                                                    │
│                                                         │
│  Gráfico barras dobles (ambos métodos por capa)         │
└─────────────────────────────────────────────────────────┘
```

### Arquitectura del código:

```
Funciones compartidas:
  holl_centro(p, B, L, z)          → (Δσz, Δσx, Δσy) ×4 cuadrantes
  calcular_sigma_v0(z, df, NF)     → σ'v0
  calcular_z_influencia_ec7(...)   → z_i

Método 1 — Steinbrenner:
  calcular_phi1(m, n)
  calcular_phi2(m, n)
  calcular_s_z(p, B, E, nu, z, L)  → s(z) analítico
  calcular_steinbrenner(p, B, L, df, z_max) → (total, resultados)

Método 2 — Ec. 68:
  calcular_ec68(p, B, L, df, z_max) → (total, resultados)

Informe Word:
  generar_informe_word(...)        → incluye ambos métodos
```

### Datos de sesión (session_state):
- `df_terreno`, `calculo_realizado`
- `res_steinbrenner`, `total_steinbrenner`
- `res_ec68`, `total_ec68`
- `z_i_ec7`

## Verification Plan

### Manual
1. Lanzar: `streamlit run app_asientos_6.py`
2. Introducir datos por defecto y calcular
3. Verificar que ambos totales son numéricos y distintos entre sí
4. Verificar tabla comparativa muestra ambas columnas de Δs
5. Verificar gráfico de barras doble funciona
6. Verificar informe Word descargable con ambos métodos
