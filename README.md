# Diario

App web personale (GitHub Pages) con due parti:

- **Diario**: abitudini sì/no della giornata. I dati restano solo sul telefono (localStorage).
- **Domani**: il piano del giorno dopo, preparato da Claude in chat e pubblicato qui **cifrato**. Solo il telefono ha la chiave privata.

## Pubblicare il piano di domani (per Claude)

1. `python3 tools/publish_plan.py publish piano.json` — cifra il piano e aggiorna `plans/index.json`.
2. Commit e push di `plans/`. Non committare mai `piano.json` in chiaro.

Formato di `piano.json`:

```json
{"date":"AAAA-MM-GG","title":"Titolo","items":[{"start":"07:00","end":"07:30","text":"...","kind":"fisso"}],"notes":["..."]}
```

`kind`: `fisso` (cose fisse), `impegno`, `turno`, `libero`.

La parte pubblica della chiave è in `plans/key.json`. Se manca (o l'utente ha ricreato la chiave nell'app), si imposta con
`python3 tools/publish_plan.py set-key <n>`, dove `<n>` è il testo mostrato in Domani → Chiave del piano.
Servono `python3` e il pacchetto `cryptography`.
