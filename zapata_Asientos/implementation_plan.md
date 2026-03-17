# Mejora: Cálculo Correcto de Zona de Influencia EC7

La aplicación actual usa un criterio simplificado (`Δσz ≤ 0.1·p`) para la zona de influencia, pero el EC7 establece que la profundidad de influencia `z_i` se alcanza cuando:

$$\Delta\sigma_z(z_i) \leq 0.20 \cdot \sigma'_{v0}(z_i)$$

Para calcular `σ'v0` correctamente se necesita:
- **γ (peso específico aparente)** → para suelo por encima del nivel freático
- **γsat (peso específico saturado)** → para suelo por debajo del nivel freático
- **Nf (profundidad nivel freático)** → para saber dónde aplica cada uno

## Proposed Changes

### Capa de Datos

#### [MODIFY] [app_asientos_2.py](file:///d:/Documentos/Desarrollo/Python/CalculoPilotes/zapata_Asientos/app_asientos_2.py)

**Tabla de estratigrafía** — añadir dos columnas nuevas con valores por defecto:

| Campo | Valor por defecto |
|---|---|
| `γ (kN/m³)` | 18.0 |
| `γsat (kN/m³)` | 20.0 |

**Sidebar** — nuevo input numérico:
- `Nf`: Profundidad nivel freático (m), por defecto 100 m (sin nivel freático)

---

### Capa de Lógica (Funciones nuevas)

**`calcular_sigma_v0(df_terreno, z, Nf)`**
- Recorre las capas acumulando tensión vertical
- Por encima de Nf: suma `γi · Δz`
- Por debajo de Nf: suma [(γsat_i - 9.81) · Δz](file:///d:/Documentos/Desarrollo/Python/CalculoPilotes/zapata_Asientos/app_asientos_2.py#22-29)
- Devuelve `σ'v0` en kPa para una profundidad z

**`calcular_zona_influencia(p, B, L, df_terreno, Nf)`**
- Búsqueda iterativa (bisección numérica con `numpy`) del z donde `Δσz(z) = 0.20·σ'v0(z)`
- Límite de búsqueda: hasta la profundidad total de las capas
- Devuelve `z_i` en metros (o `None` si no se encuentra en el rango)

---

### Capa de Interfaz

**Vista "📉 Incremento de Tensiones"**:
- Nueva curva `σ'v0(z)` (línea naranja discontinua) en el gráfico
- Nueva curva `0.20·σ'v0(z)` (línea naranja sólida) — umbral del criterio
- Línea horizontal en `z = z_i` indicando la profundidad de influencia
- Métrica numérica: `z_i` calculado en panel izquierdo

**Vista "🧮 Panel de Cálculo"**:
- Nueva métrica: `Profundidad de influencia z_i`

**Vista "📖 Fundamento Teórico"**:
- Nueva subsección explicando el criterio de `σ'v0` con la fórmula LaTeX

## Verification Plan

### Manual — Caso simple verificable a mano

Con 3 capas (Relleno 1.5m γ=18, Arcilla 3m γ=18/γsat=20, Grava 5m γ=18/γsat=21), Nf=2m, B=2m, L=3m, p=150 kPa:

1. Ejecutar la app: `streamlit run d:\Documentos\Desarrollo\Python\CalculoPilotes\zapata_Asientos\app_asientos_2.py`
2. Introducir los datos anteriores en la tabla y sidebar
3. Verificar manualmente `σ'v0` a z=2m: debe ser `18·2 = 36 kPa`
4. Verificar `σ'v0` a z=4m: `18·2 + (20-9.81)·2 = 56.38 kPa`
5. Comprobar que `z_i` mostrado en la app coincide visualmente con la intersección de `Δσz` y `0.20·σ'v0` en el gráfico

> [!IMPORTANT]
> No hay tests automatizados en el proyecto. La verificación es manual vía la app Streamlit.
