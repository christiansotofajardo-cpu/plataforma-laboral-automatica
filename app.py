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
# INICIALIZACIÓN SEGURA DE SESSION_STATE
# --------------------------------------------------------------------
if "datos_postulante" not in st.session_state:
    st.session_state["datos_postulante"] = None  # guardará un dict

if "postulante_registrado" not in st.session_state:
    st.session_state["postulante_registrado"] = False

if "historial_postulantes" not in st.session_state:
    # lista de dicts con todos los postulantes que han hecho demo
    st.session_state["historial_postulantes"] = []


# --------------------------------------------------------------------
# ENCABEZADO CON LOGO + TÍTULO
# --------------------------------------------------------------------
def mostrar_encabezado():
    col_logo, col_titulo = st.columns([1, 3])

    with col_logo:
        try:
            logo = Image.open("Logo_INE.png")  # el archivo debe estar en la misma carpeta
            st.image(logo, use_column_width=False)
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
# VISTA: POSTULANTE INE
# --------------------------------------------------------------------
def vista_postulante():
    st.subheader("Formulario de Evaluación Psicolaboral")

    st.info(
        "Por favor complete sus datos y responda todas las secciones. "
        "Esta evaluación forma parte del proceso de selección del INE."
    )

    with st.form(key="form_datos_postulante"):
        # NOTA: las keys de widgets son todas distintas a "datos_postulante"
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

    # LÓGICA AL PRESIONAR "Iniciar evaluación"
    if iniciar:
        # Validaciones básicas
        if not rut or not nombre or not correo:
            st.error("Por favor complete al menos RUT, nombre y correo electrónico.")
            st.session_state["postulante_registrado"] = False
            return

        if not acepta_uso_datos:
            st.error("Debe autorizar el uso de datos para continuar con la evaluación.")
            st.session_state["postulante_registrado"] = False
            return

        # Guardamos datos en session_state **sin usar keys de widgets**
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

        # También lo agregamos al historial para la vista administrador (demo)
        st.session_state["historial_postulantes"].append(datos)

    # Si ya está registrado, mostramos mensaje y pasamos a las pruebas
    if st.session_state["postulante_registrado"]:
        st.success("Datos registrados. Continúe con las pruebas.")
        mostrar_bloque_pruebas()
    else:
        st.info("Complete el formulario y presione **Iniciar evaluación** para continuar.")


# --------------------------------------------------------------------
# BLOQUE DE PRUEBAS (DEMO)
# --------------------------------------------------------------------
def mostrar_bloque_pruebas():
    st.markdown("## Módulo de Pruebas Psicolaborales (Demo)")

    st.write(
        "A continuación se presentan de forma simulada las pruebas que formarán parte "
        "del proceso de evaluación psicolaboral. Esta versión es un **demo funcional**."
    )

    tabs = st.tabs(
        [
            "1. Prueba Cognitiva",
            "2. Cuestionario Psicolaboral",
            "3. Inventario de Estilos Laborales",
        ]
    )

    # TAB 1: Prueba Cognitiva (demo)
    with tabs[0]:
        st.markdown("### Prueba Cognitiva – Versión Demo")
        st.write(
            "En la versión final, aquí se presentarán ítems de razonamiento lógico, "
            "memoria de trabajo y atención selectiva."
        )
        st.radio(
            "Ejemplo: ¿Cuál número completa la serie 2, 4, 6, 8, ... ?",
            options=["9", "10", "11", "12"],
            index=1,
            key="demo_cognitiva_1",
        )
        st.button("Enviar respuestas (demo)", key="btn_demo_cognitiva")

    # TAB 2: Cuestionario Psicolaboral (demo)
    with tabs[1]:
        st.markdown("### Cuestionario Psicolaboral – Versión Demo")
        st.write(
            "Aquí se aplicarán escalas breves para evaluar ajuste al rol, "
            "tolerancia a la presión, trabajo en equipo y responsabilidad."
        )
        st.slider(
            "Me siento cómodo/a trabajando bajo presión de tiempo.",
            min_value=1,
            max_value=5,
            key="demo_psico_1",
        )
        st.slider(
            "Me considero una persona ordenada y meticulosa con los datos.",
            min_value=1,
            max_value=5,
            key="demo_psico_2",
        )
        st.button("Guardar respuestas (demo)", key="btn_demo_psico")

    # TAB 3: Inventario de Estilos Laborales (demo)
    with tabs[2]:
        st.markdown("### Inventario de Estilos Laborales – Versión Demo")
        st.write(
            "En esta sección se recogerá información sobre preferencias de trabajo, "
            "autonomía, liderazgo y relación con el equipo."
        )
        st.selectbox(
            "Prefiero trabajar principalmente:",
            ["Solo/a", "En pareja", "En equipos pequeños", "En equipos grandes"],
            key="demo_estilos_1",
        )
        st.button("Registrar preferencias (demo)", key="btn_demo_estilos")

    st.info(
        "En la versión productiva, cada prueba generará puntajes e informes automáticos "
        "que se enviarán al sistema del INE."
    )


# --------------------------------------------------------------------
# VISTA: ADMINISTRADOR / RECLUTADOR
# --------------------------------------------------------------------
def vista_administrador():
    st.subheader("Panel Administrador INE / Reclutador (Demo)")

    st.info(
        "Esta vista está pensada para uso de profesionales del INE encargados del proceso "
        "de reclutamiento. En la versión final se integrará autenticación segura."
    )

    # Autenticación simple de demo
    with st.expander("Acceso administrador (versión demo)"):
        usuario = st.text_input("Usuario:", key="admin_user")
        clave = st.text_input("Contraseña:", type="password", key="admin_pass")
        acceder = st.button("Ingresar (demo)", key="btn_admin_login")

    autenticado = False
    if acceder:
        # Credenciales de DEMO (puedes cambiarlas)
        if usuario == "admin" and clave == "ine2025":
            st.success("Acceso concedido. Bienvenido/a al panel administrador (demo).")
            autenticado = True
        else:
            st.error("Credenciales incorrectas (demo). Intente nuevamente.")
            autenticado = False

    # Para no obligarte a escribir siempre las credenciales en demo,
    # también mostramos el panel si ya hubo accesos previos correctos.
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
