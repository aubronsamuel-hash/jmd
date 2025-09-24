# STEP 01 - Auth foundations for organisations

## SUMMARY
- Premiere iteration consacree a l'authentification multi-organisation, en s'appuyant sur la spec fonctionnelle v0.1 (sections 1, 2 et 3.1).
- Aligne backend, frontend et DevOps pour fournir un socle securise (RBAC complet, invitations et suivi audit).

## GOALS
- Livrer un socle d'authentification couvrant inscription, connexion (mot de passe et lien magique) et changement de contexte organisationnel.
- Mettre en place un modele RBAC coherent avec roles et portees definis dans la spec fonctionnelle.
- Outiller l'observabilite et l'audit des flux auth des le demarrage.

## CHANGES
- Backend : initialisation FastAPI (`src/backend`), configuration Settings, migrations Alembic pour Utilisateur/Organisation/Role, services et endpoints auth (inscription, connexion password + lien magique, invitations multi-organisation, switch organisation) avec journalisation RBAC.
- Backend : module dedie a la verification des permissions et tests Pytest (unitaires + integration) garantissant >= 70 % de couverture sur le domaine auth/org.
- Frontend : bootstrap React + Vite, vues formulaires inscription/connexion/lien magique/switch organisation avec gestion des erreurs et etats de chargement.
- Frontend : gestion de session (tokens, rafraichissement, selection organisation) et tests Vitest pour les composants auth.
- DevOps & Infra : secrets SMTP et tokens magie, workflows GitHub Actions (`backend-tests`, `frontend-tests`, `guards`), scripts de seeding et automatisation des migrations en CI, collecte des logs structures auth et monitoring (dashboards, alertes 5xx/latence).
- Documentation & Qualite : diagrammes de flux auth, guide RBAC, mise a jour des AGENTs, synchronisation de `docs/CHANGELOG.md` et `docs/codex/last_output.json`.

## TESTS
- `tools/guards/run_all_guards.ps1` pour verifier roadmap et documentation.
- `pytest` avec base SQLite en memoire et couverture ciblee sur auth/org.
- `pnpm test --filter frontend` pour les composants auth.

## CI
- Workflows GitHub Actions : `backend-tests.yml`, `frontend-tests.yml`, `guards.yml`.
- Execution automatique des migrations Alembic et collecte des rapports de couverture.

## ARCHIVE
- Archiver les artefacts de tests et les rapports de couverture.
- Mettre a jour `docs/roadmap/ROADMAP.readme.md`, `docs/CHANGELOG.md` et `docs/codex/last_output.json` apres completion.

VALIDATE? yes
