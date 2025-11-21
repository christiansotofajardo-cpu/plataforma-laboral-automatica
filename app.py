import streamlit as st
from PIL import Image
from datetime import datetime

# --------------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# --------------------------------------------------------------------
st.set_page_config(
    page_title="Plataforma de Evaluación Psicolaboral – INE",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------------------------
# BANCOS DE ÍTEMS (EJEMPLOS – REEMPLAZAR POR ÍTEMS REALES)
# --------------------------------------------------------------------
PREGUNTAS_COGNITIVAS = [
    {
        "id": 1,
        "enunciado": "¿Qué número completa la serie 2, 4, 6, 8, ... ?",
        "opciones": ["9", "10", "11", "12"],
        "correcta": 1,  # índice de la opción correcta (0,1,2,3)
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
]


# --------------------------------------------------------------------
# INICIALIZACIÓN DE SESSION_STATE
# --------------------------------------------------------------------
if "datos_postulante" not in st.session_state:
    st.session_state["datos_postulante"] = None

if "postulante_registrado" not in st.session_state:
    st.session_state["postulante_registrado"] = False

if "historial_postulantes" not in st.session_state:
    st.session_state["historial_postulantes"] = []

# Estado para prueba cognitiva
if "indice_cog" not in st.session_state:
    st.session_state["indice_cog"] = 0

if "resultados_cog" not in st.session_state:
    st.session_state["resultados_cog"] = None

# Resultados de otros módulos (placeholder)
if "resultados_psico" not in st.session_state:
    st.session_state["resultados_psico"] = None

if "resultados_estilos" not in st.session_state:
    st.session_state["resultados_estilos"] = None


# --------------------------------------------------------------------
# ENCABEZADO CON LOGO + TÍTULO
# --------------------------------------------------------------------
def mostrar_encabezado():
    col_logo, col_titulo = st.columns([1, 3])

    with col_logo:
        try:
            logo = Image.open("Logo_INE.png")  # debe estar en la misma carpeta que app.py
            st.image(logo, width=180)  # tamaño controlado
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
            return

        if not acepta_uso_datos:
            st.error("Debe autorizar el uso de datos para continuar con la evaluación.")
            st.session_state["postulante_registrado"] = False
            return

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

    if st.session_state["postulante_registrado"]:
        st.success("Datos registrados. Continúe con las pruebas.")
        mostrar_bloque_pruebas()
    else:
        st.info("Complete el formulario y presione **Iniciar evaluación** para continuar.")


# --------------------------------------------------------------------
# MÓDULO: PRUEBA COGNITIVA COMPLETA
# --------------------------------------------------------------------
def modulo_prueba_cognitiva():
    st.markdown("### Prueba Cognitiva – Versión Demo Extendida")
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

    if col1.button("◀ Anterior", disabled=(indice == 0)):
        st.session_state["indice_cog"] = max(0, indice - 1)

    if col2.button("Siguiente ▶", disabled=(indice == n_preg - 1)):
        st.session_state["indice_cog"] = min(n_preg - 1, indice + 1)

    if col3.button("Finalizar prueba"):
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
            st.warning("Debe responder al menos una pregunta para calcular un puntaje.")
        else:
            puntaje = round(aciertos / n_preg * 100)
            st.session_state["resultados_cog"] = {
                "aciertos": aciertos,
                "total": n_preg,
                "puntaje": puntaje,
            }

    if st.session_state["resultados_cog"] is not None:
        res = st.session_state["resultados_cog"]
        st.success(
            f"Resultado prueba cognitiva: {res['aciertos']} de {res['total']} "
            f"aciertos ({res['puntaje']} puntos sobre 100)."
        )


# --------------------------------------------------------------------
# MÓDULO: CUESTIONARIO PSICOLABORAL
# --------------------------------------------------------------------
def modulo_cuestionario_psicolaboral():
    st.markdown("### Cuestionario Psicolaboral – Versión Demo Extendida")
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

    if st.button("Guardar respuestas cuestionario"):
        promedio = sum(respuestas) / len(respuestas)
        st.session_state["resultados_psico"] = {
            "promedio": round(promedio, 2),
            "n_items": len(respuestas),
        }

    if st.session_state["resultados_psico"] is not None:
        res = st.session_state["resultados_psico"]
        st.info(
            f"Promedio global del cuestionario: **{res['promedio']}** "
            f"(sobre 5, en {res['n_items']} ítems)."
        )


# --------------------------------------------------------------------
# MÓDULO: INVENTARIO DE ESTILOS LABORALES
# --------------------------------------------------------------------
def modulo_inventario_estilos():
    st.markdown("### Inventario de Estilos Laborales – Versión Demo")
    st.write(
        "Este módulo recoge información sobre sus preferencias de trabajo y estilo "
        "de funcionamiento en equipo."
    )

    opciones_trabajo = [
        "Solo/a",
        "En pareja",
        "En equipos pequeños",
        "En equipos grandes",
    ]

    respuestas_estilos = {}

    respuestas_estilos["forma_trabajo"] = st.selectbox(
        PREGUNTAS_ESTILOS[0],
        opciones_trabajo,
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

    if st.button("Registrar preferencias (demo)"):
        st.session_state["resultados_estilos"] = respuestas_estilos

    if st.session_state["resultados_estilos"] is not None:
        st.success("Preferencias registradas (demo).")
        st.json(st.session_state["resultados_estilos"])


# --------------------------------------------------------------------
# BLOQUE GENERAL DE PRUEBAS
# --------------------------------------------------------------------
def mostrar_bloque_pruebas():
    st.markdown("## Módulo de Pruebas Psicolaborales")

    st.write(
        "A continuación se presentan, en formato demo, los módulos que conformarán la "
        "evaluación psicolaboral automatizada. En la versión productiva se integrarán "
        "bancos completos de ítems e informes automáticos."
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

    st.info(
        "En la versión definitiva, los resultados de cada módulo se integrarán en un "
        "informe psicométrico global para el INE."
    )


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
        acceder = st.button("Ingresar (demo)", key="btn_admin_login")

    autenticado = False
    if acceder:
        if usuario == "admin" and clave == "ine2025":
            st.success("Acceso concedido. Bienvenido/a al panel administrador (demo).")
            autenticado = True
        else:
            st.error("Credenciales incorrectas (demo). Intente nuevamente.")
            autenticado = False

    if autenticado or st.session_state["historial_postulantes"]:
        st.markdown("### Postulantes registrados en la sesión (demo)")
        if st.session_state["historial_postulantes"]:
            st.dataframe(st.session_state["historial_postulantes"])
        else:
            st.write("Aún no hay postulantes registrados en esta sesión de demo.")

        st.markdown("### Próximos pasos (demo)")
        st.write(
            """
            - Integrar esta plataforma con el sistema interno del INE.  
            - Activar generación automática de informes por postulante.  
            - Habilitar descarga en PDF y exportación a Excel.  
            - Incorporar filtros por región, cargo y estado del proceso.
            """
        )
    else:
        st.warning(
            "Ingrese con usuario demo para visualizar el panel.\n\n"
            "**Usuario:** `admin`  |  **Clave:** `ine2025`"
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
