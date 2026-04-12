# ☯ Ma Yi — Analisi Fisiognomica (麻衣神相)

Questa applicazione implementa un sistema di **profilazione antropometrica** basato sui testi classici della fisiognomica cinese (*Ma Yi Shen Shu*). Utilizzando l'elaborazione del linguaggio naturale (NLP), il software analizza descrizioni caratteriali per determinare l'elemento dominante del soggetto e restituirne l'identikit fisico.


## ✨ Caratteristiche
- **Motore NLP**: Utilizza `spaCy` (modello `it_core_news_md`) per il confronto semantico tra il testo inserito e il lessico Ma Yi.
- **Analisi Multi-Scheda**: Supporta il caricamento di file `.txt` contenenti più profili separati da delimitatori.
- **Fasce d'Età**: Calcola dinamicamente le zone di focus del volto in base all'età (0-14: Orecchie, 41-50: Naso, ecc.).
- **Esportazione**: Generazione di report professionali in formato `.txt` o archivi `.zip`.

## 🛠️ Architettura del Codice
- `app.py`: Interfaccia Streamlit con stile personalizzato (estetica "pergamena").
- `utils/mayi_engine.py`: Core logic per il matching semantico e il parsing dei documenti.
- `data/ma_yi_data.py`: Database centralizzato degli elementi (Metallo, Legno, Terra, Fuoco, Acqua).

## 🚀 Installazione Locale

1. Clona il repository:
   ```bash
   git clone [https://github.com/tuo-username/ma-yi-analisi.git](https://github.com/tuo-username/ma-yi-analisi.git)
   cd ma-yi-analisi
