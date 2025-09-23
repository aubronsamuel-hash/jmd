# Changelog

## 2025-09-28
- CRUD complet des artistes expose via FastAPI (routes `/api/v1/artists`).
- Synchronisation des services domaine, schemas Pydantic et contraintes Alembic pour les disponibilites.
- Documentation API et tests d'integration enrichis autour de SQLite en memoire.
- Ref: docs/roadmap/step-08.md

## 2025-09-27
- Ajout de la persistence SQLAlchemy avec models `backend.models` et configuration `backend.db`.
- Creation des migrations Alembic initiales et documentation des commandes d'execution.
- Nouveaux endpoints REST pour lister et recuperer les plannings, avec tests pytest sur SQLite.
- Ref: docs/roadmap/step-07.md

## 2025-09-25
- Bootstrap du backend FastAPI avec configuration `backend.config` et point d'entree `backend.main`.
- Mise en place des schemas de domaine (artistes, disponibilites, planning) et du service de creation de planning.
- Ajout des tests de fumee (sante et creation planning) avec couverture >= 70 % et workflow CI actualise.
- Ref: docs/roadmap/step-06.md

## 2025-09-24
- Renforcement du bootstrap pnpm dans les workflows Node avec detection conditionnelle et fallback corepack.
- Mise a jour du guard CI pour exposer l'etat du workspace pnpm.
- Ref: docs/roadmap/step-05.md

## 2025-09-23
- Creation du hub agent et des sous-agents.
- Ajout des guards PowerShell et workflows CI.
- Mise a jour roadmap step-04 et documentation associee.
- Ref: docs/roadmap/step-04.md
