import streamlit as st
import requests
import time
import io

# Recupera il token dai secrets
API_TOKEN = st.secrets.get("HF_TOKEN")

# ENDPOINT FLUX (Supportato dal Router nel 2026)
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

def query_image_model(prompt):
    if not API_TOKEN:
        st.error("HF_TOKEN non trovato nei Secrets.")
        return None

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # FLUX non supporta il negative_prompt nell'API Router semplice
    payload = {
        "inputs": prompt,
        "parameters": {
            "wait_for_model": True
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        
        # Gestione caricamento (Cold Start)
        if response.status_code == 503:
            time.sleep(25)
            response = requests.post(API_URL, headers=headers, json=payload, timeout=90)

        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Errore Router ({response.status_code}): {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Errore di connessione: {e}")
        return None

def genera_prompt_visuale(risultato, tipo="frontale"):
    v = risultato.get('volto', 'human face')
    c = risultato.get('complexion', 'skin')
    b = risultato.get('corpo', 'body')
    m = risultato.get('movimenti', 'posture')
    
    # Stile: pittura a inchiostro cinese
    stile = "Traditional Chinese ink wash painting, charcoal brush strokes on textured rice paper, ancient aesthetic."
    
    if tipo == "frontale":
        return f"{stile} Frontal portrait of a person, {v}, {c} complexion. Historical look."
    elif tipo == "laterale":
        return f"{stile} Side profile view of a head, focus on {v} structure."
    else:
        return f"{stile} Full body standing portrait, {b}, characteristic posture: {m}."
