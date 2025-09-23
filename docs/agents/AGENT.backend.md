# AGENT backend

## Objectifs
- Livrer une API FastAPI fiable pour la gestion du planning des intermittents du spectacle.
- Assurer la coherence entre models SQLAlchemy, schemas Pydantic v2 et migrations Alembic.
- Garantir la robustesse, la performance et l'observabilite du backend.

## Pile technique
- Python 3.11+ (adapter selon contraintes projet).
- FastAPI, SQLAlchemy 2.x, Alembic pour migrations, Pydantic v2 pour validation.
- Pytest + plugins (pytest-asyncio, pytest-cov).
- Base de donnees cible: PostgreSQL (defaut) avec support SQLite pour tests rapides.

## Bootstrap Step 06
- Package principal `backend` (layout `src/backend`) expose `create_app()` et l'instance FastAPI `app`.
- Configuration via `backend.config.Settings` avec prefixe API par defaut `/api/v1`.
- Endpoints disponibles:
  - `GET /api/v1/health` renvoie l'etat du service.
  - `POST /api/v1/plannings` genere un planning a partir des disponibilites artistes.
- Persistence configuree via `backend.db` (engine + session) et `backend.models` (SQLAlchemy 2.x).
- Migrations Alembic disponibles (`PYTHONPATH=src alembic -c src/backend/db/alembic.ini upgrade head`).
- Nouvelles routes REST:
  - `GET /api/v1/plannings` liste les plannings persistes.
  - `GET /api/v1/plannings/{planning_id}` renvoie un planning par identifiant.
- Tests utilisent SQLite en memoire (`BACKEND_DATABASE_URL=sqlite+pysqlite:///:memory:`) avec `pytest`.
- Schemas Pydantic: `Availability`, `Artist`, `PlanningCreate`, `PlanningResponse`.
- Service de domaine `create_planning` selectionne le premier creneau disponible par artiste et leve `PlanningError` sinon.

## Evolution Step 08
- Ajout des schemas `ArtistCreate` et `ArtistUpdate` pour differencier les payloads d'ecriture.
- Services domaine exposes pour gerer le CRUD artistes (`create_artist`, `list_artists`, `get_artist`, `update_artist`, `delete_artist`).
- Contrainte d'unicite `(artist_id, start, end)` sur la table `availabilities` via migration Alembic `20240928_02`.
- Routes REST `POST/GET/GET{id}/PUT/DELETE /api/v1/artists` avec gestion des erreurs 404/409.
- Documentation des exemples JSON dans `docs/backend/api.md`.
- Tests d'integration et fixtures dediees aux artistes (`tests/backend/test_artists.py`).

## Conventions API
- Prefixer les routes par `/api/v1` (ajuster si version change).
- Utiliser schemas Pydantic pour requetes et reponses, valider les champs obligatoires.
- Documenter les endpoints via OpenAPI (docs generes par FastAPI) et ajouter exemples JSON.
- Respecter la gestion des erreurs avec reponses structurees (`{"detail": "message"}`).

## Gestion des erreurs
- Lever `HTTPException` avec codes coherents.
- Logger les erreurs critiques via l'infrastructure observabilite definie par le DevOps agent.
- Ajouter des tests couvrant les chemins d'erreur majeurs.

## Schema et migrations
- Definir les models SQLAlchemy dans `src/backend/models` (a ajuster).
- Chaque changement de schema doit etre accompagne d'une revision Alembic.
- Executer `alembic upgrade head` dans la CI avant de lancer les tests d'integration.

## Tests et couverture
- Commande reference: `pytest` (configure avec `--cov=backend --cov-report=xml`).
- Objectif coverage minimal: 70 % global, avec seuils par module si necessaire.
- Inclure tests unitaires, integration, et eventuellement contract tests.

## Performance quick-check
- Mettre en place des tests rapides (profilage ou stress basique) lorsque des endpoints critiques evoluent.
- Surveiller la latence 95e percentile via outils d'observabilite.

## Checklist revue backend
- [ ] Schema et migrations synchronises.
- [ ] Endpoints documentes et valides par tests.
- [ ] Tests pytest passent localement et en CI.
- [ ] Coverage >= objectif ou justification documentee.
- [ ] Logs et observabilite verifies.
- [ ] Reference roadmap incluse dans commits/PR.

## Commandes utiles
- Installation dependances: `pip install .[dev]`
- Lancement API: `uvicorn backend.main:app --reload`
- Migration base de donnees: `PYTHONPATH=src alembic -c src/backend/db/alembic.ini upgrade head`
- Tests locaux: `pytest`
