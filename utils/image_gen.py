import streamlit as st
from huggingface_hub import InferenceClient
import io

# Recupera il token
API_TOKEN = st.secrets.get("HF_TOKEN")

# Inizializza il client (gestisce lui il nuovo routing)
client = InferenceClient(token=API_TOKEN)

def query_image_model(prompt):
    try:
        # Usiamo SDXL o SD 1.5 - quelli con più "uptime"
        image = client.text_to_image(
            prompt,
            model="stabilityai/stable-diffusion-2-1"
        )
        
        # Conversione in byte per Streamlit
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        st.error(f"Errore generazione: {e}")
        return None
