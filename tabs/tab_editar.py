import streamlit as st
from utils import save_books


def render(books, user_data):
    """Renderiza la pestaña de Editar Libros."""
    st.header("✏️ Editar Libros")
    st.write("Selecciona un libro de tu biblioteca para editar su información.")

    if not books:
        st.info("No hay libros en la biblioteca.")
        return

    # Selector de libro
    book_options = {f"{book['id']} - {book['title']} ({book['author']})": book for book in books}
    selected_option = st.selectbox(
        "📖 Selecciona un libro para editar:",
        options=[""] + list(book_options.keys()),
        format_func=lambda x: "-- Selecciona un libro --" if x == "" else x
    )

    if selected_option and selected_option != "":
        selected_book = book_options[selected_option]
        
        st.divider()
        st.subheader(f"Editando: {selected_book['title']}")
        
        # Mostrar información original en un expander
        with st.expander("📋 Ver información actual del libro", expanded=False):
            st.write(f"**Título:** {selected_book['title']}")
            st.write(f"**Autor:** {selected_book['author']}")
            st.write(f"**Género:** {selected_book['genre']}")
            st.write(f"**Año:** {selected_book['year']}")
            st.write(f"**Páginas:** {selected_book['pages']}")
            st.write(f"**Descripción:** {selected_book['description']}")
            if selected_book.get('cover'):
                st.write(f"**URL Portada:** {selected_book['cover']}")
        
        # Mostrar portada actual si existe
        col_preview, col_form = st.columns([1, 3])
        
        with col_preview:
            st.write("**Portada actual:**")
            if selected_book.get('cover'):
                st.image(selected_book['cover'], width=200)
            else:
                st.info("Sin portada")
        
        with col_form:
            # Formulario de edición con campos vacíos
            with st.form(f"edit_book_form_{selected_book['id']}"):
                st.write("**Nueva información (deja en blanco para mantener):**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_title = st.text_input(
                        "📖 Título", 
                        value="",
                        placeholder=selected_book['title'],
                        key=f"edit_title_{selected_book['id']}"
                    )
                    edit_author = st.text_input(
                        "✍️ Autor", 
                        value="",
                        placeholder=selected_book['author'],
                        key=f"edit_author_{selected_book['id']}"
                    )
                    edit_year = st.number_input(
                        "📅 Año de publicación (0 = mantener)", 
                        min_value=0, 
                        max_value=2026, 
                        value=0,
                        key=f"edit_year_{selected_book['id']}"
                    )
                
                with col2:
                    # Obtener géneros existentes con opción "Mantener actual"
                    existing_genres = ["-- Mantener actual --"] + sorted(list(set([book["genre"] for book in books])))
                    
                    edit_genre = st.selectbox(
                        "🏷️ Género", 
                        existing_genres,
                        index=0,
                        key=f"edit_genre_{selected_book['id']}",
                        help=f"Actual: {selected_book['genre']}"
                    )
                    
                    edit_pages = st.number_input(
                        "📄 Páginas (0 = mantener)", 
                        min_value=0, 
                        max_value=10000, 
                        value=0,
                        key=f"edit_pages_{selected_book['id']}"
                    )
                    
                    edit_cover = st.text_input(
                        "🖼️ URL de portada", 
                        value="",
                        placeholder=selected_book.get('cover', 'Sin portada actual'),
                        key=f"edit_cover_{selected_book['id']}"
                    )
                
                edit_description = st.text_area(
                    "📝 Descripción",
                    value="",
                    placeholder=selected_book['description'][:100] + "...",
                    height=120,
                    max_chars=500,
                    key=f"edit_description_{selected_book['id']}"
                )
                
                st.markdown("---")
                
                col_save, col_delete = st.columns([3, 1])
                
                with col_save:
                    submitted = st.form_submit_button(
                        "💾 Guardar Cambios", 
                        use_container_width=True, 
                        type="primary"
                    )
                
                with col_delete:
                    delete_confirm = st.form_submit_button(
                        "🗑️ Eliminar", 
                        use_container_width=True,
                        type="secondary"
                    )
                
                if submitted:
                    # Actualizar el libro solo con los campos que fueron modificados
                    for book in books:
                        if book['id'] == selected_book['id']:
                            # Solo actualizar si el campo no está vacío
                            if edit_title.strip():
                                book['title'] = edit_title.strip()
                            if edit_author.strip():
                                book['author'] = edit_author.strip()
                            if edit_genre != "-- Mantener actual --":
                                book['genre'] = edit_genre.strip()
                            if edit_year > 0:
                                book['year'] = edit_year
                            if edit_pages > 0:
                                book['pages'] = edit_pages
                            if edit_description.strip():
                                book['description'] = edit_description.strip()
                            if edit_cover.strip():
                                book['cover'] = edit_cover.strip()
                            break
                    
                    # Guardar cambios
                    save_books(books)
                    st.success(f"✅ ¡Libro actualizado exitosamente!")
                    st.balloons()
                    st.rerun()
                
                if delete_confirm:
                    # Crear confirmación de eliminación en session_state
                    st.session_state.book_to_delete = selected_book['id']
                    st.rerun()
        
        # Confirmación de eliminación fuera del formulario
        if 'book_to_delete' in st.session_state and st.session_state.book_to_delete == selected_book['id']:
            st.warning(f"⚠️ ¿Estás seguro de que deseas eliminar '{selected_book['title']}'?")
            
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
                if st.button("✅ Sí, eliminar", type="primary", use_container_width=True):
                    # Eliminar el libro
                    books[:] = [b for b in books if b['id'] != selected_book['id']]
                    
                    # Eliminar de datos de usuario si estaba leído
                    if selected_book['id'] in user_data.get('read_books', []):
                        user_data['read_books'].remove(selected_book['id'])
                    if str(selected_book['id']) in user_data.get('ratings', {}):
                        del user_data['ratings'][str(selected_book['id'])]
                    
                    from utils import save_user_data
                    save_user_data(user_data)
                    
                    # Guardar cambios
                    save_books(books)
                    
                    # Limpiar session_state
                    del st.session_state.book_to_delete
                    
                    st.success(f"✅ ¡Libro '{selected_book['title']}' eliminado exitosamente!")
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ Cancelar", use_container_width=True):
                    del st.session_state.book_to_delete
                    st.rerun()
