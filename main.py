# cálculo de pilotes según las normas vigentes en España
    # Guía de cimentaciones de obras de carretera, Dirección General de Carreteras, Ministerio de Fomento
    # CTE DB SE Cimientos
    # R.O.M 05.05 Recomendaciones de Obras Marítimas


# version 22/08/2023
# Germán López Pineda
# Ingeniero de Caminos Canales y Puertos UGR
# Master en Matemática Computacional UJI
# Master en Ingeniería del Terreno UCO
# Grupo de investigación RNM 244 Ingeniería Ambiental y Geofísica Universidad de Córdoba
# me1lopig@uco.es
# rocasysuelos@gmail.com


# llamada a las librerias
import numpy as np # librería para cálculos matematicos

# llamada a librerias definidas
import funcionesCalculo as ft # libreria de funciones auxiliares y de cálculo


# importacion de datos del terreno del archivo datos_terreno.xlsx
espesor,cotas,az,nivel_freatico,pe_seco,pe_saturado,cu,cohesion,fi,tipo_datos=ft.datos_terreno()


# graficas de las tensiones totales, efectivas y de poro
incremento=0.2
profundidad_maxima=max(cotas)
valor_z=np.arange(0,profundidad_maxima+incremento,incremento)
presionEfectiva=[]
presionTotal=[]
presionPoro=[]

for z in valor_z:
    pe_sat=pe_saturado[ft.parametro_terreno(cotas,z)]
    pe_ap=pe_seco[ft.parametro_terreno(cotas,z)]
    presion=ft.presion_total(cotas,nivel_freatico,pe_saturado,pe_seco,z)
    u_z=ft.n_freatico(nivel_freatico,z)*9.81
    presion_efectiva=presion-u_z
   
    presionEfectiva.append(presion_efectiva)
    presionTotal.append(presion)
    presionPoro.append(u_z)
    print(z,presion,presion_efectiva,u_z)

presionE = (presionEfectiva, valor_z, 'darkred', 'Presion Efectiva')
presionT = (presionTotal, valor_z, 'blue', 'Presion Total')
presionP = (presionPoro, valor_z, 'green', 'Presion de Poro')

# todas las tensiones
lista_datos = [presionE, presionT, presionP]
ft.grafico_grupo(lista_datos, "Tensiones en el terreno",'kN/m2')

# todas las tensiones
lista_datos = [presionE]
ft.grafico_grupo(lista_datos, "Tensiones en el terreno",'kN/m2')



