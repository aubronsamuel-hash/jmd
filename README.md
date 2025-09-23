# jmd

## Documentation agents
- [AGENT hub](AGENT.md)
- [Sous-agents](docs/agents/README.md)

## Scripts guards
- `tools/guards/run_all_guards.ps1`
- `tools/guards/roadmap_guard.ps1`
- `tools/guards/docs_guard.ps1`

## Roadmap
- Etape courante: [docs/roadmap/step-06.md](docs/roadmap/step-06.md)
- Sommaire: [docs/roadmap/README.md](docs/roadmap/README.md)

## Backend FastAPI
Le backend est un service FastAPI expose sous `backend.main:app` avec un point d'entree `/api/v1`.

### Installation des dependances
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .[dev]
```

### Lancement de l'API en developpement
```bash
uvicorn backend.main:app --reload
```

### Tests et couverture
```bash
pytest
```
Un rapport `coverage.xml` est genere automatiquement et le seuil minimal de couverture est de 70 %.
