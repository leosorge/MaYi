"""
utils/image_gen.py
─────────────────────────────────────────────────────────────────────────────
Generazione immagini via HuggingFace Router → FLUX.1-schnell.
Funzioni esportate:
  - genera_prompt_visuale(risultato)  : costruisce il prompt da un profilo Ma Yi
  - query_image_model(prompt)         : chiama l'API e ritorna i byte dell'immagine
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

# ── Prompt builder ────────────────────────────────────────────────────────────

# Palette cromatica per elemento (per arricchire il prompt visivo)
_PALETTE: dict[str, str] = {
    "Metallo": "silver and white tones, sharp clean lines, metallic sheen",
    "Legno":   "deep forest green and pale wood tones, slender tall figure",
    "Terra":   "warm ochre and terracotta, stocky solid build, earthy warmth",
    "Fuoco":   "deep crimson and amber, dynamic energetic pose, warm bronze skin",
    "Acqua":   "deep navy and ink-black, rounded soft silhouette, still water",
}

_VOLTO_EN: dict[str, str] = {
    "Metallo": "square jaw, deep-set eyes, straight nose",
    "Legno":   "long oval face, prominent forehead, thick lips",
    "Terra":   "large round face, wide mouth, broad nose",
    "Fuoco":   "diamond-shaped face, bushy eyebrows, exposed nostrils",
    "Acqua":   "round face, large eyes, thick arched eyebrows",
}

_CORPO_EN: dict[str, str] = {
    "Metallo": "slender upright posture, medium height, large-boned with lean limbs",
    "Legno":   "slim figure with long slender fingers",
    "Terra":   "stocky and stout, short neck, short fingers",
    "Fuoco":   "small upper body, wider lower body, small bony hands and feet",
    "Acqua":   "round and full figure, prominent belly, narrow shoulders",
}


def genera_prompt_visuale(risultato: dict) -> str:
    """
    Costruisce un prompt testuale per FLUX a partire dal dizionario
    restituito da analizza_descrizione().

    Parameters
    ----------
    risultato : dict
        Output di mayi_engine.analizza_descrizione()

    Returns
    -------
    str — prompt in inglese ottimizzato per FLUX.1-schnell
    """
    if "errore" in risultato:
        return "A serene Chinese ink painting, five elements, traditional art style."

    elemento = risultato.get("elemento", "Terra")
    eta      = risultato.get("eta", 45)
    zona     = risultato.get("zona_eta", "")

    palette = _PALETTE.get(elemento, "neutral tones")
    volto   = _VOLTO_EN.get(elemento, "")
    corpo   = _CORPO_EN.get(elemento, "")

    prompt = (
        f"Traditional Chinese ink painting portrait, Ma Yi physiognomy, "
        f"{elemento} element type. "
        f"Subject: approximately {eta} years old, {corpo}. "
        f"Face: {volto}. "
        f"Color palette: {palette}. "
        f"Active facial zone: {zona}. "
        f"Style: classical Chinese brush painting (水墨畫), soft ink washes, "
        f"white rice-paper background, elegant calligraphic brushstrokes, "
        f"no text, no watermark, high detail."
    )
    return prompt


# ── API call ──────────────────────────────────────────────────────────────────

def query_image_model(prompt: str) -> bytes | None:
    """
    Invia il prompt a FLUX.1-schnell via HuggingFace Router.
    Legge HF_TOKEN dai secrets di Streamlit.

    Returns
    -------
    bytes  — contenuto PNG/JPEG dell'immagine, oppure None in caso di errore.
    """
    api_token = st.secrets.get("HF_TOKEN")
    if not api_token:
        st.error("🔑 Token HF_TOKEN non trovato. Aggiungilo in Streamlit Secrets.")
        return None

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    payload = {"inputs": prompt}

    try:
        response = requests.post(
            API_URL, headers=headers, json=payload, timeout=120
        )

        # Modello in cold start → retry dopo 20 s
        if response.status_code == 503:
            with st.spinner("FLUX si sta avviando… attendi 20 secondi."):
                time.sleep(20)
            response = requests.post(
                API_URL, headers=headers, json=payload, timeout=120
            )

        if response.status_code == 200:
            return response.content

        st.error(f"Errore API ({response.status_code}): {response.text[:300]}")
        return None

    except requests.exceptions.Timeout:
        st.error("Timeout: FLUX non ha risposto entro 120 s. Riprova.")
        return None
    except Exception as exc:
        st.error(f"Errore connessione: {exc}")
        return None
