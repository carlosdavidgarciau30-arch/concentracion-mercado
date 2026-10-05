"""
Aplicación Streamlit para analizar concentración de mercado.

Esta etapa incluye:
- selección del número de empresas;
- ingreso manual o generación aleatoria de cuotas;
- validación de cuotas;
- selección de CRk;
- cálculo de CRk, IHH, dominancia y entropía;
- configuración y ejecución de Monte Carlo;
- comparación gráfica de un indicador a la vez;
- cálculo e interpretación del percentil;
- pregunta educativa sobre la interpretación del IHH.
"""

import numpy as np
import pandas as pd
import streamlit as st

from indicadores import calcular_indicadores, validar_cuotas
from graficos import (
    crear_histograma_comparacion,
    explicar_percentil,
    nombre_indicador,
)
from pregunta import (
    OPCIONES_RESPUESTA,
    REFERENCIA_CORTA,
    evaluar_respuesta_ihh,
)
from simulacion import (
    MAX_REPETICIONES,
    MIN_REPETICIONES,
    REPETICIONES_PREDETERMINADAS,
    calcular_percentil,
    generar_mercado_aleatorio,
    simular_indicadores,
)


UMBRAL_ADVERTENCIA_SIMULACIONES = 10_000


st.set_page_config(
    page_title="Concentración de mercado",
    page_icon="📊",
    layout="wide",
)


def crear_tabla_vacia(n_empresas):
    """Crea una tabla nueva de N empresas con cuotas iniciales iguales a cero."""
    return pd.DataFrame(
        {
            "Empresa": [f"Empresa {i}" for i in range(1, n_empresas + 1)],
            "Cuota (%)": [0.0] * n_empresas,
        }
    )


def reiniciar_respuesta_educativa():
    """Limpia la respuesta educativa cuando cambia el mercado o la simulación."""
    st.session_state["retroalimentacion_ihh"] = None
    st.session_state["version_pregunta"] = st.session_state.get("version_pregunta", 0) + 1


def limpiar_resultados():
    """Borra cálculos que hayan quedado obsoletos tras cambiar los datos."""
    st.session_state["resultados_mercado"] = None
    st.session_state["resultados_simulacion"] = None
    reiniciar_respuesta_educativa()


def limpiar_simulacion():
    """Borra solo la simulación cuando cambia su configuración."""
    st.session_state["resultados_simulacion"] = None
    reiniciar_respuesta_educativa()


def reiniciar_mercado(n_empresas):
    """
    Reinicia por completo las cuotas cuando cambia el número de empresas.

    También cambia la clave del editor para obligar a Streamlit a mostrar
    una tabla nueva en lugar de conservar ediciones del mercado anterior.
    """
    st.session_state["n_anterior"] = n_empresas
    st.session_state["tabla_cuotas"] = crear_tabla_vacia(n_empresas)
    st.session_state["version_editor"] = st.session_state.get("version_editor", 0) + 1
    limpiar_resultados()


def reemplazar_por_mercado_aleatorio(n_empresas):
    """Genera un mercado aleatorio y reemplaza la tabla actual."""
    cuotas = generar_mercado_aleatorio(n_empresas)

    st.session_state["tabla_cuotas"] = pd.DataFrame(
        {
            "Empresa": [f"Empresa {i}" for i in range(1, n_empresas + 1)],
            "Cuota (%)": cuotas,
        }
    )
    st.session_state["version_editor"] += 1
    limpiar_resultados()


def formatear_resultado(valor):
    """Muestra los indicadores con cuatro decimales."""
    return f"{valor:.4f}"


# ---------------------------------------------------------------------
# Estado inicial
# ---------------------------------------------------------------------

if "version_editor" not in st.session_state:
    st.session_state["version_editor"] = 0

if "resultados_mercado" not in st.session_state:
    st.session_state["resultados_mercado"] = None

if "resultados_simulacion" not in st.session_state:
    st.session_state["resultados_simulacion"] = None

if "retroalimentacion_ihh" not in st.session_state:
    st.session_state["retroalimentacion_ihh"] = None

if "version_pregunta" not in st.session_state:
    st.session_state["version_pregunta"] = 0


# ---------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------

st.title("📊 Concentración de mercado")
st.write(
    "Ingresa un mercado, calcula sus indicadores y genera mercados aleatorios "
    "para una simulación Monte Carlo."
)

st.caption(
    "Las cuotas se escriben como porcentajes (por ejemplo: 40, 30, 20 y 10). "
    "Los cálculos convierten esas cuotas internamente a proporciones."
)


# ---------------------------------------------------------------------
# 1. Número de empresas
# ---------------------------------------------------------------------

st.header("1. Define el mercado")

n_empresas = st.number_input(
    "¿Cuántas empresas tiene el mercado?",
    min_value=2,
    max_value=100,
    value=4,
    step=1,
    help="Puedes elegir entre 2 y 100 empresas.",
)

n_empresas = int(n_empresas)

if "n_anterior" not in st.session_state:
    reiniciar_mercado(n_empresas)
elif st.session_state["n_anterior"] != n_empresas:
    reiniciar_mercado(n_empresas)


# ---------------------------------------------------------------------
# 2. Cuotas
# ---------------------------------------------------------------------

st.subheader("Cuotas de mercado")

modo_entrada = st.radio(
    "¿Cómo quieres obtener las cuotas?",
    options=("Ingresarlas manualmente", "Generar un ejemplo al azar"),
    horizontal=True,
)

if modo_entrada == "Generar un ejemplo al azar":
    st.write(
        "La aplicación generará un mercado con una distribución "
        "Dirichlet(1, …, 1), cuyas cuotas suman 100 %."
    )

    if st.button("🎲 Generar mercado aleatorio"):
        reemplazar_por_mercado_aleatorio(n_empresas)
        st.rerun()

else:
    st.write(
        "Escribe una cuota entre 0 % y 100 % para cada empresa. "
        "La suma total debe ser 100 %."
    )


tabla_anterior = st.session_state["tabla_cuotas"].copy()

altura_tabla = min(430, 38 + 35 * n_empresas)

tabla_editada = st.data_editor(
    st.session_state["tabla_cuotas"],
    width="stretch",
    height=altura_tabla,
    hide_index=True,
    num_rows="fixed",
    disabled=["Empresa"],
    column_config={
        "Empresa": st.column_config.TextColumn(
            "Empresa",
            help="Identificador de la empresa.",
        ),
        "Cuota (%)": st.column_config.NumberColumn(
            "Cuota (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            format="%.4f",
            help="Participación de mercado entre 0 % y 100 %.",
        ),
    },
    key=f"editor_cuotas_{n_empresas}_{st.session_state['version_editor']}",
)

# Si la persona cambia una cuota, los resultados anteriores ya no representan
# el mercado actual y deben desaparecer.
if not tabla_editada.equals(tabla_anterior):
    st.session_state["tabla_cuotas"] = tabla_editada.copy()
    limpiar_resultados()
else:
    st.session_state["tabla_cuotas"] = tabla_editada.copy()


serie_cuotas = pd.to_numeric(
    st.session_state["tabla_cuotas"]["Cuota (%)"],
    errors="coerce",
)

if serie_cuotas.isna().any():
    total_cuotas = None
    st.warning("Hay al menos una cuota que no es un número válido.")
else:
    total_cuotas = float(serie_cuotas.sum())
    st.metric("Total de cuotas", f"{total_cuotas:.4f} %")


cuotas = serie_cuotas.tolist()

mercado_valido = False
mensaje_validacion = ""

try:
    validar_cuotas(cuotas)
    mercado_valido = True
except ValueError as error:
    mensaje_validacion = str(error)

if mercado_valido:
    st.success("Las cuotas son válidas y suman 100 %.")
else:
    st.info(mensaje_validacion)


# ---------------------------------------------------------------------
# 3. CRk y resultados observados
# ---------------------------------------------------------------------

st.header("2. Calcula los indicadores")

k = st.selectbox(
    "¿Qué CRk quieres calcular?",
    options=list(range(2, n_empresas + 1)),
    format_func=lambda valor: f"CR{valor}",
    index=0,
    key=f"selector_k_{n_empresas}",
    on_change=limpiar_resultados,
)

k = int(k)

if st.button(
    "Calcular indicadores",
    type="primary",
    disabled=not mercado_valido,
):
    st.session_state["resultados_mercado"] = calcular_indicadores(cuotas, k=k)
    st.session_state["resultados_simulacion"] = None
    reiniciar_respuesta_educativa()


resultados = st.session_state["resultados_mercado"]

if resultados is not None:
    st.subheader("Resultados del mercado")

    columna_1, columna_2, columna_3, columna_4 = st.columns(4)

    columna_1.metric(f"CR{resultados['k']}", formatear_resultado(resultados["crk"]))
    columna_2.metric("IHH", formatear_resultado(resultados["ihh"]))
    columna_3.metric(
        "Dominancia",
        formatear_resultado(resultados["dominancia"]),
    )
    columna_4.metric(
        "Entropía",
        formatear_resultado(resultados["entropia"]),
    )

    st.caption(
        "CRk, IHH y dominancia aumentan con la concentración. "
        "La entropía se interpreta en sentido contrario: un valor mayor "
        "indica cuotas más repartidas."
    )


# ---------------------------------------------------------------------
# 4. Monte Carlo
# ---------------------------------------------------------------------

st.header("3. Simulación Monte Carlo")

st.write(
    "La simulación generará muchos mercados aleatorios con el mismo número "
    "de empresas y calculará los cuatro indicadores en cada repetición."
)

repeticiones = st.number_input(
    "Cantidad de repeticiones",
    min_value=MIN_REPETICIONES,
    max_value=MAX_REPETICIONES,
    value=REPETICIONES_PREDETERMINADAS,
    step=100,
    key="repeticiones_mc",
    on_change=limpiar_simulacion,
    help=(
        f"Puedes elegir entre {MIN_REPETICIONES:,} y "
        f"{MAX_REPETICIONES:,} repeticiones."
    ),
)

repeticiones = int(repeticiones)

st.info(
    "Rendimiento: al aumentar el número de repeticiones, la simulación "
    "requiere más cálculos. Esto puede aumentar el tiempo de espera "
    "(latencia de respuesta) y el uso de CPU y memoria. "
    "Para pruebas rápidas, usa 100–1.000 repeticiones; para un análisis "
    "más estable puedes aumentar R según los recursos disponibles."
)

if repeticiones > 25_000:
    st.warning(
        "Carga muy alta: has seleccionado más de 25.000 repeticiones. "
        "La respuesta puede tardar perceptiblemente más y consumir más "
        "CPU y memoria, especialmente si el mercado tiene muchas empresas."
    )
elif repeticiones > UMBRAL_ADVERTENCIA_SIMULACIONES:
    st.warning(
        "Carga alta: has seleccionado más de 10.000 repeticiones. "
        "La simulación puede aumentar la latencia de respuesta y el "
        "consumo de CPU y memoria, especialmente con muchas empresas."
    )

if resultados is None:
    st.info(
        "Primero calcula los indicadores de tu mercado. "
        "Después podrás compararlo con la simulación."
    )

if st.button(
    "Ejecutar simulación",
    disabled=(not mercado_valido or resultados is None),
):
    reiniciar_respuesta_educativa()
    with st.spinner("Generando mercados y calculando indicadores..."):
        st.session_state["resultados_simulacion"] = simular_indicadores(
            n_empresas=n_empresas,
            k=k,
            repeticiones=repeticiones,
        )


simulacion = st.session_state["resultados_simulacion"]

if simulacion is not None:
    st.success(
        f"Simulación completada: {simulacion['repeticiones']:,} mercados "
        f"de {simulacion['n_empresas']} empresas."
    )

    resumen = pd.DataFrame(
        {
            "Indicador": [
                f"CR{simulacion['k']}",
                "IHH",
                "Dominancia",
                "Entropía",
            ],
            "Promedio simulado": [
                float(np.mean(simulacion["crk"])),
                float(np.mean(simulacion["ihh"])),
                float(np.mean(simulacion["dominancia"])),
                float(np.mean(simulacion["entropia"])),
            ],
        }
    )

    st.dataframe(
        resumen.style.format({"Promedio simulado": "{:.4f}"}),
        width="stretch",
        hide_index=True,
    )

    st.subheader("Compara tu mercado con las simulaciones")

    opciones_indicador = {
        f"CR{simulacion['k']}": "crk",
        "IHH": "ihh",
        "Dominancia": "dominancia",
        "Entropía": "entropia",
    }

    indicador_elegido = st.selectbox(
        "¿Qué indicador quieres mirar?",
        options=list(opciones_indicador.keys()),
        key="indicador_grafico",
    )

    clave_indicador = opciones_indicador[indicador_elegido]
    valor_observado = resultados[clave_indicador]
    valores_simulados = simulacion[clave_indicador]

    percentil = calcular_percentil(
        valor_observado,
        valores_simulados,
    )

    columna_valor, columna_percentil = st.columns(2)

    columna_valor.metric(
        "Tu mercado",
        formatear_resultado(valor_observado),
    )
    columna_percentil.metric(
        "Percentil",
        f"{percentil:.1f}",
    )

    figura = crear_histograma_comparacion(
        valores_simulados=valores_simulados,
        valor_observado=valor_observado,
        clave=clave_indicador,
        k=simulacion["k"],
    )

    st.pyplot(
        figura,
        clear_figure=True,
        width="stretch",
    )

    st.info(
        explicar_percentil(
            clave=clave_indicador,
            percentil=percentil,
            k=simulacion["k"],
        )
    )

    st.caption(
        "El percentil compara tu resultado con los mercados generados por "
        "la simulación Dirichlet. No es, por sí solo, una clasificación legal "
        "ni una prueba de que el mercado sea competitivo o anticompetitivo."
    )


    # -----------------------------------------------------------------
    # 5. Pregunta educativa sobre IHH
    # -----------------------------------------------------------------

    st.header("4. Interpreta tu mercado")

    st.write(
        "Según el IHH de tu mercado y los umbrales de referencia, "
        "¿cómo interpretarías este resultado?"
    )

    st.caption(
        "Referencia para corregir: "
        + REFERENCIA_CORTA
        + " La aplicación usa IHH en escala de 0 a 1, por lo que "
          "1500 puntos equivalen a 0,15 y 2500 puntos a 0,25. "
          "Esta actividad usa solo el nivel del IHH para practicar su interpretación; "
          "no sustituye el análisis completo de competencia de la FNE."
    )

    respuesta_ihh = st.radio(
        "Elige una respuesta:",
        options=OPCIONES_RESPUESTA,
        index=None,
        key=f"respuesta_pregunta_ihh_{st.session_state['version_pregunta']}",
    )

    if st.button(
        "Comprobar respuesta",
        disabled=respuesta_ihh is None,
    ):
        percentil_ihh = calcular_percentil(
            resultados["ihh"],
            simulacion["ihh"],
        )

        st.session_state["retroalimentacion_ihh"] = evaluar_respuesta_ihh(
            ihh=resultados["ihh"],
            respuesta_usuario=respuesta_ihh,
            percentil=percentil_ihh,
        )

    retroalimentacion = st.session_state["retroalimentacion_ihh"]

    if retroalimentacion is not None:
        if retroalimentacion["estado"] == "correcta":
            st.success(retroalimentacion["explicacion"])
        else:
            st.error(retroalimentacion["explicacion"])

        st.caption(
            "El percentil solo indica la posición de tu IHH dentro de los "
            "mercados simulados. La categoría se corrige usando los umbrales "
            "de la referencia, no usando el percentil."
        )
