"""
mayi_engine.py
─────────────────────────────────────────────────────────────────────────────
Motore di analisi fisiognomica Ma Yi (麻衣神相).
Integra spaCy (it_core_news_md) per il confronto semantico.
Se il modello md/lg non è disponibile, fallback automatico a keyword matching.

Bug corretti rispetto al Colab originale:
  1. eta hardcoded a 30 nell'invocazione principale → parametro esplicito
  2. split multi-scheda fragile (regex su '={20,}' vs '\n\n\n+') → parser
     unificato e robusto con delimitatore esplicito '---' o righe vuote doppie
  3. nessuna gestione del caso in cui più elementi abbiano punteggio uguale
     → tie-breaking deterministico con ordine canonico
  4. _analizza_testo_stringa non restituisce le fasce d'età complete → usa
     eta_focus() da ma_yi_data per l'intera tabella, non solo la fascia corrente
  5. header_patterns filtrati solo su startswith → ora filtro su presenza
     ovunque nel blocco, più robusto
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.ma_yi_data import MA_YI_DATA, LESSICO_COMPLETO, ETA_FOCUS, zona_eta

# ── CARICAMENTO SPACY (lazy, opzionale) ───────────────────────────────────────

_nlp = None
_SPACY_OK = False
_SPACY_MODEL_NAME = "—"


def _load_spacy() -> bool:
    """
    Carica it_core_news_md (o lg come fallback).
    RICHIEDE md o lg: 'sm' non ha word vectors statici → similarity() = 0.
    Verifica esplicitamente has_vector prima di accettare il modello.
    """
    global _nlp, _SPACY_OK, _SPACY_MODEL_NAME
    if _SPACY_OK:
        return True
    try:
        import spacy
        for model_name in ("it_core_news_md", "it_core_news_lg"):
            try:
                candidate = spacy.load(model_name)
                probe = candidate("paziente")
                if probe[0].has_vector:
                    _nlp = candidate
                    _SPACY_OK = True
                    _SPACY_MODEL_NAME = model_name
                    return True
            except OSError:
                continue
        return False
    except Exception:
        return False


def spacy_model_name() -> str:
    """Ritorna il nome del modello caricato (o '—' se non disponibile)."""
    return _SPACY_MODEL_NAME


# ── MATCHING SEMANTICO ────────────────────────────────────────────────────────

_SOGLIA_SIM = 0.62   # soglia similarità coseno per spaCy


def _punteggi_spacy(testo: str) -> dict[str, float]:
    """Confronto semantico testo ↔ lessico Ma Yi via word vectors."""
    doc = _nlp(testo.lower())
    tokens = [t for t in doc if not t.is_stop and not t.is_punct and t.has_vector]
    punteggi: dict[str, float] = {e: 0.0 for e in LESSICO_COMPLETO}
    for elem, lessico in LESSICO_COMPLETO.items():
        for parola in lessico:
            doc_p = _nlp(parola)
            if not doc_p or not doc_p[0].has_vector:
                continue
            for tok in tokens:
                sim = tok.similarity(doc_p[0])
                if sim > _SOGLIA_SIM:
                    punteggi[elem] += sim
    return punteggi


def _punteggi_keyword(testo: str) -> dict[str, float]:
    """Keyword matching esatto sul lessico completo (keywords + sinonimi)."""
    t = testo.lower()
    punteggi: dict[str, float] = {e: 0.0 for e in LESSICO_COMPLETO}
    for elem, lessico in LESSICO_COMPLETO.items():
        for parola in lessico:
            if parola in t:
                punteggi[elem] += 1.0
    return punteggi


# Ordine canonico per tie-breaking deterministico
_ORDINE = list(MA_YI_DATA.keys())   # ["Metallo", "Legno", "Terra", "Fuoco", "Acqua"]


def _elemento_dominante(punteggi: dict[str, float]) -> str:
    """
    Ritorna l'elemento con punteggio più alto.
    Tie-breaking: ordine canonico (Metallo > Legno > Terra > Fuoco > Acqua).
    """
    max_val = max(punteggi.values())
    # Tra i pari merito prende il primo nell'ordine canonico
    for elem in _ORDINE:
        if punteggi[elem] == max_val:
            return elem
    return _ORDINE[0]


# ── ANALISI SINGOLA DESCRIZIONE ───────────────────────────────────────────────

def analizza_descrizione(
    testo: str,
    eta: int = 45,
    use_spacy: bool = True,
) -> dict:
    """
    Analizza una descrizione testuale e restituisce il profilo Ma Yi completo.

    Returns
    -------
    dict con: elemento, punteggi, metodo, corpo, volto, voce, movimenti,
              complexion, zona_eta, nota_eta, eta_focus_completo, top3
    """
    if not testo.strip():
        return {"errore": "Testo vuoto."}

    spacy_ok = use_spacy and _load_spacy()
    if spacy_ok:
        punteggi = _punteggi_spacy(testo)
        metodo = f"spaCy ({_SPACY_MODEL_NAME})"
    else:
        punteggi = _punteggi_keyword(testo)
        metodo = "keyword"

    # Normalizza a float con 3 decimali
    punteggi = {e: round(v, 3) for e, v in punteggi.items()}
    punteggi_ord = dict(sorted(punteggi.items(), key=lambda x: x[1], reverse=True))

    max_val = max(punteggi.values())
    if max_val == 0:
        elemento = _ORDINE[0]   # fallback: Metallo
        metodo += " [nessun match → fallback]"
    else:
        elemento = _elemento_dominante(punteggi)

    info = MA_YI_DATA[elemento]
    zona, nota = zona_eta(eta)

    # Tabella completa fasce d'età
    eta_focus_completo = [
        {
            "range": f"{mn}–{mx if mx < 999 else '+'}",
            "zona": z,
            "nota": n,
            "attuale": mn <= eta <= mx,
        }
        for mn, mx, z, n in ETA_FOCUS
    ]

    # Top-3 elementi con punteggio > 0
    top3 = [(e, v) for e, v in list(punteggi_ord.items())[:3] if v > 0]

    return {
        "elemento": elemento,
        "emoji": info["emoji"],
        "colore": info["colore_elemento"],
        "punteggi": punteggi_ord,
        "top3": top3,
        "metodo": metodo,
        "eta": eta,
        "corpo": info["corpo"],
        "volto": info["volto"],
        "voce": info["voce"],
        "movimenti": info["movimenti"],
        "complexion": info["complexion"],
        "zona_eta": zona,
        "nota_eta": nota,
        "eta_focus_completo": eta_focus_completo,
    }


# ── PARSER FILE MULTI-SCHEDA ──────────────────────────────────────────────────

# Pattern di intestazione da ignorare (blocchi non-personaggio)
_HEADER_PATTERNS = re.compile(
    r"(analisi\s+ma\s+yi|generato\s+da|soggetti|spine-nummy|={10,})",
    re.IGNORECASE,
)


def _blocchi_validi(testo: str) -> list[tuple[str, str]]:
    """
    Divide il testo in blocchi per personaggio.

    Formato supportato (in ordine di priorità):
      1. Blocchi separati da '===============================' (20+ =)
      2. Blocchi con intestazione 'PERSONAGGIO N:' o 'SOGGETTO N:'
      3. Blocchi separati da almeno due righe vuote consecutive

    Ritorna lista di tuple (label, testo_descrizione).
    """
    # ── Tentativo 1: delimitatore esplicito ═══ ───────────────────────────
    if re.search(r"={20,}", testo):
        parti = re.split(r"={20,}", testo)
        blocchi = []
        for i, parte in enumerate(parti, 1):
            pulito = parte.strip()
            if pulito and not _HEADER_PATTERNS.search(pulito[:80]):
                # Estrae eventuale nome dalla prima riga
                righe = pulito.splitlines()
                label = righe[0].strip() if righe else f"Personaggio {i}"
                corpo = "\n".join(righe[1:]).strip() if len(righe) > 1 else pulito
                blocchi.append((label or f"Personaggio {i}", corpo or pulito))
        if blocchi:
            return blocchi

    # ── Tentativo 2: intestazioni esplicite ──────────────────────────────
    match_intestazioni = re.split(
        r"(?im)^(?:personaggio|soggetto|scheda)\s*\d+\s*[:\-–]?\s*", testo
    )
    if len(match_intestazioni) > 1:
        blocchi = []
        for i, parte in enumerate(match_intestazioni[1:], 1):
            pulito = parte.strip()
            if pulito:
                righe = pulito.splitlines()
                label = righe[0].strip() or f"Personaggio {i}"
                corpo = "\n".join(righe[1:]).strip() if len(righe) > 1 else pulito
                blocchi.append((label, corpo or pulito))
        if blocchi:
            return blocchi

    # ── Tentativo 3: doppia riga vuota (formato libero) ──────────────────
    parti = re.split(r"\n[ \t]*\n[ \t]*\n+", testo)
    blocchi = []
    for i, parte in enumerate(parti, 1):
        pulito = parte.strip()
        if pulito and not _HEADER_PATTERNS.search(pulito[:80]):
            righe = pulito.splitlines()
            label = righe[0].strip() or f"Personaggio {i}"
            corpo = "\n".join(righe[1:]).strip() if len(righe) > 1 else pulito
            blocchi.append((label, corpo or pulito))
    return blocchi


def parse_file_multi(
    testo: str,
    eta_default: int = 45,
    eta_map: Optional[dict[str, int]] = None,
) -> tuple[list[tuple[str, str, int]], list[str]]:
    """
    Parsa un file multi-scheda.

    Formato eta per scheda: riga con 'ETA: 38' o 'ETÀ: 38' all'interno
    del blocco (case-insensitive). Se assente usa eta_default.

    Returns
    -------
    schede : list of (label, testo_pulito, eta)
    errori : list of str
    """
    blocchi = _blocchi_validi(testo)
    if not blocchi:
        return [], ["Nessun blocco valido trovato nel file."]

    schede = []
    errori = []
    eta_map = eta_map or {}

    for label, corpo in blocchi:
        # Cerca ETA: / ETÀ: nel corpo
        m = re.search(r"et[aà]\s*[:=]\s*(\d{1,3})", corpo, re.IGNORECASE)
        if m:
            eta = int(m.group(1))
            # Rimuove la riga età dal testo per non inquinare il matching
            corpo = re.sub(r"et[aà]\s*[:=]\s*\d{1,3}", "", corpo, flags=re.IGNORECASE).strip()
        else:
            eta = eta_map.get(label, eta_default)

        if not corpo:
            errori.append(f"Scheda '{label}': testo vuoto dopo parsing, ignorata.")
            continue

        schede.append((label, corpo, eta))

    return schede, errori


# ── FORMATTAZIONE OUTPUT TXT ──────────────────────────────────────────────────

def profilo_to_txt(label: str, r: dict) -> str:
    """Formatta un risultato analisi come stringa .txt scaricabile."""
    if "errore" in r:
        return f"ERRORE per '{label}': {r['errore']}\n"

    # Tabella fasce età
    righe_eta = []
    for f in r["eta_focus_completo"]:
        marker = " ◀ età attuale" if f["attuale"] else ""
        righe_eta.append(f"  {f['range']:>8}  {f['zona']:<12}{marker}")

    top3_str = ", ".join(f"{e} ({v})" for e, v in r["top3"]) if r["top3"] else "—"

    return "\n".join([
        "═" * 54,
        f"  ANALISI MA YI (麻衣神相): {label.upper()}",
        "═" * 54,
        f"  Elemento dominante : {r['emoji']}  {r['elemento']}",
        f"  Età analizzata     : {r['eta']} anni",
        f"  Zona attiva        : {r['zona_eta']}",
        f"  Nota               : {r['nota_eta']}",
        "",
        "  CARATTERISTICHE FISICHE",
        f"  Corpo     : {r['corpo']}",
        f"  Volto     : {r['volto']}",
        f"  Complexion: {r['complexion']}",
        f"  Voce      : {r['voce']}",
        f"  Movimenti : {r['movimenti']}",
        "",
        "  FASCE D'ETÀ E ZONE DEL VOLTO",
        *righe_eta,
        "",
        f"  Top 3 elementi     : {top3_str}",
        f"  Metodo matching    : {r['metodo']}",
        "═" * 54,
    ]) + "\n"
