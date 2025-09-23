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

## Tests et coverage
- Commande reference: `pytest --cov=src/backend --cov-report=xml`.
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

