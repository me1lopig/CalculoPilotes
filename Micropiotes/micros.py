import numpy as np
import matplotlib.pyplot as plt
import sys

# Ajuste de la curvas para cada grupo

def calcular_arenas(plim):
    tau_iu = np.minimum(0.114 * plim, 0.40)
    tau_ir = np.minimum(0.145 * plim, 0.50)
    tau_irs = np.minimum(0.210 * plim, 0.62)
    return tau_iu, tau_ir, tau_irs

def calcular_arcillas(plim):
    plim = np.maximum(plim, 0.0)
    tau_irs = np.minimum(0.28 * np.power(plim, 0.5), 0.40)
    tau_ir = np.minimum(0.19 * np.power(plim, 0.6), 0.30)
    tau_iu = np.minimum(0.11 * np.power(plim, 0.7), 0.20)
    return tau_iu, tau_ir, tau_irs

# Encabezados

def leer_numero(mensaje, min_val=None, max_val=None):
    while True:
        try:
            valor = float(input(mensaje))
            if min_val is not None and valor < min_val:
                print(f"❌ Error: El valor debe ser mayor o igual a {min_val}.")
                continue
            if max_val is not None and valor > max_val:
                print(f"❌ Error: El valor debe ser menor o igual a {max_val}.")
                continue
            return valor
        except ValueError:
            print("❌ Error: Por favor, introduce un número válido.")

def imprimir_encabezado():
    print("\n" + "="*70)
    print("Calculadora de Adherencia límite en fuste para cálculo de Micropilotes")
    print("="*70 + "\n")

# Grafica 

def mostrar_grafica(tipo_suelo, plim_calculo, res_iu, res_ir, res_irs, input_label, x_min_plot):
    print("\n📊 Generando gráfica")
    
    fig, ax1 = plt.subplots(figsize=(10, 7))
    plt.subplots_adjust(bottom=0.20) 
    
    if tipo_suelo == 1: # Arenas
        x_max = 7.0
        title_graph = "Arenas y Gravas"
        label_primary = "Presión límite $P_{lim}$ (MPa)"
        label_secondary = "Índice SPT ($N$)"
        x_vals = np.linspace(x_min_plot, x_max, 200)
        y_iu, y_ir, y_irs = calcular_arenas(x_vals)
    else: # Arcillas
        x_max = 2.5
        title_graph = "Arcillas y Limos"
        label_primary = "Presión límite $P_{lim}$ (MPa)"
        label_secondary = "Compresión Simple $q_u$ (MPa)"
        x_vals = np.linspace(x_min_plot, x_max, 200)
        y_iu, y_ir, y_irs = calcular_arcillas(x_vals)

    # Ejes
    ax1.plot(x_vals, y_irs, 'k-', label='IRS', linewidth=2)
    ax1.plot(x_vals, y_ir, 'k-.', label='IR', linewidth=2)
    ax1.plot(x_vals, y_iu, 'k--', label='IU ', linewidth=2)
    
    # Punto del dato de entrada
    ax1.axvline(x=plim_calculo, color='red', linestyle=':', linewidth=2, label='Dato')
    ax1.scatter([plim_calculo]*3, [res_iu, res_ir, res_irs], color='red', zorder=5)
    
    # Etiquetas de valores
    offset = (x_max - x_min_plot) * 0.02
    ax1.text(plim_calculo + offset, res_irs, f' IRS: {res_irs:.3f}', color='red', va='bottom', fontweight='bold')
    ax1.text(plim_calculo + offset, res_ir, f' IR: {res_ir:.3f}', color='red', va='bottom')
    ax1.text(plim_calculo + offset, res_iu, f' IU: {res_iu:.3f}', color='red', va='top')

    # Eje 1
    ax1.set_xlabel(label_primary, fontsize=11, color='black')
    ax1.set_ylabel('Adherencia límite$\\tau_{f,lim}$ (MPa)', fontsize=11)
    ax1.set_title(f'Curvas: {title_graph}', fontsize=12, pad=15)
    ax1.set_xlim(x_min_plot, x_max)
    ax1.set_ylim(0, 0.7 if tipo_suelo == 1 else 0.45)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')

    
    ax2 = ax1.twiny()
    
    # Espacio para los dos ejes 
    ax2.xaxis.set_ticks_position('bottom')
    ax2.xaxis.set_label_position('bottom')
    
    # Desplazarlo 50 puntos hacia abajo
    ax2.spines['bottom'].set_position(('outward', 50))
    
    # Sincronizar límites
    ax2.set_xlim(ax1.get_xlim())
    
    # Calcular ticks coincidentes
    ticks_plim = ax1.get_xticks()
    ticks_plim = [t for t in ticks_plim if t >= x_min_plot and t <= x_max]
    ax2.set_xticks(ticks_plim)
    
    # Etiquetas 
    if tipo_suelo == 1:
        labels_sec = [f"{int(t * 20)}" for t in ticks_plim]
    else:
        labels_sec = [f"{t / 5:.2f}" for t in ticks_plim]
        
    ax2.set_xticklabels(labels_sec)
    
    # Colocar el segundo eje
    ax2.set_xlabel(label_secondary, fontsize=11, color='blue', fontweight='bold')
    ax2.tick_params(axis='x', colors='blue')
    
    plt.show()

# función principal

def main():
    while True:
        imprimir_encabezado()
        print("Seleccione el tipo de terreno:")
        print("1. Arenas y Gravas")
        print("2. Arcillas y Limos")
        print("3. Salir")
        
        opcion = input("\n👉 Opción (1/2/3): ")
        
        if opcion == '3':
            sys.exit()
            
        if opcion not in ['1', '2']:
            continue
            
        tipo_suelo = int(opcion)
        plim_calculo = 0.0
        x_min_plot = 0.0

        if tipo_suelo == 1:
            print("\n--- ARENAS Y GRAVAS ---")
            print("1. Presión Límite (Plim)\n2. Índice SPT (N)")
            sub_op = input("👉 Opción: ").upper()
            
            if sub_op == '1':
                val = leer_numero("Valor Plim [Min 0.5]: ", min_val=0.5)
                plim_calculo = val
                input_label = f"Plim={val}"
            elif sub_op == '2':
                val = leer_numero("Valor N [Min 10]: ", min_val=10)
                plim_calculo = val / 20.0
                input_label = f"N={val}"
            else: continue
            
            x_min_plot = 0.5
            res_iu, res_ir, res_irs = calcular_arenas(plim_calculo)

        elif tipo_suelo == 2:
            print("\n--- ARCILLAS Y LIMOS ---")
            print("1. Presión Límite (Plim)\n2. Compresión Simple (qu)")
            sub_op = input("👉 Opción: ").upper()
            
            if sub_op == '1':
                val = leer_numero("Valor Plim [Min 0.25]: ", min_val=0.25)
                plim_calculo = val
                input_label = f"Plim={val}"
            elif sub_op == '2':
                val = leer_numero("Valor qu [Min 0.05]: ", min_val=0.05)
                plim_calculo = val * 5.0
                input_label = f"qu={val}"
            else: continue
                
            x_min_plot = 0.25
            res_iu, res_ir, res_irs = calcular_arcillas(plim_calculo)

        print("\n" + "-"*30)
        print(f" IRS: {res_irs:.3f} MPa")
        print(f" IR:  {res_ir:.3f} MPa")
        print(f" IU:  {res_iu:.3f} MPa")
        print("-"*30)
        
        mostrar_grafica(tipo_suelo, plim_calculo, res_iu, res_ir, res_irs, input_label, x_min_plot)
        input("\n[ENTER] para nuevo cálculo...")

if __name__ == "__main__": 
    main()