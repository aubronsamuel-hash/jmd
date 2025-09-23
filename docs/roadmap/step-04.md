# STEP 04 - Initialisation des agents et de la CI

## SUMMARY
Formaliser les agents operants du monorepo et livrer une premiere boucle de guards CI/documentation.

## GOALS
- Rediger l'agent central et les sous-agents backend, frontend, devops et docs.
- Publier le sommaire des agents et cadrer la boucle documentaire.
- Preparer les scripts PowerShell de verification roadmap/docs.
- Initialiser les workflows GitHub Actions backend, frontend et guards.

## CHANGES
- Ajout de `AGENT.md` et des fichiers agents specifiques.
- Creation des scripts `roadmap_guard.ps1`, `docs_guard.ps1` et `run_all_guards.ps1`.
- Ajout des workflows CI de base backend/frontend/guards.
- Mise a jour du changelog, du README et des journaux Codex.

## TESTS
- Execution manuelle des guards; blocage PowerShell 7 dans l'environnement de controle initial.
- CI planifiee mais dependances applicatives encore manquantes.

## CI
- Workflows `backend-tests.yml`, `frontend-tests.yml` et `guards.yml` actifs.
- Suivi de la reference roadmap via le commit message.

## ARCHIVE
- Documentation agent en place pour reference future.
- Journalisation dans `docs/CHANGELOG.md` et `docs/codex/last_output.json`.

VALIDATE? yes
