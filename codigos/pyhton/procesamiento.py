#! /usr/bin/python
# procesamiento

# este codigo es el encargado de procesamiento de la senal recibida durante un minuto,al final el programa calcula la frecuencia cardiaca, la
# cantidad de picos detectados en un minuto y la variablilidad de la frecuecia cardiaca, todo esto lo almacena en diferentes archivos txt
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
import RPi.GPIO as GPIO 

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


# se hace la configuracion inicial de los pines GPIO con el fin de saber a partir de su encendido cuando esta procesando la senal

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(16,GPIO.OUT)
GPIO.output(16,GPIO.LOW)

# definimos la frecuencia de muestreo
fs=170.0
# definimos el periodo de muestreo
pas=(1.0/fs)
#cargamos los datos del archivo txt
data=np.loadtxt('/home/pi/archivo2.txt')
#definimos el eje de tiempo para ello hay que saber la cantidad de datos que se han tomado
x2=data.size
ejet=np.arange(0,((x2)*pas),pas)
# definimos el eje de frecuencias
ejefrec=np.arange(0,(x2/(x2*pas)),(1/(x2*pas)))

i=0
# con el siguiente ciclo se eliminan valores demasiado grandes que se hayan leido o escrito en los achivos por error, el electrocardiografo entrega
# valores generalmente entre 100 y 1000 por eso los valores que esten en otros rangos son eliminados
while i!=(len(data)-3):
 if(data[i]>1000 or data[i]<100):
  data=np.delete(data,i)
 i=i+1

#pasamos la senal por un filtro de media movil
data_suav=data
#se calcula es espectro de la senal suavizada para poder ver las frecuencias que externas que pueden estar afectando la medida
# por lo general la senal de ecg tiene su  mayor informacion distribida entre 0 y 40 hz
spectr=np.absolute(fft(data_suav))


###########################################
####      ETAPA DE  FILTRADO          #####
########################################### 

# se disena un filtro pasa altas para poder eliminar el valor dc y tratar de atenuar frecuencias  muy bajas que de acuerdo a la 
# literatura afecta a la senal para los propósitos que se buscan aqui
# se va a usar un filtro eliptico pasa altas que provee scipy
wl1=(2.0)*(1.0)/(fs)
wl2=(2.0)*(0.00001)/(fs)
N2,Wn2=signal.ellipord(wl1,wl2,9.0,10.0)
b1,a1=signal.ellip(N2,9.0,10.0,Wn2,'high')
w1,h1=signal.freqz(b1,a1,fs)
# elaborado el filtro se procede a pasar la senal por este
senal_high=signal.lfilter(b1,a1,data_suav)

#se comienza el diseno del filtro pasabajas usando un filtro eliptico, la senal de ecg tiene su mayor informacion entre 0 y 40 hz, el filtro
#pasabajas es usado con el fin de eliminar todas las componentes que esten por encima de 40 hz, adempas permite eliminar el ruido introducido
# por las lineas de alimentacion que afecta las frecuencias de 50 y 60 hz
wp1=(2.0)*(30.0)/(fs)
wp2=(2.0)*(40.0)/(fs)
N,Wn=signal.ellipord(wp1,wp2,0.01,100.0)
b,a=signal.ellip(N,0.01,100.0,Wn)
w,h=signal.freqz(b,a,fs,0)
#disenado el filtro se hace pasar la senal por el
senal_filtrada1=signal.lfilter(b,a,senal_high)
# para mejorar la calidad de la senal se procede a pasar esta por un filtro de media movil el cual ayuda a suavizar la senal de acurdo al
# grado del polinomio que se le de y al tamano de la ventana que se le ingrese, se usa la funcion savitzky_golay que es la que se ha definido 
# al inicio de este codigo
senal_filtrada=savitzky_golay(senal_filtrada1,5,1)

# se calcula el espectro de la senal para ver que se eliminen las componentes y comprobar que los filtros estan funcionando correctamente
spectr_filt=np.absolute(fft(senal_filtrada))


#en la literatura se han desarrollado diferentes algoritmos que permite procesar adecuadamente la senal, en este caso se va a usar la transformada 
# de hilbert la cual es un paso para sacar la envolvente de la senal deseada y poder asi determinar los picos R que son los interesados en este caso
# el algoritmo recomienda primero derivar la senal para poder determinar los maximos y los minimos por eso es necesario que la onda T de la senal de 
# ECG se haya atenuado lo maximo posible con el fin de que no se vaya a detectar como una onda R, para eso es que se hace la etapa de filtrado

#se pasa a hacer la derivada de la senal
#der=(1/pas)*(np.diff(senal_filtrada))
der=(1/pas)*(np.gradient(senal_filtrada))
#se realiza la transformada de hilbert
hilbert_signal=np.imag(signal.hilbert(der))

#se hace uso de nuevo de el filtro me media movil para poder suaivzar la senal
hilbert2=savitzky_golay(hilbert_signal,7,2)

# se calcula la envlvente de la senal
factor1=(hilbert2)*(hilbert2)
factor2=(senal_filtrada)*(senal_filtrada)
envolvente_signal=np.sqrt(np.absolute(factor1+factor2))
signal_final=savitzky_golay(envolvente_signal,7,3)
#signal_final=envolvente_signal


#####################################################################
##########################################################
##############################################
# en el siguiente ciclo se eliminan todas las componentes que estan por debajo de cero con el fin de facilitar la deteccion de los picos ya que
# esas componentes pueden afectar en la deteccion de los picos  
for indice in range(0,hilbert2.size):
  if(hilbert2[indice]<0):
     hilbert2[indice]=0

# la deteccion de los picos se puede hacer implementando funciones ya definidas por scipy pero como la version que posee la raspberry de scipy
# no se puede implementar dichas funciones por lo tanto para la deteccion de picos se diseno un algoritmo especial para esto el cual se basa 
# en el calculo de los maximos en una cantidad de muestras determinada, la ventana de muestras se va corriendo hasta recorrer todos los datos
# obtenidos y los maximos que haya encontrado se almacenan en una lista, luego ya se hacen procesos de eliminacion de los maximos que no son deseados
# para esto se tienen en cuenta la separacion entre ellos y la amplitud  

###################################
####### INICIO PICOS MANUAL ######
###################################
contador=0
contador2=0
contador3=0
inicio=0
final=35
array_extra=[]
maximos=[]
pos_maximos=[]
pos_maximos_tiempo=[]
maximo=0.0
indice3=0
rms=np.sqrt(np.mean(np.square(hilbert2)))
for indice3 in range(inicio,final):
 array_extra.insert(contador2,0)
 contador2=contador2+1

###################################################################################
############    PROCEDIMIENTO PARA DETECCION DE PICOS        ######################
###################################################################################
while(final<=hilbert2.size):
 contador2=0
 for indice2 in range(inicio,final):
  array_extra[contador2]=hilbert2[indice2]
  contador2=contador2+1
  
 maximo=np.max(array_extra)
 lugar=np.argmax(array_extra)+inicio
 contador2=0
 inicio=final
 final=final+35
# los picos detectados se descartan de acuerdo al valor RMS de toda la senal, este permite eliminar picos no deseados ya que todos deben estar
# por encima de ese valor para poder ser almacenados en la lista
 if(maximo>rms):
  maximos.insert(contador,maximo)
  pos_maximos.insert(contador,lugar)
  contador=contador+1

media=np.mean(maximos)

###################################################################################
###################################################################################


#los picos de las ondas R por lo general tienen una amplitud igual por eso se calcula la media de todos los picos determinados y se descartan los que
# esten por debajo del 95 % de esa media y los que esten 350% por encima de esa media ya que se consideran como errores

###################################################################################
######## procedimiento para eliminar los valores que son menores del 70% ##########
###################################################################################
cont=0
i=0
while(i!=(len(maximos))): 
 j=maximos[i]
 if(j<0.95*media or j>3.5*media):
  maximos.pop(i)
  pos_maximos.pop(i)
  i=i-1
   
 i=i+1


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
 if(j1<35):
  if( j2>j3): 
   maximos.pop(i)
   pos_maximos.pop(i)
  else:
   maximos.pop(i+1)
   pos_maximos.pop(i+1)
  i=i-1 
 i=i+1

###################################################################################


###################################################################################
################  PROCEDIMIENTO PARA CALCULAR DISTANCIA ENTRE PICOS  ##############
###################################################################################


######################################################################
######### CALCULO DE LA VARIABILIDAD DE LA FRECUENCIA CARDIACA  ######
######################################################################

# la variabilidad de la frecuencia cardiaca se toma teniendo en cuenta intervalos de un minuto de
# toma de senales de ECG

# SE CALCULA LA DISTANCIA ENTRE PICOS
dis_peaks=np.diff(pos_maximos)*(pas)

#se calcula el promedio entre la separacion de picos

i=0
prom_sum=0
prom_dis=0
for i in range(0,len(dis_peaks)):
 prom_sum=prom_sum+dis_peaks[i]
prom_dis=(prom_sum)/(len(dis_peaks))

#####################################################################
#####  FIN CALCULO DE LA VARIABILIDAD DE LA FRECUENCIA CARDIACA #####
#####################################################################


#################################################
######   CALCULO DE LA FRECUENCIA CARDIACA ######
#################################################
# el calculo de la frecuencia cardiaca se basa en lo que dice la pagina  
# en donde dice que se deben tomar 6 segundos y mirar cuantos QRS hay en este tiempo, sabiendo eso se multiplica por 12
# la cantidad de QRS y esto nos da una aproximacion de la frecuencia cardiaca
# en este caso tomamos los datos de la frecuencia cardiaca cada 6 segudnos del total de 60 es decir que nos va a entregar
# 10 valores de frecuencia cardiaca que suceden en el minuto que se van a calcular
#luego de esto se saca un promedio de todos estos valores 


conta=0
indice5=0 
inicio=0
#final2=(len(data)*6)/(60)
final1=1017
final3=(len(data)*6)
final2=(final3/60)
final=int(final2)
final4=final
#final=int(final2)
frecar=[]
p=0
c=0
print "este es el valor de final",final
while(p<=len(pos_maximos)-1):
# print c 
 if(pos_maximos[p]<=final):
  conta=conta+1
  p=p+1
#  frecar.insert(c,conta)
 else:
  frecar.insert(c,conta)
  final=final+final4
  conta=0
  c=c+1
frecar.insert(c,conta)

promedio_frecar=0
inicio=0
promedio_frecar1=0
#print len(frecar)
for inicio in range(0,len(frecar)):
 frecar[inicio]=frecar[inicio]*10
 promedio_frecar1=promedio_frecar1+frecar[inicio]
 inicio=inicio+1


################
##############################
#######################

# por lo general la frecuencia cardiaca coicide con la cantidad de picos detectados per cuando la senal tiene mucho ruido el calculo 
# de la frecuencia cardiaca que se hace a partir de los 6 segundos falla dando en cada 6 segundo frecuencias cardiacas muy dispersas
# lo que no puede ser posible por lo tanto se ejecuta el siguiente procedimiento para determinar si ha ocurrido lo anteriormente mencionado
# lo que se hace es calcular la desviacion estandar y si es mayor que 20 se da una frecuencia cardiaca de 0 lo que indica que ha ocurrido un error
desvi=0
desvi=np.std(frecar)
if(desvi >20):
 promedio_frecar=0
else:
 promedio_frecar=(promedio_frecar1)/len(frecar)
###################################################################################
#print len(maximos)
#print len(dis_peaks)

## pasamos la posicion de los picos a valores en segundis
t=0
tiemp=0
for t in range(0,len(pos_maximos)):
 tiemp=(pos_maximos[t])/(fs)
 pos_maximos_tiempo.insert(t,tiemp)


# una vez calculada la frecuencia cardiaca, la cantidad de picos y la HRV se procede a imprimir los datos en pantalla, esto se hara cada minuto 
# de acuerdo al llamado que le haga el proceso padre que es lectura.py
#se imprimen los resultados en pantalla y se pasa a almacenar estos valores en los archivos txt mencionados en los codigos anteriores con el fin de 
# llevar el registro de cada minuto en el que estuvo en funcionamiento la toma de datos
print " xxxxxxxxxxxx                    xxxxxxxxxxxxxxxxxxx "
print " xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx "
print " xxxxxxxxxx CALCULO COMPLETADO    xxxxxxxxxxxxxxxxxxx "
print " xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx "
print "CANTIDAD DE PICOS DETECTADOS"
print len(maximos)
file1=open('/home/pi/picos.txt','a')
file1.write('\n')
file1.write(str(len(maximos)))
print "PROMEDIO DE LA FRECUENCIA CARDIACA EN UN MINUTO"
print promedio_frecar
file2=open('/home/pi/cardiaca.txt','a')
file2.write('\n')
file2.write(str(promedio_frecar))
print "PROMEDIO DISTANCIA ENTRE PICOS EN UN MINUTO"
print prom_dis
file3=open('/home/pi/hrv.txt','a')
file3.write('\n')
file3.write(str(prom_dis))
print " xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx "
print " xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx "

file1.close()
file2.close()
file3.close()
#####################################
#######     FINAL          #########
####################################
GPIO.output(16,GPIO.HIGH)
time.sleep(0.7)
GPIO.output(16,GPIO.LOW)
time.sleep(0.7)
GPIO.output(16,GPIO.HIGH)
time.sleep(0.7)
GPIO.output(16,GPIO.LOW)
exit(0)
