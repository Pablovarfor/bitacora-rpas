import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="DroneLog Pro", page_icon="🚁", layout="centered")

st.title("🚁 DroneLog Pro")
st.subheader("Bitácora Digital de Vuelo")

# 1. ESTABLECER CONEXIÓN (El "Puente")
conn = st.connection("gsheets", type=GSheetsConnection)

tab_reg, tab_hist = st.tabs(["📝 Nuevo Registro", "📊 Historial"])

with tab_reg:
    with st.form("form_vuelo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha", datetime.now())
            piloto = st.text_input("Piloto")
            aeronave = st.selectbox("Dron", ["DJI Mavic 3E", "DJI Mini 4 Pro", "Matrice 300", "Otro"])
        with col2:
            lugar = st.text_input("Ubicación")
            h_desp = st.time_input("Despegue")
            h_aterr = st.time_input("Aterrizaje")
        
        st.divider()
        c3, c4 = st.columns(2)
        with c3:
            b_ini = st.slider("Batería Inicial %", 0, 100, 100)
        with c4:
            b_fin = st.slider("Batería Final %", 0, 100, 25)
            
        obs = st.text_area("Observaciones")
        
        # EL BOTÓN DISPARADOR
        submit = st.form_submit_button("Finalizar y Guardar en la Nube")

        if submit:
            # 2. MECANISMO DE SEGURIDAD (Try/Except)
            try:
                # Cálculo de duración
                t1 = datetime.combine(fecha, h_desp)
                t2 = datetime.combine(fecha, h_aterr)
                duracion = str(t2 - t1)

                # Crear el nuevo registro (DataFrame)
                nuevo_registro = pd.DataFrame([{
                    "Fecha": fecha.strftime('%Y-%m-%d'),
                    "Piloto": piloto,
                    "Aeronave": aeronave,
                    "Lugar": lugar,
                    "Despegue": h_desp.strftime('%H:%M'),
                    "Aterrizaje": h_aterr.strftime('%H:%M'),
                    "Duracion": duracion,
                    "Bat_Ini": b_ini,
                    "Bat_Fin": b_fin,
                    "Observaciones": obs
                }])

                # 3. LECTURA Y COMBINACIÓN
                # Leemos lo que hay en el Excel actualmente
                df_actual = conn.read(ttl=0)
                
                # Unimos lo viejo con lo nuevo
                df_final = pd.concat([df_actual, nuevo_registro], ignore_index=True)

                # 4. ACTUALIZACIÓN FINAL (El envío)
                conn.update(data=df_final)
                
                # 5. FEEDBACK VISUAL
                st.success(f"✅ ¡Vuelo guardado! Duración: {duracion}")
                st.balloons()
                
            except Exception as e:
                # Si algo falla, nos dirá exactamente qué es
                st.error(f"❌ Error al guardar: {e}")

with tab_hist:
    st.markdown("### Registros en la Nube")
    try:
        # Mostrar los datos del Excel
        df_ver = conn.read(ttl=0)
        st.dataframe(df_ver, use_container_width=True)
    except:
        st.info("Aún no hay datos para mostrar.")
