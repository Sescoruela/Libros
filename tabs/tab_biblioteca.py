import streamlit as st
from utils import display_book_card


def render(books, user_data, filtered_books):
    """Renderiza la pestaña de Biblioteca."""
    st.header("Biblioteca completa")
    
    # Paginación
    books_per_page = 9
    total_books = len(filtered_books)
    total_pages = (total_books + books_per_page - 1) // books_per_page

    # Inicializar página actual en session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    # Asegurar que la página actual esté en rango válido
    if st.session_state.current_page > total_pages and total_pages > 0:
        st.session_state.current_page = total_pages
    elif st.session_state.current_page < 1:
        st.session_state.current_page = 1

    st.write(f"Mostrando {total_books} libro(s) - Página {st.session_state.current_page} de {max(total_pages, 1)}")

    # Calcular índices para la página actual
    start_idx = (st.session_state.current_page - 1) * books_per_page
    end_idx = min(start_idx + books_per_page, total_books)
    current_page_books = filtered_books[start_idx:end_idx]

    # Mostrar libros en grid de 3 columnas
    for i in range(0, len(current_page_books), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(current_page_books):
                display_book_card(current_page_books[i + j], user_data, col, key_prefix="lib_")

    # Controles de paginación
    if total_pages > 1:
        st.divider()
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

        with col1:
            if st.button("⏮️ Primera", disabled=(st.session_state.current_page == 1), key="first_page"):
                st.session_state.current_page = 1
                st.rerun()

        with col2:
            if st.button("◀️ Anterior", disabled=(st.session_state.current_page == 1), key="prev_page"):
                st.session_state.current_page -= 1
                st.rerun()

        with col3:
            st.markdown(f"<div style='text-align: center; padding: 8px;'>Página {st.session_state.current_page} de {total_pages}</div>", unsafe_allow_html=True)

        with col4:
            if st.button("Siguiente ▶️", disabled=(st.session_state.current_page == total_pages), key="next_page"):
                st.session_state.current_page += 1
                st.rerun()

        with col5:
            if st.button("Última ⏭️", disabled=(st.session_state.current_page == total_pages), key="last_page"):
                st.session_state.current_page = total_pages
                st.rerun()
