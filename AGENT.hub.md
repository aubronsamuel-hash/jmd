# AGENT.hub.md

## Role et Portee
- Piloter la coordination des travaux du monorepo SaaS planning intermittent spectacle.
- Orchestrer la boucle d'amelioration continue (planification, execution, verification, correction, archivage, documentation).
- Garantir la coherence documentaire et la synchronisation avec la roadmap.
- Ne gere pas la redaction detaillee de specs produit ni la priorisation business (refere a la roadmap).

## Interfaces
- Entrants: prompts agents, tickets, fichiers `docs/roadmap/step-XX.md`, historiques CI.
- Sortants: commits, PR, mise a jour de la documentation, scripts de guards, artefacts CI/CD.
- Boucles de retour: rapports de guards, resultats de tests backend/frontend, alertes observabilite.

## Conventions
- Nommage ASCII uniquement pour fichiers, scripts, variables et clefs YAML.
- Commits au format Conventional Commits avec reference roadmap obligatoire: `Ref: docs/roadmap/step-XX.md`.
- Branch par defaut `DEFAULT_BRANCH`; travaux courants `WORK_BRANCH` (definis via variables d'environnement si fournis).
- Documentation en francais autorisee, mais respecter ASCII pour chemins et commandes.

## Structure du depot
- `src/` backend et frontend (a completer selon modules).
- `docs/` documentation generale, agents, roadmap, changelog.
- `tools/guards/` scripts PowerShell 7+ pour verifications locales.
- `.github/workflows/` pipelines GitHub Actions (tests et guards).

## Flux CI/CD et Gates
- Execution locale: `tools/guards/run_all_guards.ps1` avant commit.
- CI GitHub Actions: workflows `backend-tests.yml`, `frontend-tests.yml`, `guards.yml`.
- Gates minimales:
  - Tests backend FastAPI/SQLAlchemy (pytest) doivent reussir.
  - Tests frontend React/Vite (vitest) doivent reussir.
  - Coverage backend >= 70 % lorsque disponible.
  - Guards roadmap/docs doivent passer.

## Boucle d'execution (PDCA-F)
1. **Plan**: Lire la roadmap active (`docs/roadmap/step-XX.md`), definir objectifs et plan d'action.
2. **Do**: Implementer changements atomiques, commits a portee reduite.
3. **Check**: Executer tests et guards localement, analyser la CI distante.
4. **Fix**: Corriger les defauts, reexecuter les verifications.
5. **Archive**: Mettre a jour `docs/CHANGELOG.md`, roadmap, artefacts (`docs/codex/last_output.json`).
6. **Document**: Actualiser READMEs, AGENTs, sommaires, journaux.

## Checklists de validation
### Avant commit
- [ ] Roadmap referencee dans le message de commit.
- [ ] `tools/guards/run_all_guards.ps1` execute sans erreur (ou justification documentee).
- [ ] Documentation associee mise a jour.
- [ ] Tests pertinents lances (backend/frontend selon impact).

### Avant PR
- [ ] PR body complet (Summary, Changes, Testing, Risk, Rollback, Roadmap Ref, Checklist).
- [ ] Captures ou artefacts UI fournis si front impacte.
- [ ] Lien vers roadmap confirme.
- [ ] CI GitHub Actions verte.

## Artifacts et Journal
- `docs/codex/last_output.json`: plan et etat d'execution courant.
- `docs/CHANGELOG.md`: changelog synthetique, append-only.
- Journal roadmap: section RESULTATS dans `docs/roadmap/step-XX.md` + bloc `VALIDATE?`.

## Liens agents
- [AGENT backend](docs/agents/AGENT.backend.md)
- [AGENT frontend](docs/agents/AGENT.frontend.md)
- [AGENT devops](docs/agents/AGENT.devops.md)
- [AGENT docs](docs/agents/AGENT.docs.md)
- [Sommaire agents](docs/agents/AGENTS.readme.md)

## Rappels operationnels
- Basculer vers HTTPS si une action Git SSH echoue, puis documenter la correction.
- Toujours preferer chemins relatifs dans la documentation et les scripts.
- Maintenir la compatibilite PowerShell 7+ pour tous les guards.

