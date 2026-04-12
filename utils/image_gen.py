import streamlit as st
import requests
import time
import io

# Recupera il token dai secrets
API_TOKEN = st.secrets.get("HF_TOKEN")

# Endpoint più stabile in assoluto per le API gratuite
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

def query_image_model(prompt):
    if not API_TOKEN:
        st.error("HF_TOKEN non impostato correttamente nei Secrets.")
        return None

    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"wait_for_model": True}
    }
    
    try:
        # Usiamo requests per evitare conflitti di librerie esterne
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.content
        
        # Gestione modello in caricamento (Cold Start)
        if response.status_code == 503:
            with st.spinner("Il modello si sta risvegliando sui server... attendi 20 secondi"):
                time.sleep(20)
                # Unico tentativo di retry
                response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    return response.content

        st.error(f"Errore API ({response.status_code}): {response.text}")
        return None
        
    except Exception as e:
        st.error(f"Errore di rete: {e}")
        return None

def genera_prompt_visuale(risultato, tipo="frontale"):
    v = risultato.get('volto', 'face')
    c = risultato.get('complexion', 'skin')
    b = risultato.get('corpo', 'body')
    m = risultato.get('movimenti', 'posture')
    
    # Stile artistico fisso per evitare errori semantici
    stile = "Ancient Chinese ink wash painting, traditional aesthetic, charcoal strokes on old parchment."
    
    if tipo == "frontale":
        return f"{stile} Close-up frontal portrait, {v}, {c}."
    elif tipo == "laterale":
        return f"{stile} Side profile portrait, {v} structure."
    else:
        return f"{stile} Full body standing portrait, {b}, {m}."
