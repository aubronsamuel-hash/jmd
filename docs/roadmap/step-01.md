# STEP 01 - Auth foundations for organisations

## SUMMARY

Premiere iteration dediee a la mise en place de l'authentification multi-organisation, du modele RBAC et de l'observabilite associee pour preparer les modules suivants de la spec v0.1.

## GOALS

- Livrer un socle d'authentification couvrant inscription, connexion (mot de passe et lien magique), invitations et changement de contexte organisationnel.
- Mettre en production un modele RBAC complet avec roles et portees conformes a la spec fonctionnelle.
- Outiller l'observabilite et l'audit des flux d'authentification des le demarrage du produit.

## CHANGES

### Backend

1. Initialiser `src/backend` avec FastAPI, configuration Pydantic Settings et premiere migration Alembic pour Utilisateur, Organisation, Role et relations (associations user-org, invitations, sessions).
2. Implementer les services et endpoints auth: inscription, connexion password, emission/validation de lien magique, invitation multi-organisation, changement d'organisation et journalisation minimale.
3. Couvrir la logique RBAC (roles/permissions, verification portee) dans un module dedie et ecrire les tests Pytest (unitaires + integration) avec coverage >= 70 % sur le domaine auth/org.

### Frontend

1. Bootstrapper l'application (React + Vite) si necessaire avec structure modules onboarding/auth.
2. Creer les vues et formulaires pour inscription, connexion password, lien magique et switch d'organisation (avec gestion d'erreurs et etats de chargement).
3. Mettre en place la gestion de session front (stockage tokens, rafraichissement, selection organisation) et ecrire tests vitest sur composants auth.

### DevOps & Infra

1. Definir les secrets (SMTP_HOST, SMTP_USER, SMTP_PASS, tokens magie) et workflows GitHub Actions (backend-tests, frontend-tests, guards) avec caches poetry/pnpm.
2. Ajouter scripts de seeding comptes tests et automatiser les migrations dans la CI.
3. Configurer la collecte de logs structures auth (niveau audit) et le monitoring initial (dashboards, alertes 5xx/latence auth).

### Documentation & Qualite

1. Documenter les flux auth (diagrammes sequence), le guide RBAC et mettre a jour les AGENTs impactes.
2. Completer `docs/CHANGELOG.md` et `docs/codex/last_output.json` pour suivre l'avancement, et maintenir `docs/roadmap/ROADMAP.readme.md` a jour.
3. Executer `tools/guards/run_all_guards.ps1`, `pytest`, `pnpm test --filter frontend` avant chaque merge et analyser les rapports de couverture.

## TESTS

- `tools/guards/run_all_guards.ps1` pour controler la documentation et la roadmap.
- `pytest` pour les modules backend d'authentification et RBAC.
- `pnpm test --filter frontend` pour valider les composants et vues auth.

## CI

- Workflows GitHub Actions `backend-tests`, `frontend-tests` et `guards` avec caches poetry/pnpm et secrets SMTP.
- Automatisation des migrations Alembic et du seeding comptes tests dans la pipeline.

## ARCHIVE

- Archiver les diagrammes auth, le guide RBAC et les rapports de couverture dans `docs/codex/` a chaque fin d'iteration.
- Documenter les resultats dans `docs/CHANGELOG.md` et `docs/codex/last_output.json`.

## NEXT STEPS

- Planifier l'execution detaillee (Do) en sequence backend -> frontend -> devops -> docs.
- Identifier les dependances externes (SMTP, stockage tokens, service email) et lever les risques.
- Preparer la synchronisation avec les acteurs produit pour valider les parcours auth avant implementation.

VALIDATE? no
