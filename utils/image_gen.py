import streamlit as st
import requests
import time
import io

API_TOKEN = st.secrets.get("HF_TOKEN")
# Endpoint FLUX
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

def query_image_model(prompt):
    if not API_TOKEN:
        st.error("Token HF_TOKEN non trovato.")
        return None

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # FLUX su Router vuole solo gli inputs. 
    # Rimuoviamo 'parameters' per evitare conflitti di versione.
    payload = {
        "inputs": prompt
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        
        # Se il modello è in caricamento, il router restituirà un 503 o un tempo di attesa.
        # Gestiamo il retry manualmente dato che non possiamo usare wait_for_model.
        if response.status_code == 503:
            with st.spinner("FLUX si sta scaldando... attendi 20 secondi."):
                time.sleep(20)
                response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Errore Router ({response.status_code}): {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Errore connessione: {e}")
        return None
