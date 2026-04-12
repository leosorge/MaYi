# Generatore d'immagini 
# Usa stable diffusion base
# attraverso API huggingface

import streamlit as st
import requests
import io

# Recupera il token dai secrets di Streamlit
# Assicurati di aver aggiunto HF_TOKEN = "il_tuo_token" nei Secrets della tua app
API_TOKEN = st.secrets["HF_TOKEN"]

# Modello consigliato per uno stile artistico coerente con la tradizione cinese
# Puoi cambiare questo URL con altri modelli (es. FLUX.1 o SD-XL)
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

def query_image_model(prompt: str) -> bytes:
    """
    Invia il prompt all'Inference API di Hugging Face e restituisce i dati binari dell'immagine.
    """
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "low quality, blurry, modern clothing, 3d render, photo, realistic, sunglasses",
            "num_inference_steps": 30
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Errore durante la generazione dell'immagine: {e}")
        return None

def genera_prompt_visuale(risultato: dict, tipo: str = "frontale") -> str:
    """
    Costruisce un prompt in inglese ottimizzato per l'IA, traducendo le 
    caratteristiche antropometriche Ma Yi in istruzioni visive.
    """
    elemento = risultato.get('elemento', 'Metallo')
    corpo = risultato.get('corpo', '')
    volto = risultato.get('volto', '')
    complexion = risultato.get('complexion', '')
    movimenti = risultato.get('movimenti', '')

    # Stile artistico di base: pittura tradizionale a inchiostro cinese su pergamena
    base_style = (
        "Ancient Chinese ink wash painting style, Shan shui aesthetic, "
        "traditional brush strokes, charcoal lines, textured rice paper background, "
        "subtle earth tones, minimalist composition."
    )
    
    # Dettagli fisici derivati dal database Ma Yi
    physical_traits = f"A person with {volto}, {complexion} skin tone."
    
    if tipo == "frontale":
        return (
            f"{base_style} Symmetrical front portrait of a person. "
            f"{physical_traits} Calm and dignified expression, frontal view."
        )
    
    elif tipo == "laterale":
        return (
            f"{base_style} Lateral side profile view portrait. "
            f"Focus on the structure of the nose and jawline. {physical_traits}"
        )
    
    elif tipo == "corpo":
        # Combina la descrizione del corpo e della postura
        return (
            f"{base_style} Full body standing shot. {corpo}. "
            f"Posture and movement: {movimenti}. "
            f"Wearing traditional Hanfu robes reflecting the {elemento} element style."
        )
    
    return f"{base_style} Portrait of a person, {elemento} element."
