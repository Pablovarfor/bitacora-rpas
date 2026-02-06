import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración estética de la página
st.set_page_config(page_title="DroneLog Pro", page_icon="🚁", layout="centered")

# Estilo personalizado con CSS para una interfaz moderna
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #007BFF;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚁 DroneLog Pro")
st.subheader("Bitácora Digital de Vuelo RPAS")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Esto utiliza los secretos que configuraremos en Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para leer datos con caché desactivada para ver cambios al instante
def get_data():
    return conn.read(ttl="0")

# --- INTERFAZ DE USUARIO ---
tab_reg, tab_hist = st.tabs(["📝 Nuevo Registro", "📊 Historial en Vivo"])

# Pestaña 1: Formulario de Registro
with tab_reg:
    st.markdown("### Datos de la Operación")
    with st.form("form_vuelo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha = st.date_input("Fecha de vuelo", datetime.now())
            piloto = st.text_input("Nombre del Piloto", placeholder="Ej: Juan Pérez")
            aeronave = st.selectbox("Aeronave", ["DJI Mavic 3 E", "DJI Matrice 4 E", "Otro"])
            lugar = st.text_input("Ubicación/Lugar", placeholder="Ej: Sector Norte - Antofagasta")
            
        with col2:
            h_ini = st.time_input("Hora Despegue")
            h_fin = st.time_input("Hora Aterrizaje")
            bat_i = st.slider("Batería Inicial %", 0, 100, 100)
            bat_f = st.slider("Batería Final %", 0, 100, 25)
            
        st.divider()
        obs = st.text_area("Observaciones e Incidentes", placeholder="Detalle cualquier novedad durante el vuelo...")
        
        submit = st.form_submit_button("Finalizar y Guardar en la Nube")

        if submit:
            if not piloto or not lugar:
                st.error("⚠️ Por favor, completa los campos obligatorios (Piloto y Lugar).")
            else:
                # Cálculo de duración
                t1 = datetime.combine(fecha, h_ini)
                t2 = datetime.combine(fecha, h_fin)
                
                if t2 <= t1:
                    st.error("❌ Error: La hora de aterrizaje debe ser posterior al despegue.")
                else:
                    duracion = str(t2 - t1)
                    
                    # Preparar el nuevo registro
                    nuevo_vuelo = pd.DataFrame([{
                        "Fecha": fecha.strftime("%Y-%m-%d"),
                        "Piloto": piloto,
                        "Aeronave": aeronave,
                        "Lugar": lugar,
                        "Despegue": h_ini.strftime("%H:%M"),
                        "Aterrizaje": h_fin.strftime("%H:%M"),
                        "Duracion": duracion,
                        "Bat_Ini": int(bat_i),
                        "Bat_Fin": int(bat_f),
                        "Observaciones": obs
                    }])
                    
                    # Actualizar Google Sheets
                    try:
                        df_actual = get_data()
                        df_final = pd.concat([df_actual, nuevo_vuelo], ignore_index=True)
                        conn.update(data=df_final)
                        
                        st.success(f"✅ ¡Vuelo registrado con éxito! Duración total: {duracion}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error al conectar con la base de datos: {e}")

# Pestaña 2: Historial
with tab_hist:
    st.markdown("### Registros de Vuelo")
    try:
        df_ver = get_data()
        if not df_ver.empty:
            # Mostrar tabla interactiva
            st.dataframe(df_ver.sort_index(ascending=False), use_container_width=True)
            
            # Métricas rápidas
            st.divider()
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Vuelos Totales", len(df_ver))
            col_m2.metric("Última Aeronave", df_ver.iloc[-1]["Aeronave"])
        else:
            st.info("Aún no hay registros en la bitácora.")
    except:
        st.warning("Configura los 'Secrets' en Streamlit Cloud para ver el historial.")
