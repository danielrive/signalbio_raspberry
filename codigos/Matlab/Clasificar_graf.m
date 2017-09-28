clc
clear all
%% Script creado para efectos de analisis y visualizacion de los asesores

%Se cargan las variables fisiologicas con los valores registrados
frec_car= load ('frec_cardiaca.txt');
frec_res= load ('frec_respiratoria.txt');
hrv= load ('hrv.txt');
iah= load ('iah.txt');

X = [iah,frec_res,hrv,frec_car];% Se forma la matriz de entrenamiento
[numInst,numDims] = size(X);
Xa = zeros(numInst,(numDims-1));%Futura matriz normalizada
%Ciclo que normaliza la matriz y la carga en Xa
for i=1:(numDims-1)
    Xa(:,i)=X(:,i)/norm(X(:,i));
end

K=2;
[Ga,Ca,~,D] = kmeans(Xa, K ,'distance','sqEuclidean', 'start','sample','replicates',5);% Implementacion del algoritmo con replicas
Ga

% se grafican los puntos y cluster (color-coded)
clr = lines(K);
figure(1), hold on
axis equal;
scatter3(Xa(:,1), Xa(:,2), Xa(:,3), 36, clr(Ga,:), 'Marker','.')
scatter3(Ca(:,1), Ca(:,2), Ca(:,3), 100, clr, 'Marker','o', 'LineWidth',3)
hold off
title('Grupos asignados por K-Means con FC = 60');
view(3), axis vis3d, box on, rotate3d on
xlabel('IAH Normalizado'), ylabel('FR Normalizada'), zlabel('HRV Normalizada')
Verdadero = load('agrupacion.txt')

%%%%%%%%%%%%%%%%%%%%% Fase de verificacion %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Usando el algoritmo , se clasifica cada muestra de X
% El algoritmo de clasificación es correcto si G = Gp

n = numInst; % Número de muestras en X
Gp = zeros(n,1); % Inicia el vector Gp
for j = 1:n
    Gp(j) = clasificador(Ca,Xa(j,:)); % Clasifica la muestra j y la almacena 
                                    % en Gp(j)
end    
if Gp-Ga == 0 % Todas las muestras clasificadas coinciden con el resultado de kmeans
    disp('Clasificador OK')
else
    disp('Clasificador incorrecto')
end


