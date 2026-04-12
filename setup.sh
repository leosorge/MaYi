#!/bin/bash
# setup.sh — eseguito da Streamlit Cloud DOPO pip install -r requirements.txt.
# Scarica il modello italiano con word vectors (md ≈ 43 MB).
#
# NOTA: 'sm' non ha word vectors statici → token.similarity() restituisce 0.
# NOTA: spaCy deve essere >=3.8.0 (vedi requirements.txt) per evitare
#       l'errore "numpy.dtype size changed" con numpy 2.x.

set -e  # interrompe se un comando fallisce

echo "[setup.sh] Scaricamento modello spaCy it_core_news_md..."
python -m spacy download it_core_news_md

echo "[setup.sh] Verifica modello..."
python -c "
import spacy
nlp = spacy.load('it_core_news_md')
probe = nlp('paziente')
assert probe[0].has_vector, 'ERRORE: il modello non ha word vectors!'
print('[setup.sh] Modello OK — has_vector:', probe[0].has_vector)
"
