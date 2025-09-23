# Changelog

## 2025-10-01
- Entrepot analytics structure (`analytics_mission_events`, `analytics_payroll_records`, `analytics_equipment_incidents`) alimente par les evenements planning/paie/logistique.
- Service `backend.domain.analytics` et endpoints FastAPI `/api/v1/analytics/dashboard` + `/api/v1/analytics/exports` (KPIs, heatmap, comparatifs, latence < 15 min).
- Generation d'exports CSV/PDF/PNG signes (base64 + SHA-256) avec metadonnees filtres et integration storage gateway.
- Tests backend `test_analytics.py` garantissant aggregation, filtres multi-dimension et validite des exports.
- Ref: docs/roadmap/step-11.md

## 2025-09-30
- Synchronisation calendrier via module `backend.integrations.calendar` (exports ICS, webhooks, detection de conflits).
- Passage d'un gateway de stockage documentaire mutualise (`backend.integrations.storage`) pour archiver les plannings.
- Nouveaux parametres BACKEND_* exposes pour calendriers, stockage et fournisseur email.
- Documentation API enrichie sur les entetes de synchronisation et la configuration des connecteurs.
- Ref: docs/roadmap/step-10.md

## 2025-09-29
- Mise en place du module `backend.notifications` et parametrage email/Telegram.
- Envoi automatique lors de la creation de planning et endpoints de declenchement (`/notifications/test`, `/notifications/plannings/{id}/events`).
- Nouveaux tests backend couvrant la personnalisation des messages et l'orchestration multi-canaux.
- Documentation roadmap/API/agent backend mise a jour pour decrire les flux de notifications.
- Ref: docs/roadmap/step-09.md

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

## 2025-09-22
- Publication de la specification fonctionnelle v0.1 comme reference produit.
- Injection des en-tetes SUT dans les fichiers agents backend/frontend/devops/docs.
- Ajout du script ensure_spec.ps1 et durcissement du guard documentaire.
- Ref: docs/roadmap/step-03.md
