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


# Suelo Granular
print('Caso de suelo granular')
tensionesUnitariasGr,ListaCargaHundimientoGr,ListaLongitudesFusteAcumuladasGr=ft.tf_CTE_gr(cotas,nivel_freatico,pe_seco,pe_saturado,fi,D,L,kr,f,tipo_calculo)
print('Tensiones unitarias ',tensionesUnitariasGr,'KPa')
print('Carga hundimiento ',ListaCargaHundimientoGr,'KN')
print('Lista longitudes fuste acumuladas ',ListaLongitudesFusteAcumuladasGr,'m')


# Suelo Cohesivo
print('Caso de suelo cohesivo')
tensionesUnitariasCo,ListaCargaHundimientoCo,ListaLongitudesFusteAcumuladasCo=ft.tf_CTE_cohesivos(cotas,cu,D,L)
print('Tensiones unitarias ',tensionesUnitariasCo,'KPa')
print('Carga hundimiento ',ListaCargaHundimientoCo,'KN')
print('Lista longitudes fuste acumuladas ',ListaLongitudesFusteAcumuladasCo,'m')

print('Tipo de calculo')
print(tipo_calculo)

print(cotas)

# seleccion del tipo de cálculo 
for tipo in np.arange(0,len(ListaLongitudesFusteAcumuladasGr)):
    zt=ListaLongitudesFusteAcumuladasGr[tipo]
    print(zt,tipo_calculo[ft.parametro_terreno(cotas,zt)])




