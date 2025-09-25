# AgentAvailability

## Role
Collecte disponibilites et met a jour planning brut.

## Inputs
- availability submissions
- schemas/contracts/agentavailability_contract.json

## Outputs
- availability snapshots

## Event Topics
- availability.submitted
- availability.snapshot

## Guards
- tools/guards/qa_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
