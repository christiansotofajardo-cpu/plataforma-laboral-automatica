import streamlit as st
import pandas as pd
from datetime import datetime
import os

# -----------------------------
# Configuración básica
# -----------------------------
st.set_page_config(
    page_title="Plataforma Laboral Automática",
    page_icon="🧠",
    layout="centered"
)

RESULTS_FILE = "resultados_candidatos.csv"

# -----------------------------
# Utilidades
# -----------------------------
def cargar_resultados():
    if os.path.exists(RESULTS_FILE):
        return pd.read_csv(RESULTS_FILE)
    else:
        return pd.DataFrame(columns=[
            "fecha_hora", "rut", "nombre", "correo", "cargo",
            "puntaje_cognitivo", "puntaje_personalidad",
            "puntaje_socioemocional", "puntaje_competencias",
            "nota_final_1a7", "categoria_final"
        ])

def guardar_resultado(registro):
    df = cargar_resultados()
    df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
    df.to_csv(RESULTS_FILE, index=False)

def calcular_categoria(nota):
    if nota >= 5.5:
        return "Recomendable"
    elif nota >= 4.5:
        return "Recomendable con Observaciones"
    else:
        return "No Recomendable"

# -----------------------------
# Scoring de pruebas
# -----------------------------
def puntaje_cognitivo(respuestas):
    correctas = sum(respuestas)
    return round((correctas / len(respuestas)) * 100, 1)

def puntaje_likert(respuestas, min_val=1, max_val=5):
    if len(respuestas) == 0:
        return 0.0
    promedio = sum(respuestas) / len(respuestas)
    return round(((promedio - min_val) / (max_val - min_val)) * 100, 1)

def convertir_a_nota_1a7(
    p_cognitivo, p_pers, p_socio, p_comp,
    w_cog=0.35, w_pers=0.25, w_socio=0.2, w_comp=0.2
):
    combinado = (p_cognitivo * w_cog +
                 p_pers * w_pers +
                 p_socio * w_socio +
                 p_comp * w_comp)
    nota = 1 + (combinado / 100) * 6
    return round(nota, 1)

# -----------------------------
# UI – Cabecera
# -----------------------------
st.title("🧠 Plataforma Laboral Automática")
st.write("Versión demo – Evaluación Psicolaboral Automatizada")

rol = st.sidebar.selectbox(
    "Seleccione tipo de acceso",
    ["Candidato", "Administrador INE / Reclutador"]
)

# =====================================================================
# MODO CANDIDATO
# =====================================================================
if rol == "Candidato":
    st.header("Evaluación Psicolaboral")

    st.markdown("Por favor complete sus datos antes de iniciar las pruebas.")

    with st.form("datos_candidato"):
        rut = st.text_input("RUT (o ID):")
        nombre = st.text_input("Nombre completo:")
        correo = st.text_input("Correo electrónico:")
        cargo = st.text_input("Cargo al que postula:")
        iniciar = st.form_submit_button("Iniciar evaluación")

    if iniciar:
        if not rut or not nombre or not correo or not cargo:
            st.error("Por favor complete todos los datos antes de continuar.")
        else:
            st.success("Datos registrados. Continúe con las pruebas.")
            st.session_state["datos_candidato"] = {
                "rut": rut,
                "nombre": nombre,
                "correo": correo,
                "cargo": cargo
            }

    if "datos_candidato" in st.session_state:
        st.divider()
        st.subheader("1. Prueba Cognitiva (breve demo)")

        st.write("Responda las siguientes preguntas de razonamiento lógico sencillo.")

        cog_resp = []

        q1 = st.radio(
            "1) Si todos los A son B, y todos los B son C, entonces:",
            [
                "Todos los A son C",
                "Algunos A no son C",
                "Ningún A es C"
            ],
            index=None
        )
        if q1 is not None:
            cog_resp.append(q1 == "Todos los A son C")

        q2 = st.radio(
            "2) Completa la serie: 2, 4, 6, 8, ...",
            ["10", "9", "12"],
            index=None
        )
        if q2 is not None:
            cog_resp.append(q2 == "10")

        q3 = st.radio(
            "3) Si hoy es martes, dentro de 3 días será:",
            ["Viernes", "Sábado", "Lunes"],
            index=None
        )
        if q3 is not None:
            cog_resp.append(q3 == "Viernes")

        q4 = st.radio(
            "4) ¿Cuál número es distinto lógicamente del grupo?",
            ["12", "16", "21"],
            index=None
        )
        if q4 is not None:
            cog_resp.append(q4 == "21")

        st.divider()
        st.subheader("2. Rasgos de Personalidad (Big Five abreviado – demo)")

        st.write("Indique cuánto se identifica con las siguientes afirmaciones (1: Muy en desacuerdo, 5: Muy de acuerdo).")

        likert_options = [1, 2, 3, 4, 5]
        pers_resp = []

        pers_resp.append(st.slider("Me considero una persona organizada y responsable.", 1, 5, 3))
        pers_resp.append(st.slider("Disfruto interactuar con otras personas y socializar.", 1, 5, 3))
        pers_resp.append(st.slider("Suelo mantener la calma incluso bajo presión.", 1, 5, 3))
        pers_resp.append(st.slider("Me interesa aprender cosas nuevas y enfrentar desafíos intelectuales.", 1, 5, 3))

        st.divider()
        st.subheader("3. Competencias Socioemocionales")

        socio_resp = []
        socio_resp.append(st.slider("Soy capaz de manejar adecuadamente mis emociones en situaciones difíciles.", 1, 5, 3))
        socio_resp.append(st.slider("Me adapto con facilidad a cambios en el trabajo.", 1, 5, 3))
        socio_resp.append(st.slider("Mantengo buenas relaciones con compañeros/as de trabajo.", 1, 5, 3))

        st.divider()
        st.subheader("4. Competencias Laborales Generales")

        comp_resp = []
        comp_resp.append(st.slider("Cumplo oportunamente con las tareas que se me asignan.", 1, 5, 3))
        comp_resp.append(st.slider("Soy capaz de priorizar tareas cuando tengo mucho trabajo.", 1, 5, 3))
        comp_resp.append(st.slider("Me esfuerzo por mantener un trabajo de calidad.", 1, 5, 3))

        st.divider()
        if st.button("Finalizar evaluación y ver resultados"):
            if len(cog_resp) < 4:
                st.error("Por favor responda todas las preguntas de la prueba cognitiva.")
            else:
                p_cog = puntaje_cognitivo(cog_resp)
                p_pers = puntaje_likert(pers_resp)
                p_socio = puntaje_likert(socio_resp)
                p_comp = puntaje_likert(comp_resp)

                nota_final = convertir_a_nota_1a7(p_cog, p_pers, p_socio, p_comp)
                categoria = calcular_categoria(nota_final)

                st.success("Evaluación completada. A continuación se presentan sus resultados.")

                st.subheader("Resumen de resultados")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Puntaje cognitivo (0–100)", p_cog)
                    st.metric("Rasgos de personalidad (0–100)", p_pers)
                with col2:
                    st.metric("Competencias socioemocionales (0–100)", p_socio)
                    st.metric("Competencias laborales (0–100)", p_comp)

                st.markdown(f"### Nota final (1–7): **{nota_final}**")
                st.markdown(f"### Categoría: **{categoria}**")

                datos = st.session_state["datos_candidato"]
                registro = {
                    "fecha_hora": datetime.now().isoformat(),
                    "rut": datos["rut"],
                    "nombre": datos["nombre"],
                    "correo": datos["correo"],
                    "cargo": datos["cargo"],
                    "puntaje_cognitivo": p_cog,
                    "puntaje_personalidad": p_pers,
                    "puntaje_socioemocional": p_socio,
                    "puntaje_competencias": p_comp,
                    "nota_final_1a7": nota_final,
                    "categoria_final": categoria
                }
                guardar_resultado(registro)

                st.info("Sus resultados han sido registrados en la plataforma.")
                st.write("Este es un informe automatizado de demostración. En una versión completa se generará un PDF individual para cada candidato.")

# =====================================================================
# MODO ADMINISTRADOR / RECLUTADOR
# =====================================================================
if rol == "Administrador INE / Reclutador":
    st.header("Panel de Administración – Resultados de Evaluaciones")

    df = cargar_resultados()
    if df.empty:
        st.warning("Aún no existen evaluaciones registradas.")
    else:
        st.subheader("Resumen general de candidatos evaluados")
        st.dataframe(df)

        st.subheader("Estadísticas generales")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("N° de candidatos", len(df))
        with col2:
            st.metric("Promedio nota final", round(df["nota_final_1a7"].mean(), 2))
        with col3:
            dist = df["categoria_final"].value_counts().to_dict()
            txt = ", ".join([f"{k}: {v}" for k, v in dist.items()])
            st.write("Distribución categorías:")
            st.write(txt)

        st.subheader("Descarga de resultados")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar resultados en Excel (CSV)",
            data=csv,
            file_name="resultados_candidatos.csv",
            mime="text/csv"
        )

        st.info("En una versión posterior, este panel podrá incluir filtros por cargo, fecha, nota, categoría, etc.")
