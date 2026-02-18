import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# Page Configuration
st.set_page_config(page_title="Conchita Image Gen", page_icon="🎨")
st.title("🎨 Conchita Image Generator")

# Sidebar for Setup
with st.sidebar:
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.info("Powered by Nano Banana technology.")
# Main Interface
if api_key:
    client = genai.Client(api_key=api_key)

    # User Inputs
    description = st.text_area("What image do you want to generate?", 
                              placeholder="e.g., A futuristic city with flying cars")
    
    style = st.radio(
        "Choose your style:",
        ["Photorealistic", "Cartoon", "Oil Painting", "Cyberpunk", "Sketch"],
        horizontal=True
    )

    if st.button("Generate with Conchita"):
        if description:
            # Combining the user description with the selected style
            full_prompt = f"Create an image of {description} in a {style} style."
            
            with st.spinner("Conchita is painting your masterpiece..."):
                try:
                    # Requesting the image from Nano Banana (Gemini 2.5 Flash Image)
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-image",
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            response_modalities=["IMAGE"]
                        )
                    )
                    
                    # Loop through parts to find the image data
                    for part in response.parts:
                        if part.inline_data:
                                # Get the raw bytes directly
                                image_bytes = part.inline_data.data
        
                                # Display the image using the raw bytes
                                st.image(image_bytes, caption=f"Style: {style}", use_container_width=True)

                            
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please describe what you want to see!")
else:
    st.warning("Please enter your API Key in the sidebar to begin.")