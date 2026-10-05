\
# Fuentes y decisiones metodológicas

## IHH y umbrales de la pregunta educativa

Fiscalía Nacional Económica (FNE), *Guía para el Análisis de Operaciones de Concentración Horizontales* (2022), párrafos 35–36.

La guía expresa los tramos como:

- IHH inferior a 1500;
- IHH superior a 1500 e inferior a 2500: mercado moderadamente concentrado (sujeto además a la condición de ΔIHH indicada por la guía);
- IHH superior a 2500: mercado altamente concentrado (también sujeto a la condición de ΔIHH indicada por la guía).

El párrafo 36 indica que la FNE analizará con mayor detención operaciones en mercados que igualen o sobrepasen los umbrales referidos. Por ese motivo, esta aplicación ofrece la respuesta **“Está exactamente en un umbral”** cuando el IHH es exactamente 0,15 o 0,25.

La etiqueta **“Baja concentración”** es una etiqueta pedagógica de esta aplicación para el tramo inferior al primer umbral; no se presenta como una cita literal de la FNE.

## Generación aleatoria y Monte Carlo

Los mercados aleatorios se generan con una distribución Dirichlet simétrica `Dirichlet(1, …, 1)`. Cada vector generado contiene participaciones positivas que suman 1; la aplicación las muestra como porcentajes que suman 100 %.

## Entropía

Se usa la fórmula `E = -Σ s_i ln(s_i)` con logaritmo natural y la convención matemática `0 ln(0) = 0`.
