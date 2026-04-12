import streamlit as st
import requests
import time
import io

# Recupera il token dai secrets
API_TOKEN = st.secrets.get("HF_TOKEN")

# Endpoint stabile che non richiede la libreria huggingface_hub
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

def query_image_model(prompt):
    if not API_TOKEN:
        st.error("HF_TOKEN non trovato nei Secrets.")
        return None

    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"wait_for_model": True}
    }
    
    try:
        # Usiamo requests che è sempre disponibile
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            st.warning("Il modello si sta caricando sui server... attendi 20 secondi.")
            time.sleep(20)
            return query_image_model(prompt) # Riprova una volta
        else:
            st.error(f"Errore API ({response.status_code})")
            return None
    except Exception as e:
        st.error(f"Errore connessione: {e}")
        return None

def genera_prompt_visuale(risultato, tipo="frontale"):
    v = risultato.get('volto', 'human face')
    c = risultato.get('complexion', 'skin')
    b = risultato.get('corpo', 'body')
    m = risultato.get('movimenti', 'posture')
    
    stile = "Ancient Chinese ink wash painting, traditional aesthetic, charcoal strokes, aged paper."
    
    if tipo == "frontale":
        return f"{stile} Frontal portrait, close-up, {v}, {c}."
    elif tipo == "laterale":
        return f"{stile} Side profile view, profile of the head, {v}."
    else:
        return f"{stile} Full body standing, {b}, posture: {m}."
