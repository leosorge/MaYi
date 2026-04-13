"""
utils/image_gen.py
─────────────────────────────────────────────────────────────────────────────
Generazione immagini via HuggingFace Router → FLUX.1-schnell.
Fotorealistico, con rilevamento sesso dal nome e dati Ma Yi.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
import re, time, requests
import streamlit as st

API_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "black-forest-labs/FLUX.1-schnell"
)

# ── Rilevamento sesso dal nome ────────────────────────────────────────────────

# Nomi italiani esplicitamente maschili
_NOMI_M = {
    "marco","luca","andrea","giuseppe","antonio","mario","franco","roberto",
    "giovanni","paolo","luigi","giorgio","stefano","massimo","angelo","carlo",
    "pietro","matteo","davide","alberto","filippo","aldo","bruno","claudio",
    "daniele","emilio","enrico","fabio","gianni","ivan","leonardo","lorenzo",
    "mauro","nicola","oscar","piero","riccardo","sandro","sergio","silvio",
    "tiziano","umberto","valentino","vittorio","augusto","cesare","dario",
    "edoardo","ernesto","ettore","fausto","felice","fernando","flavio",
    "fortunato","franco","gerardo","giacomo","gino","giulio","guido","igor",
    "ilario","lauro","leone","lino","livio","loris","luciano","marcello",
    "marino","maurizio","mirco","mirko","moreno","nino","olimpio","oreste",
    "ottavio","remo","renzo","rocco","romeo","ruggero","salvatore","samuele",
    "sebastiano","simone","teo","teodoro","tommaso","tullio","ugo","valerio",
    "vincenzo","vladimiro","walter","zeno","romeo","achille","adriano",
    "agostino","alan","aldo","alfio","alfredo","amedeo","amerigo",
}

# Nomi italiani esplicitamente femminili
_NOMI_F = {
    "maria","anna","laura","sara","giulia","francesca","paola","elena","rosa",
    "angela","lucia","giovanna","teresa","daniela","chiara","roberta","silvia",
    "monica","alessandra","valeria","patrizia","cristina","barbara","claudia",
    "carla","rita","elisa","simona","federica","marta","ilaria","beatrice",
    "serena","valentina","lorena","eleonora","irene","miriam","nadia","norma",
    "ornella","piera","raffaella","renata","rossella","sabrina","sandra",
    "silvana","stefania","susanna","tamara","tiziana","ursula","vera","viviana",
    "wanda","yvonne","zelda","agata","alba","alberta","aldina","alessia",
    "alfonsina","alida","amalia","amelia","anastasia","angela","angelica",
    "anita","antonia","antonella","arianna","assunta","aurora","azzurra",
    "benedetta","bice","bruna","camilla","carlotta","caterina","cecilia",
    "celeste","cinzia","cira","clara","concetta","costanza","cristiana",
    "dalila","debora","diletta","dora","donatella","edda","elda","elettra",
    "emanuela","emma","enrichetta","erica","erminia","ester","eugenia","eva",
    "fernanda","fiorella","flaminia","flora","floriana","franca","gemma",
    "giada","gina","ginevra","giorgia","gisella","giuseppina","gloria",
    "graziella","grazia","ida","immacolata","ines","isabella","ivana",
    "jessica","jolanda","lara","leda","letizia","lidia","liliana","linda",
    "lisa","livia","luisa","luisella","maddalena","mafalda","manuela",
    "margherita","marina","maristella","matilde","michela","milena","mirella",
    "morena","natalia","nicoletta","noemi","nunzia","ofelia","olimpia",
    "palma","pamela","pina","priscilla","rachele","raffaella","ramona",
    "rebecca","regina","romina","rosanna","rosaria","rosella","sonia",
    "stella","tania","tina","titina","tosca","valentina","vanessa","virginia",
}


def rileva_sesso(label: str) -> str:
    """
    Determina il sesso dal primo token del label (nome).
    Ritorna 'M' o 'F'. Default 'M' se non determinabile.

    Logica:
      1. Controlla dizionario nomi italiani noti
      2. Euristica suffisso: -a → F (Giulia, Marta…), -o/-e/-i → M
      3. Default M
    """
    nome = label.strip().split()[0].lower() if label.strip() else ""
    nome_clean = re.sub(r"[^a-zàèéìòùäëïöü]", "", nome)

    if nome_clean in _NOMI_F:
        return "F"
    if nome_clean in _NOMI_M:
        return "M"

    # Euristica suffisso
    if nome_clean.endswith("a"):
        return "F"
    if nome_clean.endswith(("o", "e", "i")):
        return "M"

    return "M"


# ── Dati Ma Yi tradotti per elemento ─────────────────────────────────────────

_CORPO_EN = {
    "Metallo": "slender upright figure, medium height, large-boned with lean limbs",
    "Legno":   "slim tall figure, long slender fingers, delicate build",
    "Terra":   "stocky compact figure, short neck, heavyset",
    "Fuoco":   "narrow shoulders, wider hips, small hands and feet",
    "Acqua":   "round full figure, prominent belly, narrow shoulders",
}
_VOLTO_EN = {
    "Metallo": "square jaw, high arched eyebrows, deep-set eyes, straight prominent nose",
    "Legno":   "long oval face, prominent forehead, thick lips",
    "Terra":   "large round face, wide mouth, broad flat nose",
    "Fuoco":   "diamond-shaped face, bushy eyebrows, flared nostrils",
    "Acqua":   "round soft face, large eyes, thick arched eyebrows",
}
_CARNAGIONE_EN = {
    "Metallo": "fair pale skin",
    "Legno":   "pale slightly greenish skin tone",
    "Terra":   "warm olive yellow skin",
    "Fuoco":   "bronzed reddish skin",
    "Acqua":   "dark olive skin",
}
_MOVIMENTI_EN = {
    "Metallo": "confident posture, controlled precise movements",
    "Legno":   "reserved quiet stance, deliberate gestures",
    "Terra":   "heavy stable posture, slow movements",
    "Fuoco":   "dynamic energetic stance, restless body language",
    "Acqua":   "slow fluid movements, slightly closed introverted posture",
}
_ZONA_EN = {
    "Orecchie": "well-defined ears",
    "Fronte":   "prominent forehead",
    "Occhi":    "striking expressive eyes",
    "Naso":     "strong prominent nose",
    "Bocca":    "defined full lips and chin",
    "Mascella": "strong defined jawline",
}

DIDASCALIE = {
    "frontale": "Ritratto frontale",
    "laterale": "Profilo laterale",
    "corpo":    "Figura intera",
}

_STILE = (
    "Photorealistic portrait photography, studio lighting, "
    "neutral background, sharp focus, 8k resolution, "
    "cinematic, no text, no watermark"
)


def _eta_desc(eta: int) -> str:
    if eta <= 20:   return "young adult around 20 years old"
    elif eta <= 35: return "adult around 30 years old"
    elif eta <= 55: return "middle-aged around 45 years old"
    else:           return "elderly around 65 years old"


def genera_seed_volto(risultato: dict, sesso: str = "M") -> str:
    """
    Restituisce una stringa sintetica che descrive il volto specifico
    del soggetto. Viene iniettata nei prompt di laterale e corpo
    per aumentare la coerenza tra le tre immagini.
    """
    elemento   = risultato.get("elemento", "Terra")
    eta        = risultato.get("eta", 45)
    genere     = "man" if sesso == "M" else "woman"
    volto      = _VOLTO_EN.get(elemento, "")
    carnagione = _CARNAGIONE_EN.get(elemento, "")
    eta_en     = _eta_desc(eta)
    return (
        f"same {genere} as in the frontal portrait: "
        f"{eta_en}, {volto}, {carnagione}"
    )


def genera_prompt_visuale(risultato: dict, tipo: str = "frontale",
                          sesso: str = "M",
                          seed_volto: str = "") -> str:
    if "errore" in risultato:
        return f"{_STILE}. Portrait of a person."

    elemento   = risultato.get("elemento", "Terra")
    eta        = risultato.get("eta", 45)
    zona_ita   = risultato.get("zona_eta", "")

    genere     = "man" if sesso == "M" else "woman"
    corpo      = _CORPO_EN.get(elemento, "")
    volto      = _VOLTO_EN.get(elemento, "")
    carnagione = _CARNAGIONE_EN.get(elemento, "")
    movimenti  = _MOVIMENTI_EN.get(elemento, "")
    zona_en    = _ZONA_EN.get(zona_ita, "")
    eta_en     = _eta_desc(eta)

    if tipo == "frontale":
        return (
            f"{_STILE}. "
            f"Frontal face portrait of a {genere}, {eta_en}. "
            f"Facial features: {volto}. "
            f"{carnagione}. "
            f"Focal point: {zona_en}."
        )
    elif tipo == "laterale":
        seed = f" {seed_volto}." if seed_volto else ""
        return (
            f"{_STILE}. "
            f"Side profile portrait, head and shoulders, {eta_en}.{seed} "
            f"Facial features in profile: {volto}. "
            f"{carnagione}."
        )
    else:  # corpo
        seed = f" {seed_volto}." if seed_volto else ""
        return (
            f"{_STILE}. "
            f"Full body portrait, {eta_en}.{seed} "
            f"Body build: {corpo}. "
            f"Posture: {movimenti}."
        )


def genera_didascalia(risultato: dict, tipo: str, sesso: str = "M") -> str:
    elemento = risultato.get("elemento", "")
    eta      = risultato.get("eta", "")
    zona     = risultato.get("zona_eta", "")
    genere   = "♂" if sesso == "M" else "♀"
    base     = DIDASCALIE.get(tipo, tipo.capitalize())

    if tipo == "frontale":
        return f"{base} {genere} · {elemento}, {eta} anni · Zona: {zona}"
    elif tipo == "laterale":
        return f"{base} {genere} · Elemento {elemento}"
    else:
        return f"{base} {genere} · Corporatura {elemento}, {eta} anni"


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
