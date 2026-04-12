"""
utils/image_gen.py
─────────────────────────────────────────────────────────────────────────────
Generazione immagini via HuggingFace Router → FLUX.1-schnell.
Stile: fotorealistico, neutro etnicamente, basato sui dati Ma Yi.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import time
import requests
import streamlit as st

API_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "black-forest-labs/FLUX.1-schnell"
)

# ── Traduzione dati Ma Yi per elemento ───────────────────────────────────────

_CORPO_EN: dict[str, str] = {
    "Metallo": "slender upright figure, medium height, large-boned with lean limbs",
    "Legno":   "slim tall figure, long slender fingers, delicate build",
    "Terra":   "stocky compact figure, short neck, short fingers, heavyset",
    "Fuoco":   "narrow shoulders, wider hips, small hands and feet",
    "Acqua":   "round full figure, prominent belly, narrow shoulders",
}

_VOLTO_EN: dict[str, str] = {
    "Metallo": "square jaw, high arched eyebrows, deep-set eyes, straight prominent nose",
    "Legno":   "long oval face, prominent forehead, thick lips",
    "Terra":   "large round face, wide mouth, broad flat nose",
    "Fuoco":   "diamond-shaped face, bushy eyebrows, flared nostrils",
    "Acqua":   "round soft face, large eyes, thick arched eyebrows",
}

_CARNAGIONE_EN: dict[str, str] = {
    "Metallo": "fair pale skin",
    "Legno":   "pale slightly greenish skin tone",
    "Terra":   "warm olive yellow skin",
    "Fuoco":   "bronzed reddish skin",
    "Acqua":   "dark olive skin",
}

_MOVIMENTI_EN: dict[str, str] = {
    "Metallo": "confident posture, controlled precise movements",
    "Legno":   "reserved quiet stance, deliberate gestures",
    "Terra":   "heavy stable posture, slow movements",
    "Fuoco":   "dynamic energetic stance, restless body language",
    "Acqua":   "slow fluid movements, slightly closed introverted posture",
}

_ZONA_EN: dict[str, str] = {
    "Orecchie": "well-defined ears",
    "Fronte":   "prominent forehead",
    "Occhi":    "striking expressive eyes",
    "Naso":     "strong prominent nose",
    "Bocca":    "defined full lips and chin",
    "Mascella": "strong defined jawline",
}

# Didascalie brevi in italiano per ogni tipo
DIDASCALIE: dict[str, str] = {
    "frontale": "Ritratto frontale",
    "laterale": "Profilo laterale",
    "corpo":    "Figura intera",
}

# Stile base fotorealistico
_STILE = (
    "Photorealistic portrait photography, studio lighting, "
    "neutral background, sharp focus, 8k resolution, "
    "cinematic, no text, no watermark"
)

def _eta_desc(eta: int) -> str:
    if eta <= 20:   return "young adult, around 20 years old"
    elif eta <= 35: return "adult, around 30 years old"
    elif eta <= 55: return "middle-aged, around 45 years old"
    else:           return "elderly, around 65 years old"


def genera_prompt_visuale(risultato: dict, tipo: str = "frontale") -> str:
    if "errore" in risultato:
        return f"{_STILE}. Portrait of a person."

    elemento   = risultato.get("elemento", "Terra")
    eta        = risultato.get("eta", 45)
    zona_ita   = risultato.get("zona_eta", "")

    corpo      = _CORPO_EN.get(elemento, "")
    volto      = _VOLTO_EN.get(elemento, "")
    carnagione = _CARNAGIONE_EN.get(elemento, "")
    movimenti  = _MOVIMENTI_EN.get(elemento, "")
    zona_en    = _ZONA_EN.get(zona_ita, "")
    eta_en     = _eta_desc(eta)

    if tipo == "frontale":
        return (
            f"{_STILE}. "
            f"Frontal face portrait, {eta_en}. "
            f"Facial features: {volto}. "
            f"{carnagione}. "
            f"Facial focal point: {zona_en}."
        )
    elif tipo == "laterale":
        return (
            f"{_STILE}. "
            f"Side profile portrait, head and shoulders, {eta_en}. "
            f"Facial features in profile: {volto}. "
            f"{carnagione}."
        )
    else:  # corpo
        return (
            f"{_STILE}. "
            f"Full body portrait, {eta_en}. "
            f"Body build: {corpo}. "
            f"Posture: {movimenti}."
        )


def genera_didascalia(risultato: dict, tipo: str) -> str:
    """Didascalia breve in italiano da mostrare sotto l'immagine."""
    elemento = risultato.get("elemento", "")
    eta      = risultato.get("eta", "")
    zona     = risultato.get("zona_eta", "")

    base = DIDASCALIE.get(tipo, tipo.capitalize())

    if tipo == "frontale":
        return f"{base} — {elemento}, {eta} anni. Zona: {zona}."
    elif tipo == "laterale":
        return f"{base} — profilo {elemento}."
    else:
        return f"{base} — corporatura {elemento}, {eta} anni."


# ── API call ──────────────────────────────────────────────────────────────────

def query_image_model(prompt: str) -> bytes | None:
    api_token = st.secrets.get("HF_TOKEN")
    if not api_token:
        st.error("🔑 HF_TOKEN non trovato nei Secrets di Streamlit.")
        return None

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    payload = {"inputs": prompt}

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)

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
