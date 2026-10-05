"""
Gráficos y textos de comparación entre el mercado observado
y los resultados de la simulación Monte Carlo.
"""

import numpy as np
import matplotlib.pyplot as plt


def nombre_indicador(clave, k):
    """Devuelve el nombre que verá la persona usuaria."""
    nombres = {
        "crk": f"CR{k}",
        "ihh": "IHH",
        "dominancia": "Índice de dominancia",
        "entropia": "Índice de entropía",
    }

    if clave not in nombres:
        raise ValueError("Indicador no reconocido.")

    return nombres[clave]


def explicar_percentil(clave, percentil, k):
    """
    Construye una explicación breve del percentil.

    El percentil se define como el porcentaje de simulaciones cuyo valor
    es menor o igual que el valor observado.
    """
    nombre = nombre_indicador(clave, k)
    p = float(percentil)

    if not 0 <= p <= 100:
        raise ValueError("El percentil debe estar entre 0 y 100.")

    base = (
        f"Tu mercado está en el percentil {p:.1f} de {nombre}. "
        f"Eso significa que su valor es mayor o igual que el de "
        f"aproximadamente el {p:.1f} % de los mercados simulados."
    )

    if clave == "entropia":
        return (
            base
            + " En entropía, un valor más alto indica cuotas más repartidas. "
              "Por eso, un percentil alto de entropía se interpreta como "
              "mayor equilibrio y menor concentración relativa según este indicador."
        )

    if clave == "dominancia":
        return (
            base
            + " En el índice de dominancia, valores más altos indican una "
              "estructura relativamente más dominada por las empresas de mayor peso."
        )

    return (
        base
        + " En este indicador, valores más altos indican mayor concentración. "
          "Por eso, un percentil alto ubica a tu mercado hacia la parte más "
          "concentrada de la distribución simulada."
    )


def crear_histograma_comparacion(
    valores_simulados,
    valor_observado,
    clave,
    k,
):
    """
    Crea un histograma de la simulación y marca el valor del mercado observado.

    Retorna un objeto Figure de Matplotlib para mostrarlo con st.pyplot().
    """
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

    nombre = nombre_indicador(clave, k)

    # Un número moderado de barras funciona bien desde 100 hasta 50.000 repeticiones.
    numero_barras = min(30, max(10, int(np.sqrt(valores.size))))

    figura, eje = plt.subplots(figsize=(9, 5))

    eje.hist(valores, bins=numero_barras)
    eje.axvline(
        valor_observado,
        linestyle="--",
        linewidth=2.5,
        label=f"Tu mercado: {valor_observado:.4f}",
    )

    eje.set_title(f"Distribución simulada de {nombre}")
    eje.set_xlabel(nombre)
    eje.set_ylabel("Cantidad de simulaciones")
    eje.legend()
    figura.tight_layout()

    return figura
