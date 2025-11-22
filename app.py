import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import hashlib
import re # Necesario para la limpieza de prompts

# -------------------- CONFIGURACIÓN INICIAL Y ESTILOS --------------------

st.set_page_config(
    page_title="Sistema de Trámites Documentarios Municipal - Jauja",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS (Sin cambios, manteniendo la estética municipal)
st.markdown("""
<style>
/* --- Colores Institucionales (Azul y Blanco/Gris) --- */
:root {
    --municipal-blue: #0056b3; /* Azul primario fuerte (Institucional) */
    --municipal-light-blue: #007bff; /* Azul de acento */
    --municipal-bg-light: #f8f9fa; /* Fondo muy claro y limpio */
    --municipal-shadow: rgba(0, 86, 179, 0.2); /* Sombra sutil con tono azul */
    --completed-green: #28a745; /* Verde para etapas completadas */
    --pending-gray: #6c757d; /* Gris para etapas pendientes */
}

.stApp {
    background-color: var(--municipal-bg-light); 
}

/* Estilo para el contenedor principal de Streamlit */
.st-emotion-cache-1r6dm7m { 
    padding: 3rem 2rem 10rem;
    max-width: 100%;
}

/* Estilo para el Sidebar */
.st-emotion-cache-10ohe8c { 
    background-color: #ffffff;
    box-shadow: 2px 0 5px rgba(0,0,0,0.05);
}

/* Título Principal (H1) */
h1 {
    color: var(--municipal-blue); 
    border-bottom: 4px solid var(--municipal-light-blue); /* Línea divisoria más prominente */
    padding-bottom: 15px;
    margin-bottom: 30px;
    font-weight: 700;
}

/* Títulos Secundarios (H2/H3) */
h2, h3 {
    color: #343a40; /* Gris oscuro para subtítulos */
    margin-top: 15px;
    margin-bottom: 15px;
}

/* Estilo para los tabs (Pestañas) */
.stTabs [data-baseweb="tab-list"] {
    gap: 24px;
    border-bottom: 2px solid #ced4da; /* Línea suave para las pestañas */
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: nowrap;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding: 10px 20px;
    font-weight: 600;
    color: #6c757d;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--municipal-blue);
    border-bottom: 3px solid var(--municipal-blue);
    background-color: #ffffff;
}

/* Estilo para los mensajes de éxito/error/info (stAlert) */
.stAlert {
    border-radius: 8px;
    box-shadow: 0 4px 12px var(--municipal-shadow); /* Sombra institucional */
    padding: 1rem;
    font-size: 1rem;
}

/* Estilo para el botón primario (type="primary") */
div.stButton > button[kind="primary"] {
    background-color: var(--municipal-blue);
    border: 1px solid var(--municipal-blue);
    color: white;
    font-weight: bold;
    padding: 10px 20px;
    border-radius: 8px;
    transition: background-color 0.3s ease, box-shadow 0.3s ease;
}
div.stButton > button[kind="primary"]:hover {
    background-color: #004a99; /* Tono más oscuro al pasar el mouse */
    border-color: #004a99;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* Estilo para el enlace de descarga de reportes (Gerente) */
.report-link a {
    display: inline-block; 
    padding: 10px 15px; 
    background-color: #17a2b8 !important; /* Color de reporte (Cyan/Info) */
    color: white; 
    text-align: center; 
    text-decoration: none; 
    border-radius: 8px; 
    font-weight: bold; 
    margin-top: 15px;
    transition: background-color 0.3s ease;
}
.report-link a:hover {
    background-color: #117a8b !important;
}

/* Novedad: Estilos para el Timeline */
.timeline-container {
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #ffffff;
    margin-top: 15px;
    margin-bottom: 20px;
}

.timeline-step {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    padding: 5px 0;
    border-left: 2px dashed #ced4da; /* Línea de conexión */
    padding-left: 20px;
    position: relative;
}

.timeline-step.completed {
    border-left: 2px solid var(--completed-green);
}

.timeline-dot {
    position: absolute;
    left: -10px; /* Posición del punto en la línea */
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background-color: var(--pending-gray);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 12px;
}

.timeline-step.completed .timeline-dot {
    background-color: var(--completed-green);
    content: "✓";
}

.timeline-step-content {
    margin-left: 10px;
    font-size: 0.95rem;
}

.timeline-step.completed .timeline-step-content strong {
    color: var(--completed-green);
}
</style>
""", unsafe_allow_html=True)


# -------------------- DATOS Y CONFIGURACIÓN DEL SISTEMA --------------------

def hash_password(password):
    """Simula el hashing de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

PERSONAL_CREDENTIALS = {
    "maria.garcia": hash_password("123456"),
    "roberto.lopez": hash_password("123456"),
    "ana.torres": hash_password("123456"),
    "javier.ruiz": hash_password("123456"),
}
MANAGER_CREDENTIALS = {
    "gerente.general": hash_password("123456")
}

TIPO_TRAMITE = ['Licencia de Construcción', 'Solicitud de Permiso', 'Certificado de Uso de Suelo', 'Queja Ciudadana', 'Reclamo Administrativo']
ESTADOS = ['Pendiente', 'En Revisión', 'Observado', 'Aprobado', 'Rechazado', 'Completado']
PERSONAL_LIST = ['María García (Urbanismo)', 'Roberto López (Obras)', 'Ana Torres (Tesorería)', 'Javier Ruiz (Inspección)', 'Gerente General']
PERSONAL_USUARIOS = list(PERSONAL_CREDENTIALS.keys())
MANAGER_USUARIOS = list(MANAGER_CREDENTIALS.keys())

WORKFLOW_STAGES = {
    'Licencia de Construcción': [
        "1. Ingreso a Mesa de Partes",
        "2. Revisión Documentaria (Urbanismo)",
        "3. Evaluación Técnica (Obras)",
        "4. Inspección en Sitio (Inspección)",
        "5. Emisión de Resolución",
        "6. Notificación y Entrega",
    ],
    'Solicitud de Permiso': [
        "1. Ingreso a Mesa de Partes",
        "2. Evaluación Inicial (Departamento Relevante)",
        "3. Dictamen y Aprobación",
        "4. Notificación de Resolución",
    ],
    'Certificado de Uso de Suelo': [
        "1. Ingreso a Mesa de Partes",
        "2. Verificación de Plano (Urbanismo)",
        "3. Emisión del Certificado",
    ],
    'Queja Ciudadana': [
        "1. Ingreso/Registro",
        "2. Derivación a Área Correspondiente",
        "3. Investigación/Seguimiento",
        "4. Respuesta al Ciudadano",
    ],
    'Reclamo Administrativo': [
        "1. Ingreso Formal",
        "2. Revisión Legal Inicial",
        "3. Evaluación de Fundamentos",
        "4. Resolución Final",
    ]
}

STAGE_MAPPING = {
    'Pendiente': 1, # Solo la primera etapa (Ingreso)
    'En Revisión': 2,
    'Observado': 2, # Observado ocurre durante las revisiones
    'Aprobado': 4, # Se considera aprobado cuando está casi al final
    'Rechazado': 99, # Rechazado es un estado final
    'Completado': 99, # Completado es el estado final (todas las etapas)
}

# -------------------- MANEJO DE ESTADO DE SESIÓN (SESSION STATE) --------------------

if 'tramites' not in st.session_state:
    st.session_state.tramites = [
        {'id': 1001, 'tipo': 'Licencia de Construcción', 'ciudadano': 'Juan Pérez (DNI: 12345678)', 'fecha_envio': '2025-11-01', 'estado': 'En Revisión', 'personal_asignado': 'María García (Urbanismo)', 'fecha_actualizacion': '2025-11-10', 'documento_clave': 'LC-1001-2025', 'archivo_adjunto': 'documento_licencia.pdf', 'observacion_publica': 'Trámite en espera de revisión de planos arquitectónicos.'},
        {'id': 1002, 'tipo': 'Solicitud de Permiso', 'ciudadano': 'Elena Rojas (DNI: 87654321)', 'fecha_envio': '2025-11-05', 'estado': 'Pendiente', 'personal_asignado': 'Sin Asignar', 'fecha_actualizacion': '2025-11-05', 'documento_clave': 'SP-1002-2025', 'archivo_adjunto': 'documento_solicitud.docx', 'observacion_publica': 'Documento ingresado y pendiente de clasificación.'},
        {'id': 1003, 'tipo': 'Certificado de Uso de Suelo', 'ciudadano': 'Carlos Soto (DNI: 11223344)', 'fecha_envio': '2025-11-15', 'estado': 'Observado', 'personal_asignado': 'Roberto López (Obras)', 'fecha_actualizacion': '2025-11-17', 'documento_clave': 'CU-1003-2025', 'archivo_adjunto': 'certificado_uso.pdf', 'observacion_publica': '⚠️ Faltan firmas del notario en el anexo 3. Por favor, subsanar en 5 días hábiles.'},
    ]
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'ciudadao_usuarios' not in st.session_state:
    st.session_state.ciudadao_usuarios = {'Juan Pérez': '12345678', 'Elena Rojas': '87654321', 'Carlos Soto': '11223344'}
# NOVEDAD: Inicialización para el Chatbot
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "text": "¡Hola! Soy tu Asistente Virtual. ¿Cómo puedo ayudarte con tus trámites hoy?"}
    ]
if 'last_search_query' not in st.session_state:
    st.session_state.last_search_query = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = None

# -------------------- FUNCIONES DEL SISTEMA --------------------

def add_new_tramite(tipo, ciudadano_id, ciudadano_nombre, archivo_adjunto, personal_asignado):
    """Añade un nuevo registro de trámite, generando un ID automáticamente."""
    current_ids = [t['id'] for t in st.session_state.tramites]
    new_id = max(current_ids) + 1 if current_ids else 1001
    
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    ciudadano_display = f"{ciudadano_nombre} (DNI: {ciudadano_id})"
    new_record = {
        'id': new_id,
        'tipo': tipo,
        'ciudadano': ciudadano_display,
        'fecha_envio': fecha_hoy,
        'estado': 'Pendiente',
        'personal_asignado': personal_asignado,
        'fecha_actualizacion': fecha_hoy,
        # Documento clave basado en el tipo y el ID
        'documento_clave': tipo.split(' ')[0][:2].upper() + '-' + str(new_id) + '-' + fecha_hoy.split('-')[0],
        'archivo_adjunto': archivo_adjunto.name if archivo_adjunto else 'Sin Archivo',
        'observacion_publica': 'Documento recibido. En proceso de asignación a un área.',
    }
    st.session_state.tramites.append(new_record)
    st.success(f"🎉 Trámite **{new_id}** de {ciudadano_nombre} ingresado con éxito. Estado: Pendiente.")
    st.rerun()

def update_tramite_details(tramite_id, new_data):
    """Actualiza los detalles de un trámite específico (usado por el Personal/Gerente)."""
    for tramite in st.session_state.tramites:
        if tramite['id'] == tramite_id:
            tramite.update(new_data)
            tramite['fecha_actualizacion'] = datetime.now().strftime("%Y-%m-%d")
            return True
    return False

def generate_report_link(df, filename, text, mime_type):
    """Genera un enlace de descarga para el Gerente o reportes generales."""
    # Usar io.BytesIO para manejar el buffer de datos
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    data = csv_buffer.getvalue().encode('utf-8')
    
    b64 = base64.b64encode(data).decode()
    href = f'<div class="report-link"><a href="data:{mime_type};base64,{b64}" download="{filename}"> {text} </a></div>'
    return href

def authenticate_user(username, password, role):
    """Verifica las credenciales del usuario."""
    hashed_pass = hash_password(password)
    if role == "Personal" and username in PERSONAL_CREDENTIALS and PERSONAL_CREDENTIALS[username] == hashed_pass:
        st.session_state.logged_in = True
        st.session_state.user_role = "Personal"
        st.session_state.user_name = next(p for p in PERSONAL_LIST if username in p) # Asigna el nombre completo
        return True
    if role == "Gerente" and username in MANAGER_CREDENTIALS and MANAGER_CREDENTIALS[username] == hashed_pass:
        st.session_state.logged_in = True
        st.session_state.user_role = "Gerente"
        st.session_state.user_name = "Gerente General"
        return True 
    return False

def register_citizen(username, password_dni):
    """Registra un ciudadano (usando DNI/ID como 'contraseña')."""
    st.session_state.ciudadao_usuarios[username] = password_dni
    st.session_state.logged_in = True
    st.session_state.user_role = "Ciudadano"
    st.session_state.user_name = username
    st.session_state.user_id = password_dni
    return "registrado"

def logout():
    """Cierra la sesión del usuario."""
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_name = None
    st.session_state.user_id = None
    # NOVEDAD: Limpiar historial de chat al salir
    st.session_state.chat_history = [
        {"role": "assistant", "text": "¡Hola! Soy tu Asistente Virtual. ¿Cómo puedo ayudarte con tus trámites hoy?"}
    ]
    st.info("Ha cerrado sesión con éxito.")
    st.rerun()

def login_ui():
    """Muestra la interfaz de inicio de sesión o registro."""
    st.sidebar.markdown("## 🔒 Iniciar Sesión")
    tabs = st.tabs(["🏛️ Personal/Gerente", "👥 Ciudadano"])
    
    with tabs[0]: # Personal/Gerente Login
        st.subheader("Acceso Administrativo")
        admin_role = st.radio("Seleccione su Rol", ["Personal", "Gerente"])
        admin_placeholder = "Ej: maria.garcia o gerente.general"
        admin_username = st.text_input("Usuario", key="admin_user", placeholder=admin_placeholder)
        admin_password = st.text_input("Contraseña", type="password", key="admin_pass", placeholder="123456")
        
        if st.button(f"Entrar como {admin_role}", key="login_btn", type="primary"):
            if authenticate_user(admin_username, admin_password, admin_role):
                st.success(f"¡Bienvenido, {st.session_state.user_name}!")
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Intente de nuevo.")
                
    with tabs[1]: # Ciudadano Login/Register
        st.subheader("Acceso Ciudadano (Registro/Consulta)")
        
        st.info("Para este sistema de prueba, su ID o DNI será usado como su clave de acceso. **El DNI debe ser de 8 dígitos.**")
        
        citizen_name = st.text_input("Nombre Completo (Ej: Juan Pérez)", key="citizen_name")
        # Aseguramos que solo sean 8 dígitos
        citizen_id = st.text_input("DNI o ID Único (8 dígitos numéricos)", key="citizen_id", max_chars=8) 
        
        if st.button("Ingresar / Registrarse", key="register_btn", type="primary"): 
            if citizen_name and citizen_id:
                if not (citizen_id.isdigit() and len(citizen_id) == 8):
                    st.error("⚠️ Error de DNI: Debe ingresar exactamente 8 dígitos numéricos.")
                    return
                
                is_registered = citizen_name in st.session_state.ciudadao_usuarios
                
                if is_registered:
                    # Intento de LOGIN para usuario existente
                    if st.session_state.ciudadao_usuarios[citizen_name] == citizen_id:
                        st.session_state.logged_in = True
                        st.session_state.user_role = "Ciudadano"
                        st.session_state.user_name = citizen_name
                        st.session_state.user_id = citizen_id
                        st.success(f"Sesión iniciada como Ciudadano: {citizen_name}.")
                        st.rerun()
                    else:
                        st.error("Credenciales de Ciudadano incorrectas. El DNI ingresado no coincide con el nombre registrado.")
                else:
                    # REGISTRO de nuevo ciudadano (DNI ya validado como 8 dígitos)
                    register_citizen(citizen_name, citizen_id)
                    st.success(f"Registro exitoso. ¡Bienvenido, {citizen_name}!")
                    st.rerun() 
            else:
                st.error("Por favor, ingrese su Nombre Completo y DNI/ID.")

def display_tramite_timeline(tramite):
    """Muestra un visualizador de trazabilidad del trámite."""
    tipo = tramite['tipo']
    estado = tramite['estado']
    if tipo not in WORKFLOW_STAGES:
        st.warning(f"No hay un flujo definido para el tipo de trámite: {tipo}")
        return
        
    stages = WORKFLOW_STAGES[tipo]
    
    if estado == 'Completado' or estado == 'Rechazado':
        stages_completed_count = len(stages) 
    else:
        stages_completed_count = STAGE_MAPPING.get(estado, 1)

    st.markdown(f"**Flujo de Proceso: {tipo}**")
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)

    for i, stage in enumerate(stages):
        is_current_or_completed = (i + 1) <= stages_completed_count
        
        status_text = ""
        dot_class = ""
        
        if estado == 'Rechazado' and i == 0:
            st.markdown(f"""
                <div class="timeline-step completed">
                    <span class="timeline-dot">✓</span>
                    <div class="timeline-step-content">
                        <strong>Trámite INGRESADO</strong>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div class="timeline-step">
                    <span class="timeline-dot" style="background-color: #dc3545;">✖</span>
                    <div class="timeline-step-content">
                        <strong>RECHAZADO</strong> - Ver observaciones.
                    </div>
                </div>
            """, unsafe_allow_html=True)
            break
            
        elif estado == 'Completado':
             st.markdown(f"""
                <div class="timeline-step completed">
                    <span class="timeline-dot">✓</span>
                    <div class="timeline-step-content">
                        <strong>{stage}</strong> - ✓ FINALIZADO
                    </div>
                </div>
              """, unsafe_allow_html=True)
             
        elif estado != 'Rechazado' and estado != 'Completado':
            if is_current_or_completed:
                 dot_class = "completed"
                 status_text = f"<strong>{stage}</strong> - Revisado"
                 if (i + 1 == stages_completed_count):
                    status_text = f"<strong>{stage}</strong> - ⏳ <strong>ETAPA ACTUAL</strong>"
            else:
                 status_text = f"<strong>{stage}</strong> - Pendiente"
                 
            st.markdown(f"""
                <div class="timeline-step {'completed' if is_current_or_completed else ''}">
                    <span class="timeline-dot">{'✓' if is_current_or_completed and (i + 1 < stages_completed_count) else str(i+1)}</span>
                    <div class="timeline-step-content">
                        {status_text}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("##### 📢 Observación y Estado Actual")
    
    # Manejo del mensaje de estado actual
    if estado == 'Observado':
        st.error(f"**ATENCIÓN - SUBSANACIÓN REQUERIDA:** {tramite['observacion_publica']}")
    elif estado == 'Rechazado':
        st.error(f"**TRÁMITE RECHAZADO DEFINITIVAMENTE:** {tramite['observacion_publica']}")
    elif estado == 'Aprobado':
        st.success(f"**APROBADO, EN ESPERA DE FIRMA/ENTREGA:** {tramite['observacion_publica']}")
    elif estado == 'Completado':
        st.balloons()
        st.success(f"**TRÁMITE FINALIZADO CON ÉXITO.** {tramite['observacion_publica']}")
    else:
        st.info(f"**Mensaje del Área:** {tramite['observacion_publica']}")
    
    st.markdown(f"**Última Modificación:** {tramite['fecha_actualizacion']}")
    st.markdown(f"**Área Asignada:** {tramite['personal_asignado']}")


# -------------------- FUNCIONES DEL CHATBOT --------------------

@st.cache_data(show_spinner=False)
def get_workflow_info(tipo_tramite):
    """Genera la información detallada del flujo de trabajo."""
    if tipo_tramite in WORKFLOW_STAGES:
        stages = WORKFLOW_STAGES[tipo_tramite]
        info = f"El flujo para **{tipo_tramite}** es:\n"
        for i, stage in enumerate(stages):
            info += f"**{i+1}.** {stage}\n"
        info += "\nSi desea saber el estado de un trámite específico, vaya a la pestaña 'Consultar Mis Trámites'."
    else:
        info = f"No tengo información detallada del flujo para el trámite '{tipo_tramite}'. Los trámites disponibles son: {', '.join(TIPO_TRAMITE)}."
    return info

def get_chatbot_response(user_prompt):
    """Determina la respuesta del chatbot (uso de lógica interna o búsqueda externa)."""
    user_prompt_lower = user_prompt.lower()
    
    # 1. Trámite status check simulation
    if "estado" in user_prompt_lower or "estatus" in user_prompt_lower or "seguimiento" in user_prompt_lower or "mi trámite" in user_prompt_lower:
        return "Para consultar el estado y la trazabilidad de su trámite, por favor, vaya a la pestaña **'📋 Consultar Mis Trámites'** y seleccione el ID de su documento. Ahí encontrará el **Timeline** y la observación actual."

    # 2. Workflow stages check (Internal data)
    for t in TIPO_TRAMITE:
        if t.lower() in user_prompt_lower:
            return get_workflow_info(t)

    # 3. How to submit (Internal data)
    if "ingresar trámite" in user_prompt_lower or "enviar documento" in user_prompt_lower or "formulario" in user_prompt_lower:
        return "Para ingresar un nuevo trámite, vaya a la pestaña **'📧 Ingreso Nuevo Trámite'**, seleccione el **Tipo de Trámite** y adjunte su documento (PDF/DOCX/TXT). Luego haga clic en 'Enviar Nuevo Trámite'. Su trámite se registrará automáticamente a su nombre y DNI."

    # 4. Fallback/Greeting (Internal data)
    if "hola" in user_prompt_lower or "ayuda" in user_prompt_lower or "gracias" in user_prompt_lower:
        if "gracias" in user_prompt_lower:
             return "¡De nada! Estoy aquí para ayudarte con cualquier otra duda."
        return "¡Hola! Soy tu Asistente Virtual de la Municipalidad de Jauja. Estoy aquí para ayudarte con preguntas sobre nuestros trámites. Puedes preguntar: \n\n- ¿Cómo ingresar un nuevo trámite? \n- ¿Cuál es el flujo para una Licencia de Construcción? \n\nPara estados de trámites, use la pestaña 'Consultar Mis Trámites'."

    # 5. General municipal definitions (Trigger Google Search tool)
    if "qué es" in user_prompt_lower or "documentos para" in user_prompt_lower or "requisitos" in user_prompt_lower:
        st.session_state.last_search_query = user_prompt # Flag the search
        return "Un momento, estoy buscando información municipal oficial sobre eso... Por favor, espere un segundo mientras consulto la web."
        
    return "Lo siento, no entendí esa pregunta. Soy un asistente especializado en trámites municipales. Por favor, reformúlela o pregunte sobre un tipo de trámite específico (Ej: ¿Qué es una Queja Ciudadana?)"


def display_chatbot_ui():
    """Interfaz del Asistente Virtual para el Ciudadano."""
    st.markdown("### 🤖 Asistente Virtual Municipal")
    st.info("Soy un chatbot diseñado para orientarte en el uso del sistema y los procedimientos documentarios. Puedo usar información externa (Google Search) para respuestas generales.")

    # 1. Manejo de la consulta externa (Google Search)
    if st.session_state.last_search_query:
        # Aquí se realiza la llamada simulada al LLM con Google Search.
        # La estructura de la llamada es manejada por el entorno, pero se
        # simula la lógica de uso del prompt y la respuesta.
        with st.spinner(f"Buscando información para: **{st.session_state.last_search_query}**..."):
            
            # Limpiamos el query y añadimos contexto
            clean_query = re.sub(r'[^a-zA-Z0-9\s]', '', st.session_state.last_search_query)
            queries = [clean_query + " requisitos Jauja", "trámites municipales Jauja"]

            try:
                # Llamada al Google Search Tool
                tool_response = google.search(queries=queries)
                
                search_result_text = tool_response['result'] if tool_response and 'result' in tool_response else "No se encontraron resultados relevantes."

                # Simulamos la respuesta final del LLM usando la información obtenida
                llm_summary = f"**Resultado de la búsqueda para '{st.session_state.last_search_query}'**:\n\n"
                
                # Simulación de LLM Summary: si hay resultados, los usa, si no, usa un genérico.
                if "web" in search_result_text:
                    # Usamos solo una parte de la respuesta para no saturar
                    snippet = search_result_text.split('\n')[0]
                    llm_summary += f"*{snippet}...*\n\n**Nota del Asistente:** La información detallada y oficial (como formularios y costos) debe ser verificada en la documentación TUPA (Texto Único de Procedimientos Administrativos) de la Municipalidad de Jauja."
                else:
                    llm_summary += "No se encontró información específica en la web de la municipalidad. Generalmente, estos trámites requieren el DNI, solicitud formal y planos/documentación técnica. Le sugiero revisar la sección de TUPA en el portal web oficial."

                st.session_state.chat_history.append({"role": "assistant", "text": llm_summary})
                
            except Exception as e:
                st.session_state.chat_history.append({"role": "assistant", "text": f"Ocurrió un error al buscar información externa. Por favor, intente con otra pregunta o revise la documentación municipal."})
                
            # Limpiar el estado de búsqueda
            st.session_state.last_search_query = None
            st.rerun() 
            return # Salir del flujo para que el rerun muestre el nuevo mensaje


    # 2. Mostrar Historial de Chat
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])

    # 3. Formulario de Input
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("Escribe tu pregunta aquí:", key="user_chat_input", placeholder="Ej: ¿Cuál es el flujo para una Licencia de Construcción?")
        send_button = st.form_submit_button("Enviar Mensaje", type="primary")

        if send_button and user_input:
            # Añadir mensaje del usuario y obtener respuesta del asistente
            st.session_state.chat_history.append({"role": "user", "text": user_input})
            assistant_response = get_chatbot_response(user_input)
            
            if "Un momento, estoy buscando información municipal oficial sobre eso..." not in assistant_response:
                # Respuesta inmediata (interna)
                st.session_state.chat_history.append({"role": "assistant", "text": assistant_response})
            
            # Disparar un rerun para procesar el mensaje o la búsqueda
            st.rerun()


# -------------------- ESTRUCTURA PRINCIPAL DE LA APLICACIÓN --------------------

if st.session_state.logged_in:
    current_role_display = {
        "Personal": "Personal (Mesa de Partes)",
        "Gerente": "Gerente (Auditoría)",
        "Ciudadano": "Ciudadano (Ingreso y Consulta)"
    }[st.session_state.user_role]
    
    st.sidebar.markdown(f"**👤 Usuario:** `{st.session_state.user_name}`")
    if st.session_state.user_role == "Ciudadano":
        st.sidebar.markdown(f"**🆔 DNI:** `{st.session_state.user_id}`")
    st.sidebar.markdown(f"**📍 Rol Activo:** `{current_role_display}`")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Cerrar Sesión", on_click=logout, type="secondary"): 
        pass 
        
    df_tramites = pd.DataFrame(st.session_state.tramites)
    st.title(f"🏛️ Sistema de Trámites: {current_role_display}")
    st.markdown("---")
    
    # -------------------- VISTA PERSONAL --------------------
    if st.session_state.user_role == "Personal":
        st.subheader(f"Bandeja de Trámites para {st.session_state.user_name}")
        personal_seleccionado = st.session_state.user_name
        df_mi_bandeja = df_tramites[
            (df_tramites['personal_asignado'] == personal_seleccionado) | 
            (df_tramites['personal_asignado'] == 'Sin Asignar')
        ].sort_values(by='fecha_envio', ascending=True).reset_index(drop=True)
        
        st.info(f"Mostrando **{len(df_mi_bandeja)}** trámites pendientes o asignados a usted. Recuerde tomar los trámites 'Sin Asignar'.")
        
        edited_tramites = st.data_editor(
            df_mi_bandeja,
            column_config={
                "id": st.column_config.Column("ID Trámite", disabled=True),
                "ciudadano": st.column_config.Column("Ciudadano", disabled=True),
                "fecha_envio": st.column_config.DateColumn("Fecha Envío", disabled=True),
                "documento_clave": st.column_config.Column("Documento Clave", disabled=True),
                "fecha_actualizacion": st.column_config.DateColumn("Última Actualización", disabled=True),
                "archivo_adjunto": st.column_config.Column("Archivo Adjunto", disabled=True),
                "tipo": st.column_config.SelectboxColumn(
                    "Tipo de Trámite",
                    options=TIPO_TRAMITE,
                    required=True,
                ),
                "personal_asignado": st.column_config.SelectboxColumn(
                    "Personal Asignado",
                    options=PERSONAL_LIST + ["Sin Asignar"],
                    required=True,
                    default=personal_seleccionado
                ),
                "estado": st.column_config.SelectboxColumn(
                    "Estado de Progreso",
                    options=ESTADOS,
                    required=True
                ),
                "observacion_publica": st.column_config.TextColumn(
                    "Observación Pública (Ciudadano)",
                    help="Mensaje de estado o requisito visible para el ciudadano.",
                    width='large'
                )
            },
            use_container_width=True,
            hide_index=True,
            key="personal_data_editor"
        )
        
        if not edited_tramites.equals(df_mi_bandeja):
            st.warning("Se han detectado cambios en la tabla. Presione 'Guardar Cambios' para actualizar el sistema.")
            if st.button("💾 Guardar Cambios de Trámites", type="primary"):
                changes_made = False
                for index, row in edited_tramites.iterrows():
                    tramite_id = row['id']
                    original_tramite = next((t for t in st.session_state.tramites if t['id'] == tramite_id), None)
                    
                    if original_tramite:
                        update_data = {}
                        if original_tramite['estado'] != row['estado']:
                            update_data['estado'] = row['estado']
                        if original_tramite['personal_asignado'] != row['personal_asignado']:
                            update_data['personal_asignado'] = row['personal_asignado']
                        if original_tramite['tipo'] != row['tipo']:
                            update_data['tipo'] = row['tipo']
                        if original_tramite.get('observacion_publica') != row.get('observacion_publica'):
                             update_data['observacion_publica'] = row.get('observacion_publica', 'Sin observación.')
                        
                        if update_data:
                            update_tramite_details(tramite_id, update_data)
                            changes_made = True

                if changes_made:
                    st.success("Cambios en los trámites guardados con éxito y fecha de actualización registrada.")
                else:
                    st.info("No se detectaron cambios a guardar.")
                st.rerun() 
                
        st.markdown("---")
        st.subheader("Simulación de Descarga de Documentos")
        
        if not df_mi_bandeja.empty:
            tramite_id_to_download = st.selectbox(
                "Seleccione el ID del trámite para descargar el archivo adjunto:",
                options=df_mi_bandeja['id'].tolist(),
                key="personal_download_select"
            )
            if tramite_id_to_download:
                tramite_info = df_mi_bandeja[df_mi_bandeja['id'] == tramite_id_to_download].iloc[0]
                doc_name = tramite_info['archivo_adjunto']
                doc_content = (
                    f"--- ARCHIVO ADJUNTO SIMULADO ---\n"
                    f"Trámite ID: {tramite_info['id']}\n"
                    f"Ciudadano: {tramite_info['ciudadano']}\n"
                    f"Tipo: {tramite_info['tipo']}\n"
                    f"Estado: {tramite_info['estado']}\n"
                    f"Observación: {tramite_info['observacion_publica']}\n"
                    f"Asignado a: {tramite_info['personal_asignado']}\n"
                )
                st.download_button(
                    label=f"⬇️ Descargar Archivo: {doc_name}",
                    data=doc_content.encode('utf-8'),
                    file_name=doc_name,
                    mime='text/plain',
                    type="secondary" 
                )

    # -------------------- VISTA CIUDADANO (CON CHATBOT) --------------------
    elif st.session_state.user_role == "Ciudadano":
        st.subheader(f"Bienvenido(a), {st.session_state.user_name} (ID: {st.session_state.user_id})")
        
        # NOVEDAD: Se añade la pestaña del Asistente Virtual
        tabs = st.tabs(["📧 Ingreso Nuevo Trámite", "📋 Consultar Mis Trámites", "🤖 Asistente Virtual"])
        
        with tabs[0]: # Ingreso de Trámite
            with st.form(key='add_tramite_form', clear_on_submit=True):
                st.markdown("#### Formulario de Presentación")
                st.info("Su nombre y ID ya están registrados en el sistema para este trámite.")
                col_form_c1, col_form_c2 = st.columns(2)
                with col_form_c1:
                    tipo_tramite = st.selectbox("Tipo de Trámite a Ingresar", options=TIPO_TRAMITE) 
                with col_form_c2:
                    archivo_adjunto = st.file_uploader("Adjuntar Documento", type=['pdf', 'docx', 'txt'])
                    personal_asignado_inicial = "Sin Asignar" 
                submit_button = st.form_submit_button(label='🚀 Enviar Nuevo Trámite', type="primary")
                if submit_button:
                    if tipo_tramite and archivo_adjunto:
                        add_new_tramite(tipo_tramite, st.session_state.user_id, st.session_state.user_name, archivo_adjunto, personal_asignado_inicial)
                    else:
                        st.error("⚠️ Debe seleccionar el tipo de trámite y adjuntar un archivo.") 
                        
        with tabs[1]: # Consulta de Estado
            st.markdown("#### Historial y Estado de sus Trámites (Trazabilidad)")
            citizen_display_name = f"{st.session_state.user_name} (DNI: {st.session_state.user_id})"
            df_mis_tramites = df_tramites[df_tramites['ciudadano'] == citizen_display_name]
            
            if not df_mis_tramites.empty:
                st.success(f"✅ Se encontraron **{len(df_mis_tramites)}** trámites a su nombre. Seleccione uno para ver la trazabilidad.")
                selected_tramite_id = st.selectbox(
                    "Seleccione el ID del Trámite para ver el detalle:",
                    options=df_mis_tramites['id'].tolist(),
                    format_func=lambda x: f"ID {x} - {df_mis_tramites[df_mis_tramites['id'] == x]['tipo'].iloc[0]} ({df_mis_tramites[df_mis_tramites['id'] == x]['estado'].iloc[0]})"
                )
                if selected_tramite_id:
                    tramite_dict = next(t for t in st.session_state.tramites if t['id'] == selected_tramite_id)
                    st.markdown("---")
                    st.subheader(f"Detalle y **Timeline** del Trámite ID: {selected_tramite_id}")
                    display_tramite_timeline(tramite_dict) 
            else:
                st.warning("Aún no ha ingresado ningún trámite.")
                
        with tabs[2]: # NOVEDAD: Asistente Virtual
            display_chatbot_ui()


    # -------------------- VISTA GERENTE --------------------
    elif st.session_state.user_role == "Gerente":
        
        st.subheader("Vista Global de Trámites y Auditoría")
        st.info("Panel de control para la trazabilidad completa y monitoreo de indicadores clave.")
        
        if df_tramites.empty:
            st.warning("No hay trámites registrados en el sistema.")
        else:
            estados_filtro = st.multiselect(
                "Filtrar por Estado de Trámite",
                options=ESTADOS,
                default=['Pendiente', 'En Revisión', 'Observado', 'Aprobado', 'Rechazado', 'Completado']
            )
            df_auditoria = df_tramites[df_tramites['estado'].isin(estados_filtro)].copy()
 
            today = datetime.now()
            df_auditoria['fecha_envio'] = pd.to_datetime(df_auditoria['fecha_envio'])
            df_auditoria['dias_antiguedad'] = (today - df_auditoria['fecha_envio']).dt.days

            st.dataframe(
                df_auditoria[[
                    'id', 
                    'tipo', 
                    'ciudadano', 
                    'fecha_envio', 
                    'estado', 
                    'personal_asignado', 
                    'fecha_actualizacion',
                    'dias_antiguedad',
                    'observacion_publica' 
                ]].sort_values(by='fecha_envio', ascending=False),
                column_config={
                    "id": "ID",
                    "tipo": "Tipo de Trámite",
                    "ciudadano": "Ciudadano Atendido",
                    "fecha_envio": st.column_config.DateColumn("Fecha Envío", format="YYYY-MM-DD"),
                    "estado": "Estado",
                    "personal_asignado": "Personal Responsable",
                    "fecha_actualizacion": st.column_config.DateColumn("Última Modificación", format="YYYY-MM-DD"),
                    "dias_antiguedad": st.column_config.NumberColumn("Antigüedad (Días)", format="%d días", help="Días transcurridos desde el envío inicial."),
                    "observacion_publica": "Última Observación" 
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.markdown("---")
            st.subheader("📊 Reportes Gerenciales y KPIs de Eficiencia")
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.metric(
                    "Trámites Críticos (Pendientes/Revisión)", 
                    df_auditoria[df_auditoria['estado'].isin(['Pendiente', 'En Revisión', 'Observado'])].shape[0],
                    delta=df_auditoria[df_auditoria['estado'] == 'Completado'].shape[0], # Delta muestra los completados
                    delta_color="normal"
                )
                st.bar_chart(df_auditoria['estado'].value_counts().sort_index())
                st.caption("Distribución de Trámites por Estado")

            with col_g2:
                avg_age = int(df_auditoria['dias_antiguedad'].mean()) if not df_auditoria.empty else 0
                st.metric("Días Promedio de Proceso", avg_age, help="Indica la eficiencia promedio.")
                st.bar_chart(df_auditoria['personal_asignado'].value_counts().sort_index())
                st.caption("Carga de Trabajo por Personal Asignado")
                
            st.markdown("---")
            st.markdown(
                generate_report_link(df_auditoria, "auditoria_tramites_global.csv", "⬇️ Descargar Reporte Completo de Auditoría (CSV)", 'text/csv'), 
                unsafe_allow_html=True
            ) 
else:
    login_ui()
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
        **Credenciales de Prueba:**
        - **Personal:** `maria.garcia` / `123456`
        - **Gerente:** `gerente.general` / `123456`
        - **Ciudadano:** Nombre a su elección y **DNI de 8 dígitos** (Ej: `11112222`).
    """)