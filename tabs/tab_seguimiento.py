import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import save_user_data


def render(books, user_data):
    """Renderiza la pestaña de Seguimiento de Lectura."""
    st.header("📊 Seguimiento de Lectura")
    st.write("Gestiona tu progreso de lectura actual y visualiza tus estadísticas.")
    
    # Inicializar estructuras de datos si no existen
    if 'currently_reading' not in user_data:
        user_data['currently_reading'] = {}  # {book_id: {pages_read: X, start_date: 'YYYY-MM-DD', status: 'reading'}}
    if 'finished_books' not in user_data:
        user_data['finished_books'] = {}  # {book_id: {start_date: 'YYYY-MM-DD', finish_date: 'YYYY-MM-DD'}}
    
    # ── Sección 1: Libros que estás leyendo actualmente ──
    st.subheader("📖 Actualmente Leyendo")
    
    currently_reading = user_data.get('currently_reading', {})
    
    if currently_reading:
        for book_id_str, progress_data in list(currently_reading.items()):
            book_id = int(book_id_str)
            book = next((b for b in books if b["id"] == book_id), None)
            
            if book:
                with st.container():
                    col_info, col_progress, col_actions = st.columns([2, 2, 1])
                    
                    with col_info:
                        st.markdown(f"### 📕 {book['title']}")
                        st.write(f"**Autor:** {book['author']}")
                        st.write(f"**Total de páginas:** {book['pages']}")
                        
                        start_date = progress_data.get('start_date', 'No registrada')
                        st.caption(f"📅 Iniciado: {start_date}")
                    
                    with col_progress:
                        pages_read = progress_data.get('pages_read', 0)
                        total_pages = book['pages']
                        progress_pct = (pages_read / total_pages * 100) if total_pages > 0 else 0
                        
                        st.metric("Páginas leídas", f"{pages_read} / {total_pages}")
                        st.progress(progress_pct / 100)
                        st.caption(f"📊 Progreso: {progress_pct:.1f}%")
                        
                        # Actualizar páginas leídas
                        new_pages = st.number_input(
                            "Actualizar páginas leídas:",
                            min_value=0,
                            max_value=total_pages,
                            value=pages_read,
                            key=f"update_pages_{book_id}"
                        )
                        
                        if new_pages != pages_read:
                            currently_reading[book_id_str]['pages_read'] = new_pages
                            save_user_data(user_data)
                            st.rerun()
                    
                    with col_actions:
                        st.write("")  # Espaciado
                        st.write("")
                        
                        if st.button("✅ Marcar como Terminado", key=f"finish_{book_id}", use_container_width=True):
                            # Mover a libros terminados
                            if 'finished_books' not in user_data:
                                user_data['finished_books'] = {}
                            
                            user_data['finished_books'][book_id_str] = {
                                'start_date': progress_data.get('start_date'),
                                'finish_date': datetime.now().strftime('%Y-%m-%d'),
                                'pages': total_pages
                            }
                            
                            # Agregar a libros leídos si no está
                            if book_id not in user_data.get('read_books', []):
                                if 'read_books' not in user_data:
                                    user_data['read_books'] = []
                                user_data['read_books'].append(book_id)
                            
                            # Eliminar de actualmente leyendo
                            del currently_reading[book_id_str]
                            save_user_data(user_data)
                            st.success(f"¡Felicidades! Has terminado '{book['title']}'")
                            st.balloons()
                            st.rerun()
                        
                        if st.button("❌ Abandonar", key=f"abandon_{book_id}", use_container_width=True):
                            del currently_reading[book_id_str]
                            save_user_data(user_data)
                            st.rerun()
                    
                    st.divider()
    else:
        st.info("No estás leyendo ningún libro actualmente. ¡Comienza uno abajo!")
    
    # ── Sección 2: Comenzar a leer un nuevo libro ──
    st.subheader("➕ Comenzar a Leer")
    
    # Filtrar libros no leídos y que no estés leyendo actualmente
    available_books = [
        b for b in books 
        if b["id"] not in user_data.get("read_books", []) 
        and str(b["id"]) not in currently_reading
    ]
    
    if available_books:
        book_options = {f"{book['title']} - {book['author']}": book for book in available_books}
        
        selected_book_name = st.selectbox(
            "Selecciona un libro para comenzar:",
            options=[""] + list(book_options.keys()),
            format_func=lambda x: "-- Selecciona un libro --" if x == "" else x
        )
        
        if selected_book_name and selected_book_name != "":
            selected_book = book_options[selected_book_name]
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{selected_book['title']}** ({selected_book['pages']} páginas)")
                st.caption(selected_book['description'][:150] + "...")
            
            with col2:
                if st.button("📚 Empezar a Leer", type="primary", use_container_width=True):
                    currently_reading[str(selected_book['id'])] = {
                        'pages_read': 0,
                        'start_date': datetime.now().strftime('%Y-%m-%d'),
                        'status': 'reading'
                    }
                    save_user_data(user_data)
                    st.success(f"¡Has comenzado a leer '{selected_book['title']}'!")
                    st.rerun()
    else:
        st.info("No hay libros disponibles para leer. ¡Has leído todo o estás leyendo todos los libros!")
    
    st.divider()
    
    # ── Sección 3: Estadísticas y Historial ──
    st.subheader("📈 Estadísticas de Lectura")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_reading = len(currently_reading)
        st.metric("📚 Leyendo Ahora", total_reading)
    
    with col2:
        finished_books = user_data.get('finished_books', {})
        st.metric("✅ Libros Terminados", len(finished_books))
    
    with col3:
        total_pages_reading = sum(
            progress['pages_read'] 
            for progress in currently_reading.values()
        )
        st.metric("📄 Páginas Leídas (en progreso)", total_pages_reading)
    
    # Historial de libros terminados
    if finished_books:
        st.subheader("🏆 Historial de Libros Terminados")
        
        history_data = []
        for book_id_str, finish_data in finished_books.items():
            book = next((b for b in books if b["id"] == int(book_id_str)), None)
            if book:
                start = finish_data.get('start_date', 'N/A')
                finish = finish_data.get('finish_date', 'N/A')
                
                # Calcular días de lectura
                days = "N/A"
                if start != 'N/A' and finish != 'N/A':
                    try:
                        start_dt = datetime.strptime(start, '%Y-%m-%d')
                        finish_dt = datetime.strptime(finish, '%Y-%m-%d')
                        days = (finish_dt - start_dt).days + 1
                    except:
                        pass
                
                history_data.append({
                    "Título": book['title'],
                    "Autor": book['author'],
                    "Páginas": book['pages'],
                    "Inicio": start,
                    "Fin": finish,
                    "Días": days
                })
        
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Estadísticas adicionales
        if len(history_data) > 0:
            st.subheader("📊 Análisis de Velocidad de Lectura")
            
            valid_days = [h['Días'] for h in history_data if isinstance(h['Días'], int)]
            valid_pages = [h['Páginas'] for h in history_data if isinstance(h['Días'], int)]
            
            if valid_days:
                avg_days = sum(valid_days) / len(valid_days)
                total_pages_finished = sum(valid_pages)
                avg_pages_per_day = total_pages_finished / sum(valid_days) if sum(valid_days) > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("⏱️ Promedio de días por libro", f"{avg_days:.1f}")
                
                with col2:
                    st.metric("📖 Páginas totales terminadas", total_pages_finished)
                
                with col3:
                    st.metric("🚀 Páginas por día (promedio)", f"{avg_pages_per_day:.1f}")
