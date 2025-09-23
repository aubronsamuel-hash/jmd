# STEP 08 - Gestion des artistes et disponibilites

## SUMMARY
Ouvrir l'API a la gestion complete des artistes en permettant la creation, la mise a jour et la consultation des disponibilites ainsi que leur exploitation dans le planning.

## GOALS
- Introduire des endpoints REST pour gerer les artistes et leurs disponibilites (CRUD minimal).
- Synchroniser les schemas Pydantic, les models SQLAlchemy et les migrations Alembic associees.
- Factoriser une couche de services domaine pour la maintenance des artistes et leur reutilisation dans la generation de planning.
- Documenter les nouveaux flux (API, exemples JSON) et preparer les jeux de donnees pour tests et demonstration.

## CHANGES
- Etendre `backend.domain` et `backend.models` afin d'integrer les operations CRUD artistes/disponibilites.
- Ajouter les routes FastAPI (`POST/GET /artists`, `GET /artists/{id}`, `PUT /artists/{id}`, `DELETE /artists/{id}`) et gerer les erreurs fonctionnelles.
- Produire une revision Alembic couvrant les contraintes (unicite disponibilites, suppression en cascade) et ajuster la configuration database.
- Renforcer les tests d'integration avec une base SQLite en memoire et des fixtures dediees aux artistes.
- Mettre a jour la documentation backend (README, AGENT backend) et les scripts de demarrage pour illustrer les nouveaux endpoints.

## TESTS
- Execution de `pytest` avec SQLite en memoire, couvrant les operations CRUD artistes et la generation de planning post-synchronisation.
- Verification du rapport de couverture (>= 70 %) et ajout de tests de regression sur la selection des creneaux.

## CI
- Adapter le workflow `backend-tests` pour initialiser les donnees de reference avant les tests d'integration.
- Publier les artefacts de couverture et suivre la regression sur les routes artistes.

## ARCHIVE
- Mise a jour de `docs/CHANGELOG.md`, `docs/codex/last_output.json` et de la roadmap une fois l'etape livree.
- Archivage d'exemples de payloads artistes/planning dans `docs/` pour reference produit.

## RESULTS
- API FastAPI expose des operations completes pour la gestion des artistes et disponibilites.
- Les routes planning reutilisent la persistence artistes sans duplication de donnees.
- Suite de tests enrichie validant les scenarios CRUD et la generation de planning.

VALIDATE? no
