# AgentInventory

## Role
Gere ressources materiel.

## Inputs
- inventory requests
- schemas/contracts/agentinventory_contract.json

## Outputs
- inventory reservations

## Event Topics
- inventory.reserved
- inventory.released

## Guards
- tools/guards/qa_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
