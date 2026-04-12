"""
ma_yi_data.py
─────────────────────────────────────────────────────────────────────────────
Database centralizzato per l'analisi fisiognomica Ma Yi (麻衣神相).
Fonti: Table 1 e Sezioni 3.2, 3.4 del testo di riferimento.

Struttura per elemento:
  - keywords    : termini esatti per keyword matching (fallback)
  - sinonimi    : termini semanticamente affini (usati da spaCy md)
  - corpo       : descrizione antropometrica del corpo
  - volto       : descrizione del volto e forma cranica
  - voce        : caratteristiche della voce
  - movimenti   : postura e movimenti tipici
  - complexion  : colorazione della pelle
  - eta_focus   : zona del volto osservata per fascia d'età
─────────────────────────────────────────────────────────────────────────────
"""

# ── DATABASE ELEMENTI ─────────────────────────────────────────────────────────

MA_YI_DATA: dict[str, dict] = {
    "Metallo": {
        "keywords": [
            "determinazione", "decisionista", "razionalità", "successo",
            "leadership", "volontà", "disciplina", "rigore", "precisione",
            "controllo", "autorità", "ambizione", "fermezza", "struttura",
        ],
        "sinonimi": [
            "risoluto", "deciso", "comandare", "dirigere", "organizzare",
            "metodico", "esigente", "severo", "efficiente", "concreto",
            "pragmatico", "strategico", "competitivo", "determinato",
        ],
        "corpo": (
            "Sottile e dritto, altezza media, ossatura grande con arti snelli [2]."
        ),
        "volto": (
            "Quadrato (TIAN) o TONG (prominente). "
            "Sopracciglia alte, occhi incavati e naso dritto [2, 4]."
        ),
        "voce": "Suono squillante o tintinnante (Ringing sound) [2].",
        "movimenti": "Agilità fisica e camminata sicura [2, 5].",
        "complexion": "Bianca [2].",
        "colore_elemento": "#b0b8c1",
        "emoji": "⚔️",
    },
    "Legno": {
        "keywords": [
            "creatività", "solitudine", "isolamento", "taciturno", "tenacia",
            "estro", "intuizione", "crescita", "adattamento", "flessibilità",
            "pazienza", "resilienza", "originalità", "visione",
        ],
        "sinonimi": [
            "creativo", "solitario", "riservato", "silenzioso", "perseverante",
            "inventivo", "artistico", "immaginativo", "contemplativo", "austero",
            "introverso", "profondo", "riflessivo", "schivo",
        ],
        "corpo": (
            "Figura snella con dita lunghe e sottili; molti segni palmari [2]."
        ),
        "volto": (
            "Lungo (MU) o JIA (fronte larga). "
            "Fronte prominente e labbra spesse [2, 4]."
        ),
        "voce": "Silenziosa o parsimoniosa [2].",
        "movimenti": "Vigoroso ma riservato; movimenti taciturni [2, 5].",
        "complexion": "Verdastra o pallida [2].",
        "colore_elemento": "#6b8f5e",
        "emoji": "🌿",
    },
    "Terra": {
        "keywords": [
            "stabilità", "calcolo", "ostinazione", "sicurezza", "concretezza",
            "praticità", "solidità", "affidabilità", "tradizione", "famiglia",
            "economia", "prudenza", "pazienza", "radicamento",
        ],
        "sinonimi": [
            "stabile", "radicato", "solido", "costante", "materiale",
            "laborioso", "conservatore", "metodico", "fermo", "equilibrato",
            "ponderato", "calmo", "tenace", "lento",
        ],
        "corpo": (
            "Tarchiato, piuttosto grasso, collo e dita corte [3]."
        ),
        "volto": (
            "Grande, rotondo (YUAN) o quadrato. "
            "Bocca larga e naso grande [3, 4]."
        ),
        "voce": "Risonante [3].",
        "movimenti": "Stabile e pesante; postura solida nel mangiare e dormire [3, 5].",
        "complexion": "Gialla [3].",
        "colore_elemento": "#c8a96e",
        "emoji": "🏔️",
    },
    "Fuoco": {
        "keywords": [
            "coraggio", "passione", "rischio", "rapidità", "impulsività",
            "entusiasmo", "energia", "carisma", "innovazione", "audacia",
            "spontaneità", "intensità", "dinamismo", "ardore",
        ],
        "sinonimi": [
            "coraggioso", "appassionato", "impulsivo", "rapido", "ardito",
            "esuberante", "vivace", "esplosivo", "estroverso", "temerario",
            "frenetico", "emotivo", "focoso", "irruente",
        ],
        "corpo": (
            "Piccolo sopra la vita e largo sotto; "
            "mani e piedi piccoli e ossuti [3]."
        ),
        "volto": (
            "A rombo (SHEN). "
            "Sopracciglia cespugliose e narici esposte [3, 4]."
        ),
        "voce": "Parlata veloce [3].",
        "movimenti": "Impulsivi e rapidi [3, 5].",
        "complexion": "Bronzeo o rossastra [3].",
        "colore_elemento": "#c0533a",
        "emoji": "🔥",
    },
    "Acqua": {
        "keywords": [
            "riflessione", "pazienza", "lentezza", "profondità", "intuizione",
            "adattabilità", "fluidità", "mistero", "empatia", "sensibilità",
            "introversione", "memoria", "saggezza", "ascolto",
        ],
        "sinonimi": [
            "riflessivo", "paziente", "lento", "profondo", "intuitivo",
            "adattabile", "empatico", "sensibile", "introverso", "saggio",
            "meditativo", "tranquillo", "calmo", "riservato",
        ],
        "corpo": (
            "Grasso e rotondo, pancia prominente, "
            "spalle strette e natiche piatte [2]."
        ),
        "volto": (
            "Rotondo (YUAN). "
            "Occhi grandi e sopracciglia folte [3, 4]."
        ),
        "voce": "Lenta e profonda [3].",
        "movimenti": "Indole 'chiusa' o lenta (Costive) [3, 5].",
        "complexion": "Nerastra [3].",
        "colore_elemento": "#3a6b8f",
        "emoji": "💧",
    },
}

# ── LESSICO COMPLETO (keyword + sinonimi, usato dallo spaCy matcher) ──────────

LESSICO_COMPLETO: dict[str, list[str]] = {
    elem: dati["keywords"] + dati["sinonimi"]
    for elem, dati in MA_YI_DATA.items()
}

# ── FASCE D'ETÀ E ZONE DEL VOLTO ─────────────────────────────────────────────
# Fonte: testo Ma Yi, sezione sulle variazioni negli anni

ETA_FOCUS: list[tuple[int, int, str, str]] = [
    (0,   14,  "Orecchie",  "Struttura e forma delle orecchie rivelano la costituzione ereditata."),
    (15,  30,  "Fronte",    "La fronte indica il potenziale e le prospettive giovanili."),
    (31,  40,  "Occhi",     "Gli occhi rispecchiano la vitalità e le relazioni nel periodo maturo."),
    (41,  50,  "Naso",      "Il naso (Stato attuale) è la zona chiave tra i 40 e i 50 anni."),
    (51,  60,  "Bocca",     "La bocca e il mento rivelano la situazione nella seconda maturità."),
    (61,  999, "Mascella",  "La mascella e il mento indicano la forza vitale nella senescenza."),
]

def zona_eta(eta: int) -> tuple[str, str]:
    """Restituisce la zona del volto e la nota interpretativa per l'età data."""
    for eta_min, eta_max, zona, nota in ETA_FOCUS:
        if eta_min <= eta <= eta_max:
            return zona, nota
    return "Mascella", "Zona della senescenza."
