import streamlit as st
import pandas as pd


def render(books, user_data):
    """Renderiza la pestaña de Mis Libros Leídos."""
    st.header("📈 Mis Libros Leídos")

    read_books = [b for b in books if b["id"] in user_data.get("read_books", [])]

    if not read_books:
        st.info("Aún no has marcado ningún libro como leído. ¡Comienza tu viaje literario!")
    else:
        st.write(f"Has leído {len(read_books)} libro(s)")

        # Crear DataFrame para visualización
        df_data = []
        for book in read_books:
            rating = user_data.get("ratings", {}).get(str(book["id"]), 0)
            df_data.append({
                "Título": book["title"],
                "Autor": book["author"],
                "Género": book["genre"],
                "Año": book["year"],
                "Páginas": book["pages"],
                "Calificación": "⭐" * rating if rating > 0 else "Sin calificar"
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, width="stretch", hide_index=True)

        # Análisis adicional
        st.subheader("Análisis de lectura")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Libros por género
            genre_counts = {}
            for book in read_books:
                genre = book["genre"]
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

            st.write("**Libros por género:**")
            for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True):
                st.write(f"• {genre}: {count}")

        with col2:
            # Autores más leídos
            author_counts = {}
            for book in read_books:
                author = book["author"]
                author_counts[author] = author_counts.get(author, 0) + 1

            st.write("**Autores más leídos:**")
            for author, count in sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                st.write(f"• {author}: {count}")

        with col3:
            # Libros mejor calificados
            rated_books = []
            for book in read_books:
                rating = user_data.get("ratings", {}).get(str(book["id"]), 0)
                if rating > 0:
                    rated_books.append((book["title"], rating))

            if rated_books:
                st.write("**Mejor calificados:**")
                for title, rating in sorted(rated_books, key=lambda x: x[1], reverse=True)[:5]:
                    st.write(f"• {title}: {'⭐' * rating}")
