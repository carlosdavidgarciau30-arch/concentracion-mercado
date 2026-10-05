"""
Generación aleatoria de mercados y simulación Monte Carlo.

Decisiones del proyecto
-----------------------
- N = número de empresas, entre 2 y 100.
- R = número de repeticiones Monte Carlo, entre 100 y 50.000.
- R comienza en 1.000.
- Las cuotas aleatorias se generan con una distribución
  Dirichlet(1, ..., 1).
- Cada mercado generado tiene cuotas no negativas cuya suma es 100 %.
"""

from numbers import Integral, Real

import numpy as np

from indicadores import calcular_indicadores


MIN_EMPRESAS = 2
MAX_EMPRESAS = 100

MIN_REPETICIONES = 100
MAX_REPETICIONES = 50_000
REPETICIONES_PREDETERMINADAS = 1_000


def validar_numero_empresas(n_empresas):
    """Comprueba que N sea un entero entre 2 y 100."""
    if isinstance(n_empresas, bool) or not isinstance(n_empresas, Integral):
        raise ValueError("El número de empresas debe ser un número entero.")

    n_empresas = int(n_empresas)

    if not MIN_EMPRESAS <= n_empresas <= MAX_EMPRESAS:
        raise ValueError(
            f"El número de empresas debe estar entre "
            f"{MIN_EMPRESAS} y {MAX_EMPRESAS}."
        )

    return n_empresas


def validar_repeticiones(repeticiones):
    """Comprueba que R sea un entero entre 100 y 50.000."""
    if isinstance(repeticiones, bool) or not isinstance(repeticiones, Integral):
        raise ValueError("La cantidad de repeticiones debe ser un número entero.")

    repeticiones = int(repeticiones)

    if not MIN_REPETICIONES <= repeticiones <= MAX_REPETICIONES:
        raise ValueError(
            f"La cantidad de repeticiones debe estar entre "
            f"{MIN_REPETICIONES} y {MAX_REPETICIONES}."
        )

    return repeticiones


def _validar_k(k, n_empresas):
    """Comprueba que k sea un entero entre 2 y N."""
    if isinstance(k, bool) or not isinstance(k, Integral):
        raise ValueError("k debe ser un número entero.")

    k = int(k)

    if not 2 <= k <= n_empresas:
        raise ValueError(
            f"k debe estar entre 2 y {n_empresas} para este mercado."
        )

    return k


def _generar_proporciones(n_empresas, cantidad, rng):
    """
    Genera una matriz de mercados en proporciones.

    Cada fila representa un mercado y suma 1.
    """
    alfa = np.ones(n_empresas, dtype=float)
    mercados = rng.dirichlet(alfa, size=cantidad)

    # Dirichlet ya genera filas cuya suma es 1. Esta normalización adicional
    # elimina pequeñas desviaciones propias del punto flotante.
    mercados = mercados / mercados.sum(axis=1, keepdims=True)

    return mercados


def generar_mercado_aleatorio(n_empresas, semilla=None):
    """
    Genera un solo mercado aleatorio.

    Retorna
    -------
    list[float]
        Cuotas expresadas como porcentajes. La suma es 100 %.

    Notas
    -----
    `semilla` es opcional y sirve para reproducir exactamente un resultado,
    especialmente útil en pruebas. La futura interfaz no necesita pedirla.
    """
    n_empresas = validar_numero_empresas(n_empresas)
    rng = np.random.default_rng(semilla)

    proporciones = _generar_proporciones(n_empresas, 1, rng)[0]
    cuotas = proporciones * 100.0

    # Ajuste numérico del último elemento para que la suma en porcentajes
    # sea exactamente 100 dentro de la representación de Python.
    cuotas[-1] = 100.0 - float(np.sum(cuotas[:-1]))

    return cuotas.tolist()


def generar_mercados_aleatorios(
    n_empresas,
    repeticiones=REPETICIONES_PREDETERMINADAS,
    semilla=None,
):
    """
    Genera muchos mercados aleatorios.

    Retorna una matriz NumPy de forma (repeticiones, n_empresas).
    Cada fila contiene porcentajes que suman 100 %.
    """
    n_empresas = validar_numero_empresas(n_empresas)
    repeticiones = validar_repeticiones(repeticiones)
    rng = np.random.default_rng(semilla)

    proporciones = _generar_proporciones(n_empresas, repeticiones, rng)
    cuotas = proporciones * 100.0

    # Ajuste fila a fila del último valor para evitar pequeñas diferencias
    # numéricas respecto de 100 %.
    cuotas[:, -1] = 100.0 - np.sum(cuotas[:, :-1], axis=1)

    return cuotas


def simular_indicadores(
    n_empresas,
    k=2,
    repeticiones=REPETICIONES_PREDETERMINADAS,
    semilla=None,
):
    """
    Ejecuta la simulación Monte Carlo y calcula los cuatro indicadores.

    La función genera `repeticiones` mercados de N empresas usando
    Dirichlet(1, ..., 1) y calcula para cada mercado:

    - CRk
    - IHH
    - índice de dominancia
    - entropía

    Los cálculos se realizan de forma vectorizada con NumPy para que
    incluso decenas de miles de repeticiones sean razonablemente rápidas.

    Retorna
    -------
    dict
        Contiene N, R, k y un arreglo con los resultados simulados de cada
        indicador.
    """
    n_empresas = validar_numero_empresas(n_empresas)
    repeticiones = validar_repeticiones(repeticiones)
    k = _validar_k(k, n_empresas)

    rng = np.random.default_rng(semilla)
    mercados = _generar_proporciones(n_empresas, repeticiones, rng)

    # CRk: ordenar cada mercado y sumar las k cuotas más grandes.
    ordenadas = np.sort(mercados, axis=1)
    crk = np.sum(ordenadas[:, -k:], axis=1)

    # IHH.
    cuadrados = mercados ** 2
    ihh = np.sum(cuadrados, axis=1)

    # Índice de dominancia de Pascual García Alba.
    dominancia = np.sum(mercados ** 4, axis=1) / (ihh ** 2)

    # Entropía. Dirichlet produce cuotas positivas, pero dejamos el cálculo
    # preparado de forma segura ante un eventual cero numérico.
    log_mercados = np.zeros_like(mercados)
    np.log(mercados, out=log_mercados, where=mercados > 0)
    entropia = -np.sum(mercados * log_mercados, axis=1)

    return {
        "n_empresas": n_empresas,
        "repeticiones": repeticiones,
        "k": k,
        "crk": crk,
        "ihh": ihh,
        "dominancia": dominancia,
        "entropia": entropia,
    }


def calcular_percentil(valor_observado, valores_simulados):
    """
    Calcula el percentil empírico de un valor observado.

    El resultado es el porcentaje de simulaciones cuyo valor es menor
    o igual que el valor observado.

    Ejemplo:
    un percentil 88 significa que aproximadamente el 88 % de las
    simulaciones produjo un valor menor o igual al observado.
    """
    if isinstance(valor_observado, bool) or not isinstance(valor_observado, Real):
        raise ValueError("El valor observado debe ser numérico.")

    valores = np.asarray(valores_simulados, dtype=float)

    if valores.ndim != 1 or valores.size == 0:
        raise ValueError(
            "Los valores simulados deben ser una colección no vacía y unidimensional."
        )

    if not np.all(np.isfinite(valores)):
        raise ValueError("Los valores simulados deben ser finitos.")

    valor_observado = float(valor_observado)

    if not np.isfinite(valor_observado):
        raise ValueError("El valor observado debe ser finito.")

    return float(100.0 * np.mean(valores <= valor_observado))


def comparar_mercado_con_simulacion(cuotas, k, resultados_simulacion):
    """
    Compara un mercado particular con una simulación ya ejecutada.

    Retorna sus indicadores observados y el percentil de cada indicador.
    La interpretación del percentil de entropía se hará después en la
    interfaz, porque un percentil alto de entropía significa mayor equilibrio,
    no mayor concentración.
    """
    observado = calcular_indicadores(cuotas, k=k)

    if observado["n_empresas"] != resultados_simulacion["n_empresas"]:
        raise ValueError(
            "El mercado observado y la simulación deben tener "
            "el mismo número de empresas."
        )

    if observado["k"] != resultados_simulacion["k"]:
        raise ValueError(
            "El mercado observado y la simulación deben usar el mismo valor de k."
        )

    percentiles = {
        "crk": calcular_percentil(observado["crk"], resultados_simulacion["crk"]),
        "ihh": calcular_percentil(observado["ihh"], resultados_simulacion["ihh"]),
        "dominancia": calcular_percentil(
            observado["dominancia"],
            resultados_simulacion["dominancia"],
        ),
        "entropia": calcular_percentil(
            observado["entropia"],
            resultados_simulacion["entropia"],
        ),
    }

    return {
        "observado": observado,
        "percentiles": percentiles,
    }
