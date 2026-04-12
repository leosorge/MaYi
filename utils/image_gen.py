import streamlit as st
import requests
import time
import io

# Recupera il token dai secrets
API_TOKEN = st.secrets.get("HF_TOKEN")

# NUOVO ENDPOINT ROUTER OBBLIGATORIO (Aprile 2026)
API_URL = "https://router.huggingface.co/hf-inference/models/runwayml/stable-diffusion-v1-5"

def query_image_model(prompt):
    if not API_TOKEN:
        st.error("Token HF_TOKEN non trovato nei Secrets.")
        return None

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {"wait_for_model": True}
    }
    
    try:
        # Chiamata al nuovo Router
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        # Se il router risponde 503, il modello è in "cold start"
        if response.status_code == 503:
            with st.spinner("Il nuovo Router sta svegliando il modello..."):
                time.sleep(20)
                response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Errore Router ({response.status_code}): {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Errore di connessione: {e}")
        return None

def genera_prompt_visuale(risultato, tipo="frontale"):
    v = risultato.get('volto', 'face')
    c = risultato.get('complexion', 'skin')
    b = risultato.get('corpo', 'body')
    m = risultato.get('movimenti', 'posture')
    
    stile = "Ancient Chinese ink wash painting, traditional aesthetic, charcoal lines, aged paper."
    
    if tipo == "frontale":
        return f"{stile} Frontal portrait, close-up, {v}, {c}."
    elif tipo == "laterale":
        return f"{stile} Side profile view, {v}."
    else:
        return f"{stile} Full body standing, {b}, posture: {m}."
