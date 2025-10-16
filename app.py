import streamlit as st
import pandas as pd
from scraper import PrognolScraper
from quiniela_generator import QuinielaGenerator
from database import QuinielaDatabase
from image_exporter import QuinielaImageExporter
import time
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Generador de Quinielas Progol",
    page_icon="🎯",
    layout="wide"
)

# Inicializar objetos en session state
if 'scraper' not in st.session_state:
    st.session_state.scraper = PrognolScraper()
    st.session_state.generator = QuinielaGenerator()
    st.session_state.db = QuinielaDatabase()
    st.session_state.exporter = QuinielaImageExporter()
    st.session_state.partidos = []
    st.session_state.quinielas = []
    st.session_state.vista_actual = "generar"
    st.session_state.info_sorteo = None

# Obtener información del sorteo
if st.session_state.info_sorteo is None:
    st.session_state.info_sorteo = st.session_state.scraper.get_info_sorteo()

# Título principal
st.title("🎯 Generador de Quinielas Progol")
st.markdown("**Genera quinielas aleatorias con los partidos actuales de Progol**")

# Mostrar información del sorteo
if st.session_state.info_sorteo:
    info = st.session_state.info_sorteo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"📅 {info.get('fecha_sorteo', 'Sin fecha')}")
    with col2:
        st.info(f"🏆 {info.get('jornada', 'Jornada actual')}")
    with col3:
        st.info(f"💰 {info.get('premios', 'Premios por confirmar')}")

# Sidebar para controles
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Selector de vista
    vista = st.radio(
        "Vista:",
        ["🎲 Generar Quinielas", "📚 Historial"],
        index=0 if st.session_state.vista_actual == "generar" else 1
    )
    
    st.session_state.vista_actual = "generar" if "Generar" in vista else "historial"
    
    st.divider()
    
    if st.session_state.vista_actual == "generar":
        # Botón para actualizar partidos
        if st.button("🔄 Actualizar Partidos", use_container_width=True):
            with st.spinner("Obteniendo partidos actuales..."):
                try:
                    partidos = st.session_state.scraper.get_partidos()
                    if partidos:
                        st.session_state.partidos = partidos
                        st.success(f"✅ {len(partidos)} partidos obtenidos")
                    else:
                        st.error("❌ No se pudieron obtener partidos")
                except Exception as e:
                    st.error(f"❌ Error al obtener partidos: {str(e)}")
        
        st.divider()
        
        # Selector de cantidad de quinielas
        num_quinielas = st.selectbox(
            "Número de quinielas a generar:",
            [1, 5, 10],
            index=0
        )
        
        # Modo de generación
        modo_generacion = st.selectbox(
            "Modo de generación:",
            ["🎲 Aleatorio", "📊 Inteligente (favoritos locales)"],
            index=0
        )
        
        # Botón para generar quinielas
        if st.button("🎲 Generar Quinielas", use_container_width=True, type="primary"):
            if not st.session_state.partidos:
                st.error("❌ Primero actualiza los partidos")
            else:
                with st.spinner("Generando quinielas..."):
                    if "Aleatorio" in modo_generacion:
                        quinielas = st.session_state.generator.generar_quinielas(
                            st.session_state.partidos, num_quinielas
                        )
                    else:
                        # Modo inteligente con tendencia local
                        quinielas = []
                        for _ in range(num_quinielas):
                            q = st.session_state.generator.generar_quiniela_con_tendencia(
                                st.session_state.partidos, 'local'
                            )
                            quinielas.append(q)
                    
                    st.session_state.quinielas = quinielas
                    
                    # Guardar en base de datos
                    guardadas = 0
                    for quiniela in quinielas:
                        if st.session_state.db.guardar_quiniela(quiniela):
                            guardadas += 1
                    
                    if guardadas == num_quinielas:
                        st.success(f"✅ {num_quinielas} quiniela(s) generada(s) y guardada(s)")
                    elif guardadas > 0:
                        st.warning(f"⚠️ {num_quinielas} quiniela(s) generada(s), pero solo {guardadas} guardada(s)")
                    else:
                        st.error(f"✅ {num_quinielas} quiniela(s) generada(s), pero no se pudieron guardar en la base de datos")
    else:
        # Controles para historial
        st.markdown("### Estadísticas")
        stats = st.session_state.db.obtener_estadisticas()
        st.metric("Total de Quinielas", stats['total_quinielas'])
        
        if st.button("🔄 Actualizar Historial", use_container_width=True):
            st.rerun()

# Contenido principal
if st.session_state.vista_actual == "generar":
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("⚽ Partidos Actuales")
        
        if st.session_state.partidos:
            # Mostrar partidos en formato compacto
            for i, partido in enumerate(st.session_state.partidos, 1):
                with st.container():
                    st.markdown(f"""
                    **Partido {i}:**  
                    🏠 {partido['local']}  
                    🆚 {partido['visitante']}  
                    📅 {partido.get('fecha', 'Sin fecha')}
                    """)
                    if i < len(st.session_state.partidos):
                        st.divider()
        else:
            st.info("📋 Haz clic en 'Actualizar Partidos' para cargar los partidos actuales de Progol")

    with col2:
        st.subheader("🎯 Quinielas Generadas")
        
        if st.session_state.quinielas:
            # Mostrar cada quiniela
            for i, quiniela in enumerate(st.session_state.quinielas, 1):
                with st.expander(f"🎲 Quiniela #{i}", expanded=(len(st.session_state.quinielas) == 1)):
                    
                    # Crear DataFrame para mostrar la quiniela
                    df_quiniela = pd.DataFrame(quiniela)
                    
                    # Renombrar columnas para mejor visualización
                    df_display = df_quiniela.rename(columns={
                        'partido': 'Partido',
                        'local': 'Local',
                        'visitante': 'Visitante', 
                        'prediccion': 'Predicción',
                        'simbolo': 'Resultado'
                    })
                    
                    # Mostrar tabla
                    st.dataframe(
                        df_display,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Resumen de predicciones
                    predicciones = df_quiniela['prediccion'].value_counts()
                    st.markdown("**Resumen de predicciones:**")
                    col_local, col_empate, col_visitante = st.columns(3)
                    
                    with col_local:
                        st.metric("🏠 Local", predicciones.get('Local', 0))
                    with col_empate:
                        st.metric("🤝 Empate", predicciones.get('Empate', 0))
                    with col_visitante:
                        st.metric("✈️ Visitante", predicciones.get('Visitante', 0))
                    
                    # Botón para descargar como imagen
                    col_img, col_space = st.columns([1, 2])
                    with col_img:
                        img_bytes = st.session_state.exporter.generar_imagen(quiniela, i)
                        st.download_button(
                            label="📥 Descargar como imagen",
                            data=img_bytes,
                            file_name=f"quiniela_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    st.divider()
        else:
            st.info("🎲 Genera tu primera quiniela usando el botón en la barra lateral")

else:
    # Vista de historial
    st.subheader("📚 Historial de Quinielas")
    
    quinielas_guardadas = st.session_state.db.obtener_quinielas(limite=50)
    
    if quinielas_guardadas:
        for q in quinielas_guardadas:
            fecha_str = q['fecha_generacion'].strftime("%d/%m/%Y %H:%M:%S")
            
            with st.expander(f"Quiniela #{q['id']} - {fecha_str}"):
                quiniela_data = q['datos']
                
                # Mostrar tabla
                df = pd.DataFrame(quiniela_data)
                df_display = df.rename(columns={
                    'partido': 'Partido',
                    'local': 'Local',
                    'visitante': 'Visitante', 
                    'prediccion': 'Predicción',
                    'simbolo': 'Resultado'
                })
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Botones de acción
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    img_bytes = st.session_state.exporter.generar_imagen(quiniela_data, q['id'])
                    st.download_button(
                        label="📥 Descargar",
                        data=img_bytes,
                        file_name=f"quiniela_{q['id']}.png",
                        mime="image/png",
                        key=f"download_{q['id']}",
                        use_container_width=True
                    )
                
                with col2:
                    if st.button("🗑️ Eliminar", key=f"delete_{q['id']}", use_container_width=True):
                        if st.session_state.db.eliminar_quiniela(q['id']):
                            st.success("✅ Quiniela eliminada")
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar")
    else:
        st.info("📭 No hay quinielas guardadas todavía. ¡Genera tu primera quiniela!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    🎯 Generador de Quinielas Progol - Las predicciones son completamente aleatorias
    </div>
    """, 
    unsafe_allow_html=True
)

# Información adicional
with st.expander("ℹ️ Información sobre Progol"):
    st.markdown("""
    **¿Qué es Progol?**
    
    Progol es un juego de pronósticos deportivos de la Lotería Nacional de México donde debes predecir el resultado de 14 partidos de fútbol.
    
    **Opciones de predicción:**
    - 🏠 **Local (1)**: Gana el equipo local
    - 🤝 **Empate (X)**: Los equipos empatan  
    - ✈️ **Visitante (2)**: Gana el equipo visitante
    
    **Modos de generación:**
    - 🎲 **Aleatorio**: Predicciones completamente al azar
    - 📊 **Inteligente**: Favorece victorias locales (estadísticamente más comunes)
    
    **Nota importante:** Este generador crea predicciones con fines de entretenimiento. No garantiza ningún resultado.
    """)
