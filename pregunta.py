\
"""
Pregunta educativa sobre la interpretación del IHH.

Referencia utilizada
---------------------
Guía para el Análisis de Operaciones de Concentración Horizontales
de la Fiscalía Nacional Económica (FNE), 2022, párrafos 35 y 36.

La aplicación usa el IHH en escala de 0 a 1:
- 1500 puntos -> 0.15
- 2500 puntos -> 0.25

La redacción de la FNE es estricta:
- inferior a 1500;
- superior a 1500 e inferior a 2500: moderadamente concentrado;
- superior a 2500: altamente concentrado.

Por ello, 0.15 y 0.25 se tratan como valores exactamente ubicados en
un umbral. En esos casos la respuesta correcta de la actividad es
"Está exactamente en un umbral".
"""

from math import isclose


UMBRAL_1 = 0.15
UMBRAL_2 = 0.25

# Solo se usa para reconocer el mismo valor matemático pese a pequeñas
# diferencias de punto flotante.
TOLERANCIA_UMBRAL = 1e-12

REFERENCIA_CORTA = (
    "Fiscalía Nacional Económica (FNE), "
    "Guía para el Análisis de Operaciones de Concentración Horizontales (2022), "
    "párrafos 35–36."
)

OPCION_UMBRAL = "Está exactamente en un umbral"

OPCIONES_RESPUESTA = (
    "Baja concentración",
    "Concentración moderada",
    "Alta concentración",
    OPCION_UMBRAL,
)


def clasificar_ihh(ihh):
    """Clasifica el IHH para la actividad educativa."""
    ihh = float(ihh)

    if not 0 <= ihh <= 1:
        raise ValueError("El IHH debe estar entre 0 y 1.")

    if isclose(ihh, UMBRAL_1, rel_tol=0.0, abs_tol=TOLERANCIA_UMBRAL):
        return {
            "tipo": "umbral_015",
            "respuesta_correcta": OPCION_UMBRAL,
            "titulo": "Exactamente en el umbral de 0,15",
        }

    if isclose(ihh, UMBRAL_2, rel_tol=0.0, abs_tol=TOLERANCIA_UMBRAL):
        return {
            "tipo": "umbral_025",
            "respuesta_correcta": OPCION_UMBRAL,
            "titulo": "Exactamente en el umbral de 0,25",
        }

    if ihh < UMBRAL_1:
        return {
            "tipo": "baja",
            "respuesta_correcta": "Baja concentración",
            "titulo": "Baja concentración",
        }

    if ihh < UMBRAL_2:
        return {
            "tipo": "moderada",
            "respuesta_correcta": "Concentración moderada",
            "titulo": "Concentración moderada",
        }

    return {
        "tipo": "alta",
        "respuesta_correcta": "Alta concentración",
        "titulo": "Alta concentración",
    }


def evaluar_respuesta_ihh(ihh, respuesta_usuario, percentil):
    """
    Evalúa la respuesta del usuario y prepara una explicación educativa.

    El percentil se informa como contexto, pero no determina la categoría.
    """
    if respuesta_usuario not in OPCIONES_RESPUESTA:
        raise ValueError("La respuesta elegida no es válida.")

    percentil = float(percentil)
    if not 0 <= percentil <= 100:
        raise ValueError("El percentil debe estar entre 0 y 100.")

    clasificacion = clasificar_ihh(ihh)
    ihh = float(ihh)
    respuesta_correcta = clasificacion["respuesta_correcta"]
    acierto = respuesta_usuario == respuesta_correcta

    comun = (
        f"Tu IHH es {ihh:.4f} y quedó en el percentil {percentil:.1f} "
        "de la simulación. "
        f"Referencia: {REFERENCIA_CORTA} "
    )

    tipo = clasificacion["tipo"]

    if tipo == "umbral_015":
        regla = (
            "0,15 equivale exactamente a 1500 puntos. La Guía usa "
            "'inferior a 1500' para el primer tramo y 'superior a 1500 e "
            "inferior a 2500' para el tramo moderadamente concentrado. "
            "Por eso, en esta actividad la respuesta esperada es "
            f"'{OPCION_UMBRAL}'."
        )
    elif tipo == "umbral_025":
        regla = (
            "0,25 equivale exactamente a 2500 puntos. La Guía describe como "
            "moderadamente concentrado un IHH superior a 1500 e inferior a "
            "2500, y como altamente concentrado un IHH superior a 2500. "
            "Por eso, en esta actividad la respuesta esperada es "
            f"'{OPCION_UMBRAL}'."
        )
    elif tipo == "baja":
        regla = (
            "En esta actividad llamamos 'Baja concentración' al tramo por "
            "debajo de 0,15 (1500 puntos), es decir, por debajo del primer "
            "umbral usado por la FNE."
        )
    elif tipo == "moderada":
        regla = (
            "La FNE describe como moderadamente concentrado un mercado con "
            "IHH superior a 0,15 e inferior a 0,25 "
            "(1500 < IHH < 2500 en su escala de puntos)."
        )
    else:
        regla = (
            "La FNE describe como altamente concentrado un mercado con "
            "IHH superior a 0,25 (más de 2500 puntos)."
        )

    if acierto:
        explicacion = (
            f"Correcto. {comun}{regla} "
            f"Respuesta: {respuesta_correcta}."
        )
        estado = "correcta"
    else:
        explicacion = (
            f"Tu respuesta fue '{respuesta_usuario}', pero la respuesta esperada "
            f"es '{respuesta_correcta}'. {comun}{regla}"
        )
        estado = "incorrecta"

    return {
        "estado": estado,
        "correcta": acierto,
        "respuesta_correcta": respuesta_correcta,
        "titulo": clasificacion["titulo"],
        "explicacion": explicacion,
    }
