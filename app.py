"""
app.py — Streamlit app principale
Analisi fisiognomica Ma Yi (麻衣神相)
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import io
import zipfile
import sys
import os

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from utils.mayi_engine import (
    analizza_descrizione,
    parse_file_multi,
    profilo_to_txt,
    spacy_model_name,
    _load_spacy,
)
from data.ma_yi_data import MA_YI_DATA, ETA_FOCUS

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Ma Yi — Analisi Fisiognomica",
    page_icon="☯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;600&family=Noto+Sans:ital,wght@0,300;0,400;1,300&display=swap');

:root {
    --ink:       #14100d;
    --paper:     #f7f2ea;
    --red:       #8b1a1a;
    --red-lt:    #c0392b;
    --gold:      #b8960c;
    --gold-lt:   #d4a017;
    --brush:     #2c1810;
    --mist:      rgba(20,16,13,.06);
    --border:    rgba(139,26,26,.22);
}

html, body, [data-testid="stApp"] {
    background: var(--paper);
    color: var(--brush);
    font-family: 'Noto Sans', serif;
}

/* Texture sfondo pergamena */
[data-testid="stApp"]::before {
    content: "";
    position: fixed; inset: 0;
    background-image:
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 28px,
            rgba(139,26,26,.04) 28px,
            rgba(139,26,26,.04) 29px
        );
    pointer-events: none;
    z-index: 0;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 2.8rem 1rem 1.4rem;
    border-bottom: 2px solid var(--border);
    margin-bottom: 2rem;
    position: relative;
}
.hero-hanzi {
    font-family: 'Noto Serif SC', serif;
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    color: var(--red);
    letter-spacing: .3em;
    line-height: 1;
    text-shadow: 2px 2px 0 rgba(139,26,26,.15);
}
.hero-subtitle {
    font-size: .82rem;
    letter-spacing: .25em;
    text-transform: uppercase;
    color: rgba(44,24,16,.45);
    margin-top: .5rem;
}

/* ── Tabs ── */
[data-testid="stTabs"] button {
    font-family: 'Noto Serif SC', serif !important;
    font-size: .85rem !important;
    letter-spacing: .08em !important;
    color: rgba(44,24,16,.5) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--red) !important;
    border-bottom: 2px solid var(--red) !important;
}

/* ── Form ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,.7) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    font-family: 'Noto Sans', sans-serif !important;
    color: var(--brush) !important;
}
[data-testid="stTextArea"] textarea { font-size: .9rem !important; }

/* ── Pulsante primario ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: var(--red) !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'Noto Serif SC', serif !important;
    letter-spacing: .12em !important;
    color: var(--paper) !important;
    padding: .6rem 2rem !important;
    transition: background .2s !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    background: var(--red-lt) !important;
}

/* ── Card risultato ── */
.card {
    background: rgba(255,255,255,.65);
    border: 1px solid var(--border);
    border-left: 4px solid var(--red);
    border-radius: 4px;
    padding: 1.8rem 2rem;
    margin-top: 1.4rem;
    backdrop-filter: blur(4px);
    position: relative;
}
.card-elemento {
    font-family: 'Noto Serif SC', serif;
    font-size: 1.6rem;
    color: var(--red);
    letter-spacing: .1em;
    margin: 0 0 .25rem;
}
.card-emoji { font-size: 2.4rem; line-height: 1; }

.field-label {
    font-size: .68rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: rgba(44,24,16,.4);
    margin: .9rem 0 .2rem;
}
.field-value {
    font-size: .9rem;
    line-height: 1.55;
    color: var(--brush);
}

/* ── Barre match ── */
.bar-wrap {
    background: rgba(44,24,16,.09);
    border-radius: 2px;
    height: 5px;
    margin-bottom: .45rem;
}
.bar-fill {
    border-radius: 2px;
    height: 5px;
    background: linear-gradient(90deg, var(--red), var(--gold));
}

/* ── Tabella fasce età ── */
.eta-table { width: 100%; border-collapse: collapse; font-size: .82rem; }
.eta-table th {
    text-align: left;
    font-weight: 400;
    letter-spacing: .1em;
    font-size: .68rem;
    text-transform: uppercase;
    color: rgba(44,24,16,.4);
    padding: .3rem .5rem;
    border-bottom: 1px solid var(--border);
}
.eta-table td { padding: .35rem .5rem; border-bottom: 1px solid rgba(139,26,26,.07); }
.eta-active { background: rgba(139,26,26,.08); font-weight: 600; color: var(--red); }

/* ── Badge metodo ── */
.metodo-tag {
    display: inline-block;
    font-size: .68rem;
    letter-spacing: .1em;
    text-transform: uppercase;
    background: rgba(139,26,26,.07);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: .18rem .7rem;
    color: rgba(44,24,16,.5);
    margin-top: .6rem;
}

/* ── Download ── */
[data-testid="stDownloadButton"] button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    color: var(--red) !important;
    font-family: 'Noto Serif SC', serif !important;
    font-size: .78rem !important;
    letter-spacing: .08em !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: rgba(139,26,26,.06) !important;
}

/* ── Info box formato ── */
.formato-box {
    background: rgba(184,150,12,.07);
    border: 1px solid rgba(184,150,12,.25);
    border-radius: 4px;
    padding: .9rem 1.1rem;
    font-size: .84rem;
    line-height: 1.7;
    color: rgba(44,24,16,.7);
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="hero-hanzi">麻衣神相</div>
    <div class="hero-subtitle">Ma Yi · Analisi Fisiognomica &nbsp;·&nbsp; Sistema dei Cinque Elementi</div>
</div>
""", unsafe_allow_html=True)

# ── STATUS SPACY ──────────────────────────────────────────────────────────────

@st.cache_resource
def _init_spacy():
    """Carica spaCy una sola volta e mette in cache."""
    ok = _load_spacy()
    return ok, spacy_model_name()

spacy_loaded, spacy_name = _init_spacy()

with st.sidebar:
    st.markdown("### ⚙️ Configurazione")
    use_spacy = st.toggle(
        "Usa spaCy (similarità semantica)",
        value=spacy_loaded,
        disabled=not spacy_loaded,
        help="Richiede it_core_news_md installato. Se non disponibile usa keyword matching.",
    )
    if spacy_loaded:
        st.success(f"Modello: `{spacy_name}`")
    else:
        st.warning("spaCy md/lg non trovato → keyword matching attivo")

    st.markdown("---")
    st.markdown("**Soglia similarità spaCy:** `0.62`")
    st.markdown("**Tie-breaking:** ordine canonico")
    st.markdown("**Elementi:** Metallo · Legno · Terra · Fuoco · Acqua")


# ── HELPER: render card risultato ─────────────────────────────────────────────

def _bar(pct: int, colore: str) -> str:
    return (
        f'<div class="bar-wrap">'
        f'<div class="bar-fill" style="width:{pct}%;background:{colore}"></div>'
        f'</div>'
    )


def render_card(label: str, r: dict, key_suffix: str = ""):
    """Mostra la card di un risultato Ma Yi."""
    if "errore" in r:
        st.error(f"**{label}** — {r['errore']}")
        return

    st.markdown(f'<div class="card">', unsafe_allow_html=True)

    col_em, col_info = st.columns([1, 4])
    with col_em:
        st.markdown(f'<div class="card-emoji">{r["emoji"]}</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown(
            f'<div class="card-elemento">{r["elemento"]}</div>'
            f'<div style="font-size:.85rem;color:rgba(44,24,16,.5)">'
            f'{label} &nbsp;·&nbsp; {r["eta"]} anni'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Caratteristiche fisiche
    col_a, col_b = st.columns(2)
    with col_a:
        for campo, titolo in [("corpo", "Corpo"), ("volto", "Volto"), ("complexion", "Carnagione")]:
            st.markdown(
                f'<div class="field-label">{titolo}</div>'
                f'<div class="field-value">{r[campo]}</div>',
                unsafe_allow_html=True,
            )
    with col_b:
        for campo, titolo in [("voce", "Voce"), ("movimenti", "Postura e movimenti")]:
            st.markdown(
                f'<div class="field-label">{titolo}</div>'
                f'<div class="field-value">{r[campo]}</div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div class="field-label">Zona attiva (età {r["eta"]})</div>'
            f'<div class="field-value" style="color:var(--red);font-weight:600">'
            f'{r["zona_eta"]}</div>'
            f'<div style="font-size:.8rem;color:rgba(44,24,16,.5);margin-top:.15rem">'
            f'{r["nota_eta"]}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Fasce età (tabella)
    col_tab, col_match = st.columns([3, 2])

    with col_tab:
        st.markdown('<div class="field-label">Fasce d\'età e zone del volto</div>', unsafe_allow_html=True)
        righe = ""
        for f in r["eta_focus_completo"]:
            cls = "eta-active" if f["attuale"] else ""
            marker = " ◀" if f["attuale"] else ""
            righe += (
                f'<tr class="{cls}">'
                f'<td>{f["range"]}</td>'
                f'<td>{f["zona"]}{marker}</td>'
                f'<td style="color:rgba(44,24,16,.55)">{f["nota"]}</td>'
                f'</tr>'
            )
        st.markdown(
            f'<table class="eta-table"><thead><tr>'
            f'<th>Età</th><th>Zona</th><th>Interpretazione</th>'
            f'</tr></thead><tbody>{righe}</tbody></table>',
            unsafe_allow_html=True,
        )

    with col_match:
        if r["top3"]:
            st.markdown('<div class="field-label">Corrispondenza elementi</div>', unsafe_allow_html=True)
            max_val = r["top3"][0][1] if r["top3"] else 1
            for elem, val in r["punteggi"].items():
                if val == 0:
                    continue
                pct = int((val / max_val) * 100) if max_val > 0 else 0
                colore = MA_YI_DATA[elem]["colore_elemento"]
                emoji = MA_YI_DATA[elem]["emoji"]
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.3rem">'
                    f'<span style="width:90px;font-size:.8rem">{emoji} {elem}</span>'
                    f'<div style="flex:1">{_bar(pct, colore)}</div>'
                    f'<span style="font-size:.7rem;color:rgba(44,24,16,.4);width:38px;text-align:right">{val}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            f'<div class="metodo-tag">matching: {r["metodo"]}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Download scheda singola
    txt = profilo_to_txt(label, r)
    nome_f = label.replace(" ", "_").lower()[:40] + "-mayi.txt"
    st.download_button(
        label="⬇ Scarica profilo .txt",
        data=txt.encode("utf-8"),
        file_name=nome_f,
        mime="text/plain",
        key=f"dl_{key_suffix}",
    )


# ── TABS ──────────────────────────────────────────────────────────────────────

tab_singolo, tab_multi = st.tabs(["☯  Analisi Singola", "☯  File Multi-Scheda"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — INSERIMENTO SINGOLO
# ════════════════════════════════════════════════════════════════════════════

with tab_singolo:
    st.markdown("### Descrizione del soggetto")

    c1, c2 = st.columns([3, 1])
    with c1:
        label_input = st.text_input("Nome / etichetta", placeholder="es. Marco Aurelio")
    with c2:
        eta_input = st.number_input("Età", min_value=1, max_value=120, value=45, step=1)

    desc_input = st.text_area(
        "Descrizione del carattere e comportamento",
        placeholder=(
            'Inserisci una descrizione libera del carattere, atteggiamenti, comportamento...\n'
            'Es. "Persona con grande determinazione, leadership naturale, razionale e ambiziosa.'
            ' Movimenti precisi e camminata sicura."'
        ),
        height=160,
    )

    analizza = st.button(
        "☯  Analizza",
        type="primary",
        disabled=not (label_input.strip() and desc_input.strip()),
    )

    if analizza and label_input.strip() and desc_input.strip():
        with st.spinner("Consultando i Cinque Elementi…"):
            risultato = analizza_descrizione(
                testo=desc_input.strip(),
                eta=int(eta_input),
                use_spacy=use_spacy,
            )
        render_card(label_input.strip(), risultato, key_suffix="singolo")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — FILE MULTI-SCHEDA
# ════════════════════════════════════════════════════════════════════════════

with tab_multi:
    st.markdown("### Carica file multi-scheda")

    st.markdown("""
<div class="formato-box">
<strong>Formati supportati</strong><br>
<strong>A) Delimitatore esplicito</strong> (consigliato) — blocchi separati da <code>==============================</code>:<br>
<code>Nome Personaggio<br>ETA: 38<br>Descrizione libera del carattere…</code><br><br>
<strong>B) Doppia riga vuota</strong> — blocchi separati da due o più righe vuote (come il Colab originale):<br>
<code>Nome Personaggio</code><br><code>ETA: 38</code><br><code>Descrizione…</code><br><br>
La riga <code>ETA: N</code> è opzionale per scheda; se assente usa l'età predefinita sotto.
</div>
""", unsafe_allow_html=True)

    c_up, c_eta = st.columns([3, 1])
    with c_up:
        uploaded = st.file_uploader("Scegli file .txt", type=["txt"])
    with c_eta:
        eta_default = st.number_input(
            "Età predefinita (se non specificata per scheda)",
            min_value=1, max_value=120, value=45, step=1,
        )

    if uploaded is not None:
        raw = uploaded.read().decode("utf-8")
        schede, errori = parse_file_multi(raw, eta_default=int(eta_default))

        if errori:
            for e in errori:
                st.warning(e)

        if not schede:
            st.error("Nessuna scheda valida trovata nel file.")
        else:
            st.success(f"{len(schede)} scheda/e elaborate.")
            risultati: list[tuple[str, dict]] = []

            with st.spinner("Analisi in corso…"):
                for label, testo, eta in schede:
                    r = analizza_descrizione(testo, eta=eta, use_spacy=use_spacy)
                    risultati.append((label, r))

            for i, (label, r) in enumerate(risultati):
                with st.expander(
                    f"{MA_YI_DATA.get(r.get('elemento',''), {}).get('emoji','☯')}  "
                    f"{label}  ·  {r.get('elemento', '—')}  ·  età {r.get('eta', '—')}",
                    expanded=(i == 0),
                ):
                    render_card(label, r, key_suffix=f"multi_{i}")

            # ── Download bulk ────────────────────────────────────────────
            st.markdown("---")
            st.markdown("#### ⬇ Scarica tutti i profili")

            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for label, r in risultati:
                    nome_f = label.replace(" ", "_").lower()[:40] + "-mayi.txt"
                    zf.writestr(nome_f, profilo_to_txt(label, r))
            zip_buf.seek(0)

            testo_unico = "\n\n".join(profilo_to_txt(l, r) for l, r in risultati)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="⬇ Download ZIP (un file per scheda)",
                    data=zip_buf,
                    file_name="analisi_mayi.zip",
                    mime="application/zip",
                    key="dl_zip_multi",
                )
            with col2:
                st.download_button(
                    label="⬇ Download .txt unico",
                    data=testo_unico.encode("utf-8"),
                    file_name="tutti_mayi.txt",
                    mime="text/plain",
                    key="dl_txt_multi",
                )

# ── FOOTER ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="text-align:center;margin-top:4rem;padding-top:1.5rem;
    border-top:1px solid rgba(139,26,26,.15);
    font-size:.7rem;letter-spacing:.15em;
    color:rgba(44,24,16,.25);text-transform:uppercase">
    Ma Yi 麻衣神相 · Cinque Elementi · spaCy + Streamlit · uso creativo / narrativo
</div>
""", unsafe_allow_html=True)
