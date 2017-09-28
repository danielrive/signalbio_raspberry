
clc
clear all
%Se cargan las variables fisiologicas con los valores registrados 
frec_car= load ('frec_cardiaca.txt');
frec_res= load ('frec_respiratoria.txt');
hrv= load ('hrv.txt');
iah= load ('iah.txt');

X = [iah,frec_res,hrv,frec_car];% Se forma la matriz de entrenamiento
Xn = zeros(size(X)); %Futura matriz normalizada
[numPac,numVar] = size(X); %Dimensiones de la matriz X


for i = 1:numVar
    Xn(:,i)=X(:,i)/norm(X(:,i));
end
%% Implementacion de Kmeans
K = 2;
[G,C,~,D] = kmeans(Xn, K, 'distance','sqEuclidean', 'start','sample','replicates',5); % Implementacion del algoritmo con replicas

figure(2)
[silh3,h]= silhouette(Xn,G,'sqEuclidean');%comando silhouette para analizar la adaptacion a cada cluster
h=gca;
h.Children.EdgeColor = [.8 .8 1];
xlabel 'Indicador de Separabilidad'
ylabel 'Pacientes - Grupo Asignado'
G
Verdadero = load('agrupacion.txt') 

%% Fase de verificacion 

% Usando el algoritmo, se clasifica cada muestra de X
% y se almacena el resultado en Gp.
% El algoritmo de clasificación es correcto si G = Gp

n = numPac; % Número de muestras en X
Gp = zeros(n,1); % Inicia el vector Gp
for j = 1:n
    Gp(j) = clasificador(C,Xn(j,:)); % Se llama a la funcion clasificador 
end    
if Gp-G == 0 % Si Todas las muestras clasificadas coinciden con el resultado de kmeans
    disp('Clasificador OK')
else
    disp('Clasificador incorrecto')
end


