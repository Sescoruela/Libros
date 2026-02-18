import streamlit as st
import google.generativeai as genai
from utils import save_api_key


def render(books):
    """Renderiza la pestaña de Libros Chat."""
    st.header("💬 Libros AI Assistant")
    st.write("Tu asistente de IA personal para recomendaciones de libros y consultas literarias.")

    # Configuración de API Key
    st.subheader("🔑 Configuración")
    
    # Usar un callback para actualizar la API Key
    def on_api_key_change():
        new_key = st.session_state.api_key_input
        st.session_state.gemini_api_key = new_key
        save_api_key(new_key)
    
    st.text_input(
        "Gemini API Key:",
        type="password",
        value=st.session_state.get('gemini_api_key', ''),
        key="api_key_input",
        on_change=on_api_key_change,
        help="Necesaria para usar Libros AI",
        placeholder="Pega tu API Key aquí..."
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("🔑 Obtén tu clave gratis en [Google AI Studio](https://aistudio.google.com/)")
    with col2:
        if st.session_state.gemini_api_key:
            st.success("✅ Conectado")
        else:
            st.warning("⚠️ Sin clave")
    
    st.divider()

    # Inicializar el cliente Gemini
    if st.session_state.gemini_api_key:
        try:
            # Configurar la API key
            genai.configure(api_key=st.session_state.gemini_api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')

            # Input del usuario
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;">
                <p style="color: white; margin: 0; font-size: 1.1em;">
                    💬 Pregúntame sobre libros, pide recomendaciones o consulta sobre cualquier tema literario
                </p>
            </div>
            """, unsafe_allow_html=True)

            user_query = st.text_area(
                "¿Cómo puede ayudarte Libri hoy?",
                placeholder="Ejemplo: Recomiéndame libros de ciencia ficción similares a Dune...",
                height=100
            )

            col1, col2 = st.columns([1, 5])
            with col1:
                ask_button = st.button(" Preguntar", type="primary", use_container_width=True)

            if ask_button:
                if user_query:
                    with st.spinner(" Conchita está pensando..."):
                        try:
                            # Crear contexto con los libros de la biblioteca
                            books_context = f"\n\nContexto: Tengo acceso a una biblioteca con {len(books)} libros. "
                            books_context += "Algunos géneros disponibles: " + ", ".join(set([b['genre'] for b in books[:10]]))

                            # Llamar a Gemini
                            response = model.generate_content(user_query + books_context)

                            # Mostrar resultados con estilo
                            st.markdown("""
                            <div style="
                                background-color: #f8f9fa;
                                border-left: 4px solid #667eea;
                                padding: 20px;
                                border-radius: 8px;
                                margin-top: 20px;">
                                <h4 style="color: #1a1a2e; margin-top: 0;">💡 Respuesta de Libri:</h4>
                            """, unsafe_allow_html=True)

                            st.write(response.text)

                            st.markdown("</div>", unsafe_allow_html=True)

                        except Exception as e:
                            st.error(f"❌ Ocurrió un error: {e}")
                            st.info("💡 Verifica que tu API Key sea válida y que tengas conexión a internet.")
                else:
                    st.warning("⚠️ Por favor, escribe una pregunta primero.")

            # Sugerencias de preguntas
            st.markdown("---")
            st.subheader("💡 Sugerencias de preguntas:")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📚 Recomiéndame un libro clásico"):
                    st.session_state['suggested_query'] = "Recomiéndame un libro clásico imprescindible y explícame por qué debería leerlo"
                if st.button("🔮 Libros de fantasía épica"):
                    st.session_state['suggested_query'] = "¿Qué libros de fantasía épica me recomiendas si me gustó El Señor de los Anillos?"
                if st.button("🚀 Ciencia ficción moderna"):
                    st.session_state['suggested_query'] = "Dame recomendaciones de ciencia ficción moderna y actual"

            with col2:
                if st.button("❤️ Romance contemporáneo"):
                    st.session_state['suggested_query'] = "Recomiéndame novelas de romance contemporáneo bien escritas"
                if st.button("🔍 Misterio y suspense"):
                    st.session_state['suggested_query'] = "¿Cuáles son los mejores libros de misterio y suspense?"
                if st.button("📖 Autores latinoamericanos"):
                    st.session_state['suggested_query'] = "Háblame sobre autores latinoamericanos importantes y sus obras"

        except Exception as e:
            st.error(f"❌ Error al inicializar Libros AI: {e}")
            st.info("Verifica que tu API Key sea correcta.")
    else:
        st.warning("⚠️ Por favor, ingresa tu API Key de Gemini en la barra lateral para usar Libros AI.")
        st.markdown("""
        ### ¿Cómo obtener tu API Key?
        
        1. Visita [Google AI Studio](https://aistudio.google.com/)
        2. Inicia sesión con tu cuenta de Google
        3. Crea o selecciona un proyecto
        4. Genera una nueva API Key
        5. Copia y pega la clave en la barra lateral
        
        **Libros AI** puede ayudarte con:
        - 📚 Recomendaciones personalizadas de libros
        - 📖 Resúmenes y análisis literarios
        - ✍️ Información sobre autores y géneros
        - 💭 Discusiones sobre temas literarios
        - 🎯 Sugerencias basadas en tus gustos
        """)
