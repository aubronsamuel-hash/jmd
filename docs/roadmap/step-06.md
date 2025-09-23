# STEP 06 - Bootstrap backend FastAPI

## SUMMARY
Initier l'architecture backend du SaaS de planning en livrant un service FastAPI testable et pret pour l'integration continue.

## GOALS
- Structurer un package Python `backend` avec FastAPI, configuration de settings et point d'entree `main`.
- Definir un premier module de domaine pour la gestion des artistes et des disponibilites, incluant schemas Pydantic.
- Mettre en place la configuration de tests (pytest + coverage) et un jeu de tests de fumee couvrant l'endpoint de sante et le flux de creation de planning.
- Documenter les commandes de developpement (lancement API, tests) et integrer les dependances dans la CI backend.

## CHANGES
- Ajout de `pyproject.toml`, `src/backend/`, `tests/backend/` et scripts utilitaires.
- Mise a jour du workflow `backend-tests` pour installer les dependances projet et publier un rapport de couverture minimal.
- Documentation du backend dans `README` et `docs/agents/AGENT.backend.md`.
- Actualisation de la roadmap et du changelog apres livraison.

## TESTS
- Execution locale de `pytest` avec couverture.
- Verification des endpoints via `httpx.AsyncClient` dans les tests.
- Execution du workflow GitHub Actions `Backend Tests`.

## CI
- Mise a jour de `backend-tests.yml` pour gerer l'installation via `pip` ou `uv` et le cache `pip`.
- Publication de l'artefact de couverture et seuil >= 70 %.

## ARCHIVE
- Mise a jour de `docs/CHANGELOG.md` avec les entrees Step 06.
- Synchronisation des journaux (`docs/codex/last_output.json`) et documentation backend.

## RESULTS
- API FastAPI exposee via `backend.main:app` avec endpoints `/api/v1/health` et `/api/v1/plannings` en production.
- Module de domaine artistes/planning fonctionnel avec validation Pydantic et gestion d'erreurs `PlanningError`.
- Suite de tests asynchrones (`pytest`, `httpx.AsyncClient`) assurant la couverture minimale et generation de `coverage.xml`.
- Documentation (README, AGENT backend) et changelog synchronises avec la roadmap.

VALIDATE? yes
