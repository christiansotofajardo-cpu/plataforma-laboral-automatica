import streamlit as st
from PIL import Image
from datetime import datetime
import pandas as pd
import altair as alt

# --------------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# --------------------------------------------------------------------
st.set_page_config(
    page_title="Plataforma de Evaluación Psicolaboral – INE",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------------------------
# BANCOS DE ÍTEMS (DEMO – 5 POR MÓDULO)
# --------------------------------------------------------------------
PREGUNTAS_COGNITIVAS = [
    {
        "id": 1,
        "enunciado": "¿Qué número completa la serie 2, 4, 6, 8, ... ?",
        "opciones": ["9", "10", "11", "12"],
        "correcta": 1,
    },
    {
        "id": 2,
        "enunciado": "Si hoy es lunes, ¿qué día será en 3 días más?",
        "opciones": ["Martes", "Miércoles", "Jueves", "Viernes"],
        "correcta": 2,
    },
    {
        "id": 3,
        "enunciado": "Un encuestador aplica 5 encuestas por hora. ¿Cuántas aplicará en 4 horas?",
        "opciones": ["10", "15", "20", "25"],
        "correcta": 2,
    },
    {
        "id": 4,
        "enunciado": "Si 1 km equivale a 1.000 metros, ¿cuántos metros son 3,5 km?",
        "opciones": ["2.500", "3.000", "3.500", "4.000"],
        "correcta": 2,
    },
    {
        "id": 5,
        "enunciado": "En una tabla hay 4 filas y 3 columnas. ¿Cuántas celdas tiene en total?",
        "opciones": ["7", "10", "12", "16"],
        "correcta": 2,
    },
]

PREGUNTAS_PSICO = [
    "Me siento cómodo/a trabajando bajo presión de tiempo.",
    "Me preocupo por revisar cuidadosamente los datos antes de enviarlos.",
    "Me resulta fácil coordinarme con otras personas para cumplir una meta común.",
    "Cuando algo cambia en el trabajo, me adapto rápidamente.",
    "Me considero responsable con los plazos que se me asignan.",
]

PREGUNTAS_ESTILOS = [
    "Prefiero trabajar principalmente:",
    "Cuando tengo una tarea compleja, prefiero recibir instrucciones:",
    "En relación con la supervisión directa, me siento más cómodo/a cuando:",
    "Respecto a la toma de decisiones en terreno, prefiero:",
    "En un equipo de trabajo, suelo aportar más en:",
]

# --------------------------------------------------------------------
# INICIALIZACIÓN DE SESSION_STATE
# --------------------------------------------------------------------
def init_session_state():
    if "datos_postulante" not in st.session_state:
        st.session_state["datos_postulante"] = None

    if "postulante_registrado" not in st.session_state:
        st.session_state["postulante_registrado"] = False

    if "historial_postulantes" not in st.session_state:
        st.session_state["historial_postulantes"] = []

    # Estado interno de pruebas
    if "indice_cog" not in st.session_state:
        st.session_state["indice_cog"] = 0
    if "resultados_cog" not in st.session_state:
        st.session_state["resultados_cog"] = None
    if "resultados_psico" not in st.session_state:
        st.session_state["resultados_psico"] = None
    if "resultados_estilos" not in st.session_state:
        st.session_state["resultados_estilos"] = None

    # Resultados por postulante (clave: RUT)
    if "resultados_por_postulante" not in st.session_state:
        st.session_state["resultados_por_postulante"] = {}

    # Estado administrador
    if "admin_autenticado" not in st.session_state:
        st.session_state["admin_autenticado"] = False


init_session_state()


def reset_pruebas_para_nuevo_postulante():
    """Limpia completamente widgets y resultados de pruebas para un nuevo postulante."""
    keys_a_borrar = []
    for key in list(st.session_state.keys()):
        if key.startswith("cog_") or key.startswith("psico_") or key.startswith("est_"):
            keys_a_borrar.append(key)

    for k in keys_a_borrar:
        del st.session_state[k]

    st.session_state["indice_cog"] = 0
    st.session_state["resultados_cog"] = None
    st.session_state["resultados_psico"] = None
    st.session_state["resultados_estilos"] = None


def get_rut_actual():
    datos = st.session_state.get("datos_postulante")
    if datos is None:
        return None
    return datos.get("rut")


def asegurar_registro_postulante_en_resultados():
    rut = get_rut_actual()
    if rut is None:
        return
    if rut not in st.session_state["resultados_por_postulante"]:
        st.session_state["resultados_por_postulante"][rut] = {
            "datos": st.session_state["datos_postulante"],
            "cognitivo": None,
            "psico": None,
            "estilos": None,
        }


def registrar_resultado(modulo: str, data: dict):
    """Guarda resultados por postulante (solo para vista administrador)."""
    rut = get_rut_actual()
    if rut is None:
        return
    asegurar_registro_postulante_en_resultados()
    st.session_state["resultados_por_postulante"][rut][modulo] = data


# --------------------------------------------------------------------
# ENCABEZADO CON LOGO + TÍTULO
# --------------------------------------------------------------------
def mostrar_encabezado():
    col_logo, col_titulo = st.columns([1, 3])

    with col_logo:
        try:
            logo = Image.open("Logo_INE.png")  # Debe estar junto a app.py
            st.image(logo, width=140)
        except Exception:
            st.write("**INE**")

    with col_titulo:
        st.markdown(
            """
            # Plataforma de Evaluación Psicolaboral – INE  

            Servicio de evaluación psicolaboral automatizada para procesos de selección del  
            Instituto Nacional de Estadísticas de Chile (INE).
            """,
            unsafe_allow_html=True,
        )
    st.markdown("---")


# --------------------------------------------------------------------
# VISTA: POSTULANTE
# --------------------------------------------------------------------
def vista_postulante():
    st.subheader("Formulario de Evaluación Psicolaboral")

    st.info(
        "Por favor complete sus datos y responda todas las secciones. "
        "Esta evaluación forma parte del proceso de selección del INE."
    )

    with st.form(key="form_datos_postulante"):
        rut = st.text_input("RUT (o ID):", key="rut_input")
        nombre = st.text_input("Nombre completo:", key="nombre_input")
        correo = st.text_input("Correo electrónico:", key="correo_input")
        telefono = st.text_input("Teléfono de contacto:", key="telefono_input")

        cargo = st.selectbox(
            "Cargo al que postula:",
            (
                "Supervisor/a de campo",
                "Entrevistador/a de terreno",
                "Digitador/a",
                "Coordinador/a regional",
                "Otro",
            ),
            key="cargo_select",
        )

        acepta_uso_datos = st.checkbox(
            "Declaro que la información entregada es fidedigna y autorizo "
            "el uso de mis datos con fines de selección.",
            key="acepta_checkbox",
        )

        iniciar = st.form_submit_button("Iniciar evaluación")

    if iniciar:
        if not rut or not nombre or not correo:
            st.error("Por favor complete al menos RUT, nombre y correo electrónico.")
            st.session_state["postulante_registrado"] = False
        elif not acepta_uso_datos:
            st.error("Debe autorizar el uso de datos para continuar con la evaluación.")
            st.session_state["postulante_registrado"] = False
        else:
            datos = {
                "rut": rut,
                "nombre": nombre,
                "correo": correo,
                "telefono": telefono,
                "cargo": cargo,
                "acepta_uso_datos": acepta_uso_datos,
                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state["datos_postulante"] = datos
            st.session_state["postulante_registrado"] = True
            st.session_state["historial_postulantes"].append(datos)
            reset_pruebas_para_nuevo_postulante()
            asegurar_registro_postulante_en_resultados()

    if st.session_state["postulante_registrado"]:
        st.success("Datos registrados. Continúe con las pruebas.")
        mostrar_bloque_pruebas_postulante()
    else:
        st.info("Complete el formulario y presione **Iniciar evaluación** para continuar.")


# --------------------------------------------------------------------
# MÓDULOS DE PRUEBAS (POSTULANTE NO VE PUNTAJES)
# --------------------------------------------------------------------
def modulo_prueba_cognitiva():
    st.markdown("### 1. Prueba Cognitiva – Versión Demo (5 ítems)")
    st.write(
        "En esta prueba se presentan ítems de razonamiento lógico, cálculo sencillo y "
        "resolución de problemas vinculados al trabajo de campo."
    )

    preguntas = PREGUNTAS_COGNITIVAS
    n_preg = len(preguntas)

    indice = st.session_state.get("indice_cog", 0)
    indice = max(0, min(indice, n_preg - 1))
    st.session_state["indice_cog"] = indice
    pregunta = preguntas[indice]

    st.write(f"**Pregunta {indice + 1} de {n_preg}**")
    st.write(pregunta["enunciado"])

    key_radio = f"cog_{pregunta['id']}"
    opciones = pregunta["opciones"]

    st.radio(
        "Seleccione una alternativa:",
        options=opciones,
        key=key_radio,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("◀ Anterior", disabled=(indice == 0), key=f"btn_ant_{indice}"):
            st.session_state["indice_cog"] = max(0, indice - 1)

    with col2:
        if st.button("Siguiente ▶", disabled=(indice == n_preg - 1), key=f"btn_sig_{indice}"):
            st.session_state["indice_cog"] = min(n_preg - 1, indice + 1)

    with col3:
        if st.button("Finalizar prueba", key="btn_final_cog"):
            aciertos = 0
            contestadas = 0
            for p in preguntas:
                key_resp = f"cog_{p['id']}"
                resp = st.session_state.get(key_resp)
                if resp is not None:
                    contestadas += 1
                    if resp == p["opciones"][p["correcta"]]:
                        aciertos += 1

            if contestadas == 0:
                st.warning("Debe responder al menos una pregunta para registrar la prueba.")
            else:
                puntaje = round(aciertos / n_preg * 100)
                st.session_state["resultados_cog"] = {
                    "aciertos": aciertos,
                    "total": n_preg,
                    "puntaje": puntaje,
                }
                registrar_resultado("cognitivo", st.session_state["resultados_cog"])
                st.success("Respuestas registradas correctamente.")


def modulo_cuestionario_psicolaboral():
    st.markdown("### 2. Cuestionario Psicolaboral – Versión Demo (5 ítems)")
    st.write(
        "Responda las siguientes afirmaciones indicando su grado de acuerdo, "
        "donde 1 = Muy en desacuerdo y 5 = Muy de acuerdo."
    )

    respuestas = []
    for i, texto in enumerate(PREGUNTAS_PSICO, start=1):
        valor = st.slider(
            texto,
            min_value=1,
            max_value=5,
            value=3,
            key=f"psico_{i}",
        )
        respuestas.append(valor)

    if st.button("Guardar respuestas cuestionario", key="btn_guardar_psico"):
        promedio = sum(respuestas) / len(respuestas)
        st.session_state["resultados_psico"] = {
            "promedio": round(promedio, 2),
            "n_items": len(respuestas),
        }
        registrar_resultado("psico", st.session_state["resultados_psico"])
        st.success("Respuestas registradas correctamente.")


def modulo_inventario_estilos():
    st.markdown("### 3. Inventario de Estilos Laborales – Versión Demo")
    st.write(
        "Este módulo recoge información sobre sus preferencias de trabajo y estilo "
        "de funcionamiento en equipo."
    )

    respuestas_estilos = {}

    respuestas_estilos["forma_trabajo"] = st.selectbox(
        PREGUNTAS_ESTILOS[0],
        [
            "Solo/a",
            "En pareja",
            "En equipos pequeños",
            "En equipos grandes",
        ],
        key="est_1",
    )

    respuestas_estilos["instrucciones"] = st.selectbox(
        PREGUNTAS_ESTILOS[1],
        [
            "Muy detalladas, paso a paso",
            "Indicaciones generales y luego aclarar dudas",
            "Indicaciones mínimas; prefiero decidir cómo hacerlo",
        ],
        key="est_2",
    )

    respuestas_estilos["supervision"] = st.selectbox(
        PREGUNTAS_ESTILOS[2],
        [
            "Con supervisión frecuente",
            "Con supervisión periódica",
            "Con supervisión sólo cuando sea necesario",
        ],
        key="est_3",
    )

    respuestas_estilos["toma_decisiones"] = st.selectbox(
        PREGUNTAS_ESTILOS[3],
        [
            "Consultando siempre a mi superior",
            "Tomando decisiones dentro de los márgenes definidos",
            "Tomando decisiones de forma autónoma y luego informando",
        ],
        key="est_4",
    )

    respuestas_estilos["aporte_equipo"] = st.selectbox(
        PREGUNTAS_ESTILOS[4],
        [
            "Organización y planificación",
            "Relaciones y clima de equipo",
            "Resolución de problemas",
            "Gestión de tiempos y plazos",
        ],
        key="est_5",
    )

    if st.button("Registrar preferencias (demo)", key="btn_guardar_estilos"):
        respuestas_estilos["puntaje_demo"] = 100  # demo
        st.session_state["resultados_estilos"] = respuestas_estilos
        registrar_resultado("estilos", respuestas_estilos)
        st.success("Preferencias registradas correctamente.")


# --------------------------------------------------------------------
# BLOQUE DE PRUEBAS PARA POSTULANTE (SIN GRÁFICOS)
# --------------------------------------------------------------------
def mostrar_bloque_pruebas_postulante():
    st.markdown("## Módulo de Pruebas Psicolaborales (Demo)")

    st.write(
        "Complete los siguientes módulos. En la versión definitiva, los resultados serán "
        "analizados por el equipo del INE como parte del proceso de selección."
    )

    tabs = st.tabs(
        [
            "1. Prueba Cognitiva",
            "2. Cuestionario Psicolaboral",
            "3. Inventario de Estilos Laborales",
        ]
    )

    with tabs[0]:
        modulo_prueba_cognitiva()

    with tabs[1]:
        modulo_cuestionario_psicolaboral()

    with tabs[2]:
        modulo_inventario_estilos()

    # Mensaje global solo cuando las tres pruebas tienen resultados
    if (
        st.session_state["resultados_cog"] is not None
        and st.session_state["resultados_psico"] is not None
        and st.session_state["resultados_estilos"] is not None
    ):
        st.success("Se han registrado sus respuestas para todas las pruebas. Muchas gracias.")

    st.info(
        "En la versión definitiva, el equipo del INE revisará sus resultados "
        "en el contexto general del proceso de selección."
    )


# --------------------------------------------------------------------
# FUNCIONES PARA RESUMEN Y EXPORTACIÓN (VISTA ADMIN)
# --------------------------------------------------------------------
def obtener_resultados_para_rut(rut: str):
    datos = st.session_state["resultados_por_postulante"].get(rut)
    if not datos:
        return {}
    resultados = {}

    if datos.get("cognitivo"):
        resultados["Prueba Cognitiva"] = datos["cognitivo"]["puntaje"]

    if datos.get("psico"):
        prom = datos["psico"]["promedio"]
        resultados["Cuestionario Psicolaboral"] = round(prom / 5 * 100)

    if datos.get("estilos"):
        resultados["Estilos Laborales (demo)"] = datos["estilos"].get("puntaje_demo", 100)

    return resultados


def mostrar_resumen_resultados_admin(rut: str):
    resultados = obtener_resultados_para_rut(rut)

    st.markdown(f"#### Resumen Integrado de Resultados (Demo) – RUT {rut}")

    if not resultados:
        st.info("Este postulante aún no tiene resultados registrados en los módulos demo.")
        return

    df = pd.DataFrame(
        {
            "Módulo": list(resultados.keys()),
            "Puntaje": list(resultados.values()),
        }
    )

    chart = (
        alt.Chart(df)
        .mark_bar(size=60)
        .encode(
            x=alt.X("Módulo", sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Puntaje", scale=alt.Scale(domain=[0, 100])),
            tooltip=["Módulo", "Puntaje"],
        )
        .properties(height=350)
    )

    st.altair_chart(chart, use_container_width=True)
    st.caption(
        "Puntajes en escala 0–100 (demo). No representan resultados finales psicométricos."
    )


def construir_dataframe_resultados_global():
    filas = []
    for rut, data in st.session_state["resultados_por_postulante"].items():
        d = data["datos"]
        fila = {
            "rut": rut,
            "nombre": d.get("nombre"),
            "correo": d.get("correo"),
            "telefono": d.get("telefono"),
            "cargo": d.get("cargo"),
            "fecha_registro": d.get("fecha_registro"),
        }

        cog = data.get("cognitivo")
        if cog:
            fila["puntaje_cognitivo_0_100"] = cog["puntaje"]
            fila["aciertos_cognitivo"] = cog["aciertos"]
            fila["total_items_cognitivo"] = cog["total"]
        else:
            fila["puntaje_cognitivo_0_100"] = None
            fila["aciertos_cognitivo"] = None
            fila["total_items_cognitivo"] = None

        psico = data.get("psico")
        if psico:
            fila["prom_psico_1_5"] = psico["promedio"]
            fila["n_items_psico"] = psico["n_items"]
            fila["psico_0_100"] = round(psico["promedio"] / 5 * 100)
        else:
            fila["prom_psico_1_5"] = None
            fila["n_items_psico"] = None
            fila["psico_0_100"] = None

        estilos = data.get("estilos")
        if estilos:
            fila["estilos_0_100_demo"] = estilos.get("puntaje_demo", 100)
        else:
            fila["estilos_0_100_demo"] = None

        filas.append(fila)

    if not filas:
        return pd.DataFrame()

    return pd.DataFrame(filas)


# --------------------------------------------------------------------
# VISTA: ADMINISTRADOR / RECLUTADOR
# --------------------------------------------------------------------
def vista_administrador():
    st.subheader("Panel Administrador INE / Reclutador (Demo)")

    st.info(
        "Esta vista está pensada para profesionales del INE encargados del proceso "
        "de reclutamiento. En la versión final se integrará autenticación segura y "
        "conexión con los sistemas internos del Instituto."
    )

    with st.expander("Acceso administrador (versión demo)"):
        usuario = st.text_input("Usuario:", key="admin_user")
        clave = st.text_input("Contraseña:", type="password", key="admin_pass")
        if st.button("Ingresar (demo)", key="btn_admin_login"):
            if usuario == "admin" and clave == "ine2025":
                st.success("Acceso concedido. Bienvenido/a al panel administrador (demo).")
                st.session_state["admin_autenticado"] = True
            else:
                st.error("Credenciales incorrectas (demo). Intente nuevamente.")
                st.session_state["admin_autenticado"] = False

    if not st.session_state["admin_autenticado"]:
        st.warning(
            "Ingrese con usuario demo para visualizar el panel.\n\n"
            "**Usuario:** `admin`  |  **Clave:** `ine2025`"
        )
        return

    st.markdown("### Postulantes registrados en la sesión (demo)")
    if st.session_state["historial_postulantes"]:
        st.dataframe(st.session_state["historial_postulantes"])
    else:
        st.write("Aún no hay postulantes registrados en esta sesión de demo.")

    if st.session_state["resultados_por_postulante"]:
        st.markdown("### Visualización de resultados por postulante (demo)")

        opciones = [
            f"{rut} - {data['datos'].get('nombre','')}"
            for rut, data in st.session_state["resultados_por_postulante"].items()
        ]

        seleccion = st.selectbox(
            "Seleccione un postulante para ver sus resultados:",
            options=opciones,
        )

        if seleccion:
            rut_sel = seleccion.split(" - ")[0].strip()
            mostrar_resumen_resultados_admin(rut_sel)
    else:
        st.info("Aún no hay resultados asociados a postulantes en esta sesión demo.")

    st.markdown("### Exportar resultados (demo)")
    df_res = construir_dataframe_resultados_global()
    if df_res.empty:
        st.write("No hay resultados para exportar todavía.")
    else:
        csv = df_res.to_csv(index=False)
        st.download_button(
            "Descargar resultados (CSV para Excel)",
            data=csv.encode("utf-8"),
            file_name="resultados_psicolaborales_demo.csv",
            mime="text/csv",
        )

    st.markdown("### Próximos pasos (demo)")
    st.write(
        """
        - Integrar esta plataforma con el sistema interno del INE.  
        - Activar generación automática de informes por postulante.  
        - Habilitar descarga en PDF de informes individuales.  
        - Incorporar filtros por región, cargo y estado del proceso.
        """
    )


# --------------------------------------------------------------------
# APLICACIÓN PRINCIPAL
# --------------------------------------------------------------------
def main():
    mostrar_encabezado()

    st.sidebar.markdown("### Seleccione tipo de acceso")
    tipo_acceso = st.sidebar.selectbox(
        "",
        ("Postulante INE", "Administrador INE / Reclutador"),
        key="tipo_acceso_sidebar",
    )

    if tipo_acceso == "Postulante INE":
        vista_postulante()
    else:
        vista_administrador()


if __name__ == "__main__":
    main()
