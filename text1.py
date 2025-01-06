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
L=18
D=0.75

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
print('Carga de hundimiento por punta')
print('Qhp=',Qhp,'kN')

# Suelo Granular fuste
print()
print('Caso de suelo granular')
tensionesUnitariasGr,ListaCargaHundimientoGr,ListaLongitudesFusteAcumuladasGr=ft.tf_CTE_gr(cotas,nivel_freatico,pe_seco,pe_saturado,fi,D,L,kr,f,tipo_calculo)
print('Tensiones unitarias ',tensionesUnitariasGr,'KPa')
print('Carga hundimiento ',ListaCargaHundimientoGr,'KN')
print('Lista longitudes fuste acumuladas ',ListaLongitudesFusteAcumuladasGr,'m')


# Suelo Cohesivo fuste
print()
print('Caso de suelo cohesivo')
tensionesUnitariasCo,ListaCargaHundimientoCo,ListaLongitudesFusteAcumuladasCo=ft.tf_CTE_cohesivos(cotas,cu,D,L)
print('Tensiones unitarias ',tensionesUnitariasCo,'KPa')
print('Carga hundimiento ',ListaCargaHundimientoCo,'KN')
print('Lista longitudes fuste acumuladas ',ListaLongitudesFusteAcumuladasCo,'m')

# seleccion del tipo de cargas por fuste
Qhf=0

# seleccion de las cargas por fuste situacion drenada
for tipo in np.arange(0,len(ListaLongitudesFusteAcumuladasGr)):
    zt=ListaLongitudesFusteAcumuladasGr[tipo]
    tipoCalculo=tipo_calculo[ft.parametro_terreno(cotas,zt)]
    if tipoCalculo=='d':
        Qhf+=ListaCargaHundimientoGr[tipo]


# seleccion de las cargas por fuste situacion nodrenada
for tipo in np.arange(0,len(ListaLongitudesFusteAcumuladasCo)):
    zt=ListaLongitudesFusteAcumuladasCo[tipo]
    tipoCalculo=tipo_calculo[ft.parametro_terreno(cotas,zt)]
    if tipoCalculo=='nd':
        Qhf+=ListaCargaHundimientoCo[tipo]

print()
print('Carga de hundimiento por fuste')
print('Qhf=',Qhf,'kN')


print()
print('usando función directa')
Qhf2=ft.cargaHundimientoFuste(ListaLongitudesFusteAcumuladasGr,ListaLongitudesFusteAcumuladasCo,ListaCargaHundimientoGr,ListaCargaHundimientoCo,cotas,tipo_calculo)
print('Qhf2=',Qhf2,'kN')


print()
print('Resumen\n')
print('Carga de hundimiento por fuste')
print('Qhf=',Qhf2,'kN')
print('Carga de hundimiento por punta')
print('Qhp=',Qhp,'kN')
print('Qh ',Qhf2+Qhp,' kN')
print('Qadm ',(Qhf2+Qhp)/3,' kN')