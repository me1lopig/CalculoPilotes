# cálculo de pilotes según CTE DB SE Cimientos


# version 22/12/2024
# Germán López Pineda
# Ingeniero de Caminos Canales y Puertos UGR
# Master en Matemática Computacional UJI
# Master en Ingeniería del Terreno UCO
# Grupo de investigación RNM 244 Ingeniería Ambiental y Geofísica Universidad de Córdoba
# me1lopig@uco.es
# rocasysuelos@gmail.com


# llamada a las librerias
import numpy as np # librería para cálculos matematicos
import os

# llamada a librerias definidas
import funcionesCalculo as ft # libreria de funciones auxiliares y de cálculo



# ruta absoluta de los archivos de calculo
carpeta=os.getcwd()
carpeta=os.path.join(carpeta, 'Data/')
archivo_terreno=os.path.join(carpeta,'datos_terreno_5.xlsx')
archivo_pilotes=os.path.join(carpeta,'datos_pilotes.xlsx')

# importacion de datos del terreno
espesor,cotas,az,nivel_freatico,pe_seco,pe_saturado,cu,cohesion,fi,tipo_datos,tipo_calculo=ft.datos_terreno(archivo_terreno)

# importacion de los datos de los pilotes 
diametros,Lmin,Lincr,fp,kr,f=ft.datos_pilotes(archivo_pilotes)

# creacion del directorio de trabajo
directorio=ft.crea_directorio()

# graficas de las tensiones totales, efectivas y de poro del terreno según al archivo datos_terreno.xlsx
ft.grafica_tensiones(cotas,pe_seco,pe_saturado,nivel_freatico,directorio)

# Datos geometricos de los pilotes (ejemplo)
L=10
D=0.60

# control de longitud máxima no mas de prof max modelo-3D
if L>(max(cotas)-3*D):
    print('Longitud fuera del modelo')
    print('Se interrumpe el programa')
    exit()

# Calculo de la tensión en punta a la profundidad L
situacionCalculo=tipo_calculo[ft.parametro_terreno(cotas,L)]

if situacionCalculo=='d':
    qp,Qhp=ft.qp_CTE_gr(cotas,nivel_freatico,pe_saturado,pe_seco,fi,D,L,fp)
elif situacionCalculo=='nd':
    qp,Qhp=ft.qp_CTE_cohesivos(cotas,cu,D,L)
else:
    print('Situacion de cálculo no considerada')
    print('Revise los datos de entrada')
    exit()

# guardamos los resultados en un archivo de texto

f=open(directorio+'/calculosPunta.txt','w')
f.write('Diámetro='+str(D)+'m\n')
f.write('Longitud='+str(L)+'m\n')
f.write('Tension en la punta '+str(qp)+' kPa\n')
f.write('El Qhp para la situacion '+str(situacionCalculo)+' es '+str(Qhp)+' kN\n')
f.write('El Qadp para la situacion '+str(situacionCalculo)+' es '+str(Qhp/3)+' kN')

f.close()