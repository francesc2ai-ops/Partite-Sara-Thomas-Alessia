# Partite Sara, Thomas & Alessia

Una pagina per sapere dove giocano Sara, Thomas e Alessia ogni settimana: una scheda per settimana
con una riga per ciascuno (giorno, data, ora, campo e pulsante Google Maps). Questo weekend e il
prossimo sono aperti, gli altri si aprono toccandoli. Se qualcuno non gioca compare "Nessuna partita".

- `data/persone.json`: nomi, squadra/campionato e file delle partite di ognuno.
- `data/sara.json`, `data/thomas.json`, `data/alessia.json`: le partite.

## Spostamenti
Per una partita spostata modifica `inizio` (formato `2026-11-14T18:00`) nel file della persona,
direttamente dal sito di GitHub. Se l'orario non è ancora fissato metti `"ora_da_confermare": true`.
