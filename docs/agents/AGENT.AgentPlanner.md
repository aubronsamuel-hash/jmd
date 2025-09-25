# AgentPlanner

## Role
Planifie et sequence la roadmap.

## Inputs
- docs/roadmap/ROADMAP.template-step.md
- schemas/contracts/agentplanner_contract.json

## Outputs
- docs/roadmap/step-XX.md
- .codex/latest/last_output.json

## Event Topics
- roadmap.plan
- roadmap.progress

## Guards
- tools/guards/roadmap_guard.ps1
- tools/guards/archive_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
