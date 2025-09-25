# AgentImportExport

## Role
Pilote import/export de donnees.

## Inputs
- data exchange requests
- schemas/contracts/agentimportexport_contract.json

## Outputs
- import/export manifests

## Event Topics
- import.completed
- export.completed

## Guards
- tools/guards/security_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
