import streamlit as st

from utils import load_books, load_user_data, load_api_key
from tabs import tab_biblioteca, tab_recomendaciones, tab_mis_libros, tab_agregar, tab_editar, tab_seguimiento, tab_chat

# Configuración de la página
st.set_page_config(
    page_title="Mi Biblioteca de Libros",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    # Cargar datos
    books = load_books()

    # Inicializar session state para user_data
    if 'user_data' not in st.session_state:
        st.session_state.user_data = load_user_data()

    # Inicializar session state para gemini_api_key desde archivo
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = load_api_key()

    user_data = st.session_state.user_data

    # Título principal
    st.title("📚 Mi Biblioteca de Libros")

    # ── Sidebar: Filtros, API Key y Estadísticas ──
    with st.sidebar:
        st.header("Filtros")

        # Búsqueda por título
        search_term = st.text_input("🔍 Buscar por título", "")

        # Filtro por género
        all_genres = sorted(list(set([book["genre"] for book in books])))
        selected_genres = st.multiselect("Género", all_genres, default=all_genres)

        # Filtro por autor
        all_authors = sorted(list(set([book["author"] for book in books])))
        selected_authors = st.multiselect("Autor", all_authors)

        # Filtro por estado de lectura
        st.subheader("Estado de lectura")
        show_all = st.checkbox("Todos los libros", value=True)
        show_read = st.checkbox("Libros leídos", value=False)
        show_unread = st.checkbox("Libros no leídos", value=False)

        st.markdown("---")

        # Estadísticas
        st.header("📊 Estadísticas")
        read_count = len(user_data.get("read_books", []))
        total_count = len(books)
        st.metric("Libros leídos", f"{read_count}/{total_count}")

        if read_count > 0:
            total_pages = sum([book["pages"] for book in books if book["id"] in user_data.get("read_books", [])])
            st.metric("Páginas leídas", f"{total_pages:,}")

            ratings = user_data.get("ratings", {})
            if ratings:
                avg_rating = sum(ratings.values()) / len(ratings)
                st.metric("Calificación promedio", f"{avg_rating:.1f}/5")

            genre_counts = {}
            for book in books:
                if book["id"] in user_data.get("read_books", []):
                    genre = book["genre"]
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1

            if genre_counts:
                st.subheader("Géneros más leídos")
                for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                    st.write(f"• {genre}: {count}")

    # ── Aplicar filtros para la biblioteca ──
    filtered_books = books

    if search_term:
        filtered_books = [b for b in filtered_books if search_term.lower() in b["title"].lower()]

    if selected_genres:
        filtered_books = [b for b in filtered_books if b["genre"] in selected_genres]

    if selected_authors:
        filtered_books = [b for b in filtered_books if b["author"] in selected_authors]

    if not show_all:
        if show_read and not show_unread:
            filtered_books = [b for b in filtered_books if b["id"] in user_data.get("read_books", [])]
        elif show_unread and not show_read:
            filtered_books = [b for b in filtered_books if b["id"] not in user_data.get("read_books", [])]
        elif show_read and show_unread:
            pass
        else:
            filtered_books = []

    # Resetear página si los filtros cambian
    filter_key = f"{search_term}_{selected_genres}_{selected_authors}_{show_all}_{show_read}_{show_unread}"
    if 'last_filter_key' not in st.session_state:
        st.session_state.last_filter_key = filter_key
    if st.session_state.last_filter_key != filter_key:
        st.session_state.current_page = 1
        st.session_state.last_filter_key = filter_key

    # ── Pestañas principales ──
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📖 Biblioteca",
        "⭐ Recomendaciones",
        "📊 Seguimiento",
        "📈 Mis Libros Leídos",
        "➕ Agregar Libro",
        "✏️ Editar Libro",
        "💬 Libros Chat"
    ])

    with tab1:
        tab_biblioteca.render(books, user_data, filtered_books)

    with tab2:
        tab_recomendaciones.render(books, user_data)

    with tab3:
        tab_seguimiento.render(books, user_data)

    with tab4:
        tab_mis_libros.render(books, user_data)

    with tab5:
        tab_agregar.render(books)

    with tab6:
        tab_editar.render(books, user_data)

    with tab7:
        tab_chat.render(books)


if __name__ == "__main__":
    main()
