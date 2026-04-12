"""
tests/test_mayi_engine.py
Unit test per mayi_engine.py
Eseguire con: pytest tests/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from utils.mayi_engine import (
    analizza_descrizione,
    parse_file_multi,
    profilo_to_txt,
    _punteggi_keyword,
    _elemento_dominante,
    _ORDINE,
)
from data.ma_yi_data import MA_YI_DATA, zona_eta


# ── _punteggi_keyword ─────────────────────────────────────────────────────────

def test_keyword_metallo():
    p = _punteggi_keyword("determinazione leadership razionalità successo")
    assert p["Metallo"] > 0
    assert p["Metallo"] >= max(v for k, v in p.items() if k != "Metallo")

def test_keyword_fuoco():
    p = _punteggi_keyword("coraggio passione impulsività rapidità audacia")
    assert p["Fuoco"] > 0
    assert p["Fuoco"] >= max(v for k, v in p.items() if k != "Fuoco")

def test_keyword_acqua():
    p = _punteggi_keyword("riflessione pazienza lentezza profondità")
    assert p["Acqua"] > 0

def test_keyword_testo_vuoto():
    p = _punteggi_keyword("")
    assert all(v == 0 for v in p.values())

def test_keyword_nessun_match():
    p = _punteggi_keyword("xyz qqq zzz 123")
    assert all(v == 0 for v in p.values())


# ── _elemento_dominante ───────────────────────────────────────────────────────

def test_dominante_chiaro():
    p = {e: 0.0 for e in MA_YI_DATA}
    p["Terra"] = 5.0
    assert _elemento_dominante(p) == "Terra"

def test_tie_breaking_ordine_canonico():
    # Tutti pari merito → deve vincere il primo nell'ordine canonico
    p = {e: 1.0 for e in MA_YI_DATA}
    assert _elemento_dominante(p) == _ORDINE[0]

def test_tie_breaking_secondo():
    p = {e: 0.0 for e in MA_YI_DATA}
    p["Legno"] = 3.0
    p["Fuoco"] = 3.0   # tie tra Legno e Fuoco → vince Legno (secondo in _ORDINE)
    assert _elemento_dominante(p) == "Legno"


# ── zona_eta ──────────────────────────────────────────────────────────────────

def test_zona_infanzia():
    zona, _ = zona_eta(10)
    assert zona == "Orecchie"

def test_zona_40_50():
    zona, _ = zona_eta(45)
    assert zona == "Naso"

def test_zona_senescenza():
    zona, _ = zona_eta(70)
    assert zona == "Mascella"

def test_zona_limite_esatto():
    zona, _ = zona_eta(31)
    assert zona == "Occhi"
    zona2, _ = zona_eta(40)
    assert zona2 == "Occhi"


# ── analizza_descrizione ──────────────────────────────────────────────────────

def test_analizza_chiavi_presenti():
    r = analizza_descrizione("determinazione leadership", eta=45, use_spacy=False)
    campi = ["elemento", "emoji", "colore", "punteggi", "top3", "metodo",
             "eta", "corpo", "volto", "voce", "movimenti", "complexion",
             "zona_eta", "nota_eta", "eta_focus_completo"]
    for c in campi:
        assert c in r, f"Campo mancante: {c}"

def test_analizza_metallo():
    r = analizza_descrizione(
        "determinazione leadership razionalità successo volontà disciplina",
        eta=40, use_spacy=False,
    )
    assert r["elemento"] == "Metallo"

def test_analizza_eta_focus_completo():
    r = analizza_descrizione("pazienza lentezza", eta=45, use_spacy=False)
    assert len(r["eta_focus_completo"]) == len([x for x in __import__(
        "data.ma_yi_data", fromlist=["ETA_FOCUS"]).ETA_FOCUS])
    attivi = [f for f in r["eta_focus_completo"] if f["attuale"]]
    assert len(attivi) == 1

def test_analizza_testo_vuoto():
    r = analizza_descrizione("", eta=45, use_spacy=False)
    assert "errore" in r

def test_analizza_nessun_match_fallback():
    r = analizza_descrizione("zzz qqq www", eta=30, use_spacy=False)
    # Deve comunque restituire un elemento (fallback Metallo, primo canonico)
    assert r["elemento"] in MA_YI_DATA
    assert "fallback" in r["metodo"]

def test_analizza_metodo_keyword():
    r = analizza_descrizione("stabilità", eta=50, use_spacy=False)
    assert r["metodo"] == "keyword"


# ── parse_file_multi ──────────────────────────────────────────────────────────

TXT_DELIMITATORE = """\
==============================
Marco Aurelio
ETA: 48
Persona con grande determinazione, leadership e razionalità.
==============================
Giulia Neri
ETA: 25
Creatività, solitudine, tenacia e grande estro artistico.
==============================
"""

TXT_DOPPIA_RIGA = """\
Marco Aurelio
ETA: 48
Persona con grande determinazione, leadership e razionalità.


Giulia Neri
ETA: 25
Creatività, solitudine, tenacia e grande estro artistico.
"""

def test_parse_delimitatore_due_schede():
    schede, errori = parse_file_multi(TXT_DELIMITATORE)
    assert len(schede) == 2
    assert not errori

def test_parse_doppia_riga_due_schede():
    schede, errori = parse_file_multi(TXT_DOPPIA_RIGA)
    assert len(schede) == 2

def test_parse_eta_estratta():
    schede, _ = parse_file_multi(TXT_DELIMITATORE)
    assert schede[0][2] == 48
    assert schede[1][2] == 25

def test_parse_label_estratto():
    schede, _ = parse_file_multi(TXT_DELIMITATORE)
    assert schede[0][0] == "Marco Aurelio"
    assert schede[1][0] == "Giulia Neri"

def test_parse_eta_default_se_assente():
    txt = "==============================\nPersonaggio Senza Eta\nCoraggio passione rischio.\n=============================="
    schede, _ = parse_file_multi(txt, eta_default=33)
    assert schede[0][2] == 33

def test_parse_file_vuoto():
    schede, errori = parse_file_multi("   \n  \n  ")
    assert len(schede) == 0
    assert len(errori) > 0

def test_parse_header_filtrati():
    txt = "ANALISI MA YI generato automaticamente\n\n\n\nMarco Rossi\nETA: 30\nStabilità calcolo ostinazione."
    schede, _ = parse_file_multi(txt)
    # La prima riga è un header e deve essere filtrata o inglobata
    assert any("Marco Rossi" in s[0] or "Stabilità" in s[1] for s in schede)


# ── profilo_to_txt ────────────────────────────────────────────────────────────

def test_profilo_to_txt_contiene_elemento():
    r = analizza_descrizione("determinazione leadership", eta=40, use_spacy=False)
    txt = profilo_to_txt("Test", r)
    assert "Metallo" in txt

def test_profilo_to_txt_contiene_label():
    r = analizza_descrizione("coraggio passione", eta=30, use_spacy=False)
    txt = profilo_to_txt("Mario Rossi", r)
    assert "MARIO ROSSI" in txt

def test_profilo_to_txt_errore():
    r = {"errore": "Testo vuoto."}
    txt = profilo_to_txt("Test", r)
    assert "ERRORE" in txt
