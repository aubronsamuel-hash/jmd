# AgentSchema

## Role
Maintient les contrats et migrations schema.

## Inputs
- schemas/contracts/*.json

## Outputs
- schemas/contracts/version-manifest.json

## Event Topics
- schema.contract.published
- schema.contract.deprecated

## Guards
- tools/guards/schema_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
