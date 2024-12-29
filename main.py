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

# llamada a librerias definidas
import funcionesCalculo as ft # libreria de funciones auxiliares y de cálculo


# importacion de datos del terreno del archivo datos_terreno.xlsx
espesor,cotas,az,nivel_freatico,pe_seco,pe_saturado,cu,cohesion,fi,tipo_datos=ft.datos_terreno()

# importacion de los datos de los pilotes 
diametros,Lmin,Lincr,fp,kr,f=ft.datos_pilotes()

# creacion del directorio de trabajo
#directorio=ft.crea_directorio()

# graficas de las tensiones totales, efectivas y de poro del terreno según al archivo datos_terreno.xlsx
#ft.grafica_tensiones(cotas,pe_seco,pe_saturado,nivel_freatico,directorio)

L=15

qp,Qhp=ft.qp_CTE_gr(cotas,nivel_freatico,pe_saturado,pe_seco,fi,0.65,L,fp)
print('qp=',qp,'kPa')
print('Qhp=',Qhp,'KN')
print('Qadp=',Qhp/3,'KN')



tensionesUnitarias,Qhf=ft.tf_CTE_gr(cotas,nivel_freatico,pe_seco,pe_saturado,fi,0.65,L,kr,f)
print('Qhf=',Qhf)
print('Qadf=',Qhf/3)
print('Tansiones unitarias ',tensionesUnitarias)
print('Carga admisible')
print('Qadm=',(Qhf+Qhp)/3,'kN')