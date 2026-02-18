import streamlit as st
import json
from pathlib import Path

# Rutas a archivos de datos
BOOKS_FILE = Path("data/books.json")
USER_DATA_FILE = Path("data/user_data.json")
API_KEY_FILE = Path("data/api_key.json")

# Función para cargar API Key
def load_api_key():
    if not API_KEY_FILE.exists():
        return ""
    try:
        with open(API_KEY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("gemini_api_key", "")
    except:
        return ""

# Función para guardar API Key
def save_api_key(api_key):
    try:
        with open(API_KEY_FILE, 'w', encoding='utf-8') as f:
            json.dump({"gemini_api_key": api_key}, f, indent=2, ensure_ascii=False)
    except:
        pass

# Función para cargar libros
@st.cache_data
def load_books():
    with open(BOOKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Función para cargar datos del usuario
def load_user_data():
    if not USER_DATA_FILE.exists():
        return {"read_books": [], "ratings": {}}
    with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Función para guardar datos del usuario
def save_user_data(user_data):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=2, ensure_ascii=False)

# Función para guardar libros
def save_books(books):
    with open(BOOKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=2, ensure_ascii=False)
    # Limpiar caché para recargar los libros
    load_books.clear()

# Función para obtener recomendaciones
def get_recommendations(books, user_data, limit=5):
    read_books = user_data.get("read_books", [])
    ratings = user_data.get("ratings", {})
    
    # Si no hay libros leídos, recomendar los más populares
    if not read_books:
        return books[:limit]
    
    # Calcular géneros favoritos basados en calificaciones altas
    favorite_genres = {}
    for book_id, rating in ratings.items():
        if rating >= 4:
            book = next((b for b in books if b["id"] == int(book_id)), None)
            if book:
                genre = book["genre"]
                favorite_genres[genre] = favorite_genres.get(genre, 0) + rating
    
    # Ordenar géneros por puntuación
    sorted_genres = sorted(favorite_genres.items(), key=lambda x: x[1], reverse=True)
    
    # Recomendar libros no leídos de géneros favoritos
    recommendations = []
    for genre, _ in sorted_genres:
        for book in books:
            if book["id"] not in read_books and book["genre"] == genre:
                if book not in recommendations:
                    recommendations.append(book)
                    if len(recommendations) >= limit:
                        break
        if len(recommendations) >= limit:
            break
    
    # Si no hay suficientes, añadir libros no leídos aleatorios
    if len(recommendations) < limit:
        for book in books:
            if book["id"] not in read_books and book not in recommendations:
                recommendations.append(book)
                if len(recommendations) >= limit:
                    break
    
    return recommendations[:limit]

# Función para mostrar una tarjeta de libro
def display_book_card(book, user_data, col, key_prefix=""):
    with col:
        # Contenedor con altura mínima
        st.markdown("""
        <style>
        .book-container {
            min-height: 320px;
            display: flex;
            flex-direction: column;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            # Layout horizontal: imagen y contenido
            img_col, content_col = st.columns([1, 3])
            
            # Columna de imagen con tamaño fijo
            with img_col:
                cover_url = book.get("cover", "")
                if cover_url:
                    st.markdown(f"""
                    <div style="width: 100px; height: 150px; overflow: hidden; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); background-color: #f0f0f0;">
                        <img src="{cover_url}" style="width: 100%; height: 100%; object-fit: cover;" />
                    </div>
                    """, unsafe_allow_html=True)
            
            # Columna de contenido
            with content_col:
                # Título con máximo 2 líneas
                title = book['title']
                if len(title) > 50:
                    title = title[:47] + "..."
                
                st.markdown(f"""
                <div style="padding: 5px;">
                    <h3 style="margin-top: 0; font-size: 1.1em; margin-bottom: 10px; border-bottom: 2px solid #667eea; padding-bottom: 5px; font-weight: 600; line-height: 1.3; max-height: 2.6em; overflow: hidden;">
                        📖 {title}
                    </h3>
                    <p style="margin: 6px 0; font-size: 0.9em; line-height: 1.4;">
                        <strong>✍️ Autor:</strong> {book['author']}
                    </p>
                    <p style="margin: 6px 0; font-size: 0.9em; line-height: 1.4;">
                        <strong>🏷️ Género:</strong> <span style="background-color: #667eea; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 500;">{book['genre']}</span>
                    </p>
                    <p style="margin: 6px 0; font-size: 0.9em; line-height: 1.4;">
                        <strong>📅 Año:</strong> {book['year']} &nbsp;&nbsp; <strong>📄 Páginas:</strong> {book['pages']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Descripción con altura fija
            description = book['description']
            if len(description) > 150:
                description = description[:147] + "..."
            
            st.markdown(f"""
            <div style="
                height: 85px;
                overflow: hidden;
                padding: 10px;
                background-color: rgba(102, 126, 234, 0.08);
                border-left: 3px solid #667eea;
                border-radius: 5px;
                margin: 12px 0 8px 0;
                font-size: 0.88em;
                line-height: 1.5;">
                {description}
            </div>
            """, unsafe_allow_html=True)
        
        # Estado de lectura
        is_read = book["id"] in user_data.get("read_books", [])
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if is_read:
                st.success("✓ Leído")
            else:
                if st.button(f"Marcar como leído", key=f"{key_prefix}read_{book['id']}"):
                    user_data["read_books"].append(book["id"])
                    save_user_data(user_data)
                    st.rerun()
        
        with col2:
            if is_read:
                if st.button(f"Marcar como no leído", key=f"{key_prefix}unread_{book['id']}"):
                    user_data["read_books"].remove(book["id"])
                    if str(book["id"]) in user_data.get("ratings", {}):
                        del user_data["ratings"][str(book["id"])]
                    save_user_data(user_data)
                    st.rerun()
        
        # Calificación (solo si está marcado como leído)
        if is_read:
            current_rating = user_data.get("ratings", {}).get(str(book["id"]), 0)
            rating = st.slider(
                "Calificación",
                0, 5, 
                current_rating,
                key=f"{key_prefix}rating_{book['id']}"
            )
            if rating != current_rating:
                if "ratings" not in user_data:
                    user_data["ratings"] = {}
                user_data["ratings"][str(book["id"])] = rating
                save_user_data(user_data)
        
        st.markdown("---")
