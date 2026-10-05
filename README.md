\
# Aplicación de concentración de mercado

Proyecto en Python + Streamlit para calcular y explorar medidas de concentración de mercado.

## Qué hace la aplicación

1. Permite elegir entre **2 y 100 empresas**.
2. Permite escribir cuotas manualmente (0 % a 100 %) o generar un mercado aleatorio con una distribución **Dirichlet(1, …, 1)**.
3. Valida que las cuotas sumen 100 %.
4. Calcula **CRk**, **IHH** (escala 0–1), **índice de dominancia de Pascual García Alba** e **índice de entropía**.
5. Ejecuta una simulación Monte Carlo de **100 a 50.000 repeticiones**; el valor inicial es 1.000 y aparece una advertencia por encima de 10.000.
6. Permite elegir uno de los cuatro indicadores y ver su distribución simulada, la marca del mercado observado y su percentil.
7. Incluye una pregunta educativa para interpretar el IHH.

## Archivos

- `app.py`: interfaz Streamlit.
- `indicadores.py`: validación y fórmulas.
- `simulacion.py`: generación Dirichlet, Monte Carlo y percentiles.
- `graficos.py`: histogramas y explicación del percentil.
- `pregunta.py`: lógica de la pregunta educativa.
- `requirements.txt`: bibliotecas necesarias.
- `tests/`: pruebas automáticas.

## Referencia de la pregunta educativa

Se usa como referencia la **Fiscalía Nacional Económica (FNE), Guía para el Análisis de Operaciones de Concentración Horizontales (2022), párrafos 35–36**.

En la escala 0–1 usada por esta aplicación:

- `IHH < 0,15` → **Baja concentración** (etiqueta pedagógica usada por la aplicación para el tramo bajo el primer umbral).
- `0,15 < IHH < 0,25` → **Concentración moderada**.
- `IHH > 0,25` → **Alta concentración**.
- `IHH = 0,15` o `IHH = 0,25` → **Está exactamente en un umbral**.

La FNE utiliza además la variación del IHH (ΔIHH) y otros elementos en su análisis de operaciones de concentración. La pregunta de esta aplicación es una actividad pedagógica sobre el nivel del IHH y no sustituye ese análisis.

Referencia oficial: https://www.fne.gob.cl/fusiones/normativa-guias-y-formularios/

## Instalación (cuando estén listos para probarla)

Se recomienda Python 3.11 o 3.12.

Desde una terminal, dentro de la carpeta del proyecto:

```bash
python -m venv .venv
```

Activar el entorno virtual:

**Windows (PowerShell):**

```powershell
.venv\\Scripts\\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

Ejecutar la aplicación:

```bash
python -m streamlit run app.py
```

## Pruebas automáticas

Opcionalmente, pueden ejecutar:

```bash
python -m unittest discover -s tests -v
```

Estas pruebas revisan los indicadores, las simulaciones, los gráficos, la pregunta educativa y el flujo central entre los módulos.

## Avisos de rendimiento

La sección Monte Carlo muestra siempre una nota indicando que aumentar las
repeticiones incrementa el trabajo computacional, la latencia de respuesta
y el uso de CPU/memoria.

- 100–10.000 repeticiones: se muestra la nota informativa.
- Más de 10.000: se añade una advertencia de carga alta.
- Más de 25.000: se muestra una advertencia de carga muy alta.
- Máximo permitido: 50.000 repeticiones.

Estos mensajes no bloquean la simulación; ayudan a la persona usuaria a
decidir entre rapidez y cantidad de repeticiones.
