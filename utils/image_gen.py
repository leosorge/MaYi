import streamlit as st
import requests
import time
import io

# Recupera il token dai secrets
API_TOKEN = st.secrets.get("HF_TOKEN")

# ENDPOINT AGGIORNATO: Usiamo SDXL che è il modello standard del nuovo Router
API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

def query_image_model(prompt):
    if not API_TOKEN:
        st.error("Token HF_TOKEN non trovato nei Secrets.")
        return None

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # SDXL richiede questa struttura di payload
    payload = {
        "inputs": prompt,
        "parameters": {
            "wait_for_model": True,
            "negative_prompt": "modern, photo, blurry, bad anatomy, text, watermark"
        }
    }
    
    try:
        # Chiamata al Router
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        
        # Gestione caricamento modello
        if response.status_code == 503:
            with st.spinner("Il Router sta caricando il modello (può richiedere un minuto)..."):
                time.sleep(25)
                response = requests.post(API_URL, headers=headers, json=payload, timeout=90)

        if response.status_code == 200:
            return response.content
        else:
            # Se ancora 404, proviamo un modello alternativo d'emergenza
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
    
    # Stile: pittura tradizionale cinese
    stile = "Ancient Chinese ink wash painting, traditional aesthetic, charcoal strokes, aged paper texture."
    
    if tipo == "frontale":
        return f"{stile} Close-up front portrait, {v}, {c}."
    elif tipo == "laterale":
        return f"{stile} Side profile view, profile of the head, {v}."
    else:
        return f"{stile} Full body standing, {b}, characteristic posture: {m}."
