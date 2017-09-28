#! /usr/bin/python
# procesamiento


# este codigo es el encargado de procesamiento de la senal de respiracion recibida durante un minuto,al final el programa calcula la frecuencia
#cardiaca, esto lo almacena en un archivo txt
# se hace uso de las funciones que provee scipy y numpy los cuales permiten trabajar sobre senales

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy import linalg, optimize 
import scipy.io as sio
from scipy.fftpack import fft
from scipy import signal,misc
import scipy.fftpack
from scipy import stats
from subprocess import Popen
import time
import sys

# la version de scipy que posee la raspberry no contiene la funcion del filtro de media movil el cual permite suavizar la senal a partir de 
# el calculo del promedio de los diferentes valores que se le indiquen, este filtro es de gran utilidad ya que permite que la senal no tenga
# picos tan pronunciados suavizando asi la curva
# al no tener scipy esta funcion incluida se debe implementar el filtro en una funcion, la funcion correspondiente a este filtro fue copiada de 
# los tutoriales y ayudas que se ofrecen en los foros de scipy y numpy.


###########################################################################
########### funcion para el filtro de media movil   INICIO   ##############
###########################################################################
def savitzky_golay(y, window_size, order, deriv=0, rate=1):

    from math import factorial

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')
############################################################################
###############  FIN FUNCION DEL FILTRO DE MEDIA MOVIL     #################
############################################################################


# definimos la frecuencia de muestreo
fs=10.0
# definimos el periodo de muestreo
pas=(1.0/fs)
#cargamos los datos del archivo txt
data=np.loadtxt('/home/pi/respiracion1min.txt')
#definimos el eje de tiempo
#para ello hay que saber la cantidad de datos que se han tomado
x2=data.size
ejet=np.arange(0,((x2)*pas),pas)
# definimos el eje de frecuencias
ejefrec=np.arange(0,(x2/(x2*pas)),(1/(x2*pas)))

#se calcula es espectro de la senal
spectr=np.absolute(fft(data))
espectro=np.absolute(fft(data))

# la senal entregada por el equipo encargado de la toma de la respiracion no necesita ser pasada por ningun filtro pasa altas ni pasa bajas
# solo se pasa por un filtro de media movil para suavizar la senal

###### FILTRO PROMEDIADOR #########
#senal_filtrada=savitzky_golay(senal_filtrada1,3,2)
final_signal=savitzky_golay(data,11,1)


# se procede a eliminar todos los valores que estan por debajo de cero ya que no son relevantes
for indice in range(0,final_signal.size):
  if(final_signal[indice]<0):
     final_signal[indice]=0

rms=np.sqrt(np.mean(np.square(final_signal)))
###################################
####### INICIO PICOS MANUAL ######
###################################
contador=0
contador2=0
contador3=0
inicio=0
final=10
array_extra=[]
maximos=[]
pos_maximos=[]
pos_maximos_tiempo=[]
maximo=0.0
indice3=0
#rms=np.sqrt(np.mean(np.square(senal_filtrada)))
for indice3 in range(inicio,final):
 array_extra.insert(contador2,0)
 contador2=contador2+1


###################################################################################
############    PROCEDIMIENTO PARA DETECCION DE PICOS        ######################
###################################################################################
while(final<=final_signal.size):
 contador2=0
 for indice2 in range(inicio,final):
  array_extra[contador2]=final_signal[indice2]
  contador2=contador2+1
  
 maximo=np.max(array_extra)
 lugar=np.argmax(array_extra)+inicio
 contador2=0
 inicio=final
 final=final+10
 

 if(maximo>rms*0.8):
  maximos.insert(contador,maximo)
  pos_maximos.insert(contador,lugar)
  contador=contador+1

###################################################################################
###########   procedimiento para eliminar picos muy juntos     ####################
###################################################################################
i=0  
j1=0
j2=0
j3=0
cont=0

while(i!=(len(maximos))-1): 
 j1=pos_maximos[i+1]-pos_maximos[i]
 j2=maximos[i+1]
 j3=maximos[i]
 if(j1<21):
  if( j2>j3): 
   maximos.pop(i)
   pos_maximos.pop(i)
  else:
   maximos.pop(i+1)
   pos_maximos.pop(i+1)
  i=i-1 
 i=i+1
media=np.mean(maximos)

t=0
tiemp=0
for t in range(0,len(pos_maximos)):
 tiemp=(pos_maximos[t])/(fs)
 pos_maximos_tiempo.insert(t,tiemp)

##################################################################
######        CALCULO DE LA FRECUENCIA RESPIRATORIA        #######
##################################################################
print "****                                                   ******"
print "*************************************************************"
print "****************  frecuencia respiratoria *******************"
print "*************************************************************"
print len(maximos) 
print "*************************************************************"
print "*************************************************************"
file1=open('/home/pi/respiratoria.txt','a')
file1.write('\n')
file1.write(str(len(maximos)))
#######################################################################
########################################################################
###############           CALCULO DEL IAH      ########################
######################################################################
numApnea=0  # en esta variable se almacena la cantidad de episodios de apnea
numHipap=0  # en esta variable se almacena la cantidad de episodios de hipopn
distancia_picos=np.diff(pos_maximos)*(pas) # distancia entre picos
indice=0
for indice in range(0,len(distancia_picos)):
 j=distancia_picos[indice]
 if(j >=10):
  numApnea=numApnea+1

picos_mitad=[]
indice=0
maximos.insert(contador,maximo)
for indice in range(0,len(maximos)):
 picos_mitad.insert(contador,maximos[indice]*0.5)
 
for indice in range(0,len(picos_mitad)-1):
 if(maximos[indice+1]<=picos_mitad[indice]):
  numHipap=numHipap+1

file2=open('/home/pi/episodiosHipap.txt','a')
file2.write('\n')
file2.write(str(numHipap))

file3=open('/home/pi/episodiosApnea.txt','a')
file3.write('\n')
file3.write(str(numApnea))
 
file1.close()
exit(0)
