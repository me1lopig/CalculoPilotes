# cálculo de tensiones verticales en el terreno

# 
# Germán López Pineda
# Ingeniero de Caminos Canales y Puertos UGR
# Master en Matemática Computacional UJI
# Master en Ingeniería del Terreno UCO

# llamada a las librerias
import numpy as np # librería para cálculos matematicos
import os

# llamada a librerias definidas
import funcionesCalculo as ft # libreria de funciones auxiliares y de cálculo

# ruta absoluta de los archivos de calculo
carpeta = os.getcwd()
# Asegúrate de que la carpeta Data existe o ajusta la ruta según tu estructura
carpeta = os.path.join(carpeta, 'Data/') 
archivo_terreno = os.path.join(carpeta, 'datos_terreno.xlsx')

# importacion de datos del terreno (Solo cotas y pesos)
# Se han eliminado: espesor, az, cu, cohesion, fi, tipo_datos, tipo_calculo
cotas, nivel_freatico, pe_seco, pe_saturado = ft.datos_terreno(archivo_terreno)

# creacion del directorio de trabajo
directorio = ft.crea_directorio()

# graficas de las tensiones totales, efectivas y de poro
ft.grafica_tensiones(cotas, pe_seco, pe_saturado, nivel_freatico, directorio)
