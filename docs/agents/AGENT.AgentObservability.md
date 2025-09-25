# AgentObservability

## Role
Observe et alerte sur la plateforme.

## Inputs
- metrics streams
- schemas/contracts/agentobservability_contract.json

## Outputs
- observability alerts

## Event Topics
- obs.metric.ingested
- obs.alert.raised

## Guards
- tools/guards/obs_smoke.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
