SUT: docs/specs/spec-fonctionnelle-v0.1.md
Les guards/CI verifient la presence et la reference de la spec.

# AGENT devops

## Objectifs
- Fiabiliser la chaine CI/CD du monorepo backend + frontend.
- Maintenir les scripts PowerShell 7+ et workflows GitHub Actions.
- Assurer la supervision, la gestion des secrets et la securite des pipelines.

## Workflows CI/CD
- `backend-tests.yml`: installe Python, dependances, execute pytest + coverage.
- `frontend-tests.yml`: installe Node/pnpm, lance lint/tests/build selon besoins.
- `guards.yml`: execute `tools/guards/run_all_guards.ps1` pour valider la discipline documentaire.
- Ajouter matrices (OS/versions) si pertinents, sinon cibler `ubuntu-latest`.
- Utiliser caches (pip, pnpm) pour accelerer les builds.

## Scripts et automatisation
- Scripts PowerShell situes dans `tools/guards/` et executables sous Windows/macOS/Linux (PowerShell 7+).
- `run_all_guards.ps1` doit orchestrer l'execution des guards individuels et retourner un code non nul en cas d'echec.
- Prevoir fallback HTTP(S) si operations git SSH echouent; journaliser la bascule dans la roadmap/CHANGELOG.

## Secrets et configuration
- Stocker les secrets CI via GitHub Actions Secrets (ex: `DATABASE_URL`, `API_BASE_URL`).
- Ne jamais commiter de secrets en clair.
- Documenter les variables obligatoires dans les workflows.

## Observabilite
- Prevoir integration Prometheus/Grafana/Loki si deploiement operationnel.
- Collecter metrics backend (latence, erreurs) et logs applicatifs.
- Configurer alertes minimales (statut CI, deployment) via Slack/email.

## Politique de branches
- Tronc principal: `DEFAULT_BRANCH`.
- Branches de travail: `feature/*`, `fix/*`, `chore/*` selon Conventional Commits.
- Rebase preferentiel avant merge, merge fast-forward si possible.

## Checklist revue devops
- [ ] Scripts PowerShell testes sur PowerShell 7+.
- [ ] Workflows GitHub Actions valides (lint YAML si necessaire).
- [ ] Secrets references documentes et non exposes.
- [ ] Guards executent et echouent correctement en cas de non-conformite.
- [ ] Reference roadmap dans commits/PR.

