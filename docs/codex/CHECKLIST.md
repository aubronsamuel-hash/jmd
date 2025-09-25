# Prompt Codex Checklist Initiale

## Synthese
| Item | Description | Statut | Notes |
|------|-------------|--------|-------|
| 1 | Agents specialises | OK | Dossiers `docs/agents/` complets + alias `AGENT.planner.md`, `AGENT.schema.md`. |
| 2 | Archive et replay | OK | Scripts Codex PowerShell verifies et `last_output.json` mis a jour. |
| 3 | Automatisation roadmap | OK | Guards roadmap presents, PR template mis a jour avec bloc Codex Archive. |
| 4 | Production technique | OK | Schemas existants + nouveau `schemas/person.json` et migration initiale. |
| 5 | Observabilite et securite | OK | Guards `security_guard.ps1` et `obs_smoke.ps1` identifies. |
| 6 | Integrations externes | OK | Contrats agents deja en place (ex: `agentintegrations_contract.json`). |
| 7 | Experience dev/ops | OK | Scripts Codex et guards disponibles, PR template ajuste. |
| 8 | Boucle de validation | OK | Roadmap `step-05` contient bloc `VALIDATE`. |
| 9 | Cas d usage concret | OK | Documentation agents paie/planning deja en depot. |
| 10 | Evolutions possibles | OK | Plan de couverture `tests/COVERAGE_PLAN.md` defini avec jalons. |

## Details par item
### 1. Agents specialises — OK
- Nouveaux alias `docs/agents/AGENT.planner.md` et `docs/agents/AGENT.schema.md` pour satisfaire la checklist.
- Reference explicite vers les fiches principales existantes.

### 2. Archive et replay — OK
- Scripts PowerShell verifies dans `tools/codex/`.
- `docs/codex/last_output.json` et `.codex/latest/last_output.json` actualises avec le rapport courant.

### 3. Automatisation roadmap — OK
- PR template enrichi avec section "Codex Archive".
- Guards roadmap (`roadmap_guard.ps1`, `archive_guard.ps1`) disponibles.

### 4. Production technique — OK
- Ajout d un schema `schemas/person.json` et de la migration SQL `schemas/migrations/001_person_initial.sql`.
- Contrats JSON existants confirmes dans `schemas/contracts/`.

### 5. Observabilite et securite — OK
- Guards `security_guard.ps1` et `obs_smoke.ps1` verifies.

### 6. Integrations externes — OK
- Contrat `schemas/contracts/agentintegrations_contract.json` disponible.

### 7. Experience dev/ops — OK
- Scripts Codex (start/end session, snapshot, etc.) confirmes.
- Documentation du flux PR mise a jour.

### 8. Boucle de validation — OK
- `docs/roadmap/step-05.md` contient bloc `## VALIDATE?` conforme.

### 9. Cas d usage concret — OK
- Documentation agents paie (`AGENT.AgentPayroll.md`), missions (`AGENT.AgentAssignment.md`) et autres presente.

### 10. Evolutions possibles — OK
- Plan de couverture `tests/COVERAGE_PLAN.md` fixe les jalons jusqu a 80 %.

## Fichiers ajoutes ou modifies
- `.github/PULL_REQUEST_TEMPLATE.md`
- `docs/agents/AGENT.planner.md`
- `docs/agents/AGENT.schema.md`
- `docs/codex/CHECKLIST.md`
- `schemas/person.json`
- `schemas/migrations/001_person_initial.sql`
- `tests/COVERAGE_PLAN.md`
- `.codex/latest/last_output.json`
- `docs/codex/last_output.json`
- `.codex/archive/2025-09-25/session-239d6af0-b624-4e3a-a6e8-befc2169dab3/outputs/checklist.md`

## CI et guards
- Aucun guard ni test execute durant ce controle. Recommandation: lancer `tools/guards/run_all_guards.ps1` et la suite de tests backend/frontend lors de la prochaine session interactive.

## VALIDATE?
- yes/no (reserve a Sam)
