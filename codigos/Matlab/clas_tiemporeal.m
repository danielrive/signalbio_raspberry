clc
clear all
%% Simulacion de la logica del algoritmo para su posterior implementacion en tiempo real 

%Se cargan las variables fisiologicas con los valores registrados 
load promedios.txt; %vector que entrega las variables finales que describen el sueño del paciente

frec_car= load ('frec_cardiaca.txt');
frec_res= load ('frec_respiratoria.txt');
hrv= load ('hrv.txt');
iah= load ('iah.txt');

% Se forma la matriz de entrenamiento
X = [iah,frec_res,hrv,frec_car];
C = [0.3852 0.3106 0.3186 0.3175; 0.1498 0.3210 0.3111 0.3121]; %se cargan los centroides normalizados
Xm = [promedios(4,1),promedios(3,1),promedios(2,1), promedios(1,1)];% se arma el vector del paciente
[numPac Dim]= size(Xm);

%Se normaliza la muestra para poder establecer el grupo
for i = 1:Dim
    Xn(:,i)=Xm(:,i)/norm(X(:,i));
end

Gr = clasificador(C,Xn);
Gr
