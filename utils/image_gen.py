"""
utils/image_gen.py
─────────────────────────────────────────────────────────────────────────────
Generazione immagini via HuggingFace Router → FLUX.1-schnell.
I prompt sono costruiti a partire dai dati reali della scheda Ma Yi,
traducendo e normalizzando i campi italiani per FLUX.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import time
import requests
import streamlit as st

# ── Endpoint ──────────────────────────────────────────────────────────────────

API_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "black-forest-labs/FLUX.1-schnell"
)

# ── Dizionari di traduzione dai valori Ma Yi ──────────────────────────────────

# Corpo per elemento
_CORPO_EN: dict[str, str] = {
    "Metallo":    "slender upright figure, medium height, large-boned with lean limbs, straight posture",
    "Legno":      "slim tall figure, long slender fingers, delicate build",
    "Terra":      "stocky compact figure, short neck, short fingers, heavyset",
    "Fuoco":      "narrow shoulders, wide hips, small hands and feet, energetic stance",
    "Acqua":      "round full figure, prominent belly, narrow shoulders, flat buttocks",
}

# Volto per elemento
_VOLTO_EN: dict[str, str] = {
    "Metallo":    "square jaw, high arched eyebrows, deep-set eyes, straight nose, firm expression",
    "Legno":      "long oval face, prominent forehead, thick lips, thoughtful expression",
    "Terra":      "large round face, wide mouth, broad flat nose, serene expression",
    "Fuoco":      "diamond-shaped face, bushy eyebrows, flared nostrils, intense gaze",
    "Acqua":      "round soft face, large eyes, thick arched eyebrows, gentle expression",
}

# Carnagione per elemento
_CARNAGIONE_EN: dict[str, str] = {
    "Metallo":    "pale white complexion",
    "Legno":      "greenish pale complexion",
    "Terra":      "warm yellow ochre complexion",
    "Fuoco":      "bronze reddish complexion",
    "Acqua":      "dark olive complexion",
}

# Movimenti per elemento
_MOVIMENTI_EN: dict[str, str] = {
    "Metallo":    "confident steady gait, precise controlled movements",
    "Legno":      "vigorous but reserved movements, quiet deliberate gestures",
    "Terra":      "slow heavy posture, solid stable stance",
    "Fuoco":      "impulsive rapid movements, dynamic restless energy",
    "Acqua":      "slow fluid movements, closed introverted posture",
}

# Zona del volto attiva per età
_ZONA_EN: dict[str, str] = {
    "Orecchie":  "ears clearly defined",
    "Fronte":    "prominent forehead",
    "Occhi":     "expressive eyes as focal point",
    "Naso":      "strong prominent nose as focal point",
    "Bocca":     "defined mouth and chin",
    "Mascella":  "strong jaw and chin",
}

# Stile pittorico base
_STILE = (
    "Traditional Chinese ink wash painting (水墨畫), "
    "charcoal brush strokes on textured rice paper, "
    "soft ink washes, white rice-paper background, "
    "no text, no watermark, high detail"
)


def _pulisci(testo: str) -> str:
    """Rimuove riferimenti bibliografici tipo [2, 4] e testo extra."""
    return re.sub(r"\s*\[\d+(?:,\s*\d+)*\]", "", testo).strip()


def genera_prompt_visuale(risultato: dict, tipo: str = "frontale") -> str:
    """
    Costruisce il prompt FLUX usando i dati reali della scheda Ma Yi.

    Parametri
    ---------
    risultato : dict  — output di mayi_engine.analizza_descrizione()
    tipo      : str   — "frontale" | "laterale" | "corpo"
    """
    if "errore" in risultato:
        return f"{_STILE}. A serene scholar figure, five elements theme."

    elemento = risultato.get("elemento", "Terra")
    eta      = risultato.get("eta", 45)
    zona_ita = risultato.get("zona_eta", "")

    # Usa i dizionari tradotti — valori precisi e puliti per FLUX
    corpo      = _CORPO_EN.get(elemento, _pulisci(risultato.get("corpo", "")))
    volto      = _VOLTO_EN.get(elemento, _pulisci(risultato.get("volto", "")))
    carnagione = _CARNAGIONE_EN.get(elemento, _pulisci(risultato.get("complexion", "")))
    movimenti  = _MOVIMENTI_EN.get(elemento, _pulisci(risultato.get("movimenti", "")))
    zona_en    = _ZONA_EN.get(zona_ita, "")

    # Età come fascia descrittiva
    if eta <= 20:
        eta_desc = "young adult, approximately 20 years old"
    elif eta <= 35:
        eta_desc = "adult, approximately 30 years old"
    elif eta <= 55:
        eta_desc = "middle-aged, approximately 45 years old"
    else:
        eta_desc = "elderly, approximately 65 years old"

    if tipo == "frontale":
        return (
            f"{_STILE}. "
            f"Frontal portrait. {eta_desc}. "
            f"Face: {volto}. "
            f"{carnagione}. "
            f"{zona_en}. "
            f"Ancient Chinese historical figure, scholar aesthetic."
        )
    elif tipo == "laterale":
        return (
            f"{_STILE}. "
            f"Side profile portrait, head and shoulders only. {eta_desc}. "
            f"Profile of face: {volto}. "
            f"{carnagione}. "
            f"Ancient Chinese historical figure, elegant brushwork."
        )
    else:  # corpo
        return (
            f"{_STILE}. "
            f"Full body standing portrait, complete figure head to toe. {eta_desc}. "
            f"Body build: {corpo}. "
            f"Posture and movement: {movimenti}. "
            f"Ancient Chinese historical figure, traditional robes."
        )


# ── API call ──────────────────────────────────────────────────────────────────

def query_image_model(prompt: str) -> bytes | None:
    """
    Invia il prompt a FLUX.1-schnell via HuggingFace Router.
    Legge HF_TOKEN dai Secrets di Streamlit.
    """
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
