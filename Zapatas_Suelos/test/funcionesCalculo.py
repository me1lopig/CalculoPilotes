# libreria para el cálculo de tensiones y asientos bajo la cargas 
# cargas contempladas
    # Rectangulares

# Listado de funciones (revisar)
    # crea_directorio(), genera el directorio de trabajo para alojar los archivos de proyecto
    # datos_rectangular, importa los datos de la carga rectangular
    # datos_terreno, importa de una hoja excel los datos del terreno
    # tension_rectangular, calcula las tensiones (x,z,xz) de una carga rectanguar infinita
    # asiento_elastico, calcula el asiento elástico del terreno
    # asiento_consolidación, calcula al asiento por consolidación
    # parametro_terreno, obtiene cualquier parámetro del terreno en función de la profundidad
    # n_freatico, calcula si a una profundidad existe nivel freático
    # tension_terreno, obtiene la tensión total, efectiva y de poro para una profundidad, vertical y horizontal
    # guardar_docx_datos, se guarda un resumen de los datos y resultados en formato word
    # guardar_xlxs_tensiones, guerda en formato excel los resultados de los cálculos de las tensiones creados
        # por la carga del terraplén, en x, z, xz
    # guardar_xlxs_asientos, guarda en excel los resultados de los cálculos de los asientos
    # graficos_tensiones, guarda los graficos de las tensiones producidas por el terraplén, en contínuo e isolínea
    # graficos_asientos, guarda la gráfica de los asientos del terraplén en el ancho de banda

# librerias 
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
from docx import Document
from docx.shared import Cm
import os
from datetime import datetime


# Grupo de funciones

def crea_directorio():
    # creación del directorio de trabajo para guardar resultados
    now = datetime.now()
    directorio=(str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second))
    os.mkdir(directorio)
    return directorio


def datos_rectangular():
        # importacion de los datos del terraplen
    # desde la hoja excel
    libro = openpyxl.load_workbook('datos_rectangular.xlsx')
    hoja = libro.active 

    # datos de la carga
    b=hoja.cell(row=2, column=1).value # ancho de banda
    q=hoja.cell(row=2, column=2).value # carga 
    
    # datos del mallado de cálculo
    ax=hoja.cell(row=2, column=3).value # ancho de banda
    incrx=hoja.cell(row=2, column=4).value # incremento de x
    incrz=hoja.cell(row=2, column=5).value # incremento de z
    
    return b,q,ax,incrx,incrz

def datos_terreno():

    libro = openpyxl.load_workbook('datos_terreno.xlsx')
    hoja = libro.active

    # importacion de variables del terreno
    espesor=[]
    cotas=[]
    pe_seco=[]
    pe_saturado=[]
    E=[]
    poisson=[]
    tipo_datos=[]
    cohesion=[]
    fi=[]
   
    for row in hoja.iter_rows():
        espesor.append(row[0].value)
        espesor[0]=0
        az=sum(espesor)
        nivel_freatico=hoja.cell(row=2, column=2).value
        pe_seco.append(row[2].value)
        pe_seco[0]=0
        pe_saturado.append(row[3].value)
        pe_saturado[0]=0
        E.append(row[4].value)
        E[0]=0
        poisson.append(row[5].value)
        poisson[0]=0
        cohesion.append(row[6].value)
        cohesion[0]=0
        fi.append(row[7].value)
        fi[0]=0

    for i in np.arange(len(espesor)):
        cotas.append(sum(espesor[0:i+1]))
    
    # se toman los datos de la cabecera
    for filas in hoja.iter_cols():
        tipo_datos.append(filas[0].value)

    return espesor,cotas,az,nivel_freatico,pe_seco,pe_saturado,E,poisson,cohesion,fi,tipo_datos



def tension_rectangular(b,q,x,z):
    # b es el ancho de la carga
    # q es la carga
    # x,z son las coordenadas donde se calulan las tensiones
    # calculos de los angulos
    # los valores se calculan desde el centro de la carga
    delta=np.arctan((x-b)/z)
    alfa=np.arctan((x+b)/z)-delta
    # cálculo de las tensiones
    tensionz=(q/np.pi)*(alfa+np.sin(alfa)*np.cos(alfa+2*delta))
    tensionx=(q/np.pi)*(alfa-np.sin(alfa)*np.cos(alfa+2*delta))
    tensionxz=(q/np.pi)*(np.sin(alfa)*np.sin(alfa+2*delta))

    return tensionz,tensionx,tensionxz
    

def asiento_elastico(cotas,z,hi,E,poisson,tensionx,tensionz):
    # calculo de aientos para un estado bidimensional de tensiones
    # se calcula para un valor de z determinado
    # los valores en cm
    asiento=-hi*(tensionz-poisson[parametro_terreno(cotas,z)]*tensionx)/E[parametro_terreno(cotas,z)]
    # se pone el valor negativo
    return asiento

def asiento_consolidacion():
    # calculo de aientos para un estado bidimensional de tensiones
    # se calcula para un valor de z determinado
    # los valores en m
    return 'En construcción'

def parametro_terreno(cotas,zt):
    # esta funcion localiza el parámetro del terreno para una z determinada
    # se parte de los valores discretos tomados de la excel de datos_terreno.xlsx

    for z in np.arange(len(cotas)-1):
        cota_superior=cotas[z]
        cota_inferior=cotas[z+1]
        if zt>=cota_superior and zt<=cota_inferior:
            break
    return z+1

def n_freatico(nivel_freatico,z):
    # función para calcular el nivel freático de forma continua
    # indica si un valor del terreno está o no bajo el nf
    # devuelve el valor de z o un 0 si está por encima
    if z>=nivel_freatico:
        return z
    else:
        return 0

def tension_terreno(z_terreno,espesor,cotas,pe_saturado):
    # calculo de tensiones naturales en el terreno
    # ojo con los valores de los pesos especificos
    # metodo alternativo para el cálculo de las tensiones

    indice=parametro_terreno(cotas,espesor,z_terreno)
    tension=0
    for index in np.arange(indice):
        tension=espesor[index+1]*pe_saturado[index+1]+tension
        print(index+1)
    tension=(z_terreno-cotas[indice])*pe_saturado[indice+1]+tension
    return tension


def tension_total(z_terreno,cotas,pe_saturado,pe_seco,nf):
    # calculo por suma a lo bestia
    # cálculo de la tension total del terreno
    tension_z=0
    tension_x=0
    for zi in np.arange(0,z_terreno,0.10):
        if zi<nf:
            pe=pe_seco[parametro_terreno(cotas,zi)]
        else:
             pe=pe_saturado[parametro_terreno(cotas,zi)]
        tension_z+=pe*0.10 # tension vertical

    return tension_z


def guardar_docx_datos(a,b,h,q,ax,incrx,az,incrz,directorio,tipo_datos):
    # creación de un informe con los datos de entrada 
    # y de resultados
    
    document = Document()
    # Añadimos un titulo al documento, a nivel 0
    document.add_heading('Datos del modelo de cálculo', 0)
    # Añadimos un párrafo
    p = document.add_paragraph('En este documento se incluyen los datos de la carga y características del terreno, ')
    p.add_run('Así como los resultados de las tensiones y asientos ')
    #p.add_run('negrita').bold = True
    #p.add_run(' o ')
    #p.add_run('itálica.').italic = True
    
    # Para indicar subtitulo se indica el nivel 1
    document.add_heading('Cálculos realizados ', level=1)
    #document.add_paragraph('Los cálculos realizados son:')
    document.add_paragraph('Incremento de tensiones en x [kN/m2]', style='List Number')
    document.add_paragraph('Incremento de tensiones en xz [kN/m2]', style='List Number')
    document.add_paragraph('Incremento de tensiones en z [kN/m2]', style='List Number')
    document.add_paragraph('Asientos bajo el terraplén [cm]', style='List Number')

    # Características del terraplén
    document.add_heading('Datos del terraplen ', level=1)
    document.add_paragraph("Valor del ancho del derrame {0:0.2f} m".format(a), style='List Bullet')
    document.add_paragraph("Valor del ancho de la semibase {0:0.2f} m".format(b), style='List Bullet')
    document.add_paragraph("Valor de la altura del terraplén {0:0.2f} m".format(h), style='List Bullet')
    document.add_paragraph("Peso específico del relleno de terraplén {0:0.2f} kN/m3".format(q/h), style='List Bullet')
    document.add_paragraph("Valor de la carga de tierras  {0:0.2f} kN/m2".format(q), style='List Bullet')

    # Características del mallado de cálculo
    document.add_heading('Datos del mallado ', level=1)
    document.add_paragraph("Ancho de banda {0:0.2f} m".format(ax), style='List Bullet')
    document.add_paragraph("incremento en x= {0:0.2f} m".format(incrx), style='List Bullet')
    document.add_paragraph("Profundidad de cálculo {0:0.2f} m".format(az), style='List Bullet')
    document.add_paragraph("incremento en z= {0:0.2f} m".format(incrz), style='List Bullet')


    # Tabla de datos del terreno
    document.add_heading('Datos del terreno ', level=1)
    data = (('UG-01', 12), ('UG-02', 5), ('UG-03', 12))

    # encabezado de la tabla
    # se ponen los encabezados sin colocar c ni fi en la tabla
    table = document.add_table(rows=1, cols=len(tipo_datos[0:6])) # definición de la tabla
    # encabezados de la tabla de datos
    for dato in np.arange(len(tipo_datos[0:6])):
        table.rows[0].cells[dato].text = tipo_datos[dato]
    
    for prod, numbr in data:
        row_cells = table.add_row().cells
        row_cells[0].text = prod
        row_cells[1].text = str(numbr)

    # imágenes de resultados de los cálculos
    # se localizan las imágenes del directorio que sean *.png y se meten en unna lista
    listado=os.listdir(directorio)
    imagenes = []
    for fichero in listado:
        if os.path.isfile(os.path.join(directorio, fichero)) and fichero.endswith('.png'):
            imagenes.append(fichero)
    imagenes=sorted(imagenes) # ordenacion de la lista de imágenes

    # carga de la imagen de asientos
    document.add_heading('Asientos', 3) 
    document.add_picture(directorio+'/'+imagenes[-1],width=Cm(12))
    
    # carga del resto de imágenes
    for index in np.arange(0,len(imagenes)-1):
        document.add_heading(imagenes[index][0:len(imagenes[index])-4], 3) 
        document.add_picture(directorio+'/'+imagenes[index],width=Cm(12))

    # Guardado del archivo con la información
    document.save(directorio+'/'+'Info.docx')


def guardar_xlsx_tensiones(xcoord,zcoord,array_datos,directorio,nombre_archivo):

    # guardado en excel de los resultados de los calculos de una matriz de datos
    wb = openpyxl.Workbook()
    hoja = wb.active
    for fila in np.arange(zcoord.size):
        hoja.cell(row=fila+2, column=1, value=zcoord[fila])
        for columna in np.arange(xcoord.size):
            hoja.cell(row=fila+2, column=columna+2, value=array_datos[fila,columna])

     # valores de x
    for columna in np.arange(xcoord.size):
        hoja.cell(row=1, column=columna+2, value=xcoord[columna])

    wb.save(directorio+'/'+nombre_archivo+'.xlsx')
    

def guardar_xlsx_asientos(xcoord,array_datos,directorio,nombre_archivo):
    
    # guardado en excel de los resultados de los calculos de una matriz de datos
    wb = openpyxl.Workbook()
    hoja = wb.active
    # valores del vector
    for columna in np.arange(xcoord.size):
        hoja.cell(row=2, column=columna+1, value=array_datos[columna])
     # valores de x
    for columna in np.arange(xcoord.size):
        hoja.cell(row=1, column=columna+1, value=xcoord[columna])

    # se crea un directorio para calculo realizado

    wb.save(directorio+'/'+nombre_archivo+'.xlsx')


def graficos_tensiones(xcoord,zcoord,tension,directorio,titulo,tipo,a,b,h):
    # representacion gráfica de los resultados en modo continuo o en isolinea
    X, Z = np.meshgrid(xcoord, zcoord)
    fig, ax = plt.subplots()

    # grafica del terraplen
    x = [-b,-(b-a),0,b-a,b]
    y=[0,h,h,h,0]
    plt.plot(x,y)

    # grafias de tipo contorno o isolineas
    if tipo=='isolinea':
        # suelo del terraplen
        x = [min(xcoord),max(xcoord)]
        y=[0,0]
        plt.plot(x,y)
        # grafica de isolinea
        curvas=plt.contour(X,-Z,tension,10)
        plt.clabel(curvas, inline=1,fmt='%2.1f',fontsize=8) # etiquetas
    else:
        curvas=plt.contourf(X,-Z,tension,10)
        plt.colorbar(curvas)
    ax.set_aspect('equal', adjustable='box')
    #ax.invert_yaxis()
    plt.xlabel("x [m]")
    plt.ylabel("z [m]")
    ax.set_title(titulo+' [kN/m2]')
    plt.savefig(directorio+'/'+titulo+tipo+".png") # guardado de la imagen
    #plt.show()


def grafico_asientos(xcoord,asiento,directorio,titulo):
    
    fig, ax = plt.subplots()

    # grafica del terraplén
    #x = [-b,-(b-a),0,b-a,b]
    #y=[0,h,h,h,0]
    #plt.plot(x,y)

    # linea horizontal
    #x = [min(xcoord),max(xcoord)]
    #y=[0,0]
    #plt.plot(x,y)

    # trazado de los asientos
    plt.plot(xcoord,np.multiply(asiento,1),marker='*',color='darkred',linestyle='-')
    ax.set_aspect('auto', adjustable='box')
    #ax.invert_yaxis()
    plt.xlabel("x [m]")
    plt.ylabel("asiento [m]")
    ax.set_title(titulo)
    #ax.set_aspect('equal', adjustable='box')
    plt.savefig(directorio+'/'+titulo+".png") # guardado de la imagen
    #plt.show()
