import streamlit as st
import requests
import time

# Recupera il token dai secrets
API_TOKEN = st.secrets.get("HF_TOKEN")

# Usiamo l'endpoint di SD 2.1, solitamente più stabile del 1.5 su HF
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

def query_image_model(prompt):
    if not API_TOKEN:
        st.error("HF_TOKEN non trovato nei Secrets!")
        return None

    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"wait_for_model": True}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        # Se il modello è in caricamento (503), aspettiamo una volta sola
        if response.status_code == 503:
            with st.spinner("Il modello si sta svegliando... attendi 15 secondi"):
                time.sleep(15)
                response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Errore API ({response.status_code}): {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Errore di connessione: {e}")
        return None

def genera_prompt_visuale(risultato, tipo="frontale"):
    """Costruisce il prompt partendo dai dati Ma Yi dell'engine."""
    v = risultato.get('volto', 'human face')
    c = risultato.get('complexion', 'natural')
    b = risultato.get('corpo', 'person')
    m = risultato.get('movimenti', 'standing')
    
    # Stile: pittura a inchiostro per coerenza storica
    stile = "Ancient Chinese ink wash painting, traditional aesthetic, charcoal lines on parchment."
    
    if tipo == "frontale":
        return f"{stile} Frontal portrait, close-up, {v}, {c} skin."
    elif tipo == "laterale":
        return f"{stile} Side profile view, profile of the head, {v}."
    else:
        return f"{stile} Full body view, {b}, posture: {m}."
