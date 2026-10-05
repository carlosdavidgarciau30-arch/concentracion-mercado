"""
Validación de cuotas y cálculo de indicadores de concentración de mercado.

Convención del proyecto
-----------------------
- La persona usuaria ingresa las cuotas como porcentajes:
  por ejemplo [60, 40, 0].
- Se permiten cuotas entre 0 % y 100 %, inclusive.
- Internamente las convertimos a proporciones:
  por ejemplo [0.60, 0.40, 0.00].
- El IHH queda, por tanto, en escala de 0 a 1.
"""

from math import isclose, isfinite, log
from numbers import Real


MIN_EMPRESAS = 2
MAX_EMPRESAS = 100

# La tolerancia solo absorbe pequeñas diferencias de punto flotante.
# No acepta, por ejemplo, una suma de 99.99 % como si fuera 100 %.
TOLERANCIA_SUMA = 1e-6


def validar_cuotas(cuotas):
    """
    Comprueba que las cuotas describan un mercado válido.

    Parámetros
    ----------
    cuotas : iterable de números
        Cuotas expresadas en porcentaje, por ejemplo [60, 40, 0].

    Retorna
    -------
    list[float]
        Las mismas cuotas convertidas a float.

    Lanza
    -----
    ValueError
        Si hay menos de 2 o más de 100 empresas, si alguna cuota no es
        numérica/finita, si está fuera del intervalo [0, 100], o si las
        cuotas no suman 100 %.
    """
    if cuotas is None or isinstance(cuotas, (str, bytes)):
        raise ValueError("Las cuotas deben entregarse como una lista de números.")

    try:
        cuotas = list(cuotas)
    except TypeError as exc:
        raise ValueError("Las cuotas deben entregarse como una lista de números.") from exc

    n_empresas = len(cuotas)

    if not MIN_EMPRESAS <= n_empresas <= MAX_EMPRESAS:
        raise ValueError(
            f"El mercado debe tener entre {MIN_EMPRESAS} y {MAX_EMPRESAS} empresas."
        )

    cuotas_limpias = []

    for posicion, cuota in enumerate(cuotas, start=1):
        # bool es una subclase de int en Python; se rechaza para evitar True/False.
        if isinstance(cuota, bool) or not isinstance(cuota, Real):
            raise ValueError(
                f"La cuota de la empresa {posicion} debe ser un número."
            )

        cuota = float(cuota)

        if not isfinite(cuota):
            raise ValueError(
                f"La cuota de la empresa {posicion} debe ser un número finito."
            )

        if cuota < 0:
            raise ValueError(
                f"La cuota de la empresa {posicion} no puede ser menor que 0 %."
            )

        if cuota > 100:
            raise ValueError(
                f"La cuota de la empresa {posicion} no puede superar 100 %."
            )

        cuotas_limpias.append(cuota)

    total = sum(cuotas_limpias)

    if not isclose(total, 100.0, rel_tol=0.0, abs_tol=TOLERANCIA_SUMA):
        raise ValueError(
            f"Las cuotas suman {total:.6f} %. Deben sumar 100 %."
        )

    return cuotas_limpias


def _a_proporciones(cuotas):
    """Valida porcentajes y los convierte a proporciones entre 0 y 1."""
    cuotas_validas = validar_cuotas(cuotas)
    return [cuota / 100.0 for cuota in cuotas_validas]


def _validar_k(k, n_empresas):
    """Comprueba que k sea un entero entre 2 y el número de empresas."""
    if isinstance(k, bool) or not isinstance(k, int):
        raise ValueError("k debe ser un número entero.")

    if not 2 <= k <= n_empresas:
        raise ValueError(
            f"k debe estar entre 2 y {n_empresas} para este mercado."
        )


def calcular_crk(cuotas, k=2):
    """
    Calcula CRk en escala de 0 a 1.

    CRk = suma de las cuotas de las k empresas más grandes.
    """
    proporciones = _a_proporciones(cuotas)
    _validar_k(k, len(proporciones))

    ordenadas = sorted(proporciones, reverse=True)
    return sum(ordenadas[:k])


def calcular_ihh(cuotas):
    """
    Calcula el índice Herfindahl-Hirschman (IHH) en escala de 0 a 1.

    IHH = sum(s_i^2)
    """
    proporciones = _a_proporciones(cuotas)
    return sum(s_i ** 2 for s_i in proporciones)


def calcular_dominancia(cuotas):
    """
    Calcula el índice de dominancia de Pascual García Alba.

    ID = sum[(s_i^2 / IHH)^2]

    Forma equivalente:
    ID = sum(s_i^4) / IHH^2
    """
    proporciones = _a_proporciones(cuotas)
    ihh = sum(s_i ** 2 for s_i in proporciones)

    return sum((s_i ** 2 / ihh) ** 2 for s_i in proporciones)


def calcular_entropia(cuotas):
    """
    Calcula el índice de entropía usando logaritmo natural.

    E = -sum[s_i * ln(s_i)]

    Para una cuota igual a 0 se usa la convención matemática
    0 * ln(0) = 0, entendida como un límite.

    Un valor mayor indica una distribución de cuotas más equilibrada.
    """
    proporciones = _a_proporciones(cuotas)

    return -sum(
        s_i * log(s_i)
        for s_i in proporciones
        if s_i > 0
    )


def calcular_indicadores(cuotas, k=2):
    """
    Valida el mercado y calcula los cuatro indicadores del proyecto.

    Retorna un diccionario sencillo, cómodo para usar más adelante
    desde Streamlit.
    """
    cuotas_validas = validar_cuotas(cuotas)
    _validar_k(k, len(cuotas_validas))

    # Convertimos una sola vez para calcular todo.
    proporciones = [cuota / 100.0 for cuota in cuotas_validas]
    ordenadas = sorted(proporciones, reverse=True)

    crk = sum(ordenadas[:k])
    ihh = sum(s_i ** 2 for s_i in proporciones)
    dominancia = sum((s_i ** 2 / ihh) ** 2 for s_i in proporciones)
    entropia = -sum(
        s_i * log(s_i)
        for s_i in proporciones
        if s_i > 0
    )

    return {
        "n_empresas": len(cuotas_validas),
        "k": k,
        "crk": crk,
        "ihh": ihh,
        "dominancia": dominancia,
        "entropia": entropia,
    }
