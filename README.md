# AI Gen demo

## Setup commands

https://docs.astral.sh/uv/

```sh
uv run pre-commit install # Install the correct git hooks
uv run uvicorn src.main:app --reload # Runs fastAPI in watch mode
```

## Example text for quiz extrapolating

```sh
La Grande Barriera Corallina si trova al largo della costa nord-orientale dell'Australia, nel Mar dei Coralli. Con i suoi circa 2.300 chilometri di lunghezza, è il più grande sistema di barriere coralline del mondo ed è visibile persino dallo spazio. È composta da oltre 2.900 singole scogliere e circa 900 isole, ed ospita una biodiversità straordinaria: più di 1.500 specie di pesci, 4.000 tipi di molluschi e 240 specie di uccelli. Fu dichiarata Patrimonio dell'Umanità dall'UNESCO nel 1981. Nonostante la sua grandiosità, la barriera è seriamente minacciata. Il cambiamento climatico provoca il cosiddetto sbiancamento dei coralli: quando l'acqua si surriscalda, i coralli espellono le alghe che vivono al loro interno e da cui dipendono per nutrirsi, assumendo un colore bianco e rischiando di morire. Tra il 2016 e il 2017 si verificò uno degli episodi di sbiancamento più gravi mai registrati, che danneggiò circa il 50% della barriera. Oggi scienziati e governi lavorano a piani di protezione che includono la riduzione delle emissioni di CO₂, il controllo dell'inquinamento delle acque e la limitazione della pesca nelle aree più vulnerabili.
```

## Panoramica tecnologie

- Uso ogni strumento fornito astral:
  - Ho scelto uv come package manager
  - Ruff come linter e formatter
  - ty per dare controlli stringenti al typing di python, un po come typescript su javascript.
- Ho predisposto pre-commit per garantire integrità della codebase, in pre-commit faccio girare il formatter il type checker ed anche degli unit test fatti con pytest
- È stato usato FastAPI come mio primo esperimento di framework web con python per creare velocemete Rest API.
  - Implicitamente con la scelta di FastiAPI ho usato pydantic per definire i models e i controlli sui formati della mia Rest API.
- Ho una semplicissima autenticazzione con JWT bearer token, l'API ha un openapi e come UI web ho scelto scalar al posto di swagger per sperimentare.
- Utilizzo l'SDK di anthropic per generare i quiz
- Utilizzo docker compose per orchestrare i miei container di esempio, inniettando anche i secrets che ho nel `.env`
- Come database ho scelto un semplice postgresql, le password hanno un salting ed ho messo cloudbeaver tra i services nel docker compose per poterlo visitare in comodità.
- Per rendere più difficile il reverse engineering, ho utilizzato Cyton per convertire tutti i .py nelle cartelle Services in librerie compilate in C (code obfuscation)

> Essendo molto inesperta sull'ecosistema python mi sono spesso fatta aiutare dall'AI per prendere decisioni e generare parte della demo!
