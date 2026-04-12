"""
utils/image_gen.py
─────────────────────────────────────────────────────────────────────────────
Generazione immagini via HuggingFace Router → FLUX.1-schnell.

Funzioni esportate:
  - genera_prompt_visuale(risultato, tipo)  costruisce il prompt per uno dei
                                            tre tipi: "frontale", "laterale",
                                            "corpo"
  - query_image_model(prompt)               chiama l'API, ritorna i byte PNG
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import time
import requests
import streamlit as st

# ── Endpoint ──────────────────────────────────────────────────────────────────

API_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "black-forest-labs/FLUX.1-schnell"
)

# ── Stile base comune a tutti i prompt ───────────────────────────────────────

_STILE = (
    "Traditional Chinese ink wash painting, charcoal brush strokes "
    "on textured rice paper, ancient aesthetic, no text, no watermark."
)

# ── Prompt builder ────────────────────────────────────────────────────────────

def genera_prompt_visuale(risultato: dict, tipo: str = "frontale") -> str:
    """
    Costruisce il prompt FLUX per uno dei tre tipi di immagine.

    Parametri
    ---------
    risultato : dict
        Output di mayi_engine.analizza_descrizione()
    tipo : "frontale" | "laterale" | "corpo"

    Ritorna
    -------
    str — prompt in inglese ottimizzato per FLUX.1-schnell
    """
    if "errore" in risultato:
        return f"{_STILE} A serene five-elements figure, classical Chinese art."

    v = risultato.get("volto",     "human face")
    c = risultato.get("complexion","natural skin")
    b = risultato.get("corpo",     "human body")
    m = risultato.get("movimenti", "standing posture")

    if tipo == "frontale":
        return (
            f"{_STILE} "
            f"Frontal portrait of a person. Face features: {v}. "
            f"Complexion: {c}. Historical look, soft ink washes, "
            f"white rice-paper background, high detail."
        )
    elif tipo == "laterale":
        return (
            f"{_STILE} "
            f"Side profile view of a head and shoulders. "
            f"Face structure: {v}. "
            f"Elegant calligraphic brushstrokes, rice-paper background."
        )
    else:  # "corpo"
        return (
            f"{_STILE} "
            f"Full body standing portrait. Body: {b}. "
            f"Characteristic posture: {m}. "
            f"Complete figure from head to toe, classical ink wash style."
        )


# ── API call ──────────────────────────────────────────────────────────────────

def query_image_model(prompt: str) -> bytes | None:
    """
    Invia il prompt a FLUX.1-schnell via HuggingFace Router.
    Legge HF_TOKEN dai secrets di Streamlit.

    Ritorna i byte PNG dell'immagine, oppure None in caso di errore.
    """
    api_token = st.secrets.get("HF_TOKEN")
    if not api_token:
        st.error("🔑 HF_TOKEN non trovato nei Secrets di Streamlit.")
        return None

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": prompt,
        "parameters": {"wait_for_model": True},
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)

        # Cold start → retry dopo 25 s
        if response.status_code == 503:
            with st.spinner("FLUX si sta avviando… attendi 25 secondi."):
                time.sleep(25)
            response = requests.post(API_URL, headers=headers, json=payload, timeout=90)

        if response.status_code == 200:
            return response.content

        st.error(f"Errore Router ({response.status_code}): {response.text[:300]}")
        return None

    except requests.exceptions.Timeout:
        st.error("Timeout: FLUX non ha risposto entro 90 s. Riprova.")
        return None
    except Exception as exc:
        st.error(f"Errore di connessione: {exc}")
        return None
