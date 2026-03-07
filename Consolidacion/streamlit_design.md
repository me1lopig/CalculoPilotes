# Diseño de la Aplicación Streamlit: Consolidación de Suelos

Esta aplicación es una migración de una herramienta de MATLAB que resuelve la **Ecuación de la Consolidación de Terzaghi** mediante el método de **Diferencias Finitas Explicitas**.

## 1. Entradas de Usuario (Barra Lateral)

| Parámetro | Descripción | Unidad |
| :--- | :--- | :--- |
| **Espesor del estrato** | Longitud total de la capa de suelo | m |
| **Carga exterior** | Presión aplicada inicialmente | kPa |
| **Coeficiente de consolidación ($c_v$)** | Velocidad de consolidación | m²/día |
| **Coeficiente de compresibilidad ($m_v$)** | Compresibilidad del suelo | m²/kN |
| **Incremento de x ($h$)** | Paso espacial para la malla | m |
| **Incremento de t ($k$)** | Paso temporal para la malla | días |
| **Máximo grado de consolidación** | Límite para detener el cálculo | % |
| **Condiciones de contorno** | Tipo de drenaje (Doble, Superior, Inferior) | - |

## 2. Lógica de Cálculo (Python/NumPy)

- **Validación de Convergencia**: Se debe cumplir que $\alpha = \frac{c_v \cdot k}{h^2} \leq 0.5$.
- **Inicialización**: Vector de presiones de poro iniciales $u_0$ igual a la carga exterior.
- **Iteración Temporal**:
    - **Doble Drenaje**: $u(0)=0, u(L)=0$.
    - **Drenaje Superior**: $u(0)=0, \frac{\partial u}{\partial x}(L)=0$.
    - **Drenaje Inferior**: $\frac{\partial u}{\partial x}(0)=0, u(L)=0$.
- **Cálculos Derivados**:
    - **Grado de Consolidación ($U$)**: Calculado mediante integración numérica (Regla de Simpson/Trapecio) del área bajo la curva de presiones.
    - **Asiento ($s$)**: $s = s_{max} \cdot U$, donde $s_{max} = H \cdot m_v \cdot \Delta \sigma$.
    - **Caudal ($Q$)**: Basado en la ley de Darcy $Q = k \cdot i$, donde el gradiente $i$ se obtiene de la derivada de la presión en el contorno drenante.

## 3. Visualizaciones (Plotly)

1. **Perfil de Presiones de Poro**: Gráfico de profundidad vs. presión (eje Y invertido).
2. **Asientos vs. Tiempo**: Evolución del asentamiento.
3. **Grado de Consolidación vs. Tiempo**: Progreso de la consolidación.
4. **Caudal vs. Tiempo**: Variación del flujo de agua.
5. **Consolidación vs. Factor Tiempo ($T_v$)**: Gráfico semilogarítmico estándar en geotecnia.

## 4. Estructura del Código

- `app.py`: Archivo principal de Streamlit.
- `engine.py`: Lógica de cálculo numérica separada de la interfaz.
