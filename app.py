import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---------------------------------------------------------
# Configuración básica
# ---------------------------------------------------------
st.set_page_config(
    page_title="Plataforma de Evaluación Psicolaboral – INE",
    page_icon="📊",
    layout="centered"
)

RESULTS_FILE = "resultados_candidatos_ine.csv"
LOGO_PATH = "Logo_INE.png"  # Debe existir en el repositorio, junto a app.py


# ---------------------------------------------------------
# Utilidades para manejo de resultados
# ---------------------------------------------------------
def cargar_resultados():
    """Carga el archivo de resultados si existe, si no crea un DataFrame vacío."""
    if os.path.exists(RESULTS_FILE):
        return pd.read_csv(RESULTS_FILE)
    else:
        return pd.DataFrame(columns=[
            "fecha_hora",
            "rut",
            "nombre",
            "correo",
            "region",
            "cargo",
            "puntaje_cognitivo",
            "puntaje_personalidad",
            "puntaje_socioemocional",
            "puntaje_competencias",
            "nota_final_1a7",
            "categoria_final"
        ])


def guardar_resultado(registro: dict):
    """Agrega un registro de evaluación al archivo de resultados."""
    df = cargar_resultados()
    df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
    df.to_csv(RESULTS_FILE, index=False)


def calcular_categoria(nota: float) -> str:
    """
    Categoriza según nota final:

    >= 5.5 → Recomendable (A)
    4.5–5.4 → Recomendable con observaciones (B)
    < 4.5 → No recomendable (C)
    """
    if nota >= 5.5:
        return "Recomendable (A)"
    elif nota >= 4.5:
        return "Recomendable con observaciones (B)"
    else:
        return "No recomendable (C)"


# ---------------------------------------------------------
# Funciones de scoring
# ---------------------------------------------------------
def puntaje_cognitivo(respuestas):
    """respuestas: lista de True/False para ítems correctos. Devuelve 0–100."""
    if len(respuestas) == 0:
        return 0.0
    correctas = sum(respuestas)
    return round((correctas / len(respuestas)) * 100, 1)


def puntaje_likert(respuestas, min_val=1, max_val=5):
    """respuestas: lista de valores tipo Likert (1–5). Devuelve 0–100."""
    if len(respuestas) == 0:
        return 0.0
    promedio = sum(respuestas) / len(respuestas)
    return round(((promedio - min_val) / (max_val - min_val)) * 100, 1)


def convertir_a_nota_1a7(
    p_cognitivo,
    p_pers,
    p_socio,
    p_comp,
    w_cog=0.35,
    w_pers=0.25,
    w_socio=0.2,
    w_comp=0.2,
):
    """
    Combina puntajes en 0–100 y los transforma a una nota 1–7.
    Los pesos pueden ajustarse según acuerdo con INE.
    """
    combinado = (
        p_cognitivo * w_cog
        + p_pers * w_pers
        + p_socio * w_socio
        + p_comp * w_comp
    )
    nota = 1 + (combinado / 100) * 6
    return round(nota, 1)


# ---------------------------------------------------------
# Listas auxiliares (Regiones, Cargos)
# ---------------------------------------------------------
REGIONES_CHILE = [
    "Arica y Parinacota",
    "Tarapacá",
    "Antofagasta",
    "Atacama",
    "Coquimbo",
    "Valparaíso",
    "Metropolitana de Santiago",
    "O’Higgins",
    "Maule",
    "Ñuble",
    "Biobío",
    "La Araucanía",
    "Los Ríos",
    "Los Lagos",
    "Aysén",
    "Magallanes y de la Antártica Chilena",
]

CARGOS_INE = [
    "Encuestador/a",
    "Supervisor/a de campo",
    "Digitador/a",
    "Coordinador/a regional",
    "Profesional técnico",
    "Otro",
]


# ---------------------------------------------------------
# Cabecera – Modo INE (logo + título)
# ---------------------------------------------------------
col_logo, col_title = st.columns([1, 4])

with col_logo:
    try:
        st.image(LOGO_PATH, use_column_width=True)
    except Exception:
        st.write("")

with col_title:
    st.markdown(
        "<h1 style='margin-bottom:0px;'>Plataforma de Evaluación Psicolaboral – INE</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='margin-top:4px;'>Servicio de evaluación psicolaboral automatizada "
        "para procesos de selección del Instituto Nacional de Estadísticas de Chile (INE).</p>",
        unsafe_allow_html=True,
    )

st.write("---")

rol = st.sidebar.selectbox(
    "Seleccione tipo de acceso",
    ["Postulante INE", "Administrador INE / Reclutador"],
)


# =====================================================================
# MODO POSTULANTE INE
# =====================================================================
if rol == "Postulante INE":
    st.subheader("Formulario de Evaluación Psicolaboral")

    st.info(
        "Por favor complete sus datos y responda todas las secciones. "
        "Esta evaluación forma parte del proceso de selección del INE."
    )

    # ------------------- Datos del postulante -------------------
    with st.form("datos_postulante"):
        rut = st.text_input("RUT (o ID):")
        nombre = st.text_input("Nombre completo:")
        correo = st.text_input("Correo electrónico:")
        region = st.selectbox("Región en la que postula:", ["Seleccione..."] + REGIONES_CHILE)
        cargo = st.selectbox("Cargo al que postula:", ["Seleccione..."] + CARGOS_INE)
        aceptar = st.checkbox(
            "Declaro que la información entregada es fidedigna y autorizo el uso de mis datos con fines de selección.",
            value=False,
        )
        iniciar = st.form_submit_button("Iniciar evaluación")

    if iniciar:
        if (
            not rut
            or not nombre
            or not correo
            or region == "Seleccione..."
            or cargo == "Seleccione..."
            or not aceptar
        ):
            st.error(
                "Por favor complete todos los campos y acepte la declaración antes de continuar."
            )
        else:
            st.success("Datos registrados. Continúe con las pruebas.")
            st.session_state["datos_postulante"] = {
                "rut": rut,
                "nombre": nombre,
                "correo": correo,
                "region": region,
                "cargo": cargo,
            }

    # ------------------- Secciones de prueba -------------------
    if "datos_postulante" in st.session_state:
        st.write("---")
        st.markdown("### 1. Prueba de Aptitudes Cognitivas (demo)")

        st.write(
            "Responda las siguientes preguntas de razonamiento lógico y numérico. "
            "Marque la alternativa que considere correcta."
        )

        cog_resp = []

        q1 = st.radio(
            "1) Si todos los A son B y todos los B son C, entonces:",
            [
                "Todos los A son C",
                "Algunos A no son C",
                "Ningún A es C",
            ],
            index=None,
        )
        if q1 is not None:
            cog_resp.append(q1 == "Todos los A son C")

        q2 = st.radio(
            "2) Complete la serie: 2, 4, 6, 8, ...",
            ["9", "10", "12"],
            index=None,
        )
        if q2 is not None:
            cog_resp.append(q2 == "10")

        q3 = st.radio(
            "3) Si hoy es martes, ¿qué día será dentro de 3 días?",
            ["Lunes", "Viernes", "Sábado"],
            index=None,
        )
        if q3 is not None:
            cog_resp.append(q3 == "Viernes")

        q4 = st.radio(
            "4) ¿Cuál de los siguientes números es diferente en su patrón?",
            ["12", "16", "21"],
            index=None,
        )
        if q4 is not None:
            cog_resp.append(q4 == "21")

        st.write("---")
        st.markdown("### 2. Perfil de Personalidad (Big Five abreviado – demo)")

        st.write(
            "Indique cuánto se identifica con cada afirmación, donde "
            "1 = Muy en desacuerdo y 5 = Muy de acuerdo."
        )

        pers_resp = []
        pers_resp.append(
            st.slider(
                "Soy una persona organizada y responsable en mis tareas.",
                1,
                5,
                3,
            )
        )
        pers_resp.append(
            st.slider(
                "Disfruto interactuar y comunicarme con otras personas.",
                1,
                5,
                3,
            )
        )
        pers_resp.append(
            st.slider(
                "Mantengo la calma incluso en situaciones de presión.",
                1,
                5,
                3,
            )
        )
        pers_resp.append(
            st.slider(
                "Me interesa aprender cosas nuevas y mejorar continuamente.",
                1,
                5,
                3,
            )
        )

        st.write("---")
        st.markdown("### 3. Competencias Socioemocionales")

        socio_resp = []
        socio_resp.append(
            st.slider(
                "Manejo adecuadamente mis emociones en situaciones difíciles.",
                1,
                5,
                3,
            )
        )
        socio_resp.append(
            st.slider(
                "Me adapto con facilidad a cambios en el trabajo.",
                1,
                5,
                3,
            )
        )
        socio_resp.append(
            st.slider(
                "Mantengo relaciones respetuosas y colaborativas con los demás.",
                1,
                5,
                3,
            )
        )

        st.write("---")
        st.markdown("### 4. Competencias Laborales Generales")

        comp_resp = []
        comp_resp.append(
            st.slider(
                "Cumplo oportunamente con las tareas asignadas.",
                1,
                5,
                3,
            )
        )
        comp_resp.append(
            st.slider(
                "Priorizo adecuadamente cuando tengo varias tareas al mismo tiempo.",
                1,
                5,
                3,
            )
        )
        comp_resp.append(
            st.slider(
                "Me esfuerzo por mantener un alto estándar de calidad en mi trabajo.",
                1,
                5,
                3,
            )
        )

        st.write("---")
        if st.button("Finalizar evaluación y ver resultados"):
            if len(cog_resp) < 4:
                st.error(
                    "Por favor responda todas las preguntas de la prueba de aptitudes cognitivas."
                )
            else:
                # Cálculo de puntajes
                p_cog = puntaje_cognitivo(cog_resp)
                p_pers = puntaje_likert(pers_resp)
                p_socio = puntaje_likert(socio_resp)
                p_comp = puntaje_likert(comp_resp)

                nota_final = convertir_a_nota_1a7(
                    p_cog,
                    p_pers,
                    p_socio,
                    p_comp,
                )
                categoria = calcular_categoria(nota_final)

                st.success(
                    "Evaluación completada. A continuación se presentan sus resultados."
                )

                st.markdown("#### Resumen de resultados")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Puntaje aptitudes cognitivas (0–100)", p_cog)
                    st.metric("Perfil de personalidad (0–100)", p_pers)
                with col2:
                    st.metric("Competencias socioemocionales (0–100)", p_socio)
                    st.metric("Competencias laborales (0–100)", p_comp)

                st.markdown(f"### Nota final (escala 1–7): **{nota_final}**")
                st.markdown(f"### Categoría global: **{categoria}**")

                datos = st.session_state["datos_postulante"]
                registro = {
                    "fecha_hora": datetime.now().isoformat(),
                    "rut": datos["rut"],
                    "nombre": datos["nombre"],
                    "correo": datos["correo"],
                    "region": datos["region"],
                    "cargo": datos["cargo"],
                    "puntaje_cognitivo": p_cog,
                    "puntaje_personalidad": p_pers,
                    "puntaje_socioemocional": p_socio,
                    "puntaje_competencias": p_comp,
                    "nota_final_1a7": nota_final,
                    "categoria_final": categoria,
                }
                guardar_resultado(registro)

                st.info(
                    "Sus resultados han sido registrados en la plataforma "
                    "de evaluación psicolaboral del INE."
                )
                st.caption(
                    "Esta es una versión de demostración. En la versión definitiva se "
                    "incorporarán pruebas validadas y reportes formales en formato PDF."
                )


# =====================================================================
# MODO ADMINISTRADOR INE
# =====================================================================
if rol == "Administrador INE / Reclutador":
    st.subheader("Panel de Administración – Resultados de Evaluaciones INE")

    df = cargar_resultados()
    if df.empty:
        st.warning("Aún no existen evaluaciones registradas en la plataforma.")
    else:
        st.markdown("#### Listado de postulantes evaluados")
        st.dataframe(df)

        st.markdown("#### Estadísticas generales")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("N° de postulantes", len(df))
        with col2:
            st.metric(
                "Promedio nota final (1–7)", round(df["nota_final_1a7"].mean(), 2)
            )
        with col3:
            dist = df["categoria_final"].value_counts().to_dict()
            if dist:
                txt = ", ".join([f"{k}: {v}" for k, v in dist.items()])
                st.write("Distribución por categoría:")
                st.write(txt)
            else:
                st.write("Sin datos suficientes.")

        st.markdown("#### Descarga de resultados")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar resultados en formato CSV (Excel)",
            data=csv,
            file_name="resultados_candidatos_ine.csv",
            mime="text/csv",
        )

        st.info(
            "En una versión posterior se podrán filtrar resultados por región, cargo, "
            "rango de notas y categoría, además de generar reportes específicos para auditoría."
        )
