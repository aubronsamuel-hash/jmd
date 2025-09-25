# AgentDataOps

## Role
Supervise pipelines data.

## Inputs
- data jobs
- schemas/contracts/agentdataops_contract.json

## Outputs
- data pipeline reports

## Event Topics
- data.pipeline.completed
- data.quality.issue

## Guards
- tools/guards/qa_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
