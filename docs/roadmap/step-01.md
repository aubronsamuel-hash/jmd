# STEP 01 - Auth foundations for organisations

## CONTEXT

* Premiere etape de la roadmap fonctionnelle (spec section 11) couvrant l'authentification, le RBAC et la gestion des organisations.
* S'appuie sur les exigences des modules 1 (roles et permissions), 2 (entites Utilisateur/Organisation) et 3.1 (Auth, comptes et organisations) de la spec v0.1.
* Prepare les agents backend et frontend a disposer d'un socle securise avant d'aborder les projets et missions.

## OBJECTIVES

* Implementer les parcours d'inscription, connexion (mot de passe + lien magique) et invitation multi-organisation.
* Mettre en place un modele RBAC couvrant les roles listes et les portees organisation/projet.
* Exposer une gestion d'organisation (creation, parametres de marque, politiques paie de base).
* Documenter et monitorer les flux d'authentification pour audit et observabilite initiale.

## CHANGES

* Backend FastAPI: schemas Pydantic v2 pour Utilisateur, Organisation, Session; endpoints auth (signup, login, magic link), invitations, switch d'organisation.
* Backend services: stockage SQLAlchemy des utilisateurs, roles, associations org, tokens, journaux d'audit minimal.
* Frontend: vues onboarding/login, selection d'organisation, gestion de profil de base et parametres org.
* Devops: secrets pour emails magic link, configuration CI (migrations, seeding comptes tests), observabilite (logs auth) et policies de securite.
* Docs: mises a jour README/agents pour reflet architecture auth, sequence diagrammes des flux, guides RBAC.

## TESTS

* Local: `pytest` (backend) avec couverture >= 70 % sur domaines auth/org; `pnpm test --filter frontend` pour composants login/onboarding; `tools/guards/run_all_guards.ps1`.
* CI: workflows `backend-tests.yml`, `frontend-tests.yml`, `guards.yml` doivent passer; rapport coverage backend >= 70 %, frontend vitest >= 80 % lignes sur module auth.

## CI

* Necessite variables pour envoi email (SMTP_HOST, SMTP_USER, SMTP_PASS) en secrets, plus GH_TOKEN pour guards.
* Ajouter caches poetry/pnpm si absent pour accelerer pipelines; verifier migrations init auth dans jobs backend.

## ARCHIVE

* Apres validation: maj `docs/CHANGELOG.md`, `docs/codex/last_output.json`, `docs/roadmap/ROADMAP.readme.md` et README principal.

VALIDATE? no
