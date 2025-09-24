# STEP 02 - Projects and missions foundations

## SUMMARY
- Backend enrichi pour couvrir les modules 3.2 (Projects) et 3.3 (Missions reutilisables) de la spec et preparer le workflow WF-01.
- RBAC et sessions etendus pour encadrer la gestion des projets, lieux, gabarits de mission et tags depuis les roles STEP 01.
- Le socle debloque les entites partagees (planning, disponibilites, paie) pour les iterations suivantes.

## OBJECTIF
- Offrir des APIs backend completes pour creer et administrer projets, lieux et gabarits de mission reutilisables sous controle RBAC.

## ACTIONS
- Modele SQLAlchemy et schemas Pydantic ajoutes pour Venue, Project, MissionTag et MissionTemplate avec relations et contraintes d'organisation.
- Services FastAPI dedies (venues, projects, mission-tags, mission-templates) exposes via routes `/api/v1/*` et verifies par des tests Pytest couvrant les flux CRUD et l'autorisation.
- Extension du module RBAC (permissions view/manage) et factorisation de l'acces session/membership pour mutualiser la verification des permissions.
- Ajout de tests d'integration backend (`tests/backend/test_projects.py`) garantissant le scenario WF-01 (creation projet + missions) et la protection role Viewer.

## RESULTATS
- Les endpoints projets/missions retournent des reponses structurees (camelCase) avec venues et tags embarques; couverture Pytest 79.74 % (> 70 % cible backend).
- Les permissions Owner/Admin gerent, Member/Viewer consultent; les erreurs de references (venue/tag inconnus) sont renvoyees en 404.
- Frontend, guards graphiques et documentation visuelle restent a implementer pour finaliser la step.

## PROCHAINES ETAPES
- Implementer les vues React pour la liste/detail projet et le catalogue missions + tests Vitest associes.
- Mettre a jour les diagrammes d'architecture/relations et synchroniser les guards documentaire (docs_guard) avec les nouvelles entites.
- Ouvrir la planification WF-01 (planning, disponibilites) en reutilisant les gabarits de mission crees.

## GOALS
- Implementer le domaine backend pour projets et missions reutilisables avec persistence, validation et APIs compatibles RBAC.
- Fournir des interfaces frontend pour creer et maintenir les projets, associer les lieux et cataloguer les gabarits de mission.
- Garantir que workflows et modeles de donnees satisfont les criteres d'acceptation WF-01 sur la mise en place des projets et missions reutilisables.

- Backend : SQLAlchemy models, schemas Pydantic, services CRUD et routes FastAPI pour Project, Venue, MissionTemplate et MissionTag; RBAC et logique de session factorises.
- Backend : tests Pytest d'integration couvrant projets, missions, tags avec jeux de donnees WF-01 et couverture >=70 %.
- Frontend : vues React pour la liste/detail projet et le catalogue de missions (a realiser).
- Frontend : gestion d'etat (requete/mutations) pour les APIs projet/mission + suites Vitest (a realiser).
- Docs & tooling : mettre a jour diagrammes, guides et guards (a planifier).

## TESTS
- Local : `pytest` (domaines backend), `pnpm test --filter frontend` (UI missions/projets), `tools/guards/run_all_guards.ps1`.
- CI : assurer l'execution reussie de `backend-tests.yml`, `frontend-tests.yml` et `guards.yml` avec couverture >=70 % sur le domaine backend touche.

## CI
- Reutiliser les workflows existants; verifier qu'Alembic s'execute en CI et que les donnees seeds sont disponibles pour les suites d'integration.
- Surveiller les caches pnpm/pip; aucun nouveau secret attendu au-dela des placeholders base de donnees/SMTP.

## ARCHIVE
- Apres validation : mettre a jour `docs/CHANGELOG.md`, `docs/codex/last_output.json` et la section historique de `docs/roadmap/ROADMAP.readme.md`.

VALIDATE? no  (SAM ONLY may flip to yes)
