import streamlit as st
from utils import save_books


def render(books):
    """Renderiza la pestaña de Agregar Libro."""
    st.header("➕ Agregar Nuevo Libro")
    st.write("Completa el formulario para añadir un nuevo libro a tu biblioteca.")

    with st.form("add_book_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            new_title = st.text_input("📖 Título del libro *", placeholder="Ej: El nombre del viento")
            new_author = st.text_input("✍️ Autor *", placeholder="Ej: Patrick Rothfuss")
            new_year = st.number_input("📅 Año de publicación *", min_value=1000, max_value=2026, value=2000, step=1)
            new_pages = st.number_input("📄 Número de páginas *", min_value=1, max_value=10000, value=300, step=1)

        with col2:
            # Obtener géneros únicos existentes
            existing_genres = sorted(list(set([book["genre"] for book in books])))

            genre_option = st.radio("🏷️ Género", ["Seleccionar existente", "Crear nuevo"])

            if genre_option == "Seleccionar existente":
                new_genre = st.selectbox("Selecciona un género *", existing_genres)
            else:
                new_genre = st.text_input("Escribe un nuevo género *", placeholder="Ej: Aventura")

            new_cover = st.text_input("🖼️ URL de la portada (opcional)", placeholder="https://ejemplo.com/portada.jpg")

        new_description = st.text_area(
            "📝 Descripción del libro *",
            placeholder="Escribe una breve descripción del libro...",
            height=120,
            max_chars=500
        )

        st.markdown("**Campos obligatorios marcados con * **")

        submitted = st.form_submit_button("✅ Agregar Libro", use_container_width=True, type="primary")

        if submitted:
            # Validar campos obligatorios
            if not new_title or not new_author or not new_genre or not new_description:
                st.error("⚠️ Por favor, completa todos los campos obligatorios.")
            else:
                # Obtener el ID más alto y sumar 1
                max_id = max([book["id"] for book in books]) if books else 0
                new_id = max_id + 1

                # Crear el nuevo libro
                new_book = {
                    "id": new_id,
                    "title": new_title.strip(),
                    "author": new_author.strip(),
                    "genre": new_genre.strip(),
                    "year": new_year,
                    "description": new_description.strip(),
                    "pages": new_pages
                }

                # Agregar cover solo si se proporcionó
                if new_cover and new_cover.strip():
                    new_book["cover"] = new_cover.strip()
                else:
                    new_book["cover"] = "https://via.placeholder.com/300x450/667eea/ffffff?text=Sin+Portada"

                # Agregar a la lista de libros
                books.append(new_book)

                # Guardar en el archivo
                save_books(books)

                st.success(f"✅ ¡Libro '{new_title}' agregado exitosamente!")
                st.balloons()
                st.info("💡 Recarga la página para ver el nuevo libro en la biblioteca.")
