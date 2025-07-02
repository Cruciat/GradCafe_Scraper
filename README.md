# GradCafe Scraper

**GradCafe Scraper** è un tool da linea di comando scritto in Python per estrarre automaticamente i dati delle decisioni da [The GradCafe](https://www.thegradcafe.com/survey/). Utilizza `requests` e `BeautifulSoup` per navigare e parsare le pagine di risultati, e salva i dati raccolti in un file CSV strutturato.

---

## Caratteristiche principali

* **Ricerca parametrica**: filtra per istituzione, programma e tipo di degree.
* **Navigazione automatica**: attraversa tutte le pagine dei risultati e gestisce dinamicamente la paginazione.
* **Estrazione dettagliata**: estrae scuola, programma, livello di studio, data di inserimento, decisione, GPA e punteggi GRE (V, Q, AW), più eventuali commenti.
* **Barra di stato interattiva**: mostra una barra di progresso colorata con percentuale, pagina corrente e numero di voci raccolte.
* **Output CSV**: salva i dati in un file CSV nominato automaticamente in base ai parametri e alla data di esecuzione.

---

## Prerequisiti

* Python 3.7 o superiore
* Connessione Internet

Il programma richiede le seguenti librerie Python (installabili tramite `requirements.txt`):

```text
requests>=2.0
beautifulsoup4>=4.0
pyfiglet>=0.8
colorama>=0.4
```

---

## Installazione

1. Clona questo repository:

   ```bash
   git clone https://github.com/tuo-utente/gradcafe-scraper.git
   cd gradcafe-scraper
   ```

2. Crea e attiva un ambiente virtuale (opzionale, ma consigliato):

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. Installa le dipendenze:

   ```bash
   pip install -r requirements.txt
   ```

---

## Utilizzo

Avvia lo script da terminale:

```bash
python gradcafe_scraper.py
```

Segui le istruzioni interattive:

1. Inserisci il nome dell'istituzione (puoi lasciare vuoto per nessun filtro).
2. Inserisci il programma di studio (puoi lasciare vuoto).
3. Seleziona il tipo di degree dal menu.

Il tool mostrerà un riepilogo dei parametri e inizierà il download delle pagine; vedrai una barra di avanzamento. Al termine, troverai il CSV generato in:

```
CSVs/GradCafe/<istituzione>_<programma>_<degree>_<GGMMYYYY>.csv
```

---

## Struttura del CSV

Il file CSV conterrà le seguenti colonne:

| Colonna  | Descrizione                                |
| -------- | ------------------------------------------ |
| School   | Nome dell'istituzione                      |
| Program  | Programma                                  |
| Level    | Livello di studio (es. PhD, Masters, etc.) |
| Added on | Data di inserimento nel database           |
| Decision | Esito della decisione (First word only)    |
| GPA      | GPA segnalato                              |
| GRE V    | Punteggio GRE Verbale                      |
| GRE Q    | Punteggio GRE Quantitativo                 |
| GRE AW   | Punteggio GRE Analytical Writing           |
| Comment  | Eventuale commento aggiuntivo              |

### Esempio di riga CSV

```
MIT,Computer Science,PhD,March 15,2024,Accepted,3.9,160,170,5.0,"Excited to join!"
```

---

## Personalizzazione

* Puoi modificare l'intervallo di sleep (attualmente 0.5 s) per bilanciare velocità e carico sul server.
* Il user agent è configurato nella variabile `headers`; puoi cambiarlo se necessario.

---

## Contributi

I contributi sono i benvenuti! Apri una pull request o segnala un issue per bug o nuove funzionalità.

---

## Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per i dettagli.

---

*Ultimo aggiornamento: 2 luglio 2025*
