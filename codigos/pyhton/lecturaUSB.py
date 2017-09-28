#!/usr/bin/python


# este codigo es el encargado del almacenamiento de datos enviados por el arduino nano correspondiente al equipo que toma la respiracion
# lee todos los datos que le envia el arduino via  bluetooth con una frecuencia de aproximadamente 12 hz 
# el programa va almacenando los valores recibidos por el bluetooth que se encuentra en la raspberry, estos valores se almacenana en una lista 
# y al mismo tiempo se almacenan en un archivo .txt llamado archivo5.txt
# se usan las funciones de la libreria time para saber si han pasado 60 segundos, esto con el fin de que cuando ya hayan pasado 60 segundos se va a 
# pasar los datos almacenados en la lista a un archivo .txt llamado respiracion1min.txt, este archivo es el que va a ser procesado para calcular la 
# frecuencia respiratoria en un minuto

import numpy as np
from StringIO import StringIO
import serial
from numpy import array
import time
import RPi.GPIO as GPIO 
import subprocess
import sys

## primero establecemos la configuración de los pines GPIO para poder ubicar un led el cual va a servir de indicador cuando entre a diferentes métodos
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# se usará el pin 25 para ubicar el led
GPIO.setup(25,GPIO.OUT)
GPIO.output(25,GPIO.LOW)
# se abren los archivos en donde se van a almacenar los datos recibidos , en este caso respiracion1min que contiene los datos 
#almacenados en un minutos y son los que se van a pasar para ser procesados, archivo5 contiene todos los datos que le llegan 
#durante toda la transmisión
f1=open('/home/pi/respiracion1min.txt','w+')
f22=open('/home/pi/archivo5.txt','w+')
# en la variable response se va a almacenar los datos
response=''
# en lista se almacenaran los datos temporalmente(durante 1 minuto) para luego pasarlos al alrchivo2
lista=[]
cont=0
# se abre el puerto USB para poder recibir los datos, el bluettoh está conectado a un adaptaror que pasa de serial a USB esto con el fin de conectar
#un segundo modulo bluettoh yq que  la raspberry solo posee por defecto un puerto GPIO tanto para tx y rx
# se establece una velocidad de 9600 y un timeout de 500
ser=serial.Serial('/dev/ttyUSB0',9600,timeout=1000)
# abrimos el puerto serial
ser.open()
# se da inicio a la toma de tiempo
start=time.time()
# se hace un cilo infinito  para que se esté leyendo continuamente el puerto USB
while True:
# en la vairable response se almacena el dato recibido, el programa va a esperar el tiempo que se ha establecido en timeout, si durante ese tiempo
# no ha recibido nada pasa a la siguiente línea de código lo que va a dejar un espacio en el archivo txt 
# se hace uso de rstrip('\n') para eliminar el salto de linea que agrega arduino en el dato recibido
 response=ser.readline().rstrip('\n')
# encendemos el led para indicar que ya se esta procediendo a la toma de
 GPIO.output(25,GPIO.HIGH)
# se escribe en el archivo4.txt el dato recibido por el puerto serial
 f22.write(response)
# se almacena en la lista el valor recibido 
 lista.insert(cont,response)
 cont=cont+1
# se determina el tiempo para posteriormente ver si han pasado 60 swgundos despues de que se dio inicio al reloj
 end=time.time()
 tiemp=end-start
# si han pasado 60 segundos  se procede a almacenar los datos en archivo2, se lo contrario se sigue tomando datos
 if(tiemp>60):
  print "pasaron 60 segundos"
  indice=0
# abrimos el archivo2.txt para almacenar los datos
  f1=open('/home/pi/respiracion1min.txt','w+')  
# creamos un ciclo para poder copiar los datos que están almacenados en la lista 
  for indice in range(3,cont):
   f1.write(lista[indice])
  cont=0 
# se hace le procedimiento para borrar los datos que estan en el otro txt
  f1.close()
 # abrimos un subproceso el cual es el encargado de procesar los datos almacenados en el archivo2.txt este es llamado respiracion.py
  process4=subprocess.Popen('/home/pi/respiracion.py')
 # vaciamos la memoria cache del puerto serial
  ser.flushInput()
 # vaciamos todo el contenido de la lista
  del lista[:]
# damos inicio de nuevo al tiempo 
  start=time.time()
