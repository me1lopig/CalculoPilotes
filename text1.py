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
archivo_terreno=os.path.join(carpeta,'datos_terreno_4.xlsx')
archivo_pilotes=os.path.join(carpeta,'datos_pilotes.xlsx')

# importacion de datos del terreno
espesor,cotas,az,nivel_freatico,pe_seco,pe_saturado,cu,cohesion,fi,tipo_datos,tipo_calculo=ft.datos_terreno(archivo_terreno)

# importacion de los datos de los pilotes 
diametros,Lmin,Lincr,fp,kr,f=ft.datos_pilotes(archivo_pilotes)



# Datos geometricos de los pilotes (ejemplo)
L=21
D=0.75



print('Caso de suelo granular')


tensionesUnitarias,ListaCargaHundimiento,ListaLongitudesFusteAcumuladas,Qhf=ft.tf_CTE_gr(cotas,nivel_freatico,pe_seco,pe_saturado,fi,D,L,kr,f)
#print('Qhf=',Qhf,'kN')
#print('Qadf=',Qhf/3,'kN')
#print('Tensiones unitarias ',tensionesUnitarias,'KPa')
print('Carga hundimiento ')
print(ListaCargaHundimiento,'KN')
#print('Carga admisible')
#print('Qadm=',(Qhf)/3,'kN')


#print('Partes de la carga de hundimiento fuste')

print('Lista longitudes fuste acumuladas ')
print(ListaLongitudesFusteAcumuladas)


#print('Caso de suelo cohesivo')

#qp,Qhp=ft.qp_CTE_cohesivos(cotas,cu,D,L)
#print('qp=',qp,'kPa')
#print('Qhp=',Qhp,'KN')
#print('Qadp=',Qhp/3,'KN')

#tensionesUnitarias,ListaCargaHundimiento,Qhf=ft.tf_CTE_cohesivos(cotas,cu,D,L)
#print('Qhf=',Qhf,'kN')
#print('Qadf=',Qhf/3,'kN')
#print('Tensiones unitarias ',tensionesUnitarias,'KPa')
#print('Carga hundimiento ',ListaCargaHundimiento,'KN')
#print('Carga admisible')
#print('Qadm=',(Qhf+Qhp)/3,'kN')