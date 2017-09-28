#! /usr/bin/python

# este codigo es el encargado de dar inicio y fin a todos los otros programas encargados de la toma de senales tanto de la respiracion como
# de la senal de electrocardiografia, este es el primer codigo que se ejecuta en la raspberry el cual de acuerdo a los valores ingresados
#desde el teclado dara inicio o fin a la toma de datos, todo esto se basa en el uso de subprocesos para poder permitir que mientras se ejecuta un
# codigo se este ejecutanto otro

import subprocess
import os
import signal
import time
import sys
import RPi.GPIO as GPIO


# se establece una configuracion inicial para los datos pines GPIO los cuales tienen conectados led que sirven como indicadores
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26,GPIO.OUT)
GPIO.setup(25,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)
GPIO.output(16,GPIO.LOW)
GPIO.output(25,GPIO.LOW)
# se establece la variable tecla_ini en la cual se va a almacenar el valor ingresado desde el teclado
tecla_ini=0
# en este caso para dar inicio a la toma de datos se debe ingresar desde el teclado el numero 90
while tecla_ini!=90:
# mientras no se ingrese 90 el programa no se va a salir del ciclo while y se va a permanecer encendido un led
 GPIO.output(26,GPIO.HIGH)
 tecla_ini=input()

 # cuando se ingresa 90 se sale del cilo while y se apaga el led 
GPIO.output(26,GPIO.LOW)

# se proceden a abrir los archivos que se van a usar para almacenar la frecuencia cardiaca,frecuencia respiratoria,la HRV y la cantidad
# de picos detectados, esto se hace aqui ya que si se hace en los archivos que procesan los datos cada minuto se van a sobreescribir 
# y los datos anteriores se perderian
file1=open('/home/pi/picos.txt','w+')
file1.write("picos detectados")
file2=open('/home/pi/cardiaca.txt','w+')
file2.write("frecuencia cardiaca")
file3=open('/home/pi/hrv.txt','w+')
file3.write("variabilidad de la frecuencia cardiaca")

file4=open('/home/pi/respiratoria.txt','w+')
file4.write("frecuencia respiratoria")

file5=open('/home/pi/episodiosHipap.txt','w+')
file5.write("Episodios Hipapnea")

file6=open('/home/pi/episodiosApnea.txt','w+')
file6.write("Episodios Apnea")


file4.close()
file1.close()
file2.close()
file3.close()
file5.close()
file6.close()

# se procede a abrir los subprocesos que dan inicio a la toma de datos, en este caso el subproceso lectura.py da inicio a la toma de datos de
# la senal de cardiaca y el subproceso lecturaUSB.py da inicio a la toma de la senal de respriracion
process=subprocess.Popen('/home/pi/lectura.py',preexec_fn=os.setsid)
print "-------  abierto subproceso lectura  --------"
process2=subprocess.Popen('/home/pi/lecturaUSB.py',preexec_fn=os.setsid)
print "--------  abierto subproceso lecturaUSB  ---------"

clave=0
# se define otro ciclo por medio del cual se espera que desde el teclado se ingrese el numero 94, si se ingresa este numero 
# el programa procede a cerrar los otros subprocesos que abrio anteriormente, esto es posible ya que el proceso principal.py es el proceso padre
# lo que le da permisos para cerrar todo lo que en el se haya abienrto
while clave!=94:
# el programa se va a mantener en este ciclo mientras el usuario no ingrese 94
 clave=input()

# cuando ya ingresa desde el teclado 94 ya procede a matar los subprocesos abiertos dando fin a la toma de datos tanto de la senal respiratoria como
# de la senal de electrocardiografia
os.killpg(os.getpgid(process.pid),signal.SIGTERM)
os.killpg(os.getpgid(process2.pid),signal.SIGTERM)
#process.kill()
#process6.kill()
print "procesos finalizados"
# se hace uso de un led para avizar que ya se han cerrado los procesos, este parpadeará dos veces.
GPIO.output(26,GPIO.LOW)
time.sleep(1)
GPIO.output(26,GPIO.HIGH)
time.sleep(2)
GPIO.output(26,GPIO.LOW)

# se coloca otro ciclo el cual espera a aque el usuario de la orden para apagar la raspberry ya que no se posee de un boton externo que apague 
# la tarjeta correctamente por lo tanto se hace a partir de otro subproceso
# el usuario una vez ha visto que el led correspondiende ha titilado con la secuencia correspondiente que indica que ha cerrado los subprocesos
# puede ingresar el numero 10, el cual le indicara a la tarjeta que se debe apagar
power=0
while power!=10:
 power=input()

processFInal=subprocess.Popen('poweroff',shell=True)
exit(0)
