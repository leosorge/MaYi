import streamlit as st
import io
from huggingface_hub import InferenceClient

# Recupera il token dai secrets
API_TOKEN = st.secrets.get("HF_TOKEN")

# Inizializziamo il client ufficiale
# Usiamo un modello molto comune e stabile: Stable Diffusion v1.5 o XL
client = InferenceClient(token=API_TOKEN)

def query_image_model(prompt):
    if not API_TOKEN:
        st.error("HF_TOKEN mancante nei Secrets.")
        return None

    try:
        # Il client ufficiale gestisce automaticamente il routing corretto
        image = client.text_to_image(
            prompt,
            model="runwayml/stable-diffusion-v1-5", # Modello con massima disponibilità
            negative_prompt="modern, low quality, blurry, 3d render",
        )
        
        # Convertiamo l'oggetto PIL Image in bytes per Streamlit
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    except Exception as e:
        st.error(f"Errore durante la generazione: {e}")
        return None

def genera_prompt_visuale(risultato, tipo="frontale"):
    """Costruisce il prompt basato sui dati Ma Yi."""
    v = risultato.get('volto', 'human face')
    c = risultato.get('complexion', 'natural skin')
    b = risultato.get('corpo', 'human body')
    m = risultato.get('movimenti', 'posture')
    
    stile = "Traditional Chinese ink painting, charcoal strokes, aged parchment aesthetic."
    
    if tipo == "frontale":
        return f"{stile} Frontal portrait, close-up, {v}, {c}."
    elif tipo == "laterale":
        return f"{stile} Side profile view, profile of the head, {v}."
    else:
        return f"{stile} Full body standing, {b}, posture: {m}."
