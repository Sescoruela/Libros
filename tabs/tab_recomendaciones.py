import streamlit as st
import re
import google.generativeai as genai
from gtts import gTTS
import os
import tempfile
from utils import display_book_card, get_recommendations, save_books


def render(books, user_data):
    """Renderiza la pestaña de Recomendaciones."""
    st.header("⭐ Recomendaciones personalizadas")

    # Sección de recomendación por IA
    if user_data.get("read_books"):
        st.subheader("🤖 Recomendación Inteligente Doble")
        st.write("La IA analizará tus gustos y te recomendará dos libros: uno de tu biblioteca y otro nuevo para descubrir.")

        if st.button("✨ Obtener Recomendaciones IA", type="primary", use_container_width=True):
            with st.spinner("🔍 Analizando tu perfil de lectura..."):
                # Obtener libros leídos y sus calificaciones
                read_books_list = [b for b in books if b["id"] in user_data.get("read_books", [])]
                ratings = user_data.get("ratings", {})

                # Crear contexto para la IA
                books_context = []
                for book in read_books_list:
                    rating = ratings.get(str(book["id"]), 0)
                    books_context.append(f"- '{book['title']}' de {book['author']} ({book['genre']}, {book['year']}) - Calificación: {rating}/5 estrellas")

                # Obtener lista de libros disponibles en la biblioteca (no leídos)
                available_books = []
                for book in books:
                    if book["id"] not in user_data.get("read_books", []):
                        available_books.append(f"- ID {book['id']}: '{book['title']}' de {book['author']} ({book['genre']}, {book['year']}) - {book['description'][:100]}...")

                # Crear prompt para la IA
                prompt = f"""Analiza el perfil de lectura del usuario y recomienda EXACTAMENTE DOS libros:

Libros que ha leído y calificado:
{chr(10).join(books_context)}

Libros disponibles en la biblioteca (NO leídos):
{chr(10).join(available_books[:30])}  

IMPORTANTE: 
1. Recomienda EXACTAMENTE DOS libros:
   - RECOMENDACIÓN 1: Un libro de la lista de disponibles en la biblioteca
   - RECOMENDACIÓN 2: Un libro que NO esté en la biblioteca (sugiere un título que creas que le gustará)

2. Formato ESTRICTO requerido:
   BIBLIOTECA: ID [número]: [Título del libro] - [Explicación breve]
   NUEVO: [Título completo] por [Autor] - [Explicación breve]

3. Analiza qué géneros, autores o temas le gustaron más (calificaciones altas) y cuáles menos (calificaciones bajas)
4. Las explicaciones deben ser personales y específicas, mencionando libros que leyó
5. Para el libro nuevo, recomienda algo real que exista y esté relacionado con sus gustos

Ejemplo de formato:
BIBLIOTECA: ID 25: Cien años de soledad - Basándose en tu alta calificación a Don Quijote, este clásico latinoamericano te encantará.
NUEVO: El amor en los tiempos del cólera por Gabriel García Márquez - Continuarás disfrutando del realismo mágico que tanto te gustó."""

                try:
                    model = genai.GenerativeModel("gemini-2.0-flash")
                    response = model.generate_content(prompt)
                    ai_response = response.text.strip()

                    biblioteca_match = re.search(r"BIBLIOTECA:\s*ID\s*(\d+):\s*([^-]+)-\s*(.*?)(?=NUEVO:|$)", ai_response, re.IGNORECASE | re.DOTALL)
                    nuevo_match = re.search(r"NUEVO:\s*([^-]+?)\s*(?:por|de)\s*([^-]+)-\s*(.*)", ai_response, re.IGNORECASE | re.DOTALL)

                    # Guardar resultados en session_state para que persistan
                    st.session_state.ai_recommendation = {
                        "ai_response": ai_response,
                        "biblioteca_id": int(biblioteca_match.group(1)) if biblioteca_match else None,
                        "biblioteca_explanation": biblioteca_match.group(3).strip() if biblioteca_match else None,
                        "new_title": nuevo_match.group(1).strip() if nuevo_match else None,
                        "new_author": nuevo_match.group(2).strip() if nuevo_match else None,
                        "new_explanation": nuevo_match.group(3).strip() if nuevo_match else None,
                    }
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al generar recomendación: {str(e)}")

        # Mostrar recomendaciones guardadas en session_state
        if "ai_recommendation" in st.session_state:
            rec = st.session_state.ai_recommendation

            st.success("✨ ¡Recomendaciones generadas!")
            col_rec1, col_rec2 = st.columns(2)

            # Recomendación de la biblioteca
            with col_rec1:
                st.markdown("### 📚 De tu Biblioteca")
                if rec["biblioteca_id"]:
                    recommended_book = next((b for b in books if b["id"] == rec["biblioteca_id"]), None)
                    if recommended_book:
                        st.markdown(f"**{recommended_book['title']}**")
                        st.markdown(f"*{rec['biblioteca_explanation']}*")
                        st.divider()
                        display_book_card(recommended_book, user_data, col_rec1, key_prefix="ai_bib_")
                    else:
                        st.warning("No pude encontrar ese libro en la biblioteca.")
                else:
                    st.info("No se pudo extraer la recomendación de biblioteca.")

            # Recomendación nueva
            with col_rec2:
                st.markdown("### 🌟 Libro Nuevo para Ti")
                if rec["new_title"]:
                    st.markdown(f"**{rec['new_title']}**")
                    st.markdown(f"*por {rec['new_author']}*")
                    st.markdown(f"\n{rec['new_explanation']}")
                    st.info("💡 Este libro no está en tu biblioteca.")

                    # Botón para agregar el libro
                    if st.button("➕ Agregar a mi biblioteca", key="add_ai_book_btn", type="primary", use_container_width=True):
                        new_id = max([b["id"] for b in books]) + 1
                        new_book = {
                            "id": new_id,
                            "title": rec["new_title"],
                            "author": rec["new_author"],
                            "genre": "Ficción",
                            "year": 2020,
                            "description": rec["new_explanation"],
                            "pages": 300,
                            "cover": "https://via.placeholder.com/150x200?text=Sin+Portada"
                        }
                        books.append(new_book)
                        save_books(books)
                        del st.session_state.ai_recommendation
                        st.success(f"✅ ¡'{rec['new_title']}' ha sido agregado a tu biblioteca!")
                        st.balloons()
                        st.rerun()
                else:
                    st.info("No se pudo extraer la recomendación de libro nuevo.")

            with st.expander("📝 Ver análisis completo de la IA"):
                st.write(rec["ai_response"])

        st.divider()

    # ── Sección de Búsqueda de Libros ──
    st.subheader("🔍 Buscar y Agregar Libros Nuevos")
    st.write("Usa la IA para buscar información sobre cualquier libro que quieras añadir a tu biblioteca.")
    
    # Verificar si hay API Key configurada
    api_key_value = st.session_state.get('gemini_api_key', '')
    
    if not api_key_value or api_key_value == "":
        st.warning("⚠️ Necesitas configurar tu API Key de Gemini en la pestaña '💬 Libros Chat' para usar la búsqueda.")
        st.info(f"🔍 Debug: Estado actual de API Key = '{api_key_value}' (vacía: {api_key_value == ''})")
    else:
        st.success(f"✅ API Key configurada (primeros 10 caracteres: {api_key_value[:10]}...)")
        col_search, col_button = st.columns([4, 1])
        
        with col_search:
            search_query = st.text_input(
                "Buscar libro:",
                placeholder="Ej: El código Da Vinci, Sapiens, Harry Potter...",
                key="search_book_input"
            )
        
        with col_button:
            st.write("")  # Espaciado
            search_button = st.button("🔎 Buscar", type="primary", use_container_width=True)
    
        if search_button and search_query:
            with st.spinner("🔍 Buscando información del libro..."):
                try:
                    # Configurar la API key
                    genai.configure(api_key=st.session_state.gemini_api_key)
                    
                    # Crear prompt para buscar información del libro
                    search_prompt = f"""Busca información sobre el libro "{search_query}" y devuelve la información en el siguiente formato ESTRICTO:

TÍTULO: [Título completo del libro]
AUTOR: [Nombre del autor]
GÉNERO: [Género principal del libro]
AÑO: [Año de publicación]
PÁGINAS: [Número aproximado de páginas]
DESCRIPCIÓN: [Descripción breve del libro en 2-3 oraciones]
PORTADA: [URL de portada de Goodreads si la encuentras, o "No disponible"]

IMPORTANTE: 
- Si no encuentras el libro exacto, devuelve la información del libro más similar
- Asegúrate de que sea un libro real y conocido
- La descripción debe ser informativa pero concisa"""

                    model = genai.GenerativeModel("gemini-2.0-flash")
                    response = model.generate_content(search_prompt)
                    ai_response = response.text.strip()
                    
                    # Extraer información usando regex
                    titulo_match = re.search(r"TÍTULO:\s*(.+)", ai_response, re.IGNORECASE)
                    autor_match = re.search(r"AUTOR:\s*(.+)", ai_response, re.IGNORECASE)
                    genero_match = re.search(r"GÉNERO:\s*(.+)", ai_response, re.IGNORECASE)
                    año_match = re.search(r"AÑO:\s*(\d+)", ai_response, re.IGNORECASE)
                    paginas_match = re.search(r"PÁGINAS:\s*(\d+)", ai_response, re.IGNORECASE)
                    descripcion_match = re.search(r"DESCRIPCIÓN:\s*(.+?)(?=PORTADA:|$)", ai_response, re.IGNORECASE | re.DOTALL)
                    portada_match = re.search(r"PORTADA:\s*(.+)", ai_response, re.IGNORECASE)
                    
                    if titulo_match and autor_match:
                        st.success("✅ ¡Libro encontrado!")
                        
                        # Guardar en session_state
                        st.session_state.found_book = {
                            "titulo": titulo_match.group(1).strip(),
                            "autor": autor_match.group(1).strip(),
                            "genero": genero_match.group(1).strip() if genero_match else "Ficción",
                            "año": int(año_match.group(1)) if año_match else 2020,
                            "paginas": int(paginas_match.group(1)) if paginas_match else 300,
                            "descripcion": descripcion_match.group(1).strip() if descripcion_match else "Sin descripción disponible.",
                            "portada": portada_match.group(1).strip() if portada_match and "No disponible" not in portada_match.group(1) else "https://via.placeholder.com/150x200?text=Sin+Portada"
                        }
                        st.rerun()
                    else:
                        st.warning("No se pudo encontrar información estructurada. Intenta con otro nombre.")
                        with st.expander("Ver respuesta completa"):
                            st.write(ai_response)
                            
                except Exception as e:
                    st.error(f"❌ Error al buscar: {str(e)}")
    
    # Mostrar libro encontrado
    if "found_book" in st.session_state:
        found = st.session_state.found_book
        
        st.divider()
        st.markdown("### 📖 Libro Encontrado")
        
        col_preview, col_info = st.columns([1, 3])
        
        with col_preview:
            if found["portada"]:
                st.image(found["portada"], width=150)
        
        with col_info:
            st.markdown(f"**Título:** {found['titulo']}")
            st.markdown(f"**Autor:** {found['autor']}")
            st.markdown(f"**Género:** {found['genero']}")
            st.markdown(f"**Año:** {found['año']} | **Páginas:** {found['paginas']}")
            st.markdown(f"**Descripción:** {found['descripcion']}")
            
            # Botón para generar audio resumen
            st.divider()
            
            # Verificar si ya existe el resumen
            if "audio_summary" not in st.session_state:
                if st.button("🎧 Generar Audio Resumen", use_container_width=True, key="generate_audio_summary"):
                    if not st.session_state.get('gemini_api_key'):
                        st.error("❌ Necesitas configurar tu API Key de Gemini primero")
                    else:
                        with st.spinner("🤖 Generando resumen inteligente del libro..."):
                            try:
                                # Configurar Gemini
                                genai.configure(api_key=st.session_state.gemini_api_key)
                                model = genai.GenerativeModel("gemini-2.0-flash")
                                
                                # Generar resumen con IA
                                summary_prompt = f"""Genera un resumen profesional y atractivo del libro "{found['titulo']}" de {found['autor']}.

El resumen debe:
- Tener entre 100-150 palabras
- Ser objetivo y profesional
- Incluir los puntos clave del libro
- Mencionar qué tipo de lector disfrutaría este libro
- Usar un tono narrativo apropiado para audio

Libro: "{found['titulo']}"
Autor: {found['autor']}
Género: {found['genero']}
Descripción base: {found['descripcion']}

IMPORTANTE: Responde SOLO con el resumen, sin títulos ni encabezados."""

                                # Generar contenido con timeout implícito
                                response = model.generate_content(
                                    summary_prompt,
                                    generation_config={
                                        'temperature': 0.7,
                                        'max_output_tokens': 300,
                                    }
                                )
                                
                                if response and response.text:
                                    resumen = response.text.strip()
                                    
                                    # Guardar resumen en session_state
                                    st.session_state.audio_summary = resumen
                                    st.success("✅ Resumen generado!")
                                    
                                    # Generar audio inmediatamente después del resumen
                                    try:
                                        with st.spinner("🔊 Convirtiendo a audio..."):
                                            temp_dir = tempfile.gettempdir()
                                            audio_file = os.path.join(temp_dir, f"book_summary_{hash(found['titulo'])}.mp3")
                                            
                                            tts = gTTS(text=resumen, lang='es', slow=False)
                                            tts.save(audio_file)
                                            
                                            st.session_state.audio_file_path = audio_file
                                            st.session_state.audio_generated = True
                                            st.rerun()
                                    except Exception as audio_error:
                                        st.warning(f"⚠️ Resumen generado pero error en audio: {str(audio_error)}")
                                        st.rerun()
                                else:
                                    st.error("❌ No se pudo generar el resumen. Intenta de nuevo.")
                                
                            except Exception as e:
                                st.error(f"❌ Error al generar resumen: {str(e)}")
                                st.info("💡 Verifica que tu API Key sea válida y tenga permisos")
            
            # Mostrar resumen y audio si existe
            if "audio_summary" in st.session_state and st.session_state.get("audio_summary"):
                st.divider()
                st.markdown("#### 📝 Resumen Generado")
                st.write(st.session_state.audio_summary)
                
                # Mostrar el audio si ya fue generado
                if st.session_state.get("audio_generated") and st.session_state.get("audio_file_path"):
                    audio_file = st.session_state.audio_file_path
                    
                    if os.path.exists(audio_file):
                        # Mostrar reproductor de audio
                        st.audio(audio_file, format='audio/mp3')
                        st.success("✅ Audio generado exitosamente!")
                        
                        # Botón para descargar
                        with open(audio_file, 'rb') as f:
                            audio_bytes = f.read()
                            st.download_button(
                                label="⬇️ Descargar Audio",
                                data=audio_bytes,
                                file_name=f"{found['titulo']}_resumen.mp3",
                                mime="audio/mp3",
                                use_container_width=True
                            )
                    else:
                        st.warning("⚠️ El archivo de audio no está disponible")
                else:
                    # Si no hay audio generado aún, intentar generarlo ahora
                    st.info("🔊 Generando audio del resumen...")
                    try:
                        temp_dir = tempfile.gettempdir()
                        audio_file = os.path.join(temp_dir, f"book_summary_{hash(found['titulo'])}.mp3")
                        
                        tts = gTTS(text=st.session_state.audio_summary, lang='es', slow=False)
                        tts.save(audio_file)
                        
                        st.session_state.audio_file_path = audio_file
                        st.session_state.audio_generated = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al generar audio: {str(e)}")
                        if st.button("🔄 Reintentar Generar Audio", use_container_width=True):
                            st.rerun()
            
            st.divider()
            col_add, col_cancel = st.columns([3, 1])
            
            with col_add:
                if st.button("✅ Agregar a Mi Biblioteca", type="primary", use_container_width=True, key="add_found_book"):
                    new_id = max([b["id"] for b in books]) + 1
                    new_book = {
                        "id": new_id,
                        "title": found["titulo"],
                        "author": found["autor"],
                        "genre": found["genero"],
                        "year": found["año"],
                        "description": found["descripcion"],
                        "pages": found["paginas"],
                        "cover": found["portada"]
                    }
                    books.append(new_book)
                    save_books(books)
                    # Limpiar estados
                    if "audio_summary" in st.session_state:
                        del st.session_state.audio_summary
                    if "audio_generated" in st.session_state:
                        del st.session_state.audio_generated
                    if "audio_file_path" in st.session_state:
                        del st.session_state.audio_file_path
                    del st.session_state.found_book
                    st.success(f"✅ ¡'{found['titulo']}' ha sido agregado a tu biblioteca!")
                    st.balloons()
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ Cancelar", use_container_width=True, key="cancel_found_book"):
                    # Limpiar todos los estados relacionados
                    if "audio_summary" in st.session_state:
                        del st.session_state.audio_summary
                    if "audio_generated" in st.session_state:
                        del st.session_state.audio_generated
                    if "audio_file_path" in st.session_state:
                        del st.session_state.audio_file_path
                    del st.session_state.found_book
                    st.rerun()
    
    st.divider()

    st.subheader("📚 Recomendaciones Basadas en tu Perfil")
    recommendations = get_recommendations(books, user_data, limit=50)

    if user_data.get("read_books"):
        st.write("Basadas en tus lecturas y calificaciones:")
    else:
        st.info("👋 ¡Bienvenido! Marca algunos libros como leídos y califícalos para recibir recomendaciones personalizadas.")
        st.write("Mientras tanto, aquí tienes algunos libros populares:")

    # Paginación para recomendaciones
    rec_per_page = 9
    total_recs = len(recommendations)
    total_rec_pages = (total_recs + rec_per_page - 1) // rec_per_page

    # Inicializar página de recomendaciones en session state
    if 'rec_current_page' not in st.session_state:
        st.session_state.rec_current_page = 1

    # Asegurar que la página actual esté en rango válido
    if st.session_state.rec_current_page > total_rec_pages and total_rec_pages > 0:
        st.session_state.rec_current_page = total_rec_pages
    elif st.session_state.rec_current_page < 1:
        st.session_state.rec_current_page = 1

    st.write(f"Mostrando {total_recs} recomendación(es) - Página {st.session_state.rec_current_page} de {max(total_rec_pages, 1)}")

    # Calcular índices para la página actual
    rec_start_idx = (st.session_state.rec_current_page - 1) * rec_per_page
    rec_end_idx = min(rec_start_idx + rec_per_page, total_recs)
    current_page_recs = recommendations[rec_start_idx:rec_end_idx]

    # Mostrar recomendaciones en grid de 3 columnas
    for i in range(0, len(current_page_recs), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(current_page_recs):
                display_book_card(current_page_recs[i + j], user_data, col, key_prefix="rec_")

    # Controles de paginación para recomendaciones
    if total_rec_pages > 1:
        st.divider()
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

        with col1:
            if st.button("⏮️ Primera", disabled=(st.session_state.rec_current_page == 1), key="rec_first_page"):
                st.session_state.rec_current_page = 1
                st.rerun()

        with col2:
            if st.button("◀️ Anterior", disabled=(st.session_state.rec_current_page == 1), key="rec_prev_page"):
                st.session_state.rec_current_page -= 1
                st.rerun()

        with col3:
            st.markdown(f"<div style='text-align: center; padding: 8px;'>Página {st.session_state.rec_current_page} de {total_rec_pages}</div>", unsafe_allow_html=True)

        with col4:
            if st.button("Siguiente ▶️", disabled=(st.session_state.rec_current_page == total_rec_pages), key="rec_next_page"):
                st.session_state.rec_current_page += 1
                st.rerun()

        with col5:
            if st.button("Última ⏭️", disabled=(st.session_state.rec_current_page == total_rec_pages), key="rec_last_page"):
                st.session_state.rec_current_page = total_rec_pages
                st.rerun()
