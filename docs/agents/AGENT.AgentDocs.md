# AgentDocs

## Role
Maintien documentation.

## Inputs
- docs change requests
- schemas/contracts/agentdocs_contract.json

## Outputs
- docs updates
- docs review required reports

## Event Topics
- docs.updated
- docs.review.required

## Guards
- tools/guards/docs_guard.ps1
- tools/guards/archive_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
