%%% Clasificación  %%%%
function c = clasificador(C,m)
% C(i,j): matriz de los centros de los grupos. 
% m: muestra a clasificar
% Salida: c = grupo al que pertenece la muestra m

n = 2; % Número de grupos de clasificación
d = distancia(C(1,:),m); % Distancia de la muestra al centro del grupo 1
c = 1; % El grupo inicial al que pertenece la muestra es al grupo 1

for j = 2:n
    dn = distancia(C(j,:),m); % Distancia de la muestra al centroide del grupo j
    if dn < d
        d = dn; % La distancia mas cercana es al grupo j
        c = j;  % El grupo mas cercono a la muestra es el j
    end
end

function d = distancia(v1,v2)
% Distancia euclidiana (al cuadrado para no sacar raiz cuadrada)
n = 4; % Número de elementos de los vectores
d = 0;
for j = 1:n
    d = d+(v1(j)-v2(j))*(v1(j)-v2(j));
end